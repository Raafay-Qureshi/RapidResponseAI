import React, { useState, useEffect } from 'react';
import useWebSocket from '../../hooks/useWebSocket';

function WebSocketTest() {
  const { connected, on, emit } = useWebSocket();
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Subscribe to test events
    const cleanup = on('test_response', (data) => {
      setMessages(prev => [...prev, data]);
    });

    return cleanup;
  }, [on]);

  const sendTestMessage = () => {
    emit('test_message', { text: 'Hello from frontend!', timestamp: Date.now() });
  };

  return (
    <div style={{ padding: '2rem', background: '#2d2d2d', color: 'white' }}>
      <h2>WebSocket Test</h2>
      <p>Status: {connected ? '✅ Connected' : '❌ Disconnected'}</p>
      <button onClick={sendTestMessage}>Send Test Message</button>
      <div style={{ marginTop: '1rem' }}>
        <h3>Received Messages:</h3>
        <ul>
          {messages.map((msg, idx) => (
            <li key={idx}>{JSON.stringify(msg)}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default WebSocketTest;