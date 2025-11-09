import React, { useState } from 'react';
import { disasterAPI } from '../../services/api';
import './DisasterTrigger.css';

function DisasterTrigger({ onTrigger, disabled }) {
  const [isTriggering, setIsTriggering] = useState(false);
  const [error, setError] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const [mode, setMode] = useState('simulation'); // 'simulation' or 'real_apis'

  const handleJuly2020Trigger = async () => {
    try {
      setIsTriggering(true);
      setError(null);

      console.log('[DisasterTrigger] Triggering July 2020 fire simulation...');

      // Configure for July 2020 HWY 407/410 fire
      const disasterData = {
        type: 'wildfire',
        location: {
          lat: 43.7315,
          lon: -79.8620, // HWY 407/410 interchange
        },
        severity: 'high',
        use_real_apis: mode === 'real_apis',
        metadata: {
          scenario: 'july_2020_backtest',
          description: 'July 2020 HWY 407/410 Fire',
          historical: true,
          date: '2020-07-15',
          mode: mode,
        },
      };

      // Call backend API
      const response = await disasterAPI.trigger(disasterData);

      console.log('[DisasterTrigger] Disaster triggered successfully:', response);

      // Notify parent component
      if (onTrigger) {
        onTrigger(response);
      }

    } catch (err) {
      console.error('[DisasterTrigger] Failed to trigger disaster:', err);
      setError(err.message || 'Failed to trigger simulation');
    } finally {
      setIsTriggering(false);
    }
  };

  const handleMarch2022Trigger = async () => {
    try {
      setIsTriggering(true);
      setError(null);

      console.log('[DisasterTrigger] Triggering March 2022 residential fire...');

      // Configure for March 27, 2022 Conestoga Drive fire
      const disasterData = {
        type: 'fire',
        subtype: 'residential',
        location: {
          lat: 43.7091,  // Kennedy Rd & Sandalwood Parkway area
          lon: -79.7358,
        },
        severity: 'critical',
        use_real_apis: mode === 'real_apis',
        metadata: {
          scenario: 'march_2022_backtest',
          description: 'March 2022 Conestoga Drive Fire',
          historical: true,
          date: '2022-03-27',
          time: '02:00',
          mode: mode,
        },
      };

      // Call backend API
      const response = await disasterAPI.trigger(disasterData);

      console.log('[DisasterTrigger] March 2022 disaster triggered successfully:', response);

      // Notify parent component
      if (onTrigger) {
        onTrigger(response);
      }

    } catch (err) {
      console.error('[DisasterTrigger] Failed to trigger March 2022 disaster:', err);
      setError(err.message || 'Failed to trigger simulation');
    } finally {
      setIsTriggering(false);
    }
  };

  const handleGenericTrigger = async () => {
    try {
      setIsTriggering(true);
      setError(null);

      console.log('[DisasterTrigger] Triggering generic wildfire...');

      const disasterData = {
        type: 'wildfire',
        location: {
          lat: 43.7315 + (Math.random() - 0.5) * 0.05,
          lon: -79.8620 + (Math.random() - 0.5) * 0.05,
        },
        severity: 'high',
        use_real_apis: mode === 'real_apis',
      };

      const response = await disasterAPI.trigger(disasterData);

      console.log('[DisasterTrigger] Generic disaster triggered:', response);

      if (onTrigger) {
        onTrigger(response);
      }

    } catch (err) {
      console.error('[DisasterTrigger] Failed to trigger disaster:', err);
      setError(err.message || 'Failed to trigger simulation');
    } finally {
      setIsTriggering(false);
    }
  };

  return (
    <div className="disaster-trigger">
      <div className="trigger-header">
        <h3>🎮 Emergency Simulation</h3>
        <div className="mode-selector">
          <label>
            <input
              type="radio"
              name="mode"
              value="simulation"
              checked={mode === 'simulation'}
              onChange={(e) => setMode(e.target.value)}
              disabled={isTriggering}
            />
            Simulation Mode
          </label>
          <label>
            <input
              type="radio"
              name="mode"
              value="real_apis"
              checked={mode === 'real_apis'}
              onChange={(e) => setMode(e.target.value)}
              disabled={isTriggering}
            />
            Real API Mode
          </label>
        </div>
        <button
          className="info-button"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          type="button"
        >
          ℹ️
        </button>

        {showTooltip && (
          <div className="scenario-tooltip">
            <h4>July 2020 Historical Fire</h4>
            <p>
              On July 15, 2020, a ~40-acre wildfire broke out at the
              HWY 407/410 interchange in Brampton. The fire required
              mutual aid from 3 municipalities and closed Highway 407.
            </p>
            <p className="tooltip-highlight">
              This simulation demonstrates how RapidResponseAI would have
              provided 30-60 minutes of advance warning before the first 911 call.
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="trigger-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <div className="trigger-controls">
        <button
          onClick={handleJuly2020Trigger}
          disabled={disabled || isTriggering}
          className={`trigger-button july-2020 ${mode === 'real_apis' ? 'real-apis-mode' : ''}`}
        >
          <span className="button-icon">🔥</span>
          <span className="button-content">
            <span className="button-title">
              {mode === 'real_apis' ? 'Trigger July 2020 Fire (Real APIs)' : 'Simulate July 2020 Fire'}
            </span>
            <span className="button-subtitle">
              {mode === 'real_apis'
                ? 'HWY 407/410 • Live Data • Real API Calls'
                : 'HWY 407/410 • 40 acres • Historical Backtest'}
            </span>
          </span>
          {isTriggering && <span className="button-spinner">⏳</span>}
        </button>

        <button
          onClick={handleMarch2022Trigger}
          disabled={disabled || isTriggering}
          className={`trigger-button march-2022 ${mode === 'real_apis' ? 'real-apis-mode' : ''}`}
        >
          <span className="button-icon">🏠</span>
          <span className="button-content">
            <span className="button-title">
              {mode === 'real_apis' ? 'Trigger March 2022 Fire (Real APIs)' : 'Simulate March 2022 Fire'}
            </span>
            <span className="button-subtitle">
              {mode === 'real_apis'
                ? 'Conestoga Dr • Live Data • Real API Calls'
                : 'Conestoga Dr • Residential • 3-Alarm Fire'}
            </span>
          </span>
          {isTriggering && <span className="button-spinner">⏳</span>}
        </button>

        {/* Optional: Add generic trigger for comparison */}
        <details className="advanced-options">
          <summary>Advanced Options</summary>
          <div className="generic-trigger">
            <select disabled={disabled || isTriggering}>
              <option value="wildfire">🔥 Generic Wildfire</option>
              <option value="flood">🌊 Generic Flood (Coming Soon)</option>
            </select>
            <button
              onClick={handleGenericTrigger}
              disabled={disabled || isTriggering}
              className={`trigger-button generic ${mode === 'real_apis' ? 'real-apis-mode' : ''}`}
            >
              {mode === 'real_apis' ? '📡 Trigger Real Event (APIs)' : '🚨 Trigger Generic Event'}
            </button>
          </div>
        </details>
      </div>

      <div className="trigger-disclaimer">
        <span className="disclaimer-icon">⚠️</span>
        <span className="disclaimer-text">
          Simulation only - No connection to real emergency systems
        </span>
      </div>
    </div>
  );
}

export default DisasterTrigger;