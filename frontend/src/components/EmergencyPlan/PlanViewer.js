import React from 'react';
import './PlanViewer.css';
import ExecutiveSummary from './ExecutiveSummary';
import Timeline from './Timeline';
import ResourceTable from './ResourceTable';
import CommunicationTemplates from './CommunicationTemplates';
import PopulationImpact from './PopulationImpact';
import CommunicationTemplates from './CommunicationTemplates';

function PlanViewer({ plan, loading }) {
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

  return (
    <div className="plan-viewer">
      {/* Plan Header */}
      <div className="plan-header">
        <div className="plan-title-section">
          <h2 className="plan-title">📋 Emergency Response Plan</h2>
          <div className="plan-badges">
            <span className="badge disaster-type">{plan.disaster_type || 'WILDFIRE'}</span>
            <span className="badge severity high">HIGH SEVERITY</span>
          </div>
        </div>
        
        <div className="plan-meta">
          <div className="meta-item">
            <span className="meta-label">Disaster ID</span>
            <span className="meta-value disaster-id">{plan.disaster_id}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Generated</span>
            <span className="meta-value">
              {plan.generated_at ? new Date(plan.generated_at).toLocaleString() : 'N/A'}
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

      {/* Plan Content - Sections will be added in subsequent tasks */}
      <div className="plan-content">
        {/* ExecutiveSummary component */}
        <ExecutiveSummary
          summary={plan.executive_summary}
          predictions={plan.timeline_predictions}
          populationImpact={plan.population_impact}
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
        <CommunicationTemplates templates={plan.communication_templates} />
        {/* Population impact will go here (Task 7.6) */}
        
      </div>
    </div>
  );
}

export default PlanViewer;
