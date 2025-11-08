import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import io from 'socket.io-client';

// Create WebSocket context
const WebSocketContext = createContext(null);

// Custom hook to access WebSocket context
export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  return context;
}

/**
 * WebSocket Provider Component
 * Manages Socket.IO connection and provides context to children
 */
export function WebSocketProvider({ children, url }) {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    console.log('[WebSocket] Initializing connection...');
    
    // Create Socket.IO client
    const socketUrl = url || process.env.REACT_APP_API_URL?.replace('/api', '') || 'http://localhost:5000';
    
    const newSocket = io(socketUrl, {
      transports: ['websocket', 'polling'], // Try websocket first, fallback to polling
      reconnection: true,
      reconnectionAttempts: maxReconnectAttempts,
      reconnectionDelay: 1000,
      timeout: 10000,
    });

    // Connection event handlers
    newSocket.on('connect', () => {
      console.log('[WebSocket] Connected successfully');
      console.log('[WebSocket] Socket ID:', newSocket.id);
      setConnected(true);
      reconnectAttempts.current = 0;
    });

    newSocket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason);
      setConnected(false);
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, reconnect manually
        console.log('[WebSocket] Server disconnected, attempting reconnect...');
        newSocket.connect();
      }
    });

    newSocket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error.message);
      reconnectAttempts.current += 1;
      
      if (reconnectAttempts.current >= maxReconnectAttempts) {
        console.error('[WebSocket] Max reconnection attempts reached');
      }
    });

    newSocket.on('reconnect', (attemptNumber) => {
      console.log(`[WebSocket] Reconnected after ${attemptNumber} attempts`);
      setConnected(true);
    });

    newSocket.on('reconnect_attempt', (attemptNumber) => {
      console.log(`[WebSocket] Reconnection attempt ${attemptNumber}/${maxReconnectAttempts}`);
    });

    newSocket.on('reconnect_failed', () => {
      console.error('[WebSocket] Reconnection failed after max attempts');
    });

    // Generic message handler
    newSocket.on('message', (data) => {
      console.log('[WebSocket] Message received:', data);
      setLastUpdate(new Date());
    });

    // Test connection
    newSocket.emit('ping', { timestamp: Date.now() });

    setSocket(newSocket);

    // Cleanup on unmount
    return () => {
      console.log('[WebSocket] Cleaning up connection');
      if (newSocket) {
        newSocket.disconnect();
        newSocket.removeAllListeners();
      }
    };
  }, [url]);

  const contextValue = {
    socket,
    connected,
    lastUpdate,
    isReady: socket && connected,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
}

export default WebSocketContext;