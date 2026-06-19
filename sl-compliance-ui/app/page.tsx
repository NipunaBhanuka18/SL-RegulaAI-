'use client';

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Telemetry {
  latency: string;
  tokens: number;
  model: string;
  database: string;
  engine: string;
}

interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  timestamp: Date;
  path?: string[];
  citations?: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isEscalated, setIsEscalated] = useState(false);
  const [threadId, setThreadId] = useState('');
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [loadingStep, setLoadingStep] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const steps = [
    "Intercepting & Rewriting Query...",
    "Scanning Neon Vector Database...",
    "Executing Legal Compliance Grader...",
    "Generating Final Response..."
  ];

  useEffect(() => {
    handleResetChat();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
      }, 800);
    }
    return () => clearInterval(interval);
  }, [isLoading, steps.length]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleResetChat = () => {
    const uniqueId = `thread_${Math.random().toString(36).substring(2, 11)}`;
    setThreadId(uniqueId);
    setIsEscalated(false);
    setInput('');
    setTelemetry(null);
    setMessages([
      {
        id: 'welcome',
        sender: 'agent',
        text: 'Welcome to the genary.ai Tax Compliance Dashboard. System is fully operational and backed by Neon Serverless Postgres. How can I assist you today?',
        timestamp: new Date(),
      },
    ]);
  };

  const handleExportChat = () => {
    if (messages.length === 0) return;

    let chatText = `--- genary.ai Tax Compliance Log ---\n`;
    chatText += `Thread ID: ${threadId}\n`;
    chatText += `Date: ${new Date().toLocaleString()}\n\n`;

    messages.forEach(msg => {
      const sender = msg.sender === 'user' ? 'User' : 'genary.ai Compliance Core';
      chatText += `[${sender} - ${msg.timestamp.toLocaleTimeString()}]\n${msg.text}\n`;
      if (msg.citations && msg.citations.length > 0) {
        chatText += `\nSources Cited:\n- ${msg.citations.join('\n- ')}\n`;
      }
      chatText += `\n`;
    });

    const blob = new Blob([chatText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `compliance_log_${threadId}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSendMessage = async (e?: React.FormEvent, presetQuery?: string) => {
    if (e) e.preventDefault();
    const queryToProcess = presetQuery || input;
    if (!queryToProcess.trim() || isLoading || isEscalated) return;

    setInput('');

    const userMessage: Message = {
      id: Math.random().toString(),
      sender: 'user',
      text: queryToProcess,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || 'fallback_dev_key',
        },
        body: JSON.stringify({ query: queryToProcess, thread_id: threadId }),
      });

      if (!response.ok) throw new Error(`Server Error: ${response.status}`);

      const data = await response.json();

      if (data.requires_human) {
        setIsEscalated(true);
      }
      if (data.telemetry) {
        setTelemetry(data.telemetry);
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(),
          sender: 'agent',
          text: data.answer || 'No response text received.',
          timestamp: new Date(),
          path: data.path || [],
          citations: data.citations || [],
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(),
          sender: 'agent',
          text: 'Communication Error: Unable to reach the core compliance server. Please verify Uvicorn is running.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0f1117] text-slate-200 font-sans overflow-hidden">
      {/* ENTERPRISE SIDEBAR */}
      <aside className="w-80 bg-[#151821] border-r border-slate-800 flex flex-col hidden md:flex">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></span>
            genary.ai
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">Enterprise Compliance Agent</p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Real-time Telemetry Dashboard */}
          <div>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 pl-2">Session Telemetry</h3>
            <div className="bg-[#0f1117] rounded-lg p-4 space-y-3 text-[11px] font-mono border border-slate-800 shadow-inner">
              <div className="flex justify-between items-center">
                <span className="text-slate-500 uppercase tracking-widest text-[9px] font-bold">Database</span>
                <span className="text-emerald-400/90 bg-emerald-950/30 px-2 py-0.5 rounded">{telemetry?.database || 'Neon Postgres'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 uppercase tracking-widest text-[9px] font-bold">Engine</span>
                <span className="text-blue-400/90 bg-blue-950/30 px-2 py-0.5 rounded">{telemetry?.engine || 'LangGraph CRAG'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 uppercase tracking-widest text-[9px] font-bold">LLM API</span>
                <span className="text-purple-400/90 bg-purple-950/30 px-2 py-0.5 rounded">{telemetry?.model || 'Groq Llama 3.1'}</span>
              </div>
              <div className="border-t border-slate-800/80 pt-3 mt-3 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 uppercase tracking-widest text-[9px] font-bold">Latency</span>
                  <span className="text-amber-400/90 font-bold text-[11px]">{telemetry?.latency || '0.00s'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500 uppercase tracking-widest text-[9px] font-bold">Tokens Burned</span>
                  <span className="text-rose-400/90 font-bold text-[11px]">{telemetry?.tokens || '0'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Demo Tests */}
          <div>
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 pl-2">Quick Tests</h3>
            <div className="space-y-2">
              <button onClick={() => handleSendMessage(undefined, "What details of the purchaser must be included on a tax invoice?")} disabled={isLoading || isEscalated} className="w-full text-left bg-slate-800/50 hover:bg-slate-800 p-3 rounded-lg text-sm text-slate-300 border border-transparent hover:border-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-slate-900/30 disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:shadow-none">
                1. Standard Retrieval
              </button>
              <button onClick={() => handleSendMessage(undefined, "Wait, is their telephone number mandatory among those details?")} disabled={isLoading || isEscalated} className="w-full text-left bg-slate-800/50 hover:bg-slate-800 p-3 rounded-lg text-sm text-slate-300 border border-transparent hover:border-slate-700 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-slate-900/30 disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:shadow-none">
                2. Pronoun Edge-Case
              </button>
              <button onClick={() => handleSendMessage(undefined, "What are the specific tax rate percentages for importing luxury vehicles in 2026?")} disabled={isLoading || isEscalated} className="w-full text-left bg-slate-800/50 hover:bg-slate-800 p-3 rounded-lg text-sm text-amber-200/70 border border-transparent hover:border-amber-900/50 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-amber-900/20 disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:shadow-none">
                3. Force Escalation
              </button>
            </div>
          </div>
        </div>

        {/* Action Footer */}
        <div className="p-4 border-t border-slate-800 flex flex-col gap-3">
          <button onClick={handleResetChat} className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm py-2.5 rounded-lg transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_4px_15px_rgba(37,99,235,0.3)] flex items-center justify-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
            New Session
          </button>
          <button onClick={handleExportChat} disabled={messages.length <= 1} className="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-sm py-2.5 rounded-lg transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-slate-900/40 flex items-center justify-center gap-2 border border-slate-700 disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:shadow-none">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
            Export Log
          </button>
        </div>
      </aside>

      {/* MAIN CHAT AREA */}
      <main className="flex-1 flex flex-col relative bg-[#0f1117]">
        <header className="md:hidden flex items-center justify-between p-4 border-b border-slate-800/60 bg-[#151821]/80 backdrop-blur-xl sticky top-0 z-20">
          <h1 className="font-bold text-white tracking-tight">genary.ai</h1>
          <button onClick={handleResetChat} className="text-xs font-medium bg-slate-800 border border-slate-700 text-white px-3 py-1.5 rounded-md">New Chat</button>
        </header>

        <section className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth">
          <div className="max-w-3xl mx-auto space-y-6 pb-32">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex animate-message-reveal opacity-0 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.sender === 'agent' && (
                  <div className="w-8 h-8 rounded-full bg-emerald-900/50 border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.2)] flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                    <span className="text-emerald-400 text-[10px] font-bold tracking-wider">AI</span>
                  </div>
                )}

                <div className={`max-w-[85%] rounded-2xl p-5 shadow-md ${msg.sender === 'user'
                    ? 'bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-br-none shadow-blue-900/30 text-[15px]'
                    : 'bg-[#1e2230] text-slate-200 border border-slate-700/50 rounded-bl-none'
                  }`}
                >
                  {/* Markdown Rendering for AI Responses */}
                  {msg.sender === 'agent' ? (
                    <div className="prose prose-invert max-w-none text-[15px] leading-relaxed prose-p:leading-relaxed prose-pre:bg-[#0f1117] prose-pre:border prose-pre:border-slate-700 prose-ul:my-2 prose-li:my-0.5">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                  )}

                  {/* Observability Path & Citations (Only on AI messages) */}
                  {msg.sender === 'agent' && (msg.path?.length ? msg.path.length > 0 : false || msg.citations?.length ? msg.citations.length > 0 : false) && (
                    <div className="mt-5 pt-4 border-t border-slate-700/50 space-y-3">
                      {msg.path && msg.path.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono text-slate-500">
                          <span className="font-bold text-slate-400 uppercase tracking-wider mr-1">Execution Path:</span>
                          {msg.path.map((step, index) => (
                            <span key={index} className="flex items-center gap-1.5">
                              <span className={`border border-slate-700 px-1.5 py-0.5 rounded backdrop-blur-sm ${index === msg.path!.length - 1 ? 'bg-blue-900/20 shadow-[0_0_10px_rgba(59,130,246,0.2)] text-blue-300' : 'bg-slate-800/50 text-slate-400'}`}>{step}</span>
                              {index < msg.path!.length - 1 && <span className="text-slate-600">→</span>}
                            </span>
                          ))}
                        </div>
                      )}

                      {msg.citations && msg.citations.length > 0 && (
                        <div className="flex flex-col gap-1.5 text-[10px] font-mono">
                          <span className="font-bold text-slate-400 uppercase tracking-wider">Sources Cited:</span>
                          <ul className="flex flex-col gap-1.5">
                            {msg.citations.map((cite, index) => (
                              <li key={index} className="flex items-center gap-2 text-emerald-400/80 bg-emerald-950/10 hover:bg-emerald-950/30 transition-colors border border-emerald-900/40 px-2.5 py-1.5 rounded-lg w-fit shadow-sm cursor-default">
                                <svg className="w-3 h-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                {cite}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="w-8 h-8 rounded-full bg-emerald-900/50 border border-emerald-500/30 flex items-center justify-center mr-3 mt-1 flex-shrink-0 animate-pulse">
                  <span className="text-emerald-400 text-[10px] font-bold tracking-wider">AI</span>
                </div>
                <div className="bg-[#1e2230] border border-slate-700/50 rounded-2xl rounded-bl-none p-4 max-w-[85%] shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                    </div>
                    <span className="text-sm font-mono text-slate-400 animate-pulse">{steps[loadingStep]}</span>
                  </div>
                </div>
              </div>
            )}

            {isEscalated && (
              <div className="bg-amber-950/30 border border-amber-500/50 rounded-xl p-5 text-center shadow-inner mt-8">
                <div className="flex justify-center mb-2">
                  <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                </div>
                <p className="text-sm text-amber-400 font-medium">Thread Locked: Escalated to Human Accountant</p>
                <p className="text-xs text-amber-500/70 mt-1">Out-of-scope compliance parameters detected. Please start a new session.</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </section>

        <footer className="p-4 md:p-8 bg-gradient-to-t from-[#0f1117] via-[#0f1117]/80 to-transparent absolute bottom-0 left-0 right-0 z-20 pointer-events-none">
          <div className="max-w-3xl mx-auto relative mt-4 pointer-events-auto">
            <form onSubmit={(e) => handleSendMessage(e)} className="flex relative items-end shadow-[0_0_30px_rgba(0,0,0,0.5)] rounded-2xl bg-[#1e2230]/70 backdrop-blur-xl border border-slate-700/50 p-1.5">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={isLoading || isEscalated}
                placeholder={isEscalated ? "Thread locked due to manual escalation..." : "Message the compliance core... (Press Enter to send)"}
                className="w-full bg-transparent border-none rounded-xl pl-4 pr-16 py-3 text-[15px] text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-0 disabled:opacity-50 transition-all resize-none overflow-hidden min-h-[52px] max-h-[120px]"
                rows={1}
              />
              <button
                type="submit"
                disabled={isLoading || isEscalated || !input.trim()}
                className="absolute right-3 bottom-3 p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg disabled:opacity-30 disabled:hover:bg-blue-600 transition-colors shadow-lg shadow-blue-900/20"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
              </button>
            </form>
            <p className="text-center text-[10px] text-slate-500 mt-3 font-mono">
              Secured via Groq Llama 3.1 & LangGraph CRAG Architecture
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}