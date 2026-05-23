"""
Unified configuration for the RAG pipeline.
Loads from config.yaml with .env overrides.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

# Load .env
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    with open(_env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class EmbeddingConfig:
    provider: str = "local"  # local | api | mock
    model: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 64
    cache_dir: str = str(PROJECT_ROOT / "data" / "cache" / "embeddings")


@dataclass
class VectorStoreConfig:
    index_type: str = "flat_ip"  # flat_ip | flat_l2 | ivf
    index_dir: str = str(PROJECT_ROOT / "data" / "cache" / "faiss_index")
    nprobe: int = 10


@dataclass
class BM25Config:
    k1: float = 1.5
    b: float = 0.75
    enabled: bool = True


@dataclass
class HybridConfig:
    enabled: bool = True
    method: str = "rrf"  # rrf | weighted
    rrf_k: int = 60
    vector_weight: float = 0.6
    bm25_weight: float = 0.4


@dataclass
class QueryExpansionConfig:
    enabled: bool = False  # requires LLM
    max_expansions: int = 3


@dataclass
class AnsweringConfig:
    enabled: bool = True
    min_retrieval_score: float = 0.017  # Tuned from benchmark: filters irrelevant queries
    min_evidence_chunks: int = 1
    no_answer_threshold: float = 0.017  # Below this, evidence is too weak (Q9/Q10 score 0.0164)
    max_context_chunks: int = 8
    max_excerpt_chars: int = 500  # Truncate excerpts sent to LLM


@dataclass
class RetrievalConfig:
    max_chunks_per_paper: int = 2  # Diversity: cap per-paper results in top_k
    diversity_rerank: bool = True


@dataclass
class LLMConfig:
    provider: str = "openai_compatible"
    base_url: str = ""
    api_key: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 2000
    timeout: int = 120


@dataclass
class CorpusConfig:
    evidence_json: str = str(PROJECT_ROOT / "frontend" / "public" / "data" / "evidence.json")
    kg_nodes_json: str = str(PROJECT_ROOT / "frontend" / "public" / "data" / "kg_nodes.json")
    kg_edges_json: str = str(PROJECT_ROOT / "frontend" / "public" / "data" / "kg_edges.json")


@dataclass
class AppConfig:
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    bm25: BM25Config = field(default_factory=BM25Config)
    hybrid: HybridConfig = field(default_factory=HybridConfig)
    query_expansion: QueryExpansionConfig = field(default_factory=QueryExpansionConfig)
    answering: AnsweringConfig = field(default_factory=AnsweringConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    corpus: CorpusConfig = field(default_factory=CorpusConfig)


def load_config() -> AppConfig:
    """Load config with .env overrides."""
    cfg = AppConfig()

    # LLM config from env
    cfg.llm.api_key = os.environ.get("LLM_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    cfg.llm.base_url = os.environ.get("LLM_BASE_URL", os.environ.get("OPENAI_BASE_URL", ""))
    cfg.llm.model = os.environ.get("LLM_MODEL", os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    cfg.llm.temperature = float(os.environ.get("LLM_TEMPERATURE", "0.1"))
    cfg.llm.max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "2000"))

    # Embedding config from env
    cfg.embedding.provider = os.environ.get("EMBEDDING_PROVIDER", "local")
    cfg.embedding.model = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Hybrid config from env
    if os.environ.get("HYBRID_RETRIEVAL", "").lower() in ("false", "0"):
        cfg.hybrid.enabled = False

    return cfg
