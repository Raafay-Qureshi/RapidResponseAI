"""
Test script for July 2020 scenario agent outputs

This script tests each agent individually with the July 2020 scenario
and validates that all outputs are realistic and consistent.
"""

import asyncio
import sys
from pathlib import Path

# Fix Windows encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scenarios.july_2020_fire import load_july_2020_scenario
from agents.damage_assessment import DamageAssessmentAgent
from agents.population_impact import PopulationImpactAgent
from agents.prediction import PredictionAgent
from agents.routing import RoutingAgent
from agents.resource_allocation import ResourceAllocationAgent


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def validate_damage_assessment(result: dict) -> bool:
    """Validate Damage Assessment Agent output"""
    print_section("DAMAGE ASSESSMENT AGENT")

    # Expected values
    expected_area_km2 = 0.162
    expected_area_acres = 40

    print(f"✓ Affected Area (km²): {result.get('affected_area_km2')} (expected: {expected_area_km2})")
    print(f"✓ Affected Area (acres): {result.get('affected_area_acres')} (expected: {expected_area_acres})")
    print(f"✓ Fire Type: {result.get('fire_type')} (expected: WUI)")
    print(f"✓ Severity: {result.get('severity')} (expected: high)")
    print(f"✓ Confidence: {result.get('confidence')} (expected: 0.92)")
    print(f"✓ Notes: {result.get('analysis_notes')}")

    # Validate
    valid = (
        result.get('affected_area_km2') == expected_area_km2 and
        result.get('affected_area_acres') == expected_area_acres and
        result.get('fire_type') == 'WUI' and
        result.get('severity') == 'high' and
        result.get('confidence') == 0.92
    )

    print(f"\n{'✓ PASSED' if valid else '✗ FAILED'}")
    return valid


def validate_population_impact(result: dict) -> bool:
    """Validate Population Impact Agent output"""
    print_section("POPULATION IMPACT AGENT")

    # Expected values
    expected_total = 2000

    print(f"✓ Total Affected: {result.get('total_affected')} (expected: ~{expected_total})")
    print(f"✓ Immediate Danger: {result.get('immediate_danger')}")
    print(f"✓ Evacuation Recommended: {result.get('evacuation_recommended')}")
    print(f"✓ Vulnerable - Elderly: {result.get('vulnerable_population', {}).get('elderly')}")
    print(f"✓ Vulnerable - Children: {result.get('vulnerable_population', {}).get('children')}")
    print(f"✓ Critical Facilities: {len(result.get('critical_facilities', []))} facilities")
    print(f"✓ Affected Neighborhoods: {', '.join(result.get('affected_neighborhoods', []))}")
    print(f"✓ Economic Impact: ${result.get('economic_impact_estimate_usd'):,}")
    print(f"✓ Confidence: {result.get('confidence')} (expected: 0.88)")

    # Validate
    valid = (
        result.get('total_affected') == expected_total and
        result.get('confidence') == 0.88 and
        len(result.get('critical_facilities', [])) == 3
    )

    print(f"\n{'✓ PASSED' if valid else '✗ FAILED'}")
    return valid


def validate_prediction(result: dict) -> bool:
    """Validate Prediction Agent output"""
    print_section("PREDICTION AGENT")

    print(f"✓ Current Spread Rate: {result.get('current_spread_rate_kmh')} km/h")
    print(f"✓ Spread Direction: {result.get('spread_direction')}")
    print(f"✓ Confidence: {result.get('confidence')} (expected: 0.87)")
    print(f"✓ Outlook: {result.get('outlook')}")

    print("\nCritical Arrival Times:")
    for arrival in result.get('critical_arrival_times', []):
        print(f"  • {arrival['location']}: {arrival['hours_until_arrival']} hours")
        print(f"    Impact: {arrival['impact']}")

    print("\nTimeline Predictions:")
    for timeframe, prediction in result.get('predictions', {}).items():
        print(f"  • {timeframe}: {prediction['area_km2']} km² (confidence: {prediction['confidence']})")

    print("\nInfrastructure Threats:")
    for threat in result.get('infrastructure_threats', []):
        print(f"  • {threat['asset']}: {threat['threat_level']} threat")
        print(f"    Time to impact: {threat['time_to_impact_hours']} hours")

    # Validate HWY 407 threat timing
    hwy_407_threat = None
    for arrival in result.get('critical_arrival_times', []):
        if 'HWY 407' in arrival['location']:
            hwy_407_threat = arrival['hours_until_arrival']
            break

    valid = (
        hwy_407_threat is not None and
        2.0 <= hwy_407_threat <= 3.0 and  # Within 2-3 hours
        result.get('confidence') == 0.87
    )

    print(f"\n{'✓ PASSED - HWY 407 threat in 2-3 hours' if valid else '✗ FAILED'}")
    return valid


def validate_routing(result: dict) -> bool:
    """Validate Routing Agent output"""
    print_section("ROUTING AGENT")

    print(f"✓ Severity: {result.get('severity')}")
    print(f"✓ Routes: {len(result.get('routes', []))} evacuation routes")
    print(f"✓ Estimated Evacuation Time: {result.get('estimated_evacuation_time_minutes')} minutes")

    print("\nEvacuation Routes:")
    for route in result.get('routes', []):
        print(f"  • {route['destination']['name']}")
        print(f"    Distance: {route['distance_km']} km, Time: {route['time_minutes']} min")
        print(f"    Priority: {route['priority']}, Status: {route['status']}")

    # Validate
    valid = (
        len(result.get('routes', [])) >= 2 and
        result.get('severity') == 'high'
    )

    print(f"\n{'✓ PASSED' if valid else '✗ FAILED'}")
    return valid


def validate_resource_allocation(result: dict) -> bool:
    """Validate Resource Allocation Agent output"""
    print_section("RESOURCE ALLOCATION AGENT")

    print(f"✓ Confidence: {result.get('confidence')} (expected: 0.90)")

    print("\nRequired Resources:")
    for resource, count in result.get('required_resources', {}).items():
        print(f"  • {resource}: {count}")

    print("\nMutual Aid Requests:")
    for request in result.get('mutual_aid_requests', []):
        print(f"  • {request['municipality']}: {request['requested']}")
        print(f"    ETA: {request['eta_minutes']} minutes")
        print(f"    Justification: {request['justification']}")

    print("\nResource Gaps:")
    for gap in result.get('resource_gaps', []):
        print(f"  • {gap['resource']}: {gap['description']}")

    print("\nHighway Coordination:")
    hwy_coord = result.get('highway_coordination', {})
    print(f"  • Closure Plan: {hwy_coord.get('closure_plan')}")

    # Validate
    valid = (
        len(result.get('mutual_aid_requests', [])) == 3 and
        result.get('confidence') == 0.90 and
        result.get('required_resources', {}).get('fire_apparatus') == 15
    )

    print(f"\n{'✓ PASSED' if valid else '✗ FAILED'}")
    return valid


def cross_validate(results: dict) -> bool:
    """Cross-validate consistency across all agents"""
    print_section("CROSS-VALIDATION")

    damage = results['damage']
    population = results['population']
    prediction = results['prediction']
    routing = results['routing']
    resources = results['resources']

    checks = []

    # Check 1: Fire size consistency
    fire_size_consistent = damage.get('affected_area_acres') == 40
    print(f"{'✓' if fire_size_consistent else '✗'} Fire size: 40 acres")
    checks.append(fire_size_consistent)

    # Check 2: Population affected ~2,000
    pop_consistent = population.get('total_affected') == 2000
    print(f"{'✓' if pop_consistent else '✗'} Population affected: ~2,000")
    checks.append(pop_consistent)

    # Check 3: HWY 407 threat within 2-3 hours
    hwy_threat = None
    for arrival in prediction.get('critical_arrival_times', []):
        if 'HWY 407' in arrival['location']:
            hwy_threat = arrival['hours_until_arrival']
    hwy_consistent = hwy_threat is not None and 2.0 <= hwy_threat <= 3.0
    print(f"{'✓' if hwy_consistent else '✗'} HWY 407 threat: 2-3 hours ({hwy_threat} hours)")
    checks.append(hwy_consistent)

    # Check 4: Mutual aid from 3 municipalities
    mutual_aid_consistent = len(resources.get('mutual_aid_requests', [])) == 3
    print(f"{'✓' if mutual_aid_consistent else '✗'} Mutual aid: 3 municipalities")
    checks.append(mutual_aid_consistent)

    # Check 5: All confidence scores in range 0.85-0.92
    confidences = [
        damage.get('confidence', 0),
        population.get('confidence', 0),
        prediction.get('confidence', 0),
        resources.get('confidence', 0),
    ]
    confidence_consistent = all(0.85 <= c <= 0.92 for c in confidences)
    print(f"{'✓' if confidence_consistent else '✗'} Confidence scores: 0.85-0.92 range")
    print(f"  Scores: {confidences}")
    checks.append(confidence_consistent)

    all_valid = all(checks)
    print(f"\n{'✓ ALL CROSS-CHECKS PASSED' if all_valid else '✗ SOME CROSS-CHECKS FAILED'}")
    return all_valid


async def test_agents():
    """Test all agents with July 2020 scenario"""
    print("=" * 80)
    print("  JULY 2020 SCENARIO - AGENT OUTPUT VALIDATION")
    print("=" * 80)

    # Load scenario
    scenario = load_july_2020_scenario()
    print(f"\n✓ Loaded scenario: {scenario['disaster']['name']}")
    print(f"  Location: {scenario['disaster']['location']['description']}")
    print(f"  Fire size: {scenario['disaster']['fire_params']['initial_size_acres']} acres")

    results = {}
    all_valid = True

    # Test Damage Assessment Agent
    try:
        damage_agent = DamageAssessmentAgent()
        damage_result = await damage_agent.analyze({}, 'wildfire', scenario)
        results['damage'] = damage_result
        all_valid &= validate_damage_assessment(damage_result)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        all_valid = False

    # Test Population Impact Agent
    try:
        pop_agent = PopulationImpactAgent()
        pop_result = await pop_agent.analyze({}, None, scenario)
        results['population'] = pop_result
        all_valid &= validate_population_impact(pop_result)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        all_valid = False

    # Test Prediction Agent
    try:
        pred_agent = PredictionAgent()
        pred_result = await pred_agent.analyze({}, {}, scenario)
        results['prediction'] = pred_result
        all_valid &= validate_prediction(pred_result)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        all_valid = False

    # Test Routing Agent
    try:
        routing_agent = RoutingAgent()
        routing_result = await routing_agent.analyze(None, None, {}, scenario)
        results['routing'] = routing_result
        all_valid &= validate_routing(routing_result)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        all_valid = False

    # Test Resource Allocation Agent
    try:
        resource_agent = ResourceAllocationAgent()
        resource_result = await resource_agent.analyze({}, {}, None, scenario)
        results['resources'] = resource_result
        all_valid &= validate_resource_allocation(resource_result)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        all_valid = False

    # Cross-validate all results
    if results:
        all_valid &= cross_validate(results)

    # Final summary
    print_section("FINAL SUMMARY")
    print(f"\nTotal Agents Tested: 5")
    print(f"Status: {'✓ ALL TESTS PASSED' if all_valid else '✗ SOME TESTS FAILED'}")
    print(f"\nAcceptance Criteria:")
    print(f"{'✓' if all_valid else '✗'} Damage Assessment Agent tuned for 40-acre fire")
    print(f"{'✓' if all_valid else '✗'} Population Impact Agent returns realistic affected count (~2,000)")
    print(f"{'✓' if all_valid else '✗'} Prediction Agent shows HWY 407 threat within 2-3 hours")
    print(f"{'✓' if all_valid else '✗'} Routing Agent calculates reasonable evacuation times")
    print(f"{'✓' if all_valid else '✗'} Resource Allocation Agent requests realistic mutual aid")
    print(f"{'✓' if all_valid else '✗'} All numbers cross-validated for consistency")
    print(f"{'✓' if all_valid else '✗'} Confidence scores set appropriately (0.85-0.92)")

    return 0 if all_valid else 1


if __name__ == '__main__':
    exit_code = asyncio.run(test_agents())
    sys.exit(exit_code)
