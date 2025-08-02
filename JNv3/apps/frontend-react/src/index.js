import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import * as serviceWorkerRegistration from './serviceWorkerRegistration';
import reportWebVitals from './reportWebVitals';

// Global error handler to suppress extension errors
window.addEventListener('error', (event) => {
  // Check if error is from browser extension
  if (event.filename && (
    event.filename.includes('chrome-extension://') || 
    event.filename.includes('moz-extension://') ||
    event.error?.stack?.includes('chrome-extension://') ||
    event.error?.stack?.includes('moz-extension://')
  )) {
    console.warn('Browser extension error suppressed:', event.error);
    event.preventDefault();
    return false;
  }
});

// Handle unhandled promise rejections from extensions
window.addEventListener('unhandledrejection', (event) => {
  if (event.reason?.stack && (
    event.reason.stack.includes('chrome-extension://') ||
    event.reason.stack.includes('moz-extension://')
  )) {
    console.warn('Browser extension promise rejection suppressed:', event.reason);
    event.preventDefault();
    return false;
  }
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
serviceWorkerRegistration.unregister();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
