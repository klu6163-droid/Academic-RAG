import type { DashboardStats, EvidenceRow } from '../types';
import { BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const COLORS = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4','#84cc16','#f97316','#6366f1','#14b8a6'];

export function Dashboard({ stats, evidence }: { stats: DashboardStats; evidence: EvidenceRow[] }) {
  const catData = Object.entries(stats.category_distribution).map(([name, value]) => ({ name: name.replace(/_/g, ' '), value }));
  const claimData = Object.entries(stats.claim_type_distribution).map(([name, value]) => ({ name, value }));

  const cards = [
    { label: 'Refined Cards', value: stats.refined_cards, color: 'bg-blue-500' },
    { label: 'Active Papers', value: stats.active_work_papers, color: 'bg-green-500' },
    { label: 'Evidence Rows', value: stats.cleaned_evidence_rows, color: 'bg-purple-500' },
    { label: 'KG Nodes', value: stats.kg_nodes, color: 'bg-cyan-500' },
    { label: 'KG Edges', value: stats.kg_edges, color: 'bg-indigo-500' },
    { label: 'ML Features', value: stats.ml_feature_candidates, color: 'bg-pink-500' },
    { label: 'High Relevance', value: stats.high_value_citations, color: 'bg-amber-500' },
    { label: 'Manual Check', value: stats.manual_check_rows, color: 'bg-red-500' },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Overview Dashboard</h2>
      <div className="grid grid-cols-4 gap-4 mb-8">
        {cards.map(c => (
          <div key={c.label} className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">{c.label}</div>
            <div className="text-2xl font-bold mt-1">{(c.value ?? 0).toLocaleString()}</div>
          </div>
        ))}
      </div>

      {stats.manual_check_rows > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <span className="text-yellow-800 font-medium">Warning: {stats.manual_check_rows} evidence rows from papers with partial extraction need manual check.</span>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold mb-3">Evidence by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={catData} layout="vertical" margin={{ left: 120 }}>
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold mb-3">Claim Type Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={claimData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {claimData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
