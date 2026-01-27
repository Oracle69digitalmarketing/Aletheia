
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

  const handleGenerate = async (goal: string) => {
    setIsLoading(true);
    setLastGoal(goal);
    try {
      const plan = await generateAgenticPlan(goal);
      if (plan) {
        setCurrentPlan(plan);
        setView('strategy');
        try {
          if (onPlanUpdate) onPlanUpdate(plan);
        } catch (updateErr) {
          console.error("onPlanUpdate Error:", updateErr);
        }
      }
    } catch (err) {
      console.error(err);
      alert("Aletheia Engine is currently unreachable. Please check your connection or try again later.");
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
          </div>
        )}

        {!currentPlan && !isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-10">
            {[
              { icon: 'fa-microchip', title: 'Agentic Ensemble', desc: 'Planner, Orchestrator, and Monitor agents work together to validate your goal.' },
              { icon: 'fa-eye', title: 'Real Opik Tracing', desc: 'Every reasoning step is pushed to your Comet workspace for production-grade observability.' },
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
        )}
      </div>
    </div>
  );
};

export default Dashboard;
