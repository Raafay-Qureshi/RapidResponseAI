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

## Testing PopulationImpactAgent

```bash
# Activate virtual environment first (if using one)
pip install -r backend/requirements.txt
python backend/tests/test_population_impact.py
```

The script builds synthetic census blocks, runs `PopulationImpactAgent`, and asserts that totals, vulnerable populations, language splits, and critical facilities match expectations. It prints individual checkmarks for each scenario and a final success message when all assertions pass.

---

## Testing GeoHubClient

### ⚠️ Important: Fixing GeoJSON Loading Errors

If you see "module 'fiona' has no attribute 'path'" errors, you need to install compatible versions:

**Fix the dependencies:**
```bash
# Uninstall all geo packages
pip uninstall -y geopandas shapely pyproj fiona numpy

# Install compatible versions
pip install --user "numpy<2"
pip install --user "fiona<1.10"
pip install --user geopandas shapely pyproj

# Verify installation
python -c "import geopandas; print(f'geopandas {geopandas.__version__}')"

# Run test
python backend/tests/test_geohub_client.py
```

### Option 1: Use Virtual Environment (Recommended - Clean Installation)

```bash
# Create virtual environment
python -m venv backend/venv

# Activate it
# On Windows:
backend\venv\Scripts\activate
# On Linux/Mac:
source backend/venv/bin/activate

Testing BaseAgent Abstract Class

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

Test Summary
Passed: 6/6
✓ ALL TESTS PASSED
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
# Install compatible versions
pip install "numpy<2"
pip install "fiona<1.10"
pip install geopandas shapely pyproj

# Run test
python backend/tests/test_geohub_client.py
```

### Option 2: Fix in Existing Installation (With --user flag)

```bash
# Uninstall conflicting packages
pip uninstall -y geopandas shapely pyproj numpy fiona

# Install compatible versions with --user flag
pip install --user "numpy<2"
pip install --user "fiona<1.10"
pip install --user geopandas shapely pyproj

# Run test
python backend/tests/test_geohub_client.py
```

### Option 3: Quick Test Without GeoJSON Files

If you're having dependency issues, the GeoHubClient has built-in fallback sample data. You can test it by temporarily removing the requirement:

```bash
# Just install basic dependencies
pip install --user requests python-dotenv

# The test will use fallback sample data instead of loading GeoJSON files
python backend/tests/test_geohub_client.py
```

Note: This won't test the actual GeoJSON file loading, but will test the fallback functionality.

### Option 4: Run with WSL (if available)

Since you have WSL installed:

```bash
wsl
cd /mnt/c/Raafay/Coding/HAM
pip install geopandas shapely pyproj
python backend/tests/test_geohub_client.py
```

### What the Test Does

The GeoHubClient test suite validates:
1. **Infrastructure Data Loading** - Tests loading of Brampton infrastructure (fire stations, hospitals, etc.)
2. **Population Data Loading** - Tests loading of census tract data with population statistics
3. **Roads Data Loading** - Tests loading of major roads and highways
4. **Location-Based Filtering** - Verifies data can be filtered by geographic location
5. **Data Caching** - Ensures the caching mechanism works properly
6. **Data Structure Validation** - Confirms all data has the expected schema

### Expected Output

The test will display:
- Number of infrastructure features loaded
- Population statistics (total population, vulnerable population, density)
- Road network information (capacity, lanes, road classes)
- Caching performance metrics
- Data structure validation results

---

## Testing PredictionAgent

### ⚠️ NumPy Installation Issues

If you encounter NumPy compilation errors (GCC version issues), use selective installation:

```bash
# Install core dependencies that work
pip install --user flask requests python-dotenv numpy shapely

# Then run the test
python backend/tests/test_prediction.py
```

### Option 1: Virtual Environment (Recommended - May have NumPy issues)

```bash
# Create virtual environment
python -m venv backend/venv

# Activate it
# On Windows:
backend\venv\Scripts\activate
# On Linux/Mac:
source backend/venv/bin/activate

# Try full installation (may fail on NumPy)
pip install -r backend/requirements.txt

# If NumPy fails, install selectively
pip install flask requests python-dotenv numpy shapely
python backend/tests/test_prediction.py
```

### Option 2: User Installation (Works around NumPy issues)

```bash
# Install core dependencies
pip install --user flask requests python-dotenv numpy shapely
python backend/tests/test_prediction.py
```

### Testing Fire Spread Rate Calculation (Task #24)

The `_calculate_fire_spread_rate` function has dedicated unit tests:

```bash
# Run fire spread rate tests specifically
python backend/tests/test_fire_spread_rate.py

# Or run all prediction-related tests
python backend/tests/test_prediction.py
python backend/tests/test_fire_spread_rate.py
```

**Test Coverage:**
1. **Sample Data Testing** - Validates calculation with real Toronto weather data
2. **High Wind/Low Humidity** - Tests fast spread conditions (hot, dry, windy)
3. **Low Wind/High Humidity** - Tests slow spread conditions (cool, humid, calm)
4. **Default Values** - Tests behavior with missing weather data
5. **Extreme Values** - Tests bounds checking with extreme weather conditions
6. **Formula Validation** - Verifies mathematical correctness of the spread rate formula

**Expected Test Output:**
```
......
----------------------------------------------------------------------
Ran 6 tests in 0.002s

OK
```

The test suite validates:
1. **Wildfire Analysis** - Tests the full wildfire prediction pipeline with mocked helper functions
2. **Flood Analysis** - Verifies the placeholder implementation for flood disasters
3. **Unknown Disaster Types** - Ensures proper error handling for unsupported disaster types
4. **Fire Spread Rate Calculation** - Comprehensive unit tests for the spread rate formula

### Expected Output

The test will display:
- Successful wildfire analysis with spread rate, predictions, and arrival times
- Placeholder response for flood disasters
- Error handling for unknown disaster types
- Final success message when all tests pass

---

## Running All Tests

To run all client tests (SatelliteClient, WeatherClient, GeoHubClient, and PredictionAgent):

```bash
# Activate virtual environment first (if using one)
cd backend
python tests/test_base_agent.py
python tests/test_satellite_client.py
python tests/test_weather_client.py
python tests/test_geohub_client.py
python tests/test_prediction.py
