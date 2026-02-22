
import React, { useState } from 'react';
import GoalInput from './GoalInput';
import PlanDisplay from './PlanDisplay';
import TraceViewer from './TraceViewer';
import LogTerminal from './LogTerminal';
import { generateAgenticPlan } from '../services/api';
import { Plan, User } from '../types';

interface DashboardProps {
  onPlanUpdate?: (plan: Plan) => void;
  user: User | null;
}

const Dashboard: React.FC<DashboardProps> = ({ onPlanUpdate, user }) => {
  const [currentPlan, setCurrentPlan] = useState<Plan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastGoal, setLastGoal] = useState('');
  const [view, setView] = useState<'strategy' | 'trace'>('strategy');
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (goal: string) => {
    setIsLoading(true);
    setError(null);
    setLastGoal(goal);
    try {
      const plan = await generateAgenticPlan(goal, user?.email);
      if (plan) {
        setCurrentPlan(plan);
        setView('strategy');
        try {
          if (onPlanUpdate) onPlanUpdate(plan);
        } catch (updateErr) {
          console.error("onPlanUpdate Error:", updateErr);
        }
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Aletheia Engine is currently unreachable.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight mb-4 leading-tight">
          {user ? (
            <>Unveil Your Truth, <span className="text-indigo-600">{user.name.split(' ')[0]}</span></>
          ) : (
            <>Unveil Your <span className="text-indigo-600">Truth</span></>
          )}
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto font-medium leading-relaxed">
          Aletheia transforms resolutions into agent-orchestrated strategies 
          with real Opik observability. Built for high-accountability seekers.
        </p>
      </div>

      <div className="space-y-12">
        <GoalInput onPlanGenerated={handleGenerate} isLoading={isLoading} />

        {error && (
          <div className="max-w-3xl mx-auto animate-in slide-in-from-top-4 duration-300">
            <div className="bg-rose-50 border border-rose-200 rounded-3xl p-6 flex flex-col md:flex-row items-center gap-6 shadow-sm">
              <div className="w-14 h-14 bg-rose-100 rounded-2xl flex items-center justify-center text-rose-600 shrink-0 border border-rose-200">
                <i className="fa-solid fa-triangle-exclamation text-xl"></i>
              </div>
              <div className="flex-grow">
                <h4 className="font-black text-rose-900 mb-1 text-lg">Engine Connection Failed</h4>
                <p className="text-rose-800 font-medium leading-relaxed">
                  {error}. Check if the backend is running and CORS allows {window.location.origin}.
                </p>
              </div>
              <button
                onClick={() => handleGenerate(lastGoal)}
                className="px-6 py-3 bg-rose-600 text-white rounded-2xl font-bold text-sm hover:bg-rose-700 transition-colors shadow-lg shadow-rose-200 shrink-0"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="max-w-3xl mx-auto animate-in fade-in zoom-in-95 duration-300">
            <LogTerminal goal={lastGoal} />
          </div>
        )}

        {currentPlan && !isLoading && (
          <div className="space-y-6">
            <div className="flex items-center justify-center p-1 bg-slate-200/50 border border-slate-200 rounded-2xl w-fit mx-auto shadow-sm">
              <button
                onClick={() => setView('strategy')}
                className={`px-6 py-2.5 rounded-xl font-bold text-sm transition-all ${
                  view === 'strategy' ? 'bg-white text-indigo-600 shadow-md' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Strategy View
              </button>
              <button
                onClick={() => setView('trace')}
                className={`px-6 py-2.5 rounded-xl font-bold text-sm transition-all ${
                  view === 'trace' ? 'bg-white text-indigo-600 shadow-md' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Opik Trace Viewer
              </button>
            </div>

            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              {view === 'strategy' ? (
                <PlanDisplay plan={currentPlan} />
              ) : (
                <div className="max-w-5xl mx-auto">
                   <TraceViewer plan={currentPlan} />
                </div>
              )}
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-3xl p-8 flex items-center gap-6 no-print">
              <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-amber-500 shadow-sm shrink-0 border border-amber-100">
                <i className="fa-solid fa-lightbulb text-2xl"></i>
              </div>
              <div>
                <h5 className="font-black text-amber-900 text-lg">Pro Tip for Consistency</h5>
                <p className="text-amber-800 leading-relaxed font-medium">
                  Don't wait for motivation to strike. The strategy above is designed by agents to be actionable even on your low-energy days.
                  <span className="block mt-1 font-bold">Try to complete at least one task today to build momentum.</span>
                </p>
              </div>
            </div>
          </div>
        )}

        {!currentPlan && !isLoading && (
          <div className="space-y-12">
            <div className="bg-indigo-50 border border-indigo-100 rounded-3xl p-8 flex flex-col md:flex-row items-center gap-8 shadow-sm">
              <div className="flex-1 space-y-4 text-center md:text-left">
                <h2 className="text-2xl font-black text-slate-900">How Aletheia helps you stay on track</h2>
                <ul className="space-y-3">
                  <li className="flex items-center gap-3 text-slate-600 font-medium justify-center md:justify-start">
                    <i className="fa-solid fa-check-circle text-emerald-500"></i>
                    Decompose vague resolutions into hourly tasks.
                  </li>
                  <li className="flex items-center gap-3 text-slate-600 font-medium justify-center md:justify-start">
                    <i className="fa-solid fa-check-circle text-emerald-500"></i>
                    Predict mental friction and provide custom interventions.
                  </li>
                  <li className="flex items-center gap-3 text-slate-600 font-medium justify-center md:justify-start">
                    <i className="fa-solid fa-check-circle text-emerald-500"></i>
                    Observe agentic reasoning in real-time via Opik.
                  </li>
                </ul>
              </div>
              <div className="w-full md:w-64 aspect-video bg-white rounded-2xl border border-indigo-100 shadow-inner flex items-center justify-center text-indigo-400">
                <i className="fa-solid fa-wand-magic-sparkles text-5xl animate-pulse"></i>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-10">
              {[
                { icon: 'fa-microchip', title: 'Agentic Ensemble', desc: 'Planner, Orchestrator, and Monitor agents work together to validate your goal.' },
                { icon: 'fa-eye', title: 'Real Opik Tracing', desc: 'Every reasoning step is pushed to your Opik workspace for production-grade observability.' },
                { icon: 'fa-shield-heart', title: 'Friction Detection', desc: 'Our agents proactively identify obstacles before they derail your commitment.' }
              ].map((feature, i) => (
                <div key={i} className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm hover:shadow-xl hover:border-indigo-100 transition-all group">
                  <div className="w-14 h-14 bg-indigo-50 text-indigo-600 rounded-[1.25rem] flex items-center justify-center text-2xl mb-6 group-hover:bg-indigo-600 group-hover:text-white transition-all">
                    <i className={`fa-solid ${feature.icon}`}></i>
                  </div>
                  <h3 className="text-xl font-black text-slate-800 mb-3 tracking-tight">{feature.title}</h3>
                  <p className="text-slate-600 text-sm leading-relaxed font-medium">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
