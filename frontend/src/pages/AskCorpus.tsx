import { useState, useEffect } from 'react';
import type { EvidenceRow } from '../types';
import { askCorpus, retrieveEvidence, getHealth, getStats, type RetrievalMode, type AnswerStyle, type AskResponse, type RetrieveResponse, type HealthResponse, type StatsResponse } from '../lib/api';
import { Search, Send, Loader2, AlertTriangle, CheckCircle, XCircle, ChevronDown, ChevronUp, Wifi, WifiOff } from 'lucide-react';

export function AskCorpus({ evidence }: { evidence: EvidenceRow[] }) {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(8);
  const [mode, setMode] = useState<RetrievalMode>('evidence');
  const [answerStyle, setAnswerStyle] = useState<AnswerStyle>('concise');
  const [catFilter, setCatFilter] = useState<string[]>([]);
  const [claimFilter, setClaimFilter] = useState<string[]>([]);
  const [excludeManual, setExcludeManual] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AskResponse | RetrieveResponse | null>(null);
  const [isRetrieveOnly, setIsRetrieveOnly] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [expandedEv, setExpandedEv] = useState<Set<number>>(new Set());
  const [showFilters, setShowFilters] = useState(false);

  const categories = [...new Set(evidence.map(e => e.category))].sort();
  const claimTypes = [...new Set(evidence.map(e => e.claim_type).filter(Boolean))].sort();

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ status: 'unreachable', rag_ready: false }));
    getStats().then(setStats).catch(() => {});
  }, []);

  const toggleCat = (c: string) => {
    setCatFilter(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  };
  const toggleClaim = (c: string) => {
    setClaimFilter(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  };

  const handleAsk = async (retrieveOnly: boolean) => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setIsRetrieveOnly(retrieveOnly);
    setExpandedEv(new Set());

    const filters: Record<string, unknown> = {};
    if (catFilter.length > 0) filters.category = catFilter;
    if (claimFilter.length > 0) filters.claim_type = claimFilter;
    if (excludeManual) filters.exclude_manual_check = true;

    try {
      const payload = { question, top_k: topK, mode, answer_style: answerStyle, filters: Object.keys(filters).length ? filters : undefined };
      if (retrieveOnly) {
        const r = await retrieveEvidence(payload);
        setResult(r);
      } else {
        const r = await askCorpus(payload);
        setResult(r);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const toggleEv = (i: number) => {
    setExpandedEv(prev => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });
  };

  const askResult = result && !isRetrieveOnly ? (result as AskResponse) : null;
  const retResult = result && isRetrieveOnly ? (result as RetrieveResponse) : null;

  const Badge = ({ label, color }: { label: string; color: string }) => (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>{label}</span>
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Ask Corpus</h2>
        <div className="flex items-center gap-2 text-sm">
          {health?.rag_ready ? (
            <span className="flex items-center gap-1 text-green-600"><Wifi size={14} /> Backend connected</span>
          ) : (
            <span className="flex items-center gap-1 text-red-500"><WifiOff size={14} /> Backend unreachable</span>
          )}
        </div>
      </div>

      {/* Input area */}
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="flex gap-2 mb-3">
          <input
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleAsk(false)}
            placeholder="Ask a question about the literature corpus..."
            className="flex-1 border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={() => handleAsk(false)}
            disabled={loading || !question.trim()}
            className="px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading && !isRetrieveOnly ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
            Ask
          </button>
          <button
            onClick={() => handleAsk(true)}
            disabled={loading || !question.trim()}
            className="px-4 py-2.5 bg-gray-600 text-white rounded-lg text-sm font-medium hover:bg-gray-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading && isRetrieveOnly ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
            Retrieve
          </button>
        </div>

        {/* Filters toggle */}
        <button onClick={() => setShowFilters(!showFilters)} className="text-sm text-gray-500 flex items-center gap-1 hover:text-gray-700">
          {showFilters ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          Filters & Options
        </button>

        {showFilters && (
          <div className="mt-3 pt-3 border-t space-y-3">
            {/* Mode selector */}
            <div>
              <div className="text-sm text-gray-600 mb-1.5">Retrieval Mode:</div>
              <div className="flex gap-2">
                {([
                  { value: 'evidence', label: 'Curated Evidence', desc: '1858 cleaned evidence rows, recommended', enabled: true },
                  { value: 'full_paper', label: 'Full Paper Chunks', desc: 'All PDF chunks, broader but noisier', enabled: stats?.full_paper_mode?.enabled ?? false },
                  { value: 'hybrid', label: 'Hybrid', desc: 'Evidence first, fallback to full paper', enabled: stats?.full_paper_mode?.enabled ?? false },
                ] as const).map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => opt.enabled && setMode(opt.value)}
                    disabled={!opt.enabled}
                    className={`px-3 py-1.5 rounded text-xs border transition-colors text-left ${
                      mode === opt.value
                        ? 'bg-blue-100 border-blue-300 text-blue-700'
                        : opt.enabled
                          ? 'bg-gray-50 border-gray-200 text-gray-500 hover:bg-gray-100'
                          : 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
                    }`}
                    title={opt.desc}
                  >
                    <div className="font-medium">{opt.label}</div>
                    <div className="text-xs opacity-75">{opt.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Answer Style selector */}
            <div>
              <div className="text-sm text-gray-600 mb-1.5">Answer Style:</div>
              <div className="flex gap-2">
                {([
                  { value: 'concise', label: 'Concise', desc: '300-600 chars, 3 conclusions max, recommended' },
                  { value: 'detailed', label: 'Detailed', desc: 'Full analysis with all evidence discussion' },
                ] as const).map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setAnswerStyle(opt.value)}
                    className={`px-3 py-1.5 rounded text-xs border transition-colors text-left ${
                      answerStyle === opt.value
                        ? 'bg-blue-100 border-blue-300 text-blue-700'
                        : 'bg-gray-50 border-gray-200 text-gray-500 hover:bg-gray-100'
                    }`}
                    title={opt.desc}
                  >
                    <div className="font-medium">{opt.label}</div>
                    <div className="text-xs opacity-75">{opt.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-4">
              <label className="text-sm text-gray-600">Top K:</label>
              <select value={topK} onChange={e => setTopK(Number(e.target.value))} className="border rounded px-2 py-1 text-sm">
                {[3, 5, 8, 10, 15, 20].map(v => <option key={v} value={v}>{v}</option>)}
              </select>
              <label className="flex items-center gap-1.5 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" checked={excludeManual} onChange={e => setExcludeManual(e.target.checked)} />
                Exclude manual check
              </label>
            </div>

            <div>
              <div className="text-sm text-gray-600 mb-1">Category filter:</div>
              <div className="flex flex-wrap gap-1.5">
                {categories.map(c => (
                  <button
                    key={c}
                    onClick={() => toggleCat(c)}
                    className={`px-2 py-0.5 rounded text-xs border transition-colors ${
                      catFilter.includes(c) ? 'bg-blue-100 border-blue-300 text-blue-700' : 'bg-gray-50 border-gray-200 text-gray-500 hover:bg-gray-100'
                    }`}
                  >
                    {c.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <div className="text-sm text-gray-600 mb-1">Claim type filter:</div>
              <div className="flex flex-wrap gap-1.5">
                {claimTypes.map(c => (
                  <button
                    key={c}
                    onClick={() => toggleClaim(c)}
                    className={`px-2 py-0.5 rounded text-xs border transition-colors ${
                      claimFilter.includes(c) ? 'bg-green-100 border-green-300 text-green-700' : 'bg-gray-50 border-gray-200 text-gray-500 hover:bg-gray-100'
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 flex items-start gap-2">
          <XCircle size={16} className="text-red-500 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-red-700">{error}</div>
        </div>
      )}

      {/* Warnings */}
      {result?.warnings && result.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4 space-y-1">
          {result.warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2 text-sm text-yellow-800">
              <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" />
              {w}
            </div>
          ))}
        </div>
      )}

      {/* Answer */}
      {askResult && (
        <div className="bg-white rounded-lg shadow p-5 mb-4">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="font-semibold text-gray-800">Answer</h3>
            <Badge
              label={askResult.confidence}
              color={askResult.confidence === 'High' ? 'bg-green-100 text-green-700' : askResult.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}
            />
            {askResult.no_answer ? (
              <Badge label="No Answer" color="bg-red-100 text-red-700" />
            ) : (
              <Badge label="Answered" color="bg-green-100 text-green-700" />
            )}
          </div>
          <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{askResult.answer || 'No answer generated.'}</div>
        </div>
      )}

      {/* Evidence cards */}
      {result && result.evidence.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Search size={16} />
            Retrieved Evidence ({result.evidence.length} rows)
          </h3>
          <div className="space-y-2">
            {result.evidence.map((ev, i) => {
              const isOpen = expandedEv.has(i);
              return (
                <div key={i} className="bg-white rounded-lg shadow-sm border">
                  <button onClick={() => toggleEv(i)} className="w-full text-left px-4 py-3 flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap gap-1.5 mb-1">
                        <Badge label={ev.category.replace(/_/g, ' ')} color="bg-blue-100 text-blue-700" />
                        {ev.claim_type && <Badge label={ev.claim_type} color="bg-green-100 text-green-700" />}
                        {ev.relevance === 'high_relevance_pu' && <Badge label="High Relevance" color="bg-amber-100 text-amber-700" />}
                        {ev.needs_manual_check && <Badge label="Manual Check" color="bg-red-100 text-red-700" />}
                        {ev.support_level === 'direct' && <Badge label="Direct" color="bg-emerald-100 text-emerald-700" />}
                        {ev.support_level === 'equivalent_concept' && <Badge label="Equiv. Concept" color="bg-teal-100 text-teal-700" />}
                        {ev.support_level === 'partial' && <Badge label="Partial" color="bg-orange-100 text-orange-700" />}
                        {ev.support_level === 'insufficient' && <Badge label="Insufficient" color="bg-gray-100 text-gray-500" />}
                        <span className="text-xs text-gray-400">score: {ev.score}</span>
                      </div>
                      <p className="text-sm text-gray-700 line-clamp-2">{ev.excerpt}</p>
                      <p className="text-xs text-gray-400 mt-1">{ev.paper_id} | {ev.title} | p.{ev.pdf_page || '?'}</p>
                    </div>
                    {isOpen ? <ChevronUp size={16} className="text-gray-400 mt-1 flex-shrink-0" /> : <ChevronDown size={16} className="text-gray-400 mt-1 flex-shrink-0" />}
                  </button>
                  {isOpen && (
                    <div className="px-4 pb-3 border-t text-sm">
                      <p className="mt-2 text-gray-700 whitespace-pre-wrap">{ev.excerpt}</p>
                      <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-500">
                        <div><span className="font-medium">Paper ID:</span> {ev.paper_id}</div>
                        <div><span className="font-medium">Title:</span> {ev.title}</div>
                        <div><span className="font-medium">File:</span> {ev.file_name}</div>
                        <div><span className="font-medium">PDF Page:</span> {ev.pdf_page || '—'}</div>
                        <div><span className="font-medium">Category:</span> {ev.category.replace(/_/g, ' ')}</div>
                        <div><span className="font-medium">Claim Type:</span> {ev.claim_type || '—'}</div>
                        <div><span className="font-medium">Confidence:</span> {ev.confidence}</div>
                        <div><span className="font-medium">Relevance:</span> {ev.relevance}</div>
                        <div><span className="font-medium">Score:</span> {ev.score}</div>
                        {ev.support_level && <div><span className="font-medium">Support Level:</span> {ev.support_level.replace(/_/g, ' ')}</div>}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* No results */}
      {result && result.evidence.length === 0 && (
        <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-500">
          No evidence found for this question.
        </div>
      )}
    </div>
  );
}
