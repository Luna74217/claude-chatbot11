// 전역 에러 핸들링 유틸리티

export interface AppError {
  code: number;
  message: string;
  details?: string;
  timestamp: string;
}

export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorLog: AppError[] = [];

  private constructor() {}

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  // 에러 생성
  createError(code: number, message: string, details?: string): AppError {
    const error: AppError = {
      code,
      message,
      details,
      timestamp: new Date().toISOString()
    };

    this.logError(error);
    return error;
  }

  // 에러 로깅
  private logError(error: AppError): void {
    this.errorLog.push(error);
    
    // 콘솔에 에러 출력 (개발 모드에서만)
    if (process.env.NODE_ENV === 'development') {
      console.error('🚨 Application Error:', error);
    }

    // 에러 로그가 너무 많아지면 오래된 것들 제거
    if (this.errorLog.length > 100) {
      this.errorLog = this.errorLog.slice(-50);
    }
  }

  // 에러 로그 조회
  getErrorLog(): AppError[] {
    return [...this.errorLog];
  }

  // 에러 로그 초기화
  clearErrorLog(): void {
    this.errorLog = [];
  }

  // 네트워크 에러 처리
  handleNetworkError(error: any): AppError {
    if (error.code === 'NETWORK_ERROR') {
      return this.createError(1001, '네트워크 연결 오류', '서버에 연결할 수 없습니다.');
    }
    
    if (error.code === 'TIMEOUT') {
      return this.createError(1002, '요청 시간 초과', '서버 응답이 너무 늦습니다.');
    }

    return this.createError(1000, '알 수 없는 네트워크 오류', error.message);
  }

  // WebSocket 에러 처리
  handleWebSocketError(error: any): AppError {
    if (error.code === 1006) {
      return this.createError(2001, 'WebSocket 연결 끊김', '서버와의 연결이 끊어졌습니다.');
    }
    
    if (error.code === 1000) {
      return this.createError(2002, 'WebSocket 정상 종료', '연결이 정상적으로 종료되었습니다.');
    }

    return this.createError(2000, 'WebSocket 오류', error.message);
  }

  // 파일 업로드 에러 처리
  handleFileError(error: any): AppError {
    if (error.message.includes('파일 크기')) {
      return this.createError(3001, '파일 크기 초과', '파일이 너무 큽니다.');
    }
    
    if (error.message.includes('파일 형식')) {
      return this.createError(3002, '지원하지 않는 파일 형식', '이 파일 형식은 지원되지 않습니다.');
    }

    return this.createError(3000, '파일 업로드 오류', error.message);
  }

  // 사용자 친화적 에러 메시지
  getUserFriendlyMessage(error: AppError): string {
    const messages: Record<number, string> = {
      1001: '인터넷 연결을 확인해주세요.',
      1002: '잠시 후 다시 시도해주세요.',
      2001: '서버 연결을 다시 시도합니다.',
      2002: '연결이 종료되었습니다.',
      3001: '더 작은 파일을 선택해주세요.',
      3002: '지원되는 파일 형식으로 변경해주세요.',
      1000: '오류가 발생했습니다. 페이지를 새로고침해주세요.',
      2000: '연결에 문제가 있습니다. 다시 시도해주세요.',
      3000: '파일 업로드에 실패했습니다. 다시 시도해주세요.'
    };

    return messages[error.code] || '알 수 없는 오류가 발생했습니다.';
  }
}

// 전역 에러 핸들러 인스턴스
export const errorHandler = ErrorHandler.getInstance();

// 전역 에러 이벤트 리스너
export const setupGlobalErrorHandling = (): void => {
  // 처리되지 않은 Promise 거부 처리
  window.addEventListener('unhandledrejection', (event) => {
    const error = errorHandler.createError(
      9999,
      '처리되지 않은 Promise 오류',
      event.reason?.message || '알 수 없는 오류'
    );
    event.preventDefault();
  });

  // 전역 에러 처리
  window.addEventListener('error', (event) => {
    const error = errorHandler.createError(
      9998,
      '전역 JavaScript 오류',
      `${event.message} (${event.filename}:${event.lineno})`
    );
  });
}; 