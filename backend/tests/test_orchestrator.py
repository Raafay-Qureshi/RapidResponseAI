import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import Mock, AsyncMock, patch, MagicMock
from orchestrator import DisasterOrchestrator
import geopandas as gpd
from shapely.geometry import Point, Polygon


@pytest.fixture
def mock_socketio():
    """Create a mock SocketIO instance"""
    socketio = Mock()
    socketio.emit = Mock()
    return socketio


@pytest.fixture
def orchestrator(mock_socketio):
    """Create an orchestrator instance with mocked dependencies"""
    return DisasterOrchestrator(socketio=mock_socketio)


@pytest.fixture
def sample_disaster_data():
    """Sample disaster data for testing"""
    return {
        'type': 'wildfire',
        'location': {'lat': 43.7315, 'lon': -79.7624}
    }


@pytest.fixture
def mock_satellite_data():
    """Mock satellite imagery data"""
    return {
        'fire_detections': [
            {'latitude': 43.73, 'longitude': -79.76, 'bright_ti4': 380}
        ],
        'fire_perimeter': {
            'type': 'Polygon',
            'coordinates': [[
                [-79.77, 43.72],
                [-79.75, 43.72],
                [-79.75, 43.74],
                [-79.77, 43.74],
                [-79.77, 43.72]
            ]]
        },
        'thermal_intensity': 380,
        'satellite': 'VIIRS',
        'timestamp': '2025-11-08'
    }


@pytest.fixture
def mock_weather_data():
    """Mock weather data"""
    return {
        'main': {'temp': 25, 'humidity': 30},
        'wind': {'speed': 15, 'deg': 180},
        'weather': [{'description': 'clear sky'}]
    }


@pytest.fixture
def mock_population_gdf():
    """Mock GeoDataFrame for population data"""
    data = {
        'tract_id': ['BT001', 'BT002'],
        'population': [8500, 12000],
        'vulnerable_pop': [850, 1440],
        'age_65_plus': [500, 700],
        'age_under_18': [1500, 2000]
    }
    geometries = [
        Polygon([
            (-79.77, 43.72),
            (-79.75, 43.72),
            (-79.75, 43.74),
            (-79.77, 43.74),
            (-79.77, 43.72)
        ]),
        Polygon([
            (-79.76, 43.73),
            (-79.74, 43.73),
            (-79.74, 43.75),
            (-79.76, 43.75),
            (-79.76, 43.73)
        ])
    ]
    return gpd.GeoDataFrame(data, geometry=geometries, crs='EPSG:4326')


@pytest.fixture
def mock_infrastructure_gdf():
    """Mock GeoDataFrame for infrastructure data"""
    data = {
        'name': ['Hospital A', 'Fire Station B'],
        'type': ['hospital', 'fire_station'],
        'capacity': [500, 50]
    }
    geometries = [
        Point(-79.76, 43.73),
        Point(-79.75, 43.72)
    ]
    return gpd.GeoDataFrame(data, geometry=geometries, crs='EPSG:4326')


class TestDisasterOrchestrator:
    """Test suite for DisasterOrchestrator"""
    
    def test_initialization(self, mock_socketio):
        """Test orchestrator initialization"""
        orchestrator = DisasterOrchestrator(socketio=mock_socketio)
        
        assert orchestrator.socketio == mock_socketio
        assert 'satellite' in orchestrator.data_clients
        assert 'weather' in orchestrator.data_clients
        assert 'geohub' in orchestrator.data_clients
        assert 'damage' in orchestrator.agents
        assert 'population' in orchestrator.agents
        assert 'routing' in orchestrator.agents
        assert 'resource' in orchestrator.agents
        assert 'prediction' in orchestrator.agents
        assert orchestrator.active_disasters == {}
    
    def test_create_disaster(self, orchestrator, sample_disaster_data):
        """Test disaster creation"""
        disaster_id = 'test-disaster-001'
        disaster = orchestrator.create_disaster(disaster_id, sample_disaster_data)
        
        assert disaster['id'] == disaster_id
        assert disaster['type'] == 'wildfire'
        assert disaster['location'] == sample_disaster_data['location']
        assert disaster['status'] == 'initialized'
        assert disaster['data'] == {}
        assert disaster['agent_results'] == {}
        assert disaster['plan'] is None
        assert disaster['error'] is None
        assert disaster_id in orchestrator.active_disasters
    
    def test_get_disaster_status(self, orchestrator, sample_disaster_data):
        """Test getting disaster status"""
        disaster_id = 'test-disaster-002'
        orchestrator.create_disaster(disaster_id, sample_disaster_data)
        
        status = orchestrator.get_disaster_status(disaster_id)
        assert status['id'] == disaster_id
        assert status['status'] == 'initialized'
        
        # Test non-existent disaster
        status = orchestrator.get_disaster_status('non-existent')
        assert status == {}
    
    def test_list_active_disasters(self, orchestrator, sample_disaster_data):
        """Test listing active disasters"""
        orchestrator.create_disaster('disaster-1', sample_disaster_data)
        orchestrator.create_disaster('disaster-2', sample_disaster_data)
        
        disasters = orchestrator.list_active_disasters()
        assert len(disasters) == 2
        assert 'disaster-1' in disasters
        assert 'disaster-2' in disasters
    
    @pytest.mark.asyncio
    async def test_fetch_all_data(
        self,
        orchestrator,
        sample_disaster_data,
        mock_satellite_data,
        mock_weather_data,
        mock_population_gdf,
        mock_infrastructure_gdf
    ):
        """Test parallel data fetching"""
        disaster_id = 'test-disaster-003'
        disaster = orchestrator.create_disaster(disaster_id, sample_disaster_data)
        
        # Mock the data client methods
        orchestrator.data_clients['satellite'].fetch_imagery = AsyncMock(
            return_value=mock_satellite_data
        )
        orchestrator.data_clients['weather'].fetch_current = AsyncMock(
            return_value=mock_weather_data
        )
        orchestrator.data_clients['geohub'].fetch_population = AsyncMock(
            return_value=mock_population_gdf
        )
        orchestrator.data_clients['geohub'].fetch_infrastructure = AsyncMock(
            return_value=mock_infrastructure_gdf
        )
        
        # Fetch data
        data = await orchestrator._fetch_all_data(disaster)
        
        # Verify all data was fetched
        assert 'satellite' in data
        assert 'weather' in data
        assert 'geohub_pop' in data
        assert 'geohub_infra' in data
        
        assert data['satellite'] == mock_satellite_data
        assert data['weather'] == mock_weather_data
        assert isinstance(data['geohub_pop'], gpd.GeoDataFrame)
        assert isinstance(data['geohub_infra'], gpd.GeoDataFrame)
        
        # Verify all methods were called
        orchestrator.data_clients['satellite'].fetch_imagery.assert_called_once()
        orchestrator.data_clients['weather'].fetch_current.assert_called_once()
        orchestrator.data_clients['geohub'].fetch_population.assert_called_once()
        orchestrator.data_clients['geohub'].fetch_infrastructure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_all_agents(
        self,
        orchestrator,
        sample_disaster_data,
        mock_satellite_data,
        mock_weather_data,
        mock_population_gdf,
        mock_infrastructure_gdf
    ):
        """Test parallel agent execution"""
        disaster_id = 'test-disaster-004'
        disaster = orchestrator.create_disaster(disaster_id, sample_disaster_data)
        
        # Prepare mock data
        data = {
            'satellite': mock_satellite_data,
            'weather': mock_weather_data,
            'geohub_pop': mock_population_gdf,
            'geohub_infra': mock_infrastructure_gdf
        }
        
        # Mock agent analyze methods
        mock_damage_result = {
            'affected_area_km2': 5.2,
            'fire_perimeter': mock_satellite_data['fire_perimeter'],
            'severity': 'high',
            'confidence': 0.92
        }
        
        mock_population_result = {
            'total_affected': 15000,
            'vulnerable_population': {'elderly': 1200, 'children': 3500}
        }
        
        mock_routing_result = {
            'routes': [],
            'safe_zones': [{'name': 'Zone A', 'capacity': 2000}],
            'estimated_evacuation_time_minutes': 45
        }
        
        mock_resource_result = {
            'required_resources': {
                'ambulances': 15,
                'evacuation_buses': 60,
                'personnel': 75
            }
        }
        
        mock_prediction_result = {
            'current_spread_rate_kmh': 2.5,
            'predictions': [],
            'critical_arrival_times': []
        }
        
        orchestrator.agents['damage'].analyze = AsyncMock(return_value=mock_damage_result)
        orchestrator.agents['population'].analyze = AsyncMock(return_value=mock_population_result)
        orchestrator.agents['routing'].analyze = AsyncMock(return_value=mock_routing_result)
        orchestrator.agents['resource'].analyze = AsyncMock(return_value=mock_resource_result)
        orchestrator.agents['prediction'].analyze = AsyncMock(return_value=mock_prediction_result)
        
        # Run agents
        results = await orchestrator._run_all_agents(disaster, data)
        
        # Verify all agents were called
        assert 'damage' in results
        assert 'population' in results
        assert 'routing' in results
        assert 'resource' in results
        assert 'prediction' in results
        
        # Verify damage agent was called first
        orchestrator.agents['damage'].analyze.assert_called_once()
        
        # Verify other agents were called
        orchestrator.agents['population'].analyze.assert_called_once()
        orchestrator.agents['routing'].analyze.assert_called_once()
        orchestrator.agents['prediction'].analyze.assert_called_once()
        
        # Verify resource agent was called twice (once in parallel, once with dependency)
        assert orchestrator.agents['resource'].analyze.call_count == 2
    
    @pytest.mark.asyncio
    async def test_process_disaster_success(
        self,
        orchestrator,
        mock_socketio,
        sample_disaster_data,
        mock_satellite_data,
        mock_weather_data,
        mock_population_gdf,
        mock_infrastructure_gdf
    ):
        """Test complete disaster processing pipeline"""
        disaster_id = 'test-disaster-005'
        orchestrator.create_disaster(disaster_id, sample_disaster_data)
        
        # Mock data clients
        orchestrator.data_clients['satellite'].fetch_imagery = AsyncMock(
            return_value=mock_satellite_data
        )
        orchestrator.data_clients['weather'].fetch_current = AsyncMock(
            return_value=mock_weather_data
        )
        orchestrator.data_clients['geohub'].fetch_population = AsyncMock(
            return_value=mock_population_gdf
        )
        orchestrator.data_clients['geohub'].fetch_infrastructure = AsyncMock(
            return_value=mock_infrastructure_gdf
        )
        
        # Mock agents
        orchestrator.agents['damage'].analyze = AsyncMock(return_value={
            'affected_area_km2': 5.2,
            'fire_perimeter': mock_satellite_data['fire_perimeter'],
            'severity': 'high'
        })
        orchestrator.agents['population'].analyze = AsyncMock(return_value={
            'total_affected': 15000
        })
        orchestrator.agents['routing'].analyze = AsyncMock(return_value={
            'routes': []
        })
        orchestrator.agents['resource'].analyze = AsyncMock(return_value={
            'required_resources': {}
        })
        orchestrator.agents['prediction'].analyze = AsyncMock(return_value={
            'current_spread_rate_kmh': 2.5
        })
        
        # Process disaster
        await orchestrator.process_disaster(disaster_id)
        
        # Verify disaster status
        disaster = orchestrator.get_disaster_status(disaster_id)
        assert disaster['status'] == 'complete'
        assert 'data' in disaster
        assert 'agent_results' in disaster
        assert disaster['plan'] is not None
        assert disaster['error'] is None
        
        # Verify socketio emissions
        assert mock_socketio.emit.call_count >= 3
        
        # Check for progress emissions
        calls = [call[0] for call in mock_socketio.emit.call_args_list]
        assert any('progress' in call for call in calls)
        assert any('disaster_complete' in call for call in calls)
    
    @pytest.mark.asyncio
    async def test_process_disaster_error_handling(
        self,
        orchestrator,
        mock_socketio,
        sample_disaster_data
    ):
        """Test error handling in disaster processing"""
        disaster_id = 'test-disaster-006'
        orchestrator.create_disaster(disaster_id, sample_disaster_data)
        
        # Mock data client to raise an exception
        orchestrator.data_clients['satellite'].fetch_imagery = AsyncMock(
            side_effect=Exception("API connection failed")
        )
        
        # Process disaster
        await orchestrator.process_disaster(disaster_id)
        
        # Verify disaster status shows error
        disaster = orchestrator.get_disaster_status(disaster_id)
        assert disaster['status'] == 'error'
        assert disaster['error'] is not None
        assert 'API connection failed' in disaster['error']
        
        # Verify error emission
        calls = [call[0] for call in mock_socketio.emit.call_args_list]
        assert any('disaster_error' in call for call in calls)
    
    @pytest.mark.asyncio
    async def test_parallel_execution_performance(
        self,
        orchestrator,
        sample_disaster_data,
        mock_satellite_data,
        mock_weather_data,
        mock_population_gdf,
        mock_infrastructure_gdf
    ):
        """Test that parallel execution is actually happening"""
        disaster_id = 'test-disaster-007'
        disaster = orchestrator.create_disaster(disaster_id, sample_disaster_data)
        
        # Create async mocks that track call times
        call_times = []
        
        async def mock_fetch_with_delay(name, delay=0.1):
            start = asyncio.get_event_loop().time()
            await asyncio.sleep(delay)
            call_times.append((name, start, asyncio.get_event_loop().time()))
            return {}
        
        # Mock data clients with delays
        orchestrator.data_clients['satellite'].fetch_imagery = AsyncMock(
            side_effect=lambda loc: mock_fetch_with_delay('satellite', 0.1)
        )
        orchestrator.data_clients['weather'].fetch_current = AsyncMock(
            side_effect=lambda loc: mock_fetch_with_delay('weather', 0.1)
        )
        orchestrator.data_clients['geohub'].fetch_population = AsyncMock(
            side_effect=lambda loc: mock_fetch_with_delay('population', 0.1)
        )
        orchestrator.data_clients['geohub'].fetch_infrastructure = AsyncMock(
            side_effect=lambda loc: mock_fetch_with_delay('infrastructure', 0.1)
        )
        
        # Fetch data
        start_time = asyncio.get_event_loop().time()
        await orchestrator._fetch_all_data(disaster)
        total_time = asyncio.get_event_loop().time() - start_time
        
        # If sequential, would take ~0.4s. If parallel, should take ~0.1s
        # Allow some overhead
        assert total_time < 0.25, "Data fetching should be parallel"
        
        # Verify all tasks started around the same time (within 0.05s)
        if len(call_times) >= 2:
            start_times = [t[1] for t in call_times]
            assert max(start_times) - min(start_times) < 0.05


if __name__ == '__main__':
    pytest.main([__file__, '-v'])