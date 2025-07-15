import { useEffect, useRef, useState, useCallback } from 'react';

export const useWebSocket = (apiUrl) => {
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

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

      // HTTP를 WebSocket으로 변환
      const wsUrl = apiUrl.replace(/^http/, 'ws');
      ws.current = new WebSocket(`${wsUrl}/ws`);

      ws.current.onopen = () => {
        console.log('WebSocket 연결됨');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0; // 연결 성공 시 재시도 횟수 리셋
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
        console.log('WebSocket 연결 해제됨', event.code, event.reason);
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

  // 재연결 스케줄링
  const scheduleReconnect = useCallback(() => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      setError('최대 재연결 시도 횟수를 초과했습니다.');
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000); // 지수 백오프, 최대 30초
    reconnectAttempts.current += 1;

    console.log(`WebSocket 재연결 시도 ${reconnectAttempts.current}/${maxReconnectAttempts} (${delay}ms 후)`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, delay);
  }, [connect]);

  // 메시지 전송 (타입 안전성 추가)
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

  // 파일 전송 (검증 추가)
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