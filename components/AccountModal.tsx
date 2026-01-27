
import React, { useState } from 'react';
import { User } from '../types';
import { 
  auth, 
  googleProvider, 
  githubProvider,
  twitterProvider,
  signInWithPopup 
} from '../services/firebase';

interface AccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnect: (user: User) => void;
}

const AccountModal: React.FC<AccountModalProps> = ({ isOpen, onClose, onConnect }) => {
  const [error, setError] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFirebaseSignIn = async (providerName: 'google' | 'github' | 'twitter') => {
    setIsConnecting(providerName);
    setError(null);
    
    let provider;
    if (providerName === 'google') provider = googleProvider;
    else if (providerName === 'github') provider = githubProvider;
    else provider = twitterProvider;

    try {
      const result = await signInWithPopup(auth, provider);
      const fbUser = result.user;
      
      const mappedUser: User = {
        name: fbUser.displayName || 'Agent',
        email: fbUser.email || '',
        avatar: fbUser.photoURL || `https://api.dicebear.com/7.x/avataaars/svg?seed=${fbUser.uid}`,
        connectedAt: new Date().toISOString()
      };
      
      onConnect(mappedUser);
      onClose();
    } catch (err: any) {
      console.error("Auth Error:", err);
      if (err.code === 'auth/popup-closed-by-user') {
        setError('Sign-in window was closed.');
      } else if (err.code === 'auth/api-key-not-valid') {
        setError('Firebase API Key is missing or invalid. Check services/firebase.ts');
      } else {
        setError('Connection failed. Please ensure GitHub/Google is enabled in Firebase Console.');
      }
    } finally {
      setIsConnecting(null);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 overflow-hidden">
      <div 
        className="absolute inset-0 bg-slate-900/80 backdrop-blur-md transition-opacity duration-500"
        onClick={onClose}
      ></div>
      
      <div className="relative bg-white w-full max-w-md rounded-[2.5rem] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-300">
        <div className="p-10">
          <div className="flex justify-between items-start mb-8">
            <div>
              <h3 className="text-3xl font-black text-slate-900 tracking-tight">Connect</h3>
              <p className="text-slate-500 font-medium mt-1">Access your strategic engine.</p>
            </div>
            <button 
              onClick={onClose}
              className="p-2.5 hover:bg-slate-100 rounded-full transition-colors group"
            >
              <i className="fa-solid fa-xmark text-slate-400 group-hover:text-slate-600"></i>
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-rose-50 border border-rose-100 rounded-2xl flex items-center gap-3 text-rose-600 text-xs font-bold animate-in slide-in-from-top-2">
              <i className="fa-solid fa-circle-exclamation text-lg"></i>
              {error}
            </div>
          )}

          <div className="space-y-4">
            {/* Real Google Authentication */}
            <button 
              onClick={() => handleFirebaseSignIn('google')}
              disabled={!!isConnecting}
              className="w-full flex items-center justify-center gap-3 py-3.5 px-4 border border-slate-200 rounded-2xl hover:bg-slate-50 hover:border-slate-300 transition-all font-bold text-slate-700 disabled:opacity-50 group"
            >
              {isConnecting === 'google' ? (
                <div className="flex items-center gap-2">
                  <i className="fa-solid fa-circle-notch animate-spin text-indigo-500"></i>
                  <span>Opening Google...</span>
                </div>
              ) : (
                <>
                  <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" className="w-5 h-5 group-hover:scale-110 transition-transform" alt="Google" />
                  Continue with Google
                </>
              )}
            </button>

            {/* Real GitHub Authentication */}
            <button 
              onClick={() => handleFirebaseSignIn('github')}
              disabled={!!isConnecting}
              className="w-full flex items-center justify-center gap-3 py-3.5 px-4 bg-slate-900 text-white rounded-2xl hover:bg-black transition-all font-bold disabled:opacity-50 group shadow-lg shadow-slate-200"
            >
              {isConnecting === 'github' ? (
                <div className="flex items-center gap-2">
                  <i className="fa-solid fa-circle-notch animate-spin text-indigo-400"></i>
                  <span>Opening GitHub...</span>
                </div>
              ) : (
                <>
                  <i className="fa-brands fa-github text-lg group-hover:scale-110 transition-transform"></i>
                  Continue with GitHub
                </>
              )}
            </button>

            {/* Real Twitter Authentication */}
            <button
              onClick={() => handleFirebaseSignIn('twitter')}
              disabled={!!isConnecting}
              className="w-full flex items-center justify-center gap-3 py-3.5 px-4 bg-[#1DA1F2] text-white rounded-2xl hover:bg-[#1a8cd8] transition-all font-bold disabled:opacity-50 group shadow-lg shadow-blue-100"
            >
              {isConnecting === 'twitter' ? (
                <div className="flex items-center gap-2">
                  <i className="fa-solid fa-circle-notch animate-spin text-white"></i>
                  <span>Opening Twitter...</span>
                </div>
              ) : (
                <>
                  <i className="fa-brands fa-twitter text-lg group-hover:scale-110 transition-transform"></i>
                  Continue with Twitter
                </>
              )}
            </button>

            <div className="relative py-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-100"></div>
              </div>
              <div className="relative flex justify-center text-[10px] uppercase font-black tracking-[0.2em]">
                <span className="bg-white px-4 text-slate-400">Secure Auth</span>
              </div>
            </div>

            <p className="text-center text-[11px] text-slate-400 px-4">
              GitHub and Google provide secure identity verification. Aletheia never stores your passwords.
            </p>
          </div>
        </div>

        <div className="bg-slate-50 p-8 border-t border-slate-100">
          <p className="text-[11px] text-slate-400 text-center leading-relaxed font-medium">
            Production keys required in <code>services/firebase.ts</code>. See <a href="https://firebase.google.com/docs/auth" target="_blank" className="underline hover:text-indigo-600">Firebase Docs</a>.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AccountModal;
