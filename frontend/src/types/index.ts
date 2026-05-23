export interface EvidenceRow {
  paper_id: string;
  title: string;
  file_name: string;
  category: string;
  year: string;
  priority: string;
  extraction_quality: string;
  evidence_type: string;
  claim_type: string;
  evidence_text: string;
  figure_table_source: string;
  page_est: string;
  keyword: string;
  confidence: string;
  relevance: string;
  ml_feature_candidate: string;
  needs_manual_check: string;
  title_needs_cleanup: string;
  original_title: string;
  display_title: string;
  title_uncertain: string;
}

export interface KGNode {
  node_id: string;
  node_type: string;
  label: string;
  category: string;
  description: string;
  evidence_count: string;
  confidence: string;
  original_title: string;
  display_title: string;
  title_uncertain: string;
}

export interface KGEdge {
  source_id: string;
  target_id: string;
  edge_type: string;
  evidence_id: string;
  paper_id: string;
  confidence: string;
}

export interface DashboardStats {
  refined_cards: number;
  active_work_papers: number;
  cleaned_evidence_rows: number;
  manual_check_rows: number;
  kg_nodes: number;
  kg_edges: number;
  ml_feature_candidates: number;
  high_value_citations: number;
  page_missing: number;
  title_needs_cleanup: number;
  category_distribution: Record<string, number>;
  claim_type_distribution: Record<string, number>;
}

export interface ProjectSynthesis {
  title: string;
  file: string;
  sections: { heading: string; content: string }[];
}

export interface DataQualityReport {
  content: string;
  manual_check_papers: string[];
  title_cleanup_papers: string[];
  page_missing_count: number;
  extraction_quality?: { good: number; partial: number; poor: number };
  papers_with_evidence?: number;
  avg_confidence?: string;
  high_relevance_count?: number;
}

export type Page = 'dashboard' | 'ask' | 'evidence' | 'graph' | 'projects' | 'citations' | 'ml-features' | 'quality';
