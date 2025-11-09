import React, { useState, useEffect } from 'react';
import { useWebSocketContext } from '../services/websocket';
import MapView from './Map/MapView';
import DisasterTrigger from './Controls/DisasterTrigger';
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

  // Simulate progress when disaster is triggered
  useEffect(() => {
    if (loading && disaster) {
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setLoading(false);
            // Mock plan completion
            setPlan({
              disaster_id: disaster.disaster_id,
              executive_summary: "40-acre wildfire detected at HWY 407/410 interchange. High-risk WUI area with immediate evacuation needed.",
              situation_overview: "Satellite imagery confirms active wildfire spreading at 2.5 km/h towards residential areas. Wind conditions are favorable for rapid spread. Population impact assessment shows 2,500 residents in immediate danger zone.",
              communication_templates: {
                en: "🚨 WILDFIRE ALERT: Evacuate immediately from HWY 407/410 area. Fire spreading rapidly. Follow emergency routes. Stay tuned for updates.",
                pa: "🚨 ਅग्नि ਸੰਕਟ ਚੇਤਾਵਨੀ: HWY 407/410 ਖੇਤਰ ਤੋਂ ਤੁਰੰਤ ਖਾਲੀ ਕਰੋ। ਅੱਗ ਤੇਜ਼ੀ ਨਾਲ ਫੈਲ ਰਹੀ ਹੈ। ਐਮਰਜੈਂਸੀ ਰੂਟਾਂ ਦਾ ਪਾਲਣ ਕਰੋ। ਅਪਡੇਟਾਂ ਲਈ ਟਿਊਨਡ ਰਹੋ।",
                hi: "🚨 अग्नि संकट चेतावनी: HWY 407/410 क्षेत्र से तुरंत खाली करें। आग तेजी से फैल रही है। आपातकालीन मार्गों का पालन करें। अपडेट के लिए ट्यून रहें।"
              }
            });
            return 100;
          }
          return prev + 2; // Increment by 2% every 100ms for ~5 second demo
        });
      }, 100);

      return () => clearInterval(interval);
    }
  }, [loading, disaster]);

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
            onTrigger={(disaster) => {
              setDisaster(disaster);
              setLoading(true);
              setProgress(0);
            }}
            disabled={loading}
          />
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
              <h2>📋 Emergency Response Plan</h2>

              <div className="plan-section">
                <h3>🚨 Executive Summary</h3>
                <p>{plan.executive_summary}</p>
              </div>

              <div className="plan-section">
                <h3>📊 Situation Overview</h3>
                <p>{plan.situation_overview}</p>
              </div>

              <div className="plan-section">
                <h3>📢 Public Communications</h3>

                <div className="communication-template">
                  <h4>🇬🇧 English</h4>
                  <div className="template-content">
                    {plan.communication_templates?.en}
                  </div>
                </div>

                <div className="communication-template">
                  <h4>🇮🇳 Punjabi</h4>
                  <div className="template-content">
                    {plan.communication_templates?.pa}
                  </div>
                </div>

                <div className="communication-template">
                  <h4>🇮🇳 Hindi</h4>
                  <div className="template-content">
                    {plan.communication_templates?.hi}
                  </div>
                </div>
              </div>
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