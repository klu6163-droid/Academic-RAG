import type { EvidenceRow, DataQualityReport } from '../types';
import { useMemo } from 'react';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = ['#10b981', '#f59e0b', '#ef4444'];

export function DataQuality({ evidence, quality }: { evidence: EvidenceRow[]; quality: DataQualityReport }) {
  const manualCheck = useMemo(() => evidence.filter(e => e.needs_manual_check?.toLowerCase() === 'true'), [evidence]);
  const titleUncertain = useMemo(() => evidence.filter(e => e.title_uncertain?.toLowerCase() === 'true'), [evidence]);

  const qualityData = [
    { name: 'Good', value: evidence.length - manualCheck.length },
    { name: 'Manual Check', value: manualCheck.length },
  ];

  const cards = [
    { label: 'Total Evidence Rows', value: evidence.length, icon: Shield, color: 'text-blue-500' },
    { label: 'Manual Check Needed', value: manualCheck.length, icon: AlertTriangle, color: 'text-amber-500' },
    { label: 'Title Uncertain', value: titleUncertain.length, icon: AlertTriangle, color: 'text-red-500' },
    { label: 'Good Quality', value: evidence.length - manualCheck.length, icon: CheckCircle, color: 'text-green-500' },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Data Quality</h2>

      <div className="grid grid-cols-4 gap-4 mb-6">
        {cards.map(c => (
          <div key={c.label} className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center gap-2 mb-1">
              <c.icon size={16} className={c.color} />
              <span className="text-xs text-gray-500">{c.label}</span>
            </div>
            <div className="text-2xl font-bold">{c.value.toLocaleString()}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold mb-3">Evidence Quality Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={qualityData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                {qualityData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold mb-3">Quality Report</h3>
          <div className="text-sm text-gray-600 whitespace-pre-wrap max-h-60 overflow-auto leading-relaxed">{quality.content}</div>
        </div>
      </div>

      {manualCheck.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle size={16} className="text-amber-500" />
            Manual Check Queue ({manualCheck.length} rows, {quality.manual_check_papers?.length || 0} papers)
          </h3>
          <div className="max-h-80 overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-50">
                <tr className="text-left text-xs text-gray-500">
                  <th className="p-2">Paper ID</th>
                  <th className="p-2">Title</th>
                  <th className="p-2">Category</th>
                  <th className="p-2">Excerpt</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {manualCheck.slice(0, 50).map((r, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="p-2 text-xs font-mono">{r.paper_id}</td>
                    <td className="p-2 text-xs">{r.display_title || r.title}</td>
                    <td className="p-2 text-xs">{r.category.replace(/_/g, ' ')}</td>
                    <td className="p-2 text-xs text-gray-500 max-w-md truncate">{r.evidence_text.slice(0, 100)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {manualCheck.length > 50 && <p className="text-xs text-gray-400 mt-2">Showing 50 of {manualCheck.length} rows</p>}
        </div>
      )}

      {titleUncertain.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle size={16} className="text-red-500" />
            Uncertain Titles ({titleUncertain.length} rows)
          </h3>
          <div className="max-h-60 overflow-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-gray-50">
                <tr className="text-left text-xs text-gray-500">
                  <th className="p-2">Paper ID</th>
                  <th className="p-2">Original Title</th>
                  <th className="p-2">Display Title</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {titleUncertain.slice(0, 30).map((r, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="p-2 text-xs font-mono">{r.paper_id}</td>
                    <td className="p-2 text-xs text-gray-400">{r.original_title || '—'}</td>
                    <td className="p-2 text-xs">{r.display_title || r.title}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
