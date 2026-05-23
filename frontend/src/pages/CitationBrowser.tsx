import { useMemo, useState } from 'react';
import type { EvidenceRow } from '../types';
import { BookOpen, ExternalLink } from 'lucide-react';

export function CitationBrowser({ evidence }: { evidence: EvidenceRow[] }) {
  const [catFilter, setCatFilter] = useState('');

  const categories = useMemo(() => [...new Set(evidence.map(e => e.category))].sort(), [evidence]);

  const highValuePapers = useMemo(() => {
    let rows = evidence.filter(e => e.relevance === 'high_relevance_pu');
    if (catFilter) rows = rows.filter(r => r.category === catFilter);

    const byPaper = new Map<string, { paper_id: string; title: string; category: string; year: string; count: number; claims: Set<string>; excerpts: string[] }>();
    for (const r of rows) {
      const key = r.paper_id;
      if (!byPaper.has(key)) {
        byPaper.set(key, { paper_id: r.paper_id, title: r.display_title || r.title, category: r.category, year: r.year, count: 0, claims: new Set(), excerpts: [] });
      }
      const p = byPaper.get(key)!;
      p.count++;
      if (r.claim_type) p.claims.add(r.claim_type);
      if (p.excerpts.length < 3) p.excerpts.push(r.evidence_text.slice(0, 200));
    }

    return [...byPaper.values()]
      .map(p => ({ ...p, claims: [...p.claims] }))
      .sort((a, b) => b.count - a.count);
  }, [evidence, catFilter]);

  const byCategory = useMemo(() => {
    const map = new Map<string, typeof highValuePapers>();
    for (const p of highValuePapers) {
      if (!map.has(p.category)) map.set(p.category, []);
      map.get(p.category)!.push(p);
    }
    return [...map.entries()].sort((a, b) => b[1].length - a[1].length);
  }, [highValuePapers]);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Citation Browser</h2>
      <p className="text-sm text-gray-500 mb-4">{highValuePapers.length} high-relevance papers</p>

      <div className="mb-4">
        <select value={catFilter} onChange={e => setCatFilter(e.target.value)} className="border rounded px-2 py-1 text-sm bg-white shadow">
          <option value="">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
        </select>
      </div>

      <div className="space-y-6">
        {byCategory.map(([cat, papers]) => (
          <div key={cat}>
            <h3 className="text-lg font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <BookOpen size={16} />
              {cat.replace(/_/g, ' ')}
              <span className="text-sm font-normal text-gray-400">({papers.length} papers)</span>
            </h3>
            <div className="space-y-2">
              {papers.map(p => (
                <div key={p.paper_id} className="bg-white rounded-lg shadow-sm border p-4">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-sm font-medium text-gray-800">{p.title}</h4>
                      <p className="text-xs text-gray-400 mt-0.5">{p.paper_id} | {p.year} | {p.category.replace(/_/g, ' ')}</p>
                    </div>
                    <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-medium flex-shrink-0">{p.count} evidence</span>
                  </div>
                  {p.claims.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {p.claims.map(c => (
                        <span key={c} className="px-1.5 py-0.5 bg-green-50 text-green-700 rounded text-xs">{c}</span>
                      ))}
                    </div>
                  )}
                  {p.excerpts.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {p.excerpts.map((e, i) => (
                        <p key={i} className="text-xs text-gray-500 italic">"{e}..."</p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
