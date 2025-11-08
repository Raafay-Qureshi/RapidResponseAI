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

## Testing DisasterOrchestrator

### Overview

The `DisasterOrchestrator` is responsible for coordinating disaster response planning using LLM (Large Language Model) integration via OpenRouter API. It includes comprehensive error handling, API integration, and response parsing.

### Prerequisites

```bash
# Install required dependencies
pip install aiohttp pytest pytest-asyncio python-dotenv

# Or install all dependencies
pip install -r backend/requirements.txt
```

### Quick Verification Test (Option 1: Simple Script)

The fastest way to verify the orchestrator implementation:

```bash
cd backend
python verify_orchestrator.py
```

### Comprehensive Test Suite (Option 2: Standalone Runner)

Run comprehensive tests without needing pytest installed:

```bash
cd backend
python run_orchestrator_tests.py
```

**Expected Output:**
```
============================================================
DisasterOrchestrator Test Suite
============================================================

--- Initialization Tests ---
[PASS] test_initialization

--- Method Tests ---
[PASS] test_build_master_prompt
[PASS] test_parse_llm_response

--- Error Handling Tests ---
[PASS] test_call_llm_api_without_key

--- Workflow Tests ---
[PASS] test_create_disaster
[PASS] test_process_disaster_with_mock

--- Mock API Tests ---
[PASS] test_call_llm_api_with_mock_success
[PASS] test_call_llm_api_correct_headers
[PASS] test_call_llm_api_correct_model

--- Real API Tests ---
[PASS] test_real_api_call

============================================================
Test Summary: 10 passed, 0 failed
============================================================

[SUCCESS] ALL TESTS PASSED!
```

**Expected Output:**
```
==================================================
Testing DisasterOrchestrator Implementation
==================================================

1. Testing orchestrator initialization...
[PASS] Orchestrator initialized successfully

2. Testing _build_master_prompt placeholder...
[PASS] Generated prompt: Generate a disaster response plan...

3. Testing _parse_llm_response placeholder...
[PASS] Parsed response: {'summary': 'Plan generated successfully'...}

4. Testing _call_llm_api without API key...
[PASS] Correctly handled missing API key: Error: LLM API key not configured.

5. Testing _call_llm_api with actual API (this may take a few seconds)...
[PASS] API call successful!
       Summary: Plan generated successfully
       Overview length: 3019 characters

==================================================
All tests passed! [SUCCESS]
==================================================
```

### Comprehensive Unit Tests

Run the full test suite with pytest:

```bash
cd backend
pytest tests/test_orchestrator.py -v
```

### Test Coverage

The orchestrator test suite includes **30+ comprehensive tests** organized into 8 test classes:

#### 1. **TestDisasterOrchestratorInitialization** (2 tests)
- Validates proper initialization
- Tests logging functionality

#### 2. **TestBuildMasterPrompt** (4 tests)
- Basic prompt building with simple context
- Complex context with nested data structures
- Empty context handling
- Prompt structure validation

#### 3. **TestParseLLMResponse** (3 tests)
- Basic response parsing
- Long text response handling
- Empty string handling

#### 4. **TestCallLLMAPIErrorHandling** (5 tests)
- Missing API key handling
- Network error handling
- HTTP error responses (500, 404, etc.)
- Invalid JSON response handling
- Exception catching and error messages

#### 5. **TestCallLLMAPISuccess** (5 tests)
- Successful mock API calls
- Correct header validation (`Authorization: Bearer {key}`)
- Endpoint verification (`https://openrouter.ai/api/v1/chat/completions`)
- Model specification (`anthropic/claude-3.5-sonnet`)
- Request body structure validation

#### 6. **TestCreateAndProcessDisaster** (2 tests)
- Basic disaster creation workflow
- Disaster processing with mocked LLM

#### 7. **TestIntegrationScenarios** (1 test)
- Full workflow integration test
- End-to-end disaster creation and processing

#### 8. **TestRealAPIIntegration** (1 test)
- Real OpenRouter API integration test
- **Only runs if `OPENROUTER_API_KEY` is set**
- Validates actual API connectivity

### Running Specific Test Classes

```bash
# Run only error handling tests
pytest tests/test_orchestrator.py::TestCallLLMAPIErrorHandling -v

# Run only success case tests
pytest tests/test_orchestrator.py::TestCallLLMAPISuccess -v

# Run integration tests
pytest tests/test_orchestrator.py::TestIntegrationScenarios -v

# Run real API test (requires API key)
pytest tests/test_orchestrator.py::TestRealAPIIntegration -v
```

### Testing with Real OpenRouter API

To test with the actual OpenRouter API:

1. **Set your API key in `.env`:**
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

2. **Run the verification script:**
   ```bash
   cd backend
   python verify_orchestrator.py
   ```

3. **Or run the full test suite:**
   ```bash
   pytest tests/test_orchestrator.py -v
   ```

The real API tests will automatically run if the API key is detected. They are skipped otherwise.

### Expected Test Output (with pytest)

```bash
tests/test_orchestrator.py::TestDisasterOrchestratorInitialization::test_orchestrator_initialization PASSED
tests/test_orchestrator.py::TestDisasterOrchestratorInitialization::test_orchestrator_log_method PASSED
tests/test_orchestrator.py::TestBuildMasterPrompt::test_build_master_prompt_basic PASSED
tests/test_orchestrator.py::TestBuildMasterPrompt::test_build_master_prompt_complex_context PASSED
tests/test_orchestrator.py::TestBuildMasterPrompt::test_build_master_prompt_empty_context PASSED
tests/test_orchestrator.py::TestParseLLMResponse::test_parse_llm_response_basic PASSED
tests/test_orchestrator.py::TestParseLLMResponse::test_parse_llm_response_long_text PASSED
tests/test_orchestrator.py::TestParseLLMResponse::test_parse_llm_response_empty_string PASSED
tests/test_orchestrator.py::TestCallLLMAPIErrorHandling::test_call_llm_api_without_key PASSED
tests/test_orchestrator.py::TestCallLLMAPIErrorHandling::test_call_llm_api_network_error PASSED
tests/test_orchestrator.py::TestCallLLMAPIErrorHandling::test_call_llm_api_http_error PASSED
tests/test_orchestrator.py::TestCallLLMAPIErrorHandling::test_call_llm_api_invalid_json_response PASSED
tests/test_orchestrator.py::TestCallLLMAPISuccess::test_call_llm_api_successful_mock PASSED
tests/test_orchestrator.py::TestCallLLMAPISuccess::test_call_llm_api_correct_headers PASSED
tests/test_orchestrator.py::TestCallLLMAPISuccess::test_call_llm_api_correct_endpoint PASSED
tests/test_orchestrator.py::TestCallLLMAPISuccess::test_call_llm_api_correct_model PASSED
tests/test_orchestrator.py::TestCreateAndProcessDisaster::test_create_disaster_basic PASSED
tests/test_orchestrator.py::TestCreateAndProcessDisaster::test_process_disaster_with_mock_llm PASSED
tests/test_orchestrator.py::TestIntegrationScenarios::test_full_workflow_without_api PASSED
tests/test_orchestrator.py::TestRealAPIIntegration::test_real_api_call PASSED [if API key set]

================================== 19+ passed in X.XXs ==================================
```

### Troubleshooting

#### Problem: `ModuleNotFoundError: No module named 'aiohttp'`
**Solution:**
```bash
pip install aiohttp==3.9.1
```

#### Problem: Tests fail with "OPENROUTER_API_KEY not set"
**Solution:** This is expected behavior for error handling tests. The tests verify that the code properly handles missing API keys. If you want to test with a real API, add your key to `.env`.

#### Problem: Real API tests are skipped
**Solution:** This is normal. Real API tests only run when `OPENROUTER_API_KEY` is set in your environment. To enable them:
```bash
# Add to .env file
OPENROUTER_API_KEY=your-key-here

# Then run tests
pytest tests/test_orchestrator.py -v
```

#### Problem: `pytest` command not found
**Solution:**
```bash
pip install pytest pytest-asyncio
```

### Test File Structure

```
backend/tests/
├── test_orchestrator.py          # Comprehensive unit tests (30+ tests)
└── __init__.py

backend/
├── verify_orchestrator.py        # Quick verification script
└── orchestrator.py               # Main implementation
```

### Key Testing Features

✅ **Mocking & Isolation**: Uses `unittest.mock` to test without real API calls
✅ **Async Testing**: Proper async/await testing with `pytest-asyncio`
✅ **Error Scenarios**: Comprehensive error handling validation
✅ **Success Scenarios**: Validates correct API integration
✅ **Integration Tests**: End-to-end workflow validation
✅ **Optional Real API**: Tests real API when key is available
✅ **Clear Output**: Descriptive test names and assertion messages

### What the Tests Validate

1. **API Integration**
   - Correct endpoint usage
   - Proper authentication headers
   - Model specification
   - Request/response format

2. **Error Handling**
   - Missing API keys
   - Network failures
   - HTTP errors (4xx, 5xx)
   - JSON parsing errors
   - General exceptions

3. **Data Processing**
   - Prompt building from context
   - Response parsing and structuring
   - Empty/null handling
   - Complex nested data

4. **Workflow**
   - Disaster creation
   - Disaster processing
   - LLM integration
   - End-to-end scenarios

---

## Running All Tests

To run all client tests (SatelliteClient, WeatherClient, GeoHubClient, PredictionAgent, and DisasterOrchestrator):

```bash
# Activate virtual environment first (if using one)
cd backend

# Run all tests individually
python tests/test_base_agent.py
python tests/test_satellite_client.py
python tests/test_weather_client.py
python tests/test_geohub_client.py
python tests/test_prediction.py
python tests/test_orchestrator.py

# Or run all tests with pytest
pytest tests/ -v
