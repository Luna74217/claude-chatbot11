import { ErrorHandler, errorHandler, setupGlobalErrorHandling } from '../errorHandler';

describe('ErrorHandler', () => {
  let handler: ErrorHandler;

  beforeEach(() => {
    handler = ErrorHandler.getInstance();
    handler.clearErrorLog();
  });

  describe('createError', () => {
    it('should create an error with correct properties', () => {
      const error = handler.createError(1001, 'Test error', 'Test details');
      
      expect(error.code).toBe(1001);
      expect(error.message).toBe('Test error');
      expect(error.details).toBe('Test details');
      expect(error.timestamp).toBeDefined();
    });

    it('should log the error', () => {
      const error = handler.createError(1001, 'Test error');
      const log = handler.getErrorLog();
      
      expect(log).toHaveLength(1);
      expect(log[0]).toEqual(error);
    });
  });

  describe('handleNetworkError', () => {
    it('should handle network errors correctly', () => {
      const networkError = { code: 'NETWORK_ERROR', message: 'Connection failed' };
      const error = handler.handleNetworkError(networkError);
      
      expect(error.code).toBe(1001);
      expect(error.message).toBe('네트워크 연결 오류');
    });

    it('should handle timeout errors correctly', () => {
      const timeoutError = { code: 'TIMEOUT', message: 'Request timeout' };
      const error = handler.handleNetworkError(timeoutError);
      
      expect(error.code).toBe(1002);
      expect(error.message).toBe('요청 시간 초과');
    });
  });

  describe('handleWebSocketError', () => {
    it('should handle WebSocket connection close errors', () => {
      const wsError = { code: 1006, message: 'Connection closed' };
      const error = handler.handleWebSocketError(wsError);
      
      expect(error.code).toBe(2001);
      expect(error.message).toBe('WebSocket 연결 끊김');
    });

    it('should handle normal WebSocket closure', () => {
      const wsError = { code: 1000, message: 'Normal closure' };
      const error = handler.handleWebSocketError(wsError);
      
      expect(error.code).toBe(2002);
      expect(error.message).toBe('WebSocket 정상 종료');
    });
  });

  describe('handleFileError', () => {
    it('should handle file size errors', () => {
      const fileError = { message: '파일 크기가 너무 큽니다' };
      const error = handler.handleFileError(fileError);
      
      expect(error.code).toBe(3001);
      expect(error.message).toBe('파일 크기 초과');
    });

    it('should handle file format errors', () => {
      const fileError = { message: '지원하지 않는 파일 형식입니다' };
      const error = handler.handleFileError(fileError);
      
      expect(error.code).toBe(3002);
      expect(error.message).toBe('지원하지 않는 파일 형식');
    });
  });

  describe('getUserFriendlyMessage', () => {
    it('should return user-friendly messages for known error codes', () => {
      const error = handler.createError(1001, 'Network error');
      const message = handler.getUserFriendlyMessage(error);
      
      expect(message).toBe('인터넷 연결을 확인해주세요.');
    });

    it('should return default message for unknown error codes', () => {
      const error = handler.createError(9999, 'Unknown error');
      const message = handler.getUserFriendlyMessage(error);
      
      expect(message).toBe('알 수 없는 오류가 발생했습니다.');
    });
  });

  describe('error log management', () => {
    it('should limit error log size', () => {
      // 101개의 에러 생성
      for (let i = 0; i < 101; i++) {
        handler.createError(i, `Error ${i}`);
      }
      
      const log = handler.getErrorLog();
      expect(log.length).toBeLessThanOrEqual(100);
    });

    it('should clear error log', () => {
      handler.createError(1001, 'Test error');
      handler.clearErrorLog();
      
      const log = handler.getErrorLog();
      expect(log).toHaveLength(0);
    });
  });
});

describe('Global error handler', () => {
  it('should be a singleton instance', () => {
    const instance1 = ErrorHandler.getInstance();
    const instance2 = ErrorHandler.getInstance();
    
    expect(instance1).toBe(instance2);
  });

  it('should export errorHandler instance', () => {
    expect(errorHandler).toBeInstanceOf(ErrorHandler);
  });
});

describe('setupGlobalErrorHandling', () => {
  beforeEach(() => {
    // Mock window event listeners
    window.addEventListener = jest.fn();
  });

  it('should set up global error event listeners', () => {
    setupGlobalErrorHandling();
    
    expect(window.addEventListener).toHaveBeenCalledWith('unhandledrejection', expect.any(Function));
    expect(window.addEventListener).toHaveBeenCalledWith('error', expect.any(Function));
  });
}); 