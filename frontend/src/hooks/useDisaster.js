import { useState, useCallback, useEffect } from 'react';
import { disasterAPI } from '../services/api';
import useWebSocket from './useWebSocket';

/**
 * Custom hook for managing disaster state and lifecycle
 * Coordinates API calls with WebSocket updates
 * 
 * @returns {Object} Disaster state and control methods
 */
function useDisaster() {
  // State
  const [disaster, setDisaster] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');

  // WebSocket
  const { connected, on, subscribeToDisaster } = useWebSocket();

  /**
   * Trigger a new disaster simulation
   * @param {Object} disasterData - Disaster parameters
   */
  const triggerDisaster = useCallback(async (disasterData) => {
    try {
      console.log('[useDisaster] Triggering disaster:', disasterData);
      
      // Reset state
      setLoading(true);
      setProgress(0);
      setError(null);
      setPlan(null);
      setStatusMessage('Initializing disaster simulation...');

      // Call backend API to trigger disaster
      const response = await disasterAPI.trigger(disasterData);
      
      console.log('[useDisaster] Disaster triggered successfully:', response);
      setDisaster(response);

      // Subscribe to WebSocket updates for this disaster
      if (response.disaster_id) {
        subscribeToDisaster(response.disaster_id);
        setStatusMessage('Subscribed to real-time updates');
      }

    } catch (err) {
      console.error('[useDisaster] Failed to trigger disaster:', err);
      setError(err.message || 'Failed to trigger simulation');
      setLoading(false);
      setStatusMessage('Error occurred');
    }
  }, [subscribeToDisaster]);

  /**
   * Clear current disaster and reset state
   */
  const clearDisaster = useCallback(() => {
    console.log('[useDisaster] Clearing disaster state');
    setDisaster(null);
    setPlan(null);
    setLoading(false);
    setProgress(0);
    setError(null);
    setStatusMessage('');
  }, []);

  // Subscribe to WebSocket events
  useEffect(() => {
    if (!connected) {
      console.log('[useDisaster] WebSocket not connected, waiting...');
      return;
    }

    console.log('[useDisaster] Setting up WebSocket event listeners');

    // Progress updates
    const cleanupProgress = on('progress', (data) => {
      console.log('[useDisaster] Progress update:', data);
      setProgress(data.progress || 0);
      setStatusMessage(data.message || getProgressMessage(data.progress, data.phase));
    });

    // Disaster processing complete
    const cleanupComplete = on('disaster_complete', (data) => {
      console.log('[useDisaster] Disaster processing complete:', data);
      setPlan(data.plan);
      setLoading(false);
      setProgress(100);
      setStatusMessage('Emergency response plan generated');
    });

    // Plan updates (15-minute auto-refresh)
    const cleanupPlanUpdate = on('plan_update', (data) => {
      console.log('[useDisaster] Plan update received:', data);
      setPlan(data.plan);
      setStatusMessage('Plan updated with latest data');
    });

    // Error handling
    const cleanupError = on('disaster_error', (data) => {
      console.error('[useDisaster] Disaster error:', data);
      setError(data.error || 'Unknown error occurred');
      setLoading(false);
      setStatusMessage('Error during processing');
    });

    // Cleanup all subscriptions
    return () => {
      if (cleanupProgress) cleanupProgress();
      if (cleanupComplete) cleanupComplete();
      if (cleanupPlanUpdate) cleanupPlanUpdate();
      if (cleanupError) cleanupError();
    };
  }, [connected, on]);

  /**
   * Get human-readable status message based on progress
   * @param {number} progress - Progress percentage
   * @param {string} phase - Current processing phase
   */
  const getProgressMessage = (progress, phase) => {
    if (progress < 20) return 'Fetching satellite and weather data...';
    if (progress < 40) return 'Analyzing fire perimeter and damage...';
    if (progress < 60) return 'Calculating population impact...';
    if (progress < 80) return 'Running fire spread predictions...';
    if (progress < 95) return 'Generating emergency response plan...';
    return 'Finalizing plan and preparing deployment...';
  };

  return {
    // State
    disaster,
    plan,
    loading,
    progress,
    error,
    statusMessage,

    // Methods
    triggerDisaster,
    clearDisaster,

    // Status
    isProcessing: loading,
    hasActivePlan: !!plan,
    hasError: !!error,
  };
}

export default useDisaster;