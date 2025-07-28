/**
 * Enhanced Fallback Service
 * Centralized mock data provider with consistent structure
 * Works with FallbackManager for unified error handling
 */

export class FallbackService {
  static isDevBypass() {
    return process.env.NODE_ENV === 'development' && 
           process.env.REACT_APP_DEV_AUTH_BYPASS === 'true';
  }

  // Mock user data
  static getMockUser() {
    return {
      id: 'mock-user-id',
      email: 'demo@jobquest.com',
      full_name: 'Demo User',
      career_level: 'mid',
      preferred_roles: ['Frontend Developer', 'Full Stack Engineer'],
      location_preference: 'Los Angeles, CA',
      remote_preference: 'hybrid',
      salary_expectation_min: 80000,
      salary_expectation_max: 120000,
      profile_completed: true,
      created_at: new Date().toISOString()
    };
  }

  // Mock job data
  static getMockJobs() {
    return [
      {
        id: '1',
        title: 'Senior React Developer',
        company: { display_name: 'Tech Innovations Inc' },
        location: { display_name: 'Los Angeles, CA' },
        description: 'We are looking for a skilled React developer to join our team...',
        salary_min: 90000,
        salary_max: 120000,
        created: '2025-07-01T10:00:00Z',
        category: { label: 'Software Development' },
        isSaved: false,
        isApplied: false
      },
      {
        id: '2',
        title: 'Full Stack Engineer',
        company: { display_name: 'StartupXYZ' },
        location: { display_name: 'San Francisco, CA' },
        description: 'Join our fast-growing startup as a full stack engineer...',
        salary_min: 100000,
        salary_max: 140000,
        created: '2025-07-02T14:30:00Z',
        category: { label: 'Software Development' },
        isSaved: true,
        isApplied: false
      },
      {
        id: '3',
        title: 'Frontend Developer',
        company: { display_name: 'Digital Agency Co' },
        location: { display_name: 'Remote' },
        description: 'Remote frontend developer position with flexible hours...',
        salary_min: 75000,
        salary_max: 95000,
        created: '2025-07-03T09:15:00Z',
        category: { label: 'Software Development' },
        isSaved: false,
        isApplied: true
      }
    ];
  }

  // Mock AI suggestions
  static getMockAISuggestions() {
    return {
      jobMatches: [
        {
          job: {
            id: '1',
            title: 'Senior React Developer',
            company: 'Tech Innovations Inc',
            matchScore: 95
          },
          reasons: ['Strong React experience', 'Location match', 'Salary range fits']
        },
        {
          job: {
            id: '2',
            title: 'Full Stack Engineer', 
            company: 'StartupXYZ',
            matchScore: 88
          },
          reasons: ['Full stack skills', 'Startup experience preferred']
        }
      ],
      skillImprovements: [
        {
          skill: 'TypeScript',
          priority: 'high',
          reason: '85% of matching jobs require TypeScript',
          resources: ['TypeScript Handbook', 'Practice Projects']
        },
        {
          skill: 'Node.js',
          priority: 'medium',
          reason: 'Expands backend capabilities',
          resources: ['Node.js Documentation', 'Express.js Tutorial']
        }
      ],
      careerTips: [
        'Consider highlighting your React expertise in your profile',
        'Add portfolio projects showcasing full-stack capabilities',
        'Network with professionals in the Los Angeles tech scene'
      ]
    };
  }

  // Mock user applications
  static getMockApplications() {
    return [
      {
        id: '1',
        job: {
          id: '3',
          title: 'Frontend Developer',
          company: 'Digital Agency Co'
        },
        status: 'applied',
        appliedDate: '2025-07-03T10:00:00Z',
        lastUpdated: '2025-07-03T10:00:00Z',
        notes: 'Applied through company website'
      }
    ];
  }

  // Mock saved jobs
  static getMockSavedJobs() {
    return [
      {
        id: '1',
        job: {
          id: '2',
          title: 'Full Stack Engineer',
          company: 'StartupXYZ',
          location: 'San Francisco, CA'
        },
        savedDate: '2025-07-02T15:00:00Z'
      }
    ];
  }

  // Mock skills data
  static getMockSkills() {
    return {
      userSkills: [
        { name: 'React', level: 'expert', years: 4 },
        { name: 'JavaScript', level: 'expert', years: 5 },
        { name: 'CSS', level: 'advanced', years: 5 },
        { name: 'Python', level: 'intermediate', years: 2 },
        { name: 'Django', level: 'intermediate', years: 2 }
      ],
      recommendedSkills: [
        { name: 'TypeScript', demand: 'high', avgSalaryIncrease: 15000 },
        { name: 'Node.js', demand: 'high', avgSalaryIncrease: 12000 },
        { name: 'AWS', demand: 'medium', avgSalaryIncrease: 18000 }
      ]
    };
  }

  // Mock interview data
  static getMockInterviewData() {
    return {
      upcomingInterviews: [],
      practiceQuestions: [
        {
          question: 'Explain the difference between React hooks and class components',
          category: 'React',
          difficulty: 'medium'
        },
        {
          question: 'How would you optimize a slow React application?',
          category: 'Performance',
          difficulty: 'hard'
        }
      ],
      tips: [
        'Research the company thoroughly before the interview',
        'Prepare specific examples of your past work',
        'Practice coding problems on a whiteboard'
      ]
    };
  }

  // Mock company research data
  static getMockCompanyResearch() {
    return {
      results: [
        {
          id: 'mock-research-1',
          companyName: 'Tech Innovations Inc',
          industry: 'Technology',
          size: '500-1000 employees',
          culture: 'Innovation-focused, collaborative environment',
          benefits: ['Health insurance', 'Remote work', '401k matching'],
          recentNews: ['Raised Series B funding', 'Launched new product line'],
          interviewProcess: 'Technical screening, coding challenge, final interview'
        }
      ]
    };
  }

  // Mock certifications data
  static getMockCertifications() {
    return {
      results: [
        {
          id: 'mock-cert-1',
          name: 'AWS Certified Developer',
          provider: 'Amazon Web Services',
          status: 'in_progress',
          completionDate: null,
          expiryDate: null,
          credentialUrl: null
        }
      ]
    };
  }

  // Mock learning paths data
  static getMockLearningPaths() {
    return {
      results: [
        {
          id: 'frontend-dev',
          title: 'Frontend Development Mastery',
          description: 'Complete frontend development learning path',
          duration: '3-6 months',
          difficulty: 'intermediate',
          progress: 65,
          modules: ['HTML/CSS', 'JavaScript', 'React', 'TypeScript'],
          nextModule: 'TypeScript Fundamentals'
        }
      ]
    };
  }

  // Helper method to create consistent API responses
  static createMockResponse(data, operationName = 'operation') {
    return {
      success: true,
      data: data,
      message: `Mock ${operationName} - using fallback data`,
      timestamp: new Date().toISOString()
    };
  }

  // Helper method to create consistent list responses
  static createMockListResponse(items, operationName = 'list') {
    return {
      results: items,
      count: items.length,
      message: `Mock ${operationName} - using fallback data`,
      timestamp: new Date().toISOString()
    };
  }
}

// Export both class and singleton instance
export const fallbackService = new FallbackService();
export default FallbackService;