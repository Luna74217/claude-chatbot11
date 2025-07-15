import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { Message, Conversation, Settings } from '@/types';

// 테스트용 기본 설정
export const defaultSettings: Settings = {
  darkMode: false,
  fontSize: 'medium'
};

// 테스트용 기본 메시지
export const createMockMessage = (overrides: Partial<Message> = {}): Message => ({
  id: Math.random(),
  role: 'user',
  content: '테스트 메시지입니다.',
  timestamp: new Date().toISOString(),
  ...overrides
});

// 테스트용 기본 대화
export const createMockConversation = (overrides: Partial<Conversation> = {}): Conversation => ({
  id: 'test-conversation-1',
  title: '테스트 대화',
  messages: [
    createMockMessage({ role: 'user', content: '안녕하세요' }),
    createMockMessage({ role: 'assistant', content: '안녕하세요! 무엇을 도와드릴까요?' })
  ],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  ...overrides
});

// 테스트용 대화 목록
export const createMockConversations = (count: number = 3): Conversation[] => {
  return Array.from({ length: count }, (_, index) => 
    createMockConversation({
      id: `conversation-${index + 1}`,
      title: `테스트 대화 ${index + 1}`,
      messages: [
        createMockMessage({ 
          role: 'user', 
          content: `대화 ${index + 1}의 사용자 메시지` 
        }),
        createMockMessage({ 
          role: 'assistant', 
          content: `대화 ${index + 1}의 어시스턴트 응답` 
        })
      ]
    })
  );
};

// 커스텀 렌더 함수 (Provider 래핑용)
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  // 필요한 경우 Provider 옵션 추가
}

const customRender = (
  ui: ReactElement,
  options: CustomRenderOptions = {}
) => {
  const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
    return (
      <>
        {children}
      </>
    );
  };

  return render(ui, { wrapper: AllTheProviders, ...options });
};

// 테스트용 파일 객체 생성
export const createMockFile = (name: string, type: string, size: number): File => {
  const file = new File(['test content'], name, { type });
  Object.defineProperty(file, 'size', {
    value: size,
    writable: false
  });
  return file;
};

// 테스트용 이벤트 생성
export const createMockEvent = (type: string, target?: any) => {
  return {
    type,
    target,
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
  };
};

// 테스트용 드래그 이벤트 생성
export const createMockDragEvent = (type: string, files: File[] = []) => {
  return {
    type,
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
    dataTransfer: {
      files,
      items: files.map(file => ({
        kind: 'file',
        type: file.type,
        getAsFile: () => file
      })),
      types: ['Files']
    }
  } as any;
};

// 비동기 작업 대기
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock 함수 초기화
export const clearAllMocks = () => {
  jest.clearAllMocks();
  (localStorage.getItem as jest.Mock).mockClear();
  (localStorage.setItem as jest.Mock).mockClear();
  (localStorage.removeItem as jest.Mock).mockClear();
  (localStorage.clear as jest.Mock).mockClear();
};

// re-export everything
export * from '@testing-library/react';
export { customRender as render }; 