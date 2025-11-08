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

### Testing Timeline Predictions (Task #25)

The `_generate_timeline_predictions` function has comprehensive unit tests:

```bash
# Run timeline prediction tests specifically
python backend/tests/test_timeline_predictions.py

# Or run all prediction-related tests
python backend/tests/test_prediction.py
python backend/tests/test_fire_spread_rate.py
python backend/tests/test_timeline_predictions.py
```

**Test Coverage (12 comprehensive tests):**
1. **Structure Validation** - Ensures correct dictionary structure with hour_1, hour_3, hour_6 keys
2. **Confidence Decrease** - Verifies confidence decreases over time (0.75 - hours × 0.05)
3. **Area Increase** - Confirms predicted fire area grows with time
4. **Boundary Expansion** - Tests that GeoJSON polygons are properly expanded
5. **None Input Handling** - Validates behavior with None polygon input
6. **Different Spread Rates** - Tests predictions with varying spread rates
7. **Polygon Area Calculation** - Tests `_calculate_polygon_area` with sample data and None
8. **Polygon Expansion** - Tests `_expand_polygon` with sample data and None
9. **Distance Effect** - Verifies larger distances create larger expanded polygons
10. **Realistic Values** - Ensures predictions produce positive, increasing areas with valid confidence

**Expected Test Output:**
```
............
----------------------------------------------------------------------
Ran 12 tests in 0.007s

OK
Running test_calculate_polygon_area_with_none...
PASS: test_calculate_polygon_area_with_none
Running test_calculate_polygon_area_with_sample_data...
PASS: test_calculate_polygon_area_with_sample_data
Running test_expand_polygon_distance_effect...
PASS: test_expand_polygon_distance_effect
Running test_expand_polygon_with_none...
PASS: test_expand_polygon_with_none
Running test_expand_polygon_with_sample_data...
PASS: test_expand_polygon_with_sample_data
Running test_generate_timeline_predictions_area_increases...
PASS: test_generate_timeline_predictions_area_increases
Running test_generate_timeline_predictions_boundary_expansion...
PASS: test_generate_timeline_predictions_boundary_expansion
Running test_generate_timeline_predictions_confidence_decreases...
PASS: test_generate_timeline_predictions_confidence_decreases
Running test_generate_timeline_predictions_different_spread_rates...
PASS: test_generate_timeline_predictions_different_spread_rates
Running test_generate_timeline_predictions_structure...
PASS: test_generate_timeline_predictions_structure
Running test_generate_timeline_predictions_with_none_polygon...
PASS: test_generate_timeline_predictions_with_none_polygon
Running test_timeline_predictions_realistic_values...
PASS: test_timeline_predictions_realistic_values
```

### Testing Arrival Times at Critical Points (Task #26)

The `_calculate_arrival_times` and related functions have comprehensive unit tests:

```bash
# Run arrival time tests specifically
python backend/tests/test_arrival_times.py

# Or run all prediction-related tests
python backend/tests/test_prediction.py
python backend/tests/test_fire_spread_rate.py
python backend/tests/test_timeline_predictions.py
python backend/tests/test_arrival_times.py
```

**Test Coverage (9 comprehensive tests):**
1. **Distance Calculation** - Tests `_distance_to_boundary` with sample data and None inputs
2. **Directional Factor** - Validates wind direction effects on spread rate
3. **Critical Points** - Tests `_identify_critical_points` returns proper structure
4. **Arrival Times Structure** - Ensures correct list format with required fields
5. **Sorting** - Verifies results are sorted by arrival time
6. **None Boundary Handling** - Tests behavior with None boundary geometry
7. **Different Spread Rates** - Validates arrival times scale with spread rate
8. **Confidence Levels** - Tests confidence assignment based on time (< 6h = high, >= 6h = medium)

**Expected Test Output:**
```
.........
----------------------------------------------------------------------
Ran 9 tests in 0.003s

OK
Running test_calculate_arrival_times_confidence_levels...
PASS: test_calculate_arrival_times_confidence_levels
Running test_calculate_arrival_times_different_spread_rates...
PASS: test_calculate_arrival_times_different_spread_rates
Running test_calculate_arrival_times_sorted...
PASS: test_calculate_arrival_times_sorted
Running test_calculate_arrival_times_structure...
PASS: test_calculate_arrival_times_structure
Running test_calculate_arrival_times_with_none_boundary...
PASS: test_calculate_arrival_times_with_none_boundary
Running test_calculate_directional_factor...
PASS: test_calculate_directional_factor
Running test_distance_to_boundary_with_none...
PASS: test_distance_to_boundary_with_none
Running test_distance_to_boundary_with_sample_data...
PASS: test_distance_to_boundary_with_sample_data
Running test_identify_critical_points...
PASS: test_identify_critical_points
```

The test suite validates:
1. **Wildfire Analysis** - Tests the full wildfire prediction pipeline with mocked helper functions
2. **Flood Analysis** - Verifies the placeholder implementation for flood disasters
3. **Unknown Disaster Types** - Ensures proper error handling for unsupported disaster types
4. **Fire Spread Rate Calculation** - Comprehensive unit tests for the spread rate formula
5. **Timeline Predictions** - Tests 1, 3, and 6-hour fire spread projections
6. **Arrival Times** - Validates critical point arrival time calculations with wind effects

### Expected Output

The test will display:
- Successful wildfire analysis with spread rate, predictions, and arrival times
- Placeholder response for flood disasters
- Error handling for unknown disaster types
- Final success message when all tests pass

---

## Running All Prediction Tests

### Comprehensive Prediction Test Suite

The comprehensive test suite runs all prediction-related tests (fire spread rate, timeline predictions, and arrival times) in a single execution:

```bash
# Run all prediction tests at once
python backend/tests/test_prediction_comprehensive.py

# Or run individual test suites
python backend/tests/test_fire_spread_rate.py
python backend/tests/test_timeline_predictions.py
python backend/tests/test_arrival_times.py
```

**Comprehensive Test Coverage (27 total tests):**

**Fire Spread Rate Tests (6 tests):**
1. **Sample Data Testing** - Validates calculation with real Toronto weather data
2. **High Wind/Low Humidity** - Tests fast spread conditions (hot, dry, windy)
3. **Low Wind/High Humidity** - Tests slow spread conditions (cool, humid, calm)
4. **Default Values** - Tests behavior with missing weather data
5. **Extreme Values** - Tests bounds checking with extreme weather conditions
6. **Formula Validation** - Verifies mathematical correctness of the spread rate formula

**Timeline Predictions Tests (12 tests):**
1. **Structure Validation** - Ensures correct dictionary structure with hour_1, hour_3, hour_6 keys
2. **Confidence Decrease** - Verifies confidence decreases over time (0.75 - hours × 0.05)
3. **Area Increase** - Confirms predicted fire area grows with time
4. **Boundary Expansion** - Tests that GeoJSON polygons are properly expanded
5. **None Input Handling** - Validates behavior with None polygon input
6. **Different Spread Rates** - Tests predictions with varying spread rates
7. **Polygon Area Calculation** - Tests `_calculate_polygon_area` with sample data and None
8. **Polygon Expansion** - Tests `_expand_polygon` with sample data and None
9. **Distance Effect** - Verifies larger distances create larger expanded polygons
10. **Realistic Values** - Ensures predictions produce positive, increasing areas with valid confidence

**Arrival Times Tests (9 tests):**
1. **Distance Calculation** - Tests `_distance_to_boundary` with sample data and None inputs
2. **Directional Factor** - Validates wind direction effects on spread rate
3. **Critical Points** - Tests `_identify_critical_points` returns proper structure
4. **Arrival Times Structure** - Ensures correct list format with required fields
5. **Sorting** - Verifies results are sorted by arrival time
6. **None Boundary Handling** - Tests behavior with None boundary geometry
7. **Different Spread Rates** - Validates arrival times scale with spread rate
8. **Confidence Levels** - Tests confidence assignment based on time (< 6h = high, >= 6h = medium)

**Expected Comprehensive Test Output:**
```
=== COMPREHENSIVE PREDICTION TEST SUITE ===

test_calculate_fire_spread_rate_default_values (test_fire_spread_rate.TestFireSpreadRate.test_calculate_fire_spread_rate_default_values)
Test with empty weather dict (should use defaults). ... ok
test_calculate_fire_spread_rate_extreme_values (test_fire_spread_rate.TestFireSpreadRate.test_calculate_fire_spread_rate_extreme_values)
Test with extreme weather values (bounds testing). ... ok
test_calculate_fire_spread_rate_formula_validation (test_fire_spread_rate.TestFireSpreadRate.test_calculate_fire_spread_rate_formula_validation)
Test that the formula is calculated correctly. ... ok
test_calculate_fire_spread_rate_high_wind_low_humidity (test_fire_spread_rate.TestFireSpreadRate.test_calculate_fire_spread_rate_high_wind_low_humidity)
Test with high wind and low humidity (fast spread conditions). ... ok
test_calculate_fire_spread_rate_low_wind_high_humidity (test_fire_spread_rate.TestFireSpreadRate.test_calculate_fire_spread_rate_low_wind_high_humidity)
Test with low wind and high humidity (slow spread conditions). ... ok
test_calculate_fire_spread_rate_with_sample_data (test_fire_spread_rate.TestFireSpreadRate.test_calculate_fire_spread_rate_with_sample_data)
Test fire spread rate calculation with Toronto sample weather data. ... ok
test_calculate_polygon_area_with_none (test_timeline_predictions.TestTimelinePredictions.test_calculate_polygon_area_with_none)
Test polygon area calculation with None input. ... Running test_calculate_polygon_area_with_none...
PASS: test_calculate_polygon_area_with_none
ok
test_calculate_polygon_area_with_sample_data (test_timeline_predictions.TestTimelinePredictions.test_calculate_polygon_area_with_sample_data)
Test polygon area calculation with sample data. ... Running test_calculate_polygon_area_with_sample_data...
PASS: test_calculate_polygon_area_with_sample_data
ok
test_expand_polygon_distance_effect (test_timeline_predictions.TestTimelinePredictions.test_expand_polygon_distance_effect)
Test that larger distances create larger polygons. ... Running test_expand_polygon_distance_effect...
PASS: test_expand_polygon_distance_effect
ok
test_expand_polygon_with_none (test_timeline_predictions.TestTimelinePredictions.test_expand_polygon_with_none)
Test polygon expansion with None input. ... Running test_expand_polygon_with_none...
PASS: test_expand_polygon_with_none
ok
test_expand_polygon_with_sample_data (test_timeline_predictions.TestTimelinePredictions.test_expand_polygon_with_sample_data)
Test polygon expansion with sample data. ... Running test_expand_polygon_with_sample_data...
PASS: test_expand_polygon_with_sample_data
ok
test_generate_timeline_predictions_area_increases (test_timeline_predictions.TestTimelinePredictions.test_generate_timeline_predictions_area_increases)
Test that predicted area increases with time. ... Running test_generate_timeline_predictions_area_increases...
PASS: test_generate_timeline_predictions_area_increases
ok
test_generate_timeline_predictions_boundary_expansion (test_timeline_predictions.TestTimelinePredictions.test_generate_timeline_predictions_boundary_expansion)
Test that boundaries are properly expanded. ... Running test_generate_timeline_predictions_boundary_expansion...
PASS: test_generate_timeline_predictions_boundary_expansion
ok
test_generate_timeline_predictions_confidence_decreases (test_timeline_predictions.TestTimelinePredictions.test_generate_timeline_predictions_confidence_decreases)
Test that confidence decreases with time. ... Running test_generate_timeline_predictions_confidence_decreases...
PASS: test_generate_timeline_predictions_confidence_decreases
ok
test_generate_timeline_predictions_different_spread_rates (test_timeline_predictions.TestTimelinePredictions.test_generate_timeline_predictions_different_spread_rates)
Test predictions with different spread rates. ... Running test_generate_timeline_predictions_different_spread_rates...
PASS: test_generate_timeline_predictions_different_spread_rates
ok
test_generate_timeline_predictions_structure (test_timeline_predictions.TestTimelinePredictions.test_generate_timeline_predictions_structure)
Test that timeline predictions return correct structure. ... Running test_generate_timeline_predictions_structure...
PASS: test_generate_timeline_predictions_structure
ok
test_generate_timeline_predictions_with_none_polygon (test_timeline_predictions.TestTimelinePredictions.test_generate_timeline_predictions_with_none_polygon)
Test behavior with None polygon input. ... Running test_generate_timeline_predictions_with_none_polygon...
PASS: test_generate_timeline_predictions_with_none_polygon
ok
test_timeline_predictions_realistic_values (test_timeline_predictions.TestTimelinePredictions.test_timeline_predictions_realistic_values)
Test that predictions produce realistic fire spread values. ... Running test_timeline_predictions_realistic_values...
PASS: test_timeline_predictions_realistic_values
ok
test_calculate_arrival_times_confidence_levels (test_arrival_times.TestArrivalTimes.test_calculate_arrival_times_confidence_levels)
Test that confidence levels are assigned correctly. ... Running test_calculate_arrival_times_confidence_levels...
PASS: test_calculate_arrival_times_confidence_levels
ok
test_calculate_arrival_times_different_spread_rates (test_arrival_times.TestArrivalTimes.test_calculate_arrival_times_different_spread_rates)
Test arrival times with different spread rates. ... Running test_calculate_arrival_times_different_spread_rates...
PASS: test_calculate_arrival_times_different_spread_rates
ok
test_calculate_arrival_times_sorted (test_arrival_times.TestArrivalTimes.test_calculate_arrival_times_sorted)
Test that arrival times are sorted by time. ... Running test_calculate_arrival_times_sorted...
PASS: test_calculate_arrival_times_sorted
ok
test_calculate_arrival_times_structure (test_arrival_times.TestArrivalTimes.test_calculate_arrival_times_structure)
Test that arrival times return correct structure. ... Running test_calculate_arrival_times_structure...
PASS: test_calculate_arrival_times_structure
ok
test_calculate_arrival_times_with_none_boundary (test_arrival_times.TestArrivalTimes.test_calculate_arrival_times_with_none_boundary)
Test behavior with None boundary input. ... Running test_calculate_arrival_times_with_none_boundary...
PASS: test_calculate_arrival_times_with_none_boundary
ok
test_calculate_directional_factor (test_arrival_times.TestArrivalTimes.test_calculate_directional_factor)
Test directional factor calculation. ... Running test_calculate_directional_factor...
PASS: test_calculate_directional_factor
ok
test_distance_to_boundary_with_none (test_arrival_times.TestArrivalTimes.test_distance_to_boundary_with_none)
Test distance calculation with None input. ... Running test_distance_to_boundary_with_none...
PASS: test_distance_to_boundary_with_none
ok
test_distance_to_boundary_with_sample_data (test_arrival_times.TestArrivalTimes.test_distance_to_boundary_with_sample_data)
Test distance calculation with sample data. ... Running test_distance_to_boundary_with_sample_data...
PASS: test_distance_to_boundary_with_sample_data
ok
test_identify_critical_points (test_arrival_times.TestArrivalTimes.test_identify_critical_points)
Test critical points identification. ... Running test_identify_critical_points...
PASS: test_identify_critical_points
ok

----------------------------------------------------------------------
Ran 27 tests in 0.015s

OK

=== COMPREHENSIVE TEST SUMMARY ===
Tests run: 27
Failures: 0
Errors: 0
PASS: ALL COMPREHENSIVE PREDICTION TESTS PASSED
ok

----------------------------------------------------------------------
Ran 1 test in 0.016s

OK
```

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
