import React, { useMemo } from 'react'
import type { PaperNode, GraphData } from '../types'

interface Props {
  papers: PaperNode[]
  data: GraphData
  query: string
  onPaperClick: (paperId: string) => void
}

export default function SearchPanel({ papers, data, query, onPaperClick }: Props) {
  const results = useMemo(() => {
    if (!query || query.length < 2) return null

    const q = query.toLowerCase()

    const paperResults = papers.filter(p =>
      p.full_title.toLowerCase().includes(q) ||
      p.label.toLowerCase().includes(q) ||
      p.authors.toLowerCase().includes(q) ||
      p.journal.toLowerCase().includes(q) ||
      p.materials_raw.toLowerCase().includes(q) ||
      p.methods_raw.toLowerCase().includes(q) ||
      p.key_findings.toLowerCase().includes(q) ||
      p.scientific_questions.toLowerCase().includes(q) ||
      p.category.toLowerCase().includes(q) ||
      p.institution.toLowerCase().includes(q) ||
      p.id.toLowerCase().includes(q)
    ).slice(0, 30)

    const materialResults = data.nodes
      .filter(n => n.type === 'Material' && n.label.toLowerCase().includes(q))
      .slice(0, 15)

    const methodResults = data.nodes
      .filter(n => n.type === 'Method' && n.label.toLowerCase().includes(q))
      .slice(0, 15)

    const conceptResults = data.nodes
      .filter(n => n.type === 'Concept' && n.label.toLowerCase().includes(q))
      .slice(0, 15)

    return { papers: paperResults, materials: materialResults, methods: methodResults, concepts: conceptResults }
  }, [papers, data, query])

  if (!query || query.length < 2) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
        <div className="text-4xl mb-4">🔍</div>
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Global Search</h3>
        <p className="text-gray-500">Enter at least 2 characters to search across all papers, materials, methods, and concepts.</p>
      </div>
    )
  }

  if (!results) return null

  const totalResults = results.papers.length + results.materials.length + results.methods.length + results.concepts.length

  return (
    <div>
      <div className="bg-white rounded-xl shadow-sm p-4 mb-4 border border-gray-100">
        <h3 className="text-base font-semibold text-gray-800">
          Search Results for &ldquo;{query}&rdquo;
          <span className="text-sm font-normal text-gray-500 ml-2">({totalResults} results)</span>
        </h3>
      </div>

      {/* Papers */}
      {results.papers.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4 border border-gray-100">
          <h4 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">Papers ({results.papers.length})</h4>
          <div className="space-y-2">
            {results.papers.map(p => (
              <div
                key={p.id}
                className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors"
                onClick={() => onPaperClick(p.id)}
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-blue-600 text-sm font-semibold">{p.id}</span>
                  <span className="font-medium text-sm text-gray-900">{p.full_title || p.label}</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {p.year && `${p.year} | `}{p.journal || ''} | {p.category.replace(/_/g, ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Materials */}
      {results.materials.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4 border border-gray-100">
          <h4 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">Materials ({results.materials.length})</h4>
          <div className="flex flex-wrap gap-2">
            {results.materials.map(m => (
              <span key={m.id} className="inline-block px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg text-sm">
                {m.label}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Methods */}
      {results.methods.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4 border border-gray-100">
          <h4 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">Methods ({results.methods.length})</h4>
          <div className="flex flex-wrap gap-2">
            {results.methods.map(m => (
              <span key={m.id} className="inline-block px-3 py-1.5 bg-purple-50 text-purple-700 rounded-lg text-sm">
                {m.label}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Concepts */}
      {results.concepts.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-5 mb-4 border border-gray-100">
          <h4 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">Concepts ({results.concepts.length})</h4>
          <div className="flex flex-wrap gap-2">
            {results.concepts.map(c => (
              <span key={c.id} className="inline-block px-3 py-1.5 bg-amber-50 text-amber-700 rounded-lg text-sm">
                {c.label}
              </span>
            ))}
          </div>
        </div>
      )}

      {totalResults === 0 && (
        <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100 text-center">
          <p className="text-gray-500">No results found for &ldquo;{query}&rdquo;.</p>
        </div>
      )}
    </div>
  )
}
