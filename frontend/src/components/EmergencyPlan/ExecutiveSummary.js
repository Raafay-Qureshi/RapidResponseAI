import React, { useState } from 'react';
import './ExecutiveSummary.css';

function ExecutiveSummary({ summary, predictions, populationImpact, compact = false }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (summary) {
      navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!summary) {
    return null;
  }

  // Extract critical timeline (first prediction)
  const criticalTimeline = predictions?.critical_arrival_times?.[0];
  const totalAffected = populationImpact?.total_affected || 0;

  // Compact view for summary panel (next to map)
  if (compact) {
    return (
      <section className="plan-section executive-summary executive-summary-compact">
        <div className="section-header">
          <h3>⚡ Executive Summary</h3>
          <button
            className={`copy-button ${copied ? 'copied' : ''}`}
            onClick={handleCopy}
            title="Copy to clipboard"
          >
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>
        </div>

        {/* Critical Alert Box */}
        <div className="critical-alert">
          <div className="alert-icon">🚨</div>
          <div className="alert-content">
            <h4 className="alert-title">CRITICAL WUI FIRE</h4>
            <p className="alert-text">{summary}</p>
          </div>
        </div>

        {/* Key Statistics */}
        <div className="executive-stats executive-stats-compact">
          <div className="stat-card critical">
            <div className="stat-icon">⏱️</div>
            <div className="stat-content">
              <span className="stat-value">
                {criticalTimeline?.hours_until_arrival || 'N/A'}h
              </span>
              <span className="stat-label">Until Impact</span>
            </div>
          </div>

          <div className="stat-card warning">
            <div className="stat-icon">👥</div>
            <div className="stat-content">
              <span className="stat-value">
                {totalAffected.toLocaleString()}
              </span>
              <span className="stat-label">People Affected</span>
            </div>
          </div>

          <div className="stat-card info">
            <div className="stat-icon">🔥</div>
            <div className="stat-content">
              <span className="stat-value">HIGH</span>
              <span className="stat-label">Threat Level</span>
            </div>
          </div>
        </div>
      </section>
    );
  }

  // Full view - only recommendations (for bottom panel)
  return (
    <section className="plan-section critical-recommendations-section">
      <div className="section-header">
        <h3>🎯 Critical Recommendations</h3>
      </div>

      <div className="recommendations-grid">
        <div className="recommendation-card priority-critical">
          <div className="recommendation-header">
            <span className="priority-badge">CRITICAL</span>
            <span className="recommendation-title">Immediate Evacuation Order</span>
          </div>
          <p className="recommendation-description">
            Issue immediate evacuation order for all residents within affected zones.
            Activate emergency notification systems and coordinate with law enforcement.
          </p>
        </div>

        <div className="recommendation-card priority-high">
          <div className="recommendation-header">
            <span className="priority-badge">HIGH</span>
            <span className="recommendation-title">Request Mutual Aid</span>
          </div>
          <p className="recommendation-description">
            Contact neighboring municipalities for additional fire suppression resources,
            personnel, and emergency equipment. Activate regional support agreements.
          </p>
        </div>

        <div className="recommendation-card priority-high">
          <div className="recommendation-header">
            <span className="priority-badge">HIGH</span>
            <span className="recommendation-title">Highway Closure Protocol</span>
          </div>
          <p className="recommendation-description">
            Proactively close HWY 407 eastbound lanes to prevent civilian exposure and
            facilitate emergency vehicle access. Coordinate with OPP.
          </p>
        </div>

        <div className="recommendation-card priority-moderate">
          <div className="recommendation-header">
            <span className="priority-badge">MODERATE</span>
            <span className="recommendation-title">Activate Emergency Shelters</span>
          </div>
          <p className="recommendation-description">
            Open designated emergency shelters at community centers. Ensure adequate
            supplies, medical support, and registration systems are in place.
          </p>
        </div>
      </div>
    </section>
  );
}

export default ExecutiveSummary;