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


def create_damage_summary():
    """Create a test damage summary dictionary"""
    return {
        "severity": "high",
        "affected_area_km2": 0.5,
        "fire_perimeter": {
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-79.8650, 43.7320],
                    [-79.8550, 43.7320],
                    [-79.8550, 43.7380],
                    [-79.8650, 43.7380],
                    [-79.8650, 43.7320]
                ]]
            }
        }
    }


@pytest.mark.asyncio
async def test_routing_agent_initialization():
    """Test RoutingAgent initialization"""
    agent = RoutingAgent()
    
    assert agent.name == "RoutingAgent"
    print("✓ RoutingAgent initialized correctly")


@pytest.mark.asyncio
async def test_analyze_basic_flow():
    """Test basic analyze flow with valid inputs"""
    agent = RoutingAgent()
    
    roads_data = None
    infrastructure_data = None
    damage_summary = create_damage_summary()
    
    result = await agent.analyze(roads_data, infrastructure_data, damage_summary)
    
    # Verify result structure
    assert 'routes' in result
    assert 'severity' in result
    assert 'priority_routes' in result
    assert 'infrastructure_used' in result
    
    # Verify severity matches input
    assert result['severity'] == 'high'
    
    # Verify routes
    assert isinstance(result['routes'], list)
    assert len(result['routes']) > 0
    
    # Verify route structure
    route = result['routes'][0]
    assert 'id' in route
    assert 'origin' in route
    assert 'destination' in route
    assert 'path' in route
    assert 'distance_km' in route
    assert 'time_minutes' in route
    assert 'status' in route
    assert 'priority' in route
    
    print("✓ Basic analyze flow completed successfully")


@pytest.mark.asyncio
async def test_get_center_point():
    """Test center point extraction from fire perimeter"""
    agent = RoutingAgent()
    
    fire_perimeter = {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-79.8650, 43.7320],
                [-79.8550, 43.7320],
                [-79.8550, 43.7380],
                [-79.8650, 43.7380],
                [-79.8650, 43.7320]
            ]]
        }
    }
    
    center = agent._get_center_point(fire_perimeter)
    
    assert len(center) == 2
    # Center should be approximately in the middle of the polygon
    assert 43.730 < center[1] < 43.740
    assert -79.870 < center[0] < -79.850
    
    print("✓ Center point extracted correctly")


@pytest.mark.asyncio
async def test_get_center_point_default():
    """Test center point returns default when perimeter is invalid"""
    agent = RoutingAgent()
    
    # Test with None
    center = agent._get_center_point(None)
    assert center == [-79.8620, 43.7315]
    
    # Test with empty dict
    center = agent._get_center_point({})
    assert center == [-79.8620, 43.7315]
    
    print("✓ Default center point handled correctly")


@pytest.mark.asyncio
async def test_calculate_distance():
    """Test distance calculation using Haversine formula"""
    agent = RoutingAgent()
    
    # Test approximate distance between two known points
    lat1, lon1 = 43.7320, -79.8600
    lat2, lon2 = 43.7150, -79.8400
    
    distance = agent._calculate_distance(lat1, lon1, lat2, lon2)
    
    # Distance should be approximately 2.5 km
    assert 2.0 < distance < 3.5
    
    print("✓ Distance calculated correctly")


@pytest.mark.asyncio
async def test_generate_route_path():
    """Test route path generation"""
    agent = RoutingAgent()
    
    start_lon, start_lat = -79.8600, 43.7320
    end_lon, end_lat = -79.8400, 43.7150
    
    path = agent._generate_route_path(start_lon, start_lat, end_lon, end_lat)
    
    # Should have 11 points (0 to 10 inclusive)
    assert len(path) == 11
    
    # First point should be start
    assert path[0] == [start_lon, start_lat]
    
    # Last point should be end
    assert path[-1] == [end_lon, end_lat]
    
    # All points should be lists with 2 elements
    for point in path:
        assert len(point) == 2
        assert isinstance(point[0], float)
        assert isinstance(point[1], float)
    
    print("✓ Route path generated correctly")


@pytest.mark.asyncio
async def test_generate_evacuation_routes():
    """Test evacuation route generation"""
    agent = RoutingAgent()
    
    origin = [-79.8600, 43.7320]
    affected_area = 0.5
    status = "monitor"
    
    routes = agent._generate_evacuation_routes(origin, affected_area, status)
    
    # Should generate 3 routes
    assert len(routes) == 3
    
    # Check first route (primary)
    primary_route = routes[0]
    assert primary_route['priority'] == 'primary'
    assert primary_route['id'] == 'route-1'
    assert 'destination' in primary_route
    assert 'path' in primary_route
    assert primary_route['path']['type'] == 'Feature'
    assert primary_route['path']['geometry']['type'] == 'LineString'
    
    # Check that destinations are different
    destinations = [r['destination']['name'] for r in routes]
    assert len(set(destinations)) == 3
    
    print("✓ Evacuation routes generated correctly")


@pytest.mark.asyncio
async def test_severity_status_mapping():
    """Test that severity maps correctly to route status"""
    agent = RoutingAgent()
    
    # Test low severity
    damage_summary_low = {
        "severity": "low",
        "affected_area_km2": 0.1,
        "fire_perimeter": {}
    }
    result = await agent.analyze(None, None, damage_summary_low)
    # Primary route should be open for low severity
    assert result['routes'][0]['status'] == 'open'
    
    # Test extreme severity
    damage_summary_extreme = {
        "severity": "extreme",
        "affected_area_km2": 5.0,
        "fire_perimeter": {}
    }
    result = await agent.analyze(None, None, damage_summary_extreme)
    # Primary route should be closed for extreme severity
    assert result['routes'][0]['status'] == 'closed'
    
    print("✓ Severity to status mapping works correctly")


@pytest.mark.asyncio
async def test_analyze_with_infrastructure_data():
    """Test analyze with infrastructure data"""
    agent = RoutingAgent()
    
    # Mock infrastructure data
    import pandas as pd
    infrastructure_df = pd.DataFrame({
        'name': ['Road A', 'Road B', 'Road C'],
        'type': ['highway', 'street', 'avenue']
    })
    
    damage_summary = create_damage_summary()
    
    result = await agent.analyze(None, infrastructure_df, damage_summary)
    
    assert 'infrastructure_used' in result
    assert isinstance(result['infrastructure_used'], list)
    # Should extract up to 3 names
    assert len(result['infrastructure_used']) <= 3
    
    print("✓ Infrastructure data processed correctly")


@pytest.mark.asyncio
async def test_analyze_returns_both_routes_keys():
    """Test that analyze returns both 'routes' and 'priority_routes' for compatibility"""
    agent = RoutingAgent()
    
    damage_summary = create_damage_summary()
    result = await agent.analyze(None, None, damage_summary)
    
    # Both keys should exist for backward compatibility
    assert 'routes' in result
    assert 'priority_routes' in result
    
    # They should contain the same data
    assert result['routes'] == result['priority_routes']
    
    print("✓ Both routes keys present for compatibility")


@pytest.mark.asyncio
async def test_route_time_estimation():
    """Test that route time estimation is reasonable"""
    agent = RoutingAgent()
    
    damage_summary = create_damage_summary()
    result = await agent.analyze(None, None, damage_summary)
    
    for route in result['routes']:
        distance_km = route['distance_km']
        time_minutes = route['time_minutes']
        
        # Time should be positive
        assert time_minutes > 0
        
        # Speed should be reasonable (assumes 30 km/h average)
        # Time in minutes = (distance / speed) * 60
        expected_time = (distance_km / 30.0) * 60
        assert abs(time_minutes - expected_time) < 5  # Allow 5 minute variance
    
    print("✓ Route time estimation is reasonable")


@pytest.mark.asyncio
async def test_route_destinations_have_capacity():
    """Test that all route destinations include capacity information"""
    agent = RoutingAgent()
    
    damage_summary = create_damage_summary()
    result = await agent.analyze(None, None, damage_summary)
    
    for route in result['routes']:
        destination = route['destination']
        assert 'capacity' in destination
        assert isinstance(destination['capacity'], int)
        assert destination['capacity'] > 0
        assert 'name' in destination
        assert 'lat' in destination
        assert 'lon' in destination
    
    print("✓ Route destinations have capacity information")


@pytest.mark.asyncio
async def test_july_2020_scenario():
    """Test July 2020 scenario routing"""
    agent = RoutingAgent()
    
    scenario_config = {
        'disaster': {
            'scenario_id': 'july_2020_backtest',
            'location': {'lat': 43.7315, 'lon': -79.8620}
        }
    }
    
    result = await agent.analyze(None, None, {}, scenario_config)
    
    # Verify July 2020 specific structure
    assert 'routes' in result
    assert 'estimated_evacuation_time_minutes' in result
    assert 'traffic_management' in result
    
    # Should have 3 routes
    assert len(result['routes']) == 3
    
    # Routes should have notes
    for route in result['routes']:
        assert 'notes' in route
    
    print("✓ July 2020 scenario routing works correctly")


# Direct execution
if __name__ == "__main__":
    async def run_tests():
        print("=" * 60)
        print("Running RoutingAgent Tests")
        print("=" * 60)
        print()
        
        await test_routing_agent_initialization()
        await test_analyze_basic_flow()
        await test_get_center_point()
        await test_get_center_point_default()
        await test_calculate_distance()
        await test_generate_route_path()
        await test_generate_evacuation_routes()
        await test_severity_status_mapping()
        await test_analyze_with_infrastructure_data()
        await test_analyze_returns_both_routes_keys()
        await test_route_time_estimation()
        await test_route_destinations_have_capacity()
        await test_july_2020_scenario()
        
        print()
        print("=" * 60)
        print("✅ All RoutingAgent tests passed!")
        print("=" * 60)
    
    asyncio.run(run_tests())