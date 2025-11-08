import React from 'react';
import './Timeline.css';

function Timeline({ predictions }) {
  if (!predictions || !predictions.critical_arrival_times) {
    return (
      <section className="plan-section">
        <h3>⏱️ Timeline Predictions</h3>
        <p className="no-data">Timeline data not available</p>
      </section>
    );
  }

  const events = predictions.critical_arrival_times;
  const factors = predictions.factors || {};
  const spreadRate = predictions.current_spread_rate_kmh || 0;

  // Sort events by time
  const sortedEvents = [...events].sort((a, b) => 
    a.hours_until_arrival - b.hours_until_arrival
  );

  const getUrgencyClass = (hours) => {
    if (hours < 3) return 'critical';
    if (hours < 6) return 'warning';
    return 'info';
  };

  const getConfidenceClass = (confidence) => {
    if (confidence === 'high') return 'confidence-high';
    if (confidence === 'medium') return 'confidence-medium';
    return 'confidence-low';
  };

  return (
    <section className="plan-section timeline-section">
      <h3>⏱️ Timeline Predictions</h3>
      
      {/* Spread Rate Banner */}
      <div className="spread-rate-banner">
        <div className="spread-icon">🔥</div>
        <div className="spread-content">
          <span className="spread-label">Current Spread Rate</span>
          <span className="spread-value">{spreadRate.toFixed(1)} km/h</span>
        </div>
      </div>

      {/* Timeline */}
      <div className="timeline">
        {sortedEvents.map((event, idx) => (
          <div 
            key={idx} 
            className={`timeline-event ${getUrgencyClass(event.hours_until_arrival)}`}
            style={{ animationDelay: `${idx * 0.1}s` }}
          >
            <div className="timeline-marker">
              <div className="marker-time">
                <span className="time-value">{event.hours_until_arrival}</span>
                <span className="time-unit">hrs</span>
              </div>
              <div className="marker-line"></div>
            </div>
            
            <div className="timeline-content">
              <h4 className="event-location">{event.location}</h4>
              <div className="event-meta">
                <span className={`confidence-badge ${getConfidenceClass(event.confidence)}`}>
                  {event.confidence?.toUpperCase() || 'N/A'} confidence
                </span>
                {event.hours_until_arrival < 3 && (
                  <span className="urgent-badge">⚠️ URGENT</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Prediction Factors */}
      <div className="prediction-factors">
        <h4 className="factors-title">📊 Key Factors Influencing Spread</h4>
        <div className="factors-grid">
          <div className="factor-card">
            <div className="factor-icon">💨</div>
            <div className="factor-content">
              <span className="factor-label">Wind Speed</span>
              <span className="factor-value">{factors.wind_speed_kmh || 0} km/h</span>
            </div>
          </div>

          <div className="factor-card">
            <div className="factor-icon">🧭</div>
            <div className="factor-content">
              <span className="factor-label">Wind Direction</span>
              <span className="factor-value">{factors.wind_direction_deg || 0}°</span>
            </div>
          </div>

          <div className="factor-card">
            <div className="factor-icon">🌡️</div>
            <div className="factor-content">
              <span className="factor-label">Temperature</span>
              <span className="factor-value">{factors.temperature_c || 0}°C</span>
            </div>
          </div>

          <div className="factor-card">
            <div className="factor-icon">💧</div>
            <div className="factor-content">
              <span className="factor-label">Humidity</span>
              <span className="factor-value">{factors.humidity_percent || 0}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Warning Note */}
      <div className="timeline-note">
        <span className="note-icon">ℹ️</span>
        <p>Predictions based on current conditions. System updates every 15 minutes with latest satellite and weather data.</p>
      </div>
    </section>
  );
}

export default Timeline;