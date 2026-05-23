"""
RAG service: orchestrates the full pipeline.
Supports evidence, full_paper, and hybrid retrieval modes.
"""

import json
from pathlib import Path
from collections import Counter

import numpy as np

from src.config import load_config, AppConfig
from src.rag.retriever import BM25Retriever, HybridRetriever
from src.rag.answer_generator import AnswerGenerator
from src.rag.citation import format_evidence_row
from src.storage.vector_store import FAISSVectorStore
from src.ingest.index_builder import EmbeddingEngine


class RAGService:
    """Singleton RAG service managing the full pipeline."""

    def __init__(self):
        self.config: AppConfig = load_config()
        self.evidence: list[dict] = []
        self.embedding_engine = EmbeddingEngine(self.config)
        self.vector_store = FAISSVectorStore(self.config)
        self.bm25 = BM25Retriever(
            k1=self.config.bm25.k1,
            b=self.config.bm25.b,
        )
        self.hybrid_retriever = HybridRetriever(
            self.vector_store, self.bm25, self.embedding_engine, self.config
        )
        self._llm_client = None
        self._answer_generator = None
        self._initialized = False

        # Full paper mode state (not yet implemented)
        self._full_paper_vs: FAISSVectorStore | None = None
        self._full_paper_chunks: list[dict] = []
        self._full_paper_bm25: BM25Retriever | None = None
        self._full_paper_ready = False

    @property
    def llm_client(self):
        if self._llm_client is None:
            from src.rag.llm_client import LLMClient
            self._llm_client = LLMClient(self.config.llm)
        return self._llm_client

    @property
    def answer_generator(self) -> AnswerGenerator:
        if self._answer_generator is None:
            self._answer_generator = AnswerGenerator(self.llm_client, self.config)
        return self._answer_generator

    def initialize(self):
        """Load evidence, build/load indexes."""
        if self._initialized:
            return

        # Load evidence
        evidence_path = Path(self.config.corpus.evidence_json)
        with open(evidence_path, "r", encoding="utf-8") as f:
            self.evidence = json.load(f)

        # Build embedding texts
        texts = [
            f"{r.get('evidence_text', '')} {r.get('keyword', '')} {r.get('category', '')}"
            for r in self.evidence
        ]

        # Load or compute embeddings
        embeddings = self.embedding_engine.load_or_compute(texts, cache_key="evidence")

        # Build or load FAISS index
        if not self.vector_store.load("evidence", num_vectors=len(self.evidence)):
            self.vector_store.build(embeddings)
            self.vector_store.save("evidence")

        # Build BM25 index
        bm25_texts = [
            f"{r.get('evidence_text', '')} {r.get('title', '')} {r.get('keyword', '')} {r.get('category', '')}"
            for r in self.evidence
        ]
        self.bm25.build(bm25_texts)

        self._initialized = True

    def _diversity_rerank(self, results: list[tuple[int, float]], max_per_paper: int) -> list[tuple[int, float]]:
        """Rerank results to ensure diversity across papers.

        Caps the number of chunks from any single paper to max_per_paper.
        """
        paper_counts: Counter = Counter()
        diversified = []
        deferred = []

        for idx, score in results:
            if idx >= len(self.evidence):
                continue
            paper_id = self.evidence[idx].get("paper_id", "")
            if paper_counts[paper_id] < max_per_paper:
                diversified.append((idx, score))
                paper_counts[paper_id] += 1
            else:
                deferred.append((idx, score))

        # Fill remaining slots with deferred results
        diversified.extend(deferred)
        return diversified

    def _retrieve_evidence(
        self, question: str, top_k: int, filters: dict | None
    ) -> list[dict]:
        """Retrieve from evidence table using hybrid retrieval."""
        # Query expansion
        expanded = self.answer_generator.expand_query(question)

        # Hybrid retrieval — fetch more than needed for diversity reranking
        fetch_k = top_k * 3 if self.config.retrieval.diversity_rerank else top_k * 2
        results = self.hybrid_retriever.retrieve(
            question, top_k=fetch_k, expanded_queries=expanded
        )

        # Diversity rerank
        if self.config.retrieval.diversity_rerank:
            results = self._diversity_rerank(results, self.config.retrieval.max_chunks_per_paper)

        # Apply filters and format
        formatted = []
        for idx, score in results:
            if idx >= len(self.evidence):
                continue
            r = self.evidence[idx]

            if filters:
                if filters.get("category") and r["category"] not in filters["category"]:
                    continue
                if filters.get("claim_type") and r.get("claim_type", "") not in filters["claim_type"]:
                    continue
                if filters.get("confidence") and r.get("confidence", "") not in filters["confidence"]:
                    continue
                if filters.get("only_high_relevance") and r.get("relevance", "") != "high_relevance_pu":
                    continue
                if filters.get("exclude_manual_check") and r.get("needs_manual_check", "").lower() == "true":
                    continue

            formatted.append(format_evidence_row(idx, r, score))
            if len(formatted) >= top_k:
                break

        return formatted

    def _retrieve_full_paper(
        self, question: str, top_k: int, filters: dict | None
    ) -> list[dict]:
        """Retrieve from full PDF chunk index. Not yet implemented."""
        raise NotImplementedError(
            "full_paper mode is not configured yet. "
            "No 37043-chunk FAISS index found. "
            "Build one from 06_logs/extracted_texts/ to enable this mode."
        )

    def retrieve(
        self,
        question: str,
        top_k: int = 8,
        mode: str = "evidence",
        filters: dict | None = None,
    ) -> tuple[list[dict], list[str]]:
        """Retrieve evidence using specified mode. Returns (results, warnings)."""
        self.initialize()
        warnings = []

        if mode == "evidence":
            return self._retrieve_evidence(question, top_k, filters), warnings

        elif mode == "full_paper":
            try:
                return self._retrieve_full_paper(question, top_k, filters), warnings
            except NotImplementedError as e:
                warnings.append(str(e))
                return [], warnings

        elif mode == "hybrid":
            # Try evidence first
            results = self._retrieve_evidence(question, top_k, filters)
            top_score = results[0]["score"] if results else 0.0

            if top_score >= self.config.answering.min_retrieval_score and len(results) >= self.config.answering.min_evidence_chunks:
                return results, warnings

            # Evidence insufficient, try full_paper
            warnings.append("Evidence mode returned low-confidence results. Attempting full_paper fallback.")
            try:
                fp_results = self._retrieve_full_paper(question, top_k, filters)
                return fp_results, warnings
            except NotImplementedError as e:
                warnings.append(f"Full paper fallback unavailable: {e}")
                return results, warnings

        else:
            warnings.append(f"Unknown mode '{mode}'. Using evidence mode.")
            return self._retrieve_evidence(question, top_k, filters), warnings

    def _truncate_excerpts_for_llm(self, evidence_rows: list[dict]) -> list[dict]:
        """Truncate excerpts to max_excerpt_chars before sending to LLM."""
        max_chars = self.config.answering.max_excerpt_chars
        truncated = []
        for row in evidence_rows:
            row_copy = dict(row)
            excerpt = row_copy.get("excerpt", "")
            if len(excerpt) > max_chars:
                row_copy["excerpt"] = excerpt[:max_chars] + "..."
            truncated.append(row_copy)
        return truncated

    def _assign_support_levels(self, evidence_rows: list[dict], evidence_levels: dict) -> list[dict]:
        """Assign support_level to each evidence row based on LLM's evidence_levels output."""
        # Build lookup: evidence_number -> support_level
        level_map = {}
        for level_name, indices in evidence_levels.items():
            for idx in indices:
                level_map[idx] = level_name

        result = []
        for i, row in enumerate(evidence_rows):
            row_copy = dict(row)
            row_copy["support_level"] = level_map.get(i + 1, "")  # 1-indexed
            result.append(row_copy)
        return result

    def answer_question(
        self,
        question: str,
        top_k: int = 8,
        mode: str = "evidence",
        filters: dict | None = None,
        include_raw_evidence: bool = True,
        answer_style: str = "concise",
    ) -> dict:
        """Full RAG: retrieve + generate answer."""
        self.initialize()

        evidence_rows, warnings = self.retrieve(question, top_k=top_k, mode=mode, filters=filters)

        # Collect warnings
        mc_count = sum(1 for r in evidence_rows if r.get("needs_manual_check"))
        if mc_count > 0:
            warnings.append(f"{mc_count} evidence rows need manual check — verify before citing.")

        # Truncate excerpts for LLM
        llm_evidence = self._truncate_excerpts_for_llm(evidence_rows)

        # Generate answer
        answer_result = self.answer_generator.generate(question, llm_evidence, answer_style=answer_style)

        # Assign support levels to evidence rows
        evidence_levels = answer_result.get("evidence_levels", {})
        evidence_with_levels = self._assign_support_levels(evidence_rows, evidence_levels)

        # Update evidence rows with support_level for output
        if include_raw_evidence:
            for i, row in enumerate(evidence_with_levels):
                if i < len(evidence_rows):
                    evidence_rows[i]["support_level"] = row.get("support_level", "")

        return {
            "question": question,
            "answer": answer_result["answer"],
            "confidence": answer_result["confidence"],
            "no_answer": answer_result["no_answer"],
            "evidence": evidence_rows if include_raw_evidence else [],
            "evidence_levels": evidence_levels,
            "retrieval": {
                "top_k": top_k,
                "retrieved_count": len(evidence_rows),
                "mode": mode,
                "hybrid_retrieval": self.config.hybrid.enabled and self.bm25.is_ready,
                "query_expansion_used": self.config.query_expansion.enabled and self.llm_client.is_available,
            },
            "warnings": warnings + answer_result.get("warnings", []),
        }

    def get_stats(self) -> dict:
        """Return corpus and pipeline statistics."""
        self.initialize()

        mc = sum(1 for r in self.evidence if r.get("needs_manual_check", "").lower() == "true")
        ml = sum(1 for r in self.evidence if r.get("ml_feature_candidate", "").lower() == "true")
        hr = sum(1 for r in self.evidence if r.get("relevance", "") == "high_relevance_pu")
        papers = len(set(r.get("paper_id", "") for r in self.evidence))

        return {
            "evidence_rows": len(self.evidence),
            "unique_papers": papers,
            "manual_check_rows": mc,
            "ml_feature_candidates": ml,
            "high_relevance": hr,
            "rag_backend_mode": "full_pipeline",
            "available_modes": ["evidence", "full_paper", "hybrid"],
            "default_mode": "evidence",
            "evidence_mode": {
                "enabled": True,
                "vector_count": len(self.evidence),
                "source": "global_evidence_table_cleaned.csv",
                "index_version": f"evidence_{len(self.evidence)}",
            },
            "full_paper_mode": {
                "enabled": self._full_paper_ready,
                "vector_count": len(self._full_paper_chunks) if self._full_paper_ready else None,
                "source": "PDF chunks" if self._full_paper_ready else "not configured",
                "index_version": "",
            },
            "retriever": "faiss_hybrid_rrf" if (self.config.hybrid.enabled and self.bm25.is_ready) else "faiss_dense",
            "query_expansion": self.config.query_expansion.enabled,
            "embedding_provider": self.config.embedding.provider,
            "embedding_model": self.config.embedding.model,
            "llm_provider": self.config.llm.provider,
            "llm_model": self.config.llm.model,
            "no_answer_gate": True,
            "faiss_vectors": self.vector_store.num_vectors,
            "bm25_ready": self.bm25.is_ready,
            "diversity_rerank": True,
            "max_chunks_per_paper": 2,
        }


# Global singleton
_service: RAGService | None = None


def get_service() -> RAGService:
    global _service
    if _service is None:
        _service = RAGService()
    return _service
