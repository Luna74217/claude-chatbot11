import path from 'path';

const isReplit = process.env.REPL_ID !== undefined;

export const resolvePath = (relativePath: string): string => {
  if (isReplit) {
    // Replit 특수 경로 처리
    return path.resolve(process.cwd(), 'src', relativePath);
  }
  return relativePath;
};

export const setupTestPaths = (): void => {
  if (isReplit) {
    // Replit에서 Jest 모듈 경로 재설정
    const srcPath = path.resolve(process.cwd(), 'src');
    process.env.NODE_PATH = srcPath;
    
    // 모듈 경로 초기화 (Node.js 내부 API 사용)
    try {
      const Module = require('module');
      if (Module._initPaths) {
        Module._initPaths();
      }
    } catch (error) {
      console.warn('Module path initialization failed:', error);
    }
  }
};

// 환경 정보 출력
export const getEnvironmentInfo = () => ({
  isReplit,
  nodePath: process.env.NODE_PATH,
  cwd: process.cwd(),
  platform: process.platform
}); 