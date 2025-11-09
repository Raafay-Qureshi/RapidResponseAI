import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';

/**
 * Markers Component
 * Displays critical facilities on the map with custom icons and popups
 */
function Markers({ map, facilities, dangerZone }) {
  const markersRef = useRef([]);

  useEffect(() => {
    if (!map || !facilities || facilities.length === 0) {
      console.log('[Markers] No facilities to display');
      return;
    }

    console.log('[Markers] Adding facility markers to map', facilities);

    // Add marker styles
    addMarkerStyles();

    // Create markers for each facility
    const markers = facilities.map(facility => 
      createFacilityMarker(map, facility, dangerZone)
    );

    markersRef.current = markers;

    // Cleanup
    return () => {
      console.log('[Markers] Cleaning up facility markers');
      markers.forEach(marker => marker.remove());
      markersRef.current = [];
    };
  }, [map, facilities, dangerZone]);

  return null;
}

/**
 * Create a marker for a facility
 */
function createFacilityMarker(map, facility, dangerZone) {
  const config = getFacilityConfig(facility.type);
  const isInDanger = checkIfInDangerZone(facility.location, dangerZone);

  // Create marker element
  const el = document.createElement('div');
  el.className = `facility-marker ${facility.type} ${isInDanger ? 'in-danger' : ''}`;
  el.innerHTML = `
    <div class="marker-container">
      <div class="marker-icon-wrapper" style="background-color: ${config.color}">
        <span class="marker-icon">${config.icon}</span>
      </div>
      ${isInDanger ? '<div class="danger-indicator">⚠️</div>' : ''}
      <div class="marker-pulse" style="border-color: ${config.color}"></div>
    </div>
  `;

  // Create popup
  const popup = new mapboxgl.Popup({ 
    offset: 25,
    className: 'facility-popup',
  }).setHTML(createPopupHTML(facility, config, isInDanger));

  // Create marker
  const marker = new mapboxgl.Marker(el)
    .setLngLat([facility.location.lon, facility.location.lat])
    .setPopup(popup)
    .addTo(map);

  // Add click handler for additional interactivity
  el.addEventListener('click', () => {
    console.log('[Markers] Facility clicked:', facility.name);
    // Could trigger additional actions like flying to location
  });

  return marker;
}

/**
 * Get configuration for facility type
 */
function getFacilityConfig(type) {
  const configs = {
    elementary_school: {
      icon: '🏫',
      color: '#FF9800',
      label: 'Elementary School',
      priority: 'high',
    },
    high_school: {
      icon: '🎓',
      color: '#FF9800',
      label: 'High School',
      priority: 'high',
    },
    hospital: {
      icon: '🏥',
      color: '#f44336',
      label: 'Hospital',
      priority: 'critical',
    },
    senior_center: {
      icon: '👴',
      color: '#9C27B0',
      label: 'Senior Center',
      priority: 'critical',
    },
    daycare: {
      icon: '👶',
      color: '#FF9800',
      label: 'Daycare',
      priority: 'high',
    },
    care_home: {
      icon: '🏥',
      color: '#9C27B0',
      label: 'Care Home',
      priority: 'critical',
    },
    fire_station: {
      icon: '🚒',
      color: '#f44336',
      label: 'Fire Station',
      priority: 'resource',
    },
    police_station: {
      icon: '🚓',
      color: '#2196F3',
      label: 'Police Station',
      priority: 'resource',
    },
    shelter: {
      icon: '🏠',
      color: '#4CAF50',
      label: 'Emergency Shelter',
      priority: 'safe',
    },
    default: {
      icon: '📍',
      color: '#607D8B',
      label: 'Facility',
      priority: 'normal',
    },
  };

  return configs[type] || configs.default;
}

/**
 * Create popup HTML for a facility
 */
function createPopupHTML(facility, config, isInDanger) {
  return `
    <div class="facility-popup-content">
      <div class="popup-header">
        <span class="popup-icon" style="background-color: ${config.color}">
          ${config.icon}
        </span>
        <div class="popup-title-section">
          <h3 class="popup-title">${facility.name}</h3>
          <p class="popup-type">${config.label}</p>
        </div>
      </div>
      
      ${isInDanger ? `
        <div class="popup-danger-alert">
          <span class="alert-icon">⚠️</span>
          <span class="alert-text">IN DANGER ZONE - Priority Evacuation</span>
        </div>
      ` : ''}
      
      <div class="popup-details">
        ${facility.population ? `
          <div class="detail-item">
            <span class="detail-label">Occupancy:</span>
            <span class="detail-value">${facility.population.toLocaleString()} people</span>
          </div>
        ` : ''}
        
        <div class="detail-item">
          <span class="detail-label">Priority:</span>
          <span class="detail-value priority-${config.priority}">${config.priority.toUpperCase()}</span>
        </div>
        
        <div class="detail-item">
          <span class="detail-label">Location:</span>
          <span class="detail-value coords">
            ${facility.location.lat.toFixed(4)}, ${facility.location.lon.toFixed(4)}
          </span>
        </div>
        
        ${facility.address ? `
          <div class="detail-item">
            <span class="detail-label">Address:</span>
            <span class="detail-value">${facility.address}</span>
          </div>
        ` : ''}
      </div>
      
      ${isInDanger ? `
        <div class="popup-actions">
          <button class="action-button primary">View Evacuation Plan</button>
        </div>
      ` : ''}
    </div>
  `;
}

/**
 * Check if facility is in danger zone
 */
function checkIfInDangerZone(location, dangerZone) {
  if (!dangerZone || !dangerZone.geometry) {
    return false;
  }

  // Simple bounding box check for demo
  // In production, use proper point-in-polygon algorithm
  const coordinates = dangerZone.geometry.coordinates[0];
  if (!coordinates || coordinates.length === 0) return false;

  const lons = coordinates.map(c => c[0]);
  const lats = coordinates.map(c => c[1]);
  
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);

  return (
    location.lon >= minLon &&
    location.lon <= maxLon &&
    location.lat >= minLat &&
    location.lat <= maxLat
  );
}

/**
 * Add CSS styles for markers
 */
function addMarkerStyles() {
  if (document.getElementById('facility-marker-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'facility-marker-styles';
  style.textContent = `
    .facility-marker {
      cursor: pointer;
      animation: markerAppear 0.5s ease-out;
    }

    @keyframes markerAppear {
      from {
        opacity: 0;
        transform: scale(0) translateY(-20px);
      }
      to {
        opacity: 1;
        transform: scale(1) translateY(0);
      }
    }

    .marker-container {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .marker-icon-wrapper {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      border: 3px solid white;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      position: relative;
      z-index: 2;
      transition: transform 0.2s ease;
    }

    .facility-marker:hover .marker-icon-wrapper {
      transform: scale(1.2);
    }

    .marker-icon {
      font-size: 18px;
    }

    .marker-pulse {
      position: absolute;
      width: 36px;
      height: 36px;
      border: 2px solid;
      border-radius: 50%;
      animation: pulse-facility 2s ease-out infinite;
      z-index: 1;
    }

    @keyframes pulse-facility {
      0% {
        transform: scale(1);
        opacity: 0.8;
      }
      100% {
        transform: scale(2);
        opacity: 0;
      }
    }

    .danger-indicator {
      position: absolute;
      top: -8px;
      right: -8px;
      width: 20px;
      height: 20px;
      background: #ff0000;
      border: 2px solid white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      z-index: 3;
      animation: dangerBlink 1s ease-in-out infinite;
    }

    @keyframes dangerBlink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .facility-marker.in-danger .marker-pulse {
      border-color: #ff0000 !important;
      animation: pulse-danger 1.5s ease-out infinite;
    }

    @keyframes pulse-danger {
      0% {
        transform: scale(1);
        opacity: 1;
      }
      100% {
        transform: scale(2.5);
        opacity: 0;
      }
    }

    /* Popup Styles */
    .mapboxgl-popup-content {
      padding: 0;
      border-radius: 8px;
      overflow: hidden;
      min-width: 280px;
    }

    .facility-popup-content {
      font-family: 'Inter', sans-serif;
    }

    .popup-header {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 1rem;
      background: #2d2d2d;
      border-bottom: 1px solid #444;
    }

    .popup-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      flex-shrink: 0;
    }

    .popup-title-section {
      flex: 1;
    }

    .popup-title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      color: white;
    }

    .popup-type {
      margin: 0.25rem 0 0 0;
      font-size: 0.75rem;
      color: #b0b0b0;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .popup-danger-alert {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1rem;
      background: rgba(255, 68, 68, 0.2);
      border-bottom: 1px solid #ff4444;
    }

    .alert-icon {
      font-size: 1.25rem;
    }

    .alert-text {
      font-size: 0.875rem;
      font-weight: 600;
      color: #ff4444;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .popup-details {
      padding: 1rem;
      background: white;
    }

    .detail-item {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.5rem;
    }

    .detail-item:last-child {
      margin-bottom: 0;
    }

    .detail-label {
      font-size: 0.875rem;
      color: #666;
      font-weight: 500;
    }

    .detail-value {
      font-size: 0.875rem;
      color: #1a1a1a;
      font-weight: 600;
      text-align: right;
    }

    .detail-value.coords {
      font-family: 'Roboto Mono', monospace;
      font-size: 0.75rem;
    }

    .detail-value.priority-critical {
      color: #f44336;
    }

    .detail-value.priority-high {
      color: #FF9800;
    }

    .detail-value.priority-resource {
      color: #2196F3;
    }

    .detail-value.priority-safe {
      color: #4CAF50;
    }

    .popup-actions {
      padding: 0.75rem 1rem;
      background: #f5f5f5;
      border-top: 1px solid #ddd;
    }

    .action-button {
      width: 100%;
      padding: 0.5rem 1rem;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s ease;
    }

    .action-button:hover {
      background: #5568d3;
    }
  `;

  document.head.appendChild(style);
}

export default Markers;