"""
Test Prompt Structure for July 2020 Scenario
Tests that the prompt is correctly constructed with HWY 407 emphasis
This test doesn't require the OPENROUTER_API_KEY
"""

import asyncio
import json
import os
import sys

# Add parent directory to path to import orchestrator
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import DisasterOrchestrator
from scenarios.july_2020_fire import load_july_2020_scenario


def test_prompt_structure():
    """Test the July 2020 prompt structure without making API calls"""
    print("=" * 80)
    print("Testing Prompt Structure for July 2020 Scenario")
    print("=" * 80)
    print()

    # Load scenario
    print("Loading July 2020 scenario configuration...")
    scenario = load_july_2020_scenario()
    print(f"[OK] Loaded: {scenario['disaster']['name']}")
    print()

    # Create mock agent outputs based on scenario
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
                ],
            },
            'routing': {
                'evacuation_routes': [
                    {'route': 'Creditview Rd South', 'capacity': 'high'},
                ],
            },
            'resource': {
                'mutual_aid_requests': [
                    {'municipality': 'Mississauga Fire', 'units': 4},
                    {'municipality': 'Caledon Fire', 'units': 2},
                ],
            },
        },
    }

    # Create orchestrator instance
    print("Initializing DisasterOrchestrator...")
    orchestrator = DisasterOrchestrator(socketio_instance=None)
    print("[OK] Orchestrator ready")
    print()

    # Test prompt generation
    print("=" * 80)
    print("Testing July 2020 Specialized Prompt")
    print("=" * 80)
    print()

    july_2020_prompt = orchestrator._create_july_2020_prompt(context)

    print("Generated prompt successfully")
    print(f"Prompt length: {len(july_2020_prompt)} characters")
    print()

    # Validate prompt structure
    print("=" * 80)
    print("VALIDATION CHECKS")
    print("=" * 80)

    checks = [
        (
            "Mentions 'WILDLAND-URBAN INTERFACE (WUI) FIRE'",
            'WILDLAND-URBAN INTERFACE' in july_2020_prompt
            or 'WUI FIRE' in july_2020_prompt,
        ),
        ("Mentions Highway 407 or HWY 407", '407' in july_2020_prompt),
        (
            "Instructs to start with 'CRITICAL WUI FIRE AT HWY 407/410 INTERCHANGE'",
            'CRITICAL WUI FIRE AT HWY 407/410 INTERCHANGE' in july_2020_prompt,
        ),
        (
            "Instructs to recommend 'PROACTIVE CLOSURE OF HWY 407'",
            'PROACTIVE CLOSURE OF HWY 407' in july_2020_prompt
            or 'proactive closure' in july_2020_prompt.lower(),
        ),
        (
            "Mentions timeline requirement",
            'timeline' in july_2020_prompt.lower(),
        ),
        (
            "Mentions mutual aid requirement",
            'mutual aid' in july_2020_prompt.lower(),
        ),
        (
            "Specifies urgent tone requirement",
            'urgent' in july_2020_prompt.lower(),
        ),
        (
            "Requires all-caps for critical recommendations",
            'all-caps' in july_2020_prompt.lower()
            or 'ALL-CAPS' in july_2020_prompt,
        ),
        (
            "Includes multilingual template requirement (Punjabi)",
            'Punjabi' in july_2020_prompt or 'ਪੰਜਾਬੀ' in july_2020_prompt,
        ),
        (
            "Includes multilingual template requirement (Hindi)",
            'Hindi' in july_2020_prompt or 'हिंदी' in july_2020_prompt,
        ),
        (
            "Uses === delimiter format",
            '===EXECUTIVE_SUMMARY===' in july_2020_prompt,
        ),
        (
            "Includes specific formatting instructions",
            '===SITUATION_OVERVIEW===' in july_2020_prompt,
        ),
        (
            "Includes communication template sections",
            '===COMMUNICATION_EN===' in july_2020_prompt,
        ),
        (
            "Emphasizes satellite detection advantage",
            'satellite detection' in july_2020_prompt.lower(),
        ),
        (
            "Mentions life-safety critical nature",
            'life' in july_2020_prompt.lower()
            or 'Lives depend' in july_2020_prompt,
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

    # Test standard prompt for comparison
    print("Testing Standard Prompt (for non-July 2020 scenarios)")
    print("=" * 80)
    print()

    standard_context = context.copy()
    standard_context['disaster_type'] = 'earthquake'  # Different disaster type

    standard_prompt = orchestrator._create_standard_prompt(standard_context)

    standard_checks = [
        (
            "Uses ### delimiter format (not ===)",
            '### EXECUTIVE SUMMARY ###' in standard_prompt,
        ),
        (
            "Does NOT include WUI fire specific language",
            'WILDLAND-URBAN INTERFACE' not in standard_prompt,
        ),
    ]

    for check_name, passed in standard_checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("[SUCCESS] ALL PROMPT STRUCTURE CHECKS PASSED!")
        print()
        print("The July 2020 specialized prompt:")
        print("  - Correctly emphasizes HWY 407 threat")
        print("  - Instructs LLM to recommend proactive closure")
        print("  - Uses urgent, actionable tone")
        print("  - Includes multilingual requirements")
        print("  - Uses distinct formatting (===) for parsing")
        print()
        print("Next Steps:")
        print("  1. Set up OPENROUTER_API_KEY in .env file")
        print("  2. Run 'python test_llm_prompt.py' to test actual LLM response")
        return True
    else:
        print("[FAILURE] SOME PROMPT STRUCTURE CHECKS FAILED")
        print()
        print("The prompt may need adjustments to ensure:")
        print("  - All required elements are present")
        print("  - Formatting instructions are clear")
        return False


if __name__ == '__main__':
    success = test_prompt_structure()
    sys.exit(0 if success else 1)
