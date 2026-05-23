import React, { useState, useMemo } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import PaperTable from './components/PaperTable'
import PaperDetail from './components/PaperDetail'
import KnowledgeGraph from './components/KnowledgeGraph'
import SearchPanel from './components/SearchPanel'
import graphData from './data/graph.json'
import type { Page, PaperNode, GraphData } from './types'

const data = graphData as GraphData

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [selectedPaperId, setSelectedPaperId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const papers = useMemo(() => data.nodes.filter(n => n.type === 'Paper') as PaperNode[], [])

  const handlePaperClick = (paperId: string) => {
    setSelectedPaperId(paperId)
    setCurrentPage('paper-detail')
  }

  const selectedPaper = useMemo(() => {
    if (!selectedPaperId) return null
    return papers.find(p => p.id === selectedPaperId) || null
  }, [selectedPaperId, papers])

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard data={data} papers={papers} onNavigate={setCurrentPage} />
      case 'papers':
        return <PaperTable papers={papers} onPaperClick={handlePaperClick} />
      case 'paper-detail':
        return selectedPaper ? (
          <PaperDetail paper={selectedPaper} data={data} onBack={() => setCurrentPage('papers')} />
        ) : <PaperTable papers={papers} onPaperClick={handlePaperClick} />
      case 'knowledge-graph':
        return <KnowledgeGraph data={data} onPaperClick={handlePaperClick} />
      case 'search':
        return <SearchPanel papers={papers} data={data} query={searchQuery} onPaperClick={handlePaperClick} />
      default:
        return <Dashboard data={data} papers={papers} onNavigate={setCurrentPage} />
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Academic Literature Research Dashboard</h1>
                <p className="text-sm text-gray-500 mt-1">
                  {data.metadata.total_papers} papers &middot; {data.metadata.total_edges} relationships &middot; Knowledge graph from deep reading
                </p>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  placeholder="Search papers, topics, methods..."
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm w-72 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value)
                    if (e.target.value) setCurrentPage('search')
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && searchQuery) setCurrentPage('search')
                  }}
                />
              </div>
            </div>
          </div>
          {renderPage()}
        </div>
      </div>
    </div>
  )
}

export default App
