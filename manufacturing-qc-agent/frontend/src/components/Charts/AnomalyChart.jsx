/**
 * AnomalyChart — scatter plot of anomaly scores over time + feature importance bar.
 */
import React from 'react';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, BarChart, Bar, LabelList,
} from 'recharts';
import { SENSOR_COLORS } from './chartUtils';

export function AnomalyScatterChart({ data = [] }) {
  const chartData = data.map((d, i) => ({
    x:      i,
    y:      d.score ?? 0,
    sensor: d.sensor_type || d.sensor || 'unknown',
    value:  d.value,
    isAnom: d.is_anomaly,
  }));

  return (
    <div className="glass rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-white">Anomaly Score Distribution</span>
        <span className="text-xs text-slate-500">{data.length} readings</span>
      </div>
      <ResponsiveContainer width="100%" height={160}>
        <ScatterChart margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(59,130,246,0.07)" />
          <XAxis dataKey="x" name="Reading #" tick={{ fontSize: 9, fill: '#475569' }} />
          <YAxis dataKey="y" name="Score" domain={[0, 1]} tick={{ fontSize: 9, fill: '#475569' }} />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{ background: '#12122a', border: '1px solid #1e1e4a', fontSize: 11 }}
            formatter={(v, n, props) => [
              `${v.toFixed(4)} — ${props.payload.sensor} = ${props.payload.value?.toFixed(3)}`,
              'Score',
            ]}
          />
          <Scatter data={chartData} isAnimationActive={false}>
            {chartData.map((d, i) => (
              <Cell key={i} fill={d.isAnom ? '#ef4444' : SENSOR_COLORS[d.sensor] || '#3b82f6'} fillOpacity={0.8} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <div className="mt-2 flex gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500 inline-block" /> Anomaly</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500 inline-block" /> Normal</span>
      </div>
    </div>
  );
}

export function FeatureImportanceChart({ data = {} }) {
  const sorted = Object.entries(data)
    .map(([k, v]) => ({ name: k, importance: v }))
    .sort((a, b) => b.importance - a.importance);

  return (
    <div className="glass rounded-xl p-4">
      <div className="mb-3 text-sm font-semibold text-white">Feature Importance</div>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={sorted} layout="vertical" margin={{ top: 2, right: 40, bottom: 2, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(59,130,246,0.07)" horizontal={false} />
          <XAxis type="number" domain={[0, 0.3]} tick={{ fontSize: 9, fill: '#475569' }} />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#94a3b8' }} width={80} />
          <Tooltip contentStyle={{ background: '#12122a', border: '1px solid #1e1e4a', fontSize: 11 }} />
          <Bar dataKey="importance" fill="#3b82f6" radius={[0, 3, 3, 0]} isAnimationActive={false}>
            {sorted.map((d, i) => (
              <Cell key={i} fill={SENSOR_COLORS[d.name] || '#3b82f6'} />
            ))}
            <LabelList dataKey="importance" position="right" formatter={v => v.toFixed(3)} style={{ fontSize: 9, fill: '#94a3b8' }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
