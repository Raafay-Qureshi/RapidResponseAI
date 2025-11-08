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
        </div>
      </div>
    </div>
  );
}

export default Dashboard;