# Hybrid Mode Implementation Guide

This document explains how to use the hybrid mode feature that allows switching between simulation mode (mock data) and real API mode.

## Overview

The hybrid mode implementation allows users to choose between:
1. **Simulation Mode**: Uses mock data for fast, predictable results (default)
2. **Real API Mode**: Uses actual APIs for real-world data (NASA FIRMS, OpenWeather, OpenRouter)

## Configuration

### Backend Configuration

Set the mode in `backend/.env`:

```env
# API Integration Mode
# When True, uses real APIs (NASA FIRMS, OpenWeather, OpenRouter)
# When False, uses mock/simulation data
USE_REAL_APIS=False
```

### API Keys Required for Real Mode

Ensure these are set in `backend/.env`:

```env
NASA_FIRMS_API_KEY=your_nasa_firms_key
OPENWEATHER_API_KEY=your_openweather_key
OPENROUTER_API_KEY=your_openrouter_key
MAPBOX_TOKEN=your_mapbox_token
```

## How It Works

### Backend Implementation

1. **Configuration Flag**: `USE_REAL_APIS` in `backend/utils/config.py`
2. **Orchestrator Initialization**: In `backend/app.py`, the orchestrator is conditionally initialized based on the config
3. **Mode Selection**: The `/api/disaster/trigger` endpoint accepts a `use_real_apis` parameter
4. **WebSocket Routing**: The `subscribe_disaster` WebSocket event routes to either real processing or simulation

### Frontend Implementation

1. **Mode Selector**: Added radio buttons in `DisasterTrigger` component
2. **API Status Display**: Progress bar shows real-time API fetch status
3. **Visual Indicators**: Buttons change appearance based on selected mode

## Testing

### Running Tests

1. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

2. Run the test script:
   ```bash
   cd backend
   python test_hybrid_mode.py
   ```

### Manual Testing

1. Open the frontend in a browser
2. Select "Simulation Mode" or "Real API Mode" 
3. Trigger the July 2020 fire scenario
4. Observe the differences in:
   - Processing time (simulation: ~4s, real: ~20-30s)
   - API status indicators (only shown in real mode)
   - Data accuracy (mock vs real)

## API Status Indicators

When using real API mode, the progress bar shows detailed status for each API:

- **📡 NASA FIRMS Satellite Data**: Fire perimeter and hotspot detection
- **🌤️ OpenWeather Current Conditions**: Real-time weather data
- **🔮 OpenWeather 5-Day Forecast**: Weather predictions
- **👥 Brampton GeoHub Population Data**: Population density information
- **🏢 Brampton GeoHub Infrastructure**: Critical facilities data
- **🛣️ Brampton GeoHub Road Network**: Road and evacuation route data
- **🤖 OpenRouter LLM**: AI-generated emergency response plan

Status icons:
- ⏳ Fetching data
- ✅ Success
- ⚠️ Fallback (when API fails, uses cached data)

## Troubleshooting

### Real API Mode Not Working

1. Check that `USE_REAL_APIS=True` in `.env`
2. Verify all API keys are set correctly
3. Ensure the backend server was restarted after config changes
4. Check backend logs for API errors

### API Key Issues

- **NASA FIRMS**: Register at https://nrt3.modaps.eosdis.nasa.gov/
- **OpenWeather**: Get key at https://openweathermap.org/api
- **OpenRouter**: Get key at https://openrouter.ai/
- **Mapbox**: Get token at https://account.mapbox.com/

### Performance Considerations

- Real API mode takes 15-30 seconds vs 3-4 seconds for simulation
- API rate limits may apply
- OpenRouter costs per request (~$0.01-0.10 per call)