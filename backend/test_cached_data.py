"""
Validate cached July 2020 response data structure
"""

import json
import os


def test_validate_cached_data():
    """Validate the cached data structure"""
    cache_path = os.path.join(os.path.dirname(__file__), 'cached_data', 'july_2020_response.json')

    assert os.path.exists(cache_path), f"[ERROR] Cache file not found at {cache_path}"

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("[OK] Cache file loaded successfully\n")

        # Check all required fields exist
        required_fields = ['disaster', 'plan', 'agent_outputs', 'cached_metadata']
        for field in required_fields:
            assert field in data, f"[ERROR] Missing required field: {field}"
            print(f"[OK] Field '{field}' exists")

        # Validate disaster object
        disaster_fields = ['disaster_id', 'type', 'location', 'severity', 'status']
        for field in disaster_fields:
            assert field in data['disaster'], f"[ERROR] Missing disaster field: {field}"

        print("[OK] Disaster object structure valid")

        # Validate plan object
        plan_fields = ['executive_summary', 'situation_overview', 'communication_templates']
        for field in plan_fields:
            assert field in data['plan'], f"[ERROR] Missing plan field: {field}"

        print("[OK] Plan object structure valid")

        # Check executive summary mentions HWY 407
        assert '407' in data['plan']['executive_summary'], "[WARNING] Executive summary does not mention HWY 407"
        print("[OK] Executive summary mentions HWY 407")

        # Check agent outputs
        expected_agents = ['damage_assessment', 'population_impact', 'routing', 'resource_allocation', 'predictions']
        for agent in expected_agents:
            assert agent in data['agent_outputs'], f"[ERROR] Missing agent output: {agent}"
            print(f"[OK] Agent output '{agent}' present")

        # Check multi-language templates
        languages = ['en', 'pa', 'hi']
        for lang in languages:
            assert lang in data['plan']['communication_templates'], f"[ERROR] Missing language template: {lang}"
        print("[OK] All language templates present (en, pa, hi)")

        # Check file size
        file_size_kb = os.path.getsize(cache_path) / 1024
        assert file_size_kb < 500, f"[WARNING] File size large ({file_size_kb:.1f} KB)"
        print(f"[OK] File size reasonable ({file_size_kb:.1f} KB < 500 KB)")

        # Check metadata identifies as cached
        assert data['cached_metadata'].get('purpose') == 'demo_backup', "[WARNING] Metadata purpose unclear"
        print("[OK] Metadata identifies as demo backup")

        print("\n[SUCCESS] All validation checks passed!")
        assert True

    except json.JSONDecodeError as e:
        assert False, f"[ERROR] Failed to parse JSON: {e}"
    except Exception as e:
        assert False, f"[ERROR] Validation failed: {e}"


if __name__ == '__main__':
    validate_cached_data()
