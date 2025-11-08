import React, { useState } from 'react';
import { useWebSocketContext } from '../services/websocket';
import MapView from './Map/MapView';
import WebSocketTest from './Test/WebSocketTest';
import './Dashboard.css';

function Dashboard() {
  const { connected, isReady, socket } = useWebSocketContext();
  // eslint-disable-next-line no-unused-vars
  const [disaster, setDisaster] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [plan, setPlan] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [loading, setLoading] = useState(false);
  // eslint-disable-next-line no-unused-vars
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
          <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}>
            <span className={`status-dot ${connected ? 'ready' : ''}`}></span>
            <span className="status-text">
              {connected ? '🟢 WebSocket Connected' : '🔴 WebSocket Disconnected'}
            </span>
            {socket && connected && (
              <span className="socket-id">ID: {socket.id.substring(0, 8)}...</span>
            )}
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
              {isReady && (
                <div className="websocket-ready-badge">
                  ✓ Real-time updates enabled
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* WebSocket Test Component - Temporary for testing */}
      <WebSocketTest />
    </div>
  );
}

export default Dashboard;