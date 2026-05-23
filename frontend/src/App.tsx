import { useState, useEffect } from 'react';
import type { EvidenceRow, KGNode, KGEdge, DashboardStats, ProjectSynthesis, DataQualityReport, Page } from './types';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { EvidenceExplorer } from './pages/EvidenceExplorer';
import { KnowledgeGraph } from './pages/KnowledgeGraph';
import { ProjectViews } from './pages/ProjectViews';
import { CitationBrowser } from './pages/CitationBrowser';
import { MLFeatures } from './pages/MLFeatures';
import { DataQuality } from './pages/DataQuality';
import { AskCorpus } from './pages/AskCorpus';

function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [evidence, setEvidence] = useState<EvidenceRow[]>([]);
  const [nodes, setNodes] = useState<KGNode[]>([]);
  const [edges, setEdges] = useState<KGEdge[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [projects, setProjects] = useState<ProjectSynthesis[]>([]);
  const [quality, setQuality] = useState<DataQualityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch('/data/evidence.json').then(r => r.json()),
      fetch('/data/kg_nodes.json').then(r => r.json()),
      fetch('/data/kg_edges.json').then(r => r.json()),
      fetch('/data/dashboard_stats.json').then(r => r.json()),
      fetch('/data/project_syntheses.json').then(r => r.json()),
      fetch('/data/data_quality_report.json').then(r => r.json()),
    ]).then(([ev, nd, ed, st, pj, dq]) => {
      setEvidence(ev);
      setNodes(nd);
      setEdges(ed);
      setStats(st);
      setProjects(pj);
      setQuality(dq);
      setLoading(false);
    }).catch(err => {
      console.error('Failed to load data:', err);
      setError('Failed to load data. Please refresh the page.');
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="flex items-center justify-center h-screen text-gray-500">Loading literature corpus...</div>;
  if (error) return <div className="flex flex-col items-center justify-center h-screen text-red-500 gap-4"><p>{error}</p><button onClick={() => window.location.reload()} className="px-4 py-2 bg-blue-500 text-white rounded">Retry</button></div>;

  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <Dashboard stats={stats!} evidence={evidence} />;
      case 'ask': return <AskCorpus evidence={evidence} />;
      case 'evidence': return <EvidenceExplorer evidence={evidence} />;
      case 'graph': return <KnowledgeGraph nodes={nodes} edges={edges} />;
      case 'projects': return <ProjectViews projects={projects} />;
      case 'citations': return <CitationBrowser evidence={evidence} />;
      case 'ml-features': return <MLFeatures evidence={evidence} />;
      case 'quality': return <DataQuality evidence={evidence} quality={quality!} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar current={page} onNavigate={setPage} />
      <main className="flex-1 overflow-auto p-6">{renderPage()}</main>
    </div>
  );
}

export default App;
