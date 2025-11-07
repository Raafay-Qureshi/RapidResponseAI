# RapidResponseAI - System Architecture Overview

## 🎯 Executive Summary

**RapidResponseAI** is an automated emergency response intelligence system that uses satellite data, real-time sensors, and multi-agent AI to generate complete emergency response plans in under 60 seconds.

**Core Value Proposition:** Reduce emergency analysis time from 2-3 hours to 60 seconds, enabling faster life-saving decisions.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                     (React Web Dashboard)                    │
│  - Real-time map visualization                              │
│  - Emergency plan display                                    │
│  - Alert controls                                            │
└────────────────────────┬────────────────────────────────────┘
                         │ WebSocket + REST API
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY / BACKEND                     │
│                    (Flask/FastAPI Server)                    │
│  - Request routing                                           │
│  - WebSocket management                                      │
│  - Authentication/rate limiting                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR SERVICE                       │
│              (Multi-Agent Coordinator)                       │
│  - Receives disaster trigger                                 │
│  - Coordinates all agents                                    │
│  - Manages data flow                                         │
│  - Generates final output                                    │
└───────┬─────────┬─────────┬─────────┬─────────┬────────────┘
        │         │         │         │         │
        ↓         ↓         ↓         ↓         ↓
┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Agent 1  │ │ Agent 2  │ │ Agent 3  │ │ Agent 4  │ │ Agent 5  │
│  Damage   │ │Population│ │ Routing  │ │Resource  │ │Prediction│
│Assessment │ │ Impact   │ │ Planning │ │Allocation│ │ Modeling │
└─────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
      │            │            │            │            │
      └────────────┴────────────┴────────────┴────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                      │
│  - Satellite API clients                                     │
│  - Weather data feeds                                        │
│  - Infrastructure databases                                  │
│  - Census/demographic data                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL DATA SOURCES                    │
│  • NASA FIRMS (fire detection)                              │
│  • NOAA GOES (satellite imagery)                            │
│  • OpenWeather (weather/wind)                               │
│  • OSM/OSRM (roads/routing)                                 │
│  • Brampton GeoHub (local data)                             │
│  • Claude API (LLM orchestration)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Component Breakdown

### 1. Frontend (React Dashboard)
- **Technology:** React 18, Mapbox GL JS, WebSocket
- **Responsibilities:**
  - Display real-time map with danger zones
  - Show generated emergency plans
  - Provide controls for simulation/testing
  - Real-time updates via WebSocket
  - Data visualization (charts, timelines)

### 2. Backend API Server
- **Technology:** Flask or FastAPI (Python)
- **Responsibilities:**
  - REST API endpoints
  - WebSocket server for real-time updates
  - Request validation
  - Error handling
  - API key management

### 3. Orchestrator Service
- **Technology:** Python with async/await
- **Responsibilities:**
  - Multi-agent coordination
  - Data aggregation
  - Claude API integration for synthesis
  - Response plan generation
  - Update scheduling (every 15 min)

### 4. Specialized Agents
Each agent is a Python module with specific responsibilities:

#### Agent 1: Damage Assessment
- Analyzes satellite imagery
- Detects disaster boundaries
- Calculates affected area
- Estimates severity

#### Agent 2: Population Impact
- Counts affected population
- Identifies vulnerable groups
- Finds critical facilities (schools, hospitals)
- Determines language demographics

#### Agent 3: Routing & Evacuation
- Calculates optimal evacuation routes
- Identifies safe zones
- Estimates evacuation time
- Considers real-time traffic

#### Agent 4: Resource Allocation
- Maps emergency service locations
- Calculates resource needs
- Optimizes deployment
- Identifies gaps

#### Agent 5: Prediction & Modeling
- Fire/flood spread simulation
- Timeline predictions
- Confidence intervals
- Scenario modeling

### 5. Data Ingestion Layer
- **Technology:** Python with requests, aiohttp
- **Responsibilities:**
  - API client wrappers
  - Data caching
  - Rate limiting
  - Retry logic
  - Data normalization

---

## 🔄 Data Flow

### Disaster Detection to Response Plan (60 seconds)

```
1. TRIGGER (T+0s)
   └─> Disaster detected (satellite or manual)

2. DATA INGESTION (T+5s)
   └─> Parallel API calls to all data sources
   └─> Cached data retrieved
   └─> Real-time data fetched

3. AGENT PROCESSING (T+10-30s)
   ├─> Agent 1: Analyzes satellite imagery (5s)
   ├─> Agent 2: Calculates population impact (5s)
   ├─> Agent 3: Generates routes (8s)
   ├─> Agent 4: Plans resource deployment (4s)
   └─> Agent 5: Runs prediction models (8s)

4. ORCHESTRATION (T+35-45s)
   └─> Orchestrator collects all agent outputs
   └─> Feeds to Claude API
   └─> Claude synthesizes into coherent plan

5. DOCUMENT GENERATION (T+45-55s)
   └─> Claude generates 12-page emergency plan
   └─> Maps and visualizations created
   └─> Multi-language translations

6. DELIVERY (T+60s)
   └─> Complete plan sent to frontend
   └─> WebSocket pushes to all connected clients
   └─> Maps updated with danger zones
```

---

## 💾 Data Models

### Disaster Event
```python
{
    "id": "fire-2025-11-06-001",
    "type": "wildfire",  # wildfire | flood | storm
    "detected_at": "2025-11-06T14:23:00Z",
    "location": {
        "lat": 43.7315,
        "lon": -79.8620
    },
    "severity": "high",
    "status": "active"
}
```

### Affected Area
```python
{
    "disaster_id": "fire-2025-11-06-001",
    "boundary": {
        "type": "Polygon",
        "coordinates": [[...]]  # GeoJSON polygon
    },
    "area_km2": 2.3,
    "confidence": 0.95
}
```

### Population Impact
```python
{
    "disaster_id": "fire-2025-11-06-001",
    "total_affected": 8430,
    "vulnerable_population": {
        "elderly": 1250,
        "children": 2100,
        "disabled": 340
    },
    "languages": {
        "english": 5224,
        "punjabi": 1517,
        "hindi": 759,
        "spanish": 340
    },
    "critical_facilities": [
        {
            "type": "school",
            "name": "Brampton Elementary",
            "location": {"lat": 43.73, "lon": -79.86},
            "population": 450
        }
    ]
}
```

### Evacuation Plan
```python
{
    "disaster_id": "fire-2025-11-06-001",
    "zones": [
        {
            "id": "zone-1",
            "priority": "mandatory",
            "population": 3200,
            "evacuation_routes": [
                {
                    "id": "route-a",
                    "path": [[lat, lon], ...],
                    "destination": "Safe Zone Alpha",
                    "estimated_time_minutes": 45
                }
            ]
        }
    ]
}
```

### Emergency Response Plan (Final Output)
```python
{
    "disaster_id": "fire-2025-11-06-001",
    "generated_at": "2025-11-06T14:24:00Z",
    "confidence": 0.87,
    "sections": {
        "executive_summary": "...",
        "situation_overview": "...",
        "affected_areas": {...},
        "evacuation_orders": {...},
        "resource_deployment": {...},
        "timeline_predictions": {...},
        "communication_templates": {...}
    },
    "maps": [
        {
            "title": "Danger Zones",
            "url": "/api/maps/danger-zones/..."
        }
    ],
    "languages": ["en", "pa", "hi"]
}
```

---

## 🔐 Security Considerations

### API Security
- All external API keys stored in environment variables
- Rate limiting on all endpoints
- Input validation and sanitization
- CORS configured for frontend origin only

### Data Privacy
- No personal data stored
- Demographic data aggregated only
- Location data anonymized where possible

### Demo Safety
- Clearly labeled as "SIMULATION" in UI
- Disclaimer: "For demonstration purposes only"
- Not connected to real emergency systems

---

## 📊 Performance Requirements

### Response Times
- Disaster detection to initial display: < 5 seconds
- Complete plan generation: < 60 seconds
- Map updates: < 2 seconds
- WebSocket message delivery: < 100ms

### Scalability (for demo)
- Support 10+ concurrent users
- Handle 1 disaster scenario at a time
- Process updates every 15 minutes

### Data Volume
- Satellite imagery: ~50MB per event
- Generated plans: ~2MB per event
- Map tiles: Cached, served from CDN

---

## 🛠️ Technology Stack Summary

### Backend
- **Language:** Python 3.11+
- **Framework:** Flask or FastAPI
- **Async:** asyncio, aiohttp
- **Geospatial:** geopandas, shapely, rasterio
- **Routing:** OSRM Python client
- **WebSocket:** Flask-SocketIO or FastAPI WebSocket

### Frontend
- **Framework:** React 18
- **Mapping:** Mapbox GL JS
- **Charts:** Chart.js or Recharts
- **State Management:** React Context or Zustand
- **HTTP Client:** Axios
- **WebSocket:** socket.io-client

### AI/ML
- **LLM:** Claude 3.5 Sonnet (via Anthropic API)
- **Vision:** GPT-4 Vision (optional, for image analysis)
- **Fire Modeling:** Custom cellular automata

### External Services
- NASA FIRMS
- NOAA GOES
- OpenWeather
- OpenStreetMap
- OSRM
- Brampton GeoHub

### Development Tools
- **Version Control:** Git
- **Package Management:** pip (Python), npm (Node)
- **Environment:** Docker (optional, for deployment)
- **Testing:** pytest (Python), Jest (React)

---

## 🚀 Deployment Architecture (Hackathon)

### Simple Setup (Recommended for 3 days)
```
┌─────────────────┐
│   Frontend      │ → Served via npm start (localhost:3000)
│   (React)       │
└─────────────────┘
        ↓ HTTP/WebSocket
┌─────────────────┐
│   Backend       │ → Flask server (localhost:5000)
│   (Python)      │
└─────────────────┘
        ↓ API calls
┌─────────────────┐
│ External APIs   │ → NASA, NOAA, OpenWeather, etc.
└─────────────────┘
```

### File Structure
```
rapidresponse-ai/
├── backend/
│   ├── app.py              # Flask server
│   ├── orchestrator.py     # Multi-agent coordinator
│   ├── agents/
│   │   ├── damage_assessment.py
│   │   ├── population_impact.py
│   │   ├── routing.py
│   │   ├── resource_allocation.py
│   │   └── prediction.py
│   ├── data/
│   │   ├── satellite_client.py
│   │   ├── weather_client.py
│   │   └── geohub_client.py
│   ├── models/
│   │   └── fire_spread.py
│   └── utils/
│       ├── geospatial.py
│       └── config.py
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── Map.js
│   │   │   ├── EmergencyPlan.js
│   │   │   ├── Timeline.js
│   │   │   └── Controls.js
│   │   ├── services/
│   │   │   └── api.js
│   │   └── utils/
│   │       └── websocket.js
│   └── public/
├── docs/
│   └── architecture/ (these documents)
└── README.md
```

---

## 🔄 Update Mechanism (Every 15 Minutes)

```python
# Pseudo-code for update loop
async def update_loop(disaster_id):
    while disaster.status == "active":
        # 1. Re-fetch latest data
        new_satellite_data = await fetch_satellite()
        new_weather = await fetch_weather()
        
        # 2. Re-run models
        updated_spread = predict_fire_spread(new_satellite_data, new_weather)
        
        # 3. Re-generate affected sections
        if updated_spread.changed_significantly():
            updated_plan = await regenerate_plan_sections(disaster_id, updated_spread)
            
            # 4. Push to clients
            await websocket.broadcast({
                "type": "plan_update",
                "disaster_id": disaster_id,
                "updated_sections": updated_plan,
                "changes": calculate_diff(old_plan, updated_plan)
            })
        
        # 5. Wait 15 minutes
        await asyncio.sleep(900)
```

---

## 📝 Next Steps

1. Review detailed architecture documents:
   - `02_BACKEND_ARCHITECTURE.md`
   - `03_FRONTEND_ARCHITECTURE.md`
   - `04_AGENT_ARCHITECTURE.md`
   - `05_API_INTEGRATIONS.md`

2. Check implementation guides:
   - `06_DAY_BY_DAY_PLAN.md`
   - `07_DEMO_SCRIPT.md`
   - `08_TROUBLESHOOTING.md`

3. Set up development environment (see Day 0 guide)