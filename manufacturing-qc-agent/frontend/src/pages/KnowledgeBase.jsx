import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { listDocuments, getDocument, askKnowledgeBase } from '../api/client';

export default function KnowledgeBase() {
  const [docs,       setDocs]       = useState([]);
  const [selected,   setSelected]   = useState(null);
  const [docContent, setDocContent] = useState(null);
  const [question,   setQuestion]   = useState('');
  const [answer,     setAnswer]     = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [tab,        setTab]        = useState('docs'); // 'docs' | 'qa'

  useEffect(() => {
    listDocuments().then(r => setDocs(r.data.documents || [])).catch(() => {});
  }, []);

  const openDoc = async (id) => {
    setSelected(id);
    try {
      const r = await getDocument(id);
      setDocContent(r.data);
    } catch { setDocContent(null); }
  };

  const askQuestion = async () => {
    if (!question.trim() || loading) return;
    setLoading(true);
    setAnswer(null);
    try {
      const r = await askKnowledgeBase(question);
      setAnswer(r.data);
    } catch (err) {
      setAnswer({ answer: `Error: ${err.message}`, sources: [] });
    } finally {
      setLoading(false);
    }
  };

  const EXAMPLE_QS = [
    'What are the Nelson rules for SPC control charts?',
    'How do I calculate Cpk process capability?',
    'What corrective action is required for a Rule 1 violation?',
    'Explain FMEA Risk Priority Number calculation',
    'What are the habitability requirements in ISO 9001:2015?',
    'How to detect bearing faults using vibration analysis?',
  ];

  return (
    <div className="p-6 space-y-5">
      {/* Tabs */}
      <div className="flex gap-2">
        {['docs', 'qa'].map(t => (
          <button key={t}
            onClick={() => setTab(t)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t ? 'bg-blue-600 text-white' : 'glass text-slate-400 hover:text-white'
            }`}>
            {t === 'docs' ? '📄 Knowledge Documents' : '❓ RAG Q&A'}
          </button>
        ))}
      </div>

      {tab === 'docs' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Document list */}
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
              {docs.length} Documents in ChromaDB
            </div>
            {docs.map(d => (
              <button key={d.id} onClick={() => openDoc(d.id)}
                className={`w-full text-left glass rounded-xl p-4 transition-all ${
                  selected === d.id ? 'border-blue-500/50 bg-blue-600/10' : 'hover:bg-white/5'
                }`}>
                <div className="text-sm font-semibold text-white mb-1">{d.title}</div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {d.tags?.map(t => (
                    <span key={t} className="px-2 py-0.5 rounded text-xs bg-blue-900/30 text-blue-300 border border-blue-500/20">{t}</span>
                  ))}
                </div>
              </button>
            ))}
          </div>

          {/* Document content */}
          <div className="lg:col-span-2 glass rounded-xl p-5">
            {docContent ? (
              <div>
                <h2 className="text-base font-bold text-white mb-3">{docContent.title}</h2>
                <div className="flex gap-1 flex-wrap mb-4">
                  {docContent.tags?.map(t => (
                    <span key={t} className="px-2 py-0.5 rounded text-xs bg-blue-900/30 text-blue-300 border border-blue-500/20">{t}</span>
                  ))}
                </div>
                <pre className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap font-sans overflow-y-auto max-h-[60vh]">
                  {docContent.content}
                </pre>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-slate-500">
                Select a document to view its contents
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Q&A input */}
          <div className="glass rounded-xl p-5">
            <div className="text-sm font-semibold text-white mb-3">
              Ask the RAG Knowledge Base
              <span className="ml-2 text-xs text-slate-500 font-normal">
                Powered by ChromaDB + IBM Granite (LangChain RAG)
              </span>
            </div>
            <div className="flex gap-2">
              <input
                className="flex-1 bg-white/5 border border-blue-900/30 text-white text-sm rounded-lg px-4 py-2.5 outline-none focus:border-blue-500/50 placeholder-slate-600"
                placeholder="Ask about ISO standards, SPC rules, FMEA, defect analysis…"
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && askQuestion()}
              />
              <button onClick={askQuestion} disabled={!question.trim() || loading}
                className="px-5 py-2.5 rounded-lg text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 transition-colors">
                {loading ? 'Searching…' : 'Ask'}
              </button>
            </div>

            {/* Example questions */}
            <div className="mt-3 flex flex-wrap gap-2">
              {EXAMPLE_QS.map((q, i) => (
                <button key={i} onClick={() => setQuestion(q)}
                  className="text-xs px-3 py-1.5 rounded-lg glass text-slate-400 hover:text-white hover:bg-white/5 transition-colors">
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Answer */}
          {answer && (
            <div className="glass rounded-xl p-5 animate-slide">
              <div className="text-sm font-semibold text-white mb-3">Answer</div>
              <div className="text-sm text-slate-200 leading-relaxed markdown-body">
                <ReactMarkdown>{answer.answer}</ReactMarkdown>
              </div>
              {answer.sources?.length > 0 && (
                <div className="mt-4 pt-3 border-t border-blue-900/20">
                  <div className="text-xs text-slate-500 mb-2">Sources retrieved from ChromaDB:</div>
                  {answer.sources.map((s, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs py-1">
                      <span className="text-purple-300">📄 {s.title}</span>
                      <span className="text-slate-600">relevance: {(s.score * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
