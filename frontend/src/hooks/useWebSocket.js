import { useEffect, useCallback, useRef } from 'react';
import { useWebSocketContext } from '../services/websocket';

/**
 * Custom hook for WebSocket operations
 * Provides clean API for components to interact with WebSocket
 * 
 * @returns {Object} WebSocket utilities
 */
function useWebSocket() {
  const { socket, connected, lastUpdate, isReady } = useWebSocketContext();
  const eventHandlers = useRef(new Map());

  /**
   * Subscribe to a WebSocket event
   * @param {string} eventName - Name of the event to listen for
   * @param {Function} handler - Callback function when event fires
   * @param {Array} dependencies - Dependency array for handler (optional)
   */
  const on = useCallback((eventName, handler, dependencies = []) => {
    if (!socket) {
      console.warn('[useWebSocket] Socket not ready, queueing event listener');
      return;
    }

    // Wrap handler to ensure it's stable
    const wrappedHandler = (...args) => {
      console.log(`[useWebSocket] Event received: ${eventName}`, args);
      handler(...args);
    };

    // Store handler reference for cleanup
    eventHandlers.current.set(eventName, wrappedHandler);

    // Register event listener
    socket.on(eventName, wrappedHandler);
    console.log(`[useWebSocket] Subscribed to event: ${eventName}`);

    // Return cleanup function
    return () => {
      if (socket) {
        socket.off(eventName, wrappedHandler);
        eventHandlers.current.delete(eventName);
        console.log(`[useWebSocket] Unsubscribed from event: ${eventName}`);
      }
    };
  }, [socket]);

  /**
   * Emit a WebSocket event
   * @param {string} eventName - Name of the event to emit
   * @param {*} data - Data to send with the event
   */
  const emit = useCallback((eventName, data) => {
    if (!socket || !connected) {
      console.error('[useWebSocket] Cannot emit - socket not connected');
      return false;
    }

    console.log(`[useWebSocket] Emitting event: ${eventName}`, data);
    socket.emit(eventName, data);
    return true;
  }, [socket, connected]);

  /**
   * Subscribe to disaster updates for a specific disaster ID
   * @param {string} disasterId - Disaster ID to subscribe to
   */
  const subscribeToDisaster = useCallback((disasterId) => {
    if (!disasterId) {
      console.warn('[useWebSocket] No disaster ID provided for subscription');
      return;
    }

    console.log(`[useWebSocket] Subscribing to disaster: ${disasterId}`);
    emit('subscribe_disaster', { disaster_id: disasterId });
  }, [emit]);

  /**
   * Unsubscribe from disaster updates
   * @param {string} disasterId - Disaster ID to unsubscribe from
   */
  const unsubscribeFromDisaster = useCallback((disasterId) => {
    if (!disasterId) return;

    console.log(`[useWebSocket] Unsubscribing from disaster: ${disasterId}`);
    emit('unsubscribe_disaster', { disaster_id: disasterId });
  }, [emit]);

  // Cleanup all event handlers on unmount
  useEffect(() => {
    return () => {
      console.log('[useWebSocket] Cleaning up all event handlers');
      eventHandlers.current.forEach((handler, eventName) => {
        if (socket) {
          socket.off(eventName, handler);
        }
      });
      eventHandlers.current.clear();
    };
  }, [socket]);

  return {
    // Connection state
    connected,
    isReady,
    lastUpdate,

    // Event methods
    on,
    emit,

    // Convenience methods
    subscribeToDisaster,
    unsubscribeFromDisaster,

    // Raw socket (use sparingly)
    socket,
  };
}

export default useWebSocket;