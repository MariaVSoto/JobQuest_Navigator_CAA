/**
 * Mock data for frontend testing
 * Provides comprehensive test data that mirrors real application data
 */

import { faker } from '@faker-js/faker';

// User Mock Data
export const mockUsers = {
  currentUser: {
    id: 'user-123',
    email: 'john.doe@example.com',
    firstName: 'John',
    lastName: 'Doe',
    phone: '+1-555-0123',
    location: 'San Francisco, CA',
    bio: 'Senior software engineer with 8 years of experience in full-stack development.',
    website: 'https://johndoe.dev',
    linkedinUrl: 'https://linkedin.com/in/johndoe',
    githubUrl: 'https://github.com/johndoe',
    experienceLevel: 'senior',
    currentJobTitle: 'Senior Software Engineer',
    currentCompany: 'TechCorp Inc.',
    yearsOfExperience: 8,
    preferredSalaryMin: 120000,
    preferredSalaryMax: 180000,
    remotePreference: 'hybrid',
    willingToRelocate: false,
    skills: ['JavaScript', 'React', 'Node.js', 'Python', 'PostgreSQL', 'AWS', 'Docker'],
    certifications: ['AWS Certified Solutions Architect', 'Google Cloud Professional'],
    isActive: true,
    isVerified: true,
    profileVisibility: 'public',
    emailNotifications: true,
    jobAlerts: true,
    createdAt: '2023-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    lastLogin: '2024-01-20T08:30:00Z'
  },

  testUser: {
    id: 'user-456',
    email: 'jane.smith@example.com',
    firstName: 'Jane',
    lastName: 'Smith',
    phone: '+1-555-0456',
    location: 'New York, NY',
    bio: 'Product manager with a passion for user experience and data-driven decisions.',
    experienceLevel: 'mid',
    currentJobTitle: 'Product Manager',
    currentCompany: 'StartupXYZ',
    yearsOfExperience: 5,
    preferredSalaryMin: 90000,
    preferredSalaryMax: 130000,
    remotePreference: 'remote',
    willingToRelocate: true,
    skills: ['Product Management', 'Agile', 'SQL', 'Analytics', 'User Research'],
    certifications: ['Certified Scrum Product Owner'],
    isActive: true,
    isVerified: true,
    profileVisibility: 'private',
    emailNotifications: false,
    jobAlerts: true,
    createdAt: '2023-06-10T14:20:00Z',
    updatedAt: '2024-01-10T16:45:00Z',
    lastLogin: '2024-01-19T12:15:00Z'
  },

  adminUser: {
    id: 'admin-001',
    email: 'admin@jobquest.com',
    firstName: 'Admin',
    lastName: 'User',
    phone: '+1-555-0001',
    location: 'Remote',
    bio: 'Platform administrator',
    experienceLevel: 'executive',
    isActive: true,
    isAdmin: true,
    isVerified: true,
    createdAt: '2022-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    lastLogin: '2024-01-20T09:00:00Z'
  }
};

// Job Mock Data
export const mockJobs = {
  frontendJob: {
    id: 'job-123',
    title: 'Senior Frontend Developer',
    description: 'We are looking for a senior frontend developer to join our growing team. You will be responsible for building user-facing applications using modern JavaScript frameworks.',
    company: 'TechCorp Inc.',
    department: 'Engineering',
    location: 'San Francisco, CA',
    country: 'United States',
    remoteOk: true,
    hybridOk: true,
    jobType: 'full_time',
    experienceLevel: 'senior',
    educationLevel: 'bachelors',
    salaryMin: 130000,
    salaryMax: 180000,
    salaryCurrency: 'USD',
    equityMin: 0.1,
    equityMax: 0.5,
    skillsRequired: ['JavaScript', 'React', 'TypeScript', 'CSS', 'HTML'],
    skillsPreferred: ['Vue.js', 'GraphQL', 'Jest', 'Cypress'],
    languagesRequired: ['English'],
    languagesPreferred: ['Spanish'],
    benefits: ['Health Insurance', '401k Match', 'Unlimited PTO', 'Stock Options', 'Remote Work'],
    applicationDeadline: '2024-03-01T23:59:59Z',
    applicationUrl: 'https://techcorp.com/careers/senior-frontend-developer',
    contactEmail: 'hiring@techcorp.com',
    status: 'published',
    isFeatured: true,
    viewCount: 245,
    applicationCount: 12,
    slug: 'senior-frontend-developer-2024',
    tags: ['startup', 'saas', 'remote-friendly'],
    createdById: 'user-789',
    companyId: 'company-123',
    createdAt: '2024-01-10T10:00:00Z',
    updatedAt: '2024-01-15T14:30:00Z'
  },

  backendJob: {
    id: 'job-456',
    title: 'Backend Engineer',
    description: 'Join our backend team to build scalable APIs and microservices. Experience with Python and cloud technologies required.',
    company: 'CloudTech Solutions',
    department: 'Engineering',
    location: 'Austin, TX',
    country: 'United States',
    remoteOk: false,
    hybridOk: true,
    jobType: 'full_time',
    experienceLevel: 'mid',
    educationLevel: 'bachelors',
    salaryMin: 90000,
    salaryMax: 130000,
    salaryCurrency: 'USD',
    skillsRequired: ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker'],
    skillsPreferred: ['Kubernetes', 'Redis', 'GraphQL'],
    languagesRequired: ['English'],
    benefits: ['Health Insurance', '401k', 'PTO', 'Learning Budget'],
    applicationDeadline: '2024-02-15T23:59:59Z',
    status: 'published',
    isFeatured: false,
    viewCount: 89,
    applicationCount: 7,
    slug: 'backend-engineer-austin',
    tags: ['cloud', 'microservices'],
    createdById: 'user-790',
    companyId: 'company-456',
    createdAt: '2024-01-05T09:00:00Z',
    updatedAt: '2024-01-12T11:15:00Z'
  },

  remoteJob: {
    id: 'job-789',
    title: 'Full Stack Developer (Remote)',
    description: 'Remote-first company seeking a full stack developer to work on our customer-facing platform.',
    company: 'RemoteFirst Corp',
    department: 'Product Engineering',
    location: 'Remote',
    country: 'United States',
    remoteOk: true,
    hybridOk: false,
    jobType: 'full_time',
    experienceLevel: 'mid',
    educationLevel: 'bachelors',
    salaryMin: 100000,
    salaryMax: 140000,
    salaryCurrency: 'USD',
    skillsRequired: ['JavaScript', 'React', 'Node.js', 'MongoDB'],
    skillsPreferred: ['TypeScript', 'AWS', 'Docker'],
    languagesRequired: ['English'],
    benefits: ['Health Insurance', 'Unlimited PTO', 'Home Office Budget', 'Stock Options'],
    applicationDeadline: '2024-02-28T23:59:59Z',
    status: 'published',
    isFeatured: true,
    viewCount: 156,
    applicationCount: 23,
    slug: 'full-stack-developer-remote',
    tags: ['remote', 'full-stack', 'startup'],
    createdById: 'user-791',
    companyId: 'company-789',
    createdAt: '2024-01-08T16:00:00Z',
    updatedAt: '2024-01-18T10:20:00Z'
  }
};

// Generate additional jobs for testing
export const generateMockJobs = (count = 10) => {
  return Array.from({ length: count }, (_, index) => ({
    id: `job-${1000 + index}`,
    title: faker.person.jobTitle(),
    description: faker.lorem.paragraphs(3),
    company: faker.company.name(),
    department: faker.helpers.arrayElement(['Engineering', 'Product', 'Design', 'Marketing', 'Sales']),
    location: faker.location.city(),
    country: 'United States',
    remoteOk: faker.datatype.boolean(),
    hybridOk: faker.datatype.boolean(),
    jobType: faker.helpers.arrayElement(['full_time', 'part_time', 'contract', 'internship']),
    experienceLevel: faker.helpers.arrayElement(['entry', 'junior', 'mid', 'senior', 'lead']),
    educationLevel: faker.helpers.arrayElement(['high_school', 'associates', 'bachelors', 'masters', 'phd']),
    salaryMin: faker.number.int({ min: 50000, max: 120000 }),
    salaryMax: faker.number.int({ min: 120000, max: 200000 }),
    salaryCurrency: 'USD',
    skillsRequired: faker.helpers.arrayElements(
      ['JavaScript', 'Python', 'React', 'Node.js', 'Java', 'C++', 'SQL', 'AWS', 'Docker'],
      { min: 3, max: 6 }
    ),
    skillsPreferred: faker.helpers.arrayElements(
      ['TypeScript', 'GraphQL', 'Kubernetes', 'MongoDB', 'Redis'],
      { min: 0, max: 3 }
    ),
    languagesRequired: ['English'],
    benefits: faker.helpers.arrayElements(
      ['Health Insurance', '401k', 'PTO', 'Stock Options', 'Remote Work', 'Learning Budget'],
      { min: 2, max: 5 }
    ),
    applicationDeadline: faker.date.future().toISOString(),
    status: faker.helpers.arrayElement(['published', 'draft', 'closed']),
    isFeatured: faker.datatype.boolean({ probability: 0.2 }),
    viewCount: faker.number.int({ min: 0, max: 500 }),
    applicationCount: faker.number.int({ min: 0, max: 50 }),
    slug: faker.helpers.slugify(`${faker.person.jobTitle()}-${faker.number.int({ min: 1000, max: 9999 })}`),
    tags: faker.helpers.arrayElements(['startup', 'enterprise', 'remote', 'fintech', 'saas'], { min: 1, max: 3 }),
    createdById: `user-${faker.number.int({ min: 100, max: 999 })}`,
    companyId: `company-${faker.number.int({ min: 100, max: 999 })}`,
    createdAt: faker.date.past().toISOString(),
    updatedAt: faker.date.recent().toISOString()
  }));
};

// Job Application Mock Data
export const mockJobApplications = {
  application1: {
    id: 'app-123',
    userId: 'user-123',
    jobId: 'job-123',
    resumeId: 'resume-123',
    status: 'submitted',
    coverLetter: 'I am excited to apply for the Senior Frontend Developer position...',
    customResume: false,
    questionResponses: {
      'Why are you interested in this role?': 'I am passionate about frontend development and excited about the opportunity to work with modern technologies.',
      'What makes you a good fit?': 'My 8 years of experience with React and JavaScript, combined with my leadership skills, make me an ideal candidate.',
      'Salary expectations?': '$150k - $170k'
    },
    submittedAt: '2024-01-15T14:30:00Z',
    lastUpdatedAt: '2024-01-15T14:30:00Z',
    interviewRounds: 3,
    currentRound: 1,
    nextInterviewDate: '2024-01-25T10:00:00Z',
    recruiterNotes: 'Strong technical background, good communication skills',
    candidateNotes: 'Really interested in this role, company culture seems great',
    responseTimeHours: 24,
    source: 'direct_application'
  },

  application2: {
    id: 'app-456',
    userId: 'user-456',
    jobId: 'job-456',
    resumeId: 'resume-456',
    status: 'interview_scheduled',
    coverLetter: 'As a product manager with 5 years of experience...',
    customResume: true,
    questionResponses: {
      'Why are you interested in this role?': 'The backend engineering challenges align perfectly with my career goals.',
      'What makes you a good fit?': 'My experience with Python and cloud technologies.'
    },
    submittedAt: '2024-01-12T09:15:00Z',
    lastUpdatedAt: '2024-01-18T16:20:00Z',
    interviewRounds: 4,
    currentRound: 2,
    nextInterviewDate: '2024-01-22T14:00:00Z',
    recruiterNotes: 'Impressed with technical assessment, moving to next round',
    candidateNotes: 'Technical interview went well, looking forward to team interview',
    responseTimeHours: 48,
    source: 'job_board'
  }
};

// Resume Mock Data
export const mockResumes = {
  primaryResume: {
    id: 'resume-123',
    userId: 'user-123',
    title: 'Senior Software Engineer Resume',
    content: {
      personalInfo: {
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+1-555-0123',
        location: 'San Francisco, CA',
        website: 'https://johndoe.dev',
        linkedin: 'https://linkedin.com/in/johndoe',
        github: 'https://github.com/johndoe'
      },
      summary: 'Senior software engineer with 8 years of experience in full-stack development, specializing in React, Node.js, and cloud technologies.',
      experience: [
        {
          title: 'Senior Software Engineer',
          company: 'TechCorp Inc.',
          location: 'San Francisco, CA',
          startDate: '2021-03-01',
          endDate: 'present',
          description: 'Lead development of customer-facing web applications using React and Node.js.',
          achievements: [
            'Improved application performance by 40% through code optimization',
            'Led team of 4 developers on major product redesign',
            'Implemented CI/CD pipeline reducing deployment time by 60%'
          ]
        },
        {
          title: 'Software Engineer',
          company: 'StartupXYZ',
          location: 'San Francisco, CA',
          startDate: '2019-01-15',
          endDate: '2021-02-28',
          description: 'Developed and maintained full-stack web applications.',
          achievements: [
            'Built RESTful APIs serving 100k+ daily requests',
            'Reduced bug reports by 50% through comprehensive testing',
            'Mentored 2 junior developers'
          ]
        }
      ],
      education: [
        {
          degree: 'BS Computer Science',
          school: 'University of California, Berkeley',
          location: 'Berkeley, CA',
          graduationDate: '2018-05-15',
          gpa: 3.8
        }
      ],
      skills: {
        technical: [
          'JavaScript', 'TypeScript', 'React', 'Node.js', 'Python',
          'PostgreSQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes'
        ],
        soft: [
          'Leadership', 'Communication', 'Problem Solving',
          'Team Collaboration', 'Project Management'
        ]
      },
      projects: [
        {
          name: 'E-commerce Platform',
          description: 'Full-stack e-commerce platform built with React and Node.js',
          technologies: ['React', 'Node.js', 'PostgreSQL', 'Stripe API'],
          url: 'https://ecommerce-demo.johndoe.dev',
          github: 'https://github.com/johndoe/ecommerce-platform'
        },
        {
          name: 'Task Management App',
          description: 'Real-time collaborative task management application',
          technologies: ['React', 'Socket.io', 'MongoDB', 'Express'],
          url: 'https://taskapp.johndoe.dev',
          github: 'https://github.com/johndoe/task-manager'
        }
      ],
      certifications: [
        {
          name: 'AWS Certified Solutions Architect',
          issuer: 'Amazon Web Services',
          date: '2023-06-15',
          credentialId: 'AWS-CSA-123456'
        },
        {
          name: 'Google Cloud Professional Developer',
          issuer: 'Google Cloud',
          date: '2022-09-20',
          credentialId: 'GCP-PD-789012'
        }
      ],
      languages: [
        {
          language: 'English',
          proficiency: 'Native'
        },
        {
          language: 'Spanish',
          proficiency: 'Intermediate'
        }
      ]
    },
    version: 3,
    isDefault: true,
    isPublic: false,
    filePath: '/resumes/user-123/resume-123.pdf',
    fileSize: 245760,
    fileType: 'application/pdf',
    viewCount: 45,
    downloadCount: 12,
    lastViewedAt: '2024-01-18T10:30:00Z',
    aiScore: 87,
    aiSuggestions: [
      'Add more quantified achievements',
      'Include relevant keywords for target roles',
      'Consider adding a professional summary section'
    ],
    keywordsMatched: ['JavaScript', 'React', 'Node.js', 'AWS', 'Leadership'],
    status: 'active',
    createdAt: '2024-01-01T12:00:00Z',
    updatedAt: '2024-01-15T16:45:00Z'
  }
};

// Company Mock Data
export const mockCompanies = {
  techcorp: {
    id: 'company-123',
    name: 'TechCorp Inc.',
    slug: 'techcorp-inc',
    description: 'Leading technology company focused on innovative software solutions.',
    website: 'https://techcorp.com',
    email: 'contact@techcorp.com',
    phone: '+1-555-0100',
    headquarters: 'San Francisco, CA',
    country: 'United States',
    locations: ['San Francisco, CA', 'New York, NY', 'Austin, TX'],
    industry: 'Technology',
    companySize: '201-500',
    foundedYear: 2015,
    linkedinUrl: 'https://linkedin.com/company/techcorp-inc',
    twitterUrl: 'https://twitter.com/techcorp',
    githubUrl: 'https://github.com/techcorp',
    values: ['Innovation', 'Integrity', 'Collaboration', 'Excellence'],
    benefits: [
      'Health Insurance', '401k Match', 'Unlimited PTO',
      'Stock Options', 'Remote Work', 'Learning Budget'
    ],
    glassdoorRating: 4.2,
    indeedRating: 4.0,
    isVerified: true,
    isHiring: true,
    logoUrl: 'https://logo.clearbit.com/techcorp.com',
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z'
  }
};

// AI Suggestions Mock Data
export const mockAISuggestions = {
  jobRecommendations: [
    {
      id: 'suggestion-1',
      jobId: 'job-123',
      job: mockJobs.frontendJob,
      matchScore: 0.95,
      reasons: [
        'Strong match with React and JavaScript skills',
        'Salary range aligns with preferences',
        'Company size matches preference',
        'Remote work available'
      ],
      skillsMatched: ['JavaScript', 'React', 'TypeScript'],
      skillsGaps: ['Vue.js', 'GraphQL'],
      confidenceLevel: 'high'
    },
    {
      id: 'suggestion-2',
      jobId: 'job-789',
      job: mockJobs.remoteJob,
      matchScore: 0.87,
      reasons: [
        'Full remote position matches preference',
        'Tech stack includes preferred technologies',
        'Experience level is appropriate'
      ],
      skillsMatched: ['JavaScript', 'React', 'Node.js'],
      skillsGaps: ['MongoDB'],
      confidenceLevel: 'medium'
    }
  ],

  skillsRecommendations: [
    {
      id: 'skill-rec-1',
      skill: 'TypeScript',
      priority: 'high',
      reason: 'High demand in your target job market',
      marketDemand: 0.78,
      salaryImpact: 15000,
      learningResources: [
        {
          title: 'TypeScript Handbook',
          url: 'https://typescriptlang.org/docs',
          type: 'documentation'
        },
        {
          title: 'TypeScript Course',
          url: 'https://udemy.com/typescript',
          type: 'course'
        }
      ]
    },
    {
      id: 'skill-rec-2',
      skill: 'GraphQL',
      priority: 'medium',
      reason: 'Emerging technology in your field',
      marketDemand: 0.45,
      salaryImpact: 8000,
      learningResources: [
        {
          title: 'GraphQL Tutorial',
          url: 'https://graphql.org/learn',
          type: 'tutorial'
        }
      ]
    }
  ],

  careerPaths: [
    {
      id: 'path-1',
      title: 'Senior Frontend Developer → Tech Lead',
      timeframe: '2-3 years',
      steps: [
        'Gain team leadership experience',
        'Develop system architecture skills',
        'Learn project management',
        'Mentor junior developers'
      ],
      requiredSkills: ['Leadership', 'System Design', 'Project Management'],
      salaryRange: { min: 160000, max: 220000 }
    },
    {
      id: 'path-2',
      title: 'Senior Frontend Developer → Full Stack Architect',
      timeframe: '3-4 years',
      steps: [
        'Strengthen backend development skills',
        'Learn cloud architecture',
        'Gain DevOps experience',
        'Study system design patterns'
      ],
      requiredSkills: ['Backend Development', 'Cloud Architecture', 'DevOps'],
      salaryRange: { min: 180000, max: 250000 }
    }
  ]
};

// Interview Preparation Mock Data
export const mockInterviewData = {
  questions: [
    {
      id: 'q-1',
      question: 'Tell me about yourself',
      category: 'behavioral',
      difficulty: 'easy',
      tips: [
        'Keep it professional and relevant',
        'Focus on your career journey',
        'Connect to the role you\'re applying for'
      ],
      sampleAnswer: 'I\'m a senior software engineer with 8 years of experience...'
    },
    {
      id: 'q-2',
      question: 'What is the virtual DOM in React?',
      category: 'technical',
      difficulty: 'medium',
      tips: [
        'Explain the concept clearly',
        'Mention performance benefits',
        'Provide a simple example'
      ],
      sampleAnswer: 'The virtual DOM is a JavaScript representation of the actual DOM...'
    }
  ],

  practiceInterviews: [
    {
      id: 'practice-1',
      title: 'Frontend Developer Technical Interview',
      duration: 45,
      questions: ['q-1', 'q-2'],
      completedAt: '2024-01-15T14:00:00Z',
      score: 85,
      feedback: 'Good technical knowledge, work on explaining concepts more clearly'
    }
  ]
};

// Skills and Certifications Mock Data
export const mockSkillsData = {
  userSkills: [
    {
      id: 'skill-1',
      name: 'JavaScript',
      category: 'Programming Language',
      proficiency: 'expert',
      yearsOfExperience: 8,
      lastUsed: '2024-01-20',
      verified: true,
      endorsements: 15
    },
    {
      id: 'skill-2',
      name: 'React',
      category: 'Framework',
      proficiency: 'expert',
      yearsOfExperience: 6,
      lastUsed: '2024-01-20',
      verified: true,
      endorsements: 12
    },
    {
      id: 'skill-3',
      name: 'Python',
      category: 'Programming Language',
      proficiency: 'intermediate',
      yearsOfExperience: 3,
      lastUsed: '2024-01-10',
      verified: false,
      endorsements: 5
    }
  ],

  availableCertifications: [
    {
      id: 'cert-1',
      name: 'AWS Certified Solutions Architect',
      provider: 'Amazon Web Services',
      category: 'Cloud Computing',
      difficulty: 'intermediate',
      duration: '130 minutes',
      cost: 150,
      validityYears: 3,
      description: 'Validates expertise in designing distributed systems on AWS',
      prerequisites: ['AWS fundamentals', '1+ years AWS experience'],
      studyMaterials: [
        {
          title: 'AWS Training',
          url: 'https://aws.amazon.com/training',
          type: 'official'
        }
      ]
    }
  ],

  skillsGapAnalysis: {
    targetRole: 'Senior Frontend Developer',
    currentSkills: ['JavaScript', 'React', 'CSS'],
    requiredSkills: ['JavaScript', 'React', 'TypeScript', 'GraphQL', 'Testing'],
    missingSkills: ['TypeScript', 'GraphQL', 'Testing'],
    recommendations: [
      {
        skill: 'TypeScript',
        priority: 'high',
        estimatedLearningTime: '2-3 weeks'
      },
      {
        skill: 'GraphQL',
        priority: 'medium',
        estimatedLearningTime: '1-2 weeks'
      }
    ]
  }
};

// Dashboard Mock Data
export const mockDashboardData = {
  stats: {
    totalApplications: 15,
    activeApplications: 8,
    interviewsScheduled: 3,
    jobsViewed: 127,
    profileViews: 34,
    resumeDownloads: 12
  },

  recentActivity: [
    {
      id: 'activity-1',
      type: 'application_submitted',
      description: 'Applied to Senior Frontend Developer at TechCorp Inc.',
      timestamp: '2024-01-18T10:30:00Z',
      metadata: {
        jobId: 'job-123',
        jobTitle: 'Senior Frontend Developer',
        company: 'TechCorp Inc.'
      }
    },
    {
      id: 'activity-2',
      type: 'interview_scheduled',
      description: 'Interview scheduled for Backend Engineer position',
      timestamp: '2024-01-17T15:45:00Z',
      metadata: {
        jobId: 'job-456',
        interviewDate: '2024-01-25T10:00:00Z'
      }
    },
    {
      id: 'activity-3',
      type: 'profile_viewed',
      description: 'Your profile was viewed by a recruiter',
      timestamp: '2024-01-16T09:20:00Z',
      metadata: {
        viewerCompany: 'StartupXYZ'
      }
    }
  ],

  upcomingEvents: [
    {
      id: 'event-1',
      type: 'interview',
      title: 'Technical Interview - TechCorp Inc.',
      date: '2024-01-25T10:00:00Z',
      duration: 60,
      location: 'Video call',
      preparation: [
        'Review React concepts',
        'Practice coding problems',
        'Research company background'
      ]
    },
    {
      id: 'event-2',
      type: 'application_deadline',
      title: 'Application deadline - Full Stack Developer',
      date: '2024-01-28T23:59:59Z',
      company: 'RemoteFirst Corp'
    }
  ]
};

// Error mock data for testing error states
export const mockErrors = {
  networkError: {
    message: 'Network error occurred',
    code: 'NETWORK_ERROR',
    details: 'Please check your internet connection'
  },
  
  authError: {
    message: 'Authentication failed',
    code: 'AUTH_ERROR',
    details: 'Please log in again'
  },
  
  validationError: {
    message: 'Validation failed',
    code: 'VALIDATION_ERROR',
    details: 'Please check the form fields',
    fieldErrors: {
      email: 'Invalid email format',
      password: 'Password must be at least 8 characters'
    }
  },
  
  serverError: {
    message: 'Internal server error',
    code: 'SERVER_ERROR',
    details: 'Something went wrong on our end'
  }
};

// Utility functions for generating dynamic mock data
export const generateMockUser = (overrides = {}) => ({
  id: faker.string.uuid(),
  email: faker.internet.email(),
  firstName: faker.person.firstName(),
  lastName: faker.person.lastName(),
  phone: faker.phone.number(),
  location: faker.location.city(),
  bio: faker.lorem.paragraph(),
  experienceLevel: faker.helpers.arrayElement(['entry', 'junior', 'mid', 'senior', 'lead']),
  skills: faker.helpers.arrayElements(
    ['JavaScript', 'Python', 'React', 'Node.js', 'Java', 'C++'],
    { min: 3, max: 8 }
  ),
  isActive: true,
  isVerified: faker.datatype.boolean(),
  createdAt: faker.date.past().toISOString(),
  updatedAt: faker.date.recent().toISOString(),
  ...overrides
});

export const generateMockJobApplication = (overrides = {}) => ({
  id: faker.string.uuid(),
  userId: faker.string.uuid(),
  jobId: faker.string.uuid(),
  status: faker.helpers.arrayElement([
    'draft', 'submitted', 'under_review', 'interview_scheduled',
    'interviewed', 'offer_made', 'accepted', 'rejected', 'withdrawn'
  ]),
  coverLetter: faker.lorem.paragraphs(2),
  submittedAt: faker.date.past().toISOString(),
  lastUpdatedAt: faker.date.recent().toISOString(),
  ...overrides
});

// Export all mock data
export default {
  users: mockUsers,
  jobs: mockJobs,
  jobApplications: mockJobApplications,
  resumes: mockResumes,
  companies: mockCompanies,
  aiSuggestions: mockAISuggestions,
  interviewData: mockInterviewData,
  skillsData: mockSkillsData,
  dashboardData: mockDashboardData,
  errors: mockErrors,
  generators: {
    generateMockJobs,
    generateMockUser,
    generateMockJobApplication
  }
};