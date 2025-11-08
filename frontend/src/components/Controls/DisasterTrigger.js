import React, { useState } from 'react';
import { disasterAPI } from '../../services/api';
import './DisasterTrigger.css';

function DisasterTrigger({ onTrigger, disabled }) {
  const [isTriggering, setIsTriggering] = useState(false);
  const [error, setError] = useState(null);

  const handleTrigger = async () => {
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
        metadata: {
          scenario: 'july_2020_backtest',
          description: '40-acre WUI fire at 407/410 interchange',
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

  return (
    <div className="disaster-trigger">
      <button
        onClick={handleTrigger}
        disabled={disabled || isTriggering}
        className={`trigger-button ${isTriggering ? 'loading' : ''}`}
      >
        {isTriggering ? (
          <>
            <span className="spinner-small"></span>
            Processing...
          </>
        ) : (
          <>
            🔥 Simulate July 2020 Fire
          </>
        )}
      </button>

      {error && (
        <div className="trigger-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <div className="trigger-info">
        <small>40-acre WUI fire at HWY 407/410 interchange</small>
      </div>
    </div>
  );
}

export default DisasterTrigger;