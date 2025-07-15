import React from 'react';
import { render, screen } from '@/test-utils';
import App from '@/App';

// ChatInterface 컴포넌트 모킹
jest.mock('./components/ChatInterface/ChatInterface', () => {
  return function MockChatInterface() {
    return <div data-testid="chat-interface">Chat Interface Mock</div>;
  };
});

describe('App', () => {
  beforeEach(() => {
    // 각 테스트 전에 mock 초기화
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
  });

  it('renders ChatInterface component', () => {
    render(<App />);
    const chatInterface = screen.getByTestId('chat-interface');
    expect(chatInterface).toBeInTheDocument();
    expect(chatInterface).toHaveTextContent('Chat Interface Mock');
  });

  it('has correct component structure', () => {
    const { container } = render(<App />);
    expect(container.firstChild).toBeInTheDocument();
  });
}); 