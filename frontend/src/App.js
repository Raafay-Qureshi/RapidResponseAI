import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';
import MapView from './components/Map/MapView';

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <h1>🚨 RapidResponse AI</h1>
        <p className="subtitle">Emergency Response Intelligence System</p>
        <div className="disclaimer">
          ⚠️ SIMULATION MODE - For Demonstration Only
        </div>
      </header>
<<<<<<< HEAD
      <Dashboard />
=======
      <main style={{ height: 'calc(100vh - 120px)', width: '100%' }}>
        <MapView />
      </main>
>>>>>>> 63c03dced260d27a12c55fa251c3640e72c3099c
    </div>
  );
}

export default App;
