import React from 'react';
import MapView from './Map/MapView';
import PlanViewer from './EmergencyPlan/PlanViewer';
import DisasterTrigger from './Controls/DisasterTrigger';
import useDisaster from '../hooks/useDisaster';
import useWebSocket from '../hooks/useWebSocket';
import './Dashboard.css';

function Dashboard() {
  const { 
    disaster, 
    plan, 
    loading, 
    progress,
    error,
    statusMessage,
    triggerDisaster,
    clearDisaster,
  } = useDisaster();
  
  const { connected } = useWebSocket();

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

      {/* Progress Bar (shown during processing) */}
      {loading && (
        <div className="progress-bar-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="progress-text">{statusMessage}</p>
        </div>
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

      {/* Main Content - Split View */}
      <div className="main-content">
        {/* Left Panel: Map */}
        <div className="map-panel">
          <MapView disaster={disaster} plan={plan} />
        </div>

        {/* Right Panel: Emergency Plan */}
        <div className="plan-panel">
          <PlanViewer plan={plan} loading={loading} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;