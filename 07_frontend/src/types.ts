export interface PaperNode {
  id: string
  type: 'Paper'
  label: string
  full_title: string
  category: string
  year: string
  journal: string
  authors: string
  institution: string
  materials_raw: string
  methods_raw: string
  key_findings: string
  scientific_questions: string
}

export interface EntityNode {
  id: string
  type: 'Material' | 'Method' | 'Concept' | 'Institution'
  label: string
  category: string
}

export type GraphNode = PaperNode | EntityNode

export interface GraphEdge {
  source: string
  target: string
  relation: string
  weight?: number
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  summary: {
    categories: Record<string, number>
    years: Record<string, number>
    journals: Record<string, number>
    institutions: Record<string, number>
  }
  metadata: {
    total_papers: number
    total_materials: number
    total_methods: number
    total_concepts: number
    total_edges: number
  }
}

export type Page = 'dashboard' | 'papers' | 'paper-detail' | 'knowledge-graph' | 'search'
