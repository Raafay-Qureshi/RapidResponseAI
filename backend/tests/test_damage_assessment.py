import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.damage_assessment import DamageAssessmentAgent


@pytest.mark.asyncio
async def test_damage_assessment_fire():
    """Test fire damage assessment with sample data"""
    agent = DamageAssessmentAgent()
    
    # Sample satellite imagery data (simulating SatelliteClient output)
    satellite_imagery = {
        'fire_perimeter': {
            "type": "Polygon",
            "coordinates": [[
                [-60.0, -3.0],
                [-59.5, -3.0],
                [-59.5, -2.5],
                [-60.0, -2.5],
                [-60.0, -3.0]
            ]]
        },
        'thermal_intensity': 380,  # Kelvin
        'satellite': 'VIIRS',
        'fire_detections': []
    }
    
    result = await agent.analyze(satellite_imagery, "wildfire")
    
    # Verify result structure
    assert 'affected_area_km2' in result
    assert 'fire_perimeter' in result
    assert 'severity' in result
    assert 'confidence' in result
    assert 'analysis_time' in result
    
    # Verify area calculation
    assert result['affected_area_km2'] > 0
    assert isinstance(result['affected_area_km2'], float)
    
    # Verify severity classification
    assert result['severity'] in ['low', 'moderate', 'high', 'extreme']
    assert result['severity'] == 'high'  # 380K should be high
    
    # Verify confidence
    assert result['confidence'] == 0.92
    
    print(f"\n✅ Fire damage assessment test passed!")
    print(f"   Affected area: {result['affected_area_km2']:.2f} km²")
    print(f"   Severity: {result['severity']}")


@pytest.mark.asyncio
async def test_damage_assessment_no_perimeter():
    """Test handling of missing fire perimeter"""
    agent = DamageAssessmentAgent()
    
    satellite_imagery = {
        'fire_perimeter': None,
        'thermal_intensity': 340
    }
    
    result = await agent.analyze(satellite_imagery, "wildfire")
    
    # Should handle None perimeter gracefully
    assert result['affected_area_km2'] == 0.0
    assert result['severity'] == 'moderate'


@pytest.mark.asyncio
async def test_severity_classification():
    """Test severity classification thresholds"""
    agent = DamageAssessmentAgent()
    
    test_cases = [
        (450, 'extreme'),
        (380, 'high'),
        (350, 'moderate'),
        (320, 'low')
    ]
    
    for thermal_intensity, expected_severity in test_cases:
        satellite_imagery = {
            'fire_perimeter': {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
            },
            'thermal_intensity': thermal_intensity
        }
        
        result = await agent.analyze(satellite_imagery, "wildfire")
        assert result['severity'] == expected_severity, \
            f"Expected {expected_severity} for {thermal_intensity}K, got {result['severity']}"


@pytest.mark.asyncio
async def test_unknown_disaster_type():
    """Test error handling for unknown disaster type"""
    agent = DamageAssessmentAgent()
    
    satellite_imagery = {'fire_perimeter': None}
    
    with pytest.raises(ValueError, match="Unknown disaster type"):
        await agent.analyze(satellite_imagery, "earthquake")


@pytest.mark.asyncio
async def test_flood_assessment_placeholder():
    """Test flood assessment placeholder"""
    agent = DamageAssessmentAgent()
    
    satellite_imagery = {}
    result = await agent.analyze(satellite_imagery, "flood")
    
    assert result['status'] == 'not_implemented'


if __name__ == "__main__":
    # Run tests directly
    async def run_tests():
        print("Running DamageAssessmentAgent tests...\n")
        
        await test_damage_assessment_fire()
        await test_damage_assessment_no_perimeter()
        await test_severity_classification()
        
        try:
            await test_unknown_disaster_type()
            print("❌ Should have raised ValueError")
        except ValueError:
            print("✅ Unknown disaster type test passed!")
        
        await test_flood_assessment_placeholder()
        print("✅ Flood assessment placeholder test passed!")
        
        print("\n🎉 All tests passed!")
    
    asyncio.run(run_tests())