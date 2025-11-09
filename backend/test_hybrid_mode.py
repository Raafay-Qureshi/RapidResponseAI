#!/usr/bin/env python3
"""
Test script for the hybrid mode implementation.
Verifies that both simulation and real API modes work correctly.
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from utils.config import config

def test_backend_config():
    """Test that backend configuration is correct"""
    print("=== Testing Backend Configuration ===")
    print(f"USE_REAL_APIS: {config.USE_REAL_APIS}")
    print(f"DEMO_MODE: {config.DEMO_MODE}")
    print(f"USE_CACHED_RESPONSES: {config.USE_CACHED_RESPONSES}")
    
    # Check if API keys are set
    api_keys = {
        'NASA_FIRMS_API_KEY': config.NASA_FIRMS_API_KEY,
        'OPENWEATHER_API_KEY': config.OPENWEATHER_API_KEY,
        'OPENROUTER_API_KEY': config.OPENROUTER_API_KEY,
        'MAPBOX_TOKEN': config.MAPBOX_TOKEN
    }
    
    for key, value in api_keys.items():
        status = "SET" if value else "MISSING"
        print(f"{key}: {status}")
    
    print()

def test_simulation_mode():
    """Test simulation mode (default behavior)"""
    print("=== Testing Simulation Mode ===")
    
    # Trigger a July 2020 scenario with simulation mode
    url = "http://localhost:5000/api/disaster/trigger"
    payload = {
        "type": "wildfire",
        "location": {
            "lat": 43.7315,
            "lon": -79.8620
        },
        "severity": "high",
        "use_real_apis": False,  # Explicitly set to simulation mode
        "metadata": {
            "scenario": "july_2020_backtest",
            "description": "July 2020 HWY 407/410 Fire",
            "historical": True,
            "date": "2020-07-15"
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Simulation mode trigger successful")
            print(f"  Disaster ID: {data.get('disaster_id')}")
            print(f"  Mode: {data.get('mode')}")
            print(f"  Status: {data.get('status')}")
            return data.get('disaster_id')
        else:
            print(f"✗ Simulation mode trigger failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"✗ Simulation mode trigger failed: {e}")
        return None

def test_real_apis_mode():
    """Test real APIs mode"""
    print("\n=== Testing Real APIs Mode ===")
    
    # Trigger a July 2020 scenario with real APIs mode
    url = "http://localhost:5000/api/disaster/trigger"
    payload = {
        "type": "wildfire",
        "location": {
            "lat": 43.7315,
            "lon": -79.8620
        },
        "severity": "high",
        "use_real_apis": True,  # Explicitly set to real APIs mode
        "metadata": {
            "scenario": "july_2020_backtest",
            "description": "July 2020 HWY 407/410 Fire",
            "historical": True,
            "date": "2020-07-15"
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Real APIs mode trigger successful")
            print(f"  Disaster ID: {data.get('disaster_id')}")
            print(f"  Mode: {data.get('mode')}")
            print(f"  Status: {data.get('status')}")
            return data.get('disaster_id')
        else:
            print(f"✗ Real APIs mode trigger failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"✗ Real APIs mode trigger failed: {e}")
        return None

def test_config_endpoint():
    """Test the config endpoint to verify backend settings"""
    print("\n=== Testing Config Endpoint ===")
    
    url = "http://localhost:5000/api/config"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Config endpoint successful")
            print(f"  Demo mode: {data.get('demo_mode')}")
            print(f"  Cached mode: {data.get('cached_mode')}")
            print(f"  Use real APIs: {data.get('use_real_apis')}")
            print(f"  Orchestrator available: {data.get('orchestrator_available')}")
        else:
            print(f"✗ Config endpoint failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Config endpoint failed: {e}")

def main():
    """Main test function"""
    print("Hybrid Mode Implementation Test")
    print("=" * 40)
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    # Test backend configuration
    test_backend_config()
    
    # Test config endpoint
    test_config_endpoint()
    
    # Test both modes
    sim_disaster_id = test_simulation_mode()
    real_disaster_id = test_real_apis_mode()
    
    print("\n=== Test Summary ===")
    if sim_disaster_id:
        print("✓ Simulation mode working correctly")
    else:
        print("✗ Simulation mode failed")
        
    if real_disaster_id:
        print("✓ Real APIs mode working correctly")
    else:
        print("✗ Real APIs mode failed (this is expected if USE_REAL_APIS=False)")
    
    print("\nTo test real APIs mode:")
    print("1. Set USE_REAL_APIS=True in backend/.env")
    print("2. Ensure all API keys are set")
    print("3. Restart the backend server")
    print("4. Run this test again")

if __name__ == "__main__":
    main()