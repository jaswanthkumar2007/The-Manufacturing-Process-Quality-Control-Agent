import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import Header  from './components/Layout/Header';
import Dashboard    from './pages/Dashboard';
import LiveMonitor  from './pages/LiveMonitor';
import QCAnalysis   from './pages/QCAnalysis';
import AgentConsole from './pages/AgentConsole';
import KnowledgeBase from './pages/KnowledgeBase';
import Reports       from './pages/Reports';
import { useWebSocket } from './hooks/useWebSocket';
import { useSensorData } from './hooks/useSensorData';

export default function App() {
  const { connected } = useWebSocket();
  const { alerts }    = useSensorData(5000);

  return (
    <Router>
      <div className="flex h-screen overflow-hidden" style={{ background: '#0a0a1a' }}>
        <Sidebar wsConnected={connected} />

        {/* Main area */}
        <div className="flex-1 flex flex-col ml-64 overflow-hidden">
          <Header alerts={alerts} />
          <main className="flex-1 overflow-y-auto">
            <Routes>
              <Route path="/"           element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard"  element={<Dashboard />} />
              <Route path="/monitor"    element={<LiveMonitor />} />
              <Route path="/analysis"   element={<QCAnalysis />} />
              <Route path="/agents"     element={<AgentConsole />} />
              <Route path="/knowledge"  element={<KnowledgeBase />} />
              <Route path="/reports"    element={<Reports />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}
