import React, { useState, useEffect } from 'react';
import MapView from './Map/MapView';
import PlanViewer from './EmergencyPlan/PlanViewer';
import DisasterTrigger from './Controls/DisasterTrigger';
import ProgressBar from './Shared/ProgressBar';
import useDisaster from '../hooks/useDisaster';
import { useWebSocketContext } from '../services/websocket';
import './Dashboard.css';

function Dashboard() {
  const { connected, isReady } = useWebSocketContext();
  const {
    disaster,
    plan,
    loading,
    progress,
    error,
    statusMessage,
    apiStatus,
    triggerDisaster,
    clearDisaster
  } = useDisaster();

  const [isCachedMode, setIsCachedMode] = useState(false);

  // Check if backend is in cached mode
  useEffect(() => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    fetch(`${apiUrl}/api/config`)
      .then(res => res.json())
      .then(data => setIsCachedMode(data.cached_mode))
      .catch(() => setIsCachedMode(false));
  }, []);

  return (
    <div className="dashboard">
      {/* Top Control Bar */}
      <div className="control-bar">
        <div className="control-section">
          <h3 className="control-title">Emergency Operations Center</h3>
          <span className="location-badge">Brampton, ON</span>
        </div>
        
        <div className="control-section">
          <DisasterTrigger 
            onTrigger={triggerDisaster}
            disabled={loading}
          />
        </div>

        <div className="control-section">
          <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {connected ? 'System Ready' : 'Connecting...'}
            </span>
          </div>
        </div>
      </div>

      {/* Cached Mode Banner */}
      {isCachedMode && (
        <div className="cached-mode-banner">
          <span className="banner-icon">💾</span>
          <span className="banner-text">Demo Mode: Using cached responses for reliability</span>
        </div>
      )}

      {/* Progress Bar (shown during processing) */}
      {loading && (
        <ProgressBar
          progress={progress}
          message={statusMessage}
          estimatedTimeSeconds={60}
          apiStatus={apiStatus || {}}
        />
      )}

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{error}</span>
          <button onClick={clearDisaster} className="error-dismiss">
            Dismiss
          </button>
        </div>
      )}

      {/* Main Content - Wrap Around Layout */}
      <div className="main-content">
        {/* Left Panel: Map */}
        <div className="map-panel">
          <MapView disaster={disaster} plan={plan} />
        </div>

        {/* Right Panel: Plan Summary */}
        <div className="plan-panel">
          <PlanViewer plan={plan} loading={loading} section="summary" />
          
          {!plan && !loading && (
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
              {isReady && (
                <div className="websocket-ready-badge">
                  ✓ Real-time updates enabled
                </div>
              )}
            </div>
          )}
        </div>

        {/* Bottom Panel: Detailed Plan Sections */}
        {plan && !loading && (
          <div className="plan-panel-bottom">
            <PlanViewer plan={plan} loading={loading} section="details" />
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;