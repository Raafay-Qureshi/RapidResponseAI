# 🧪 Backend Tests

This directory contains all test files for the HAM backend.

## 📁 Directory Structure

```
backend/tests/
├── test_satellite_client.py  # Comprehensive API test with real data
├── test_basic.py             # Quick validation test (no dependencies)
└── sample_data/              # Sample JSON responses from APIs
    ├── sample_fire_data.json
    └── sample_fire_data_amazon_rainforest.json
```

## 🚀 Running Tests

### Quick Test (No Dependencies)

Test the code structure without external dependencies:

```bash
python backend/tests/test_basic.py
```

### Full API Test

Test with real NASA FIRMS API calls:

```bash
# Make sure you have dependencies installed
pip install requests python-dotenv

# Run the test
python backend/tests/test_satellite_client.py
```

## 📊 Test Coverage

### `test_basic.py`
- ✓ Module imports
- ✓ Class structure validation
- ✓ Method existence checks
- ✓ Client initialization
- ✓ BBOX creation logic
- ✓ CSV parsing logic
- ✓ Perimeter calculation

### `test_satellite_client.py`
- ✓ API key loading
- ✓ Real API calls to NASA FIRMS
- ✓ Multiple location testing
- ✓ Fire detection parsing
- ✓ GeoJSON polygon generation
- ✓ Data persistence (JSON files)

## 🌍 Test Locations

The comprehensive test checks these fire-prone regions:
1. **Amazon Rainforest** (Brazil)
2. **California** (USA)
3. **Australia** (Victoria)
4. **Sub-Saharan Africa** (Central region)

## 📝 Sample Data

Sample fire detection responses are saved in [`sample_data/`](sample_data/) for:
- Integration testing
- Frontend development
- Demo purposes

## 🔑 Prerequisites

Ensure your `.env` file contains:
```
NASA_FIRMS_API_KEY=your_api_key_here
```

See [`backend/.env.example`](../.env.example) for reference.