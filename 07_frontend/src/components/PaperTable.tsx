import React, { useState, useMemo } from 'react'
import type { PaperNode } from '../types'

interface Props {
  papers: PaperNode[]
  onPaperClick: (paperId: string) => void
}

export default function PaperTable({ papers, onPaperClick }: Props) {
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [yearFilter, setYearFilter] = useState('')
  const [sortField, setSortField] = useState<string>('id')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
  const [page, setPage] = useState(0)
  const pageSize = 50

  const categories = useMemo(() => {
    const cats = new Set(papers.map(p => p.category).filter(Boolean))
    return Array.from(cats).sort()
  }, [papers])

  const years = useMemo(() => {
    const yrs = new Set(papers.map(p => p.year).filter(Boolean))
    return Array.from(yrs).sort().reverse()
  }, [papers])

  const filtered = useMemo(() => {
    let result = papers

    if (search) {
      const q = search.toLowerCase()
      result = result.filter(p =>
        p.full_title.toLowerCase().includes(q) ||
        p.label.toLowerCase().includes(q) ||
        p.authors.toLowerCase().includes(q) ||
        p.journal.toLowerCase().includes(q) ||
        p.materials_raw.toLowerCase().includes(q) ||
        p.methods_raw.toLowerCase().includes(q) ||
        p.key_findings.toLowerCase().includes(q) ||
        p.id.toLowerCase().includes(q)
      )
    }

    if (categoryFilter) {
      result = result.filter(p => p.category === categoryFilter)
    }

    if (yearFilter) {
      result = result.filter(p => p.year === yearFilter)
    }

    result.sort((a, b) => {
      const aVal = ((a as any)[sortField] || '').toString()
      const bVal = ((b as any)[sortField] || '').toString()
      return sortDir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
    })

    return result
  }, [papers, search, categoryFilter, yearFilter, sortField, sortDir])

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('asc')
    }
    setPage(0)
  }

  const totalPages = Math.ceil(filtered.length / pageSize)
  const paged = filtered.slice(page * pageSize, (page + 1) * pageSize)

  return (
    <div>
      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-4 border border-gray-100">
        <div className="flex flex-wrap gap-3 items-center">
          <input
            type="text"
            placeholder="Search title, author, material, method, findings..."
            className="flex-1 min-w-[280px] px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0) }}
          />
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
            value={categoryFilter}
            onChange={e => { setCategoryFilter(e.target.value); setPage(0) }}
          >
            <option value="">All Categories</option>
            {categories.map(c => (
              <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
            ))}
          </select>
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
            value={yearFilter}
            onChange={e => { setYearFilter(e.target.value); setPage(0) }}
          >
            <option value="">All Years</option>
            {years.map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <span className="text-sm text-gray-500">{filtered.length} papers</span>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                {[
                  { field: 'id', label: 'ID', w: 'w-16' },
                  { field: 'full_title', label: 'Title', w: '' },
                  { field: 'year', label: 'Year', w: 'w-16' },
                  { field: 'journal', label: 'Journal', w: 'w-40' },
                  { field: 'category', label: 'Category', w: 'w-32' },
                ].map(col => (
                  <th
                    key={col.field}
                    className={`text-left py-3 px-3 text-xs font-semibold text-gray-500 uppercase cursor-pointer hover:text-gray-700 ${col.w}`}
                    onClick={() => handleSort(col.field)}
                  >
                    {col.label} {sortField === col.field ? (sortDir === 'asc' ? '↑' : '↓') : ''}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paged.map(p => (
                <tr
                  key={p.id}
                  className="border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition-colors"
                  onClick={() => onPaperClick(p.id)}
                >
                  <td className="py-3 px-3 font-mono text-blue-600 text-sm font-semibold">{p.id}</td>
                  <td className="py-3 px-3">
                    <div className="text-sm font-medium text-gray-900 truncate max-w-lg">{p.full_title || p.label}</div>
                    <div className="text-xs text-gray-400 truncate max-w-lg">{p.authors}</div>
                  </td>
                  <td className="py-3 px-3 text-sm text-gray-600">{p.year || '-'}</td>
                  <td className="py-3 px-3 text-sm text-gray-500 max-w-[160px] truncate">{p.journal || '-'}</td>
                  <td className="py-3 px-3">
                    <span className="inline-block px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">
                      {p.category.replace(/_/g, ' ')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
            <span className="text-sm text-gray-500">
              Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, filtered.length)} of {filtered.length}
            </span>
            <div className="flex gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage(p => p - 1)}
                className="px-3 py-1 text-sm border rounded disabled:opacity-40 hover:bg-white"
              >Prev</button>
              <span className="px-3 py-1 text-sm text-gray-600">{page + 1} / {totalPages}</span>
              <button
                disabled={page >= totalPages - 1}
                onClick={() => setPage(p => p + 1)}
                className="px-3 py-1 text-sm border rounded disabled:opacity-40 hover:bg-white"
              >Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
