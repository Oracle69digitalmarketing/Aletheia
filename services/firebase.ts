// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyA_F3-1BPpnm4T04L7tRQGn1ElloKKHKIU",
  authDomain: "aletheia-db208.firebaseapp.com",
  projectId: "aletheia-db208",
  storageBucket: "aletheia-db208.firebasestorage.app",
  messagingSenderId: "230765515082",
  appId: "1:230765515082:web:1e78b1cc54b290459131b3",
  measurementId: "G-2Z60TPXEQS"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
