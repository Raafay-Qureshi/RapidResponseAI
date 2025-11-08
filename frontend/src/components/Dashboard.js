import React, { useState } from 'react';
<<<<<<< Updated upstream
import PlanViewer from './EmergencyPlan/PlanViewer';
import './Dashboard.css';

function Dashboard() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  // Mock function to simulate triggering a disaster
  const handleTriggerDisaster = () => {
    setLoading(true);
    setPlan(null);

    // Simulate API call with delay
    setTimeout(() => {
      const mockPlan = {
        disaster_id: 'wildfire-20200715-001',
        disaster_type: 'WILDFIRE',
        generated_at: new Date().toISOString(),
        confidence: 0.87,
        executive_summary: 'Mock plan data for testing',
      };
      setPlan(mockPlan);
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="dashboard">
      {/* Top Controls */}
      <div className="control-bar">
        <div className="disaster-trigger">
          <h3>🎮 Simulate Disaster</h3>
          <button 
            onClick={handleTriggerDisaster} 
            disabled={loading}
            className="trigger-button"
          >
            {loading ? '⏳ Processing...' : '🚨 Trigger Wildfire Event'}
          </button>
        </div>
        <div className="status-indicator">
          <span className="status-dot connected"></span>
          <span>System Ready</span>
        </div>
      </div>

      {/* Main Content - Split View */}
      <div className="main-content">
        {/* Left: Map Placeholder */}
        <div className="map-panel">
          <div className="map-placeholder">
            <h2>🗺️ Map View</h2>
            <p>Map component will be added in future tasks</p>
            <div className="placeholder-box">
              <span>Interactive map with danger zones and evacuation routes</span>
            </div>
          </div>
        </div>

        {/* Right: Emergency Plan */}
        <div className="plan-panel">
          {plan || loading ? (
            <PlanViewer plan={plan} loading={loading} />
          ) : (
            <div className="empty-state">
              <h2>No Active Emergency</h2>
              <p>Trigger a disaster simulation to see RapidResponse AI in action</p>
              <div className="empty-icon">🚨</div>
=======
import MapView from './Map/MapView';
import './Dashboard.css';

function Dashboard() {
  const [disaster, setDisaster] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  return (
    <div className="dashboard">
      {/* Top Control Bar */}
      <div className="control-bar">
        <div className="control-section">
          <h3 className="control-title">Emergency Operations Center</h3>
          <span className="location-badge">Brampton, ON</span>
        </div>

        <div className="control-section">
          <div className="status-indicator">
            <span className="status-dot ready"></span>
            <span className="status-text">System Ready</span>
          </div>
        </div>
      </div>

      {/* Progress Bar (shown during processing) */}
      {loading && (
        <div className="progress-bar-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="progress-text">
            Analyzing satellite data and generating response plan...
          </p>
        </div>
      )}

      {/* Main Content - Split View */}
      <div className="main-content">
        {/* Left Panel: Map */}
        <div className="map-panel">
          <MapView disaster={disaster} plan={plan} />
        </div>

        {/* Right Panel: Emergency Plan */}
        <div className="plan-panel">
          {plan ? (
            <div className="plan-content">
              {/* PlanViewer will go here in next epic */}
              <h2>📋 Emergency Response Plan</h2>
              <p>Plan viewer component coming in Epic 7...</p>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">🚨</div>
              <h2>No Active Emergency</h2>
              <p>
                System monitoring satellite feeds.
                Trigger simulation to see RapidResponse AI in action.
              </p>
              <div className="empty-state-stats">
                <div className="stat-item">
                  <span className="stat-value">0</span>
                  <span className="stat-label">Active Incidents</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">24/7</span>
                  <span className="stat-label">Monitoring</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{'<60s'}</span>
                  <span className="stat-label">Response Time</span>
                </div>
              </div>
>>>>>>> Stashed changes
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;