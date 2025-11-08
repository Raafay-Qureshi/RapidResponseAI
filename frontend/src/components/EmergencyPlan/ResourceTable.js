import React from 'react';
import './ResourceTable.css';

function ResourceTable({ allocation }) {
  if (!allocation) {
    return (
      <section className="plan-section">
        <h3>🚑 Resource Allocation</h3>
        <p className="no-data">Resource data not available</p>
      </section>
    );
  }

  const required = allocation.required_resources || {};
  const available = allocation.available_resources || {};
  const gaps = allocation.resource_gaps || [];

  // Provide default infrastructure if not available from backend
  const fireStations = available.fire_stations || [
    { id: 'Fire Station 202', lat: 43.7200, lon: -79.8400, trucks: 3 },
    { id: 'Fire Station 205', lat: 43.7350, lon: -79.8750, trucks: 2 },
    { id: 'Fire Station 201', lat: 43.7450, lon: -79.7800, trucks: 4 }
  ];

  const hospitals = available.hospitals || [
    { id: 'Brampton Civic Hospital', lat: 43.7315, lon: -79.7624, ambulances: 8 },
    { id: 'Peel Memorial Centre', lat: 43.6900, lon: -79.7500, ambulances: 5 }
  ];

  const policeStations = available.police_stations || [
    { id: 'Peel Police 21 Division', lat: 43.7280, lon: -79.8300, units: 12 },
    { id: 'Peel Police 22 Division', lat: 43.7100, lon: -79.7600, units: 10 }
  ];

  const calculateStatus = (requiredCount, availableCount) => {
    if (availableCount >= requiredCount) return 'sufficient';
    if (availableCount >= requiredCount * 0.7) return 'marginal';
    return 'insufficient';
  };

  const resources = [
    {
      type: 'Ambulances',
      icon: '🚑',
      required: required.ambulances || 0,
      available: hospitals.reduce((sum, h) => sum + (h.ambulances || 0), 0),
    },
    {
      type: 'Evacuation Buses',
      icon: '🚌',
      required: required.evacuation_buses || 0,
      available: required.evacuation_buses || 0,
    },
    {
      type: 'Fire Trucks',
      icon: '🚒',
      required: Math.ceil((required.personnel || 0) / 4),
      available: fireStations.reduce((sum, fs) => sum + (fs.trucks || 0), 0),
    },
    {
      type: 'Police Units',
      icon: '🚓',
      required: Math.ceil((required.personnel || 0) / 2),
      available: policeStations.reduce((sum, ps) => sum + (ps.units || 0), 0),
    },
  ];

  return (
    <section className="plan-section resource-section">
      <h3>🚑 Resource Allocation & Deployment</h3>

      {/* Resource Summary Cards */}
      <div className="resource-summary">
        {resources.map((resource, idx) => {
          const status = calculateStatus(resource.required, resource.available);
          const percentage = resource.required > 0 
            ? Math.round((resource.available / resource.required) * 100)
            : 100;

          return (
            <div key={idx} className={`resource-card ${status}`}>
              <div className="resource-icon">{resource.icon}</div>
              <div className="resource-content">
                <h4 className="resource-type">{resource.type}</h4>
                <div className="resource-numbers">
                  <span className="required-count">{resource.required}</span>
                  <span className="separator">/</span>
                  <span className="available-count">{resource.available}</span>
                </div>
                <div className="resource-label">
                  <span>Required / Available</span>
                  <span className={`status-badge ${status}`}>
                    {percentage}% {status.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Resource Gaps Alert */}
      {gaps.length > 0 && (
        <div className="resource-gaps-alert">
          <div className="gaps-icon">⚠️</div>
          <div className="gaps-content">
            <h4>Critical Resource Gaps</h4>
            <ul className="gaps-list">
              {gaps.map((gap, idx) => (
                <li key={idx}>
                  <strong>{gap.resource}:</strong> {gap.description}
                </li>
              ))}
            </ul>
            <p className="gaps-recommendation">
              <strong>Recommendation:</strong> Request mutual aid from Mississauga, Caledon, and Vaughan fire services.
            </p>
          </div>
        </div>
      )}

      {/* Deployment Locations */}
      <div className="deployment-section">
        <h4 className="deployment-title">📍 Deployment Locations</h4>
        <div className="deployment-grid">
          {fireStations.map((station, idx) => (
            <div key={idx} className="deployment-card fire-station">
              <div className="deployment-header">
                <span className="deployment-icon">🚒</span>
                <span className="deployment-name">{station.id}</span>
              </div>
              <div className="deployment-details">
                <span className="deployment-resources">{station.trucks} trucks available</span>
                <span className="deployment-coords">
                  {station.lat.toFixed(4)}, {station.lon.toFixed(4)}
                </span>
              </div>
            </div>
          ))}

          {hospitals.map((hospital, idx) => (
            <div key={idx} className="deployment-card hospital">
              <div className="deployment-header">
                <span className="deployment-icon">🏥</span>
                <span className="deployment-name">{hospital.id}</span>
              </div>
              <div className="deployment-details">
                <span className="deployment-resources">{hospital.ambulances} ambulances available</span>
                <span className="deployment-coords">
                  {hospital.lat.toFixed(4)}, {hospital.lon.toFixed(4)}
                </span>
              </div>
            </div>
          ))}

          {policeStations.map((station, idx) => (
            <div key={idx} className="deployment-card police">
              <div className="deployment-header">
                <span className="deployment-icon">🚓</span>
                <span className="deployment-name">{station.id}</span>
              </div>
              <div className="deployment-details">
                <span className="deployment-resources">{station.units} units available</span>
                <span className="deployment-coords">
                  {station.lat.toFixed(4)}, {station.lon.toFixed(4)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mutual Aid Section */}
      <div className="mutual-aid-section">
        <h4 className="mutual-aid-title">🤝 Recommended Mutual Aid</h4>
        <div className="mutual-aid-list">
          <div className="mutual-aid-item">
            <span className="municipality-name">Mississauga Fire</span>
            <span className="requested-resources">Request: 2 pumpers, 1 aerial ladder</span>
          </div>
          <div className="mutual-aid-item">
            <span className="municipality-name">Caledon Fire</span>
            <span className="requested-resources">Request: 2 pumpers, 1 tanker</span>
          </div>
          <div className="mutual-aid-item">
            <span className="municipality-name">Vaughan Fire</span>
            <span className="requested-resources">Standby: Available if needed</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default ResourceTable;