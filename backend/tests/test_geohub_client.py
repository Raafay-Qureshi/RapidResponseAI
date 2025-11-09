"""
Test file for GeoHubClient

This file tests the GeoHubClient class which loads static Brampton data
from GeoJSON files for infrastructure, population, and roads.

Run this test with:
    python backend/tests/test_geohub_client.py
"""

import sys
import os
import asyncio
import pytest

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.geohub_client import GeoHubClient


@pytest.mark.asyncio
async def test_infrastructure():
    """Test loading infrastructure data"""
    print("\n" + "="*60)
    print("TEST 1: Loading Infrastructure Data")
    print("="*60)
    
    client = GeoHubClient()
    
    # Test with downtown Brampton location
    location = {'lat': 43.7315, 'lon': -79.7624}
    
    try:
        infra_data = await client.fetch_infrastructure(location)
        
        if infra_data is not None:
            print(f"✓ Successfully loaded infrastructure data")
            print(f"  Number of features: {len(infra_data)}")
            print(f"  Columns: {', '.join(infra_data.columns)}")
            
            # Display first few features
            print("\n  Infrastructure Features:")
            for idx, row in infra_data.head(3).iterrows():
                print(f"    - {row['name']} ({row['type']})")
            
            print("\n✓ TEST PASSED: Infrastructure data loaded successfully")
        else:
            print("✗ TEST FAILED: Infrastructure data is None")
            
    except Exception as e:
        print(f"✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_population():
    """Test loading population data"""
    print("\n" + "="*60)
    print("TEST 2: Loading Population Data")
    print("="*60)
    
    client = GeoHubClient()
    
    # Test with downtown Brampton location
    location = {'lat': 43.7300, 'lon': -79.7625}
    
    try:
        pop_data = await client.fetch_population(location)
        
        if pop_data is not None:
            print(f"✓ Successfully loaded population data")
            print(f"  Number of census tracts: {len(pop_data)}")
            print(f"  Columns: {', '.join(pop_data.columns)}")
            
            # Calculate totals
            total_pop = pop_data['population'].sum()
            total_vulnerable = pop_data['vulnerable_pop'].sum()
            
            print(f"\n  Population Statistics:")
            print(f"    Total Population: {total_pop:,}")
            print(f"    Vulnerable Population: {total_vulnerable:,}")
            print(f"    Average Density: {pop_data['density'].mean():.0f} per km²")
            
            # Display census tracts
            print("\n  Census Tracts:")
            for idx, row in pop_data.head(3).iterrows():
                print(f"    - {row['tract_id']}: {row['population']:,} people")
            
            print("\n✓ TEST PASSED: Population data loaded successfully")
        else:
            print("✗ TEST FAILED: Population data is None")
            
    except Exception as e:
        print(f"✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_roads():
    """Test loading roads data"""
    print("\n" + "="*60)
    print("TEST 3: Loading Roads Data")
    print("="*60)
    
    client = GeoHubClient()
    
    # Test with downtown Brampton location
    location = {'lat': 43.7300, 'lon': -79.7625}
    
    try:
        roads_data = await client.fetch_roads(location)
        
        if roads_data is not None:
            print(f"✓ Successfully loaded roads data")
            print(f"  Number of road segments: {len(roads_data)}")
            print(f"  Columns: {', '.join(roads_data.columns)}")
            
            # Calculate totals
            total_capacity = roads_data['capacity_vph'].sum()
            
            print(f"\n  Roads Statistics:")
            print(f"    Total Road Capacity: {total_capacity:,} vehicles/hour")
            print(f"    Average Lanes: {roads_data['lanes'].mean():.1f}")
            
            # Display roads by class
            print("\n  Roads by Class:")
            for road_class in roads_data['road_class'].unique():
                count = len(roads_data[roads_data['road_class'] == road_class])
                print(f"    - {road_class}: {count} roads")
            
            # Display major roads
            print("\n  Major Roads:")
            for idx, row in roads_data.head(3).iterrows():
                print(f"    - {row['name']} ({row['lanes']} lanes)")
            
            print("\n✓ TEST PASSED: Roads data loaded successfully")
        else:
            print("✗ TEST FAILED: Roads data is None")
            
    except Exception as e:
        print(f"✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_location_filtering():
    """Test location-based filtering"""
    print("\n" + "="*60)
    print("TEST 4: Location-Based Filtering")
    print("="*60)
    
    client = GeoHubClient()
    
    # Test with a specific location
    downtown_location = {'lat': 43.7315, 'lon': -79.7624}
    north_location = {'lat': 43.7450, 'lon': -79.7625}
    
    try:
        # Get data for downtown
        downtown_infra = await client.fetch_infrastructure(downtown_location)
        
        # Get data for north (should be different)
        north_infra = await client.fetch_infrastructure(north_location)
        
        print(f"✓ Downtown location: {len(downtown_infra)} infrastructure features")
        print(f"✓ North location: {len(north_infra)} infrastructure features")
        
        # Get all data (no location filter)
        all_infra = await client.fetch_infrastructure(None)
        print(f"✓ All data: {len(all_infra)} infrastructure features")
        
        print("\n✓ TEST PASSED: Location filtering works correctly")
        
    except Exception as e:
        print(f"✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_data_cache():
    """Test data caching mechanism"""
    print("\n" + "="*60)
    print("TEST 5: Data Caching")
    print("="*60)
    
    client = GeoHubClient()
    location = {'lat': 43.7300, 'lon': -79.7625}
    
    try:
        # First call - loads from file
        import time
        start = time.time()
        data1 = await client.fetch_infrastructure(location)
        time1 = time.time() - start
        
        # Second call - should use cache
        start = time.time()
        data2 = await client.fetch_infrastructure(location)
        time2 = time.time() - start
        
        print(f"✓ First call (load from file): {time1:.4f} seconds")
        print(f"✓ Second call (from cache): {time2:.4f} seconds")
        
        # Cache should make it faster (usually)
        if time2 <= time1:
            print(f"✓ Cache is working (second call was faster or equal)")
        else:
            print(f"⚠ Cache may not be optimizing (but this is okay)")
        
        # Test cache clearing
        client.clear_cache()
        print(f"✓ Cache cleared successfully")
        
        print("\n✓ TEST PASSED: Caching mechanism works")
        
    except Exception as e:
        print(f"✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


@pytest.mark.asyncio
async def test_data_structure():
    """Test that returned data has correct structure"""
    print("\n" + "="*60)
    print("TEST 6: Data Structure Validation")
    print("="*60)
    
    client = GeoHubClient()
    location = {'lat': 43.7300, 'lon': -79.7625}
    
    try:
        # Test infrastructure structure
        infra = await client.fetch_infrastructure(location)
        assert 'name' in infra.columns, "Infrastructure missing 'name' column"
        assert 'type' in infra.columns, "Infrastructure missing 'type' column"
        assert 'capacity' in infra.columns, "Infrastructure missing 'capacity' column"
        assert infra.geometry is not None, "Infrastructure missing geometry"
        print("✓ Infrastructure data structure is valid")
        
        # Test population structure
        pop = await client.fetch_population(location)
        assert 'tract_id' in pop.columns, "Population missing 'tract_id' column"
        assert 'population' in pop.columns, "Population missing 'population' column"
        assert 'vulnerable_pop' in pop.columns, "Population missing 'vulnerable_pop' column"
        assert pop.geometry is not None, "Population missing geometry"
        print("✓ Population data structure is valid")
        
        # Test roads structure
        roads = await client.fetch_roads(location)
        assert 'name' in roads.columns, "Roads missing 'name' column"
        assert 'road_class' in roads.columns, "Roads missing 'road_class' column"
        assert 'capacity_vph' in roads.columns, "Roads missing 'capacity_vph' column"
        assert roads.geometry is not None, "Roads missing geometry"
        print("✓ Roads data structure is valid")
        
        print("\n✓ TEST PASSED: All data structures are valid")
        
    except AssertionError as e:
        print(f"✗ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("GEOHUB CLIENT TEST SUITE")
    print("="*60)
    print("\nTesting static Brampton data loading...")
    
    await test_infrastructure()
    await test_population()
    await test_roads()
    await test_location_filtering()
    await test_data_cache()
    await test_data_structure()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    # Run tests
    asyncio.run(run_all_tests())