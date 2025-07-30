/**
 * Unit tests for JobListings component
 * Tests job listing display, filtering, sorting, and user interactions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MockedProvider } from '@apollo/client/testing';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';

// Import component
import JobListings from '@/pages/JobListings';
import { AuthContext } from '@/context/AuthContext';
import { JobContext } from '@/context/JobContext';

// Import GraphQL queries and mutations
import { GET_JOBS, APPLY_TO_JOB, SAVE_JOB } from '@/graphql/queries';

// Import mock data
import mockData from '@fixtures/frontend/mockData';

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ search: '' }),
    useSearchParams: () => [new URLSearchParams(), vi.fn()]
  };
});

// Test wrapper component
const TestWrapper = ({ children, authValue, jobValue, apolloMocks = [] }) => (
  <MockedProvider mocks={apolloMocks} addTypename={false}>
    <BrowserRouter>
      <AuthContext.Provider value={authValue}>
        <JobContext.Provider value={jobValue}>
          {children}
        </JobContext.Provider>
      </AuthContext.Provider>
    </BrowserRouter>
  </MockedProvider>
);

describe('JobListings Component', () => {
  // Mock context values
  const mockAuthContext = {
    user: mockData.users.currentUser,
    isAuthenticated: true,
    login: vi.fn(),
    logout: vi.fn(),
    loading: false
  };

  const mockJobContext = {
    jobs: mockData.generators.generateMockJobs(10),
    loading: false,
    error: null,
    fetchJobs: vi.fn(),
    applyToJob: vi.fn(),
    saveJob: vi.fn(),
    filters: {},
    setFilters: vi.fn(),
    sortBy: 'created_at',
    setSortBy: vi.fn()
  };

  // GraphQL mocks
  const getJobsMock = {
    request: {
      query: GET_JOBS,
      variables: {
        filters: {},
        pagination: { offset: 0, limit: 20 },
        sortBy: 'created_at'
      }
    },
    result: {
      data: {
        jobs: {
          items: mockData.generators.generateMockJobs(10),
          totalCount: 25,
          hasNextPage: true,
          hasPreviousPage: false
        }
      }
    }
  };

  const applyToJobMock = {
    request: {
      query: APPLY_TO_JOB,
      variables: {
        input: {
          jobId: 'job-123',
          coverLetter: 'Test cover letter',
          resumeId: 'resume-123'
        }
      }
    },
    result: {
      data: {
        applyToJob: {
          success: true,
          application: {
            id: 'app-123',
            status: 'submitted',
            submittedAt: new Date().toISOString()
          }
        }
      }
    }
  };

  const saveJobMock = {
    request: {
      query: SAVE_JOB,
      variables: {
        jobId: 'job-123'
      }
    },
    result: {
      data: {
        saveJob: {
          success: true,
          savedJob: {
            id: 'saved-123',
            jobId: 'job-123',
            savedAt: new Date().toISOString()
          }
        }
      }
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    test('renders job listings page with header', async () => {
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByRole('heading', { name: /job listings/i })).toBeInTheDocument();
      expect(screen.getByText(/search and filter jobs/i)).toBeInTheDocument();
    });

    test('renders job cards when jobs are loaded', async () => {
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        const jobCards = screen.getAllByTestId(/job-card-/);
        expect(jobCards).toHaveLength(10);
      });
    });

    test('renders loading state initially', () => {
      const loadingJobContext = { ...mockJobContext, loading: true };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={loadingJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(screen.getByText(/loading jobs/i)).toBeInTheDocument();
    });

    test('renders error state when there is an error', () => {
      const errorJobContext = { 
        ...mockJobContext, 
        loading: false,
        error: 'Failed to fetch jobs',
        jobs: []
      };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={errorJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByText(/failed to fetch jobs/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    test('renders empty state when no jobs found', () => {
      const emptyJobContext = { 
        ...mockJobContext, 
        jobs: [],
        loading: false,
        error: null
      };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={emptyJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByText(/no jobs found/i)).toBeInTheDocument();
      expect(screen.getByText(/try adjusting your filters/i)).toBeInTheDocument();
    });
  });

  describe('Job Card Display', () => {
    test('displays job information correctly', async () => {
      const singleJob = [mockData.jobs.frontendJob];
      const singleJobContext = { ...mockJobContext, jobs: singleJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={singleJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('TechCorp Inc.')).toBeInTheDocument();
        expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
        expect(screen.getByText('$130,000 - $180,000')).toBeInTheDocument();
      });
    });

    test('displays remote badge for remote jobs', async () => {
      const remoteJob = [mockData.jobs.remoteJob];
      const remoteJobContext = { ...mockJobContext, jobs: remoteJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={remoteJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Remote')).toBeInTheDocument();
      });
    });

    test('displays skills required', async () => {
      const singleJob = [mockData.jobs.frontendJob];
      const singleJobContext = { ...mockJobContext, jobs: singleJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={singleJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('JavaScript')).toBeInTheDocument();
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('TypeScript')).toBeInTheDocument();
      });
    });

    test('displays posted date correctly', async () => {
      const singleJob = [mockData.jobs.frontendJob];
      const singleJobContext = { ...mockJobContext, jobs: singleJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={singleJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/posted/i)).toBeInTheDocument();
      });
    });
  });

  describe('Filtering', () => {
    test('renders filter controls', () => {
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByPlaceholderText(/search jobs/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/location/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/experience level/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/job type/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/remote work/i)).toBeInTheDocument();
    });

    test('calls setFilters when search input changes', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search jobs/i);
      await user.type(searchInput, 'React Developer');

      await waitFor(() => {
        expect(mockJobContext.setFilters).toHaveBeenCalledWith(
          expect.objectContaining({
            query: 'React Developer'
          })
        );
      });
    });

    test('calls setFilters when location filter changes', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const locationSelect = screen.getByLabelText(/location/i);
      await user.selectOptions(locationSelect, 'San Francisco, CA');

      expect(mockJobContext.setFilters).toHaveBeenCalledWith(
        expect.objectContaining({
          location: 'San Francisco, CA'
        })
      );
    });

    test('calls setFilters when experience level filter changes', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const experienceSelect = screen.getByLabelText(/experience level/i);
      await user.selectOptions(experienceSelect, 'senior');

      expect(mockJobContext.setFilters).toHaveBeenCalledWith(
        expect.objectContaining({
          experienceLevel: 'senior'
        })
      );
    });

    test('calls setFilters when remote work filter changes', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const remoteCheckbox = screen.getByLabelText(/remote work/i);
      await user.click(remoteCheckbox);

      expect(mockJobContext.setFilters).toHaveBeenCalledWith(
        expect.objectContaining({
          remoteOk: true
        })
      );
    });

    test('clears all filters when clear button is clicked', async () => {
      const user = userEvent.setup();
      const filtersSetContext = { 
        ...mockJobContext, 
        filters: { query: 'test', location: 'SF' }
      };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={filtersSetContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const clearButton = screen.getByRole('button', { name: /clear filters/i });
      await user.click(clearButton);

      expect(mockJobContext.setFilters).toHaveBeenCalledWith({});
    });
  });

  describe('Sorting', () => {
    test('renders sort controls', () => {
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByLabelText(/sort by/i)).toBeInTheDocument();
    });

    test('calls setSortBy when sort option changes', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const sortSelect = screen.getByLabelText(/sort by/i);
      await user.selectOptions(sortSelect, 'salary_max');

      expect(mockJobContext.setSortBy).toHaveBeenCalledWith('salary_max');
    });

    test('displays sort options correctly', () => {
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const sortSelect = screen.getByLabelText(/sort by/i);
      expect(within(sortSelect).getByText('Newest First')).toBeInTheDocument();
      expect(within(sortSelect).getByText('Salary: High to Low')).toBeInTheDocument();
      expect(within(sortSelect).getByText('Salary: Low to High')).toBeInTheDocument();
      expect(within(sortSelect).getByText('Most Relevant')).toBeInTheDocument();
    });
  });

  describe('Job Actions', () => {
    test('renders apply button for authenticated users', async () => {
      const singleJob = [mockData.jobs.frontendJob];
      const singleJobContext = { ...mockJobContext, jobs: singleJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={singleJobContext}
          apolloMocks={[getJobsMock, applyToJobMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /apply now/i })).toBeInTheDocument();
      });
    });

    test('renders save button for authenticated users', async () => {
      const singleJob = [mockData.jobs.frontendJob];
      const singleJobContext = { ...mockJobContext, jobs: singleJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={singleJobContext}
          apolloMocks={[getJobsMock, saveJobMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /save job/i })).toBeInTheDocument();
      });
    });

    test('calls applyToJob when apply button is clicked', async () => {
      const user = userEvent.setup();
      const singleJob = [mockData.jobs.frontendJob];
      const singleJobContext = { ...mockJobContext, jobs: singleJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={singleJobContext}
          apolloMocks={[getJobsMock, applyToJobMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        const applyButton = screen.getByRole('button', { name: /apply now/i });
        return user.click(applyButton);
      });

      expect(mockJobContext.applyToJob).toHaveBeenCalledWith(mockData.jobs.frontendJob.id);
    });

    test('calls saveJob when save button is clicked', async () => {
      const user = userEvent.setup();
      const singleJob = [mockData.jobs.frontendJob];
      const singleJobContext = { ...mockJobContext, jobs: singleJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={singleJobContext}
          apolloMocks={[getJobsMock, saveJobMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        const saveButton = screen.getByRole('button', { name: /save job/i });
        return user.click(saveButton);
      });

      expect(mockJobContext.saveJob).toHaveBeenCalledWith(mockData.jobs.frontendJob.id);
    });

    test('navigates to job details when job title is clicked', async () => {
      const user = userEvent.setup();
      const singleJob = [mockData.jobs.frontendJob];
      const singleJobContext = { ...mockJobContext, jobs: singleJob };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={singleJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        const jobTitle = screen.getByRole('link', { name: /senior frontend developer/i });
        return user.click(jobTitle);
      });

      expect(mockNavigate).toHaveBeenCalledWith(`/jobs/${mockData.jobs.frontendJob.id}`);
    });

    test('shows login prompt for unauthenticated users', () => {
      const unauthenticatedContext = { 
        ...mockAuthContext, 
        isAuthenticated: false, 
        user: null 
      };
      
      render(
        <TestWrapper 
          authValue={unauthenticatedContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByText(/sign in to apply/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });
  });

  describe('Pagination', () => {
    test('renders pagination controls when there are multiple pages', async () => {
      const paginatedJobContext = { 
        ...mockJobContext,
        pagination: {
          currentPage: 1,
          totalPages: 5,
          hasNextPage: true,
          hasPreviousPage: false
        }
      };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={paginatedJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('navigation', { name: /pagination/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /next page/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /previous page/i })).toBeDisabled();
      });
    });

    test('calls fetchJobs with correct page when pagination is used', async () => {
      const user = userEvent.setup();
      const paginatedJobContext = { 
        ...mockJobContext,
        pagination: {
          currentPage: 1,
          totalPages: 5,
          hasNextPage: true,
          hasPreviousPage: false
        }
      };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={paginatedJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        const nextButton = screen.getByRole('button', { name: /next page/i });
        return user.click(nextButton);
      });

      expect(mockJobContext.fetchJobs).toHaveBeenCalledWith(
        expect.objectContaining({
          page: 2
        })
      );
    });
  });

  describe('Mobile Responsiveness', () => {
    test('adapts layout for mobile screens', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      // Check for mobile-specific elements or classes
      const container = screen.getByTestId('job-listings-container');
      expect(container).toHaveClass('mobile-layout');
    });

    test('shows mobile filter toggle button', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByRole('button', { name: /filters/i })).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels and roles', () => {
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('search')).toBeInTheDocument();
      expect(screen.getByLabelText(/search jobs/i)).toBeInTheDocument();
    });

    test('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search jobs/i);
      searchInput.focus();
      
      // Tab through interactive elements
      await user.tab();
      expect(screen.getByLabelText(/location/i)).toHaveFocus();
      
      await user.tab();
      expect(screen.getByLabelText(/experience level/i)).toHaveFocus();
    });

    test('announces filter changes to screen readers', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search jobs/i);
      await user.type(searchInput, 'Developer');

      // Check for aria-live region updates
      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent(/searching/i);
      });
    });
  });

  describe('Error Handling', () => {
    test('handles network errors gracefully', () => {
      const errorJobContext = { 
        ...mockJobContext, 
        error: 'Network error',
        jobs: []
      };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={errorJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      expect(screen.getByText(/network error/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    test('retries loading when try again button is clicked', async () => {
      const user = userEvent.setup();
      const errorJobContext = { 
        ...mockJobContext, 
        error: 'Network error',
        jobs: []
      };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={errorJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      await user.click(tryAgainButton);

      expect(mockJobContext.fetchJobs).toHaveBeenCalled();
    });
  });

  describe('Performance', () => {
    test('implements virtual scrolling for large job lists', async () => {
      const largeJobContext = { 
        ...mockJobContext, 
        jobs: mockData.generators.generateMockJobs(1000)
      };
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={largeJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      await waitFor(() => {
        // Should only render visible items plus buffer
        const jobCards = screen.getAllByTestId(/job-card-/);
        expect(jobCards.length).toBeLessThan(50); // Much less than 1000
      });
    });

    test('debounces search input', async () => {
      const user = userEvent.setup();
      vi.useFakeTimers();
      
      render(
        <TestWrapper 
          authValue={mockAuthContext} 
          jobValue={mockJobContext}
          apolloMocks={[getJobsMock]}
        >
          <JobListings />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search jobs/i);
      
      // Type multiple characters quickly
      await user.type(searchInput, 'React');
      
      // Should not call setFilters immediately
      expect(mockJobContext.setFilters).not.toHaveBeenCalled();
      
      // Fast-forward timers
      vi.advanceTimersByTime(500);
      
      // Should call setFilters after debounce delay
      expect(mockJobContext.setFilters).toHaveBeenCalledWith(
        expect.objectContaining({
          query: 'React'
        })
      );
      
      vi.useRealTimers();
    });
  });
});