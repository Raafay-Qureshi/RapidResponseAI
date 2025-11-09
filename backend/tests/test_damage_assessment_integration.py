"""
Integration test for DamageAssessmentAgent with SatelliteClient
"""
import asyncio
import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.damage_assessment import DamageAssessmentAgent


@pytest.mark.asyncio
async def test_with_satellite_client_data():
    """Test DamageAssessmentAgent with sample SatelliteClient output"""
    agent = DamageAssessmentAgent()
    
    # Simulated data from SatelliteClient (similar to what fetch_imagery returns)
    satellite_imagery = {
        'fire_detections': [
            {'latitude': -3.0, 'longitude': -60.0, 'bright_ti4': 380.0, 'acq_date': '2024-01-15'},
            {'latitude': -3.1, 'longitude': -59.9, 'bright_ti4': 375.0, 'acq_date': '2024-01-15'},
        ],
        'fire_perimeter': {
            "type": "Polygon",
            "coordinates": [[
                [-60.5, -3.5],
                [-59.5, -3.5],
                [-59.5, -2.5],
                [-60.5, -2.5],
                [-60.5, -3.5]
            ]]
        },
        'thermal_intensity': 380,
        'satellite': 'VIIRS',
        'timestamp': '2024-01-15'
    }
    
    print("\n" + "="*60)
    print("🧪 Testing DamageAssessmentAgent with SatelliteClient data")
    print("="*60)
    
    result = await agent.analyze(satellite_imagery, "wildfire")
    
    print("\n📊 Analysis Results:")
    print(f"   Affected Area: {result['affected_area_km2']:.2f} km²")
    print(f"   Severity: {result['severity']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Analysis Time: {result['analysis_time']}")
    print(f"   Fire Perimeter: {result['fire_perimeter']['type']}")
    
    # Verify results
    assert result['affected_area_km2'] > 0, "Area should be greater than 0"
    assert result['severity'] in ['low', 'moderate', 'high', 'extreme'], "Severity should be valid"
    assert result['confidence'] == 0.92, "Confidence should be 0.92"
    assert result['fire_perimeter'] is not None, "Fire perimeter should exist"
    
    print("\n✅ Integration test passed!")
    print("="*60)
    
    return result


if __name__ == "__main__":
    asyncio.run(test_with_satellite_client_data())