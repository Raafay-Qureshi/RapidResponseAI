import React from 'react';
import './PlanViewer.css';
import ExecutiveSummary from './ExecutiveSummary';
import Timeline from './Timeline';
import ResourceTable from './ResourceTable';
import CommunicationTemplates from './CommunicationTemplates';
import PopulationImpact from './PopulationImpact';

function PlanViewer({ plan, loading, section = 'summary' }) {
  if (loading) {
    return (
      <div className="plan-viewer loading">
        <div className="plan-loading">
          <div className="spinner-large"></div>
          <h3>Generating Emergency Response Plan...</h3>
          <p>AI agents analyzing situation and synthesizing intelligence</p>
        </div>
      </div>
    );
  }

  if (!plan) {
    return null;
  }

  // Summary section (top-right panel)
  if (section === 'summary') {
    return (
      <div className="plan-viewer plan-viewer-summary">
        {/* Plan Header */}
        <div className="plan-header plan-header-compact">
          <div className="plan-title-section">
            <h2 className="plan-title">📋 Response Plan</h2>
            <div className="plan-badges">
              <span className="badge disaster-type">{plan.disaster_type || 'WILDFIRE'}</span>
              <span className="badge severity high">HIGH</span>
            </div>
          </div>
          
          <div className="plan-meta plan-meta-compact">
            <div className="meta-item">
              <span className="meta-label">ID</span>
              <span className="meta-value disaster-id">{plan.disaster_id?.substring(0, 8)}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Generated</span>
              <span className="meta-value">
                {plan.generated_at ? new Date(plan.generated_at).toLocaleTimeString() : 'N/A'}
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Confidence</span>
              <span className="meta-value confidence-score">
                {plan.confidence ? `${Math.round(plan.confidence * 100)}%` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Executive Summary - Compact Version */}
        <div className="plan-content">
          <ExecutiveSummary
            summary={plan.executive_summary}
            predictions={plan.timeline_predictions}
            populationImpact={plan.population_impact}
            compact={true}
          />
        </div>
      </div>
    );
  }

  // Details section (bottom panel)
  if (section === 'details') {
    return (
      <div className="plan-viewer plan-viewer-details">
        <div className="plan-content plan-content-grid">
          {/* Critical Recommendations - Full Width */}
          <ExecutiveSummary
            summary={plan.executive_summary}
            predictions={plan.timeline_predictions}
            populationImpact={plan.population_impact}
            compact={false}
          />
          
          {/* Timeline component */}
          <Timeline predictions={plan.timeline_predictions} />
          
          {/* ResourceTable component */}
          <ResourceTable allocation={plan.resource_deployment} />
          
          {/* CommunicationTemplates component */}
          <CommunicationTemplates templates={plan.communication_templates} />
          
          {/* PopulationImpact component */}
          <PopulationImpact
            populationImpact={plan.population_impact}
            affectedAreas={plan.affected_areas}
          />
        </div>
      </div>
    );
  }

  return null;
}

export default PlanViewer;
