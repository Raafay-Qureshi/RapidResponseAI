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

## Running All Tests

To run both SatelliteClient and WeatherClient tests:

```bash
# Activate virtual environment first (if using one)
cd backend
python tests/test_satellite_client.py
python tests/test_weather_client.py
python tests/test_population_impact.py
