import asyncio
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from data.satellite_client import SatelliteClient
from data.weather_client import WeatherClient
from data.geohub_client import GeoHubClient
from agents.damage_assessment import DamageAssessmentAgent
from agents.population_impact import PopulationImpactAgent
from agents.routing import RoutingAgent
from agents.resource_allocation import ResourceAllocationAgent
from agents.prediction import PredictionAgent


class DisasterOrchestrator:
    """
    Orchestrates disaster response by coordinating data collection and agent analysis.
    Uses asyncio to run tasks in parallel for optimal performance.
    """
    
    def __init__(self, socketio=None):
        """
        Initialize the orchestrator with data clients and agents.
        
        Args:
            socketio: Flask-SocketIO instance for real-time progress updates
        """
        self.socketio = socketio
        
        # Initialize data clients
        self.data_clients = {
            'satellite': SatelliteClient(),
            'weather': WeatherClient(),
            'geohub': GeoHubClient()
        }
        
        # Initialize agents
        self.agents = {
            'damage': DamageAssessmentAgent(),
            'population': PopulationImpactAgent(),
            'routing': RoutingAgent(),
            'resource': ResourceAllocationAgent(),
            'prediction': PredictionAgent()
        }
        
        # Track active disasters
        self.active_disasters: Dict[str, Dict[str, Any]] = {}
    
    def create_disaster(self, disaster_id: str, disaster_data: Dict) -> Dict:
        """
        Create a new disaster entry.
        
        Args:
            disaster_id: Unique identifier for the disaster
            disaster_data: Dictionary containing disaster details (type, location, etc.)
        
        Returns:
            The created disaster dictionary
        """
        self.active_disasters[disaster_id] = {
            'id': disaster_id,
            'type': disaster_data.get('type', 'wildfire'),
            'location': disaster_data.get('location'),
            'status': 'initialized',
            'created_at': datetime.now().isoformat(),
            'data': {},
            'agent_results': {},
            'plan': None,
            'error': None
        }
        return self.active_disasters[disaster_id]
    
    async def process_disaster(self, disaster_id: str):
        """Main processing pipeline"""
        disaster = self.active_disasters[disaster_id]
        
        try:
            # PHASE 1: Data Ingestion (5 seconds)
            disaster['status'] = 'fetching_data'
            if self.socketio:
                self.socketio.emit('progress', {
                    'disaster_id': disaster_id, 'phase': 'data_ingestion', 'progress': 10
                }, room=disaster_id)
            
            data = await self._fetch_all_data(disaster)
            disaster['data'] = data
            
            # PHASE 2: Agent Processing (25 seconds)
            disaster['status'] = 'analyzing'
            if self.socketio:
                self.socketio.emit('progress', {
                    'disaster_id': disaster_id, 'phase': 'agent_processing', 'progress': 30
                }, room=disaster_id)
            
            agent_results = await self._run_all_agents(disaster, data)
            disaster['agent_results'] = agent_results
            
            # PHASE 3: Synthesis (20 seconds) - (Stubbed for now)
            disaster['status'] = 'generating_plan'
            if self.socketio:
                self.socketio.emit('progress', {
                    'disaster_id': disaster_id, 'phase': 'synthesis', 'progress': 70
                }, room=disaster_id)
            
            # This 'plan' will be replaced by the LLM call in the next epic
            plan = {"executive_summary": "Plan synthesis pending...", **agent_results}
            disaster['plan'] = plan
            
            # --- HACKATHON: Mark as complete after agents ---
            disaster['status'] = 'complete'
            if self.socketio:
                self.socketio.emit('disaster_complete', {
                    'disaster_id': disaster_id,
                    'plan': plan
                }, room=disaster_id)
            
        except Exception as e:
            disaster['status'] = 'error'
            disaster['error'] = str(e)
            if self.socketio:
                self.socketio.emit('disaster_error', {
                    'disaster_id': disaster_id,
                    'error': str(e)
                }, room=disaster_id)
            print(f"Error processing {disaster_id}: {e}")

    async def _fetch_all_data(self, disaster: Dict) -> Dict:
        """Fetch data from all sources in parallel"""
        location = disaster['location']
        
        # Parallel API calls
        tasks = {
            'satellite': self.data_clients['satellite'].fetch_imagery(location),
            'weather': self.data_clients['weather'].fetch_current(location),
            'geohub_pop': self.data_clients['geohub'].fetch_population(location),
            'geohub_infra': self.data_clients['geohub'].fetch_infrastructure(location)
        }
        
        results = await asyncio.gather(*tasks.values())
        
        return dict(zip(tasks.keys(), results))
    
    async def _run_all_agents(self, disaster: Dict, data: Dict) -> Dict:
        """Run all agents in parallel"""
        location = disaster['location']
        
        # Agents can run in parallel.
        # We must get the damage assessment *first* to pass its boundary to other agents.
        
        # 1. Run Damage Assessment first
        damage_result = await self.agents['damage'].analyze(
            data['satellite'], 
            disaster['type']
        )
        affected_boundary_geojson = damage_result.get('fire_perimeter')
        affected_boundary_geom = None
        if affected_boundary_geojson:
            from shapely.geometry import shape
            affected_boundary_geom = shape(affected_boundary_geojson)
        
        # 2. Run remaining agents in parallel
        tasks = {
            'population': self.agents['population'].analyze(
                affected_boundary_geojson, 
                data['geohub_pop']
            ),
            'routing': self.agents['routing'].analyze(
                location, 
                None,  # 'roads' data stubbed
                affected_boundary_geom
            ),
            'resource': self.agents['resource'].analyze(
                {},  # 'population_impact' - will be added post-gather
                data['geohub_infra']
            ),
            'prediction': self.agents['prediction'].analyze(
                disaster, 
                {'weather': data['weather'], 'fire_perimeter': affected_boundary_geojson}
            )
        }
        
        results = await asyncio.gather(*tasks.values())
        agent_outputs = dict(zip(tasks.keys(), results))
        
        # 3. Add dependencies
        # ResourceAgent needs population output
        agent_outputs['resource'] = await self.agents['resource'].analyze(
            agent_outputs['population'],
            data['geohub_infra']
        )
        
        # 4. Combine all results
        agent_outputs['damage'] = damage_result
        return agent_outputs
    
    def get_disaster_status(self, disaster_id: str) -> Dict:
        """Get the current status of a disaster"""
        return self.active_disasters.get(disaster_id, {})
    
    def list_active_disasters(self) -> Dict[str, Dict]:
        """List all active disasters"""
        return self.active_disasters