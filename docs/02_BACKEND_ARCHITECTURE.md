# RapidResponseAI - Backend Architecture

## 🎯 Overview

The backend is a Python-based system that coordinates data ingestion, agent processing, and response generation. Built for speed and reliability in a 3-day hackathon context.

---

## 🏗️ Backend Components

### 1. Flask/FastAPI Server (`app.py`)

```python
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import asyncio

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins="*")

# REST Endpoints
@app.route('/api/disaster/trigger', methods=['POST'])
def trigger_disaster():
    """
    Manually trigger a disaster simulation
    Request body:
    {
        "type": "wildfire",
        "location": {"lat": 43.7315, "lon": -79.8620},
        "severity": "high"
    }
    """
    data = request.json
    disaster_id = orchestrator.create_disaster(data)
    
    # Start async processing
    socketio.start_background_task(
        target=orchestrator.process_disaster,
        disaster_id=disaster_id
    )
    
    return jsonify({
        "disaster_id": disaster_id,
        "status": "processing"
    })

@app.route('/api/disaster/<disaster_id>', methods=['GET'])
def get_disaster(disaster_id):
    """Get current state of a disaster"""
    disaster = orchestrator.get_disaster(disaster_id)
    return jsonify(disaster)

@app.route('/api/disaster/<disaster_id>/plan', methods=['GET'])
def get_plan(disaster_id):
    """Get generated emergency plan"""
    plan = orchestrator.get_plan(disaster_id)
    return jsonify(plan)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'WebSocket connected'})

@socketio.on('subscribe_disaster')
def handle_subscribe(data):
    """Subscribe to updates for a specific disaster"""
    disaster_id = data['disaster_id']
    join_room(disaster_id)
    emit('subscribed', {'disaster_id': disaster_id})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
```

---

### 2. Orchestrator Service (`orchestrator.py`)

The brain of the system - coordinates all agents and generates final output.

```python
import asyncio
from typing import Dict, List
import uuid
from datetime import datetime

class DisasterOrchestrator:
    def __init__(self):
        self.active_disasters = {}
        self.data_clients = DataClients()
        self.agents = {
            'damage': DamageAssessmentAgent(),
            'population': PopulationImpactAgent(),
            'routing': RoutingAgent(),
            'resource': ResourceAllocationAgent(),
            'prediction': PredictionAgent()
        }
        
    def create_disaster(self, trigger_data: Dict) -> str:
        """Create new disaster event"""
        disaster_id = f"{trigger_data['type']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        self.active_disasters[disaster_id] = {
            'id': disaster_id,
            'type': trigger_data['type'],
            'location': trigger_data['location'],
            'status': 'initializing',
            'created_at': datetime.now().isoformat(),
            'data': {},
            'plan': None
        }
        
        return disaster_id
    
    async def process_disaster(self, disaster_id: str):
        """Main processing pipeline"""
        disaster = self.active_disasters[disaster_id]
        
        try:
            # PHASE 1: Data Ingestion (5 seconds)
            disaster['status'] = 'fetching_data'
            data = await self._fetch_all_data(disaster)
            disaster['data'] = data
            
            # Emit progress update
            socketio.emit('progress', {
                'disaster_id': disaster_id,
                'phase': 'data_ingestion',
                'progress': 20
            })
            
            # PHASE 2: Agent Processing (25 seconds)
            disaster['status'] = 'analyzing'
            agent_results = await self._run_all_agents(disaster, data)
            disaster['agent_results'] = agent_results
            
            socketio.emit('progress', {
                'disaster_id': disaster_id,
                'phase': 'agent_processing',
                'progress': 60
            })
            
            # PHASE 3: Synthesis (20 seconds)
            disaster['status'] = 'generating_plan'
            plan = await self._synthesize_plan(disaster, agent_results)
            disaster['plan'] = plan
            disaster['status'] = 'complete'
            
            # Emit final result
            socketio.emit('disaster_complete', {
                'disaster_id': disaster_id,
                'plan': plan
            }, room=disaster_id)
            
            # PHASE 4: Start update loop
            asyncio.create_task(self._update_loop(disaster_id))
            
        except Exception as e:
            disaster['status'] = 'error'
            disaster['error'] = str(e)
            socketio.emit('disaster_error', {
                'disaster_id': disaster_id,
                'error': str(e)
            })
    
    async def _fetch_all_data(self, disaster: Dict) -> Dict:
        """Fetch data from all sources in parallel"""
        location = disaster['location']
        disaster_type = disaster['type']
        
        # Parallel API calls
        tasks = [
            self.data_clients.satellite.fetch_imagery(location),
            self.data_clients.weather.fetch_current(location),
            self.data_clients.geohub.fetch_infrastructure(location),
            self.data_clients.geohub.fetch_population(location),
            self.data_clients.osm.fetch_roads(location)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            'satellite_imagery': results[0],
            'weather': results[1],
            'infrastructure': results[2],
            'population': results[3],
            'roads': results[4]
        }
    
    async def _run_all_agents(self, disaster: Dict, data: Dict) -> Dict:
        """Run all agents in parallel"""
        location = disaster['location']
        
        # Agents can run in parallel since they're independent
        tasks = [
            self.agents['damage'].analyze(data['satellite_imagery'], disaster['type']),
            self.agents['population'].analyze(location, data['population']),
            self.agents['routing'].plan_routes(location, data['roads']),
            self.agents['resource'].allocate(location, data['infrastructure']),
            self.agents['prediction'].model_spread(disaster, data)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            'damage_assessment': results[0],
            'population_impact': results[1],
            'evacuation_routes': results[2],
            'resource_allocation': results[3],
            'predictions': results[4]
        }
    
    async def _synthesize_plan(self, disaster: Dict, agent_results: Dict) -> Dict:
        """Use Claude API to synthesize final plan"""
        
        # Prepare context for Claude
        context = {
            'disaster_type': disaster['type'],
            'location': disaster['location'],
            'timestamp': disaster['created_at'],
            'agent_outputs': agent_results
        }
        
        # Call Claude API
        claude_response = await self._call_claude_api(context)
        
        # Structure the plan
        plan = {
            'executive_summary': claude_response['summary'],
            'situation_overview': claude_response['overview'],
            'affected_areas': agent_results['damage_assessment'],
            'population_impact': agent_results['population_impact'],
            'evacuation_plan': agent_results['evacuation_routes'],
            'resource_deployment': agent_results['resource_allocation'],
            'timeline_predictions': agent_results['predictions'],
            'communication_templates': claude_response['templates'],
            'maps': self._generate_map_urls(disaster['id'], agent_results),
            'generated_at': datetime.now().isoformat()
        }
        
        return plan
    
    async def _call_claude_api(self, context: Dict) -> Dict:
        """Call Claude API to generate plan text"""
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        prompt = f"""
        You are an emergency response coordinator. Generate a comprehensive emergency response plan.
        
        DISASTER INFORMATION:
        - Type: {context['disaster_type']}
        - Location: {context['location']}
        - Time: {context['timestamp']}
        
        ANALYSIS FROM SPECIALIZED SYSTEMS:
        {json.dumps(context['agent_outputs'], indent=2)}
        
        Generate a complete emergency response plan with:
        1. Executive Summary (2-3 sentences)
        2. Situation Overview (detailed analysis)
        3. Communication templates in English, Punjabi, and Hindi
        
        Be specific, actionable, and use the exact data provided.
        """
        
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse Claude's response
        response_text = message.content[0].text
        
        # Extract sections (simplified for demo)
        return {
            'summary': self._extract_section(response_text, 'Executive Summary'),
            'overview': self._extract_section(response_text, 'Situation Overview'),
            'templates': self._extract_section(response_text, 'Communication')
        }
    
    async def _update_loop(self, disaster_id: str):
        """Update loop - runs every 15 minutes"""
        while self.active_disasters[disaster_id]['status'] == 'complete':
            await asyncio.sleep(900)  # 15 minutes
            
            # Re-fetch data
            disaster = self.active_disasters[disaster_id]
            new_data = await self._fetch_all_data(disaster)
            
            # Re-run prediction agent
            new_predictions = await self.agents['prediction'].model_spread(disaster, new_data)
            
            # Check if significant changes
            if self._has_significant_changes(
                disaster['agent_results']['predictions'],
                new_predictions
            ):
                # Update plan
                disaster['agent_results']['predictions'] = new_predictions
                updated_plan = await self._synthesize_plan(disaster, disaster['agent_results'])
                disaster['plan'] = updated_plan
                
                # Emit update
                socketio.emit('plan_update', {
                    'disaster_id': disaster_id,
                    'updated_sections': ['timeline_predictions'],
                    'plan': updated_plan
                }, room=disaster_id)
    
    def _has_significant_changes(self, old_pred: Dict, new_pred: Dict) -> bool:
        """Check if predictions changed significantly"""
        # Simple threshold check
        old_area = old_pred.get('affected_area_km2', 0)
        new_area = new_pred.get('affected_area_km2', 0)
        return abs(new_area - old_area) / old_area > 0.1  # 10% change

# Global instance
orchestrator = DisasterOrchestrator()
```

---

### 3. Agent Implementations

Each agent is a separate module with a consistent interface.

#### Base Agent Class

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main analysis method - must be implemented by each agent
        Returns a dictionary with analysis results
        """
        pass
    
    def _log(self, message: str):
        """Log agent activity"""
        print(f"[{self.name}] {message}")
```

#### Damage Assessment Agent (`agents/damage_assessment.py`)

```python
from .base_agent import BaseAgent
import numpy as np
from typing import Dict

class DamageAssessmentAgent(BaseAgent):
    async def analyze(self, satellite_imagery: Dict, disaster_type: str) -> Dict:
        """
        Analyze satellite imagery to assess damage extent
        
        For hackathon: Simplified using bounding box calculations
        Production: Would use computer vision models
        """
        self._log(f"Analyzing {disaster_type} damage from satellite data")
        
        if disaster_type == "wildfire":
            return await self._assess_fire_damage(satellite_imagery)
        elif disaster_type == "flood":
            return await self._assess_flood_damage(satellite_imagery)
        else:
            raise ValueError(f"Unknown disaster type: {disaster_type}")
    
    async def _assess_fire_damage(self, imagery: Dict) -> Dict:
        """Assess fire damage extent"""
        # In real system: Use thermal bands, NDVI analysis, etc.
        # For demo: Simulate based on NASA FIRMS data
        
        fire_perimeter = imagery.get('fire_perimeter')  # GeoJSON polygon
        
        # Calculate area
        area_km2 = self._calculate_polygon_area(fire_perimeter)
        
        # Estimate severity based on thermal data
        thermal_intensity = imagery.get('thermal_intensity', 350)  # Kelvin
        severity = self._calculate_severity(thermal_intensity)
        
        return {
            'affected_area_km2': area_km2,
            'fire_perimeter': fire_perimeter,
            'severity': severity,
            'confidence': 0.92,
            'analysis_time': datetime.now().isoformat()
        }
    
    def _calculate_polygon_area(self, polygon: Dict) -> float:
        """Calculate area of GeoJSON polygon in km²"""
        from shapely.geometry import shape
        from pyproj import Geod
        
        geom = shape(polygon)
        geod = Geod(ellps="WGS84")
        area_m2, _ = geod.geometry_area_perimeter(geom)
        return abs(area_m2) / 1_000_000  # Convert to km²
    
    def _calculate_severity(self, thermal_intensity: float) -> str:
        """Classify severity based on thermal intensity"""
        if thermal_intensity > 400:
            return "extreme"
        elif thermal_intensity > 370:
            return "high"
        elif thermal_intensity > 340:
            return "moderate"
        else:
            return "low"
```

#### Population Impact Agent (`agents/population_impact.py`)

```python
from .base_agent import BaseAgent
import geopandas as gpd
from typing import Dict

class PopulationImpactAgent(BaseAgent):
    async def analyze(self, location: Dict, population_data: Dict) -> Dict:
        """
        Calculate affected population and identify vulnerable groups
        """
        self._log("Analyzing population impact")
        
        # Get affected area boundary (from damage assessment)
        affected_boundary = population_data.get('affected_boundary')
        
        # Spatial join: Find census blocks within affected area
        census_blocks = gpd.read_file(population_data['census_shapefile'])
        affected_blocks = census_blocks[
            census_blocks.intersects(affected_boundary)
        ]
        
        # Calculate totals
        total_population = affected_blocks['population'].sum()
        elderly = affected_blocks['age_65_plus'].sum()
        children = affected_blocks['age_under_18'].sum()
        
        # Language breakdown
        languages = affected_blocks.groupby('primary_language')['population'].sum()
        
        # Find critical facilities
        facilities = self._find_critical_facilities(affected_boundary)
        
        return {
            'total_affected': int(total_population),
            'vulnerable_population': {
                'elderly': int(elderly),
                'children': int(children)
            },
            'languages': languages.to_dict(),
            'critical_facilities': facilities,
            'affected_neighborhoods': affected_blocks['neighborhood'].tolist()
        }
    
    def _find_critical_facilities(self, boundary) -> List[Dict]:
        """Find schools, hospitals, etc. within boundary"""
        # Query Brampton GeoHub or OSM for facilities
        facilities = []
        
        # Simplified for demo - would query actual databases
        example_facilities = [
            {
                'type': 'elementary_school',
                'name': 'Brampton Heights Elementary',
                'location': {'lat': 43.731, 'lon': -79.862},
                'population': 450
            },
            {
                'type': 'senior_center',
                'name': 'Golden Years Community Center',
                'location': {'lat': 43.733, 'lon': -79.859},
                'population': 120
            }
        ]
        
        return example_facilities
```

#### Routing Agent (`agents/routing.py`)

```python
from .base_agent import BaseAgent
import requests
from typing import Dict, List

class RoutingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.osrm_url = "http://router.project-osrm.org"
    
    async def analyze(self, location: Dict, roads: Dict) -> Dict:
        """
        Plan optimal evacuation routes
        """
        self._log("Planning evacuation routes")
        
        # Define danger zone and safe zones
        danger_zone = roads['danger_zone']
        safe_zones = self._identify_safe_zones(location, danger_zone)
        
        # Find evacuation origins (neighborhood centroids)
        origins = self._get_evacuation_origins(danger_zone)
        
        # Calculate routes for each origin
        routes = []
        for origin in origins:
            best_route = await self._calculate_best_route(origin, safe_zones)
            routes.append(best_route)
        
        # Estimate total evacuation time
        evacuation_time = self._estimate_evacuation_time(routes)
        
        return {
            'routes': routes,
            'safe_zones': safe_zones,
            'estimated_evacuation_time_minutes': evacuation_time,
            'primary_route': routes[0],  # Highest capacity route
            'alternate_routes': routes[1:]
        }
    
    async def _calculate_best_route(self, origin: Dict, safe_zones: List[Dict]) -> Dict:
        """Use OSRM to calculate optimal route"""
        # Try each safe zone, pick shortest
        best_route = None
        best_time = float('inf')
        
        for safe_zone in safe_zones:
            # OSRM query
            url = f"{self.osrm_url}/route/v1/driving/{origin['lon']},{origin['lat']};{safe_zone['lon']},{safe_zone['lat']}"
            params = {
                'overview': 'full',
                'geometries': 'geojson'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                route = data['routes'][0]
                
                if route['duration'] < best_time:
                    best_time = route['duration']
                    best_route = {
                        'origin': origin,
                        'destination': safe_zone,
                        'path': route['geometry'],  # GeoJSON LineString
                        'distance_km': route['distance'] / 1000,
                        'time_minutes': route['duration'] / 60
                    }
        
        return best_route
    
    def _identify_safe_zones(self, location: Dict, danger_zone) -> List[Dict]:
        """Identify safe evacuation destinations"""
        # Query for community centers, arenas, schools outside danger zone
        # Simplified for demo
        return [
            {
                'name': 'Brampton Soccer Centre',
                'lat': 43.7150,
                'lon': -79.8400,
                'capacity': 2000
            },
            {
                'name': 'CAA Centre',
                'lat': 43.7300,
                'lon': -79.7500,
                'capacity': 5000
            }
        ]
```

#### Resource Allocation Agent (`agents/resource_allocation.py`)

```python
from .base_agent import BaseAgent
from typing import Dict, List

class ResourceAllocationAgent(BaseAgent):
    async def analyze(self, location: Dict, infrastructure: Dict) -> Dict:
        """
        Determine resource needs and optimal deployment
        """
        self._log("Planning resource allocation")
        
        # Get population impact data
        affected_population = infrastructure.get('affected_population', 8430)
        vulnerable_population = infrastructure.get('vulnerable_population', {})
        
        # Calculate needs
        ambulances_needed = self._calculate_ambulances(vulnerable_population)
        buses_needed = self._calculate_buses(affected_population)
        personnel_needed = self._calculate_personnel(affected_population)
        
        # Map current resources
        current_resources = self._map_current_resources(location)
        
        # Optimize deployment
        deployment_plan = self._optimize_deployment(
            current_resources,
            {
                'ambulances': ambulances_needed,
                'buses': buses_needed,
                'personnel': personnel_needed
            }
        )
        
        return {
            'required_resources': {
                'ambulances': ambulances_needed,
                'evacuation_buses': buses_needed,
                'personnel': personnel_needed
            },
            'available_resources': current_resources,
            'deployment_plan': deployment_plan,
            'resource_gaps': self._identify_gaps(current_resources, deployment_plan)
        }
    
    def _calculate_ambulances(self, vulnerable_pop: Dict) -> int:
        """Estimate ambulance needs"""
        elderly = vulnerable_pop.get('elderly', 0)
        disabled = vulnerable_pop.get('disabled', 0)
        # Assume 1 ambulance per 100 vulnerable individuals
        return max(1, (elderly + disabled) // 100)
    
    def _calculate_buses(self, total_population: int) -> int:
        """Estimate evacuation bus needs"""
        # Assume 80% have cars, 20% need buses
        # Each bus holds ~50 people
        people_needing_buses = total_population * 0.20
        return max(1, int(people_needing_buses / 50))
    
    def _map_current_resources(self, location: Dict) -> Dict:
        """Map fire stations, hospitals, ambulance bases"""
        # Query infrastructure databases
        # Simplified for demo
        return {
            'fire_stations': [
                {'id': 'FS-202', 'lat': 43.720, 'lon': -79.840, 'trucks': 3},
                {'id': 'FS-205', 'lat': 43.735, 'lon': -79.875, 'trucks': 2}
            ],
            'hospitals': [
                {'id': 'Brampton Civic', 'lat': 43.731, 'lon': -79.762, 'ambulances': 8}
            ],
            'police_stations': [
                {'id': 'PS-21', 'lat': 43.728, 'lon': -79.830, 'units': 12}
            ]
        }
```

#### Prediction Agent (`agents/prediction.py`)

```python
from .base_agent import BaseAgent
import numpy as np
from typing import Dict

class PredictionAgent(BaseAgent):
    async def analyze(self, disaster: Dict, data: Dict) -> Dict:
        """
        Model disaster spread and generate timeline predictions
        """
        self._log(f"Modeling {disaster['type']} spread")
        
        if disaster['type'] == 'wildfire':
            return await self._model_fire_spread(disaster, data)
        elif disaster['type'] == 'flood':
            return await self._model_flood_spread(disaster, data)
        else:
            raise ValueError(f"Unknown disaster type: {disaster['type']}")
    
    async def _model_fire_spread(self, disaster: Dict, data: Dict) -> Dict:
        """
        Simplified cellular automata fire spread model
        """
        # Get inputs
        weather = data['weather']
        wind_speed = weather['wind']['speed']  # km/h
        wind_direction = weather['wind']['deg']  # degrees
        temperature = weather['main']['temp']
        humidity = weather['main']['humidity']
        
        current_boundary = disaster['data'].get('fire_perimeter')
        
        # Simplified fire spread rate calculation
        # Real models use Rothermel equations, but this is hackathon-friendly
        base_spread_rate = 2.0  # km/hour base rate
        
        # Wind factor (0.5x to 3x multiplier)
        wind_factor = 1 + (wind_speed / 50)
        
        # Temperature factor
        temp_factor = 1 + ((temperature - 20) / 40)
        
        # Humidity factor (inverse)
        humidity_factor = 1.5 - (humidity / 100)
        
        spread_rate = base_spread_rate * wind_factor * temp_factor * humidity_factor
        
        # Project forward 1, 3, 6 hours
        predictions = {}
        for hours in [1, 3, 6]:
            spread_distance_km = spread_rate * hours
            
            # Expand fire perimeter by spread distance in wind direction
            # Simplified: Just expand radius
            predictions[f'hour_{hours}'] = {
                'boundary': self._expand_polygon(current_boundary, spread_distance_km),
                'area_km2': self._calculate_area(current_boundary, spread_distance_km),
                'confidence': 0.75 - (hours * 0.05)  # Confidence decreases with time
            }
        
        # Key prediction: When will fire reach specific locations?
        critical_points = self._identify_critical_points(disaster['location'])
        arrival_times = self._calculate_arrival_times(
            current_boundary, 
            critical_points, 
            spread_rate, 
            wind_direction
        )
        
        return {
            'current_spread_rate_kmh': spread_rate,
            'predictions': predictions,
            'critical_arrival_times': arrival_times,
            'factors': {
                'wind_speed_kmh': wind_speed,
                'wind_direction_deg': wind_direction,
                'temperature_c': temperature,
                'humidity_percent': humidity
            }
        }
    
    def _identify_critical_points(self, location: Dict) -> List[Dict]:
        """Identify critical infrastructure or population centers"""
        return [
            {'name': 'Residential Area A', 'lat': 43.735, 'lon': -79.860},
            {'name': 'Highway 410', 'lat': 43.740, 'lon': -79.855},
            {'name': 'Main Street Commercial', 'lat': 43.745, 'lon': -79.850}
        ]
    
    def _calculate_arrival_times(self, boundary, points: List, spread_rate: float, wind_dir: float) -> List[Dict]:
        """Calculate when fire will reach each critical point"""
        results = []
        for point in points:
            # Calculate distance from boundary to point
            distance_km = self._distance_to_boundary(boundary, point)
            
            # Adjust for wind direction (fire spreads faster downwind)
            directional_factor = self._calculate_directional_factor(
                boundary, point, wind_dir
            )
            
            effective_spread_rate = spread_rate * directional_factor
            hours_until_arrival = distance_km / effective_spread_rate
            
            results.append({
                'location': point['name'],
                'hours_until_arrival': round(hours_until_arrival, 1),
                'confidence': 'high' if hours_until_arrival < 6 else 'medium'
            })
        
        return sorted(results, key=lambda x: x['hours_until_arrival'])
```

---

## 📦 Data Client Implementations

### Satellite Data Client (`data/satellite_client.py`)

```python
import requests
from typing import Dict
import os

class SatelliteClient:
    def __init__(self):
        self.firms_api_key = os.getenv('NASA_FIRMS_API_KEY')
        self.firms_url = "https://firms.modaps.eosdis.nasa.gov/api/area"
    
    async def fetch_imagery(self, location: Dict) -> Dict:
        """
        Fetch satellite imagery and fire detection data
        """
        # For fires: Use NASA FIRMS active fire data
        fires = await self._fetch_active_fires(location)
        
        # For satellite imagery: Use NOAA GOES or similar
        # For demo: Can use pre-downloaded images
        
        return {
            'fire_detections': fires,
            'fire_perimeter': self._calculate_fire_perimeter(fires),
            'thermal_intensity': fires[0]['bright_ti4'] if fires else 300,
            'satellite': 'VIIRS',
            'timestamp': fires[0]['acq_date'] if fires else None
        }
    
    async def _fetch_active_fires(self, location: Dict) -> List[Dict]:
        """Query NASA FIRMS for active fires"""
        # FIRMS API format: /area/csv/{api_key}/VIIRS_SNPP_NRT/{bbox}/{days}
        bbox = self._create_bbox(location, radius_km=20)
        url = f"{self.firms_url}/csv/{self.firms_api_key}/VIIRS_SNPP_NRT/{bbox}/1"
        
        response = requests.get(url)
        if response.status_code == 200:
            # Parse CSV
            fires = self._parse_firms_csv(response.text)
            return fires
        else:
            return []
    
    def _create_bbox(self, location: Dict, radius_km: float) -> str:
        """Create bounding box around location"""
        lat = location['lat']
        lon = location['lon']
        # Rough conversion: 1 degree ≈ 111 km
        delta = radius_km / 111
        
        west = lon - delta
        south = lat - delta
        east = lon + delta
        north = lat + delta
        
        return f"{west},{south},{east},{north}"
```

### Weather Client (`data/weather_client.py`)

```python
import requests
import os
from typing import Dict

class WeatherClient:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def fetch_current(self, location: Dict) -> Dict:
        """Fetch current weather conditions"""
        url = f"{self.base_url}/weather"
        params = {
            'lat': location['lat'],
            'lon': location['lon'],
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Weather API error: {response.status_code}")
    
    async def fetch_forecast(self, location: Dict) -> Dict:
        """Fetch weather forecast (next 6 hours)"""
        url = f"{self.base_url}/forecast"
        params = {
            'lat': location['lat'],
            'lon': location['lon'],
            'appid': self.api_key,
            'units': 'metric',
            'cnt': 2  # Next 6 hours (3-hour intervals)
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {}
```

---

## 🔧 Configuration (`utils/config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    NASA_FIRMS_API_KEY = os.getenv('NASA_FIRMS_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')
    
    # Server
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Update intervals
    UPDATE_INTERVAL_SECONDS = 900  # 15 minutes
    
    # Brampton coordinates
    BRAMPTON_CENTER = {'lat': 43.7315, 'lon': -79.7624}
    BRAMPTON_BBOX = {
        'north': 43.83,
        'south': 43.63,
        'east': -79.63,
        'west': -79.90
    }

config = Config()
```

---

## 🚀 Running the Backend

```bash
# Install dependencies
pip install flask flask-socketio flask-cors anthropic requests geopandas shapely pyproj python-dotenv

# Set environment variables
export NASA_FIRMS_API_KEY="your-key"
export OPENWEATHER_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Run server
python app.py
```

Server will start on `http://localhost:5000`

---

## 🧪 Testing Endpoints

```bash
# Trigger a disaster
curl -X POST http://localhost:5000/api/disaster/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "type": "wildfire",
    "location": {"lat": 43.7315, "lon": -79.8620},
    "severity": "high"
  }'

# Get disaster status
curl http://localhost:5000/api/disaster/wildfire-20251106-142300

# Get generated plan
curl http://localhost:5000/api/disaster/wildfire-20251106-142300/plan
```

---

## 📝 Next Steps

See the frontend architecture document for how to build the React dashboard that consumes this API.
