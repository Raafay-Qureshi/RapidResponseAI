import { useWebSocketContext } from '../services/websocket';
import React, { useState, useEffect } from 'react';
import MapView from './Map/MapView';
import WebSocketTest from './Test/WebSocketTest';
import DisasterTrigger from './Controls/DisasterTrigger';
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
                pa: "🚨 ਅग्नi ਸੰਕਟ ਚੇਤਾਵਨੀ: HWY 407/410 ਖੇਤਰ ਤੋਂ ਤੁਰੰਤ ਖਾਲੀ ਕਰੋ। ਅੱਗ ਤੇਜ਼ੀ ਨਾਲ ਫੈਲ ਰਹੀ ਹੈ। ਐਮਰਜੈਂਸੀ ਰੂਟਾਂ ਦਾ ਪਾਲਣ ਕਰੋ। ਅਪਡੇਟਾਂ ਲਈ ਟਿਊਨਡ ਰਹੋ।",
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
          <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}>
            <span className={`status-dot ${connected ? 'ready' : ''}`}></span>
            <span className="status-text">
              {connected ? '🟢 WebSocket Connected' : '🔴 WebSocket Disconnected'}
            </span>
            {socket && connected && (
              <span className="socket-id">ID: {socket.id.substring(0, 8)}...</span>
            )}
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
      {/* WebSocket Test Component - Temporary for testing */}
      <WebSocketTest />
    </div>
  );
}

export default Dashboard;