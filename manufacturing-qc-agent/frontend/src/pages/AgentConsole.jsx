import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import { chatWithAgent, getAgentStatus } from '../api/client';
import StatusBadge from '../components/UI/StatusBadge';
import { PROCESS_LINES } from './constants';

const SESSION_ID = uuidv4();

const QUICK_PROMPTS = [
  'What is the current quality status of all process lines?',
  'Explain SPC Rule 1 violation and recommended action',
  'Analyse anomalies on CNC_LINE_A and recommend corrective actions',
  'What are the top causes of temperature anomalies in CNC machining?',
  'Generate a quality shift summary report',
  'Explain FMEA methodology for this process',
];

const AGENTS = [
  { name: 'QC Agent',      type: 'orchestrator', color: '#3b82f6', icon: '🎯', desc: 'Intent routing & coordination' },
  { name: 'Anomaly Agent', type: 'ml+llm',       color: '#ef4444', icon: '🔍', desc: 'ML detection + Granite analysis' },
  { name: 'RAG Agent',     type: 'rag+llm',      color: '#8b5cf6', icon: '📚', desc: 'ChromaDB + Granite knowledge' },
  { name: 'Report Agent',  type: 'llm',          color: '#10b981', icon: '📋', desc: 'Synthesis & report generation' },
];

export default function AgentConsole() {
  const [messages,    setMessages]    = useState([
    { role: 'assistant', content: '👋 Hello! I\'m the Manufacturing QC Agent powered by **IBM Granite 13B** on **IBM watsonx.ai**.\n\nI can:\n- 🔍 Detect and analyse sensor anomalies\n- 📊 Predict quality outcomes using ML\n- 📚 Answer questions using ISO 9001, SPC & FMEA knowledge (RAG)\n- 📋 Generate shift reports\n\nAsk me anything about your manufacturing quality!', ts: new Date() }
  ]);
  const [input,       setInput]       = useState('');
  const [loading,     setLoading]     = useState(false);
  const [processLine, setProcessLine] = useState('CNC_LINE_A');
  const [agentStatus, setAgentStatus] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    getAgentStatus().then(r => setAgentStatus(r.data)).catch(() => {});
  }, []);

  const sendMessage = async (text = input) => {
    if (!text.trim() || loading) return;
    const userMsg = { role: 'user', content: text, ts: new Date() };
    setMessages(p => [...p, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await chatWithAgent({ session_id: SESSION_ID, message: text, process_line: processLine });
      const data = res.data;

      const assistantMsg = {
        role:          'assistant',
        content:       data.response,
        ts:            new Date(),
        route:         data.agent_route,
        anomaly:       data.anomaly_result,
        sources:       data.rag_sources,
        qualityResult: data.quality_result,
      };
      setMessages(p => [...p, assistantMsg]);
    } catch (err) {
      setMessages(p => [...p, {
        role: 'assistant',
        content: `⚠️ Error connecting to agent: ${err.message}. Make sure the FastAPI backend is running on port 8000.`,
        ts: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Left: Chat */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Controls */}
        <div className="px-4 py-2.5 border-b border-blue-900/20 flex items-center gap-3 flex-wrap"
             style={{ background: 'rgba(13,13,36,0.6)' }}>
          <label className="text-xs text-slate-500">Process Line</label>
          <select className="text-sm bg-transparent border border-blue-900/30 text-white rounded-lg px-3 py-1 outline-none"
            value={processLine} onChange={e => setProcessLine(e.target.value)}>
            {PROCESS_LINES.map(l => <option key={l} value={l}>{l}</option>)}
          </select>
          <span className="ml-auto text-xs text-slate-600 font-mono">session: {SESSION_ID.slice(0, 8)}</span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 animate-slide ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm ${
                msg.role === 'user' ? 'bg-blue-600' : 'bg-gradient-to-br from-blue-600 to-cyan-500'
              }`}>
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'user' ? 'chat-user rounded-tr-sm' : 'chat-ai rounded-tl-sm'
              }`}>
                <div className="markdown-body">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>

                {/* Metadata badges */}
                {msg.route && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    <span className="sensor-badge bg-blue-900/40 border border-blue-500/30 text-blue-300">
                      route: {msg.route}
                    </span>
                    {msg.anomaly?.is_anomaly && (
                      <span className="sensor-badge bg-red-900/40 border border-red-500/30 text-red-300">anomaly detected</span>
                    )}
                    {msg.sources?.map((s, j) => (
                      <span key={j} className="sensor-badge bg-purple-900/30 border border-purple-500/20 text-purple-300" title={s.id}>
                        📚 {s.title?.slice(0, 20)}…
                      </span>
                    ))}
                  </div>
                )}
                <div className="mt-1 text-xs text-slate-600">{msg.ts.toLocaleTimeString()}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center text-sm">🤖</div>
              <div className="chat-ai rounded-2xl rounded-tl-sm px-4 py-3 text-sm flex items-center gap-2">
                <span className="inline-flex gap-1">
                  {[0,1,2].map(i => (
                    <span key={i} className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce"
                          style={{ animationDelay: `${i * 0.15}s` }} />
                  ))}
                </span>
                <span className="text-slate-500 text-xs">IBM Granite analysing…</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Quick prompts */}
        <div className="px-4 py-2 border-t border-blue-900/20 flex gap-2 overflow-x-auto">
          {QUICK_PROMPTS.map((qp, i) => (
            <button key={i} onClick={() => sendMessage(qp)}
              className="flex-shrink-0 text-xs px-3 py-1.5 rounded-lg glass text-slate-400 hover:text-white hover:bg-white/5 transition-colors">
              {qp.length > 40 ? qp.slice(0, 40) + '…' : qp}
            </button>
          ))}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-blue-900/20">
          <div className="flex gap-2">
            <textarea
              className="flex-1 bg-white/5 border border-blue-900/30 text-white text-sm rounded-xl px-4 py-2.5 resize-none outline-none focus:border-blue-500/50 placeholder-slate-600"
              rows={2}
              placeholder="Ask the QC Agent about anomalies, quality predictions, ISO standards…"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              className="px-5 rounded-xl text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
              Send
            </button>
          </div>
          <div className="mt-1.5 text-xs text-slate-600 flex gap-3">
            <span>Enter to send · Shift+Enter for newline</span>
            <span className="ml-auto">IBM Granite 13B · watsonx.ai · LangGraph</span>
          </div>
        </div>
      </div>

      {/* Right: Agent status panel */}
      <div className="w-64 flex-shrink-0 border-l border-blue-900/20 p-4 space-y-4 overflow-y-auto"
           style={{ background: 'rgba(13,13,36,0.6)' }}>
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Agent Graph</div>
        {AGENTS.map(agent => (
          <div key={agent.name} className="glass rounded-xl p-3">
            <div className="flex items-center gap-2 mb-1.5">
              <span style={{ fontSize: 18 }}>{agent.icon}</span>
              <div>
                <div className="text-xs font-semibold text-white">{agent.name}</div>
                <div className="text-xs text-slate-500">{agent.type}</div>
              </div>
              <span className="ml-auto status-dot normal" />
            </div>
            <div className="text-xs text-slate-600">{agent.desc}</div>
          </div>
        ))}

        {agentStatus?.granite && (
          <div className="glass rounded-xl p-3">
            <div className="text-xs font-semibold text-slate-400 mb-2">IBM Granite</div>
            <div className="text-xs space-y-1">
              <div className="text-slate-500">Model: <span className="text-blue-300">{agentStatus.granite.model?.split('/')[1]}</span></div>
              <div className="text-slate-500">Platform: <span className="text-cyan-300">watsonx.ai</span></div>
              <div className="text-slate-500">Mode: <span className={agentStatus.granite.mock_mode ? 'text-yellow-400' : 'text-emerald-400'}>
                {agentStatus.granite.mock_mode ? 'Mock' : 'Live'}
              </span></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
