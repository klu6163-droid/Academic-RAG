import { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import type { KGNode, KGEdge } from '../types';
import ForceGraph2D from 'react-force-graph-2d';
import { Search, X } from 'lucide-react';

const NODE_COLORS: Record<string, string> = {
  Paper: '#3b82f6',
  Material: '#10b981',
  Method: '#f59e0b',
  Property: '#ef4444',
  Mechanism: '#8b5cf6',
  Project: '#ec4899',
  MLFeature: '#06b6d4',
};

export function KnowledgeGraph({ nodes, edges }: { nodes: KGNode[]; edges: KGEdge[] }) {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [selected, setSelected] = useState<KGNode | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dims, setDims] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setDims({ width, height });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const nodeTypes = useMemo(() => [...new Set(nodes.map(n => n.node_type))].sort(), [nodes]);

  const filteredNodes = useMemo(() => {
    let ns = nodes;
    if (typeFilter) ns = ns.filter(n => n.node_type === typeFilter);
    if (search) {
      const q = search.toLowerCase();
      ns = ns.filter(n => n.label.toLowerCase().includes(q) || n.description.toLowerCase().includes(q));
    }
    return ns;
  }, [nodes, typeFilter, search]);

  const filteredIds = useMemo(() => new Set(filteredNodes.map(n => n.node_id)), [filteredNodes]);

  const graphData = useMemo(() => {
    const gNodes = filteredNodes.map(n => ({ id: n.node_id, label: n.label, type: n.node_type, node: n }));
    const gEdges = edges
      .filter(e => filteredIds.has(e.source_id) && filteredIds.has(e.target_id))
      .map(e => ({ source: e.source_id, target: e.target_id, edge: e }));
    return { nodes: gNodes, links: gEdges };
  }, [filteredNodes, edges, filteredIds]);

  const nodeCanvasObject = useCallback((node: any, ctx: CanvasRenderingContext2D) => {
    const r = 5;
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    ctx.fillStyle = NODE_COLORS[node.type] || '#999';
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.font = '10px sans-serif';
    ctx.fillStyle = '#333';
    ctx.textAlign = 'center';
    ctx.fillText(node.label.length > 20 ? node.label.slice(0, 18) + '…' : node.label, node.x, node.y + r + 10);
  }, []);

  const handleClick = useCallback((node: any) => {
    setSelected(node.node || null);
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Knowledge Graph</h2>
      <div className="text-sm text-gray-500 mb-4">{filteredNodes.length} nodes / {graphData.links.length} edges</div>

      <div className="flex gap-3 mb-4">
        <div className="flex items-center gap-2 bg-white rounded-lg shadow px-3 py-1.5 flex-1 max-w-md">
          <Search size={14} className="text-gray-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search nodes..." className="flex-1 text-sm outline-none" />
          {search && <button onClick={() => setSearch('')}><X size={14} className="text-gray-400" /></button>}
        </div>
        <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} className="border rounded px-2 py-1 text-sm bg-white shadow">
          <option value="">All Types</option>
          {nodeTypes.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </div>

      <div className="flex gap-4">
        <div ref={containerRef} className="flex-1 bg-white rounded-lg shadow overflow-hidden" style={{ minHeight: 500 }}>
          <ForceGraph2D
            graphData={graphData}
            width={dims.width}
            height={dims.height}
            nodeCanvasObject={nodeCanvasObject}
            nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D) => {
              ctx.fillStyle = color;
              ctx.fillRect(node.x - 6, node.y - 6, 12, 12);
            }}
            onNodeClick={handleClick}
            linkColor={() => '#cbd5e1'}
            linkWidth={() => 0.5}
            linkDirectionalArrowLength={3}
            linkDirectionalArrowRelPos={1}
            cooldownTicks={100}
          />
        </div>

        {selected && (
          <div className="w-72 bg-white rounded-lg shadow p-4 self-start">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium px-2 py-0.5 rounded" style={{ backgroundColor: (NODE_COLORS[selected.node_type] || '#999') + '22', color: NODE_COLORS[selected.node_type] || '#999' }}>{selected.node_type}</span>
              <button onClick={() => setSelected(null)}><X size={14} className="text-gray-400" /></button>
            </div>
            <h3 className="font-semibold text-sm mb-2">{selected.label}</h3>
            <p className="text-xs text-gray-600 mb-3">{selected.description}</p>
            <div className="text-xs text-gray-400 space-y-1">
              <div><span className="font-medium">Category:</span> {selected.category}</div>
              <div><span className="font-medium">Evidence count:</span> {selected.evidence_count}</div>
              <div><span className="font-medium">Confidence:</span> {selected.confidence}</div>
              <div><span className="font-medium">Node ID:</span> {selected.node_id}</div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5 text-xs">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            <span>{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
