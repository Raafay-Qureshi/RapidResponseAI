# 🔥 RapidResponseAI - Automated Emergency Response Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**RapidResponseAI** is an AI-powered emergency response platform that generates comprehensive emergency plans in under 60 seconds using real-time satellite data and multi-agent AI analysis.

## 🎯 The Problem

Emergency managers currently spend 2-3 hours manually analyzing disasters to create response plans. In emergencies, every minute counts.

## 💡 Our Solution

An automated intelligence pipeline that:
- **Detects** wildfires using NASA satellite data
- **Analyzes** impact using 5 specialized AI agents
- **Generates** complete response plans via LLM synthesis
- **Updates** every 15 minutes with real-time data

**Result:** 60 seconds vs 2-3 hours = Lives saved

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- API Keys: [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/api/), [OpenWeather](https://openweathermap.org/api), [Mapbox](https://account.mapbox.com/), [OpenRouter](https://openrouter.ai/)

### Setup & Run

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your REACT_APP_MAPBOX_TOKEN
npm start
```

Access at `http://localhost:3000`

## 🏗️ Architecture

```
React Dashboard
      ↓ WebSocket/REST
Flask Backend
      ↓
Orchestrator (LLM-powered)
      ↓
5 AI Agents (parallel processing)
├─ Damage Assessment
├─ Population Impact
├─ Routing & Evacuation
├─ Resource Allocation
└─ Prediction Modeling
      ↓
Real-time Data Sources
├─ NASA FIRMS (satellite)
├─ OpenWeather (weather)
└─ OpenStreetMap (infrastructure)
```

## ✨ Key Features

- **Proactive Detection:** Automatic wildfire identification via satellite
- **Multi-Agent AI:** Parallel specialized analysis
- **60-Second Plans:** Complete emergency response in under a minute
- **Real-time Updates:** Continuous monitoring every 15 minutes
- **Interactive Dashboard:** Map visualization with danger zones & evacuation routes
- **Demo Mode:** Pre-cached historical scenarios for reliable demonstrations

## 🎮 Demo Mode

For demonstrations without live API calls:

1. Set `USE_CACHED_RESPONSES=True` in `backend/.env`
2. Restart backend server
3. System will use pre-generated July 2020 Brampton fire scenario

## 📊 Tech Stack

**Backend:** Python, Flask, Flask-SocketIO, Geopandas, Shapely  
**Frontend:** React, Mapbox GL JS, Socket.IO, Axios, Chart.js  
**AI:** OpenRouter API (LLM orchestration)  
**Data:** NASA FIRMS, OpenWeather, OpenStreetMap

## 📚 Documentation

- [`SETUP.md`](./SETUP.md) - Detailed installation & configuration
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) - System design & data flow
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) - Development guidelines

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- NASA FIRMS for satellite fire data
- OpenWeather for weather APIs
- Brampton GeoHub for local infrastructure data

---

**Built with ❤️ for emergency responders everywhere**