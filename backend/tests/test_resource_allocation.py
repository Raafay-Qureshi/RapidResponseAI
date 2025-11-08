import os
import sys
import pytest

# Add backend to the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.resource_allocation import ResourceAllocationAgent


@pytest.fixture
def agent():
    """Create a ResourceAllocationAgent instance for testing"""
    return ResourceAllocationAgent()


@pytest.fixture
def sample_population_impact():
    """Sample population impact data from PopulationImpactAgent"""
    return {
        'total_affected': 10000,
        'vulnerable_population': {
            'elderly': 1500,
            'disabled': 500,
            'children': 2000
        },
        'evacuation_zones': ['Zone A', 'Zone B'],
        'severity': 'high'
    }


@pytest.fixture
def sample_infrastructure():
    """Sample infrastructure data"""
    return {
        'roads': [],
        'buildings': [],
        'critical_facilities': []
    }


@pytest.mark.asyncio
async def test_resource_allocation_agent_initialization(agent):
    """Test that the agent initializes correctly"""
    assert isinstance(agent, ResourceAllocationAgent)
    assert agent.name == "ResourceAllocationAgent"


@pytest.mark.asyncio
async def test_analyze_returns_correct_structure(agent, sample_population_impact, sample_infrastructure):
    """Test that analyze method returns the expected structure"""
    result = await agent.analyze(sample_population_impact, sample_infrastructure)
    
    assert 'required_resources' in result
    assert 'available_resources' in result
    
    # Check required_resources structure
    assert 'ambulances' in result['required_resources']
    assert 'evacuation_buses' in result['required_resources']
    assert 'personnel' in result['required_resources']
    
    # Check available_resources structure
    assert 'fire_stations' in result['available_resources']
    assert 'hospitals' in result['available_resources']
    assert 'police_stations' in result['available_resources']


@pytest.mark.asyncio
async def test_calculate_ambulances_correct_logic(agent):
    """Test ambulance calculation: 1 per 100 vulnerable people"""
    # Test case 1: 1500 elderly + 500 disabled = 2000 vulnerable
    # Expected: 2000 // 100 = 20 ambulances
    vulnerable_pop = {'elderly': 1500, 'disabled': 500}
    result = agent._calculate_ambulances(vulnerable_pop)
    assert result == 20
    
    # Test case 2: Small numbers should return at least 1
    vulnerable_pop = {'elderly': 50, 'disabled': 30}
    result = agent._calculate_ambulances(vulnerable_pop)
    assert result == 1
    
    # Test case 3: Exactly 100 vulnerable
    vulnerable_pop = {'elderly': 60, 'disabled': 40}
    result = agent._calculate_ambulances(vulnerable_pop)
    assert result == 1
    
    # Test case 4: Missing disabled key
    vulnerable_pop = {'elderly': 250}
    result = agent._calculate_ambulances(vulnerable_pop)
    assert result == 2
    
    # Test case 5: Empty dict
    vulnerable_pop = {}
    result = agent._calculate_ambulances(vulnerable_pop)
    assert result == 1  # Minimum of 1


@pytest.mark.asyncio
async def test_calculate_buses_correct_logic(agent):
    """Test bus calculation: 20% of population, 1 bus per 50 people"""
    # Test case 1: 10000 people
    # 20% = 2000 people needing buses
    # 2000 / 50 = 40 buses
    result = agent._calculate_buses(10000)
    assert result == 40
    
    # Test case 2: 1000 people
    # 20% = 200 people
    # 200 / 50 = 4 buses
    result = agent._calculate_buses(1000)
    assert result == 4
    
    # Test case 3: Small population should return at least 1
    result = agent._calculate_buses(100)
    assert result == 1
    
    # Test case 4: Zero population
    result = agent._calculate_buses(0)
    assert result == 1  # Minimum of 1


@pytest.mark.asyncio
async def test_calculate_personnel_correct_logic(agent):
    """Test personnel calculation: 1 responder per 200 affected people"""
    # Test case 1: 10000 people
    # 10000 / 200 = 50 personnel
    result = agent._calculate_personnel(10000)
    assert result == 50
    
    # Test case 2: 1000 people
    # 1000 / 200 = 5 personnel
    result = agent._calculate_personnel(1000)
    assert result == 5
    
    # Test case 3: Small population should return at least 5
    result = agent._calculate_personnel(100)
    assert result == 5  # Minimum of 5
    
    # Test case 4: Zero population
    result = agent._calculate_personnel(0)
    assert result == 5  # Minimum of 5


@pytest.mark.asyncio
async def test_map_current_resources_structure(agent):
    """Test that _map_current_resources returns expected structure"""
    resources = agent._map_current_resources()
    
    # Check top-level keys
    assert 'fire_stations' in resources
    assert 'hospitals' in resources
    assert 'police_stations' in resources
    
    # Check fire stations structure
    assert len(resources['fire_stations']) == 2
    for station in resources['fire_stations']:
        assert 'id' in station
        assert 'lat' in station
        assert 'lon' in station
        assert 'trucks' in station
    
    # Check hospitals structure
    assert len(resources['hospitals']) == 1
    for hospital in resources['hospitals']:
        assert 'id' in hospital
        assert 'lat' in hospital
        assert 'lon' in hospital
        assert 'ambulances' in hospital
    
    # Check police stations structure
    assert len(resources['police_stations']) == 1
    for station in resources['police_stations']:
        assert 'id' in station
        assert 'lat' in station
        assert 'lon' in station
        assert 'units' in station


@pytest.mark.asyncio
async def test_analyze_with_minimal_data(agent):
    """Test analyze with minimal/empty population impact data"""
    minimal_impact = {
        'total_affected': 0,
        'vulnerable_population': {}
    }
    infrastructure = {}
    
    result = await agent.analyze(minimal_impact, infrastructure)
    
    # Should still return valid structure with minimum values
    assert result['required_resources']['ambulances'] >= 1
    assert result['required_resources']['evacuation_buses'] >= 1
    assert result['required_resources']['personnel'] >= 5
    assert 'available_resources' in result


@pytest.mark.asyncio
async def test_analyze_with_large_population(agent):
    """Test analyze with large population numbers"""
    large_impact = {
        'total_affected': 50000,
        'vulnerable_population': {
            'elderly': 8000,
            'disabled': 2000
        }
    }
    infrastructure = {}
    
    result = await agent.analyze(large_impact, infrastructure)
    
    # 10000 vulnerable / 100 = 100 ambulances
    assert result['required_resources']['ambulances'] == 100
    
    # 50000 * 0.20 / 50 = 200 buses
    assert result['required_resources']['evacuation_buses'] == 200
    
    # 50000 / 200 = 250 personnel
    assert result['required_resources']['personnel'] == 250


@pytest.mark.asyncio
async def test_analyze_integration(agent, sample_population_impact, sample_infrastructure):
    """Integration test for the full analyze workflow"""
    result = await agent.analyze(sample_population_impact, sample_infrastructure)
    
    # Verify calculations based on sample data
    # 1500 elderly + 500 disabled = 2000 vulnerable
    # 2000 / 100 = 20 ambulances
    assert result['required_resources']['ambulances'] == 20
    
    # 10000 * 0.20 / 50 = 40 buses
    assert result['required_resources']['evacuation_buses'] == 40
    
    # 10000 / 200 = 50 personnel
    assert result['required_resources']['personnel'] == 50
    
    # Verify available resources are populated
    assert len(result['available_resources']['fire_stations']) > 0
    assert len(result['available_resources']['hospitals']) > 0
    assert len(result['available_resources']['police_stations']) > 0


@pytest.mark.asyncio
async def test_analyze_with_missing_vulnerable_keys(agent):
    """Test analyze when vulnerable_population has missing keys"""
    impact = {
        'total_affected': 5000,
        'vulnerable_population': {
            'elderly': 800
            # 'disabled' key is missing
        }
    }
    infrastructure = {}
    
    result = await agent.analyze(impact, infrastructure)
    
    # Should handle missing 'disabled' key gracefully
    # 800 / 100 = 8 ambulances
    assert result['required_resources']['ambulances'] == 8
    assert isinstance(result['required_resources']['ambulances'], int)


@pytest.mark.asyncio
async def test_resource_types_are_integers(agent, sample_population_impact, sample_infrastructure):
    """Test that all resource counts are integers"""
    result = await agent.analyze(sample_population_impact, sample_infrastructure)
    
    assert isinstance(result['required_resources']['ambulances'], int)
    assert isinstance(result['required_resources']['evacuation_buses'], int)
    assert isinstance(result['required_resources']['personnel'], int)


@pytest.mark.asyncio
async def test_available_resources_coordinates(agent):
    """Test that all available resources have valid coordinates"""
    resources = agent._map_current_resources()
    
    # Check fire stations
    for station in resources['fire_stations']:
        assert isinstance(station['lat'], float)
        assert isinstance(station['lon'], float)
        assert -90 <= station['lat'] <= 90
        assert -180 <= station['lon'] <= 180
    
    # Check hospitals
    for hospital in resources['hospitals']:
        assert isinstance(hospital['lat'], float)
        assert isinstance(hospital['lon'], float)
        assert -90 <= hospital['lat'] <= 90
        assert -180 <= hospital['lon'] <= 180
    
    # Check police stations
    for station in resources['police_stations']:
        assert isinstance(station['lat'], float)
        assert isinstance(station['lon'], float)
        assert -90 <= station['lat'] <= 90
        assert -180 <= station['lon'] <= 180