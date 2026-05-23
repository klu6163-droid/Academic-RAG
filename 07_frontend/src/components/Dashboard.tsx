import React, { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import type { GraphData, PaperNode, Page } from '../types'

interface Props {
  data: GraphData
  papers: PaperNode[]
  onNavigate: (page: Page) => void
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#14b8a6', '#a855f7', '#e11d48']

export default function Dashboard({ data, papers, onNavigate }: Props) {
  const yearDist = useMemo(() => {
    return Object.entries(data.summary.years)
      .filter(([y]) => y && y !== 'Unknown')
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([year, count]) => ({ year, count }))
  }, [data])

  const categoryDist = useMemo(() => {
    return Object.entries(data.summary.categories)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 12)
      .map(([name, value]) => ({ name: name.replace(/_/g, ' '), value }))
  }, [data])

  const journalDist = useMemo(() => {
    return Object.entries(data.summary.journals)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([name, value]) => ({ name: name.length > 30 ? name.slice(0, 28) + '...' : name, value }))
  }, [data])

  const recentPapers = useMemo(() => {
    return papers
      .filter(p => p.year && parseInt(p.year) >= 2024)
      .sort((a, b) => (b.year || '').localeCompare(a.year || ''))
      .slice(0, 12)
  }, [papers])

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        {[
          { label: 'Papers', value: data.metadata.total_papers, color: 'text-blue-700' },
          { label: 'Materials', value: data.metadata.total_materials, color: 'text-emerald-700' },
          { label: 'Methods', value: data.metadata.total_methods, color: 'text-purple-700' },
          { label: 'Concepts', value: data.metadata.total_concepts, color: 'text-amber-700' },
          { label: 'Relationships', value: data.metadata.total_edges, color: 'text-rose-700' },
        ].map(s => (
          <div key={s.label} className="bg-white rounded-xl shadow-sm p-5 text-center border border-gray-100">
            <div className={`text-3xl font-bold ${s.color}`}>{s.value.toLocaleString()}</div>
            <div className="text-sm text-gray-500 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <h3 className="text-base font-semibold text-gray-800 mb-4">Publication Year Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={yearDist}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="year" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <h3 className="text-base font-semibold text-gray-800 mb-4">Research Categories</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={categoryDist}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => percent > 0.04 ? `${name} (${(percent * 100).toFixed(0)}%)` : ''}
                outerRadius={90}
                dataKey="value"
              >
                {categoryDist.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <h3 className="text-base font-semibold text-gray-800 mb-4">Top Journals</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={journalDist} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#10b981" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <h3 className="text-base font-semibold text-gray-800 mb-4">Top Institutions</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={Object.entries(data.summary.institutions).sort(([,a],[,b])=>b-a).slice(0,10).map(([name,value])=>({name:name.length>25?name.slice(0,23)+'...':name,value}))} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Papers */}
      <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-800">Recent Papers (2024-2026)</h3>
          <button onClick={() => onNavigate('papers')} className="text-sm text-blue-600 hover:text-blue-800">View all &rarr;</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">ID</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Title</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Year</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Category</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase">Journal</th>
              </tr>
            </thead>
            <tbody>
              {recentPapers.map(p => (
                <tr
                  key={p.id}
                  className="border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition-colors"
                  onClick={() => onNavigate('papers')}
                >
                  <td className="py-2.5 px-3 font-mono text-blue-600 text-sm font-semibold">{p.id}</td>
                  <td className="py-2.5 px-3 text-sm max-w-md truncate">{p.full_title || p.label}</td>
                  <td className="py-2.5 px-3 text-sm">{p.year}</td>
                  <td className="py-2.5 px-3">
                    <span className="inline-block px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">
                      {p.category.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-sm text-gray-500 max-w-[180px] truncate">{p.journal}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
