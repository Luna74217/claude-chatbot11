import { useEffect, useRef, useState, useCallback } from 'react';

export const useWebSocket = (apiUrl) => {
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 10; // Replit에서는 더 많은 재시도 허용

  // WebSocket 연결
  const connect = useCallback(() => {
    try {
      // 이전 연결 정리
      if (ws.current) {
        ws.current.close();
      }

      // 이전 타이머 정리
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      // Replit 환경에 맞는 WebSocket URL 생성
      let wsUrl;
      if (apiUrl.includes('repl.co')) {
        // Replit URL인 경우
        wsUrl = apiUrl.replace(/^https?/, 'wss') + '/ws';
      } else {
        // 로컬 개발 환경인 경우
        wsUrl = apiUrl.replace(/^http/, 'ws') + '/ws';
      }

      console.log('WebSocket 연결 시도:', wsUrl);
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('✅ WebSocket 연결됨');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // 에러 메시지 처리
          if (data.type === 'error') {
            console.error('서버 에러:', data.message);
            setError(data.message);
            return;
          }
          
          setLastMessage(data);
        } catch (err) {
          console.error('메시지 파싱 오류:', err);
          setError('메시지 파싱 오류');
        }
      };

      ws.current.onclose = (event) => {
        console.log('❌ WebSocket 연결 해제됨', event.code, event.reason);
        setIsConnected(false);
        
        // 정상적인 연결 해제가 아닌 경우에만 재연결 시도
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          scheduleReconnect();
        }
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

  // 재연결 스케줄링 (Replit 환경에 맞게 조정)
  const scheduleReconnect = useCallback(() => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      setError('최대 재연결 시도 횟수를 초과했습니다. 페이지를 새로고침해주세요.');
      return;
    }

    // Replit 환경에서는 더 짧은 간격으로 재시도
    const delay = Math.min(2000 * Math.pow(1.5, reconnectAttempts.current), 15000);
    reconnectAttempts.current += 1;

    console.log(`🔄 WebSocket 재연결 시도 ${reconnectAttempts.current}/${maxReconnectAttempts} (${delay}ms 후)`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  }, [connect]);

  // 메시지 전송
  const sendMessage = useCallback((message) => {
    if (!message || typeof message !== 'string') {
      console.error('잘못된 메시지 형식');
      return false;
    }

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      try {
        const messageData = {
          type: 'chat',
          message: message.trim(),
          timestamp: new Date().toISOString()
        };
        
        ws.current.send(JSON.stringify(messageData));
        return true;
      } catch (err) {
        console.error('메시지 전송 실패:', err);
        setError('메시지 전송 실패');
        return false;
      }
    } else {
      console.error('WebSocket이 연결되지 않음');
      return false;
    }
  }, []);

  // 파일 전송
  const sendFile = useCallback((fileInfo) => {
    if (!fileInfo || typeof fileInfo !== 'object') {
      console.error('잘못된 파일 정보');
      return false;
    }

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      try {
        const fileData = {
          type: 'file',
          file: {
            name: fileInfo.name || 'unknown',
            type: fileInfo.type || 'application/octet-stream',
            size: fileInfo.size || 0
          },
          timestamp: new Date().toISOString()
        };
        
        ws.current.send(JSON.stringify(fileData));
        return true;
      } catch (err) {
        console.error('파일 전송 실패:', err);
        setError('파일 전송 실패');
        return false;
      }
    } else {
      console.error('WebSocket이 연결되지 않음');
      return false;
    }
  }, []);

  // 연결 해제
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (ws.current) {
      ws.current.close(1000, '사용자 요청으로 연결 해제');
    }
  }, []);

  // 수동 재연결
  const reconnect = useCallback(() => {
    reconnectAttempts.current = 0;
    setError(null);
    connect();
  }, [connect]);

  // 자동 재연결
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // 연결 상태 모니터링
  useEffect(() => {
    if (!isConnected && !error && reconnectAttempts.current < maxReconnectAttempts) {
      scheduleReconnect();
    }
  }, [isConnected, error, scheduleReconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    sendMessage,
    sendFile,
    connect,
    disconnect,
    reconnect,
    reconnectAttempts: reconnectAttempts.current
  };
}; 