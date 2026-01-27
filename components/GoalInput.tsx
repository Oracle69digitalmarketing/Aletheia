
import React, { useState } from 'react';

interface GoalInputProps {
  onPlanGenerated: (goal: string) => void;
  isLoading: boolean;
}

const GoalInput: React.FC<GoalInputProps> = ({ onPlanGenerated, isLoading }) => {
  const [goal, setGoal] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (goal.trim() && !isLoading) {
      onPlanGenerated(goal);
    }
  };

  const suggestions = [
    "Learn Spanish in 3 months",
    "Run a marathon this summer",
    "Master React and Tailwind",
    "Read 24 books this year"
  ];

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">What is your commitment?</h2>
        <p className="text-slate-500 mb-8">Tell Aletheia your New Year's resolution. Our agents will decompose it into a proactive strategy.</p>
        
        <form onSubmit={handleSubmit} className="relative mb-6">
          <input
            type="text"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            disabled={isLoading}
            placeholder="e.g. Learn to code and get a job in 2024"
            className="w-full pl-6 pr-28 sm:pr-36 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-base sm:text-lg"
          />
          <button
            type="submit"
            disabled={isLoading || !goal.trim()}
            className="absolute right-1.5 top-1.5 bottom-1.5 bg-indigo-600 text-white px-4 sm:px-6 rounded-lg font-bold hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2 text-sm sm:text-base"
          >
            {isLoading ? (
              <>
                <i className="fa-solid fa-spinner animate-spin"></i>
                Planning...
              </>
            ) : (
              <>
                Generate
                <i className="fa-solid fa-wand-magic-sparkles"></i>
              </>
            )}
          </button>
        </form>

        <div className="flex flex-wrap gap-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider w-full mb-1">Try these:</span>
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => setGoal(s)}
              className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-600 px-3 py-1.5 rounded-full transition-colors border border-slate-200"
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GoalInput;
