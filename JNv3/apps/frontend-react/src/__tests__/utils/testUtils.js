/**
 * Testing utilities for JobQuest Navigator frontend tests.
 * Provides common mocks, providers, and helper functions.
 */

import React from 'react';
import { render } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { BrowserRouter } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import { JobContext } from '../../context/JobContext';
import { ToastContext } from '../../context/ToastContext';

// Mock authentication context
export const mockAuthContext = {
  user: {
    id: 'test-user-id',
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
    fullName: 'Test User',
    isActive: true,
    isVerified: true
  },
  isAuthenticated: true,
  isLoading: false,
  login: jest.fn(),
  logout: jest.fn(),
  signup: jest.fn(),
  updateProfile: jest.fn(),
  token: 'mock-jwt-token',
  refreshToken: jest.fn()
};

// Mock job context
export const mockJobContext = {
  jobs: [],
  selectedJob: null,
  isLoading: false,
  error: null,
  searchFilters: {},
  createJob: jest.fn(),
  updateJob: jest.fn(),
  deleteJob: jest.fn(),
  searchJobs: jest.fn(),
  selectJob: jest.fn(),
  clearSelection: jest.fn(),
  setSearchFilters: jest.fn()
};

// Mock toast context
export const mockToastContext = {
  toasts: [],
  showToast: jest.fn(),
  removeToast: jest.fn()
};

/**
 * Custom render function that includes all providers
 * @param {React.Component} ui - Component to render
 * @param {Object} options - Render options
 * @param {Array} mocks - GraphQL mocks for MockedProvider
 * @param {Object} authContextValue - Custom auth context value
 * @param {Object} jobContextValue - Custom job context value
 * @param {Object} toastContextValue - Custom toast context value
 */
export function renderWithProviders(
  ui, 
  {
    mocks = [],
    authContextValue = mockAuthContext,
    jobContextValue = mockJobContext,
    toastContextValue = mockToastContext,
    route = '/',
    ...renderOptions
  } = {}
) {
  // Set initial URL if route is provided
  if (route !== '/') {
    window.history.pushState({}, 'Test page', route);
  }

  function Wrapper({ children }) {
    return (
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <JobContext.Provider value={jobContextValue}>
              <ToastContext.Provider value={toastContextValue}>
                {children}
              </ToastContext.Provider>
            </JobContext.Provider>
          </AuthContext.Provider>
        </BrowserRouter>
      </MockedProvider>
    );
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

/**
 * Render component with only authentication context
 */
export function renderWithAuth(ui, authContextValue = mockAuthContext, options = {}) {
  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        <AuthContext.Provider value={authContextValue}>
          {children}
        </AuthContext.Provider>
      </BrowserRouter>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

/**
 * Render component with only GraphQL mocks
 */
export function renderWithGraphQL(ui, mocks = [], options = {}) {
  function Wrapper({ children }) {
    return (
      <MockedProvider mocks={mocks} addTypename={false}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </MockedProvider>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

// Common GraphQL mocks
export const commonMocks = {
  // User queries
  GET_USER_PROFILE: {
    request: {
      query: require('../../graphql/queries').GET_USER_PROFILE,
    },
    result: {
      data: {
        myProfile: {
          id: 'test-user-id',
          email: 'test@example.com',
          firstName: 'Test',
          lastName: 'User',
          fullName: 'Test User',
          isActive: true,
          preferences: {
            jobAlerts: true,
            marketingEmails: false,
            preferredLocation: 'San Francisco, CA'
          }
        }
      }
    }
  },

  // Job queries
  GET_JOBS: {
    request: {
      query: require('../../graphql/queries').GET_JOBS,
      variables: { limit: 10 }
    },
    result: {
      data: {
        jobs: [
          {
            id: 'job-1',
            title: 'Frontend Developer',
            company: {
              id: 'company-1',
              name: 'Tech Corp',
              industry: 'Technology'
            },
            location: 'San Francisco, CA',
            jobType: 'full_time',
            workArrangement: 'hybrid',
            salaryMin: 80000,
            salaryMax: 120000,
            createdAt: new Date().toISOString()
          },
          {
            id: 'job-2',
            title: 'Backend Engineer',
            company: {
              id: 'company-2',
              name: 'StartupCo',
              industry: 'Technology'
            },
            location: 'Remote',
            jobType: 'full_time',
            workArrangement: 'remote',
            salaryMin: 90000,
            salaryMax: 140000,
            createdAt: new Date().toISOString()
          }
        ]
      }
    }
  },

  // Job mutations
  CREATE_JOB: {
    request: {
      query: require('../../graphql/mutations').CREATE_USER_JOB,
      variables: {
        input: expect.any(Object)
      }
    },
    result: {
      data: {
        createUserJob: {
          success: true,
          message: 'Job created successfully',
          job: {
            id: 'new-job-id',
            title: 'Test Job',
            company: {
              id: 'company-id',
              name: 'Test Company'
            },
            location: 'Test Location',
            jobType: 'full_time',
            workArrangement: 'remote'
          }
        }
      }
    }
  }
};

/**
 * Create a mock function that tracks calls and provides helpful assertions
 */
export function createMockFunction(name = 'mockFunction') {
  const fn = jest.fn();
  fn.mockName = name;
  return fn;
}

/**
 * Wait for async operations to complete
 */
export function waitFor(callback, options = {}) {
  return require('@testing-library/react').waitFor(callback, {
    timeout: 5000,
    ...options
  });
}

/**
 * Mock implementation for localStorage
 */
export const mockLocalStorage = {
  getItem: jest.fn((key) => {
    const mockData = {
      'jobquest_access_token': 'mock-token',
      'user_preferences': JSON.stringify({
        theme: 'light',
        notifications: true
      })
    };
    return mockData[key] || null;
  }),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

/**
 * Reset all mocks to clean state
 */
export function resetAllMocks() {
  jest.clearAllMocks();
  mockLocalStorage.getItem.mockClear();
  mockLocalStorage.setItem.mockClear();
  mockLocalStorage.removeItem.mockClear();
  mockLocalStorage.clear.mockClear();
}

// Export everything from @testing-library/react for convenience
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';