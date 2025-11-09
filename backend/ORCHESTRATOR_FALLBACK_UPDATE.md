# Orchestrator Fallback Update

## Changes Made

Updated the [`orchestrator.py`](orchestrator.py) to implement **try-first, fallback-on-failure** pattern for agent processing.

## Previous Behavior

The system would check `config.USE_CACHED_RESPONSES` and immediately load cached data for July 2020 scenarios, **bypassing all agent processing**.

```python
# OLD CODE (Lines 82-86)
if config.USE_CACHED_RESPONSES and is_july_2020_scenario(disaster.get('trigger', {})):
    self._log("Using cached July 2020 response (Demo Mode)")
    await self._load_cached_response(disaster_id)
    return self.active_disasters[disaster_id].get("plan")
```

## New Behavior

The system now **always attempts real agent processing first**, and only uses cached data as a fallback when processing fails.

### Key Changes:

1. **Removed early cache check** (lines 82-86)
   - System now always starts with real agent processing
   - No more bypass based on `config.USE_CACHED_RESPONSES`

2. **Enhanced error handling** (lines 180-214)
   - Catches exceptions from agent processing
   - Checks if cached fallback is available
   - Attempts to load cached data only on failure
   - Provides clear logging for each step

3. **Updated `_load_cached_response` method** (lines 578-620)
   - Added `is_fallback` parameter to distinguish fallback mode
   - Different progress messages for fallback vs demo mode
   - Marks plans loaded from cache with `_source` and `_note` fields
   - Faster loading for fallback (0.3s vs 0.5s per step)

## Flow Diagram

```
User triggers disaster
        ↓
Try: Agent Processing
    ├── Fetch data (satellite, weather, geohub)
    ├── Run 5 agents (damage, population, routing, resource, prediction)
    └── Call LLM API for synthesis
        ↓
    SUCCESS → Return generated plan
        ↓
    FAILURE → Catch exception
        ↓
    Check: Is July 2020 scenario + cached data available?
        ↓
        YES → Load cached fallback
            ↓
            SUCCESS → Return cached plan (marked as fallback)
            ↓
            FAILURE → Raise both errors
        ↓
        NO → Raise original error
```

## Error Handling Modes

### Mode 1: Successful Agent Processing
```
✓ Starting agent processing pipeline...
✓ Loading July 2020 scenario configuration
✓ Running all agents
✓ Calling LLM API
✓ Plan generated successfully
```

### Mode 2: Agent Fails, Fallback Succeeds
```
✓ Starting agent processing pipeline...
❌ Agent processing failed: [error details]
⚠️ Agent processing failed - falling back to cached data
✓ Successfully loaded cached fallback data
```

### Mode 3: Both Fail
```
✓ Starting agent processing pipeline...
❌ Agent processing failed: [error details]
⚠️ Agent processing failed - falling back to cached data
❌ Cached fallback also failed: [cache error]
❌ Both methods failed - propagating errors
```

### Mode 4: No Fallback Available
```
✓ Starting agent processing pipeline...
❌ Agent processing failed: [error details]
❌ No cached fallback available
❌ Error propagated to client
```

## Benefits

1. **More Authentic**: System always attempts real processing first
2. **Demo Safety**: Fallback ensures demos don't fail if APIs are down
3. **Transparency**: Clear logging shows when fallback is used
4. **Marked Data**: Cached plans are labeled with `_source: 'cached_fallback'`
5. **Better Testing**: Forces agent code to be exercised in all scenarios

## Configuration

The `config.USE_CACHED_RESPONSES` flag is now **ignored** - the system always attempts agent processing first. Cached data is only used when:

1. Agent processing fails (any exception)
2. Scenario is July 2020 (`is_july_2020_scenario()` returns true)
3. Cached data is available (`is_cached_data_available()` returns true)

## Example Plan Metadata

When using cached fallback, the plan includes:

```json
{
  "disaster_id": "wildfire-20251109-034523-a1b2c3d4",
  "executive_summary": "...",
  "situation_overview": "...",
  "_source": "cached_fallback",
  "_note": "Agent processing failed, using cached data",
  ...
}
```

## Testing Recommendations

1. **Test normal flow**: Verify agents run successfully with valid API keys
2. **Test fallback**: Temporarily break API keys to verify fallback works
3. **Test no fallback**: Try non-July-2020 scenario with broken APIs (should fail cleanly)
4. **Test cache unavailable**: Remove cached file and verify proper error handling

---

**Date**: 2025-11-09  
**Modified by**: Kilo Code  
**Related files**: [`backend/orchestrator.py`](orchestrator.py)