import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react'
import type { GraphData, GraphNode, PaperNode } from '../types'

interface Props {
  data: GraphData
  onPaperClick: (paperId: string) => void
}

const NODE_COLORS: Record<string, string> = {
  Paper: '#3b82f6',
  Material: '#10b981',
  Method: '#8b5cf6',
  Concept: '#f59e0b',
  Institution: '#ef4444',
}

const NODE_SIZES: Record<string, number> = {
  Paper: 4,
  Material: 6,
  Method: 5,
  Concept: 7,
  Institution: 5,
}

interface SimNode {
  id: string
  x: number
  y: number
  vx: number
  vy: number
  node: GraphNode
  radius: number
}

interface SimEdge {
  source: string
  target: string
  relation: string
}

export default function KnowledgeGraph({ data, onPaperClick }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [search, setSearch] = useState('')
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [showEdges, setShowEdges] = useState(true)
  const [maxNodes, setMaxNodes] = useState(200)
  const nodesRef = useRef<Map<string, SimNode>>(new Map())
  const edgesRef = useRef<SimEdge[]>([])
  const animRef = useRef<number>(0)
  const draggingRef = useRef<{ node: SimNode; offsetX: number; offsetY: number } | null>(null)
  const panRef = useRef({ x: 0, y: 0, scale: 1 })

  // Filter nodes
  const { displayNodes, displayEdges } = useMemo(() => {
    let nodes = data.nodes
    if (typeFilter !== 'all') {
      nodes = nodes.filter(n => n.type === typeFilter)
    }
    if (search) {
      const q = search.toLowerCase()
      nodes = nodes.filter(n =>
        n.label.toLowerCase().includes(q) ||
        n.id.toLowerCase().includes(q)
      )
    }

    // Limit nodes for performance
    const paperNodes = nodes.filter(n => n.type === 'Paper')
    const otherNodes = nodes.filter(n => n.type !== 'Paper')

    // Sort papers by connectedness
    const edgeCounts = new Map<string, number>()
    for (const e of data.edges) {
      edgeCounts.set(e.source, (edgeCounts.get(e.source) || 0) + 1)
      edgeCounts.set(e.target, (edgeCounts.get(e.target) || 0) + 1)
    }

    paperNodes.sort((a, b) => (edgeCounts.get(b.id) || 0) - (edgeCounts.get(a.id) || 0))
    otherNodes.sort((a, b) => (edgeCounts.get(b.id) || 0) - (edgeCounts.get(a.id) || 0))

    const limitedPapers = paperNodes.slice(0, Math.min(80, Math.floor(maxNodes * 0.4)))
    const limitedOthers = otherNodes.slice(0, maxNodes - limitedPapers.length)
    const displayNodes = [...limitedPapers, ...limitedOthers]
    const nodeIds = new Set(displayNodes.map(n => n.id))

    const displayEdges = data.edges.filter(e =>
      nodeIds.has(e.source) && nodeIds.has(e.target) &&
      (e.relation === 'studies' || e.relation === 'uses' || e.relation === 'addresses' || e.relation === 'from' || e.relation.startsWith('related_'))
    ).slice(0, 1000)

    return { displayNodes, displayEdges }
  }, [data, typeFilter, search, maxNodes])

  // Initialize simulation
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const w = canvas.parentElement?.clientWidth || 800
    const h = 600
    canvas.width = w
    canvas.height = h

    // Init positions
    const nodes = new Map<string, SimNode>()
    const cx = w / 2
    const cy = h / 2

    for (const n of displayNodes) {
      const existing = nodesRef.current.get(n.id)
      if (existing) {
        nodes.set(n.id, { ...existing, node: n })
      } else {
        const angle = Math.random() * Math.PI * 2
        const r = 100 + Math.random() * 200
        nodes.set(n.id, {
          id: n.id,
          x: cx + Math.cos(angle) * r,
          y: cy + Math.sin(angle) * r,
          vx: 0,
          vy: 0,
          node: n,
          radius: NODE_SIZES[n.type] || 4,
        })
      }
    }

    nodesRef.current = nodes
    edgesRef.current = displayEdges

    // Force simulation
    let running = true
    let tick = 0

    const simulate = () => {
      if (!running || tick > 300) return
      tick++

      const nodeArr = Array.from(nodes.values())
      const alpha = Math.max(0.01, 1 - tick / 300)

      // Repulsion
      for (let i = 0; i < nodeArr.length; i++) {
        for (let j = i + 1; j < nodeArr.length; j++) {
          const a = nodeArr[i]
          const b = nodeArr[j]
          let dx = b.x - a.x
          let dy = b.y - a.y
          const dist = Math.sqrt(dx * dx + dy * dy) || 1
          const force = -500 * alpha / (dist * dist)
          const fx = dx / dist * force
          const fy = dy / dist * force
          a.vx -= fx
          a.vy -= fy
          b.vx += fx
          b.vy += fy
        }
      }

      // Attraction (edges)
      for (const edge of displayEdges) {
        const a = nodes.get(edge.source)
        const b = nodes.get(edge.target)
        if (!a || !b) continue
        const dx = b.x - a.x
        const dy = b.y - a.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = (dist - 80) * 0.005 * alpha
        const fx = dx / dist * force
        const fy = dy / dist * force
        a.vx += fx
        a.vy += fy
        b.vx -= fx
        b.vy -= fy
      }

      // Center gravity
      for (const n of nodeArr) {
        n.vx += (cx - n.x) * 0.001 * alpha
        n.vy += (cy - n.y) * 0.001 * alpha
      }

      // Update positions
      for (const n of nodeArr) {
        if (draggingRef.current?.node.id === n.id) continue
        n.vx *= 0.85
        n.vy *= 0.85
        n.x += n.vx
        n.y += n.vy
        n.x = Math.max(20, Math.min(w - 20, n.x))
        n.y = Math.max(20, Math.min(h - 20, n.y))
      }

      animRef.current = requestAnimationFrame(simulate)
    }

    animRef.current = requestAnimationFrame(simulate)

    return () => {
      running = false
      cancelAnimationFrame(animRef.current)
    }
  }, [displayNodes, displayEdges])

  // Render
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const render = () => {
      const w = canvas.width
      const h = canvas.height
      const pan = panRef.current

      ctx.clearRect(0, 0, w, h)
      ctx.save()
      ctx.translate(pan.x, pan.y)
      ctx.scale(pan.scale, pan.scale)

      // Draw edges
      if (showEdges) {
        for (const edge of edgesRef.current) {
          const a = nodesRef.current.get(edge.source)
          const b = nodesRef.current.get(edge.target)
          if (!a || !b) continue

          const isHighlighted = hoveredNode === edge.source || hoveredNode === edge.target || selectedNode === edge.source || selectedNode === edge.target
          ctx.strokeStyle = isHighlighted ? 'rgba(59,130,246,0.4)' : 'rgba(200,200,200,0.3)'
          ctx.lineWidth = isHighlighted ? 1.5 : 0.5
          ctx.beginPath()
          ctx.moveTo(a.x, a.y)
          ctx.lineTo(b.x, b.y)
          ctx.stroke()
        }
      }

      // Draw nodes
      for (const [, n] of nodesRef.current) {
        const color = NODE_COLORS[n.node.type] || '#888'
        const isHovered = hoveredNode === n.id
        const isSelected = selectedNode === n.id
        const r = isHovered || isSelected ? n.radius * 1.5 : n.radius

        ctx.fillStyle = color
        ctx.globalAlpha = isHovered || isSelected ? 1 : 0.7
        ctx.beginPath()
        ctx.arc(n.x, n.y, r, 0, Math.PI * 2)
        ctx.fill()

        if (isHovered || isSelected) {
          ctx.strokeStyle = '#1e293b'
          ctx.lineWidth = 1.5
          ctx.stroke()

          // Label
          ctx.fillStyle = '#1e293b'
          ctx.font = '11px sans-serif'
          ctx.textAlign = 'center'
          const label = n.node.label.length > 40 ? n.node.label.slice(0, 38) + '...' : n.node.label
          ctx.fillText(label, n.x, n.y - r - 5)
        }
      }

      ctx.globalAlpha = 1
      ctx.restore()

      requestAnimationFrame(render)
    }

    const animId = requestAnimationFrame(render)
    return () => cancelAnimationFrame(animId)
  }, [hoveredNode, selectedNode, showEdges])

  // Mouse interaction
  const getNodeAt = useCallback((mx: number, my: number): SimNode | null => {
    const pan = panRef.current
    const x = (mx - pan.x) / pan.scale
    const y = (my - pan.y) / pan.scale

    for (const [, n] of nodesRef.current) {
      const dx = n.x - x
      const dy = n.y - y
      if (dx * dx + dy * dy < (n.radius + 5) * (n.radius + 5)) {
        return n
      }
    }
    return null
  }, [])

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top

    if (draggingRef.current) {
      const pan = panRef.current
      draggingRef.current.node.x = (mx - pan.x) / pan.scale - draggingRef.current.offsetX
      draggingRef.current.node.y = (my - pan.y) / pan.scale - draggingRef.current.offsetY
      draggingRef.current.node.vx = 0
      draggingRef.current.node.vy = 0
      return
    }

    const node = getNodeAt(mx, my)
    setHoveredNode(node?.id || null)
  }, [getNodeAt])

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const node = getNodeAt(mx, my)

    if (node) {
      const pan = panRef.current
      draggingRef.current = {
        node,
        offsetX: (mx - pan.x) / pan.scale - node.x,
        offsetY: (my - pan.y) / pan.scale - node.y,
      }
      setSelectedNode(node.id)
    }
  }, [getNodeAt])

  const handleMouseUp = useCallback(() => {
    draggingRef.current = null
  }, [])

  const handleWheel = useCallback((e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    panRef.current.scale = Math.max(0.3, Math.min(3, panRef.current.scale * delta))
  }, [])

  const handleDoubleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current!.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const node = getNodeAt(mx, my)
    if (node && node.node.type === 'Paper') {
      onPaperClick(node.id)
    }
  }, [getNodeAt, onPaperClick])

  // Stats
  const nodeTypeStats = useMemo(() => {
    const stats: Record<string, number> = {}
    for (const n of displayNodes) {
      stats[n.type] = (stats[n.type] || 0) + 1
    }
    return Object.entries(stats).sort(([, a], [, b]) => b - a)
  }, [displayNodes])

  const selectedNodeData = useMemo(() => {
    if (!selectedNode) return null
    return displayNodes.find(n => n.id === selectedNode)
  }, [selectedNode, displayNodes])

  return (
    <div>
      {/* Controls */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-4 border border-gray-100">
        <div className="flex flex-wrap gap-3 items-center">
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
            value={typeFilter}
            onChange={e => setTypeFilter(e.target.value)}
          >
            <option value="all">All Node Types</option>
            {['Paper', 'Material', 'Method', 'Concept', 'Institution'].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Search nodes..."
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm flex-1 min-w-[200px] focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input type="checkbox" checked={showEdges} onChange={e => setShowEdges(e.target.checked)} />
            Show edges
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-600">
            Max nodes:
            <select
              className="px-2 py-1 border border-gray-300 rounded text-sm"
              value={maxNodes}
              onChange={e => setMaxNodes(Number(e.target.value))}
            >
              <option value={100}>100</option>
              <option value={200}>200</option>
              <option value={500}>500</option>
            </select>
          </label>
          <span className="text-sm text-gray-500">{displayNodes.length} nodes, {displayEdges.length} edges</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
        {nodeTypeStats.map(([type, count]) => (
          <div key={type} className="bg-white rounded-lg shadow-sm p-3 text-center border border-gray-100">
            <div className="text-lg font-bold" style={{ color: NODE_COLORS[type] }}>{count}</div>
            <div className="text-xs text-gray-500">{type}</div>
          </div>
        ))}
      </div>

      {/* Canvas */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-4">
        <canvas
          ref={canvasRef}
          className="w-full cursor-grab active:cursor-grabbing"
          style={{ height: '600px' }}
          onMouseMove={handleMouseMove}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
          onDoubleClick={handleDoubleClick}
        />
        <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500 flex justify-between">
          <span>Hover to preview &middot; Click to select &middot; Double-click paper to view details &middot; Scroll to zoom &middot; Drag to move</span>
          <span>Color: <span className="text-blue-600">Paper</span> <span className="text-emerald-600">Material</span> <span className="text-purple-600">Method</span> <span className="text-amber-600">Concept</span> <span className="text-rose-600">Institution</span></span>
        </div>
      </div>

      {/* Selected Node Info */}
      {selectedNodeData && (
        <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100">
          <h3 className="text-base font-semibold text-gray-800 mb-2">
            <span className="inline-block w-3 h-3 rounded-full mr-2" style={{ backgroundColor: NODE_COLORS[selectedNodeData.type] }}></span>
            {selectedNodeData.label}
          </h3>
          <div className="text-sm text-gray-500 mb-2">ID: {selectedNodeData.id} &middot; Type: {selectedNodeData.type}</div>
          {selectedNodeData.type === 'Paper' && (
            <div className="text-sm text-gray-700">
              <div><strong>Category:</strong> {(selectedNodeData as PaperNode).category?.replace(/_/g, ' ')}</div>
              <div><strong>Year:</strong> {(selectedNodeData as PaperNode).year}</div>
              <div><strong>Journal:</strong> {(selectedNodeData as PaperNode).journal}</div>
              {(selectedNodeData as PaperNode).key_findings && (
                <div className="mt-2"><strong>Key Findings:</strong> {(selectedNodeData as PaperNode).key_findings.slice(0, 300)}...</div>
              )}
              <button
                className="mt-3 text-blue-600 hover:text-blue-800 text-sm font-medium"
                onClick={() => onPaperClick(selectedNodeData.id)}
              >
                View full paper details &rarr;
              </button>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="bg-white rounded-xl shadow-sm p-5 border border-gray-100 mt-4">
        <h3 className="text-base font-semibold text-gray-800 mb-3">Legend</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Object.entries(NODE_COLORS).map(([type, color]) => (
            <div key={type} className="flex items-center gap-2">
              <span className="inline-block w-4 h-4 rounded-full" style={{ backgroundColor: color }}></span>
              <span className="text-sm text-gray-700">{type}</span>
            </div>
          ))}
        </div>
        <div className="mt-3 text-xs text-gray-500">
          <strong>Edge types:</strong> studies (paper→material), uses (paper→method), addresses (paper→concept), from (paper→institution), related_* (paper↔paper)
        </div>
      </div>
    </div>
  )
}
