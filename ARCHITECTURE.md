# System Architecture

Technical overview of RapidResponseAI's design and implementation.

## High-Level Overview

```
┌──────────────────────────────────────┐
│      React Dashboard (Frontend)      │
│  • Map visualization (Mapbox)        │
│  • Real-time updates (WebSocket)     │
│  • Emergency plan display            │
└──────────────┬───────────────────────┘
               ↓ REST API + WebSocket
┌──────────────────────────────────────┐
│      Flask Backend (Python)          │
│  • API endpoints                     │
│  • WebSocket server                  │
│  • Request coordination              │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│      Orchestrator Service            │
│  • Agent coordination                │
│  • LLM synthesis (OpenRouter)        │
│  • Response generation               │
└───┬──────┬──────┬──────┬──────┬──────┘
    ↓      ↓      ↓      ↓      ↓
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Damage  │ │Popula- │ │Routing │ │Resource│ │Predic- │
│Assess  │ │tion    │ │Planning│ │Alloca- │ │tion    │
│Agent   │ │Agent   │ │Agent   │ │tion    │ │Agent   │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
    ↓          ↓          ↓          ↓          ↓
┌──────────────────────────────────────────────────────┐
│           External Data Sources                      │
│  NASA FIRMS • OpenWeather • OpenStreetMap           │
└──────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend (React)

**Location:** [`frontend/src/`](frontend/src/)

**Key Files:**
- [`Dashboard.js`](frontend/src/components/Dashboard.js) - Main UI component
- [`MapView.js`](frontend/src/components/Map/MapView.js) - Mapbox integration
- [`useWebSocket.js`](frontend/src/hooks/useWebSocket.js) - Real-time updates
- [`api.js`](frontend/src/services/api.js) - Backend communication

**Responsibilities:**
- Display real-time disaster map
- Visualize danger zones & evacuation routes
- Show generated emergency plans
- Handle user interactions
- Receive WebSocket updates

### 2. Backend (Flask)

**Location:** [`backend/`](backend/)

**Key Files:**
- [`app.py`](backend/app.py) - Flask server & WebSocket setup
- [`routes.py`](backend/routes.py) - API endpoints
- [`sockets.py`](backend/sockets.py) - WebSocket handlers

**API Endpoints:**
```python
POST /api/disaster/trigger   # Start disaster analysis
GET  /api/disaster/:id        # Get disaster status
GET  /api/disaster/:id/plan   # Get emergency plan
```

**WebSocket Events:**
```python
'connect'     # Client connection
'progress'    # Analysis progress updates
'plan_ready'  # Plan generation complete
'plan_update' # Periodic plan updates
```

### 3. Orchestrator

**Location:** [`backend/orchestrator.py`](backend/orchestrator.py)

**Process Flow (60 seconds):**

```
1. Receive Disaster Trigger (T+0s)
   └─ Location, type, severity

2. Data Collection (T+5s)
   ├─ Fetch satellite imagery (NASA FIRMS)
   ├─ Get weather data (OpenWeather)
   └─ Load infrastructure (GeoHub)

3. Agent Analysis (T+10-30s) - Parallel Execution
   ├─ Damage Assessment Agent (5s)
   │  └─ Analyzes affected area, severity
   ├─ Population Impact Agent (5s)
   │  └─ Calculates affected population
   ├─ Routing Agent (8s)
   │  └─ Generates evacuation routes
   ├─ Resource Allocation Agent (4s)
   │  └─ Plans emergency resource deployment
   └─ Prediction Agent (8s)
      └─ Models fire spread & timeline

4. LLM Synthesis (T+35-50s)
   └─ OpenRouter API generates coherent plan

5. Delivery (T+55-60s)
   └─ WebSocket push to all clients
```

### 4. AI Agents

**Location:** [`backend/agents/`](backend/agents/)

Each agent inherits from [`BaseAgent`](backend/agents/base_agent.py) and implements `analyze()` method.

#### Damage Assessment Agent
**File:** [`damage_assessment.py`](backend/agents/damage_assessment.py)

**Input:** Satellite thermal anomaly data  
**Output:** Affected area boundaries, severity classification  
**Processing:** GeoJSON polygon generation, area calculation

#### Population Impact Agent
**File:** [`population_impact.py`](backend/agents/population_impact.py)

**Input:** Disaster boundaries, census data  
**Output:** Affected population count, vulnerable groups, critical facilities  
**Processing:** Spatial intersection, demographic analysis

#### Routing Agent
**File:** [`routing.py`](backend/agents/routing.py)

**Input:** Danger zones, road network  
**Output:** Evacuation routes, safe zones, estimated times  
**Processing:** Graph algorithms, route optimization

#### Resource Allocation Agent
**File:** [`resource_allocation.py`](backend/agents/resource_allocation.py)

**Input:** Population impact, infrastructure  
**Output:** Required resources, deployment plan  
**Processing:** Demand calculation, facility mapping

#### Prediction Agent
**File:** [`prediction.py`](backend/agents/prediction.py)

**Input:** Current fire state, weather, terrain  
**Output:** Spread predictions, timeline  
**Processing:** Cellular automata, wind modeling

### 5. Data Clients

**Location:** [`backend/data/`](backend/data/)

#### Satellite Client
**File:** [`satellite_client.py`](backend/data/satellite_client.py)  
**API:** NASA FIRMS  
**Data:** Thermal anomalies, confidence scores

#### Weather Client
**File:** [`weather_client.py`](backend/data/weather_client.py)  
**API:** OpenWeather  
**Data:** Temperature, wind speed/direction, humidity

#### GeoHub Client
**File:** [`geohub_client.py`](backend/data/geohub_client.py)  
**Source:** Brampton Open Data  
**Data:** Roads, infrastructure, population

## Data Flow

### Emergency Plan Generation

```python
# Simplified orchestrator flow
async def generate_plan(disaster):
    # 1. Collect data
    satellite_data = await satellite_client.fetch(disaster.location)
    weather_data = await weather_client.fetch(disaster.location)
    infrastructure = await geohub_client.load()
    
    # 2. Run agents in parallel
    agent_results = await asyncio.gather(
        damage_agent.analyze(satellite_data),
        population_agent.analyze(disaster.boundary, infrastructure),
        routing_agent.analyze(disaster.boundary, infrastructure),
        resource_agent.analyze(population_impact),
        prediction_agent.analyze(satellite_data, weather_data)
    )
    
    # 3. Synthesize with LLM
    plan = await llm_synthesize(agent_results)
    
    # 4. Return complete plan
    return plan
```

### Real-Time Updates

```python
# Update loop (every 15 minutes)
while disaster.active:
    # Re-fetch latest data
    new_data = await fetch_latest()
    
    # Re-run affected agents
    updated_results = await re_analyze(new_data)
    
    # Generate delta
    changes = calculate_diff(old_plan, updated_results)
    
    # Push to clients
    await websocket.emit('plan_update', changes)
    
    await asyncio.sleep(900)  # 15 minutes
```

## Technology Choices

### Why Flask?
- Fast setup for hackathon
- WebSocket support via Flask-SocketIO
- Python ecosystem for geospatial processing

### Why React?
- Component reusability
- Fast development
- Good mapping libraries (Mapbox GL JS)

### Why OpenRouter?
- Access to multiple LLM providers
- No vendor lock-in
- Simple API

### Why Multi-Agent Architecture?
- **Parallel processing:** Faster than sequential
- **Separation of concerns:** Each agent specialized
- **Scalability:** Easy to add new agents
- **Testability:** Agents tested independently

## Performance Considerations

### Optimization Strategies

1. **Parallel Agent Execution**
   - All 5 agents run simultaneously
   - Reduces total time from ~30s to ~8s

2. **Caching**
   - Static infrastructure data cached
   - Weather data cached for 10 minutes
   - Satellite data cached for 5 minutes

3. **Async Operations**
   - All external API calls async
   - Non-blocking I/O
   - WebSocket updates don't block processing

4. **Demo Mode**
   - Pre-cached responses for reliability
   - No external API dependencies
   - Instant results

## Security

- API keys in environment variables
- CORS configured for frontend origin
- Input validation on all endpoints
- Rate limiting on API routes
- No sensitive data stored

## Testing

**Unit Tests:** [`backend/tests/`](backend/tests/)
- Individual agent testing
- API client mocking
- Data processing validation

**Integration Tests:**
- Full orchestrator flow
- End-to-end scenarios
- WebSocket communication

## Deployment

### Development
```bash
# Backend: localhost:5000
python backend/app.py

# Frontend: localhost:3000
npm start
```

### Production (Hackathon Demo)
- Use Demo Mode for reliability
- Pre-cache all data
- Test on presentation hardware
- Have offline backup (video)

## File Structure

```
RapidResponseAI/
├── backend/
│   ├── app.py              # Flask server
│   ├── orchestrator.py     # Multi-agent coordinator
│   ├── routes.py           # API endpoints
│   ├── sockets.py          # WebSocket handlers
│   ├── agents/             # AI agents
│   ├── data/               # API clients
│   ├── scenarios/          # Test scenarios
│   ├── tests/              # Unit tests
│   └── utils/              # Helper functions
├── frontend/
│   └── src/
│       ├── components/     # React components
│       ├── hooks/          # Custom hooks
│       └── services/       # API/WebSocket clients
└── docs/                   # Documentation
```

## Extension Points

Want to add features?

- **New Agent:** Extend [`BaseAgent`](backend/agents/base_agent.py)
- **New Data Source:** Create client in [`backend/data/`](backend/data/)
- **New Disaster Type:** Add scenario in [`backend/scenarios/`](backend/scenarios/)
- **New Visualization:** Add component in [`frontend/src/components/`](frontend/src/components/)

## Next Steps

- Review [`SETUP.md`](./SETUP.md) for installation
- Check [`CONTRIBUTING.md`](./CONTRIBUTING.md) for development
- Explore code in [`backend/`](./backend/) and [`frontend/`](./frontend/)

---

**Questions?** Check code comments or create an issue.