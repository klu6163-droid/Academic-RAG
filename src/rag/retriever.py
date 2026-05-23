"""
BM25 retriever + Hybrid retriever (FAISS + BM25 with RRF fusion).
"""

import math
import re
from collections import Counter


class BM25Retriever:
    """BM25 sparse retriever."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_tokens: list[list[str]] = []
        self.doc_freqs: list[Counter] = []
        self.idf: dict[str, float] = {}
        self.doc_len: list[int] = []
        self.avg_doc_len: float = 0.0
        self.num_docs: int = 0
        self._built = False

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9一-鿿]+", text.lower())

    def build(self, texts: list[str]):
        self.corpus_tokens = [self.tokenize(t) for t in texts]
        self.num_docs = len(self.corpus_tokens)
        self.doc_len = [len(t) for t in self.corpus_tokens]
        self.avg_doc_len = sum(self.doc_len) / max(self.num_docs, 1)

        df: Counter = Counter()
        self.doc_freqs = []
        for tokens in self.corpus_tokens:
            tf = Counter(tokens)
            self.doc_freqs.append(tf)
            for word in set(tokens):
                df[word] += 1

        self.idf = {}
        for word, freq in df.items():
            self.idf[word] = math.log((self.num_docs - freq + 0.5) / (freq + 0.5) + 1.0)
        self._built = True

    def search(self, query: str, top_k: int = 20) -> list[tuple[int, float]]:
        if not self._built:
            return []
        query_tokens = self.tokenize(query)
        scores = []
        for i in range(self.num_docs):
            score = 0.0
            for token in query_tokens:
                if token not in self.idf:
                    continue
                tf = self.doc_freqs[i].get(token, 0)
                dl = self.doc_len[i]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * dl / max(self.avg_doc_len, 1))
                score += self.idf[token] * numerator / max(denominator, 1e-10)
            scores.append((i, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    @property
    def is_ready(self) -> bool:
        return self._built


class HybridRetriever:
    """Combines FAISS dense retrieval with BM25 sparse retrieval using RRF."""

    def __init__(self, vector_store, bm25_retriever, embedding_engine, config):
        self.vs = vector_store
        self.bm25 = bm25_retriever
        self.emb = embedding_engine
        self.hybrid_enabled = config.hybrid.enabled
        self.rrf_k = config.hybrid.rrf_k

    def retrieve(self, query: str, top_k: int = 8, expanded_queries: list[str] | None = None) -> list[tuple[int, float]]:
        """
        Hybrid retrieval with RRF fusion.
        Returns (index, rrf_score) pairs sorted by score desc.
        """
        queries = [query] + (expanded_queries or [])

        # Collect all FAISS results
        faiss_results: dict[int, float] = {}
        for q in queries:
            q_emb = self.emb.encode_query(q)
            for idx, score in self.vs.search(q_emb, top_k=top_k * 3):
                faiss_results[idx] = max(faiss_results.get(idx, 0), score)

        if not self.hybrid_enabled or not self.bm25.is_ready:
            # Dense-only mode
            sorted_results = sorted(faiss_results.items(), key=lambda x: x[1], reverse=True)
            return sorted_results[:top_k]

        # Collect all BM25 results
        bm25_results: dict[int, float] = {}
        for q in queries:
            for idx, score in self.bm25.search(q, top_k=top_k * 3):
                bm25_results[idx] = max(bm25_results.get(idx, 0), score)

        # RRF fusion
        all_indices = set(faiss_results.keys()) | set(bm25_results.keys())
        rrf_scores: dict[int, float] = {}

        # Rank within each method
        faiss_ranked = sorted(faiss_results.items(), key=lambda x: x[1], reverse=True)
        bm25_ranked = sorted(bm25_results.items(), key=lambda x: x[1], reverse=True)

        faiss_rank = {idx: rank + 1 for rank, (idx, _) in enumerate(faiss_ranked)}
        bm25_rank = {idx: rank + 1 for rank, (idx, _) in enumerate(bm25_ranked)}

        for idx in all_indices:
            rrf = 0.0
            if idx in faiss_rank:
                rrf += 1.0 / (self.rrf_k + faiss_rank[idx])
            if idx in bm25_rank:
                rrf += 1.0 / (self.rrf_k + bm25_rank[idx])
            rrf_scores[idx] = rrf

        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    @property
    def is_ready(self) -> bool:
        return self.vs.is_ready
