/**
 * Tests for JobListings page component
 * Tests job display, filtering, pagination, and user interactions
 */

import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import JobListings from '../../pages/JobListings';
import { renderWithProviders, commonMocks } from '../utils/testUtils';
import { GET_JOBS } from '../../graphql/queries';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

describe('JobListings', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('data loading', () => {
    test('shows loading state while fetching jobs', () => {
      const mocks = [
        {
          request: {
            query: GET_JOBS,
            variables: { limit: 10 }
          },
          delay: 1000 // Simulate slow loading
        }
      ];

      renderWithProviders(<JobListings />, { mocks });

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    test('displays jobs after successful fetch', async () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
      });

      // Check job details are displayed
      expect(screen.getByText('Tech Corp')).toBeInTheDocument();
      expect(screen.getByText('StartupCo')).toBeInTheDocument();
      expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
      expect(screen.getByText('Remote')).toBeInTheDocument();
    });

    test('shows error message when fetch fails', async () => {
      const errorMock = {
        request: {
          query: GET_JOBS,
          variables: { limit: 10 }
        },
        error: new Error('Failed to fetch jobs')
      };

      renderWithProviders(<JobListings />, { mocks: [errorMock] });

      await waitFor(() => {
        expect(screen.getByText(/error loading jobs/i)).toBeInTheDocument();
        expect(screen.getByText(/failed to fetch jobs/i)).toBeInTheDocument();
      });
    });

    test('shows empty state when no jobs found', async () => {
      const emptyMock = {
        request: {
          query: GET_JOBS,
          variables: { limit: 10 }
        },
        result: {
          data: {
            jobs: []
          }
        }
      };

      renderWithProviders(<JobListings />, { mocks: [emptyMock] });

      await waitFor(() => {
        expect(screen.getByText(/no jobs found/i)).toBeInTheDocument();
        expect(screen.getByText(/create your first job/i)).toBeInTheDocument();
      });
    });
  });

  describe('job display', () => {
    test('displays job cards with correct information', async () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        // Check first job
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('Tech Corp')).toBeInTheDocument();
        expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
        expect(screen.getByText('$80,000 - $120,000')).toBeInTheDocument();
        expect(screen.getByText('Full Time')).toBeInTheDocument();
        expect(screen.getByText('Hybrid')).toBeInTheDocument();

        // Check second job
        expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
        expect(screen.getByText('StartupCo')).toBeInTheDocument();
        expect(screen.getByText('Remote')).toBeInTheDocument();
        expect(screen.getByText('$90,000 - $140,000')).toBeInTheDocument();
      });
    });

    test('shows job type and work arrangement badges', async () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        // Check for badge elements
        const fullTimeBadges = screen.getAllByText('Full Time');
        expect(fullTimeBadges).toHaveLength(2);

        const hybridBadge = screen.getByText('Hybrid');
        const remoteBadge = screen.getByText('Remote');
        
        expect(hybridBadge).toBeInTheDocument();
        expect(remoteBadge).toBeInTheDocument();
      });
    });

    test('displays relative creation dates', async () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        // Should show relative time like "Just now", "5 minutes ago", etc.
        expect(screen.getByText(/ago|just now|recently/i)).toBeInTheDocument();
      });
    });
  });

  describe('job interactions', () => {
    test('navigates to job details when job card is clicked', async () => {
      const user = userEvent.setup();
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      });

      const jobCard = screen.getByTestId('job-card-job-1');
      await user.click(jobCard);

      expect(mockNavigate).toHaveBeenCalledWith('/jobs/job-1');
    });

    test('shows save job button and handles save action', async () => {
      const user = userEvent.setup();
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      });

      const saveButtons = screen.getAllByRole('button', { name: /save job/i });
      expect(saveButtons).toHaveLength(2);

      await user.click(saveButtons[0]);

      // Should show saved state
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /saved/i })).toBeInTheDocument();
      });
    });

    test('shows apply button and handles apply action', async () => {
      const user = userEvent.setup();
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      });

      const applyButtons = screen.getAllByRole('button', { name: /apply/i });
      expect(applyButtons).toHaveLength(2);

      await user.click(applyButtons[0]);

      expect(mockNavigate).toHaveBeenCalledWith('/jobs/job-1/apply');
    });
  });

  describe('filtering and search', () => {
    test('shows search input and filters', async () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      // Check for search input
      const searchInput = screen.getByPlaceholderText(/search jobs/i);
      expect(searchInput).toBeInTheDocument();

      // Check for filter options
      expect(screen.getByText(/job type/i)).toBeInTheDocument();
      expect(screen.getByText(/location/i)).toBeInTheDocument();
      expect(screen.getByText(/work arrangement/i)).toBeInTheDocument();
    });

    test('filters jobs by search term', async () => {
      const user = userEvent.setup();
      const mocks = [
        commonMocks.GET_JOBS,
        {
          request: {
            query: GET_JOBS,
            variables: { limit: 10, search: 'frontend' }
          },
          result: {
            data: {
              jobs: [commonMocks.GET_JOBS.result.data.jobs[0]] // Only frontend job
            }
          }
        }
      ];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search jobs/i);
      await user.type(searchInput, 'frontend');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        expect(screen.queryByText('Backend Engineer')).not.toBeInTheDocument();
      });
    });

    test('filters jobs by job type', async () => {
      const user = userEvent.setup();
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      });

      // Open job type filter
      const jobTypeFilter = screen.getByText(/job type/i);
      await user.click(jobTypeFilter);

      // Select full-time filter
      const fullTimeOption = screen.getByRole('option', { name: /full time/i });
      await user.click(fullTimeOption);

      // Results should be filtered (both jobs are full-time in mock data)
      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
      });
    });

    test('clears filters when clear button is clicked', async () => {
      const user = userEvent.setup();
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      // Apply some filters first
      const searchInput = screen.getByPlaceholderText(/search jobs/i);
      await user.type(searchInput, 'test search');

      // Click clear filters button
      const clearButton = screen.getByRole('button', { name: /clear filters/i });
      await user.click(clearButton);

      // Search input should be cleared
      expect(searchInput).toHaveValue('');
    });
  });

  describe('create job functionality', () => {
    test('shows create job button for authenticated users', () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      const createButton = screen.getByRole('button', { name: /create job|add job/i });
      expect(createButton).toBeInTheDocument();
    });

    test('navigates to create job page when button is clicked', async () => {
      const user = userEvent.setup();
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      const createButton = screen.getByRole('button', { name: /create job|add job/i });
      await user.click(createButton);

      expect(mockNavigate).toHaveBeenCalledWith('/jobs/create');
    });
  });

  describe('pagination', () => {
    test('shows pagination controls when there are many jobs', async () => {
      const manyJobsMock = {
        request: {
          query: GET_JOBS,
          variables: { limit: 10 }
        },
        result: {
          data: {
            jobs: Array.from({ length: 10 }, (_, i) => ({
              id: `job-${i + 1}`,
              title: `Job ${i + 1}`,
              company: {
                id: `company-${i + 1}`,
                name: `Company ${i + 1}`,
                industry: 'Technology'
              },
              location: 'Test Location',
              jobType: 'full_time',
              workArrangement: 'remote',
              salaryMin: 80000,
              salaryMax: 120000,
              createdAt: new Date().toISOString()
            }))
          }
        }
      };

      renderWithProviders(<JobListings />, { mocks: [manyJobsMock] });

      await waitFor(() => {
        expect(screen.getByText('Job 1')).toBeInTheDocument();
      });

      // Check for pagination controls
      expect(screen.getByRole('button', { name: /next page/i })).toBeInTheDocument();
      expect(screen.getByText(/page 1 of/i)).toBeInTheDocument();
    });

    test('loads next page when next button is clicked', async () => {
      const user = userEvent.setup();
      const firstPageMock = {
        request: {
          query: GET_JOBS,
          variables: { limit: 10, offset: 0 }
        },
        result: {
          data: {
            jobs: [
              {
                id: 'job-1',
                title: 'First Page Job',
                company: { id: 'company-1', name: 'Company 1', industry: 'Technology' },
                location: 'Location 1',
                jobType: 'full_time',
                workArrangement: 'remote',
                salaryMin: 80000,
                salaryMax: 120000,
                createdAt: new Date().toISOString()
              }
            ]
          }
        }
      };

      const secondPageMock = {
        request: {
          query: GET_JOBS,
          variables: { limit: 10, offset: 10 }
        },
        result: {
          data: {
            jobs: [
              {
                id: 'job-2',
                title: 'Second Page Job',
                company: { id: 'company-2', name: 'Company 2', industry: 'Technology' },
                location: 'Location 2',
                jobType: 'full_time',
                workArrangement: 'remote',
                salaryMin: 90000,
                salaryMax: 130000,
                createdAt: new Date().toISOString()
              }
            ]
          }
        }
      };

      renderWithProviders(<JobListings />, { 
        mocks: [firstPageMock, secondPageMock] 
      });

      await waitFor(() => {
        expect(screen.getByText('First Page Job')).toBeInTheDocument();
      });

      const nextButton = screen.getByRole('button', { name: /next page/i });
      await user.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Second Page Job')).toBeInTheDocument();
        expect(screen.queryByText('First Page Job')).not.toBeInTheDocument();
      });
    });
  });

  describe('accessibility', () => {
    test('has proper heading structure', async () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      // Should have main heading
      expect(screen.getByRole('heading', { level: 1, name: /job listings|jobs/i }))
        .toBeInTheDocument();
    });

    test('job cards have proper accessibility attributes', async () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      await waitFor(() => {
        const jobCards = screen.getAllByRole('article');
        expect(jobCards).toHaveLength(2);

        jobCards.forEach(card => {
          expect(card).toHaveAttribute('tabindex', '0');
          expect(card).toHaveAccessibleName();
        });
      });
    });

    test('filter controls have proper labels', () => {
      const mocks = [commonMocks.GET_JOBS];

      renderWithProviders(<JobListings />, { mocks });

      const searchInput = screen.getByLabelText(/search jobs/i);
      expect(searchInput).toBeInTheDocument();

      const jobTypeFilter = screen.getByLabelText(/job type/i);
      expect(jobTypeFilter).toBeInTheDocument();
    });
  });
});