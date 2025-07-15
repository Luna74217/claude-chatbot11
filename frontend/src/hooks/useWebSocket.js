import { useEffect, useRef, useState, useCallback } from 'react';

export const useWebSocket = (apiUrl) => {
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);

  // WebSocket 연결
  const connect = useCallback(() => {
    try {
      // HTTP를 WebSocket으로 변환
      const wsUrl = apiUrl.replace(/^http/, 'ws');
      ws.current = new WebSocket(`${wsUrl}/ws`);

      ws.current.onopen = () => {
        console.log('WebSocket 연결됨');
        setIsConnected(true);
        setError(null);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
        } catch (err) {
          console.error('메시지 파싱 오류:', err);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket 연결 해제됨');
        setIsConnected(false);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket 오류:', error);
        setError('WebSocket 연결 오류');
        setIsConnected(false);
      };

    } catch (err) {
      console.error('WebSocket 연결 실패:', err);
      setError('WebSocket 연결 실패');
    }
  }, [apiUrl]);

  // 메시지 전송
  const sendMessage = useCallback((message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'chat',
        message: message,
        timestamp: new Date().toISOString()
      }));
      return true;
    } else {
      console.error('WebSocket이 연결되지 않음');
      return false;
    }
  }, []);

  // 파일 전송
  const sendFile = useCallback((fileInfo) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'file',
        file: fileInfo,
        timestamp: new Date().toISOString()
      }));
      return true;
    } else {
      console.error('WebSocket이 연결되지 않음');
      return false;
    }
  }, []);

  // 연결 해제
  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
    }
  }, []);

  // 자동 재연결
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // 연결 상태 모니터링 및 재연결
  useEffect(() => {
    if (!isConnected && !error) {
      const timer = setTimeout(() => {
        console.log('WebSocket 재연결 시도...');
        connect();
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [isConnected, error, connect]);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    sendFile,
    connect,
    disconnect
  };
}; 