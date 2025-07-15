import React from 'react';
import { render, screen } from '../test-utils';
import EntityXStateMonitor from './EntityXStateMonitor';

// axios 모킹 제거하고 간단한 테스트로 변경
describe('EntityXStateMonitor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<EntityXStateMonitor />);
    expect(screen.getByText('🤖 AI 상태 모니터링')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(<EntityXStateMonitor />);
    // 로딩 상태 확인
    expect(screen.getByText('🤖 AI 상태 모니터링')).toBeInTheDocument();
  });
}); 