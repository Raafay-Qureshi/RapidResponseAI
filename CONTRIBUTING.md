# Contributing Guide

Guidelines for developing and extending RapidResponseAI.

## Development Setup

Follow [`SETUP.md`](./SETUP.md) for initial installation, then:

```bash
# Install development dependencies
cd backend
pip install pytest pytest-cov black flake8

cd frontend
npm install --save-dev @testing-library/react
```

## Code Style

### Python (Backend)

**Formatting:** Black
```bash
black backend/
```

**Linting:** Flake8
```bash
flake8 backend/ --max-line-length=100
```

**Style Guidelines:**
- Use type hints where possible
- Docstrings for all public functions
- Keep functions small and focused
- Async operations for I/O

**Example:**
```python
async def fetch_satellite_data(location: dict) -> dict:
    """
    Fetch satellite thermal anomaly data for a location.
    
    Args:
        location: Dict with 'lat' and 'lon' keys
        
    Returns:
        Dict containing satellite data
    """
    # Implementation
```

### JavaScript (Frontend)

**Formatting:** Prettier
```bash
npx prettier --write frontend/src/
```

**Style Guidelines:**
- Functional components with hooks
- PropTypes for type checking
- Descriptive component names
- Keep components under 200 lines

**Example:**
```javascript
/**
 * Displays danger zone on the map
 * @param {Object} zone - GeoJSON polygon
 * @param {number} severity - 0-1 severity score
 */
const DangerZone = ({ zone, severity }) => {
  // Implementation
};
```

## Project Structure

### Adding a New Agent

1. **Create agent file:**
   ```bash
   touch backend/agents/new_agent.py
   ```

2. **Extend BaseAgent:**
   ```python
   from agents.base_agent import BaseAgent
   
   class NewAgent(BaseAgent):
       def __init__(self):
           super().__init__()
           self.name = "new_agent"
       
       async def analyze(self, data):
           # Your implementation
           return result
   ```

3. **Add to orchestrator:**
   ```python
   # In orchestrator.py
   from agents.new_agent import NewAgent
   
   self.agents['new'] = NewAgent()
   ```

4. **Write tests:**
   ```bash
   touch backend/tests/test_new_agent.py
   ```

### Adding a New Data Source

1. **Create client:**
   ```python
   # backend/data/new_client.py
   class NewDataClient:
       def __init__(self, api_key):
           self.api_key = api_key
       
       async def fetch(self, location):
           # Implementation
           return data
   ```

2. **Add to config:**
   ```python
   # backend/utils/config.py
   NEW_API_KEY = os.getenv('NEW_API_KEY')
   ```

3. **Update environment:**
   ```bash
   # backend/.env.example
   NEW_API_KEY=your-key-here
   ```

### Adding a Frontend Component

1. **Create component:**
   ```bash
   touch frontend/src/components/NewComponent/NewComponent.js
   touch frontend/src/components/NewComponent/NewComponent.css
   ```

2. **Implement component:**
   ```javascript
   import React from 'react';
   import './NewComponent.css';
   
   const NewComponent = ({ data }) => {
     return (
       <div className="new-component">
         {/* Your JSX */}
       </div>
     );
   };
   
   export default NewComponent;
   ```

3. **Add to Dashboard:**
   ```javascript
   import NewComponent from './components/NewComponent/NewComponent';
   ```

## Testing

### Backend Tests

**Run all tests:**
```bash
cd backend
pytest
```

**Run with coverage:**
```bash
pytest --cov=. --cov-report=html
```

**Test structure:**
```python
# backend/tests/test_example.py
import pytest
from agents.example import ExampleAgent

def test_example_agent_basic():
    agent = ExampleAgent()
    result = agent.analyze(test_data)
    assert result['status'] == 'success'

@pytest.mark.asyncio
async def test_example_agent_async():
    agent = ExampleAgent()
    result = await agent.fetch_data()
    assert result is not None
```

### Frontend Tests

**Run tests:**
```bash
cd frontend
npm test
```

**Test structure:**
```javascript
import { render, screen } from '@testing-library/react';
import NewComponent from './NewComponent';

test('renders component', () => {
  render(<NewComponent data={testData} />);
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `test/description` - Test updates

### Commit Messages

Format: `type: description`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Formatting changes
- `perf`: Performance improvements

**Examples:**
```bash
git commit -m "feat: add prediction confidence scores"
git commit -m "fix: resolve websocket reconnection issue"
git commit -m "docs: update setup instructions"
```

### Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Ensure all tests pass
4. Update documentation if needed
5. Submit PR with description
6. Address review feedback

## Debugging

### Backend

**Enable debug logging:**
```python
# app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Test individual agents:**
```python
# Quick test script
from agents.damage_assessment import DamageAssessmentAgent

agent = DamageAssessmentAgent()
result = agent.analyze(test_data)
print(result)
```

### Frontend

**React Developer Tools:**
- Install browser extension
- Inspect component state/props
- Track render performance

**Console debugging:**
```javascript
console.log('Disaster data:', disaster);
console.log('WebSocket state:', socket.connected);
```

## Common Tasks

### Update Dependencies

**Backend:**
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

**Frontend:**
```bash
npm update
```

### Add New Scenario

1. Create scenario file:
   ```python
   # backend/scenarios/new_scenario.py
   SCENARIO = {
       'name': 'New Scenario',
       'location': {'lat': 43.7, 'lon': -79.8},
       'type': 'wildfire',
       'severity': 'high'
   }
   ```

2. Add test:
   ```python
   # backend/tests/test_new_scenario.py
   from scenarios.new_scenario import SCENARIO
   ```

### Regenerate Cached Data

```bash
cd backend
python scripts/generate_cached_july_2020.py
```

## Performance Optimization

### Backend

**Profile code:**
```python
import cProfile
cProfile.run('orchestrator.generate_plan(disaster)')
```

**Optimize queries:**
- Use spatial indexes for GeoDataFrames
- Cache expensive calculations
- Batch API requests

### Frontend

**React optimization:**
```javascript
// Memoize expensive components
const MemoMap = React.memo(MapView);

// Lazy load heavy components
const PlanViewer = React.lazy(() => import('./PlanViewer'));
```

## API Documentation

### Endpoint Template

```python
@app.route('/api/endpoint', methods=['POST'])
def endpoint():
    """
    Brief description.
    
    Request Body:
        {
            "param1": "string",
            "param2": 123
        }
    
    Returns:
        {
            "status": "success",
            "data": {...}
        }
    
    Errors:
        400: Invalid input
        500: Server error
    """
    # Implementation
```

### WebSocket Event Template

```python
@socketio.on('event_name')
def handle_event(data):
    """
    Brief description.
    
    Input:
        data: Dict with keys...
    
    Emits:
        'response_event': Response data
    """
    # Implementation
```

## Documentation

### Code Comments

**Do:** Explain *why*, not *what*
```python
# Calculate buffer based on wind speed to account for fire spread
buffer_km = wind_speed_kmh * 0.5
```

**Don't:** State the obvious
```python
# Set variable x to 5
x = 5
```

### README Updates

When adding features, update:
- Main [`README.md`](./README.md)
- Feature-specific docs
- API documentation

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**WebSocket not connecting:**
```python
# Check CORS settings in app.py
CORS(app, origins=["http://localhost:3000"])
```

**Map not rendering:**
```javascript
// Verify Mapbox token
console.log(process.env.REACT_APP_MAPBOX_TOKEN);
```

## Resources

### Learning

- **Flask:** https://flask.palletsprojects.com/
- **React:** https://react.dev/
- **Mapbox GL JS:** https://docs.mapbox.com/mapbox-gl-js/
- **Geopandas:** https://geopandas.org/

### Tools

- **Postman:** API testing
- **React DevTools:** Component inspection
- **Python Debugger:** pdb, ipdb
- **Chrome DevTools:** Network/Console debugging

## Getting Help

1. **Check existing docs:** README, SETUP, ARCHITECTURE
2. **Search issues:** Someone may have hit same problem
3. **Review code:** Well-commented and self-documenting
4. **Ask team:** Hackathon collaboration encouraged

## Code of Conduct

- Be respectful and constructive
- Help others when you can
- Share knowledge and learnings
- Celebrate wins together

## Questions?

Create an issue or reach out to the team. We're here to help!