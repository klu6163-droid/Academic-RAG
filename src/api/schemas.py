"""Pydantic schemas for the RAG API."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=8, ge=1, le=50)
    mode: str = Field(default="evidence", pattern="^(evidence|full_paper|hybrid)$")
    answer_style: str = Field(default="concise", pattern="^(concise|detailed)$")
    filters: dict | None = None


class RetrieveRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=8, ge=1, le=50)
    mode: str = Field(default="evidence", pattern="^(evidence|full_paper|hybrid)$")
    filters: dict | None = None


class EvidenceItem(BaseModel):
    evidence_id: str
    paper_id: str
    title: str
    file_name: str
    pdf_page: str
    category: str
    claim_type: str
    relevance: str
    confidence: str
    excerpt: str
    score: float
    needs_manual_check: bool
    support_level: str = ""


class RetrievalInfo(BaseModel):
    top_k: int
    retrieved_count: int
    mode: str
    hybrid_retrieval: bool
    query_expansion_used: bool


class AskResponse(BaseModel):
    question: str
    answer: str
    confidence: str
    no_answer: bool
    evidence: list[EvidenceItem]
    evidence_levels: dict = {}
    retrieval: RetrievalInfo
    warnings: list[str]


class RetrieveResponse(BaseModel):
    question: str
    evidence: list[EvidenceItem]
    retrieval: RetrievalInfo
    warnings: list[str]


class HealthResponse(BaseModel):
    status: str
    rag_ready: bool


class ModeInfo(BaseModel):
    enabled: bool
    vector_count: int | None = None
    source: str = ""
    index_version: str = ""


class StatsResponse(BaseModel):
    evidence_rows: int
    unique_papers: int
    manual_check_rows: int
    ml_feature_candidates: int
    high_relevance: int
    rag_backend_mode: str
    available_modes: list[str]
    default_mode: str
    evidence_mode: ModeInfo
    full_paper_mode: ModeInfo
    retriever: str
    query_expansion: bool
    embedding_provider: str
    embedding_model: str
    llm_provider: str
    llm_model: str
    no_answer_gate: bool
    faiss_vectors: int
    bm25_ready: bool
    diversity_rerank: bool = False
    max_chunks_per_paper: int = 2
