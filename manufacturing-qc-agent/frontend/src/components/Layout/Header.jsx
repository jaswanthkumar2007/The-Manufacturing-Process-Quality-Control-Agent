import React from 'react';
import { useLocation } from 'react-router-dom';

const PAGE_TITLES = {
  '/dashboard': { title: 'Dashboard',       sub: 'Real-time QC overview' },
  '/monitor':   { title: 'Live Monitor',    sub: 'MQTT sensor streams' },
  '/analysis':  { title: 'QC Analysis',     sub: 'Anomaly detection & quality prediction' },
  '/agents':    { title: 'Agent Console',   sub: 'IBM Granite · LangGraph multi-agent' },
  '/knowledge': { title: 'Knowledge Base',  sub: 'RAG · ISO 9001 · SPC · FMEA' },
  '/reports':   { title: 'Reports',         sub: 'AI-generated shift reports' },
};

export default function Header({ alerts = [] }) {
  const { pathname } = useLocation();
  const page = PAGE_TITLES[pathname] || { title: 'QC Agent', sub: '' };
  const criticalAlerts = alerts.filter(a => a.severity === 'critical').length;
  const highAlerts     = alerts.filter(a => a.severity === 'high').length;

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-blue-900/30"
            style={{ background: 'rgba(13,13,36,0.95)', backdropFilter: 'blur(8px)' }}>
      <div>
        <h1 className="text-lg font-semibold text-white">{page.title}</h1>
        <p className="text-xs text-slate-500">{page.sub}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Alert badges */}
        {criticalAlerts > 0 && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-900/40 border border-red-500/40 text-red-300 animate-pulse">
            🚨 {criticalAlerts} Critical
          </div>
        )}
        {highAlerts > 0 && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-orange-900/40 border border-orange-500/40 text-orange-300">
            ⚠ {highAlerts} High
          </div>
        )}

        {/* Platform badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs border border-blue-500/30"
             style={{ background: 'rgba(59,130,246,0.08)' }}>
          <span className="text-blue-400 font-medium">IBM watsonx.ai</span>
          <span className="text-slate-600">·</span>
          <span className="text-cyan-400 font-medium">Granite 13B</span>
        </div>

        {/* Clock */}
        <LiveClock />
      </div>
    </header>
  );
}

function LiveClock() {
  const [time, setTime] = React.useState(new Date());
  React.useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="text-xs font-mono text-slate-400 tabular-nums">
      {time.toLocaleTimeString()} UTC
    </div>
  );
}
