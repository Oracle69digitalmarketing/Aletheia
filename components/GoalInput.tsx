
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
    "Best fertilizer for Cassava in Owo",
    "Buy 50kg of Cocoa beans",
    "Book a mechanic in Akure",
    "Request plastic waste collection"
  ];

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">How can we help you today?</h2>
        <p className="text-slate-500 mb-8">Ask about farming advice, search the market, or book a local service in Ondo.</p>
        
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="relative flex flex-col sm:block">
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              disabled={isLoading}
              placeholder="e.g. I need advice on my cocoa farm in Idanre"
              rows={2}
              className="w-full pl-6 pr-6 sm:pr-40 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all text-base sm:text-lg resize-none min-h-[100px]"
            />
            <button
              type="submit"
              disabled={isLoading || !goal.trim()}
              className="sm:absolute right-2 bottom-2 bg-indigo-600 text-white px-6 py-3 sm:py-2.5 rounded-lg font-bold hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 text-sm sm:text-base mt-3 sm:mt-0 w-full sm:w-auto"
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
          </div>
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
