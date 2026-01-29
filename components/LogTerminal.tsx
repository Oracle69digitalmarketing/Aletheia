
import React, { useEffect, useState, useRef } from 'react';
import { LogEntry } from '../types';

interface LogTerminalProps {
  goal: string;
}

const mockLogsTemplates = [
  { level: 'INFO', source: 'SYSTEM', message: 'Initializing Aletheia Agentic Workflow for: "{goal}"' },
  { level: 'TRACE', source: 'OPIK', message: 'Trace context created. Session ID: {session}' },
  { level: 'DEBUG', source: 'PLANNER', message: 'Analyzing goal structure and semantic intent...' },
  { level: 'INFO', source: 'PLANNER', message: 'Decomposing milestones based on gemini-1.5-flash reasoning engine.' },
  { level: 'DEBUG', source: 'MONITOR', message: 'Scanning for psychological friction and habit blockers...' },
  { level: 'INFO', source: 'MONITOR', message: 'Predictive friction analysis complete. Generating intervention.' },
  { level: 'DEBUG', source: 'ORCHESTRATOR', message: 'Calculating optimal task sequences and dependencies.' },
  { level: 'TRACE', source: 'OPIK', message: 'Pushing intermediate reasoning span to Comet dashboard.' },
  { level: 'INFO', source: 'EVALUATOR', message: 'Running Actionability and Relevance judge.' },
  { level: 'DEBUG', source: 'SYSTEM', message: 'Finalizing response structure and formatting tasks...' },
];

const LogTerminal: React.FC<LogTerminalProps> = ({ goal }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [mockLogsCount, setMockLogsCount] = useState(mockLogsTemplates.length);

  useEffect(() => {
    const sessionId = Math.random().toString(36).substr(2, 9);
    const mockLogs = mockLogsTemplates.map(log => ({
      ...log,
      message: log.message.replace('{goal}', goal).replace('{session}', sessionId)
    }));
    setMockLogsCount(mockLogs.length);

    let index = 0;
    const interval = setInterval(() => {
      if (index < mockLogs.length) {
        const currentMock = mockLogs[index];
        if (currentMock) {
          setLogs(prev => [...prev, {
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toLocaleTimeString(),
            level: (currentMock.level || 'INFO') as any,
            source: currentMock.source || 'SYSTEM',
            message: currentMock.message || ''
          }]);
        }
        index++;
      } else {
        clearInterval(interval);
      }
    }, 500);
    return () => clearInterval(interval);
  }, [goal]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-[#0d1117] rounded-xl border border-slate-800 font-mono text-[11px] h-64 overflow-hidden flex flex-col shadow-2xl">
      <div className="bg-[#161b22] px-4 py-2 border-b border-slate-800 flex justify-between items-center">
        <div className="flex gap-1.5">
          <div className="w-2 h-2 rounded-full bg-slate-700"></div>
          <div className="w-2 h-2 rounded-full bg-slate-700"></div>
          <div className="w-2 h-2 rounded-full bg-slate-700"></div>
        </div>
        <div className="text-slate-500 uppercase font-bold tracking-widest text-[9px]">Live Agent Stream</div>
        <div className="flex items-center gap-2">
           <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
           <span className="text-emerald-500/80 text-[9px]">LIVE</span>
        </div>
      </div>
      <div ref={scrollRef} className="p-4 space-y-1.5 overflow-y-auto flex-1 scrollbar-thin scrollbar-thumb-slate-800">
        {logs.map(log => (
          <div key={log.id} className="flex gap-3 leading-relaxed">
            <span className="text-slate-600 shrink-0">{log.timestamp}</span>
            <span className={`font-bold shrink-0 ${
              log.level === 'INFO' ? 'text-emerald-400' : 
              log.level === 'TRACE' ? 'text-indigo-400' : 
              log.level === 'DEBUG' ? 'text-sky-400' : 'text-slate-400'
            }`}>[{log.source}]</span>
            <span className="text-slate-300">{log.message}</span>
          </div>
        ))}
        {logs.length < mockLogsCount && (
          <div className="flex gap-2 items-center text-slate-500 italic">
            <span className="animate-bounce">_</span>
            <span>Waiting for agent response...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default LogTerminal;
