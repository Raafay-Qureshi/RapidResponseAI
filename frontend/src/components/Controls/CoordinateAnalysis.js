import React, { useState } from 'react';
import { disasterAPI } from '../../services/api';
import './CoordinateAnalysis.css';

function CoordinateAnalysis({ onTrigger, disabled }) {
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [disasterType, setDisasterType] = useState('wildfire');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);

  // Preset locations
  const presets = [
    { name: 'Brampton City Hall', lat: 43.7315, lon: -79.7624 },
    { name: 'HWY 407/410 Interchange', lat: 43.7315, lon: -79.8620 },
    { name: 'Toronto Pearson Airport', lat: 43.6777, lon: -79.6248 },
    { name: 'Downtown Brampton', lat: 43.6842, lon: -79.7606 },
  ];

  const handlePresetSelect = (preset) => {
    setLatitude(preset.lat.toString());
    setLongitude(preset.lon.toString());
    setDescription(preset.name);
  };

  const validateCoordinates = () => {
    const lat = parseFloat(latitude);
    const lon = parseFloat(longitude);

    if (isNaN(lat) || isNaN(lon)) {
      setError('Please enter valid numbers for latitude and longitude');
      return false;
    }

    if (lat < -90 || lat > 90) {
      setError('Latitude must be between -90 and 90');
      return false;
    }

    if (lon < -180 || lon > 180) {
      setError('Longitude must be between -180 and 180');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!validateCoordinates()) {
      return;
    }

    try {
      setIsSubmitting(true);

      const analysisData = {
        type: disasterType,
        location: {
          lat: parseFloat(latitude),
          lon: parseFloat(longitude),
        },
        severity: 'high',
        description: description || `Analysis at ${latitude}, ${longitude}`,
      };

      console.log('[CoordinateAnalysis] Submitting analysis request:', analysisData);
      
      const response = await disasterAPI.analyzeCoordinates(analysisData);
      
      console.log('[CoordinateAnalysis] Analysis triggered successfully:', response);

      // Notify parent component
      if (onTrigger) {
        onTrigger(response);
      }

      // Reset form
      setShowForm(false);
      setLatitude('');
      setLongitude('');
      setDescription('');

    } catch (err) {
      console.error('[CoordinateAnalysis] Failed to analyze coordinates:', err);
      setError(err.message || 'Failed to analyze coordinates');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="coordinate-analysis">
      <button
        className={`toggle-button ${showForm ? 'active' : ''}`}
        onClick={() => setShowForm(!showForm)}
        disabled={disabled || isSubmitting}
      >
        <span className="button-icon">📍</span>
        <span className="button-text">Custom Coordinates</span>
        <span className="toggle-icon">{showForm ? '▼' : '▶'}</span>
      </button>

      {showForm && (
        <div className="coordinate-form">
          <div className="form-header">
            <h4>🌍 Analyze Custom Location</h4>
            <p className="form-description">
              Enter coordinates to run full agentic analysis with live data fetching
            </p>
          </div>

          {error && (
            <div className="form-error">
              <span className="error-icon">⚠️</span>
              <span className="error-text">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-section">
              <label className="form-label">Quick Presets</label>
              <div className="preset-buttons">
                {presets.map((preset, index) => (
                  <button
                    key={index}
                    type="button"
                    className="preset-button"
                    onClick={() => handlePresetSelect(preset)}
                    disabled={disabled || isSubmitting}
                  >
                    {preset.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-section">
              <label className="form-label">
                Disaster Type
              </label>
              <select
                className="form-select"
                value={disasterType}
                onChange={(e) => setDisasterType(e.target.value)}
                disabled={disabled || isSubmitting}
              >
                <option value="wildfire">🔥 Wildfire</option>
                <option value="fire">🏠 Structure Fire</option>
                <option value="flood">🌊 Flood (Coming Soon)</option>
              </select>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">
                  Latitude
                  <span className="label-hint">(-90 to 90)</span>
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., 43.7315"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  disabled={disabled || isSubmitting}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">
                  Longitude
                  <span className="label-hint">(-180 to 180)</span>
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., -79.8620"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  disabled={disabled || isSubmitting}
                  required
                />
              </div>
            </div>

            <div className="form-section">
              <label className="form-label">
                Description (Optional)
              </label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Downtown area analysis"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={disabled || isSubmitting}
              />
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="submit-button"
                disabled={disabled || isSubmitting || !latitude || !longitude}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner">⏳</span>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <span className="button-icon">🚀</span>
                    <span>Run Full Analysis</span>
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="form-footer">
            <span className="footer-icon">ℹ️</span>
            <span className="footer-text">
              This will fetch live satellite, weather, and infrastructure data for the specified location
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default CoordinateAnalysis;