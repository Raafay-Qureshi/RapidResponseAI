import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import DangerZoneLayer from './DangerZoneLayer';
import EvacuationRoutes from './EvacuationRoutes';
import Markers from './Markers';
import './MapView.css';

// Set Mapbox access token
mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;

function MapView({ disaster, plan }) {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (map.current) return; // Initialize only once

    console.log('[MapView] Initializing Mapbox GL map...');

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11', // Dark theme for emergency ops
      center: [-79.8620, 43.7315], // HWY 407/410 interchange [lon, lat]
      zoom: 12,
      pitch: 0, // Top-down view initially
      bearing: 0,
    });

    // Add navigation controls
    map.current.addControl(
      new mapboxgl.NavigationControl({
        showCompass: true,
        showZoom: true,
      }),
      'top-right'
    );

    // Add scale control
    map.current.addControl(
      new mapboxgl.ScaleControl({
        maxWidth: 100,
        unit: 'metric',
      }),
      'bottom-right'
    );

    // Set map loaded flag
    map.current.on('load', () => {
      console.log('[MapView] Map loaded successfully');
      setMapLoaded(true);
    });

    // Error handling - only log once to prevent infinite loops
    let errorLogged = false;
    map.current.on('error', (e) => {
      if (!errorLogged) {
        console.error('[MapView] Map error:', {
          type: e?.type,
          error: e?.error,
          message: e?.error?.message || e?.message,
          sourceId: e?.sourceId,
          tile: e?.tile
        });
        errorLogged = true;
        
        // Reset after a delay to allow future errors
        setTimeout(() => {
          errorLogged = false;
        }, 5000);
      }
    });

    // Cleanup on unmount
    return () => {
      if (map.current) {
        console.log('[MapView] Cleaning up map instance');
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Update map when disaster location changes
  useEffect(() => {
    if (!mapLoaded || !disaster) return;

    console.log('[MapView] Flying to disaster location:', disaster.location);

    map.current.flyTo({
      center: [disaster.location.lon, disaster.location.lat],
      zoom: 13,
      duration: 2000,
      essential: true, // This animation is considered essential
    });
  }, [disaster, mapLoaded]);

  return (
    <div className="map-view">
      <div ref={mapContainer} className="map-container" />
      
      {/* Map Layers */}
      {mapLoaded && disaster && (
        <>
          <DangerZoneLayer map={map.current} disaster={disaster} />
          
          {plan && (
            <>
              {plan.evacuation_plan && (
                <EvacuationRoutes
                  map={map.current}
                  routes={plan.evacuation_plan.routes || []}
                />
              )}
              
              {plan.population_impact && (
                <Markers
                  map={map.current}
                  facilities={plan.population_impact.critical_facilities || []}
                  dangerZone={disaster.data?.fire_perimeter}
                />
              )}
            </>
          )}
        </>
      )}
      
      {!mapLoaded && (
        <div className="map-loading">
          <div className="spinner"></div>
          <p>Loading map...</p>
        </div>
      )}
    </div>
  );
}

export default MapView;