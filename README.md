# RapidResponseAI: Automated Emergency Response Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**RapidResponseAI** is a proactive, AI-powered intelligence platform designed for emergency management professionals. It autonomously detects wildfires using satellite data and generates comprehensive, actionable emergency response plans in under 60 seconds, a process that typically takes 2-3 hours of manual analysis.

This tool provides a critical head-start, enabling faster, more effective decisions that can save lives and property.

## Core Features

- **Proactive Wildfire Detection:** Automatically identifies potential wildfires using near real-time satellite thermal anomaly data from NASA FIRMS.
- **Multi-Agent AI System:** Utilizes a team of specialized AI agents that work in parallel to analyze the situation.
- **Comprehensive Response Plan Generation:** The AI agents assess damage, population impact, resource needs, and predict the fire's spread to generate a complete response strategy.
- **LLM-Powered Synthesis:** An AI Language Model synthesizes the data from all agents into a human-readable, multi-page emergency plan.
- **Real-time Dashboard:** A web-based dashboard provides a real-time map-based view of the incident, including danger zones, evacuation routes, and the full emergency plan.
- **Continuous Updates:** The system monitors the situation and provides updates every 15 minutes.
- **Historical Scenario Analysis:** Includes a "backtest" feature to simulate historical events, such as the July 2020 wildfire in Brampton, Ontario, to validate the system's effectiveness.

## System Architecture

The system is composed of a React-based frontend dashboard that communicates with a Python backend via a REST API and WebSockets for real-time updates.

The backend features a multi-agent orchestrator that coordinates the analysis and response generation process. Each agent is responsible for a specific task, and their findings are synthesized by a Large Language Model (LLM) into a complete plan.

```
┌────────────────────────────────┐
│      React Web Dashboard       │
└───────────────┬────────────────┘
                │ (REST API / WebSocket)
┌───────────────▼────────────────┐
│      Python Backend (Flask)    │
└───────────────┬────────────────┘
                │
┌───────────────▼────────────────┐
│     Orchestrator Service       │
└──────┬─────────┬─────────┬─────┘
       │         │         │
┌──────▼───┐ ┌───▼─────┐ ┌─▼───────┐
│  Agent 1 │ │ Agent 2 │ │ Agent N │
└──────────┘ └─────────┘ └─────────┘
```

## Technology Stack

- **Backend:** Python, Flask, Flask-SocketIO, Geopandas, Shapely
- **Frontend:** React, Mapbox GL JS, Socket.IO Client, Axios, Chart.js
- **AI:** OpenRouter API for Large Language Model access
- **Data Sources:** NASA FIRMS, OpenWeather, OpenStreetMap

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js and npm
- API keys for:
  - NASA FIRMS
  - OpenWeather
  - Mapbox
  - OpenRouter API

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/RapidResponseAI.git
cd RapidResponseAI
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit .env and add your REACT_APP_MAPBOX_TOKEN
```

### 4. Running the Application

1.  **Start the Backend Server:**
    ```bash
    cd backend
    python app.py
    ```

2.  **Start the Frontend Development Server:**
    ```bash
    cd frontend
    npm start
    ```

The application will be available at `http://localhost:3000`.

## Configuration

The application is configured using environment variables. See the `.env.example` files in both the `frontend` and `backend` directories for a full list of available options.

### Key Backend Variables

- `OPENROUTER_API_KEY`: For LLM access.
- `FIRMS_API_KEY`: For NASA FIRMS satellite data.
- `OPENWEATHER_API_KEY`: For weather data.
- `USE_CACHED_RESPONSES`: Set to `True` to use the demo mode.

### Key Frontend Variables

- `REACT_APP_API_URL`: The URL of the backend server.
- `REACT_APP_MAPBOX_TOKEN`: Your Mapbox access token for rendering maps.

## Running in Demo Mode

For reliable demonstrations or offline use, you can run the system in "Demo Mode." In this mode, the backend serves a pre-generated, cached response for the July 2020 historical scenario, bypassing the need for live API calls.

1.  In the `backend/.env` file, set `USE_CACHED_RESPONSES=True`.
2.  Restart the backend server.

When running in demo mode, the frontend will display a banner indicating that you are viewing cached data.

To regenerate the cached data, run the following command from the `backend` directory:
```bash
python scripts/generate_cached_july_2020.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.