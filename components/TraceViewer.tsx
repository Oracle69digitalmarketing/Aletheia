
import React from 'react';
import { Plan } from '../types';

interface TraceViewerProps {
  plan: Plan;
}

const TraceViewer: React.FC<TraceViewerProps> = ({ plan }) => {
  const isDefaultConfig = plan.traceUrl.includes('/default/');

  return (
    <div className="bg-[#0d1117] rounded-xl border border-slate-800 overflow-hidden shadow-2xl font-mono text-xs">
      <div className="bg-[#161b22] px-4 py-3 border-b border-slate-800 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <div className="flex gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/80"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80"></div>
          </div>
          <span className="text-slate-400 border-l border-slate-700 pl-4 flex items-center gap-2">
            Opik Real-Time Tracing
            <span className="inline-block w-1 h-1 bg-emerald-500 rounded-full animate-ping"></span>
          </span>
        </div>
        <div className="flex items-center gap-3">
          {isDefaultConfig && (
            <div className="hidden sm:flex items-center gap-2 text-amber-500 bg-amber-500/10 px-2 py-1 rounded border border-amber-500/20 text-[9px] font-bold">
              <i className="fa-solid fa-triangle-exclamation"></i>
              CHECK .ENV CONFIG
            </div>
          )}
          <a 
            href={plan.traceUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-indigo-400 hover:text-indigo-300 transition-colors bg-indigo-500/10 px-3 py-1 rounded border border-indigo-500/20 flex items-center gap-2"
          >
            <i className="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
            VIEW IN COMET
          </a>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 border-b border-slate-800">
        {[
          { label: 'Latency', value: `${plan.metrics.latency}ms`, color: 'text-sky-400' },
          { label: 'Trace ID', value: plan.traceId.substring(0, 8) + '...', color: 'text-slate-400' },
          { label: 'Environment', value: isDefaultConfig ? 'Default' : 'Production', color: 'text-indigo-400' },
          { label: 'Opik Link', value: 'Active', color: 'text-emerald-400' }
        ].map((m, i) => (
          <div key={i} className="p-4 border-r border-slate-800 last:border-r-0">
            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">{m.label}</div>
            <div className={`text-sm font-bold ${m.color}`}>{m.value}</div>
          </div>
        ))}
      </div>

      <div className="p-6 space-y-3 max-h-[400px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700 bg-black/20">
        {isDefaultConfig && (
          <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded text-amber-200 leading-relaxed">
            <span className="font-bold">[SYSTEM WARNING]:</span> Trace URL is using 'default' workspace. Ensure COMET_WORKSPACE and COMET_API_KEY are set in your backend .env file to view traces on Comet.com.
          </div>
        )}

        {plan.logs.map(log => (
          <div key={log.id} className="flex gap-4">
            <span className="text-slate-600 shrink-0">{log.timestamp}</span>
            <span className={`font-bold shrink-0 ${
              log.level === 'INFO' ? 'text-emerald-400' : 
              log.level === 'TRACE' ? 'text-indigo-400' : 
              'text-sky-400'
            }`}>[{log.source}]</span>
            <span className="text-slate-300">{log.message}</span>
          </div>
        ))}
        
        {plan.agentReasoning.map((r, idx) => (
          <div key={idx} className="space-y-1">
             <div className="flex gap-4">
              <span className="text-slate-600 shrink-0">{r.timestamp}</span>
              <span className="text-sky-400 font-bold shrink-0">[{r.agent.toUpperCase()}]</span>
              <span className="text-slate-300 italic">"Span generated successfully"</span>
            </div>
            <div className="pl-16 text-slate-500 text-[11px] leading-relaxed border-l border-slate-800 ml-4 py-1">
              {r.thought}
            </div>
          </div>
        ))}

        <div className="pt-4 mt-4 border-t border-slate-800/50">
          <div className="flex gap-4">
            <span className="text-indigo-400 font-bold shrink-0">[OPIK]</span>
            <span className="text-slate-400">Successfully indexed trace to metadata store.</span>
          </div>
        </div>
      </div>

      <div className="bg-[#161b22] px-6 py-4 border-t border-slate-800">
        <div className="flex justify-between items-center mb-4">
           <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Model Performance</span>
           <span className="text-[10px] text-indigo-400 font-mono">judge: gemini-3-flash-preview</span>
        </div>
        <div className="grid grid-cols-3 gap-8">
          {[
            { label: 'Actionability', value: plan.metrics.actionability, color: 'bg-indigo-500' },
            { label: 'Relevance', value: plan.metrics.relevance, color: 'bg-emerald-500' },
            { label: 'Helpfulness', value: plan.metrics.helpfulness, color: 'bg-violet-500' }
          ].map((m, i) => (
            <div key={i}>
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-[10px] text-slate-400 font-medium">{m.label}</span>
                <span className="text-slate-200 font-bold">{m.value}/5</span>
              </div>
              <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${m.color} transition-all duration-1000`} 
                  style={{ width: `${(m.value / 5) * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TraceViewer;
