"""
Comprehensive tests for RoutingAgent
"""
import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from shapely.geometry import Polygon

# Add backend to the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.routing import RoutingAgent


def create_test_polygon():
    """Create a test polygon for danger zone"""
    return Polygon([
        (-79.8650, 43.7320),
        (-79.8550, 43.7320),
        (-79.8550, 43.7380),
        (-79.8650, 43.7380),
        (-79.8650, 43.7320)
    ])


@pytest.mark.asyncio
async def test_routing_agent_initialization():
    """Test RoutingAgent initialization"""
    agent = RoutingAgent()
    
    assert agent.name == "RoutingAgent"
    assert agent.osrm_url == "http://router.project-osrm.org"
    print("✓ RoutingAgent initialized correctly")


@pytest.mark.asyncio
async def test_identify_safe_zones():
    """Test safe zone identification"""
    agent = RoutingAgent()
    location = {"lat": 43.7315, "lon": -79.8600}
    danger_zone = create_test_polygon()
    
    safe_zones = agent._identify_safe_zones(location, danger_zone)
    
    assert len(safe_zones) == 2
    assert safe_zones[0]['name'] == 'Brampton Soccer Centre'
    assert safe_zones[1]['name'] == 'CAA Centre'
    assert safe_zones[0]['capacity'] == 2000
    assert safe_zones[1]['capacity'] == 5000
    assert 'lat' in safe_zones[0]
    assert 'lon' in safe_zones[0]
    
    print("✓ Safe zones identified correctly")


@pytest.mark.asyncio
async def test_get_evacuation_origins():
    """Test evacuation origin extraction from danger zone"""
    agent = RoutingAgent()
    danger_zone = create_test_polygon()
    
    origins = agent._get_evacuation_origins(danger_zone)
    
    assert len(origins) == 1
    assert origins[0]['name'] == 'Affected Area Centroid'
    assert 'lat' in origins[0]
    assert 'lon' in origins[0]
    # Verify centroid is approximately correct
    assert 43.730 < origins[0]['lat'] < 43.740
    assert -79.870 < origins[0]['lon'] < -79.850
    
    print("✓ Evacuation origins extracted correctly")


@pytest.mark.asyncio
async def test_get_evacuation_origins_none():
    """Test handling of None danger zone"""
    agent = RoutingAgent()
    
    origins = agent._get_evacuation_origins(None)
    
    assert origins == []
    print("✓ None danger zone handled gracefully")


@pytest.mark.asyncio
async def test_estimate_evacuation_time():
    """Test evacuation time estimation"""
    agent = RoutingAgent()
    
    routes = [
        {'time_minutes': 15.5},
        {'time_minutes': 22.3},
        {'time_minutes': 18.7}
    ]
    
    evac_time = agent._estimate_evacuation_time(routes)
    
    assert evac_time == 22.3  # Maximum time
    print("✓ Evacuation time estimated correctly")


@pytest.mark.asyncio
async def test_estimate_evacuation_time_empty():
    """Test evacuation time estimation with empty routes"""
    agent = RoutingAgent()
    
    evac_time = agent._estimate_evacuation_time([])
    
    assert evac_time == 0.0
    print("✓ Empty routes handled correctly")


@pytest.mark.asyncio
async def test_calculate_best_route_success():
    """Test route calculation with successful OSRM response"""
    agent = RoutingAgent()
    
    origin = {'name': 'Test Origin', 'lat': 43.7320, 'lon': -79.8600}
    safe_zones = [
        {'name': 'Zone 1', 'lat': 43.7150, 'lon': -79.8400, 'capacity': 2000},
        {'name': 'Zone 2', 'lat': 43.7300, 'lon': -79.7500, 'capacity': 5000}
    ]
    
    # Mock OSRM response
    mock_response_data = {
        'routes': [{
            'geometry': {
                'type': 'LineString',
                'coordinates': [[-79.8600, 43.7320], [-79.8400, 43.7150]]
            },
            'distance': 5000,  # meters
            'duration': 600    # seconds
        }]
    }
    
    # Mock aiohttp session and response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_response_data)
    
    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_response)
    mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
    
    route = await agent._calculate_best_route(mock_session, origin, safe_zones)
    
    assert route is not None
    assert route['origin'] == origin
    assert 'destination' in route
    assert 'path' in route
    assert 'distance_km' in route
    assert 'time_minutes' in route
    assert route['distance_km'] == 5.0
    assert route['time_minutes'] == 10.0
    
    print("✓ Best route calculated successfully")


@pytest.mark.asyncio
async def test_calculate_best_route_api_error():
    """Test route calculation with OSRM API error"""
    agent = RoutingAgent()
    
    origin = {'name': 'Test Origin', 'lat': 43.7320, 'lon': -79.8600}
    safe_zones = [
        {'name': 'Zone 1', 'lat': 43.7150, 'lon': -79.8400, 'capacity': 2000}
    ]
    
    # Mock failed response
    mock_response = AsyncMock()
    mock_response.status = 500
    
    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_response)
    mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
    
    route = await agent._calculate_best_route(mock_session, origin, safe_zones)
    
    assert route is None
    print("✓ API error handled gracefully")


@pytest.mark.asyncio
async def test_calculate_best_route_exception():
    """Test route calculation with exception"""
    agent = RoutingAgent()
    
    origin = {'name': 'Test Origin', 'lat': 43.7320, 'lon': -79.8600}
    safe_zones = [
        {'name': 'Zone 1', 'lat': 43.7150, 'lon': -79.8400, 'capacity': 2000}
    ]
    
    # Mock session that raises exception
    mock_session = AsyncMock()
    mock_session.get.side_effect = Exception("Network error")
    
    route = await agent._calculate_best_route(mock_session, origin, safe_zones)
    
    assert route is None
    print("✓ Exception handled gracefully")


@pytest.mark.asyncio
async def test_analyze_full_flow():
    """Test full analyze flow with mocked OSRM responses"""
    agent = RoutingAgent()
    
    location = {"lat": 43.7315, "lon": -79.8600}
    roads = {}  # Not used in current implementation
    danger_zone = create_test_polygon()
    
    # Mock OSRM response
    mock_route_data = {
        'routes': [{
            'geometry': {
                'type': 'LineString',
                'coordinates': [[-79.8600, 43.7350], [-79.8400, 43.7150]]
            },
            'distance': 3500,
            'duration': 480
        }]
    }
    
    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_route_data)
        
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await agent.analyze(location, roads, danger_zone)
        
        # Verify result structure
        assert 'routes' in result
        assert 'safe_zones' in result
        assert 'estimated_evacuation_time_minutes' in result
        assert 'primary_route' in result
        assert 'alternate_routes' in result
        
        # Verify safe zones
        assert len(result['safe_zones']) == 2
        
        # Verify routes
        assert isinstance(result['routes'], list)
        
        # Verify evacuation time
        assert isinstance(result['estimated_evacuation_time_minutes'], (int, float))
        
        print("✓ Full analyze flow completed successfully")


@pytest.mark.asyncio
async def test_analyze_no_routes_found():
    """Test analyze when no routes can be calculated"""
    agent = RoutingAgent()
    
    location = {"lat": 43.7315, "lon": -79.8600}
    roads = {}
    danger_zone = create_test_polygon()
    
    with patch('aiohttp.ClientSession') as mock_session_class:
        # Mock failed response
        mock_response = AsyncMock()
        mock_response.status = 500
        
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await agent.analyze(location, roads, danger_zone)
        
        assert result['routes'] == []
        assert result['estimated_evacuation_time_minutes'] == 0.0
        assert result['primary_route'] is None
        assert result['alternate_routes'] == []
        
        print("✓ No routes scenario handled correctly")


@pytest.mark.asyncio
async def test_best_route_selection():
    """Test that the shortest route is selected"""
    agent = RoutingAgent()
    
    origin = {'name': 'Test Origin', 'lat': 43.7320, 'lon': -79.8600}
    safe_zones = [
        {'name': 'Far Zone', 'lat': 43.6000, 'lon': -79.9000, 'capacity': 1000},
        {'name': 'Near Zone', 'lat': 43.7300, 'lon': -79.8500, 'capacity': 2000}
    ]
    
    # Mock different response times for each zone
    call_count = 0
    
    async def mock_json():
        nonlocal call_count
        call_count += 1
        if call_count == 1:  # Far zone - longer route
            return {
                'routes': [{
                    'geometry': {'type': 'LineString', 'coordinates': []},
                    'distance': 10000,
                    'duration': 1200
                }]
            }
        else:  # Near zone - shorter route
            return {
                'routes': [{
                    'geometry': {'type': 'LineString', 'coordinates': []},
                    'distance': 2000,
                    'duration': 300
                }]
            }
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = mock_json
    
    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_response)
    mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
    
    route = await agent._calculate_best_route(mock_session, origin, safe_zones)
    
    # Should select the shorter route
    assert route['destination']['name'] == 'Near Zone'
    assert route['time_minutes'] == 5.0  # 300 seconds / 60
    
    print("✓ Best route selection works correctly")


@pytest.mark.asyncio
async def test_multiple_routes():
    """Test that multiple routes are returned for multiple origins"""
    agent = RoutingAgent()
    
    # This test would require multiple origins, which isn't currently
    # supported by the implementation (only returns centroid)
    # But we can test the structure
    
    location = {"lat": 43.7315, "lon": -79.8600}
    roads = {}
    danger_zone = create_test_polygon()
    
    mock_route_data = {
        'routes': [{
            'geometry': {
                'type': 'LineString',
                'coordinates': [[-79.8600, 43.7350], [-79.8400, 43.7150]]
            },
            'distance': 3500,
            'duration': 480
        }]
    }
    
    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_route_data)
        
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        result = await agent.analyze(location, roads, danger_zone)
        
        # Verify primary and alternate routes structure
        if result['routes']:
            assert result['primary_route'] == result['routes'][0]
            if len(result['routes']) > 1:
                assert result['alternate_routes'] == result['routes'][1:]
            else:
                assert result['alternate_routes'] == []
        
        print("✓ Multiple routes structure verified")


# Direct execution
if __name__ == "__main__":
    async def run_tests():
        print("=" * 60)
        print("Running RoutingAgent Tests")
        print("=" * 60)
        print()
        
        await test_routing_agent_initialization()
        await test_identify_safe_zones()
        await test_get_evacuation_origins()
        await test_get_evacuation_origins_none()
        await test_estimate_evacuation_time()
        await test_estimate_evacuation_time_empty()
        await test_calculate_best_route_success()
        await test_calculate_best_route_api_error()
        await test_calculate_best_route_exception()
        await test_analyze_full_flow()
        await test_analyze_no_routes_found()
        await test_best_route_selection()
        await test_multiple_routes()
        
        print()
        print("=" * 60)
        print("✅ All RoutingAgent tests passed!")
        print("=" * 60)
    
    asyncio.run(run_tests())