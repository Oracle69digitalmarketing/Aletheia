
import { initializeApp } from "firebase/app";
import { 
  getAuth, 
  GoogleAuthProvider, 
  GithubAuthProvider, 
  signInWithPopup, 
  signOut,
  onAuthStateChanged
} from "firebase/auth";

/**
 * FIREBASE CONFIGURATION:
 * Get these from Firebase Console > Project Settings > General > Your Apps
 */

const firebaseConfig = {
  apiKey: "AIzaSyA_F3-1BPpnm4T04L7tRQGn1ElloKKHKIU",
  authDomain: "aletheia-db208.firebaseapp.com",
  projectId: "aletheia-db208",
  storageBucket: "aletheia-db208.firebasestorage.app",
  messagingSenderId: "230765515082",
  appId: "1:230765515082:web:1e78b1cc54b290459131b3",
  measurementId: "G-2Z60TPXEQS"
};

// Check if keys are still placeholders. 
// Firebase throws a hard error if initialized with "YOUR_API_KEY", causing a blank screen.
const isRealConfig = firebaseConfig.apiKey !== "YOUR_API_KEY" && firebaseConfig.apiKey !== "";

const app = initializeApp(isRealConfig ? firebaseConfig : {
  apiKey: "mock-api-key-to-prevent-crash",
  authDomain: "mock-auth-domain",
  projectId: "mock-project-id"
});

export const auth = getAuth(app);

export const googleProvider = new GoogleAuthProvider();
export const githubProvider = new GithubAuthProvider();

export { signInWithPopup, signOut, onAuthStateChanged };
