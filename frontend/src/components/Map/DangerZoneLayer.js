import { useEffect } from 'react';

/**
 * DangerZoneLayer - Displays fire perimeter on map
 * Adds a red polygon overlay showing the affected area
 */
function DangerZoneLayer({ map, disaster }) {
  useEffect(() => {
    if (!map || !disaster) return;

    const sourceId = 'danger-zone';
    const fillLayerId = 'danger-zone-fill';
    const outlineLayerId = 'danger-zone-outline';

    console.log('[DangerZoneLayer] Adding danger zone to map');

    // Remove existing layers if present
    if (map.getLayer(fillLayerId)) {
      map.removeLayer(fillLayerId);
    }
    if (map.getLayer(outlineLayerId)) {
      map.removeLayer(outlineLayerId);
    }
    if (map.getSource(sourceId)) {
      map.removeSource(sourceId);
    }

    // Get fire perimeter from disaster data
    const firePerimeter = disaster.data?.fire_perimeter || createDefaultPerimeter(disaster.location);

    // Add source
    map.addSource(sourceId, {
      type: 'geojson',
      data: firePerimeter,
    });

    // Add fill layer
    map.addLayer({
      id: fillLayerId,
      type: 'fill',
      source: sourceId,
      paint: {
        'fill-color': '#ff0000',
        'fill-opacity': 0.4,
      },
    });

    // Add outline layer
    map.addLayer({
      id: outlineLayerId,
      type: 'line',
      source: sourceId,
      paint: {
        'line-color': '#ff0000',
        'line-width': 3,
        'line-opacity': 0.9,
      },
    });

    // Optional: Animate the danger zone appearance
    animateDangerZoneAppearance(map, fillLayerId, outlineLayerId);

    // Optional: Add pulsing animation to outline
    animatePulsingOutline(map, outlineLayerId);

    // Cleanup
    return () => {
      console.log('[DangerZoneLayer] Cleaning up danger zone layers');
      if (map.getLayer(fillLayerId)) map.removeLayer(fillLayerId);
      if (map.getLayer(outlineLayerId)) map.removeLayer(outlineLayerId);
      if (map.getSource(sourceId)) map.removeSource(sourceId);
    };
  }, [map, disaster]);

  return null; // This is a non-visual component
}

/**
 * Create a default perimeter polygon if none provided
 * @param {Object} location - Center point {lat, lon}
 * @returns {Object} GeoJSON Feature
 */
function createDefaultPerimeter(location) {
  if (!location) {
    // Default to HWY 407/410 area
    location = { lat: 43.7315, lon: -79.8620 };
  }

  // Create a small square around the point (approx 0.5km radius)
  const offset = 0.005; // degrees (roughly 500m)
  
  return {
    type: 'Feature',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [location.lon - offset, location.lat - offset], // SW
        [location.lon + offset, location.lat - offset], // SE
        [location.lon + offset, location.lat + offset], // NE
        [location.lon - offset, location.lat + offset], // NW
        [location.lon - offset, location.lat - offset], // Close polygon
      ]],
    },
    properties: {
      type: 'danger_zone',
      disaster_id: 'default',
    },
  };
}

/**
 * Animate the danger zone appearance
 * @param {Object} map - Mapbox map instance
 * @param {string} fillLayerId - Fill layer ID
 * @param {string} outlineLayerId - Outline layer ID
 */
function animateDangerZoneAppearance(map, fillLayerId, outlineLayerId) {
  let opacity = 0;
  const duration = 1000; // 1 second
  const steps = 30;
  const increment = 1 / steps;
  const delay = duration / steps;

  const animate = () => {
    opacity += increment;
    
    if (opacity <= 1) {
      map.setPaintProperty(fillLayerId, 'fill-opacity', opacity * 0.4);
      map.setPaintProperty(outlineLayerId, 'line-opacity', opacity * 0.9);
      setTimeout(animate, delay);
    }
  };

  animate();
}

/**
 * Add pulsing animation to the outline
 * @param {Object} map - Mapbox map instance
 * @param {string} outlineLayerId - Outline layer ID
 */
function animatePulsingOutline(map, outlineLayerId) {
  let width = 2;
  let increasing = true;
  const minWidth = 2;
  const maxWidth = 5;

  const pulse = () => {
    if (increasing) {
      width += 0.1;
      if (width >= maxWidth) increasing = false;
    } else {
      width -= 0.1;
      if (width <= minWidth) increasing = true;
    }

    try {
      map.setPaintProperty(outlineLayerId, 'line-width', width);
    } catch (error) {
      // Layer might have been removed, stop animation
      return;
    }

    setTimeout(pulse, 50);
  };

  pulse();
}

export default DangerZoneLayer;