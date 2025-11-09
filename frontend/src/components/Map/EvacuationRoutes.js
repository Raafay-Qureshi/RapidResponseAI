  import { useEffect } from 'react';
import mapboxgl from 'mapbox-gl';

/**
 * EvacuationRoutes Component
 * Displays evacuation routes on the map with animated arrows
 */
function EvacuationRoutes({ map, routes }) {
  useEffect(() => {
    if (!map || !routes || routes.length === 0) {
      console.log('[EvacuationRoutes] No routes to display');
      return;
    }

    console.log('[EvacuationRoutes] Adding evacuation routes to map', routes);

    const routeLayers = [];
    const routeSources = [];
    const safeZoneMarkers = [];

    // Process each route
    routes.forEach((route, index) => {
      const isPrimary = index === 0;
      const routeId = `evacuation-route-${index}`;
      const arrowId = `evacuation-arrows-${index}`;
      const labelId = `${routeId}-label`;
      
      // Create route line and collect layer/source IDs
      const { layers, sources } = addRouteLayer(map, route, routeId, arrowId, isPrimary, index);
      routeLayers.push(...layers);
      routeSources.push(...sources);

      // Add safe zone marker
      const marker = addSafeZoneMarker(map, route);
      if (marker) {
        safeZoneMarkers.push(marker);
      }
    });

    // Cleanup function
    return () => {
      console.log('[EvacuationRoutes] Cleaning up routes');
      
      // Remove layers
      routeLayers.forEach(layerId => {
        if (map.getLayer(layerId)) {
          map.removeLayer(layerId);
        }
      });

      // Remove sources
      routeSources.forEach(sourceId => {
        if (map.getSource(sourceId)) {
          map.removeSource(sourceId);
        }
      });

      // Remove markers
      safeZoneMarkers.forEach(marker => marker.remove());
    };
  }, [map, routes]);

  return null;
}

/**
 * Add a route layer to the map
 * Returns arrays of layer and source IDs for cleanup tracking
 */
function addRouteLayer(map, route, routeId, arrowId, isPrimary, index) {
  const layers = [];
  const sources = [];
  
  // Route colors - primary is bright green, alternates are lighter
  const routeColors = [
    '#4CAF50', // Primary - bright green
    '#66BB6A', // Alternate 1 - lighter green
    '#81C784', // Alternate 2 - even lighter
  ];

  const color = routeColors[Math.min(index, routeColors.length - 1)];
  const width = isPrimary ? 6 : 4;

  // Get route path from route object
  const routePath = route.path || route.geometry;

  // Add source
  map.addSource(routeId, {
    type: 'geojson',
    data: routePath,
  });
  sources.push(routeId);

  // Add route line
  map.addLayer({
    id: routeId,
    type: 'line',
    source: routeId,
    paint: {
      'line-color': color,
      'line-width': width,
      'line-opacity': 0.9,
    },
    layout: {
      'line-cap': 'round',
      'line-join': 'round',
    },
  });
  layers.push(routeId);

  // Add animated arrows using triangle symbols
  map.addLayer({
    id: arrowId,
    type: 'symbol',
    source: routeId,
    layout: {
      'symbol-placement': 'line',
      'symbol-spacing': 100, // Distance between arrows
      'text-field': '▶', // Triangle arrow character
      'text-size': isPrimary ? 20 : 16,
      'text-keep-upright': false,
      'text-rotation-alignment': 'map',
      'text-pitch-alignment': 'viewport',
      'text-allow-overlap': true,
      'text-ignore-placement': true,
    },
    paint: {
      'text-color': color,
      'text-opacity': 0.8,
      'text-halo-color': '#000000',
      'text-halo-width': 1,
    },
  });
  layers.push(arrowId);

  // Animate the arrows
  animateRouteArrows(map, arrowId);

  // Add route label
  if (route.destination) {
    const { labelLayer, labelSource } = addRouteLabel(map, route, routeId, color, index);
    if (labelLayer) layers.push(labelLayer);
    if (labelSource) sources.push(labelSource);
  }
  
  return { layers, sources };
}

/**
 * Animate arrows along the route
 */
function animateRouteArrows(map, arrowId) {
  let offset = 0;
  const speed = 2; // pixels per frame

  const animate = () => {
    offset = (offset + speed) % 200;
    
    try {
      map.setLayoutProperty(arrowId, 'text-offset', [0, offset / 10]);
    } catch (error) {
      // Layer removed, stop animation
      return;
    }

    requestAnimationFrame(animate);
  };

  // Start animation after a short delay
  setTimeout(animate, 500);
}

/**
 * Add a label to the route
 * Returns label layer and source IDs for cleanup tracking
 */
function addRouteLabel(map, route, routeId, color, index) {
  const labelId = `${routeId}-label`;
  
  // Get the midpoint of the route for label placement
  const coordinates = route.path?.geometry?.coordinates ||
                     route.geometry?.coordinates || [];
  
  if (coordinates.length === 0) return { labelLayer: null, labelSource: null };

  const midIndex = Math.floor(coordinates.length / 2);
  const midPoint = coordinates[midIndex];

  // Add label source
  map.addSource(labelId, {
    type: 'geojson',
    data: {
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: midPoint,
      },
      properties: {
        title: `→ ${route.destination?.name || 'Safe Zone'}`,
        description: `${route.distance_km?.toFixed(1) || '?'} km • ${route.time_minutes || '?'} min`,
      },
    },
  });

  // Add label layer
  map.addLayer({
    id: labelId,
    type: 'symbol',
    source: labelId,
    layout: {
      'text-field': ['get', 'title'],
      'text-size': 14,
      'text-offset': [0, -2],
      'text-anchor': 'bottom',
      'text-font': ['DIN Pro Bold', 'Arial Unicode MS Bold'],
    },
    paint: {
      'text-color': color,
      'text-halo-color': '#000000',
      'text-halo-width': 2,
    },
  });
  
  return { labelLayer: labelId, labelSource: labelId };
}

/**
 * Add a safe zone marker
 */
function addSafeZoneMarker(map, route) {
  const destination = route.destination;
  if (!destination || !destination.lat || !destination.lon) {
    return null;
  }

  // Create marker element
  const el = document.createElement('div');
  el.className = 'safe-zone-marker';
  el.innerHTML = `
    <div class="marker-icon">✓</div>
    <div class="marker-pulse"></div>
  `;

  // Add CSS for the marker
  addSafeZoneMarkerStyles();

  // Create popup
  const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
    <div class="safe-zone-popup">
      <h3>${destination.name}</h3>
      <p><strong>Capacity:</strong> ${destination.capacity?.toLocaleString() || 'Unknown'} people</p>
      <p><strong>Distance:</strong> ${route.distance_km?.toFixed(1) || '?'} km</p>
      <p><strong>Est. Time:</strong> ${route.time_minutes || '?'} minutes</p>
    </div>
  `);

  // Create and add marker
  const marker = new mapboxgl.Marker(el)
    .setLngLat([destination.lon, destination.lat])
    .setPopup(popup)
    .addTo(map);

  return marker;
}

/**
 * Add CSS styles for safe zone markers
 */
function addSafeZoneMarkerStyles() {
  // Check if styles already added
  if (document.getElementById('safe-zone-marker-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'safe-zone-marker-styles';
  style.textContent = `
    .safe-zone-marker {
      width: 40px;
      height: 40px;
      cursor: pointer;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .marker-icon {
      width: 40px;
      height: 40px;
      background: #4CAF50;
      border: 3px solid white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      font-weight: bold;
      color: white;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      position: relative;
      z-index: 2;
    }

    .marker-pulse {
      position: absolute;
      width: 40px;
      height: 40px;
      border: 2px solid #4CAF50;
      border-radius: 50%;
      animation: pulse-marker 2s ease-out infinite;
      z-index: 1;
    }

    @keyframes pulse-marker {
      0% {
        transform: scale(1);
        opacity: 1;
      }
      100% {
        transform: scale(2.5);
        opacity: 0;
      }
    }

    .safe-zone-popup {
      padding: 0.5rem;
    }

    .safe-zone-popup h3 {
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
      color: #4CAF50;
    }

    .safe-zone-popup p {
      margin: 0.25rem 0;
      font-size: 0.875rem;
    }
  `;

  document.head.appendChild(style);
}

export default EvacuationRoutes;