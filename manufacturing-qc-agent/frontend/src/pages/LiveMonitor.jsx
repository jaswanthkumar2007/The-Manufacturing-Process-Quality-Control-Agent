import React, { useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import SensorChart from '../components/Charts/SensorChart';
import StatusBadge from '../components/UI/StatusBadge';
import { SENSOR_COLORS, SENSOR_UNITS, THRESHOLDS_DEFAULT } from '../components/Charts/chartUtils';
import { PROCESS_LINES, SENSOR_TYPES } from './constants';

export default function LiveMonitor() {
  const { connected, sensorData } = useWebSocket();
  const [selectedLine, setSelectedLine] = useState('CNC_LINE_A');

  const lineReadings = Object.entries(sensorData)
    .filter(([k]) => k.startsWith(`${selectedLine}:`))
    .reduce((acc, [k, v]) => { acc[k.split(':')[1]] = v; return acc; }, {});

  return (
    <div className="p-6 space-y-5">
      {/* Connection bar */}
      <div className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm ${
        connected ? 'bg-emerald-900/20 border border-emerald-500/20 text-emerald-300'
                  : 'bg-red-900/20 border border-red-500/20 text-red-300'}`}>
        <span className={`status-dot ${connected ? 'normal' : 'critical'}`} />
        {connected
          ? `MQTT stream active — receiving sensor data via WebSocket`
          : 'Connecting to WebSocket / MQTT stream…'}
        <span className="ml-auto text-xs font-mono text-slate-500">
          {Object.keys(sensorData).length} channels
        </span>
      </div>

      {/* Line selector */}
      <div className="flex gap-2 flex-wrap">
        {PROCESS_LINES.map(line => (
          <button key={line}
            onClick={() => setSelectedLine(line)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
              selectedLine === line
                ? 'bg-blue-600 text-white'
                : 'glass text-slate-400 hover:text-white hover:bg-white/5'
            }`}>
            {line.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      {/* Live values row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        {SENSOR_TYPES.map(sensor => {
          const r = lineReadings[sensor];
          const val = r?.value ?? r;
          const thr = THRESHOLDS_DEFAULT[sensor] || {};
          const anomaly = val != null && (val > thr.ucl || (thr.lcl > 0 && val < thr.lcl));
          return (
            <div key={sensor}
                 className={`glass rounded-xl p-3 text-center ${anomaly ? 'border-red-500/40 glow-red' : ''}`}>
              <div className="text-xs text-slate-500 capitalize mb-1">{sensor.replace('_', ' ')}</div>
              <div className="text-xl font-mono font-bold" style={{ color: anomaly ? '#ef4444' : SENSOR_COLORS[sensor] }}>
                {val != null ? Number(val).toFixed(1) : '—'}
              </div>
              <div className="text-xs text-slate-600">{SENSOR_UNITS[sensor]}</div>
              {anomaly && <div className="text-xs text-red-400 font-bold mt-0.5">ALERT</div>}
            </div>
          );
        })}
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {SENSOR_TYPES.map(sensor => (
          <SensorChart key={`${selectedLine}-${sensor}`}
            sensorType={sensor}
            processLine={selectedLine}
            liveData={sensorData} />
        ))}
      </div>
    </div>
  );
}
