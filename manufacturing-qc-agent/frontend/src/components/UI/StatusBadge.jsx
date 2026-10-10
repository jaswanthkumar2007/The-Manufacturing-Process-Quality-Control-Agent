import React from 'react';

const SEVERITY = {
  normal:   { cls: 'bg-emerald-900/40 border-emerald-500/40 text-emerald-300', dot: 'normal' },
  warning:  { cls: 'bg-yellow-900/40 border-yellow-500/40 text-yellow-300',    dot: 'warning' },
  critical: { cls: 'bg-red-900/40 border-red-500/40 text-red-300',             dot: 'critical' },
  high:     { cls: 'bg-orange-900/40 border-orange-500/40 text-orange-300',    dot: 'warning' },
  medium:   { cls: 'bg-yellow-900/30 border-yellow-600/30 text-yellow-400',    dot: 'warning' },
  low:      { cls: 'bg-slate-800/60 border-slate-600/40 text-slate-400',       dot: '' },
  pass:     { cls: 'bg-emerald-900/40 border-emerald-500/40 text-emerald-300', dot: 'normal' },
  fail:     { cls: 'bg-red-900/40 border-red-500/40 text-red-300',             dot: 'critical' },
  review:   { cls: 'bg-yellow-900/40 border-yellow-500/40 text-yellow-300',    dot: 'warning' },
};

export default function StatusBadge({ status = 'normal', label, small = false }) {
  const s   = SEVERITY[status?.toLowerCase()] || SEVERITY.normal;
  const lbl = label || status;
  return (
    <span className={`inline-flex items-center gap-1.5 border rounded-full font-semibold uppercase tracking-wide ${s.cls} ${small ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-xs'}`}>
      {s.dot && <span className={`status-dot ${s.dot}`} style={{ width: 6, height: 6 }} />}
      {lbl}
    </span>
  );
}
