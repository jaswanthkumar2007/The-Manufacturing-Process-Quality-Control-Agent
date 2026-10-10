/**
 * useWebSocket hook — connects to the FastAPI WebSocket for live sensor data.
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

export function useWebSocket() {
  const [connected, setConnected]         = useState(false);
  const [sensorData, setSensorData]       = useState({});
  const [lastMessage, setLastMessage]     = useState(null);
  const wsRef  = useRef(null);
  const sid    = useRef(uuidv4());
  const pingRef = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      wsRef.current = new WebSocket(`${WS_URL}/ws/${sid.current}`);

      wsRef.current.onopen = () => {
        setConnected(true);
        pingRef.current = setInterval(() => {
          wsRef.current?.send('ping');
        }, 20000);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'pong') return;
          setLastMessage(msg);

          if (msg.type === 'sensor_reading' && msg.payload) {
            const { process_line, sensor_type, value, unit, timestamp } = msg.payload;
            const key = `${process_line}:${sensor_type}`;
            setSensorData(prev => ({
              ...prev,
              [key]: { value, unit, timestamp, process_line, sensor_type },
            }));
          }
        } catch { /* ignore malformed */ }
      };

      wsRef.current.onclose  = () => { setConnected(false); clearInterval(pingRef.current); };
      wsRef.current.onerror  = () => { setConnected(false); };
    } catch (err) {
      console.warn('WebSocket connection failed:', err.message);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearInterval(pingRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { connected, sensorData, lastMessage };
}
