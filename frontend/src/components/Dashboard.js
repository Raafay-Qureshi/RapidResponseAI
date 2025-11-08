import React from 'react';
import { useWebSocketContext } from '../services/websocket';
import './Dashboard.css';

function Dashboard() {
  const { connected, isReady, socket } = useWebSocketContext();

  return (
    <div className="dashboard">
      <div className="connection-status">
        <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}>
          <span className="status-dot"></span>
          <span className="status-text">
            {connected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
        </div>
        {socket && connected && (
          <div className="socket-info">
            Socket ID: {socket.id}
          </div>
        )}
      </div>
      
      <div className="dashboard-content">
        <div className="welcome-card">
          <h2>Welcome to RapidResponse AI</h2>
          <p>Emergency Response Intelligence System</p>
          <div className="system-status">
            <div className="status-item">
              <span className="label">WebSocket:</span>
              <span className={`value ${isReady ? 'ready' : 'not-ready'}`}>
                {isReady ? 'Ready' : 'Not Ready'}
              </span>
            </div>
            <div className="status-item">
              <span className="label">Connection:</span>
              <span className={`value ${connected ? 'active' : 'inactive'}`}>
                {connected ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="info-card">
          <h3>🔌 Real-time Features</h3>
          <ul>
            <li>Live pipeline progress updates (60-second processing)</li>
            <li>Real-time plan modifications</li>
            <li>Auto-refresh capabilities (15-minute intervals)</li>
            <li>Instant emergency response notifications</li>
          </ul>
import React, { useState } from 'react';
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
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;