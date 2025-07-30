// Jest DOM matchers
import '@testing-library/jest-dom';

// Mock Service Worker setup
import { server } from '../shared/mocks/server';

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock
});

// Mock window.location
delete window.location;
window.location = {
  href: 'http://localhost:3000',
  origin: 'http://localhost:3000',
  protocol: 'http:',
  hostname: 'localhost',
  port: '3000',
  pathname: '/',
  search: '',
  hash: '',
  assign: jest.fn(),
  replace: jest.fn(),
  reload: jest.fn(),
};

// Mock window.history
Object.defineProperty(window, 'history', {
  value: {
    pushState: jest.fn(),
    replaceState: jest.fn(),
    go: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    length: 1,
    state: null,
  },
  writable: true,
});

// Mock fetch if not available
if (!global.fetch) {
  global.fetch = jest.fn();
}

// Mock console methods for cleaner test output
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  // Start MSW server
  server.listen({ onUnhandledRequest: 'error' });
  
  // Suppress expected errors/warnings in tests
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning:') || 
       args[0].includes('ReactDOMTestUtils.act'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };

  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning:')
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterEach(() => {
  // Reset MSW handlers
  server.resetHandlers();
  
  // Clear all mocks
  jest.clearAllMocks();
  
  // Clear localStorage/sessionStorage
  localStorageMock.clear();
  sessionStorageMock.clear();
});

afterAll(() => {
  // Restore console methods
  console.error = originalError;
  console.warn = originalWarn;
  
  // Stop MSW server
  server.close();
});

// Global test utilities
global.testUtils = {
  // Wait for async operations
  waitFor: async (callback, options = {}) => {
    const { timeout = 5000, interval = 50 } = options;
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        const result = await callback();
        if (result) return result;
      } catch (error) {
        // Continue waiting
      }
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    
    throw new Error(`waitFor timed out after ${timeout}ms`);
  },
  
  // Create mock component
  createMockComponent: (name) => {
    const MockComponent = ({ children, ...props }) => {
      return React.createElement('div', {
        'data-testid': `mock-${name.toLowerCase()}`,
        ...props
      }, children);
    };
    MockComponent.displayName = `Mock${name}`;
    return MockComponent;
  },
  
  // Create mock function with tracking
  createMockFunction: (name) => {
    const mockFn = jest.fn();
    mockFn.mockName = name;
    return mockFn;
  }
};

// Custom matchers
expect.extend({
  toBeInTheDocument(received) {
    const pass = received !== null && received.ownerDocument === document;
    return {
      message: () => 
        pass 
          ? `Expected element not to be in the document`
          : `Expected element to be in the document`,
      pass,
    };
  },
  
  toHaveBeenCalledWithError(received, expectedError) {
    const pass = received.mock.calls.some(call => 
      call.some(arg => arg instanceof Error && arg.message.includes(expectedError))
    );
    return {
      message: () => 
        pass
          ? `Expected function not to have been called with error: ${expectedError}`
          : `Expected function to have been called with error: ${expectedError}`,
      pass,
    };
  }
});

// Test timeout configuration
jest.setTimeout(30000);

// Unhandled promise rejection handler
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Setup React Testing Library globals
import { cleanup } from '@testing-library/react';

// Cleanup after each test
afterEach(() => {
  cleanup();
});