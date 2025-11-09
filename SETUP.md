# Setup Guide

Complete setup instructions for RapidResponseAI.

## Prerequisites

- **Python:** 3.9 or higher
- **Node.js:** 16 or higher
- **Git:** For cloning the repository

## API Keys Required

| Service | URL | Purpose | Free Tier |
|---------|-----|---------|-----------|
| NASA FIRMS | https://firms.modaps.eosdis.nasa.gov/api/ | Satellite fire detection | ✅ Yes |
| OpenWeather | https://openweathermap.org/api | Weather data | ✅ Yes (1000 calls/day) |
| Mapbox | https://account.mapbox.com/ | Map visualization | ✅ Yes (50k loads/month) |
| OpenRouter | https://openrouter.ai/ | LLM API access | 💳 Paid (credit required) |

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-username/RapidResponseAI.git
cd RapidResponseAI
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `backend/.env` and add your API keys:

```env
# Required
OPENROUTER_API_KEY=your-openrouter-key-here
FIRMS_API_KEY=your-firms-key-here
OPENWEATHER_API_KEY=your-openweather-key-here

# Optional features
USE_CACHED_RESPONSES=False  # Set to True for demo mode
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
```

Edit `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_MAPBOX_TOKEN=your-mapbox-token-here
```

### 4. Verify Setup

**Start Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * WebSocket server started
```

**Start Frontend (new terminal):**
```bash
cd frontend
npm start
```

Browser should automatically open to `http://localhost:3000`

## Demo Mode Setup

For reliable demonstrations without API dependencies:

1. **Enable cached responses:**
   ```bash
   # In backend/.env
   USE_CACHED_RESPONSES=True
   ```

2. **Restart backend server**

3. **System will use pre-cached July 2020 scenario**

To regenerate cache:
```bash
cd backend
python scripts/generate_cached_july_2020.py
```

## Troubleshooting

### Port Already in Use

**Backend (Port 5000):**
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

**Frontend (Port 3000):**
```bash
# Set different port
PORT=3001 npm start
```

### Module Not Found

Ensure virtual environment is activated:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### CORS Errors

Backend should have CORS configured for `http://localhost:3000`. Check [`app.py`](backend/app.py):

```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

### Mapbox Map Not Loading

1. Verify token in `frontend/.env`
2. Check browser console for errors
3. Confirm token is valid at https://account.mapbox.com/

### API Rate Limits

If hitting rate limits during development:
- Use `USE_CACHED_RESPONSES=True` in demo mode
- Reduce update frequency in [`orchestrator.py`](backend/orchestrator.py)
- Cache responses locally

## Development Workflow

1. **Backend changes:** Restart Flask server
2. **Frontend changes:** Hot reload automatic (React)
3. **Environment changes:** Restart both servers
4. **Dependency changes:** Reinstall requirements

## Testing

**Backend:**
```bash
cd backend
pytest tests/
```

**Frontend:**
```bash
cd frontend
npm test
```

## Production Deployment

For hackathon demos:

1. **Use Demo Mode** (`USE_CACHED_RESPONSES=True`)
2. **Test on presentation machine** before demo
3. **Have offline backup** (video recording)
4. **Monitor logs** during presentation

## Next Steps

- Read [`ARCHITECTURE.md`](./ARCHITECTURE.md) for system design
- Check [`CONTRIBUTING.md`](./CONTRIBUTING.md) for development guidelines
- Review code in [`backend/`](./backend/) and [`frontend/`](./frontend/)

## Support

- **Issues:** Search existing issues or create new one
- **Questions:** Check documentation first
- **Hackathon:** Ask mentors for help

---

**Setup complete? Start the servers and try triggering a disaster scenario!** 🔥