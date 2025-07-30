/**
 * Mock Service Worker (MSW) server setup for API mocking
 * Provides comprehensive API mocking for both REST and GraphQL endpoints
 */

import { setupServer } from 'msw/node';
import { rest, graphql } from 'msw';
import mockData from '../../fixtures/frontend/mockData.js';

// GraphQL Schema mocks
const graphqlHandlers = [
  // Authentication mutations
  graphql.mutation('LoginUser', (req, res, ctx) => {
    const { email, password } = req.variables;
    
    if (email === 'test@example.com' && password === 'password123') {
      return res(
        ctx.data({
          login: {
            success: true,
            token: 'mock-jwt-token',
            refreshToken: 'mock-refresh-token',
            user: mockData.users.currentUser
          }
        })
      );
    }
    
    return res(
      ctx.errors([
        {
          message: 'Invalid credentials',
          extensions: { code: 'INVALID_CREDENTIALS' }
        }
      ])
    );
  }),

  graphql.mutation('RegisterUser', (req, res, ctx) => {
    const { input } = req.variables;
    
    if (input.email === 'existing@example.com') {
      return res(
        ctx.errors([
          {
            message: 'User already exists',
            extensions: { code: 'USER_EXISTS' }
          }
        ])
      );
    }
    
    return res(
      ctx.data({
        register: {
          success: true,
          token: 'mock-jwt-token',
          refreshToken: 'mock-refresh-token',
          user: {
            ...mockData.users.currentUser,
            ...input,
            id: 'new-user-id'
          }
        }
      })
    );
  }),

  graphql.mutation('RefreshToken', (req, res, ctx) => {
    const { refreshToken } = req.variables;
    
    if (refreshToken === 'valid-refresh-token') {
      return res(
        ctx.data({
          refreshToken: {
            success: true,
            token: 'new-jwt-token',
            refreshToken: 'new-refresh-token'
          }
        })
      );
    }
    
    return res(
      ctx.errors([
        {
          message: 'Invalid refresh token',
          extensions: { code: 'INVALID_REFRESH_TOKEN' }
        }
      ])
    );
  }),

  // User queries
  graphql.query('GetCurrentUser', (req, res, ctx) => {
    const authHeader = req.headers.get('authorization');
    
    if (!authHeader || !authHeader.includes('Bearer')) {
      return res(
        ctx.errors([
          {
            message: 'Authentication required',
            extensions: { code: 'UNAUTHENTICATED' }
          }
        ])
      );
    }
    
    return res(
      ctx.data({
        me: mockData.users.currentUser
      })
    );
  }),

  graphql.query('GetUserProfile', (req, res, ctx) => {
    const { userId } = req.variables;
    
    if (userId === 'user-123') {
      return res(
        ctx.data({
          user: mockData.users.currentUser
        })
      );
    }
    
    return res(
      ctx.errors([
        {
          message: 'User not found',
          extensions: { code: 'USER_NOT_FOUND' }
        }
      ])
    );
  }),

  graphql.mutation('UpdateUserProfile', (req, res, ctx) => {
    const { input } = req.variables;
    
    return res(
      ctx.data({
        updateUser: {
          success: true,
          user: {
            ...mockData.users.currentUser,
            ...input,
            updatedAt: new Date().toISOString()
          }
        }
      })
    );
  }),

  // Job queries
  graphql.query('GetJobs', (req, res, ctx) => {
    const { filters, pagination } = req.variables;
    const jobs = mockData.generators.generateMockJobs(10);
    
    // Apply basic filtering
    let filteredJobs = jobs;
    
    if (filters?.location) {
      filteredJobs = filteredJobs.filter(job => 
        job.location.toLowerCase().includes(filters.location.toLowerCase())
      );
    }
    
    if (filters?.experienceLevel) {
      filteredJobs = filteredJobs.filter(job => 
        job.experienceLevel === filters.experienceLevel
      );
    }
    
    if (filters?.remoteOk !== undefined) {
      filteredJobs = filteredJobs.filter(job => 
        job.remoteOk === filters.remoteOk
      );
    }
    
    // Apply pagination
    const limit = pagination?.limit || 10;
    const offset = pagination?.offset || 0;
    const paginatedJobs = filteredJobs.slice(offset, offset + limit);
    
    return res(
      ctx.data({
        jobs: {
          items: paginatedJobs,
          totalCount: filteredJobs.length,
          hasNextPage: offset + limit < filteredJobs.length,
          hasPreviousPage: offset > 0
        }
      })
    );
  }),

  graphql.query('GetJob', (req, res, ctx) => {
    const { jobId } = req.variables;
    
    if (jobId === 'job-123') {
      return res(
        ctx.data({
          job: mockData.jobs.frontendJob
        })
      );
    }
    
    return res(
      ctx.errors([
        {
          message: 'Job not found',
          extensions: { code: 'JOB_NOT_FOUND' }
        }
      ])
    );
  }),

  graphql.mutation('CreateJob', (req, res, ctx) => {
    const { input } = req.variables;
    
    return res(
      ctx.data({
        createJob: {
          success: true,
          job: {
            id: 'new-job-id',
            ...input,
            status: 'draft',
            viewCount: 0,
            applicationCount: 0,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        }
      })
    );
  }),

  graphql.mutation('UpdateJob', (req, res, ctx) => {
    const { jobId, input } = req.variables;
    
    return res(
      ctx.data({
        updateJob: {
          success: true,
          job: {
            ...mockData.jobs.frontendJob,
            ...input,
            updatedAt: new Date().toISOString()
          }
        }
      })
    );
  }),

  // Job Application mutations and queries
  graphql.mutation('ApplyToJob', (req, res, ctx) => {
    const { input } = req.variables;
    
    return res(
      ctx.data({
        applyToJob: {
          success: true,
          application: {
            id: 'new-application-id',
            ...input,
            status: 'submitted',
            submittedAt: new Date().toISOString(),
            lastUpdatedAt: new Date().toISOString()
          }
        }
      })
    );
  }),

  graphql.query('GetUserApplications', (req, res, ctx) => {
    const { userId } = req.variables;
    
    return res(
      ctx.data({
        userApplications: [
          mockData.jobApplications.application1,
          mockData.jobApplications.application2
        ]
      })
    );
  }),

  graphql.mutation('UpdateApplicationStatus', (req, res, ctx) => {
    const { applicationId, status } = req.variables;
    
    return res(
      ctx.data({
        updateApplicationStatus: {
          success: true,
          application: {
            ...mockData.jobApplications.application1,
            status,
            lastUpdatedAt: new Date().toISOString()
          }
        }
      })
    );
  }),

  // Resume queries and mutations
  graphql.query('GetUserResumes', (req, res, ctx) => {
    const { userId } = req.variables;
    
    return res(
      ctx.data({
        userResumes: [mockData.resumes.primaryResume]
      })
    );
  }),

  graphql.mutation('CreateResume', (req, res, ctx) => {
    const { input } = req.variables;
    
    return res(
      ctx.data({
        createResume: {
          success: true,
          resume: {
            id: 'new-resume-id',
            ...input,
            version: 1,
            isDefault: false,
            status: 'draft',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        }
      })
    );
  }),

  graphql.mutation('UpdateResume', (req, res, ctx) => {
    const { resumeId, input } = req.variables;
    
    return res(
      ctx.data({
        updateResume: {
          success: true,
          resume: {
            ...mockData.resumes.primaryResume,
            ...input,
            updatedAt: new Date().toISOString()
          }
        }
      })
    );
  }),

  // AI Suggestions
  graphql.query('GetJobRecommendations', (req, res, ctx) => {
    const { userId } = req.variables;
    
    return res(
      ctx.data({
        jobRecommendations: mockData.aiSuggestions.jobRecommendations
      })
    );
  }),

  graphql.query('GetSkillsRecommendations', (req, res, ctx) => {
    const { userId } = req.variables;
    
    return res(
      ctx.data({
        skillsRecommendations: mockData.aiSuggestions.skillsRecommendations
      })
    );
  }),

  // Dashboard data
  graphql.query('GetDashboardData', (req, res, ctx) => {
    const { userId } = req.variables;
    
    return res(
      ctx.data({
        dashboard: mockData.dashboardData
      })
    );
  })
];

// REST API handlers for non-GraphQL endpoints
const restHandlers = [
  // File upload endpoints
  rest.post('/api/upload/resume', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        fileUrl: '/uploads/resumes/mock-resume.pdf',
        fileName: 'resume.pdf',
        fileSize: 245760
      })
    );
  }),

  rest.post('/api/upload/avatar', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        success: true,
        fileUrl: '/uploads/avatars/mock-avatar.jpg',
        fileName: 'avatar.jpg',
        fileSize: 102400
      })
    );
  }),

  // External API mocks
  rest.get('/api/external/jobs', (req, res, ctx) => {
    const location = req.url.searchParams.get('location');
    const query = req.url.searchParams.get('q');
    
    return res(
      ctx.status(200),
      ctx.json({
        jobs: mockData.generators.generateMockJobs(5),
        totalCount: 50
      })
    );
  }),

  // Company data
  rest.get('/api/companies/:companyId', (req, res, ctx) => {
    const { companyId } = req.params;
    
    if (companyId === 'company-123') {
      return res(
        ctx.status(200),
        ctx.json(mockData.companies.techcorp)
      );
    }
    
    return res(
      ctx.status(404),
      ctx.json({ error: 'Company not found' })
    );
  }),

  // Skills data
  rest.get('/api/skills/search', (req, res, ctx) => {
    const query = req.url.searchParams.get('q');
    
    const skills = [
      'JavaScript', 'TypeScript', 'React', 'Vue.js', 'Angular',
      'Node.js', 'Python', 'Django', 'Flask', 'Java', 'Spring',
      'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes'
    ];
    
    const filteredSkills = query 
      ? skills.filter(skill => 
          skill.toLowerCase().includes(query.toLowerCase())
        )
      : skills;
    
    return res(
      ctx.status(200),
      ctx.json({
        skills: filteredSkills.slice(0, 10)
      })
    );
  }),

  // Analytics endpoints
  rest.post('/api/analytics/track', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({ success: true })
    );
  }),

  // Health check
  rest.get('/health', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        status: 'healthy',
        timestamp: new Date().toISOString()
      })
    );
  }),

  // Error simulation endpoints for testing
  rest.get('/api/test/500', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({ error: 'Internal server error' })
    );
  }),

  rest.get('/api/test/network-error', (req, res, ctx) => {
    return res.networkError('Network error');
  }),

  rest.get('/api/test/timeout', (req, res, ctx) => {
    // Simulate timeout by not resolving
    return new Promise(() => {});
  })
];

// Create MSW server
export const server = setupServer(...graphqlHandlers, ...restHandlers);

// Export individual handlers for specific test scenarios
export const handlers = {
  graphql: graphqlHandlers,
  rest: restHandlers
};

// Utility functions for test scenarios
export const mockScenarios = {
  // Authentication scenarios
  validLogin: () => {
    server.use(
      graphql.mutation('LoginUser', (req, res, ctx) => {
        return res(
          ctx.data({
            login: {
              success: true,
              token: 'valid-token',
              refreshToken: 'valid-refresh-token',
              user: mockData.users.currentUser
            }
          })
        );
      })
    );
  },

  invalidLogin: () => {
    server.use(
      graphql.mutation('LoginUser', (req, res, ctx) => {
        return res(
          ctx.errors([
            {
              message: 'Invalid credentials',
              extensions: { code: 'INVALID_CREDENTIALS' }
            }
          ])
        );
      })
    );
  },

  expiredToken: () => {
    server.use(
      graphql.query('GetCurrentUser', (req, res, ctx) => {
        return res(
          ctx.errors([
            {
              message: 'Token expired',
              extensions: { code: 'TOKEN_EXPIRED' }
            }
          ])
        );
      })
    );
  },

  // Network error scenarios
  networkError: () => {
    server.use(
      rest.all('*', (req, res, ctx) => {
        return res.networkError('Network connection failed');
      })
    );
  },

  serverError: () => {
    server.use(
      rest.all('*', (req, res, ctx) => {
        return res(
          ctx.status(500),
          ctx.json({
            error: 'Internal server error',
            message: 'Something went wrong'
          })
        );
      })
    );
  },

  slowResponse: (delay = 5000) => {
    server.use(
      rest.all('*', (req, res, ctx) => {
        return res(
          ctx.delay(delay),
          ctx.status(200),
          ctx.json({ message: 'Slow response' })
        );
      })
    );
  },

  // Data scenarios
  emptyResults: () => {
    server.use(
      graphql.query('GetJobs', (req, res, ctx) => {
        return res(
          ctx.data({
            jobs: {
              items: [],
              totalCount: 0,
              hasNextPage: false,
              hasPreviousPage: false
            }
          })
        );
      })
    );
  },

  largeDataset: () => {
    server.use(
      graphql.query('GetJobs', (req, res, ctx) => {
        return res(
          ctx.data({
            jobs: {
              items: mockData.generators.generateMockJobs(100),
              totalCount: 1000,
              hasNextPage: true,
              hasPreviousPage: false
            }
          })
        );
      })
    );
  }
};

export default server;