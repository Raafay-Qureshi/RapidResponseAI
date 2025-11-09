"""
Test LLM Prompt Engineering for July 2020 Scenario
Tests the specialized prompt that emphasizes HWY 407 threat
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import orchestrator
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import DisasterOrchestrator
from scenarios.july_2020_fire import load_july_2020_scenario


async def test_llm_prompt():
    """Test the July 2020 LLM prompt and validate output"""
    print("=" * 80)
    print("Testing LLM Prompt for July 2020 Scenario")
    print("=" * 80)
    print()

    # Load scenario
    print("Loading July 2020 scenario configuration...")
    scenario = load_july_2020_scenario()
    print(f"[OK] Loaded: {scenario['disaster']['name']}")
    print()

    # Create mock agent outputs based on scenario
    # These simulate the outputs from all 5 agents
    context = {
        'disaster_type': 'wildfire',
        'location': scenario['disaster']['location'],
        'timestamp': '2020-07-15T14:30:00Z',
        'agent_outputs': {
            'damage': {
                'affected_area_km2': 0.162,
                'fire_perimeter': scenario['fire_perimeter'],
                'severity': 'high',
                'burn_severity': 'extreme',
            },
            'population': {
                'total_affected': 2000,
                'vulnerable_elderly': 280,
                'evacuation_required': True,
                'affected_demographics': {
                    'punjabi_speakers': 450,
                    'hindi_speakers': 380,
                },
            },
            'prediction': {
                'current_spread_rate_kmh': 3.8,
                'wind_driven': True,
                'critical_arrival_times': [
                    {
                        'location': 'HWY 407 Eastbound Lanes',
                        'hours_until_arrival': 2.5,
                        'confidence': 'high',
                    },
                    {
                        'location': 'Residential area (Creditview/Sandalwood)',
                        'hours_until_arrival': 3.2,
                        'confidence': 'medium',
                    },
                ],
                'weather_forecast': scenario['weather'],
            },
            'routing': {
                'evacuation_routes': [
                    {'route': 'Creditview Rd South', 'capacity': 'high'},
                    {'route': 'Highway 410 South', 'capacity': 'medium'},
                ],
                'affected_roads': ['HWY 407'],
            },
            'resource': {
                'mutual_aid_requests': [
                    {'municipality': 'Mississauga Fire', 'units': 4},
                    {'municipality': 'Caledon Fire', 'units': 2},
                ],
                'required_units': 12,
                'current_available': 6,
            },
        },
    }

    # Create orchestrator instance (without socketio for testing)
    print("Initializing DisasterOrchestrator...")
    orchestrator = DisasterOrchestrator(socketio_instance=None)
    print("[OK] Orchestrator ready")
    print()

    # Test LLM call
    print("=" * 80)
    print("Calling LLM API...")
    print("=" * 80)
    print()

    start_time = datetime.now()
    try:
        result = await orchestrator._call_llm_api(context)
        elapsed_time = (datetime.now() - start_time).total_seconds()

        print("=" * 80)
        print("EXECUTIVE SUMMARY")
        print("=" * 80)
        print(result['summary'])
        print()

        print("=" * 80)
        print("SITUATION OVERVIEW")
        print("=" * 80)
        print(result['overview'])
        print()

        print("=" * 80)
        print("COMMUNICATION TEMPLATES")
        print("=" * 80)
        try:
            print(f"EN: {result['templates']['en']}")
            print()
            print(f"PA: {result['templates']['pa']}")
            print()
            print(f"HI: {result['templates']['hi']}")
            print()
        except UnicodeEncodeError:
            # Windows console encoding issue with non-ASCII characters
            print(f"EN: {result['templates']['en']}")
            print()
            print(f"PA: [Punjabi text - {len(result['templates']['pa'])} characters]")
            print()
            print(f"HI: [Hindi text - {len(result['templates']['hi'])} characters]")
            print()

        # Validate requirements
        print("=" * 80)
        print("VALIDATION CHECKS")
        print("=" * 80)

        summary_lower = result['summary'].lower()
        overview_lower = result['overview'].lower()

        checks = [
            ("Mentions HWY 407 or Highway 407", '407' in result['summary']),
            (
                "Recommends closure",
                'closure' in summary_lower or 'close' in summary_lower,
            ),
            (
                "Urgent tone (uses CRITICAL or IMMEDIATE)",
                'CRITICAL' in result['summary'] or 'IMMEDIATE' in result['summary'],
            ),
            (
                "Mentions mutual aid",
                'mutual aid' in summary_lower
                or 'mississauga' in summary_lower
                or 'mutual aid' in overview_lower,
            ),
            ("English template exists", len(result['templates']['en']) > 0),
            (
                "English template is SMS-length (< 200 chars)",
                len(result['templates']['en']) < 200,
            ),
            ("Punjabi template exists", len(result['templates']['pa']) > 0),
            ("Hindi template exists", len(result['templates']['hi']) > 0),
            (
                "Response time < 20 seconds",
                elapsed_time < 20,
            ),
            (
                "Uses specific numbers",
                any(
                    str(num) in result['summary']
                    for num in [2000, 407, 410, 2, 3, 4]
                ),
            ),
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False

        print()
        print("=" * 80)
        print(f"Response Time: {elapsed_time:.2f} seconds")
        print("=" * 80)
        print()

        if all_passed:
            print("[SUCCESS] ALL VALIDATION CHECKS PASSED!")
            print()
            print("The LLM prompt successfully:")
            print("  - Explicitly mentions HWY 407 threat")
            print("  - Recommends proactive closure")
            print("  - Uses urgent, actionable tone")
            print("  - Includes multilingual communication templates")
            print("  - Responds within acceptable time limits")
            return True
        else:
            print("[FAILURE] SOME VALIDATION CHECKS FAILED")
            print()
            print("Consider adjusting the prompt to ensure:")
            print("  - Executive summary explicitly mentions 'HWY 407' or 'Highway 407'")
            print("  - Executive summary uses 'proactive closure' or 'immediate closure'")
            print("  - Tone is urgent with all-caps for critical items")
            print("  - Communication templates are SMS-length (140-160 chars)")
            return False

    except Exception as exc:
        elapsed_time = (datetime.now() - start_time).total_seconds()
        print(f"[ERROR] {exc}")
        print(f"Time elapsed before error: {elapsed_time:.2f} seconds")
        import traceback

        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = asyncio.run(test_llm_prompt())
    sys.exit(0 if success else 1)
