import React from 'react';
import { render, screen } from '@/test-utils';
import Dashboard from '@/Dashboard';

// EntityXStateMonitor 컴포넌트 모킹
jest.mock('./components/EntityXStateMonitor', () => {
  return function MockEntityXStateMonitor() {
    return <div data-testid="entity-x-state-monitor">Entity X State Monitor Mock</div>;
  };
});

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<Dashboard />);
    expect(screen.getByText('🌿 Garden 대시보드')).toBeInTheDocument();
  });

  it('renders the main heading', () => {
    render(<Dashboard />);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading).toHaveTextContent('🌿 Garden 대시보드');
  });

  it('renders EntityXStateMonitor component', () => {
    render(<Dashboard />);
    const monitor = screen.getByTestId('entity-x-state-monitor');
    expect(monitor).toBeInTheDocument();
    expect(monitor).toHaveTextContent('Entity X State Monitor Mock');
  });

  it('has correct styling classes', () => {
    const { container } = render(<Dashboard />);
    const mainDiv = container.firstChild as HTMLElement;
    expect(mainDiv).toHaveClass('p-8');
  });

  it('has proper semantic structure', () => {
    render(<Dashboard />);
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });
}); 