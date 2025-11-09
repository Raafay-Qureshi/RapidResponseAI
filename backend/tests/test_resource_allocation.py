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
def sample_population_summary():
    """Sample population summary data from PopulationImpactAgent"""
    return {
        'total_affected': 10000,
        'vulnerable_population': {
            'elderly': 1500,
            'children': 2000
        },
        'critical_facilities': [
            {'name': 'Hospital A', 'type': 'hospital'},
            {'name': 'School B', 'type': 'school'}
        ]
    }


@pytest.fixture
def sample_routing_summary():
    """Sample routing summary data from RoutingAgent"""
    return {
        'severity': 'high',
        'routes': [
            {'id': 'route-1', 'status': 'open'}
        ]
    }


@pytest.fixture
def sample_infrastructure():
    """Sample infrastructure data"""
    import pandas as pd
    return pd.DataFrame({
        'name': ['Fire Station A', 'Police Station B'],
        'type': ['fire', 'police']
    })


@pytest.mark.asyncio
async def test_resource_allocation_agent_initialization(agent):
    """Test that the agent initializes correctly"""
    assert isinstance(agent, ResourceAllocationAgent)
    assert agent.name == "ResourceAllocationAgent"


@pytest.mark.asyncio
async def test_analyze_returns_correct_structure(agent, sample_population_summary, sample_routing_summary, sample_infrastructure):
    """Test that analyze returns the correct structure"""
    result = await agent.analyze(
        sample_population_summary,
        sample_routing_summary,
        sample_infrastructure
    )
    
    # Check expected keys
    assert 'total_affected' in result
    assert 'shelters_needed' in result
    assert 'medical_units' in result
    assert 'relief_kits' in result
    assert 'critical_facilities' in result
    assert 'route_status' in result
    assert 'staging_sites' in result


@pytest.mark.asyncio
async def test_shelters_calculation(agent, sample_routing_summary):
    """Test shelter calculation: 1 shelter per 500 people"""
    # 10000 people / 500 = 20 shelters
    population_summary = {
        'total_affected': 10000,
        'vulnerable_population': {'elderly': 1500},
        'critical_facilities': []
    }
    
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['shelters_needed'] == 20
    
    # Test with 2500 people
    population_summary['total_affected'] = 2500
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['shelters_needed'] == 5
    
    # Test with 0 people
    population_summary['total_affected'] = 0
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['shelters_needed'] == 0


@pytest.mark.asyncio
async def test_medical_units_calculation(agent, sample_routing_summary):
    """Test medical units calculation: 1 unit per 100 elderly"""
    # 1500 elderly / 100 = 15 medical units
    population_summary = {
        'total_affected': 10000,
        'vulnerable_population': {'elderly': 1500},
        'critical_facilities': []
    }
    
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['medical_units'] == 15
    
    # Test with 250 elderly
    population_summary['vulnerable_population']['elderly'] = 250
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['medical_units'] == 3  # ceil(250/100) = 3
    
    # Test with no vulnerable population
    population_summary['vulnerable_population'] = {}
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['medical_units'] == 0


@pytest.mark.asyncio
async def test_relief_kits_calculation(agent, sample_routing_summary):
    """Test relief kits calculation: 1 kit per affected person"""
    population_summary = {
        'total_affected': 10000,
        'vulnerable_population': {'elderly': 1500},
        'critical_facilities': []
    }
    
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['relief_kits'] == 10000
    
    # Test with different numbers
    population_summary['total_affected'] = 5000
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['relief_kits'] == 5000
    
    # Test with 0
    population_summary['total_affected'] = 0
    result = await agent.analyze(population_summary, sample_routing_summary, None)
    assert result['relief_kits'] == 0


@pytest.mark.asyncio
async def test_analyze_with_minimal_data(agent):
    """Test analyze with minimal/empty population summary data"""
    minimal_summary = {
        'total_affected': 0,
        'vulnerable_population': {},
        'critical_facilities': []
    }
    routing_summary = {'severity': 'low'}
    
    result = await agent.analyze(minimal_summary, routing_summary, None)
    
    # Should still return valid structure with zero/empty values
    assert result['total_affected'] == 0
    assert result['shelters_needed'] == 0
    assert result['medical_units'] == 0
    assert result['relief_kits'] == 0
    assert result['critical_facilities'] == []


@pytest.mark.asyncio
async def test_analyze_with_large_population(agent, sample_routing_summary):
    """Test analyze with large population numbers"""
    large_summary = {
        'total_affected': 50000,
        'vulnerable_population': {
            'elderly': 8000,
            'children': 12000
        },
        'critical_facilities': []
    }
    
    result = await agent.analyze(large_summary, sample_routing_summary, None)
    
    # 50000 / 500 = 100 shelters
    assert result['shelters_needed'] == 100
    
    # 8000 / 100 = 80 medical units
    assert result['medical_units'] == 80
    
    # 50000 relief kits
    assert result['relief_kits'] == 50000


@pytest.mark.asyncio
async def test_summarize_facilities(agent):
    """Test critical facilities summarization"""
    facilities = [
        {'name': 'Hospital A', 'type': 'hospital'},
        {'name': 'School B', 'type': 'school'},
        {'name': 'Fire Station C', 'type': 'fire'}
    ]
    
    result = agent._summarize_facilities(facilities)
    
    assert len(result) == 3
    assert 'Hospital A' in result
    assert 'School B' in result
    assert 'Fire Station C' in result


@pytest.mark.asyncio
async def test_summarize_facilities_empty(agent):
    """Test critical facilities summarization with empty list"""
    result = agent._summarize_facilities([])
    assert result == []


@pytest.mark.asyncio
async def test_candidate_sites_with_dataframe(agent):
    """Test staging sites extraction from infrastructure DataFrame"""
    import pandas as pd
    
    infrastructure_df = pd.DataFrame({
        'name': ['Site A', 'Site B', 'Site C'],
        'type': ['government', 'government', 'private']
    })
    
    result = agent._candidate_sites(infrastructure_df)
    
    # Should return up to 2 government sites
    assert isinstance(result, list)
    assert len(result) <= 2


@pytest.mark.asyncio
async def test_candidate_sites_with_none(agent):
    """Test staging sites extraction with None infrastructure"""
    result = agent._candidate_sites(None)
    assert result == []


@pytest.mark.asyncio
async def test_analyze_integration(agent, sample_population_summary, sample_routing_summary, sample_infrastructure):
    """Test full analyze integration"""
    result = await agent.analyze(
        sample_population_summary,
        sample_routing_summary,
        sample_infrastructure
    )
    
    # Verify calculations based on sample data
    assert result['total_affected'] == 10000
    assert result['shelters_needed'] == 20  # 10000 / 500
    assert result['medical_units'] == 15  # 1500 / 100
    assert result['relief_kits'] == 10000
    
    # Verify other fields exist
    assert 'critical_facilities' in result
    assert 'route_status' in result
    assert result['route_status'] == 'high'
    assert 'staging_sites' in result


@pytest.mark.asyncio
async def test_route_status_extraction(agent, sample_population_summary):
    """Test that route_status is correctly extracted from routing_summary"""
    routing_summary = {'severity': 'extreme', 'routes': []}
    
    result = await agent.analyze(sample_population_summary, routing_summary, None)
    
    assert result['route_status'] == 'extreme'


@pytest.mark.asyncio
async def test_resource_types_are_integers(agent, sample_population_summary, sample_routing_summary):
    """Test that all resource counts are integers"""
    result = await agent.analyze(sample_population_summary, sample_routing_summary, None)
    
    assert isinstance(result['total_affected'], int)
    assert isinstance(result['shelters_needed'], int)
    assert isinstance(result['medical_units'], int)
    assert isinstance(result['relief_kits'], int)


@pytest.mark.asyncio
async def test_july_2020_scenario(agent):
    """Test July 2020 scenario resource allocation"""
    scenario_config = {
        'disaster': {
            'scenario_id': 'july_2020_backtest'
        },
        'population_estimate': {
            'total_affected': 2000,
            'immediate_danger': 800,
            'evacuation_recommended': 1200,
            'vulnerable_elderly': 285,
            'vulnerable_children': 420
        }
    }
    
    result = await agent.analyze({}, {}, None, scenario_config)
    
    # Verify July 2020 specific structure
    assert 'required_resources' in result
    assert 'available_resources' in result
    assert 'deployment_plan' in result
    assert 'mutual_aid_requests' in result
    assert 'resource_gaps' in result
    assert 'highway_coordination' in result
    
    # Check required resources
    assert result['required_resources']['ambulances'] == 12
    assert result['required_resources']['evacuation_buses'] == 8
    assert result['required_resources']['personnel'] == 85


@pytest.mark.asyncio
async def test_analyze_with_missing_vulnerable_keys(agent, sample_routing_summary):
    """Test analyze when vulnerable_population has missing keys"""
    summary = {
        'total_affected': 5000,
        'vulnerable_population': {
            'children': 800
            # 'elderly' key is missing
        },
        'critical_facilities': []
    }
    
    result = await agent.analyze(summary, sample_routing_summary, None)
    
    # Should handle missing 'elderly' key gracefully and return 0 medical units
    assert result['medical_units'] == 0
    assert isinstance(result['medical_units'], int)


@pytest.mark.asyncio
async def test_critical_facilities_list(agent, sample_routing_summary):
    """Test that critical_facilities are properly extracted"""
    summary = {
        'total_affected': 1000,
        'vulnerable_population': {},
        'critical_facilities': [
            {'name': 'Hospital A'},
            {'name': 'School B'},
            {'name': 'Fire Station C'}
        ]
    }
    
    result = await agent.analyze(summary, sample_routing_summary, None)
    
    assert len(result['critical_facilities']) == 3
    assert 'Hospital A' in result['critical_facilities']
    assert 'School B' in result['critical_facilities']
    assert 'Fire Station C' in result['critical_facilities']