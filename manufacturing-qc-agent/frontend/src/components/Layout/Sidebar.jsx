import React from 'react';
import { NavLink } from 'react-router-dom';

const NAV = [
  { to: '/dashboard',    icon: '⬡', label: 'Dashboard'      },
  { to: '/monitor',      icon: '📡', label: 'Live Monitor'   },
  { to: '/analysis',     icon: '🔬', label: 'QC Analysis'   },
  { to: '/agents',       icon: '🤖', label: 'Agent Console' },
  { to: '/knowledge',    icon: '📚', label: 'Knowledge Base' },
  { to: '/reports',      icon: '📋', label: 'Reports'       },
];

export default function Sidebar({ wsConnected }) {
  return (
    <aside className="fixed left-0 top-0 h-full w-64 flex flex-col z-50 border-r border-blue-900/30"
           style={{ background: '#0d0d24' }}>
      {/* Logo */}
      <div className="px-5 py-5 border-b border-blue-900/30">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center text-lg"
               style={{ background: 'linear-gradient(135deg, #3b82f6, #06b6d4)' }}>
            ⚙
          </div>
          <div>
            <div className="text-white font-bold text-sm leading-tight">MFG QC Agent</div>
            <div className="text-blue-400 text-xs">IBM Granite · watsonx.ai</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-2 py-1 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
          Navigation
        </div>
        {NAV.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              }`
            }
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-blue-900/30 space-y-2">
        <div className="flex items-center gap-2 text-xs">
          <span className={`status-dot ${wsConnected ? 'normal' : 'critical'}`} />
          <span className={wsConnected ? 'text-emerald-400' : 'text-red-400'}>
            {wsConnected ? 'Live stream active' : 'Connecting...'}
          </span>
        </div>
        <div className="text-xs text-slate-600 leading-tight">
          Platform: IBM Cloud<br />
          LLM: IBM Granite 13B<br />
          v1.0.0
        </div>
      </div>
    </aside>
  );
}
