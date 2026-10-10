import React, { useState, useEffect } from 'react';
import { predictQuality, checkAnomaly, getControlChart } from '../api/client';
import ControlChart from '../components/Charts/ControlChart';
import { AnomalyScatterChart, FeatureImportanceChart } from '../components/Charts/AnomalyChart';
import { QualityGauge } from '../components/Charts/QualityGauge';
import StatusBadge from '../components/UI/StatusBadge';
import { PROCESS_LINES, SENSOR_TYPES } from './constants';

export default function QCAnalysis() {
  const [selectedLine,    setSelectedLine]    = useState('CNC_LINE_A');
  const [selectedSensor,  setSelectedSensor]  = useState('temperature');
  const [prediction,      setPrediction]      = useState(null);
  const [anomalyCheck,    setAnomalyCheck]    = useState(null);
  const [controlData,     setControlData]     = useState(null);
  const [loading,         setLoading]         = useState(false);
  const [controlLoading,  setControlLoading]  = useState(false);

  // Auto-refresh every 5 s
  useEffect(() => {
    const run = async () => {
      setLoading(true);
      try {
        const [predRes, anomRes] = await Promise.allSettled([
          predictQuality(selectedLine),
          checkAnomaly(selectedLine),
        ]);
        if (predRes.status  === 'fulfilled') setPrediction(predRes.value.data);
        if (anomRes.status  === 'fulfilled') setAnomalyCheck(anomRes.value.data);
      } finally {
        setLoading(false);
      }
    };
    run();
    const id = setInterval(run, 5000);
    return () => clearInterval(id);
  }, [selectedLine]);

  useEffect(() => {
    const run = async () => {
      setControlLoading(true);
      try {
        const res = await getControlChart(selectedLine, selectedSensor);
        setControlData(res.data.chart);
      } catch { /* ignore */ }
      finally { setControlLoading(false); }
    };
    run();
  }, [selectedLine, selectedSensor]);

  const pred = prediction?.prediction || {};
  const anomAlerts = anomalyCheck?.sensor_alerts || [];
  const importance = prediction?.feature_importance || {};

  return (
    <div className="p-6 space-y-5">
      {/* Controls */}
      <div className="flex flex-wrap gap-3 items-center">
        <div>
          <label className="text-xs text-slate-500 mr-2">Process Line</label>
          <select className="bg-factory-800 border border-blue-900/40 text-white text-sm rounded-lg px-3 py-1.5 outline-none"
            value={selectedLine} onChange={e => setSelectedLine(e.target.value)}>
            {PROCESS_LINES.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-slate-500 mr-2">Sensor (Control Chart)</label>
          <select className="bg-factory-800 border border-blue-900/40 text-white text-sm rounded-lg px-3 py-1.5 outline-none"
            value={selectedSensor} onChange={e => setSelectedSensor(e.target.value)}>
            {SENSOR_TYPES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        {loading && <span className="text-xs text-blue-400 animate-pulse">Refreshing…</span>}
      </div>

      {/* Top row: Gauge + Anomaly summary */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <QualityGauge score={pred.quality_score ?? 0} grade={pred.quality_grade ?? 'unknown'} />

        <div className="lg:col-span-3 glass rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-semibold text-white">Quality Prediction</span>
            <StatusBadge status={pred.quality_grade === 'pass' ? 'pass' : pred.quality_grade === 'fail' ? 'fail' : 'review'} />
          </div>
          <div className="grid grid-cols-3 gap-4">
            {['pass', 'review', 'fail'].map(g => (
              <div key={g} className={`rounded-lg p-3 text-center ${pred.quality_grade === g ? 'ring-1 ring-blue-500' : 'bg-white/3'}`}>
                <div className="text-xs text-slate-500 capitalize mb-1">{g}</div>
                <div className="text-xl font-mono font-bold text-white">
                  {((pred.probabilities?.[g] || 0) * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 text-xs text-slate-500">
            Confidence: <span className="text-blue-300 font-mono">{((pred.confidence || 0) * 100).toFixed(1)}%</span>
            &nbsp;· Model: RandomForest · Sklearn
          </div>
        </div>
      </div>

      {/* Anomaly panel */}
      {anomAlerts.length > 0 && (
        <div className="glass rounded-xl p-4 border border-red-500/30 glow-red">
          <div className="text-sm font-semibold text-red-300 mb-3">⚠ Anomalies Detected ({anomAlerts.length})</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {anomAlerts.map((a, i) => (
              <div key={i} className="bg-red-900/10 border border-red-500/20 rounded-lg p-3">
                <div className="text-sm font-semibold text-white capitalize">{a.sensor}</div>
                <div className="font-mono text-lg text-red-300">{Number(a.value)?.toFixed(3)}</div>
                <div className="text-xs text-slate-500">Score: {a.score?.toFixed(4)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Control Chart */}
      <div>
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
          SPC Control Chart — {selectedSensor} · {selectedLine}
        </div>
        <ControlChart data={controlData || {}} sensorType={selectedSensor} loading={controlLoading} />
      </div>

      {/* Feature importance */}
      {Object.keys(importance).length > 0 && (
        <FeatureImportanceChart data={importance} />
      )}
    </div>
  );
}
