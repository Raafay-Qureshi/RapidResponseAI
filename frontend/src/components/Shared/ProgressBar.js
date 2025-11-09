import React, { useState, useEffect } from 'react';
import './ProgressBar.css';

function ProgressBar({ progress = 0, message = '', estimatedTimeSeconds = 60 }) {
  const [displayProgress, setDisplayProgress] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(estimatedTimeSeconds);

  // Update progress immediately without delay
  useEffect(() => {
    setDisplayProgress(progress);
  }, [progress]);

  // Calculate time remaining
  useEffect(() => {
    if (progress > 0) {
      const elapsed = (progress / 100) * estimatedTimeSeconds;
      const remaining = Math.max(0, estimatedTimeSeconds - elapsed);
      setTimeRemaining(Math.ceil(remaining));
    }
  }, [progress, estimatedTimeSeconds]);

  // Get progress stage for styling
  const getProgressStage = () => {
    if (progress < 25) return 'starting';
    if (progress < 50) return 'processing';
    if (progress < 75) return 'analyzing';
    return 'finalizing';
  };

  const progressStage = getProgressStage();

  return (
    <div className="progress-bar-wrapper">
      <div className="progress-bar-container">
        {/* Progress Bar */}
        <div className="progress-bar-track">
          <div 
            className={`progress-bar-fill ${progressStage}`}
            style={{ width: `${displayProgress}%` }}
          >
            <div className="progress-bar-glow"></div>
          </div>
          
          {/* Progress markers */}
          <div className="progress-markers">
            <span className="marker" style={{ left: '25%' }}>25%</span>
            <span className="marker" style={{ left: '50%' }}>50%</span>
            <span className="marker" style={{ left: '75%' }}>75%</span>
          </div>
        </div>

        {/* Progress Info */}
        <div className="progress-info">
          <div className="progress-left">
            <span className="progress-percentage">{Math.round(displayProgress)}%</span>
            <span className="progress-message">{message}</span>
          </div>
          
          <div className="progress-right">
            <span className="progress-timer">
              ⏱️ ~{timeRemaining}s remaining
            </span>
          </div>
        </div>

        {/* Phase Indicators */}
        <div className="progress-phases">
          <div className={`phase-indicator ${progress >= 0 ? 'active' : ''} ${progress >= 25 ? 'complete' : ''}`}>
            <span className="phase-icon">📡</span>
            <span className="phase-label">Data Ingestion</span>
          </div>
          <div className={`phase-indicator ${progress >= 25 ? 'active' : ''} ${progress >= 50 ? 'complete' : ''}`}>
            <span className="phase-icon">🤖</span>
            <span className="phase-label">AI Analysis</span>
          </div>
          <div className={`phase-indicator ${progress >= 50 ? 'active' : ''} ${progress >= 75 ? 'complete' : ''}`}>
            <span className="phase-icon">🔮</span>
            <span className="phase-label">Predictions</span>
          </div>
          <div className={`phase-indicator ${progress >= 75 ? 'active' : ''} ${progress >= 100 ? 'complete' : ''}`}>
            <span className="phase-icon">📋</span>
            <span className="phase-label">Plan Generation</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProgressBar;