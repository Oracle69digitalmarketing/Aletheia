
import React, { useState, useRef, useEffect } from 'react';
import AccountModal from './AccountModal';
import { User } from '../types';

interface HeaderProps {
  projectUrl?: string;
  user: User | null;
  onConnect: (user: User) => void;
  onDisconnect: () => void;
}

const Header: React.FC<HeaderProps> = ({ projectUrl, user, onConnect, onDisconnect }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const closeAllMenus = () => {
    setShowDropdown(false);
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            {/* Logo Section */}
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
              <div className="w-10 h-10 rounded-xl overflow-hidden shadow-lg shadow-indigo-100 border border-slate-100">
                <img src="/logo.jpeg" alt="Aletheia Logo" className="w-full h-full object-cover" />
              </div>
              <span className="text-xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">
                Aletheia
              </span>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-6">
              <button 
                onClick={() => { window.scrollTo({ top: 0, behavior: 'smooth' }); closeAllMenus(); }}
                className="text-slate-500 hover:text-indigo-600 transition-colors text-sm font-bold"
              >
                Strategy
              </button>
              <a 
                href="https://github.com/aletheia-engine/aletheia/blob/main/docs/ALETHEIA.md"
                target="_blank" 
                rel="noopener noreferrer"
                className="text-slate-500 hover:text-indigo-600 transition-colors text-sm font-bold flex items-center gap-1.5"
              >
                Docs
              </a>
              <a 
                href={projectUrl || "https://www.comet.com/opik"} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-slate-500 hover:text-indigo-600 transition-colors text-sm font-bold flex items-center gap-1.5"
              >
                Opik Trace
                <i className="fa-solid fa-external-link text-[10px]"></i>
              </a>

              <div className="h-6 w-px bg-slate-200 mx-1"></div>

              {user ? (
                <div className="relative" ref={dropdownRef}>
                  <button 
                    onClick={() => setShowDropdown(!showDropdown)}
                    className={`flex items-center gap-2 p-1.5 pr-3 rounded-full transition-all border ${
                      showDropdown ? 'bg-indigo-50 border-indigo-200 ring-2 ring-indigo-100' : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <img 
                      src={user.avatar} 
                      alt={user.name}
                      className="w-7 h-7 rounded-full border border-white shadow-sm object-cover" 
                    />
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-bold text-slate-700 max-w-[100px] truncate">
                        {user.name}
                      </span>
                      <i className={`fa-solid fa-chevron-down text-[9px] transition-transform duration-200 ${showDropdown ? 'rotate-180 text-indigo-500' : 'text-slate-400'}`}></i>
                    </div>
                  </button>

                  {showDropdown && (
                    <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl border border-slate-200 shadow-2xl py-2 animate-in fade-in slide-in-from-top-2 duration-200 overflow-hidden z-[60]">
                      <div className="px-4 py-3 bg-slate-50/50 border-b border-slate-100 mb-2">
                        <div className="flex items-center gap-3">
                          <img src={user.avatar} className="w-10 h-10 rounded-full border-2 border-white shadow-sm" alt="" />
                          <div className="overflow-hidden">
                            <p className="text-sm font-bold text-slate-900 truncate">{user.name}</p>
                            <p className="text-[10px] font-medium text-slate-500 truncate">{user.email}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="px-2 space-y-0.5">
                        <button className="w-full text-left px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg transition-colors flex items-center gap-3">
                          <i className="fa-solid fa-chart-line w-4 text-slate-400"></i>
                          <span>Personal Dashboard</span>
                        </button>
                        <button className="w-full text-left px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg transition-colors flex items-center gap-3">
                          <i className="fa-solid fa-folder-open w-4 text-slate-400"></i>
                          <span>Commitment History</span>
                        </button>
                        <div className="h-px bg-slate-100 my-1 mx-3"></div>
                        <button className="w-full text-left px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 rounded-lg transition-colors flex items-center gap-3">
                          <i className="fa-solid fa-gear w-4 text-slate-400"></i>
                          <span>System Preferences</span>
                        </button>
                      </div>

                      <div className="border-t border-slate-100 mt-2 pt-2 px-2">
                        <button 
                          onClick={() => { onDisconnect(); closeAllMenus(); }}
                          className="w-full text-left px-3 py-2 text-sm text-rose-600 hover:bg-rose-50 rounded-lg transition-colors flex items-center gap-3 font-semibold"
                        >
                          <i className="fa-solid fa-right-from-bracket w-4 text-rose-400"></i>
                          Disconnect Agent
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <button 
                  onClick={() => setIsModalOpen(true)}
                  className="bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 active:scale-95"
                >
                  Get Started
                </button>
              )}
            </div>

            {/* Mobile Menu Toggle */}
            <div className="md:hidden flex items-center gap-3">
               <button 
                 onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                 className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors border border-slate-200"
               >
                 <i className={`fa-solid ${isMobileMenuOpen ? 'fa-xmark' : 'fa-bars-staggered'} text-xl`}></i>
               </button>
            </div>
          </div>
        </div>

        {/* Mobile Slide-down Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-white border-b border-slate-200 animate-in slide-in-from-top-4 duration-300">
            <div className="px-4 pt-2 pb-6 space-y-4">
              <div className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] px-4 pt-2">Navigation</div>
              <button 
                onClick={() => { window.scrollTo({ top: 0, behavior: 'smooth' }); closeAllMenus(); }}
                className="w-full text-left px-4 py-3 text-slate-700 font-bold hover:bg-slate-50 rounded-xl flex items-center gap-3"
              >
                <i className="fa-solid fa-house text-indigo-400 w-5"></i>
                Dashboard
              </button>
              <a 
                href="https://github.com/aletheia-engine/aletheia/blob/main/docs/ALETHEIA.md"
                target="_blank" 
                rel="noopener noreferrer"
                className="w-full text-left px-4 py-3 text-slate-700 font-bold hover:bg-slate-50 rounded-xl flex items-center gap-3"
              >
                <i className="fa-solid fa-book text-indigo-400 w-5"></i>
                Documentation
              </a>
              <a 
                href={projectUrl || "https://www.comet.com/opik"} 
                target="_blank" 
                rel="noopener noreferrer"
                onClick={closeAllMenus}
                className="w-full text-left px-4 py-3 text-slate-700 font-bold hover:bg-slate-50 rounded-xl flex items-center gap-3"
              >
                <i className="fa-solid fa-terminal text-indigo-400 w-5"></i>
                Opik Control Plane
              </a>
              
              <div className="pt-4 border-t border-slate-100">
                {user ? (
                  <div className="space-y-2">
                    <div className="px-4 py-3 flex items-center gap-3 mb-2 bg-slate-50 rounded-2xl">
                       <img src={user.avatar} className="w-10 h-10 rounded-full border border-white shadow-sm" alt="" />
                       <div>
                         <p className="font-bold text-slate-900 text-sm leading-none mb-1">{user.name}</p>
                         <p className="text-[10px] text-slate-500 font-medium">{user.email}</p>
                       </div>
                    </div>
                    <button 
                      onClick={() => { onDisconnect(); closeAllMenus(); }}
                      className="w-full text-left px-4 py-3 text-rose-600 font-bold hover:bg-rose-50 rounded-xl flex items-center gap-3"
                    >
                      <i className="fa-solid fa-right-from-bracket w-5"></i>
                      Sign Out
                    </button>
                  </div>
                ) : (
                  <button 
                    onClick={() => { setIsModalOpen(true); setIsMobileMenuOpen(false); }}
                    className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-black text-center shadow-lg shadow-indigo-100"
                  >
                    Connect Account
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>

      <AccountModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConnect={onConnect}
      />
    </>
  );
};

export default Header;
