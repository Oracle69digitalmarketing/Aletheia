
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import { Plan, User } from './types';
import { auth, signOut, onAuthStateChanged } from './services/firebase';

const App: React.FC = () => {
  const [activePlan, setActivePlan] = useState<Plan | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Listen for real Firebase Auth changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        const mappedUser: User = {
          name: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'Agent',
          email: firebaseUser.email || '',
          avatar: firebaseUser.photoURL || `https://api.dicebear.com/7.x/avataaars/svg?seed=${firebaseUser.uid}`,
          connectedAt: new Date().toISOString()
        };
        setUser(mappedUser);
        // We don't show the toast here to avoid popping up on every refresh
      } else {
        setUser(null);
      }
    });

    return () => unsubscribe();
  }, []);

  const handleConnect = (newUser: User) => {
    setUser(newUser);
    showToast(`Authentication Successful: Welcome ${newUser.name}!`, 'success');
  };

  const handleDisconnect = async () => {
    try {
      await signOut(auth);
      setUser(null);
      showToast('Session terminated securely.', 'success');
    } catch (error) {
      showToast('Failed to sign out. Please try again.', 'error');
    }
  };

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header 
        projectUrl={activePlan?.metrics?.projectUrl}
        user={user}
        onConnect={handleConnect}
        onDisconnect={handleDisconnect}
      />
      
      {toast && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[200] animate-in slide-in-from-bottom-4 fade-in duration-300">
          <div className={`px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3 border ${
            toast.type === 'success' ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-rose-600 border-rose-500 text-white'
          }`}>
            <div className="w-6 h-6 rounded-full flex items-center justify-center bg-white/20">
               <i className={`fa-solid ${toast.type === 'success' ? 'fa-check text-[10px]' : 'fa-exclamation text-[10px]'}`}></i>
            </div>
            <span className="font-bold text-sm tracking-wide">{toast.message}</span>
          </div>
        </div>
      )}

      <main className="flex-grow">
        <Dashboard onPlanUpdate={(plan) => setActivePlan(plan)} user={user} />
      </main>

      <footer className="bg-white border-t border-slate-200 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl overflow-hidden shadow-sm border border-slate-100">
              <img src="/logo.jpeg" alt="Aletheia Logo" className="w-full h-full object-cover" />
            </div>
            <span className="text-slate-900 font-black text-xl tracking-tight">Aletheia</span>
          </div>
          <p className="text-slate-500 text-sm mb-8 max-w-lg mx-auto leading-relaxed">
            Real-time agentic co-pilot for high-accountability goal orchestration. 
            Integrated with Firebase Auth and Opik Observability.
          </p>
          <div className="flex justify-center gap-6 mb-10">
            {[
              { icon: 'fa-github', url: 'https://github.com/oracle69digitalmarketing' },
              { icon: 'fa-twitter', url: 'https://x.com/sophiemabel69' },
              { icon: 'fa-discord', url: 'https://support.discord.com/hc/en-us/profiles/17067005644695' },
              { icon: 'fa-linkedin', url: 'https://www.linkedin.com/in/oracle69digitalmarketing' }
            ].map((social, i) => (
              <a 
                key={i} 
                href={social.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-full bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400 hover:text-indigo-600 hover:border-indigo-200 transition-all"
              >
                <i className={`fa-brands ${social.icon} text-lg`}></i>
              </a>
            ))}
          </div>
          <div className="pt-8 border-t border-slate-100 flex flex-col md:flex-row items-center justify-between gap-4">
             <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">
               &copy; 2026 Aletheia Engine &bull; Production Auth
             </p>
             <div className="flex gap-6">
               <a href="https://firebase.google.com/support/privacy" target="_blank" className="text-[10px] font-bold text-slate-400 uppercase tracking-widest hover:text-indigo-600">Privacy</a>
               <a href="#" className="text-[10px] font-bold text-slate-400 uppercase tracking-widest hover:text-indigo-600">Status</a>
             </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
