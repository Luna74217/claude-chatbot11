import React from 'react';
import { render } from '@testing-library/react';

// 가장 기본적인 smoke test
describe('Smoke Test', () => {
  it('should render a simple div', () => {
    const { container } = render(<div>Hello World</div>);
    expect(container.firstChild).toBeInTheDocument();
    expect(container.firstChild).toHaveTextContent('Hello World');
  });

  it('should handle basic DOM operations', () => {
    const div = document.createElement('div');
    div.textContent = 'Test';
    expect(div.textContent).toBe('Test');
  });

  it('should have testing environment set up', () => {
    expect(global.localStorage).toBeDefined();
    expect(global.WebSocket).toBeDefined();
  });
}); 