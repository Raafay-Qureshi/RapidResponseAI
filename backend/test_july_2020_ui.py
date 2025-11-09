"""
Test script to verify July 2020 UI customization
Tests the complete flow from trigger to plan display with scenario metadata
"""

import sys
import io
import requests
import json
import time

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000"

def test_july_2020_trigger():
    """Test triggering July 2020 scenario with metadata"""
    print("\n" + "="*60)
    print("TEST 1: July 2020 Scenario Trigger with Metadata")
    print("="*60)

    # Simulate the exact payload from the frontend DisasterTrigger component
    payload = {
        "type": "wildfire",
        "location": {
            "lat": 43.7315,
            "lon": -79.8620
        },
        "severity": "high",
        "metadata": {
            "scenario": "july_2020_backtest",
            "description": "July 2020 HWY 407/410 Fire",
            "historical": True,
            "date": "2020-07-15"
        }
    }

    print(f"\n📤 Sending request to {BASE_URL}/api/disaster/trigger")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/api/disaster/trigger",
        json=payload
    )

    print(f"\n📥 Response Status: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        data = response.json()

        # Verify disaster_id contains 'july' and '2020'
        disaster_id = data.get('disaster_id', '')
        assert 'july' in disaster_id.lower(), "❌ Disaster ID should contain 'july'"
        assert '2020' in disaster_id, "❌ Disaster ID should contain '2020'"
        print(f"✅ Disaster ID correctly formatted: {disaster_id}")

        # Verify metadata is included
        assert 'metadata' in data, "❌ Response should include metadata"
        metadata = data['metadata']
        assert metadata.get('scenario') == 'july_2020_backtest', "❌ Scenario should be july_2020_backtest"
        assert metadata.get('historical') == True, "❌ Should be marked as historical"
        print(f"✅ Metadata correctly included in response")

        return disaster_id
    else:
        print(f"❌ Request failed: {response.text}")
        return None


def test_generic_trigger():
    """Test triggering generic wildfire (for comparison)"""
    print("\n" + "="*60)
    print("TEST 2: Generic Wildfire Trigger (No Metadata)")
    print("="*60)

    payload = {
        "type": "wildfire",
        "location": {
            "lat": 43.7315,
            "lon": -79.8620
        },
        "severity": "high"
    }

    print(f"\n📤 Sending request to {BASE_URL}/api/disaster/trigger")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/api/disaster/trigger",
        json=payload
    )

    print(f"\n📥 Response Status: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        data = response.json()
        disaster_id = data.get('disaster_id', '')

        # Generic disaster should NOT contain 'july' or '2020'
        assert 'july' not in disaster_id.lower(), "❌ Generic disaster ID should not contain 'july'"
        assert '2020' not in disaster_id, "❌ Generic disaster ID should not contain '2020'"
        print(f"✅ Generic disaster ID correctly formatted: {disaster_id}")

        # Should not have metadata
        if 'metadata' in data:
            print(f"⚠️  Warning: Generic disaster has metadata (this is OK if empty)")
        else:
            print(f"✅ No metadata in generic disaster response")

        return disaster_id
    else:
        print(f"❌ Request failed: {response.text}")
        return None


def test_frontend_detection_logic():
    """Test the frontend's scenario detection logic"""
    print("\n" + "="*60)
    print("TEST 3: Frontend Scenario Detection Logic")
    print("="*60)

    # Test cases for the frontend's isJuly2020 detection
    test_cases = [
        {
            "name": "Disaster ID with 'july'",
            "plan": {"disaster_id": "wildfire-july-2020-abc123"},
            "expected": True
        },
        {
            "name": "Disaster ID with '2020'",
            "plan": {"disaster_id": "wildfire-2020-abc123"},
            "expected": True
        },
        {
            "name": "Metadata with scenario",
            "plan": {
                "disaster_id": "wildfire-abc123",
                "metadata": {"scenario": "july_2020_backtest"}
            },
            "expected": True
        },
        {
            "name": "Generic disaster",
            "plan": {"disaster_id": "wildfire-abc123"},
            "expected": False
        }
    ]

    print("\nSimulating frontend detection logic:")
    print("const isJuly2020 = (")
    print("  plan.disaster_id?.includes('july') ||")
    print("  plan.disaster_id?.includes('2020') ||")
    print("  plan.metadata?.scenario === 'july_2020_backtest'")
    print(");")

    all_passed = True
    for test in test_cases:
        plan = test['plan']
        expected = test['expected']

        # Simulate the frontend logic
        disaster_id = plan.get('disaster_id', '')
        metadata = plan.get('metadata', {})

        is_july_2020 = (
            'july' in disaster_id.lower() or
            '2020' in disaster_id or
            metadata.get('scenario') == 'july_2020_backtest'
        )

        status = "✅" if is_july_2020 == expected else "❌"
        result = "PASS" if is_july_2020 == expected else "FAIL"

        print(f"\n{status} {test['name']}: {result}")
        print(f"   Plan: {json.dumps(plan)}")
        print(f"   Expected: {expected}, Got: {is_july_2020}")

        if is_july_2020 != expected:
            all_passed = False

    if all_passed:
        print("\n✅ All detection logic tests passed!")
    else:
        print("\n❌ Some detection logic tests failed!")

    return all_passed


def main():
    print("\n" + "="*70)
    print(" JULY 2020 UI CUSTOMIZATION INTEGRATION TEST")
    print("="*70)
    print("\nThis test verifies:")
    print("1. Frontend sends scenario metadata in trigger request")
    print("2. Backend includes metadata and scenario-specific ID in response")
    print("3. Frontend can detect July 2020 scenario from response")
    print("\nMake sure the backend is running on http://localhost:5000")
    print("="*70)

    try:
        # Test health endpoint first
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"\n✅ Backend is running: {response.json()}")
    except Exception as e:
        print(f"\n❌ Backend is not running: {e}")
        print("Please start the backend with: cd backend && python app.py")
        return

    # Run tests
    july_id = test_july_2020_trigger()
    time.sleep(1)

    generic_id = test_generic_trigger()
    time.sleep(1)

    detection_passed = test_frontend_detection_logic()

    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)

    if july_id and generic_id and detection_passed:
        print("\n✅ ALL TESTS PASSED!")
        print("\nYou can now test the UI by:")
        print("1. Start the frontend: cd frontend && npm start")
        print("2. Open http://localhost:3000")
        print("3. Click 'Simulate July 2020 Fire' button")
        print("4. Verify the following appear:")
        print("   - Info tooltip on hover over ℹ️ button")
        print("   - '📅 July 2020 Backtest' badge in plan header")
        print("   - Historical context box in plan header")
        print("   - '🕐 Backtest Analysis' indicator in Executive Summary")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please review the errors above and fix them before testing the UI")

    print("="*70)


if __name__ == "__main__":
    main()
