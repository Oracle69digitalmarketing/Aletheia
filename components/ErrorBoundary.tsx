
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 font-sans">
          <div className="max-w-md w-full bg-white rounded-[2rem] shadow-2xl border border-rose-100 p-10 text-center animate-in fade-in zoom-in-95 duration-500">
            <div className="w-20 h-20 bg-rose-50 text-rose-600 rounded-3xl flex items-center justify-center text-3xl mx-auto mb-8 shadow-inner">
              <i className="fa-solid fa-triangle-exclamation"></i>
            </div>
            <h1 className="text-2xl font-black text-slate-900 mb-4 tracking-tight">Something went wrong.</h1>
            <p className="text-slate-600 mb-8 leading-relaxed font-medium">
              Aletheia encountered an unexpected runtime error. We've logged the incident and our agents are looking into it.
            </p>
            <div className="bg-slate-50 rounded-2xl p-4 mb-8 text-left border border-slate-100 overflow-hidden">
               <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Error Details</p>
               <p className="text-xs font-mono text-rose-600 break-words line-clamp-3">
                 {this.state.error?.message || 'Unknown Error'}
               </p>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold transition-all shadow-lg shadow-indigo-200 active:scale-[0.98]"
            >
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
