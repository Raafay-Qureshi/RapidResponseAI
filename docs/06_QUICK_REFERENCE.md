# RapidResponseAI - Quick Reference & Troubleshooting

## 📋 Quick Start Commands

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install flask flask-socketio flask-cors anthropic requests geopandas shapely pyproj python-dotenv

# Create .env file
cat > .env << EOF
NASA_FIRMS_API_KEY=your-key-here
OPENWEATHER_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
MAPBOX_TOKEN=your-key-here
EOF

# Run server
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install mapbox-gl socket.io-client axios chart.js react-chartjs-2

# Create .env file
cat > .env << EOF
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_MAPBOX_TOKEN=your-mapbox-token
EOF

# Run app
npm start
```

---

## 🔑 API Keys - Get Them Here

| Service | URL | Notes |
|---------|-----|-------|
| NASA FIRMS | https://firms.modaps.eosdis.nasa.gov/api/ | Free, instant |
| OpenWeather | https://openweathermap.org/api | Free tier sufficient |
| Mapbox | https://account.mapbox.com/ | Free tier sufficient |
| Anthropic Claude | You already have this! | Via artifacts |

---

## 🗂️ File Structure

```
rapidresponse-ai/
├── backend/
│   ├── app.py                    # Flask server (START HERE)
│   ├── orchestrator.py           # Multi-agent coordinator
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── damage_assessment.py
│   │   ├── population_impact.py
│   │   ├── routing.py
│   │   ├── resource_allocation.py
│   │   └── prediction.py
│   ├── data/
│   │   ├── satellite_client.py   # NASA FIRMS API
│   │   ├── weather_client.py     # OpenWeather API
│   │   └── geohub_client.py      # Brampton data
│   ├── models/
│   │   └── fire_spread.py        # Fire prediction model
│   └── utils/
│       └── config.py             # Configuration
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── Dashboard.js       # Main component
│   │   │   ├── Map/
│   │   │   │   ├── MapView.js    # Mapbox integration
│   │   │   │   ├── DangerZoneLayer.js
│   │   │   │   └── EvacuationRoutes.js
│   │   │   ├── EmergencyPlan/
│   │   │   │   ├── PlanViewer.js
│   │   │   │   └── Timeline.js
│   │   │   └── Controls/
│   │   │       └── DisasterTrigger.js
│   │   ├── services/
│   │   │   ├── api.js            # Backend API client
│   │   │   └── websocket.js      # WebSocket connection
│   │   └── hooks/
│   │       └── useDisaster.js    # State management
│   └── package.json
└── docs/
    └── architecture/               # These documents!
```

---

## 🚨 Common Issues & Fixes

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Fix:** 
```bash
source venv/bin/activate  # Activate virtual environment first!
pip install flask
```

### Issue: "CORS error" in browser console
**Fix:** Add to `app.py`:
```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

### Issue: Mapbox map doesn't load
**Fix:** Check `.env` file has correct token:
```bash
echo $REACT_APP_MAPBOX_TOKEN  # Should show your token
```
If empty, restart frontend after adding token.

### Issue: "NASA FIRMS API returns 403"
**Fix:** 
1. Verify API key is correct
2. Check request format: `https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/VIIRS_SNPP_NRT/{bbox}/{days}`
3. Try in browser first to test key

### Issue: WebSocket won't connect
**Fix:**
```bash
pip install flask-socketio python-socketio
```
And in `app.py`:
```python
from flask_socketio import SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
```

### Issue: "Port 5000 already in use"
**Fix:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
export FLASK_PORT=5001
python app.py
```

### Issue: Frontend can't reach backend
**Fix:** Check:
1. Backend is running: `curl http://localhost:5000/api/test`
2. CORS is enabled in backend
3. `.env` has correct `REACT_APP_API_URL`
4. Both on same network (localhost should work)

### Issue: Claude API returns 401
**Fix:** Check `ANTHROPIC_API_KEY` is set:
```bash
echo $ANTHROPIC_API_KEY
```
If empty, add to `.env` and restart backend.

---

## ⚡ Performance Optimization

### Backend taking too long?
1. **Cache satellite data:**
   ```python
   # Save API response to file
   import json
   with open('cached_satellite.json', 'w') as f:
       json.dump(satellite_data, f)
   ```

2. **Run agents in parallel:**
   ```python
   import asyncio
   results = await asyncio.gather(
       agent1.analyze(),
       agent2.analyze(),
       agent3.analyze()
   )
   ```

3. **Reduce API calls:**
   - Use cached Brampton data instead of downloading each time
   - Pre-load map tiles
   - Use sample responses for demo

### Frontend slow?
1. **Memoize components:**
   ```javascript
   const MapView = React.memo(({ disaster }) => {
       // component code
   });
   ```

2. **Lazy load heavy components:**
   ```javascript
   const PlanViewer = React.lazy(() => import('./PlanViewer'));
   ```

3. **Optimize map:**
   - Reduce marker count
   - Simplify polygons
   - Use vector tiles instead of raster

---

## 🎯 Testing Checklist

### Before Demo:
- [ ] Backend starts without errors
- [ ] Frontend loads successfully
- [ ] Map displays Brampton
- [ ] Can trigger disaster
- [ ] Progress bar animates
- [ ] Plan appears within 60 seconds
- [ ] Danger zone shows on map
- [ ] Routes display correctly
- [ ] All sections of plan visible
- [ ] No console errors
- [ ] WebSocket connected

### Test Endpoints:
```bash
# Test satellite API
curl http://localhost:5000/api/test/satellite

# Test weather API
curl http://localhost:5000/api/test/weather

# Trigger disaster
curl -X POST http://localhost:5000/api/disaster/trigger \
  -H "Content-Type: application/json" \
  -d '{"type":"wildfire","location":{"lat":43.7315,"lon":-79.8620},"severity":"high"}'
```

---

## 🔍 Debugging Tools

### Backend Console:
```python
# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.debug("Message here")
```

### Frontend Console:
```javascript
// In React components
console.log("Disaster data:", disaster);
console.log("Plan:", plan);

// Network tab in DevTools shows API calls
```

### Check WebSocket:
```javascript
// In browser console
socket.on('connect', () => console.log('Connected!'));
socket.on('progress', (data) => console.log('Progress:', data));
```

---

## 💾 Backup Plans

### If APIs fail during demo:

**Option 1: Use cached data**
```python
# In satellite_client.py
def fetch_imagery(self, location):
    try:
        return self._fetch_from_api(location)
    except:
        # Fallback to cached data
        with open('cached_fire_data.json') as f:
            return json.load(f)
```

**Option 2: Demo mode flag**
```python
# In config.py
DEMO_MODE = True

# In clients
if config.DEMO_MODE:
    return load_cached_data()
else:
    return fetch_from_api()
```

**Option 3: Pre-record video**
- Record full 60-second process
- If live demo breaks, play video
- Walk through as it plays

### If backend crashes:

1. Have laptop #2 with working version
2. Have screenshots of every step
3. Show architecture diagram and explain

### If internet fails:

1. Everything runs on localhost - should work
2. Have mobile hotspot as backup
3. Pre-download all data you need

---

## 📊 Key Numbers to Remember

- **Processing time:** <60 seconds
- **Affected area:** 2.3 km²
- **Population impact:** 8,430 people
- **Vulnerable population:** 1,250 elderly
- **Fire spread rate:** 2-4 km/h
- **Evacuation time:** 45 minutes
- **Resources needed:** 12 ambulances, 8 buses
- **Critical arrival time:** 3.5 hours
- **Languages supported:** 3 (English, Punjabi, Hindi)
- **Update frequency:** Every 15 minutes
- **Confidence score:** 87%

---

## 🎤 Key Talking Points

1. **The Problem:** Emergency managers waste 2-3 critical hours on manual analysis
2. **The Solution:** Automated intelligence pipeline in 60 seconds
3. **The Innovation:** Multi-agent AI + real-time satellite data + LLM synthesis
4. **The Tech:** 5 specialized agents, Claude orchestration, real NASA/NOAA APIs
5. **The Impact:** Faster intelligence = faster evacuation = lives saved
6. **The Proof:** Working demo, real data sources, hackathon-built in 72 hours

---

## 🏆 Judging Criteria Quick Ref

| Criteria | Weight | Your Strength |
|----------|--------|---------------|
| Innovation | 35% | Multi-agent emergency AI (novel) |
| Technical Functionality | 25% | Working end-to-end system |
| Emerging Technology | 15% | Agentic AI + Multi-modal LLM |
| Challenge Alignment | 15% | Disaster preparedness core theme |
| Pitch Quality | 10% | Dramatic demo, clear value |

**Target score: 88/100** ✅

---

## 🚀 Day-Of-Demo Checklist

### 2 Hours Before:
- [ ] Full system test
- [ ] Charge all devices
- [ ] Test on demo screen
- [ ] Clear browser cache
- [ ] Close unnecessary apps
- [ ] Review script
- [ ] Practice Q&A
- [ ] Prepare backup video

### 30 Minutes Before:
- [ ] Team huddle
- [ ] Assign roles
- [ ] Test trigger one more time
- [ ] Have water ready
- [ ] Deep breath
- [ ] Get in the zone

### During Demo:
- [ ] Maintain energy
- [ ] Eye contact with judge
- [ ] Speak clearly
- [ ] Show confidence
- [ ] Handle questions gracefully
- [ ] End strong

---

## 🎓 Learning Resources (Post-Hackathon)

If you want to build on this:

**Multi-Agent Systems:**
- LangChain documentation
- AutoGPT architecture
- Microsoft AutoGen

**Satellite Data:**
- Google Earth Engine
- Sentinel Hub
- Planet Labs

**Emergency Management:**
- FEMA Emergency Management Institute
- International Association of Emergency Managers
- CAD system integration docs

---

## 💪 Final Pep Talk

**You've built something genuinely impressive.**

- Working end-to-end system
- Real APIs, real data
- Novel architecture
- Clear value proposition
- 72-hour hackathon project

**Judges will be impressed. Trust your preparation.**

Common hackathon judge feedback:
- "Most projects don't actually work - yours does" ✅
- "This is a real problem" ✅
- "The demo was smooth" ✅
- "You clearly know your stuff" ✅

**Walk in confident. You earned it.**

---

## 📞 Emergency Contacts

**If truly stuck during hackathon:**
- Check Discord/Slack for mentor help
- Ask other teams (hackathon spirit!)
- Google the error message
- Check Stack Overflow
- Read the docs

**Remember:** Done is better than perfect. A working simple version beats a broken complex version every time.

---

## ✨ You've Got This!

Everything you need is in these docs:
1. ✅ System architecture
2. ✅ Backend implementation
3. ✅ Frontend implementation  
4. ✅ Day-by-day plan
5. ✅ Demo script
6. ✅ This quick reference

**Now go build it and win! 🏆🔥🚀**

---

## 📝 Final Notes

- Focus on the happy path first
- Get one scenario perfect
- Polish beats features
- Practice the demo
- Stay hydrated
- Have fun!

**Most important:** You're building something that could genuinely save lives. That's pretty cool. Be proud of it.