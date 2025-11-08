import React, { useState } from 'react';
import './ExecutiveSummary.css';

function ExecutiveSummary({ summary, predictions, populationImpact }) {
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

  return (
    <section className="plan-section executive-summary">
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
          <h4 className="alert-title">CRITICAL WUI FIRE - IMMEDIATE ACTION REQUIRED</h4>
          <p className="alert-text">{summary}</p>
        </div>
      </div>

      {/* Key Statistics */}
      <div className="executive-stats">
        <div className="stat-card critical">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <span className="stat-value">
              {criticalTimeline?.hours_until_arrival || 'N/A'}h
            </span>
            <span className="stat-label">Until Critical Impact</span>
            <span className="stat-detail">
              {criticalTimeline?.location || 'Primary infrastructure'}
            </span>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <span className="stat-value">
              {totalAffected.toLocaleString()}
            </span>
            <span className="stat-label">People Affected</span>
            <span className="stat-detail">Immediate evacuation zone</span>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">🔥</div>
          <div className="stat-content">
            <span className="stat-value">HIGH</span>
            <span className="stat-label">Threat Level</span>
            <span className="stat-detail">Rapidly evolving situation</span>
          </div>
        </div>
      </div>

      {/* Critical Recommendations */}
      <div className="recommendations">
        <h4 className="recommendations-title">🎯 Critical Recommendations</h4>
        <ul className="recommendations-list">
          <li className="recommendation-item priority-critical">
            <span className="priority-badge">CRITICAL</span>
            <span>Immediate evacuation order for affected zones</span>
          </li>
          <li className="recommendation-item priority-high">
            <span className="priority-badge">HIGH</span>
            <span>Request mutual aid from neighboring municipalities</span>
          </li>
          <li className="recommendation-item priority-high">
            <span className="priority-badge">HIGH</span>
            <span>Proactive closure of HWY 407 eastbound lanes</span>
          </li>
          <li className="recommendation-item priority-moderate">
            <span className="priority-badge">MODERATE</span>
            <span>Activate emergency shelters at designated locations</span>
          </li>
        </ul>
      </div>
    </section>
  );
}

export default ExecutiveSummary;