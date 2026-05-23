/**
 * RAG API client.
 * Base URL from VITE_RAG_API_BASE_URL or defaults to http://localhost:8000
 */

const BASE = import.meta.env.VITE_RAG_API_BASE_URL || 'http://localhost:8001';

export type RetrievalMode = 'evidence' | 'full_paper' | 'hybrid';
export type AnswerStyle = 'concise' | 'detailed';

export interface EvidenceItem {
  evidence_id: string;
  paper_id: string;
  title: string;
  file_name: string;
  pdf_page: string;
  category: string;
  claim_type: string;
  relevance: string;
  confidence: string;
  excerpt: string;
  score: number;
  needs_manual_check: boolean;
  support_level: string;
}

export interface RetrievalInfo {
  top_k: number;
  retrieved_count: number;
  mode: string;
  hybrid_retrieval: boolean;
  query_expansion_used: boolean;
}

export interface AskResponse {
  question: string;
  answer: string;
  confidence: string;
  no_answer: boolean;
  evidence: EvidenceItem[];
  evidence_levels: Record<string, number[]>;
  retrieval: RetrievalInfo;
  warnings: string[];
}

export interface RetrieveResponse {
  question: string;
  evidence: EvidenceItem[];
  retrieval: RetrievalInfo;
  warnings: string[];
}

export interface HealthResponse {
  status: string;
  rag_ready: boolean;
}

export interface ModeInfo {
  enabled: boolean;
  vector_count: number | null;
  source: string;
  index_version: string;
}

export interface StatsResponse {
  evidence_rows: number;
  unique_papers: number;
  manual_check_rows: number;
  ml_feature_candidates: number;
  high_relevance: number;
  rag_backend_mode: string;
  available_modes: string[];
  default_mode: string;
  evidence_mode: ModeInfo;
  full_paper_mode: ModeInfo;
  retriever: string;
  query_expansion: boolean;
  embedding_provider: string;
  embedding_model: string;
  llm_provider: string;
  llm_model: string;
  no_answer_gate: boolean;
  faiss_vectors: number;
  bm25_ready: boolean;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${text.slice(0, 300)}`);
  }
  return res.json();
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${text.slice(0, 300)}`);
  }
  return res.json();
}

export async function getHealth(): Promise<HealthResponse> {
  return get('/health');
}

export async function getStats(): Promise<StatsResponse> {
  return get('/api/stats');
}

export async function askCorpus(payload: {
  question: string;
  top_k?: number;
  mode?: RetrievalMode;
  answer_style?: AnswerStyle;
  filters?: Record<string, unknown>;
}): Promise<AskResponse> {
  return post('/api/ask', payload);
}

export async function retrieveEvidence(payload: {
  question: string;
  top_k?: number;
  mode?: RetrievalMode;
  filters?: Record<string, unknown>;
}): Promise<RetrieveResponse> {
  return post('/api/retrieve', payload);
}
