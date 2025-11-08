import React, { useState } from 'react';
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
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;