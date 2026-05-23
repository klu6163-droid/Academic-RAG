import React, { useMemo } from 'react'
import type { PaperNode, GraphData } from '../types'

interface Props {
  paper: PaperNode
  data: GraphData
  onBack: () => void
}

export default function PaperDetail({ paper, data, onBack }: Props) {
  // Find connected nodes
  const connections = useMemo(() => {
    const materials: string[] = []
    const methods: string[] = []
    const concepts: string[] = []
    const institutions: string[] = []
    const relatedPapers: string[] = []

    for (const edge of data.edges) {
      if (edge.source === paper.id) {
        const targetNode = data.nodes.find(n => n.id === edge.target)
        if (!targetNode) continue
        if (edge.relation === 'studies') materials.push(targetNode.label)
        else if (edge.relation === 'uses') methods.push(targetNode.label)
        else if (edge.relation === 'addresses') concepts.push(targetNode.label)
        else if (edge.relation === 'from') institutions.push(targetNode.label)
        else if (edge.relation.startsWith('related_')) relatedPapers.push(edge.target)
      } else if (edge.target === paper.id) {
        const sourceNode = data.nodes.find(n => n.id === edge.source)
        if (!sourceNode) continue
        if (edge.relation === 'studies') materials.push(sourceNode.label)
        else if (edge.relation === 'uses') methods.push(sourceNode.label)
        else if (edge.relation === 'addresses') concepts.push(sourceNode.label)
        else if (edge.relation === 'from') institutions.push(sourceNode.label)
        else if (edge.relation.startsWith('related_')) relatedPapers.push(edge.source)
      }
    }

    return {
      materials: [...new Set(materials)],
      methods: [...new Set(methods)],
      concepts: [...new Set(concepts)],
      institutions: [...new Set(institutions)],
      relatedPapers: [...new Set(relatedPapers)],
    }
  }, [paper, data])

  return (
    <div>
      <button
        className="mb-4 text-blue-600 hover:text-blue-800 flex items-center gap-1 text-sm font-medium"
        onClick={onBack}
      >
        &larr; Back to Papers
      </button>

      {/* Paper Info */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-4 border border-gray-100">
        <div className="flex items-start justify-between mb-4">
          <div>
            <span className="inline-block px-2 py-1 bg-blue-100 text-blue-700 rounded font-mono text-sm font-bold mr-3">{paper.id}</span>
            <span className="inline-block px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">{paper.category.replace(/_/g, ' ')}</span>
          </div>
          <span className="text-sm text-gray-500">{paper.year}</span>
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-3">{paper.full_title || paper.label}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400 text-xs uppercase tracking-wide">Authors</span>
            <div className="text-gray-700 mt-1">{paper.authors || 'Not extracted'}</div>
          </div>
          <div>
            <span className="text-gray-400 text-xs uppercase tracking-wide">Institution</span>
            <div className="text-gray-700 mt-1">{paper.institution || 'Not extracted'}</div>
          </div>
          <div className="md:col-span-2">
            <span className="text-gray-400 text-xs uppercase tracking-wide">Journal</span>
            <div className="text-gray-700 mt-1">{paper.journal || 'Not identified'}</div>
          </div>
        </div>
      </div>

      {/* Materials */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-4 border border-gray-100">
        <h3 className="text-base font-semibold text-gray-800 mb-3">Materials</h3>
        <p className="text-sm text-gray-700 leading-relaxed">{paper.materials_raw || 'Not extracted'}</p>
        {connections.materials.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {connections.materials.map(m => (
              <span key={m} className="inline-block px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded text-xs">{m}</span>
            ))}
          </div>
        )}
      </div>

      {/* Methods */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-4 border border-gray-100">
        <h3 className="text-base font-semibold text-gray-800 mb-3">Methods</h3>
        <p className="text-sm text-gray-700 leading-relaxed">{paper.methods_raw || 'Not extracted'}</p>
        {connections.methods.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {connections.methods.map(m => (
              <span key={m} className="inline-block px-2 py-0.5 bg-purple-50 text-purple-700 rounded text-xs">{m}</span>
            ))}
          </div>
        )}
      </div>

      {/* Key Findings */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-4 border border-gray-100">
        <h3 className="text-base font-semibold text-gray-800 mb-3">Key Findings</h3>
        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{paper.key_findings || 'Not extracted'}</p>
      </div>

      {/* Scientific Questions */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-4 border border-gray-100">
        <h3 className="text-base font-semibold text-gray-800 mb-3">Scientific Questions</h3>
        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{paper.scientific_questions || 'Not extracted'}</p>
        {connections.concepts.length > 0 && (
          <div className="mt-4">
            <span className="text-xs text-gray-400 uppercase tracking-wide">Related Concepts</span>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {connections.concepts.map(c => (
                <span key={c} className="inline-block px-2 py-0.5 bg-amber-50 text-amber-700 rounded text-xs">{c}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Related Papers */}
      {connections.relatedPapers.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-4 border border-gray-100">
          <h3 className="text-base font-semibold text-gray-800 mb-3">Related Papers ({connections.relatedPapers.length})</h3>
          <div className="space-y-2">
            {connections.relatedPapers.slice(0, 10).map(pid => {
              const related = data.nodes.find(n => n.id === pid) as PaperNode | undefined
              if (!related) return null
              return (
                <div key={pid} className="p-2 bg-gray-50 rounded-lg text-sm">
                  <span className="font-mono text-blue-600 mr-2">{pid}</span>
                  <span className="text-gray-700">{related.full_title || related.label}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
