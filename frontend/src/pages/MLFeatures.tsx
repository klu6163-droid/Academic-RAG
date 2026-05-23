import { useMemo, useState } from 'react';
import type { EvidenceRow } from '../types';
import { Cpu, ChevronDown, ChevronUp } from 'lucide-react';

export function MLFeatures({ evidence }: { evidence: EvidenceRow[] }) {
  const [catFilter, setCatFilter] = useState('');
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const mlRows = useMemo(() => {
    let rows = evidence.filter(e => e.ml_feature_candidate?.toLowerCase() === 'true');
    if (catFilter) rows = rows.filter(r => r.category === catFilter);
    return rows;
  }, [evidence, catFilter]);

  const categories = useMemo(() => {
    const cats = evidence.filter(e => e.ml_feature_candidate?.toLowerCase() === 'true').map(e => e.category);
    return [...new Set(cats)].sort();
  }, [evidence]);

  const byCategory = useMemo(() => {
    const map = new Map<string, EvidenceRow[]>();
    for (const r of mlRows) {
      if (!map.has(r.category)) map.set(r.category, []);
      map.get(r.category)!.push(r);
    }
    return [...map.entries()].sort((a, b) => b[1].length - a[1].length);
  }, [mlRows]);

  const toggle = (i: number) => {
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">ML Feature Candidates</h2>
      <p className="text-sm text-gray-500 mb-4">{mlRows.length} evidence rows flagged as ML-feature candidates</p>

      <div className="mb-4 flex items-center gap-3">
        <Cpu size={16} className="text-purple-500" />
        <select value={catFilter} onChange={e => setCatFilter(e.target.value)} className="border rounded px-2 py-1 text-sm bg-white shadow">
          <option value="">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
        </select>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6 text-sm text-purple-800">
        <strong>ML Feature Candidates:</strong> Evidence rows containing quantitative data, spectral features, or property measurements
        that could serve as input features or regression targets for machine learning models predicting polyurethane properties.
      </div>

      <div className="space-y-4">
        {byCategory.map(([cat, rows]) => (
          <div key={cat} className="bg-white rounded-lg shadow">
            <div className="px-4 py-3 border-b">
              <h3 className="font-semibold text-gray-700">{cat.replace(/_/g, ' ')} <span className="text-sm font-normal text-gray-400">({rows.length} features)</span></h3>
            </div>
            <div className="divide-y">
              {rows.slice(0, 20).map((row, i) => {
                const isOpen = expanded.has(i);
                return (
                  <div key={i}>
                    <button onClick={() => toggle(i)} className="w-full text-left px-4 py-2.5 flex items-start justify-between gap-2 hover:bg-gray-50">
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap gap-1.5 mb-1">
                          {row.claim_type && <span className="px-1.5 py-0.5 bg-green-50 text-green-700 rounded text-xs">{row.claim_type}</span>}
                          {row.keyword && <span className="px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{row.keyword}</span>}
                          {row.confidence && <span className="px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{row.confidence}</span>}
                        </div>
                        <p className="text-sm text-gray-700 line-clamp-2">{row.evidence_text}</p>
                        <p className="text-xs text-gray-400 mt-0.5">{row.display_title || row.title}</p>
                      </div>
                      {isOpen ? <ChevronUp size={14} className="text-gray-400 mt-1 flex-shrink-0" /> : <ChevronDown size={14} className="text-gray-400 mt-1 flex-shrink-0" />}
                    </button>
                    {isOpen && (
                      <div className="px-4 pb-3 border-t text-sm">
                        <p className="mt-2 text-gray-700 whitespace-pre-wrap">{row.evidence_text}</p>
                        <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-500">
                          <div><span className="font-medium">Paper:</span> {row.paper_id}</div>
                          <div><span className="font-medium">Figure/Table:</span> {row.figure_table_source}</div>
                          <div><span className="font-medium">Page est:</span> {row.page_est}</div>
                          <div><span className="font-medium">Evidence Type:</span> {row.evidence_type}</div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
              {rows.length > 20 && (
                <div className="px-4 py-2 text-xs text-gray-400">...and {rows.length - 20} more</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
