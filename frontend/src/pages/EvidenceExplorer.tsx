import { useState, useMemo } from 'react';
import type { EvidenceRow } from '../types';
import { Search, Filter, ChevronDown, ChevronUp } from 'lucide-react';

export function EvidenceExplorer({ evidence }: { evidence: EvidenceRow[] }) {
  const [search, setSearch] = useState('');
  const [catFilter, setCatFilter] = useState('');
  const [claimFilter, setClaimFilter] = useState('');
  const [relFilter, setRelFilter] = useState('');
  const [confFilter, setConfFilter] = useState('');
  const [mlOnly, setMlOnly] = useState(false);
  const [manualOnly, setManualOnly] = useState(false);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 50;

  const categories = useMemo(() => [...new Set(evidence.map(e => e.category))].sort(), [evidence]);
  const claimTypes = useMemo(() => [...new Set(evidence.map(e => e.claim_type).filter(Boolean))].sort(), [evidence]);
  const relevances = useMemo(() => [...new Set(evidence.map(e => e.relevance).filter(Boolean))].sort(), [evidence]);
  const confidences = useMemo(() => [...new Set(evidence.map(e => e.confidence).filter(Boolean))].sort(), [evidence]);

  const filtered = useMemo(() => {
    let rows = evidence;
    if (search) {
      const q = search.toLowerCase();
      rows = rows.filter(r =>
        (r.evidence_text ?? '').toLowerCase().includes(q) ||
        (r.title ?? '').toLowerCase().includes(q) ||
        (r.keyword ?? '').toLowerCase().includes(q) ||
        r.paper_id.toLowerCase().includes(q)
      );
    }
    if (catFilter) rows = rows.filter(r => r.category === catFilter);
    if (claimFilter) rows = rows.filter(r => r.claim_type === claimFilter);
    if (relFilter) rows = rows.filter(r => r.relevance === relFilter);
    if (confFilter) rows = rows.filter(r => r.confidence === confFilter);
    if (mlOnly) rows = rows.filter(r => r.ml_feature_candidate?.toLowerCase() === 'true');
    if (manualOnly) rows = rows.filter(r => r.needs_manual_check?.toLowerCase() === 'true');
    return rows;
  }, [evidence, search, catFilter, claimFilter, relFilter, confFilter, mlOnly, manualOnly]);

  const paged = useMemo(() => filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE), [filtered, page]);
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);

  const toggle = (i: number) => {
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });
  };

  const Badge = ({ label, color }: { label: string; color: string }) => (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>{label}</span>
  );

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Evidence Explorer</h2>
      <div className="text-sm text-gray-500 mb-4">{filtered.length} rows / {evidence.length} total</div>

      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="flex items-center gap-2 mb-3">
          <Search size={16} className="text-gray-400" />
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0); }}
            placeholder="Search evidence text, title, keyword, paper_id..."
            className="flex-1 border rounded px-3 py-1.5 text-sm"
          />
        </div>
        <div className="flex flex-wrap gap-3 items-center">
          <Filter size={14} className="text-gray-400" />
          <select value={catFilter} onChange={e => { setCatFilter(e.target.value); setPage(0); }} className="border rounded px-2 py-1 text-sm">
            <option value="">All Categories</option>
            {categories.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
          </select>
          <select value={claimFilter} onChange={e => { setClaimFilter(e.target.value); setPage(0); }} className="border rounded px-2 py-1 text-sm">
            <option value="">All Claim Types</option>
            {claimTypes.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={relFilter} onChange={e => { setRelFilter(e.target.value); setPage(0); }} className="border rounded px-2 py-1 text-sm">
            <option value="">All Relevance</option>
            {relevances.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <select value={confFilter} onChange={e => { setConfFilter(e.target.value); setPage(0); }} className="border rounded px-2 py-1 text-sm">
            <option value="">All Confidence</option>
            {confidences.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <label className="flex items-center gap-1 text-sm cursor-pointer">
            <input type="checkbox" checked={mlOnly} onChange={e => { setMlOnly(e.target.checked); setPage(0); }} />
            ML Features
          </label>
          <label className="flex items-center gap-1 text-sm cursor-pointer">
            <input type="checkbox" checked={manualOnly} onChange={e => { setManualOnly(e.target.checked); setPage(0); }} />
            Manual Check
          </label>
        </div>
      </div>

      <div className="space-y-2">
        {paged.map((row, i) => {
          const idx = page * PAGE_SIZE + i;
          const isOpen = expanded.has(idx);
          return (
            <div key={idx} className="bg-white rounded-lg shadow-sm border">
              <button onClick={() => toggle(idx)} className="w-full text-left px-4 py-3 flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap gap-1.5 mb-1">
                    <Badge label={row.category.replace(/_/g, ' ')} color="bg-blue-100 text-blue-700" />
                    {row.claim_type && <Badge label={row.claim_type} color="bg-green-100 text-green-700" />}
                    {row.relevance && <Badge label={row.relevance} color={row.relevance === 'high' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'} />}
                    {row.ml_feature_candidate?.toLowerCase() === 'true' && <Badge label="ML Feature" color="bg-purple-100 text-purple-700" />}
                    {row.needs_manual_check?.toLowerCase() === 'true' && <Badge label="Manual Check" color="bg-red-100 text-red-700" />}
                  </div>
                  <p className="text-sm text-gray-700 line-clamp-2">{row.evidence_text}</p>
                  <p className="text-xs text-gray-400 mt-1">{row.display_title || row.title} | {row.paper_id}</p>
                </div>
                {isOpen ? <ChevronUp size={16} className="text-gray-400 mt-1 flex-shrink-0" /> : <ChevronDown size={16} className="text-gray-400 mt-1 flex-shrink-0" />}
              </button>
              {isOpen && (
                <div className="px-4 pb-3 border-t text-sm">
                  <p className="mt-2 text-gray-700 whitespace-pre-wrap">{row.evidence_text}</p>
                  <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-500">
                    <div><span className="font-medium">Paper:</span> {row.paper_id}</div>
                    <div><span className="font-medium">Title:</span> {row.display_title || row.title}</div>
                    <div><span className="font-medium">Keyword:</span> {row.keyword}</div>
                    <div><span className="font-medium">Confidence:</span> {row.confidence}</div>
                    <div><span className="font-medium">Evidence Type:</span> {row.evidence_type}</div>
                    <div><span className="font-medium">Figure/Table:</span> {row.figure_table_source}</div>
                    <div><span className="font-medium">Page est:</span> {row.page_est}</div>
                    <div><span className="font-medium">Year:</span> {row.year}</div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 mt-4">
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="px-3 py-1 rounded border text-sm disabled:opacity-40">Prev</button>
          <span className="text-sm text-gray-500">Page {page + 1} / {totalPages}</span>
          <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="px-3 py-1 rounded border text-sm disabled:opacity-40">Next</button>
        </div>
      )}
    </div>
  );
}
