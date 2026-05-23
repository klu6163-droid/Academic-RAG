import React from 'react'
import type { Page } from '../types'

interface Props {
  currentPage: Page
  onNavigate: (page: Page) => void
}

const navItems: { page: Page; label: string; icon: string }[] = [
  { page: 'dashboard', label: 'Dashboard', icon: '📊' },
  { page: 'papers', label: 'Papers', icon: '📄' },
  { page: 'knowledge-graph', label: 'Knowledge Graph', icon: '🕸️' },
  { page: 'search', label: 'Search', icon: '🔍' },
]

export default function Sidebar({ currentPage, onNavigate }: Props) {
  return (
    <div className="w-56 bg-gradient-to-b from-slate-800 to-slate-900 text-white flex flex-col h-screen sticky top-0 shrink-0">
      <div className="p-5 border-b border-white/10">
        <h2 className="text-lg font-bold">📚 Literature</h2>
        <p className="text-xs text-blue-200 mt-1">412 papers analyzed</p>
      </div>
      <nav className="flex-1 p-3 mt-2">
        {navItems.map(item => (
          <button
            key={item.page}
            onClick={() => onNavigate(item.page)}
            className={`w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium mb-1 transition-all ${
              currentPage === item.page
                ? 'bg-blue-600/40 text-white border-l-2 border-blue-400'
                : 'text-slate-300 hover:bg-white/10 hover:text-white'
            }`}
          >
            <span className="mr-2">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="p-4 border-t border-white/10 text-xs text-slate-400">
        Deep reading complete<br/>
        456 PDFs &rarr; 412 unique entries
      </div>
    </div>
  )
}
