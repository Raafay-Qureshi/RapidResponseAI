import React, { useState, useEffect } from 'react';
import { useWebSocketContext } from '../services/websocket';
import MapView from './Map/MapView';
import DisasterTrigger from './Controls/DisasterTrigger';
import PlanViewer from './EmergencyPlan/PlanViewer';
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
            // Mock comprehensive plan data for Epic 7 testing
            setPlan({
              disaster_id: disaster.disaster_id,
              disaster_type: 'WILDFIRE',
              generated_at: new Date().toISOString(),
              confidence: 0.92,
              executive_summary: "Critical WUI wildfire detected at HWY 407/410 interchange. 40-acre active fire spreading at 2.5 km/h towards residential areas. Immediate evacuation of 2,500+ residents required. High wind conditions creating extreme fire behavior.",
              timeline_predictions: {
                current_spread_rate_kmh: 2.5,
                critical_arrival_times: [
                  {
                    location: 'HWY 407 Eastbound Lanes',
                    hours_until_arrival: 2.5,
                    confidence: 'high'
                  },
                  {
                    location: 'Residential Zone - Sector 3',
                    hours_until_arrival: 4.0,
                    confidence: 'high'
                  },
                  {
                    location: 'Peel Memorial Hospital Access',
                    hours_until_arrival: 6.5,
                    confidence: 'medium'
                  }
                ],
                factors: {
                  wind_speed_kmh: 35,
                  wind_direction_deg: 270,
                  temperature_c: 32,
                  humidity_percent: 18
                }
              },
              resource_deployment: {
                required_resources: {
                  personnel: 120,
                  ambulances: 15,
                  evacuation_buses: 8
                },
                resource_gaps: [
                  {
                    resource: 'Fire Trucks',
                    description: 'Need 6 additional pumpers for perimeter control'
                  },
                  {
                    resource: 'Ambulances',
                    description: 'Medical capacity stretched, request 5 more units'
                  }
                ]
              },
              communication_templates: {
                en: "🚨 WILDFIRE ALERT: Evacuate immediately from HWY 407/410 area. Fire spreading rapidly. Follow emergency routes. Stay tuned for updates.",
                pa: "🚨 ਅੱਗ ਦੀ ਚੇਤਾਵਨੀ: HWY 407/410 ਖੇਤਰ ਤੋਂ ਤੁਰੰਤ ਖਾਲੀ ਕਰੋ। ਅੱਗ ਤੇਜ਼ੀ ਨਾਲ ਫੈਲ ਰਹੀ ਹੈ। ਐਮਰਜੈਂਸੀ ਰੂਟਾਂ ਦਾ ਪਾਲਣ ਕਰੋ।",
                hi: "🚨 अग्नि चेतावनी: HWY 407/410 क्षेत्र से तुरंत खाली करें। आग तेजी से फैल रही है। आपातकालीन मार्गों का पालन करें।"
              },
              population_impact: {
                total_affected: 2500,
                vulnerable_population: {
                  elderly: 450,
                  children: 680,
                  disabled: 125
                },
                languages: {
                  English: 1250,
                  Punjabi: 625,
                  Hindi: 250,
                  Urdu: 200,
                  Other: 175
                },
                critical_facilities: [
                  {
                    name: 'Spring Dale Elementary School',
                    type: 'elementary_school',
                    location: { lat: 43.7285, lon: -79.8156 },
                    population: 450
                  },
                  {
                    name: 'Brampton Senior Care Center',
                    type: 'senior_center',
                    location: { lat: 43.7312, lon: -79.8201 },
                    population: 85
                  },
                  {
                    name: 'Little Angels Daycare',
                    type: 'daycare',
                    location: { lat: 43.7298, lon: -79.8178 },
                    population: 45
                  }
                ],
                affected_neighborhoods: [
                  'Heart Lake East',
                  'Sandalwood Heights',
                  'Fletcher\'s Creek South'
                ]
              },
              affected_areas: {
                affected_area_km2: 4.2
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
          <PlanViewer plan={plan} loading={loading} />
          
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
      </div>

      {/* WebSocket Test Component - Temporary for testing */}
      <WebSocketTest />
    </div>
  );
}

export default Dashboard;