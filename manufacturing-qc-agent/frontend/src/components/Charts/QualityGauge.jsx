/**
 * QualityGauge — RadialBarChart quality score gauge + PieChart quality distribution.
 */
import React from 'react';
import {
  RadialBarChart, RadialBar, PolarAngleAxis,
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

export function QualityGauge({ score = 0, grade = 'unknown' }) {
  const pct = Math.round(score);
  const color = pct >= 80 ? '#10b981' : pct >= 60 ? '#f59e0b' : '#ef4444';

  return (
    <div className="glass rounded-xl p-4 flex flex-col items-center">
      <div className="text-sm font-semibold text-white mb-3">Quality Score</div>
      <div className="relative">
        <ResponsiveContainer width={140} height={140}>
          <RadialBarChart
            cx={70} cy={70}
            innerRadius={50} outerRadius={65}
            startAngle={210} endAngle={-30}
            data={[{ value: pct, fill: color }]}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
            <RadialBar background={{ fill: 'rgba(255,255,255,0.04)' }} dataKey="value" cornerRadius={4} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold font-mono" style={{ color }}>{pct}</span>
          <span className="text-xs text-slate-400">/ 100</span>
        </div>
      </div>
      <div className="mt-2 text-xs font-semibold uppercase tracking-wide" style={{ color }}>
        {grade?.toUpperCase()}
      </div>
    </div>
  );
}

export function QualityDistribution({ data = {} }) {
  const pie = [
    { name: 'Pass',   value: data.pass   || 0, fill: '#10b981' },
    { name: 'Review', value: data.review || 0, fill: '#f59e0b' },
    { name: 'Fail',   value: data.fail   || 0, fill: '#ef4444' },
  ].filter(d => d.value > 0);

  return (
    <div className="glass rounded-xl p-4">
      <div className="mb-3 text-sm font-semibold text-white">Quality Distribution</div>
      {pie.length === 0 ? (
        <div className="h-32 flex items-center justify-center text-sm text-slate-500">No data</div>
      ) : (
        <ResponsiveContainer width="100%" height={140}>
          <PieChart>
            <Pie
              data={pie}
              cx="50%" cy="50%"
              innerRadius={35} outerRadius={55}
              paddingAngle={3}
              dataKey="value"
              isAnimationActive={false}
            >
              {pie.map((d, i) => <Cell key={i} fill={d.fill} />)}
            </Pie>
            <Tooltip contentStyle={{ background: '#12122a', border: '1px solid #1e1e4a', fontSize: 11 }} />
            <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
