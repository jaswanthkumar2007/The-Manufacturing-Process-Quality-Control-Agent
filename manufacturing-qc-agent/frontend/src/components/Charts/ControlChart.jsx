/**
 * ControlChart — X-bar + R-chart with UCL/LCL using Recharts.
 */
import React from 'react';
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Legend, Scatter,
} from 'recharts';

export default function ControlChart({ data = {}, sensorType = 'temperature', loading }) {
  if (loading) {
    return (
      <div className="glass rounded-xl p-4 h-64 flex items-center justify-center">
        <div className="text-sm text-slate-500">Loading control chart…</div>
      </div>
    );
  }

  const xbar = data?.xbar || {};
  const rChart = data?.r_chart || {};
  const xbarData = (xbar.data || []).map((v, i) => ({
    i,
    value: v,
    violation: (data?.violations || []).includes(i),
  }));
  const rData = (rChart.data || []).map((v, i) => ({ i, value: v }));

  return (
    <div className="space-y-4">
      {/* X-bar chart */}
      <div className="glass rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-white">X-bar Chart — {sensorType}</span>
          <div className="flex gap-3 text-xs text-slate-400">
            <span>Mean: <span className="text-blue-300 font-mono">{xbar.mean?.toFixed(3)}</span></span>
            <span>UCL: <span className="text-red-300 font-mono">{xbar.ucl?.toFixed(2)}</span></span>
            <span>LCL: <span className="text-yellow-300 font-mono">{xbar.lcl?.toFixed(2)}</span></span>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={160}>
          <ComposedChart data={xbarData} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(59,130,246,0.07)" />
            <XAxis dataKey="i" tick={{ fontSize: 9, fill: '#475569' }} />
            <YAxis tick={{ fontSize: 9, fill: '#475569' }} />
            <Tooltip contentStyle={{ background: '#12122a', border: '1px solid #1e1e4a', fontSize: 11 }} />
            {xbar.ucl != null && <ReferenceLine y={xbar.ucl} stroke="#ef4444" strokeDasharray="5 3" label={{ value: 'UCL', position: 'insideTopRight', fontSize: 9, fill: '#ef4444' }} />}
            {xbar.lcl != null && <ReferenceLine y={xbar.lcl} stroke="#f59e0b" strokeDasharray="5 3" label={{ value: 'LCL', position: 'insideBottomRight', fontSize: 9, fill: '#f59e0b' }} />}
            {xbar.mean != null && <ReferenceLine y={xbar.mean} stroke="#22c55e" strokeDasharray="2 6" />}
            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={1.5} dot={(props) => {
              const { cx, cy, payload } = props;
              return payload.violation
                ? <circle key={props.key} cx={cx} cy={cy} r={4} fill="#ef4444" stroke="#ef4444" />
                : <circle key={props.key} cx={cx} cy={cy} r={2} fill="#3b82f6" />;
            }} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
        {(data?.violations?.length > 0) && (
          <div className="mt-1 text-xs text-red-400">
            ⚠ {data.violations.length} Nelson Rule violation{data.violations.length > 1 ? 's' : ''} detected
          </div>
        )}
      </div>

      {/* R chart */}
      <div className="glass rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-white">R-Chart (Range)</span>
          <div className="flex gap-3 text-xs text-slate-400">
            <span>R-bar: <span className="text-cyan-300 font-mono">{rChart.mean?.toFixed(3)}</span></span>
            <span>UCL_R: <span className="text-red-300 font-mono">{rChart.ucl_r?.toFixed(2)}</span></span>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={100}>
          <ComposedChart data={rData} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(59,130,246,0.07)" />
            <XAxis dataKey="i" tick={{ fontSize: 9, fill: '#475569' }} />
            <YAxis tick={{ fontSize: 9, fill: '#475569' }} />
            <Tooltip contentStyle={{ background: '#12122a', border: '1px solid #1e1e4a', fontSize: 11 }} />
            {rChart.ucl_r != null && <ReferenceLine y={rChart.ucl_r} stroke="#ef4444" strokeDasharray="5 3" />}
            {rChart.mean != null  && <ReferenceLine y={rChart.mean}  stroke="#22c55e" strokeDasharray="2 6" />}
            <Bar dataKey="value" fill="#06b6d4" fillOpacity={0.7} radius={[2, 2, 0, 0]} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
