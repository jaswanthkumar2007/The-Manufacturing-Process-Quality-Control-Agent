import React from 'react';
import { useSensorData } from '../hooks/useSensorData';
import { useWebSocket } from '../hooks/useWebSocket';
import { QualityGauge, QualityDistribution } from '../components/Charts/QualityGauge';
import StatusBadge from '../components/UI/StatusBadge';
import { SENSOR_COLORS, SENSOR_UNITS } from '../components/Charts/chartUtils';
import { PROCESS_LINES } from './constants';

// PROCESS_LINES imported from constants

function KPICard({ label, value, sub, color = '#3b82f6', icon }) {
  return (
    <div className="glass rounded-xl p-5 metric-card" style={{ borderColor: `${color}22` }}>
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">{label}</div>
          <div className="text-3xl font-bold font-mono" style={{ color }}>{value}</div>
          {sub && <div className="text-xs text-slate-500 mt-1">{sub}</div>}
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  );
}

function LineStatusCard({ line, lineStatus = {}, readings = {} }) {
  const isWarning = lineStatus[line];
  const lineReadings = Object.entries(readings)
    .filter(([k]) => k.startsWith(`${line}:`))
    .map(([k, v]) => ({ sensor: k.split(':')[1], ...(typeof v === 'object' ? v : { value: v }) }));

  return (
    <div className={`glass rounded-xl p-4 border ${isWarning ? 'border-red-500/30 glow-red' : 'border-blue-900/20'}`}>
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-sm font-semibold text-white">{line.replace(/_/g, ' ')}</div>
        </div>
        <StatusBadge status={isWarning ? 'warning' : 'normal'} small />
      </div>
      <div className="grid grid-cols-2 gap-1.5">
        {lineReadings.slice(0, 4).map(r => (
          <div key={r.sensor} className="bg-white/3 rounded-lg px-2 py-1.5">
            <div className="text-xs text-slate-500 capitalize">{r.sensor?.replace('_', ' ')}</div>
            <div className="font-mono text-sm font-semibold" style={{ color: SENSOR_COLORS[r.sensor] || '#3b82f6' }}>
              {Number(r.value)?.toFixed(1)} <span className="text-xs text-slate-500">{SENSOR_UNITS[r.sensor] || ''}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { summary, readings, alerts, loading } = useSensorData(3000);
  const { sensorData } = useWebSocket();

  const kpis = summary?.kpis || {};
  const lineStatus = summary?.line_status || {};

  const criticalAlerts = alerts.filter(a => a.severity === 'critical' || a.severity === 'high');

  return (
    <div className="space-y-6 bg-grid min-h-full p-6">
      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Process Lines" value={kpis.total_lines ?? 4}
          sub={`${kpis.lines_normal ?? 0} normal · ${kpis.lines_warning ?? 0} warning`}
          color="#3b82f6" icon="🏭" />
        <KPICard label="Quality Score" value={`${kpis.avg_quality_score ?? 0}%`}
          sub="Average across all lines" color="#10b981" icon="✅" />
        <KPICard label="Defect Rate" value={`${kpis.avg_defect_rate ?? 0}%`}
          sub="Target: < 3.0%" color={kpis.avg_defect_rate > 3 ? '#ef4444' : '#10b981'} icon="🔬" />
        <KPICard label="Active Alerts" value={kpis.active_alerts ?? 0}
          sub={criticalAlerts.length > 0 ? `${criticalAlerts.length} critical` : 'All clear'}
          color={kpis.active_alerts > 0 ? '#ef4444' : '#10b981'} icon="🔔" />
      </div>

      {/* Process Lines Grid */}
      <div>
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
          Production Lines — Live Status
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {PROCESS_LINES.map(line => (
            <LineStatusCard key={line} line={line} lineStatus={lineStatus}
              readings={Object.keys(sensorData).length > 0 ? sensorData : readings} />
          ))}
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Quality gauge */}
        <QualityGauge score={kpis.avg_quality_score ?? 0}
          grade={kpis.avg_quality_score >= 80 ? 'pass' : kpis.avg_quality_score >= 60 ? 'review' : 'fail'} />

        {/* Alerts panel */}
        <div className="lg:col-span-2 glass rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-white">Recent Alerts</span>
            <span className="text-xs text-slate-500">{alerts.length} active</span>
          </div>
          {alerts.length === 0 ? (
            <div className="text-sm text-emerald-400 flex items-center gap-2">
              <span className="status-dot normal" />  All systems normal — no active alerts
            </div>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {alerts.slice(0, 8).map((a, i) => (
                <div key={i} className={`flex items-start gap-3 p-2.5 rounded-lg ${
                  a.severity === 'critical' ? 'bg-red-900/20 border border-red-500/20' :
                  a.severity === 'high'     ? 'bg-orange-900/20 border border-orange-500/20' :
                  'bg-slate-800/40 border border-slate-700/40'}`}>
                  <StatusBadge status={a.severity} small />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-white truncate">{a.title}</div>
                    <div className="text-xs text-slate-500">{a.process_line} · {new Date(a.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* IBM branding footer */}
      <div className="flex items-center gap-3 text-xs text-slate-600 pt-2">
        <span>Powered by</span>
        <span className="text-blue-500 font-semibold">IBM watsonx.ai</span>
        <span>·</span>
        <span className="text-cyan-500">Granite 13B Instruct</span>
        <span>·</span>
        <span className="text-purple-400">LangGraph Multi-Agent</span>
        <span>·</span>
        <span className="text-emerald-400">ChromaDB RAG</span>
        <span>·</span>
        <span className="text-yellow-400">MQTT Real-Time</span>
      </div>
    </div>
  );
}
