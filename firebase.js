// Import the functions you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyAuLVFjh5JyhJNYXaHS0RT-Ewah0iONBKE",
    authDomain: "seatalgo-14ad1.firebaseapp.com",
    projectId: "seatalgo-14ad1",
    storageBucket: "seatalgo-14ad1.firebasestorage.app",
    messagingSenderId: "709506219442",
    appId: "1:709506219442:web:38eaed9525da19e03d78ab"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth };
