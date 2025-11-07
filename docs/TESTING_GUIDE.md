# 🧪 Testing Guide

## Testing SatelliteClient

## Option 1: Use Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv backend/venv

# Activate it
# On Windows:
backend\venv\Scripts\activate
# On Linux/Mac:
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run test
python backend/tests/test_satellite_client.py
```

## Option 2: Install with --user flag

```bash
pip install --user -r backend/requirements.txt
python backend/tests/test_satellite_client.py
```

## Option 3: Install Selectively (Skip problematic packages)

If you just need to test the SatelliteClient, you only need these packages:

```bash
pip install requests python-dotenv
python backend/tests/test_satellite_client.py
```

## Option 4: Run with WSL (if available)

Since you have WSL installed:

```bash
wsl
cd /mnt/c/Raafay/Coding/HAM
pip install requests python-dotenv
python backend/tests/test_satellite_client.py
```

## Quick Test Without Full Setup

If you just want to verify the code structure without API calls, create a simple test:

```python
# test_basic.py
from data.satellite_client import SatelliteClient

client = SatelliteClient()
print(f"✓ SatelliteClient initialized")
print(f"✓ API Key: {'Set' if client.firms_api_key else 'Not set'}")
print(f"✓ URL: {client.firms_url}")
```

Run with:
```bash
cd backend
python test_basic.py
```

---

## Testing WeatherClient

### Option 1: Use Virtual Environment (Recommended)

```bash
# Create virtual environment (if not already created)
python -m venv backend/venv

# Activate it
# On Windows:
backend\venv\Scripts\activate
# On Linux/Mac:
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run test
python backend/tests/test_weather_client.py
```

### Option 2: Install with --user flag

```bash
pip install --user -r backend/requirements.txt
python backend/tests/test_weather_client.py
```

### Option 3: Install Selectively (Skip problematic packages)

If you just need to test the WeatherClient, you only need these packages:

```bash
pip install requests python-dotenv
python backend/tests/test_weather_client.py
```

### Option 4: Run with WSL (if available)

Since you have WSL installed:

```bash
wsl
cd /mnt/c/Raafay/Coding/HAM
pip install requests python-dotenv
python backend/tests/test_weather_client.py
```

### Quick Test Without Full Setup

If you just want to verify the code structure without API calls, create a simple test:

```python
# test_weather_basic.py
from data.weather_client import WeatherClient

client = WeatherClient()
print(f"✓ WeatherClient initialized")
print(f"✓ API Key: {'Set' if client.api_key else 'Not set'}")
print(f"✓ Base URL: {client.base_url}")
```

Run with:
```bash
cd backend
python test_weather_basic.py
```

---

---

## Testing BaseAgent

The BaseAgent is an abstract base class that doesn't require any external API dependencies, making it easy to test.

### Option 1: Use Virtual Environment (Recommended)

```bash
# Create virtual environment (if not already created)
python -m venv backend/venv

# Activate it
# On Windows:
backend\venv\Scripts\activate
# On Linux/Mac:
source backend/venv/bin/activate

# No additional dependencies needed (uses only Python standard library)

# Run test
python backend/tests/test_base_agent.py
```

### Option 2: Run Directly (No Dependencies Required)

Since BaseAgent only uses Python's standard library (`abc` module), you can run the test directly:

```bash
python backend/tests/test_base_agent.py
```

### What the Tests Verify

The test suite for BaseAgent includes 6 comprehensive tests:

1. **Cannot Instantiate BaseAgent** - Verifies that the abstract class raises `TypeError` when instantiated directly
2. **Cannot Instantiate Incomplete Agent** - Verifies that classes missing the `analyze` method cannot be instantiated
3. **Can Instantiate Concrete Agent** - Verifies that properly implemented subclasses work correctly
4. **Analyze Method Works** - Tests that the async `analyze` method functions properly
5. **Log Method Works** - Tests that the `_log` helper method outputs correctly
6. **Inheritance Properties** - Verifies that all required methods and attributes are present

### Expected Output

When all tests pass, you should see:

```
============================================================
Testing BaseAgent Abstract Class
============================================================

=== Test 1: BaseAgent Cannot Be Instantiated ===
✓ PASSED: BaseAgent cannot be instantiated

=== Test 2: Incomplete Agent Cannot Be Instantiated ===
✓ PASSED: IncompleteAgent cannot be instantiated

=== Test 3: Concrete Agent Can Be Instantiated ===
✓ PASSED: ConcreteAgent instantiated successfully
  Agent name: ConcreteAgent

=== Test 4: Analyze Method Works ===
[ConcreteAgent] Running analysis
✓ PASSED: Analyze method works correctly

=== Test 5: Log Method Works ===
[ConcreteAgent] This is a test message
✓ PASSED: Log method works correctly

=== Test 6: Inheritance Properties ===
✓ PASSED: Inheritance properties are correct

============================================================
Test Summary
============================================================
Passed: 6/6
✓ ALL TESTS PASSED
============================================================
```

### Quick Test

To quickly verify the BaseAgent structure without running the full test suite:

```python
# quick_test_agent.py
from agents.base_agent import BaseAgent
from typing import Dict, Any

class MyAgent(BaseAgent):
    async def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        self._log("Hello from MyAgent!")
        return {"status": "ok"}

import asyncio
agent = MyAgent()
print(f"Agent name: {agent.name}")
result = asyncio.run(agent.analyze())
print(f"Result: {result}")
```

Run with:
```bash
cd backend
python quick_test_agent.py
```

---

## Running All Tests

To run all tests (SatelliteClient, WeatherClient, and BaseAgent):

```bash
# Activate virtual environment first (if using one)
cd backend
python tests/test_base_agent.py
python tests/test_satellite_client.py
python tests/test_weather_client.py
```