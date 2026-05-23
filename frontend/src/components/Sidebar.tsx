import type { Page } from '../types';
import { LayoutDashboard, MessageSquare, Search, Network, FolderOpen, BookOpen, Cpu, Shield } from 'lucide-react';

const items: { page: Page; label: string; icon: typeof LayoutDashboard }[] = [
  { page: 'dashboard', label: 'Overview', icon: LayoutDashboard },
  { page: 'ask', label: 'Ask Corpus', icon: MessageSquare },
  { page: 'evidence', label: 'Evidence Explorer', icon: Search },
  { page: 'graph', label: 'Knowledge Graph', icon: Network },
  { page: 'projects', label: 'Projects', icon: FolderOpen },
  { page: 'citations', label: 'Citations', icon: BookOpen },
  { page: 'ml-features', label: 'ML Features', icon: Cpu },
  { page: 'quality', label: 'Data Quality', icon: Shield },
];

export function Sidebar({ current, onNavigate }: { current: Page; onNavigate: (p: Page) => void }) {
  return (
    <aside className="w-56 bg-white border-r flex flex-col">
      <div className="p-4 border-b">
        <h1 className="text-lg font-bold text-gray-800">Literature RAG</h1>
        <p className="text-xs text-gray-500">Refined Corpus Dashboard</p>
      </div>
      <nav className="flex-1 p-2">
        {items.map(({ page, label, icon: Icon }) => (
          <button
            key={page}
            onClick={() => onNavigate(page)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm mb-1 transition-colors ${
              current === page ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Icon size={18} />
            {label}
          </button>
        ))}
      </nav>
      <div className="p-3 border-t text-xs text-gray-400">290 refined cards / 179 papers</div>
    </aside>
  );
}
