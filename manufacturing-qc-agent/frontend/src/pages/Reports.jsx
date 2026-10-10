import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { generateReport, listReports } from '../api/client';
import StatusBadge from '../components/UI/StatusBadge';
import { PROCESS_LINES } from './constants';

export default function Reports() {
  const [reports,     setReports]     = useState([]);
  const [selected,    setSelected]    = useState(null);
  const [generating,  setGenerating]  = useState(false);
  const [processLine, setProcessLine] = useState('CNC_LINE_A');
  const [periodHours, setPeriodHours] = useState(8);

  useEffect(() => {
    listReports().then(r => setReports(r.data.reports || [])).catch(() => {});
  }, []);

  const generate = async () => {
    setGenerating(true);
    try {
      const r = await generateReport({ process_line: processLine, period_hours: periodHours });
      const newReport = r.data;
      setReports(prev => [newReport, ...prev]);
      setSelected(newReport);
    } catch (err) {
      alert(`Error generating report: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="p-6 space-y-5">
      {/* Generate panel */}
      <div className="glass rounded-xl p-5">
        <div className="text-sm font-semibold text-white mb-4">Generate AI Shift Report</div>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="text-xs text-slate-500 block mb-1">Process Line</label>
            <select className="bg-white/5 border border-blue-900/30 text-white text-sm rounded-lg px-3 py-2 outline-none"
              value={processLine} onChange={e => setProcessLine(e.target.value)}>
              {PROCESS_LINES.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-slate-500 block mb-1">Period</label>
            <select className="bg-white/5 border border-blue-900/30 text-white text-sm rounded-lg px-3 py-2 outline-none"
              value={periodHours} onChange={e => setPeriodHours(Number(e.target.value))}>
              {[4, 8, 12, 24].map(h => <option key={h} value={h}>Last {h}h</option>)}
            </select>
          </div>
          <button onClick={generate} disabled={generating}
            className="px-6 py-2 rounded-lg text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 transition-colors flex items-center gap-2">
            {generating ? (
              <><span className="animate-spin">⚙</span> Generating…</>
            ) : '📋 Generate Report'}
          </button>
        </div>
        <div className="mt-2 text-xs text-slate-500">
          Uses IBM Granite 13B to synthesise quality data into an actionable shift report.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Report list */}
        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            {reports.length} Reports
          </div>
          {reports.length === 0 ? (
            <div className="glass rounded-xl p-4 text-sm text-slate-500">
              No reports yet. Generate your first report above.
            </div>
          ) : (
            reports.map((r, i) => (
              <button key={i} onClick={() => setSelected(r)}
                className={`w-full text-left glass rounded-xl p-3 transition-all ${
                  selected === r ? 'border-blue-500/50 bg-blue-600/10' : 'hover:bg-white/5'
                }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono text-blue-300">{r.report_id}</span>
                  <StatusBadge status={r.avg_quality >= 80 ? 'normal' : r.avg_quality >= 60 ? 'warning' : 'critical'} small />
                </div>
                <div className="text-xs text-white font-medium">{r.process_line?.replace(/_/g, ' ')}</div>
                <div className="text-xs text-slate-500 mt-0.5">{new Date(r.timestamp).toLocaleString()}</div>
                {r.total_alerts > 0 && (
                  <div className="text-xs text-orange-400 mt-0.5">⚠ {r.total_alerts} alerts</div>
                )}
              </button>
            ))
          )}
        </div>

        {/* Report content */}
        <div className="lg:col-span-2 glass rounded-xl p-5">
          {selected ? (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-bold text-white">{selected.process_line?.replace(/_/g, ' ')} Shift Report</h2>
                  <div className="text-xs text-slate-500 mt-0.5">
                    ID: {selected.report_id} · Generated: {new Date(selected.generated_at || selected.timestamp).toLocaleString()}
                  </div>
                </div>
                <span className="sensor-badge bg-emerald-900/30 border border-emerald-500/20 text-emerald-300">
                  IBM Granite
                </span>
              </div>
              <div className="text-sm text-slate-200 leading-relaxed markdown-body max-h-[60vh] overflow-y-auto">
                <ReactMarkdown>{selected.summary || selected.content || 'No content'}</ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-sm text-slate-500">
              Select a report or generate a new one
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
