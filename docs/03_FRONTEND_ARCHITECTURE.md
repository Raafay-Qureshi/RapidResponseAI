# RapidResponseAI - Frontend Architecture

## 🎯 Overview

React-based web dashboard that displays real-time emergency response intelligence with interactive maps, live updates, and generated emergency plans.

---

## 🏗️ Component Structure

```
src/
├── App.js                          # Main app component
├── components/
│   ├── Dashboard.js                # Main dashboard layout
│   ├── Map/
│   │   ├── MapView.js             # Mapbox GL map component
│   │   ├── DangerZoneLayer.js     # Fire/flood visualization
│   │   ├── EvacuationRoutes.js    # Route overlays
│   │   └── Markers.js             # Schools, hospitals, etc.
│   ├── EmergencyPlan/
│   │   ├── PlanViewer.js          # Document display
│   │   ├── ExecutiveSummary.js    # Top section
│   │   ├── Timeline.js            # Prediction timeline
│   │   └── ResourceTable.js       # Resource allocation table
│   ├── Controls/
│   │   ├── DisasterTrigger.js     # Simulate disasters
│   │   ├── UpdateTimer.js         # Shows time since update
│   │   └── StatusIndicator.js     # System status
│   └── Shared/
│       ├── LoadingSpinner.js
│       ├── ProgressBar.js
│       └── Alert.js
├── services/
│   ├── api.js                      # Backend API client
│   └── websocket.js                # WebSocket connection
├── hooks/
│   ├── useDisaster.js              # Disaster state management
│   └── useWebSocket.js             # WebSocket hook
├── utils/
│   ├── mapHelpers.js               # Map utility functions
│   └── formatting.js               # Data formatting
└── styles/
    └── theme.js                    # Color scheme, fonts
```

---

## 🎨 Main Components

### App.js

```jsx
import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import { WebSocketProvider } from './services/websocket';
import './App.css';

function App() {
  return (
    <WebSocketProvider url="ws://localhost:5000">
      <div className="App">
        <header className="app-header">
          <h1>🚨 RapidResponse AI</h1>
          <p className="subtitle">Emergency Response Intelligence System</p>
          <div className="disclaimer">
            ⚠️ SIMULATION MODE - For Demonstration Only
          </div>
        </header>
        <Dashboard />
      </div>
    </WebSocketProvider>
  );
}

export default App;
```

### Dashboard.js

```jsx
import React, { useState, useEffect } from 'react';
import MapView from './Map/MapView';
import PlanViewer from './EmergencyPlan/PlanViewer';
import DisasterTrigger from './Controls/DisasterTrigger';
import StatusIndicator from './Controls/StatusIndicator';
import ProgressBar from './Shared/ProgressBar';
import useDisaster from '../hooks/useDisaster';
import useWebSocket from '../hooks/useWebSocket';
import './Dashboard.css';

function Dashboard() {
  const { 
    disaster, 
    plan, 
    loading, 
    progress, 
    triggerDisaster 
  } = useDisaster();
  
  const { connected, lastUpdate } = useWebSocket();

  return (
    <div className="dashboard">
      {/* Top Controls */}
      <div className="control-bar">
        <DisasterTrigger onTrigger={triggerDisaster} disabled={loading} />
        <StatusIndicator connected={connected} lastUpdate={lastUpdate} />
      </div>

      {/* Progress Bar (shown during processing) */}
      {loading && (
        <ProgressBar 
          progress={progress} 
          message="Analyzing satellite data and generating response plan..."
        />
      )}

      {/* Main Content - Split View */}
      <div className="main-content">
        {/* Left: Map */}
        <div className="map-panel">
          <MapView disaster={disaster} plan={plan} />
        </div>

        {/* Right: Emergency Plan */}
        <div className="plan-panel">
          {plan ? (
            <PlanViewer plan={plan} />
          ) : (
            <div className="empty-state">
              <h2>No Active Emergency</h2>
              <p>Trigger a disaster simulation to see RapidResponse AI in action</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
```

### Map/MapView.js

```jsx
import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import DangerZoneLayer from './DangerZoneLayer';
import EvacuationRoutes from './EvacuationRoutes';

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;

function MapView({ disaster, plan }) {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (map.current) return; // Initialize only once

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11', // Dark theme for emergency
      center: [-79.7624, 43.7315], // Brampton center
      zoom: 11
    });

    map.current.on('load', () => {
      setMapLoaded(true);
    });

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    return () => map.current.remove();
  }, []);

  // Update map when disaster data changes
  useEffect(() => {
    if (!mapLoaded || !disaster) return;

    // Fly to disaster location
    map.current.flyTo({
      center: [disaster.location.lon, disaster.location.lat],
      zoom: 13,
      duration: 2000
    });
  }, [disaster, mapLoaded]);

  return (
    <div className="map-view">
      <div ref={mapContainer} className="map-container" />
      
      {mapLoaded && disaster && (
        <>
          <DangerZoneLayer map={map.current} disaster={disaster} />
          {plan && (
            <EvacuationRoutes map={map.current} routes={plan.evacuation_plan.routes} />
          )}
        </>
      )}
    </div>
  );
}

export default MapView;
```

### Map/DangerZoneLayer.js

```jsx
import { useEffect } from 'react';

function DangerZoneLayer({ map, disaster }) {
  useEffect(() => {
    if (!map || !disaster) return;

    const sourceId = 'danger-zone';
    const layerId = 'danger-zone-fill';

    // Remove existing layer if present
    if (map.getLayer(layerId)) {
      map.removeLayer(layerId);
    }
    if (map.getSource(sourceId)) {
      map.removeSource(sourceId);
    }

    // Add danger zone polygon
    const firePerimeter = disaster.data?.fire_perimeter || {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [-79.8620, 43.7315],
          [-79.8520, 43.7315],
          [-79.8520, 43.7415],
          [-79.8620, 43.7415],
          [-79.8620, 43.7315]
        ]]
      }
    };

    map.addSource(sourceId, {
      type: 'geojson',
      data: firePerimeter
    });

    map.addLayer({
      id: layerId,
      type: 'fill',
      source: sourceId,
      paint: {
        'fill-color': '#ff0000',
        'fill-opacity': 0.4
      }
    });

    // Add border
    map.addLayer({
      id: `${layerId}-outline`,
      type: 'line',
      source: sourceId,
      paint: {
        'line-color': '#ff0000',
        'line-width': 2
      }
    });

    // Cleanup
    return () => {
      if (map.getLayer(layerId)) map.removeLayer(layerId);
      if (map.getLayer(`${layerId}-outline`)) map.removeLayer(`${layerId}-outline`);
      if (map.getSource(sourceId)) map.removeSource(sourceId);
    };
  }, [map, disaster]);

  return null;
}

export default DangerZoneLayer;
```

### EmergencyPlan/PlanViewer.js

```jsx
import React from 'react';
import ExecutiveSummary from './ExecutiveSummary';
import Timeline from './Timeline';
import ResourceTable from './ResourceTable';
import './PlanViewer.css';

function PlanViewer({ plan }) {
  return (
    <div className="plan-viewer">
      <div className="plan-header">
        <h2>📋 Emergency Response Plan</h2>
        <div className="plan-meta">
          <span className="disaster-id">{plan.disaster_id}</span>
          <span className="generated-time">
            Generated: {new Date(plan.generated_at).toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className="plan-content">
        <ExecutiveSummary summary={plan.executive_summary} />
        
        <section className="plan-section">
          <h3>🔥 Situation Overview</h3>
          <div className="situation-details">
            <p>{plan.situation_overview}</p>
            <div className="key-stats">
              <div className="stat">
                <span className="stat-value">{plan.population_impact.total_affected.toLocaleString()}</span>
                <span className="stat-label">People Affected</span>
              </div>
              <div className="stat">
                <span className="stat-value">{plan.affected_areas.affected_area_km2} km²</span>
                <span className="stat-label">Affected Area</span>
              </div>
              <div className="stat danger">
                <span className="stat-value">{plan.timeline_predictions.critical_arrival_times[0].hours_until_arrival}h</span>
                <span className="stat-label">Until Critical Impact</span>
              </div>
            </div>
          </div>
        </section>

        <section className="plan-section">
          <h3>🚨 Evacuation Orders</h3>
          <div className="evacuation-zones">
            {plan.evacuation_plan.zones?.map((zone, idx) => (
              <div key={idx} className={`zone-card priority-${zone.priority}`}>
                <div className="zone-header">
                  <span className="zone-name">{zone.id}</span>
                  <span className={`priority-badge ${zone.priority}`}>
                    {zone.priority.toUpperCase()}
                  </span>
                </div>
                <div className="zone-info">
                  <p><strong>{zone.population.toLocaleString()}</strong> people</p>
                  <p>Evacuation time: <strong>{zone.evacuation_routes[0].estimated_time_minutes} min</strong></p>
                </div>
              </div>
            )) || <p>Calculating evacuation zones...</p>}
          </div>
        </section>

        <Timeline predictions={plan.timeline_predictions} />
        
        <ResourceTable allocation={plan.resource_deployment} />

        <section className="plan-section">
          <h3>📢 Communication Templates</h3>
          <div className="templates">
            <div className="template-card">
              <h4>🇬🇧 English</h4>
              <p className="template-text">{plan.communication_templates.en}</p>
            </div>
            <div className="template-card">
              <h4>🇮🇳 ਪੰਜਾਬੀ Punjabi</h4>
              <p className="template-text">{plan.communication_templates.pa}</p>
            </div>
            <div className="template-card">
              <h4>🇮🇳 हिंदी Hindi</h4>
              <p className="template-text">{plan.communication_templates.hi}</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default PlanViewer;
```

### EmergencyPlan/Timeline.js

```jsx
import React from 'react';
import './Timeline.css';

function Timeline({ predictions }) {
  if (!predictions || !predictions.critical_arrival_times) {
    return null;
  }

  const events = predictions.critical_arrival_times;

  return (
    <section className="plan-section">
      <h3>⏱️ Timeline Predictions</h3>
      <div className="timeline">
        {events.map((event, idx) => (
          <div key={idx} className={`timeline-event ${event.confidence}`}>
            <div className="timeline-marker">
              <span className="time-value">{event.hours_until_arrival}h</span>
            </div>
            <div className="timeline-content">
              <h4>{event.location}</h4>
              <p className="confidence">Confidence: {event.confidence}</p>
            </div>
          </div>
        ))}
      </div>
      
      <div className="prediction-factors">
        <h4>Key Factors:</h4>
        <ul>
          <li>Wind speed: {predictions.factors.wind_speed_kmh} km/h</li>
          <li>Wind direction: {predictions.factors.wind_direction_deg}°</li>
          <li>Temperature: {predictions.factors.temperature_c}°C</li>
          <li>Humidity: {predictions.factors.humidity_percent}%</li>
        </ul>
        <p className="spread-rate">
          Current spread rate: <strong>{predictions.current_spread_rate_kmh.toFixed(1)} km/h</strong>
        </p>
      </div>
    </section>
  );
}

export default Timeline;
```

### Controls/DisasterTrigger.js

```jsx
import React, { useState } from 'react';
import './DisasterTrigger.css';

function DisasterTrigger({ onTrigger, disabled }) {
  const [type, setType] = useState('wildfire');
  const [severity, setSeverity] = useState('high');

  const handleTrigger = () => {
    onTrigger({
      type,
      location: {
        lat: 43.7315 + (Math.random() - 0.5) * 0.05,
        lon: -79.8620 + (Math.random() - 0.5) * 0.05
      },
      severity
    });
  };

  return (
    <div className="disaster-trigger">
      <h3>🎮 Simulate Disaster</h3>
      <div className="trigger-controls">
        <select value={type} onChange={(e) => setType(e.target.value)} disabled={disabled}>
          <option value="wildfire">🔥 Wildfire</option>
          <option value="flood">🌊 Flood (Coming Soon)</option>
        </select>
        
        <select value={severity} onChange={(e) => setSeverity(e.target.value)} disabled={disabled}>
          <option value="low">Low Severity</option>
          <option value="moderate">Moderate</option>
          <option value="high">High Severity</option>
          <option value="extreme">Extreme</option>
        </select>

        <button 
          onClick={handleTrigger} 
          disabled={disabled}
          className="trigger-button"
        >
          {disabled ? '⏳ Processing...' : '🚨 Trigger Event'}
        </button>
      </div>
    </div>
  );
}

export default DisasterTrigger;
```

---

## 🔌 Services

### services/api.js

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const disasterAPI = {
  trigger: async (disasterData) => {
    const response = await api.post('/disaster/trigger', disasterData);
    return response.data;
  },

  getDisaster: async (disasterId) => {
    const response = await api.get(`/disaster/${disasterId}`);
    return response.data;
  },

  getPlan: async (disasterId) => {
    const response = await api.get(`/disaster/${disasterId}/plan`);
    return response.data;
  }
};

export default api;
```

### services/websocket.js

```javascript
import React, { createContext, useContext, useEffect, useState } from 'react';
import io from 'socket.io-client';

const WebSocketContext = createContext(null);

export function WebSocketProvider({ children, url }) {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const newSocket = io(url || 'http://localhost:5000', {
      transports: ['websocket']
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
      setConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    });

    setSocket(newSocket);

    return () => newSocket.close();
  }, [url]);

  return (
    <WebSocketContext.Provider value={{ socket, connected }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocketContext() {
  return useContext(WebSocketContext);
}
```

---

## 🎣 Custom Hooks

### hooks/useDisaster.js

```javascript
import { useState, useCallback } from 'react';
import { disasterAPI } from '../services/api';
import { useWebSocketContext } from '../services/websocket';

function useDisaster() {
  const [disaster, setDisaster] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  
  const { socket } = useWebSocketContext();

  // Listen for WebSocket updates
  useEffect(() => {
    if (!socket) return;

    socket.on('progress', (data) => {
      setProgress(data.progress);
    });

    socket.on('disaster_complete', (data) => {
      setPlan(data.plan);
      setLoading(false);
      setProgress(100);
    });

    socket.on('plan_update', (data) => {
      setPlan(data.plan);
    });

    socket.on('disaster_error', (data) => {
      setError(data.error);
      setLoading(false);
    });

    return () => {
      socket.off('progress');
      socket.off('disaster_complete');
      socket.off('plan_update');
      socket.off('disaster_error');
    };
  }, [socket]);

  const triggerDisaster = useCallback(async (disasterData) => {
    try {
      setLoading(true);
      setProgress(0);
      setError(null);
      setPlan(null);

      const response = await disasterAPI.trigger(disasterData);
      setDisaster(response);

      // Subscribe to updates for this disaster
      if (socket) {
        socket.emit('subscribe_disaster', { disaster_id: response.disaster_id });
      }

    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }, [socket]);

  return {
    disaster,
    plan,
    loading,
    progress,
    error,
    triggerDisaster
  };
}

export default useDisaster;
```

---

## 🎨 Styling

### App.css (Key Styles)

```css
:root {
  --danger-red: #ff4444;
  --warning-orange: #ff9500;
  --safe-green: #4CAF50;
  --info-blue: #2196F3;
  --dark-bg: #1a1a1a;
  --card-bg: #2d2d2d;
  --text-primary: #ffffff;
  --text-secondary: #b0b0b0;
}

.App {
  min-height: 100vh;
  background: var(--dark-bg);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1.5rem 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.app-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.subtitle {
  margin: 0.5rem 0;
  opacity: 0.9;
  font-size: 1rem;
}

.disclaimer {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 0, 0.2);
  border: 2px solid #ffeb3b;
  border-radius: 4px;
  font-weight: 600;
}

.dashboard {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
}

.control-bar {
  display: flex;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: var(--card-bg);
  border-bottom: 1px solid #444;
}

.main-content {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 0;
  flex: 1;
  overflow: hidden;
}

.map-panel, .plan-panel {
  overflow: auto;
}

.map-container {
  width: 100%;
  height: 100%;
}

/* Emergency colors */
.priority-mandatory {
  border-left: 4px solid var(--danger-red);
}

.priority-warning {
  border-left: 4px solid var(--warning-orange);
}

.priority-watch {
  border-left: 4px solid var(--info-blue);
}
```

---

## 📦 Dependencies

```json
{
  "name": "rapidresponse-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "mapbox-gl": "^2.15.0",
    "socket.io-client": "^4.6.0",
    "axios": "^1.6.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
```

---

## 🚀 Running the Frontend

```bash
# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env
echo "REACT_APP_MAPBOX_TOKEN=your-mapbox-token" >> .env

# Start development server
npm start
```

App will open at `http://localhost:3000`

---

## 🎯 Key Features

1. **Real-time Updates**: WebSocket connection for live plan updates
2. **Interactive Map**: Mapbox GL for professional visualizations
3. **Responsive Design**: Works on different screen sizes
4. **Multi-language Support**: Display alerts in English, Punjabi, Hindi
5. **Progress Tracking**: Shows system working in real-time
6. **Clean UI**: Dark theme optimized for emergency operations

---

Next: See API Integration Guide for connecting frontend to backend.
