
import React, { useState } from 'react';
import { Plan, TaskStatus, Task } from '../types';

interface PlanDisplayProps {
  plan: Plan;
}

const PlanDisplay: React.FC<PlanDisplayProps> = ({ plan }) => {
  const [tasks, setTasks] = useState<Task[]>(plan.tasks);

  const updateTaskStatus = (id: string, newStatus: TaskStatus) => {
    setTasks(prev => prev.map(t => 
      t.id === id ? { ...t, status: newStatus } : t
    ));
  };

  const completed = tasks.filter(t => t.status === TaskStatus.COMPLETED).length;
  const progress = tasks.length > 0 ? Math.round((completed / tasks.length) * 100) : 0;

  const statusConfig = {
    [TaskStatus.TODO]: {
      color: 'bg-slate-100 border-slate-300 text-slate-500',
      icon: 'fa-regular fa-circle',
      label: 'To Do',
      bgLight: 'hover:bg-slate-50'
    },
    [TaskStatus.IN_PROGRESS]: {
      color: 'bg-indigo-100 border-indigo-400 text-indigo-600',
      icon: 'fa-solid fa-circle-notch fa-spin',
      label: 'In Progress',
      bgLight: 'bg-indigo-50/30'
    },
    [TaskStatus.COMPLETED]: {
      color: 'bg-emerald-100 border-emerald-500 text-emerald-600',
      icon: 'fa-solid fa-check-double',
      label: 'Completed',
      bgLight: 'bg-emerald-50/20'
    },
    [TaskStatus.BLOCKED]: {
      color: 'bg-rose-100 border-rose-400 text-rose-600',
      icon: 'fa-solid fa-ban',
      label: 'Blocked',
      bgLight: 'bg-rose-50/30'
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <div className="lg:col-span-8 space-y-6">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-5 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
            <h3 className="font-bold text-slate-800 flex items-center gap-2">
              <i className="fa-solid fa-route text-indigo-600"></i>
              Execution Strategy
            </h3>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              {tasks.length} Action Items
            </span>
          </div>
          
          <div className="divide-y divide-slate-100">
            {tasks.map(task => {
              const config = statusConfig[task.status];
              return (
                <div 
                  key={task.id}
                  className={`p-5 flex flex-col sm:flex-row gap-4 transition-all ${config.bgLight}`}
                >
                  <div className="flex gap-4 flex-1">
                    <div className={`w-10 h-10 rounded-xl border flex-shrink-0 flex items-center justify-center transition-all shadow-sm ${config.color}`}>
                      <i className={config.icon}></i>
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-1 gap-2">
                        <h4 className={`font-bold transition-all text-sm sm:text-base ${
                          task.status === TaskStatus.COMPLETED ? 'text-slate-400 line-through' : 'text-slate-800'
                        }`}>
                          {task.title}
                        </h4>
                        <span className="text-[10px] font-bold bg-white border border-slate-200 text-slate-500 px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
                          {task.duration}
                        </span>
                      </div>
                      <p className={`text-xs sm:text-sm ${task.status === TaskStatus.COMPLETED ? 'text-slate-400' : 'text-slate-500'}`}>
                        {task.description}
                      </p>
                    </div>
                  </div>

                  <div className="flex sm:flex-col justify-end gap-1 shrink-0 mt-4 sm:mt-0">
                    <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200 gap-1" role="group" aria-label="Task Status Selector">
                      {Object.values(TaskStatus).map((status) => (
                        <button
                          key={status}
                          onClick={() => updateTaskStatus(task.id, status as TaskStatus)}
                          aria-label={`Mark as ${statusConfig[status as TaskStatus].label}`}
                          aria-pressed={task.status === status}
                          className={`w-8 h-8 rounded flex items-center justify-center transition-all ${
                            task.status === status 
                              ? `${statusConfig[status as TaskStatus].color} shadow-sm border` 
                              : 'text-slate-400 hover:text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          <i className={statusConfig[status as TaskStatus].icon.replace('fa-spin', '')}></i>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-indigo-900 rounded-2xl p-6 text-white relative overflow-hidden shadow-lg border border-indigo-700">
          <div className="relative z-10 flex gap-4 items-start">
            <div className="w-10 h-10 bg-indigo-500/20 rounded-xl flex items-center justify-center text-indigo-300 border border-indigo-400/20">
              <i className="fa-solid fa-shield-halved"></i>
            </div>
            <div>
              <p className="text-xs font-bold text-indigo-300 uppercase tracking-widest mb-1">Monitor Agent Intervention</p>
              <p className="text-sm text-indigo-50 leading-relaxed italic">
                "{plan.frictionIntervention}"
              </p>
            </div>
          </div>
          <div className="absolute -right-4 -bottom-4 opacity-10 text-9xl">
            <i className="fa-solid fa-robot"></i>
          </div>
        </div>
      </div>

      <div className="lg:col-span-4 space-y-6">
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <h4 className="font-bold text-slate-800">Plan Health</h4>
            <span className="text-2xl font-black text-indigo-600">{progress}%</span>
          </div>
          <div className="space-y-4">
             <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
               <div 
                 className="h-full bg-indigo-600 transition-all duration-1000" 
                 style={{ width: `${progress}%` }}
               ></div>
             </div>
             <div className="grid grid-cols-2 gap-4">
               <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                 <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">Score</div>
                 <div className="text-lg font-bold text-slate-800">4.9/5</div>
               </div>
               <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                 <div className="text-[10px] text-slate-500 font-bold uppercase mb-1">Tasks</div>
                 <div className="text-lg font-bold text-slate-800">{tasks.length}</div>
               </div>
             </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h4 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
            <i className="fa-solid fa-brain text-violet-500"></i>
            Agentic Logic Chain
          </h4>
          <div className="space-y-6">
            {plan.agentReasoning.map((r, i) => (
              <div key={i} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs border ${
                    r.agent === 'Planner' ? 'bg-blue-50 text-blue-600 border-blue-100' :
                    r.agent === 'Orchestrator' ? 'bg-amber-50 text-amber-600 border-amber-100' :
                    'bg-emerald-50 text-emerald-600 border-emerald-100'
                  }`}>
                    {(r.agent || 'A')[0]}
                  </div>
                  {i !== plan.agentReasoning.length - 1 && <div className="w-px h-full bg-slate-100 my-2"></div>}
                </div>
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">{r.agent}</div>
                  <p className="text-xs text-slate-600 leading-relaxed font-medium">
                    {r.thought}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanDisplay;
