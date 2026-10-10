/**
 * SensorChart — real-time line chart for a single sensor using Recharts.
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ResponsiveContainer, Brush,
} from 'recharts';
import { format } from 'date-fns';
import { THRESHOLDS_DEFAULT } from './chartUtils';

const MAX_POINTS = 60;

const COLORS = {
  temperature: '#f59e0b',
  pressure:    '#3b82f6',
  vibration:   '#ef4444',
  humidity:    '#06b6d4',
  speed:       '#8b5cf6',
  defect_rate: '#ec4899',
  torque:      '#10b981',
  flow_rate:   '#f97316',
};

export default function SensorChart({ sensorType = 'temperature', processLine = 'CNC_LINE_A', liveData }) {
  const [points,   setPoints]   = useState([]);
  const counterRef = useRef(0);

  useEffect(() => {
    if (!liveData) return;
    const key = `${processLine}:${sensorType}`;
    const reading = liveData[key];
    if (!reading) return;

    setPoints(prev => {
      const newPt = {
        t:         counterRef.current++,
        time:      format(new Date(), 'HH:mm:ss'),
        value:     reading.value ?? reading,
        label:     sensorType,
      };
      return [...prev.slice(-(MAX_POINTS - 1)), newPt];
    });
  }, [liveData, sensorType, processLine]);

  const thresholds = THRESHOLDS_DEFAULT[sensorType] || {};
  const color = COLORS[sensorType] || '#3b82f6';
  const latest = points.at(-1)?.value;
  const isAnomaly = latest != null && (latest > thresholds.ucl || latest < (thresholds.lcl ?? 0));

  return (
    <div className={`glass rounded-xl p-4 ${isAnomaly ? 'glow-red border-red-500/40' : ''}`}>
      <div className="flex items-center justify-between mb-3">
        <div>
          <span className="text-sm font-semibold text-white capitalize">{sensorType.replace('_', ' ')}</span>
          <span className="ml-2 text-xs text-slate-500">{processLine}</span>
        </div>
        <div className="flex items-center gap-2">
          {isAnomaly && (
            <span className="text-xs font-bold text-red-400 animate-pulse">⚠ ANOMALY</span>
          )}
          <span className="text-lg font-mono font-bold" style={{ color }}>
            {latest?.toFixed(2) ?? '—'}
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={points} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(59,130,246,0.08)" />
          <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#475569' }} interval="preserveStartEnd" />
          <YAxis tick={{ fontSize: 9, fill: '#475569' }} domain={['auto', 'auto']} />
          <Tooltip
            contentStyle={{ background: '#12122a', border: '1px solid #1e1e4a', borderRadius: 8, fontSize: 11 }}
            labelStyle={{ color: '#94a3b8' }}
            itemStyle={{ color }}
          />
          {thresholds.ucl != null && (
            <ReferenceLine y={thresholds.ucl} stroke="#ef4444" strokeDasharray="4 4" label={{ value: 'UCL', position: 'insideTopRight', fontSize: 9, fill: '#ef4444' }} />
          )}
          {thresholds.lcl != null && thresholds.lcl > 0 && (
            <ReferenceLine y={thresholds.lcl} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: 'LCL', position: 'insideBottomRight', fontSize: 9, fill: '#f59e0b' }} />
          )}
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
