import React from 'react';
import Dashboard from './components/Dashboard';
import { WebSocketProvider } from './services/websocket';
import './App.css';

function App() {
  return (
    <WebSocketProvider>
      <div className="App">
        <header className="app-header">
          <h1>🚨 RapidResponse AI</h1>
          <p className="subtitle">Emergency Response Intelligence System</p>
          <div className="disclaimer">
            ⚠️ SIMULATION MODE - For Demonstration Only
          </div>
        </header>
        <Dashboard />
      </div>
    </WebSocketProvider>
  );
}

export default App;
