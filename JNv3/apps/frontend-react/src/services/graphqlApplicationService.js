/**
 * GraphQL Application Service for JobQuest Navigator v2
 * Handles all application-related operations via GraphQL queries and mutations
 */

import { gql } from '@apollo/client';
import apolloClient from '../apolloClient';

// GraphQL Queries
const GET_APPLICATIONS_QUERY = gql`
  query GetApplications(
    $userId: String
    $status: String
    $limit: Int
    $offset: Int
  ) {
    applications(
      userId: $userId
      status: $status
      limit: $limit
      offset: $offset
    ) {
      id
      userId
      jobId
      status
      appliedDate
      lastUpdated
      coverLetter
      notes
      optimizedResumeData
      aiSuggestions
      skillsAnalysis
      job {
        id
        title
        description
        locationText
        salaryMin
        salaryMax
        salaryCurrency
        jobType
        experienceLevel
        remoteType
        company {
          id
          name
          industry
        }
      }
    }
  }
`;

const GET_APPLICATION_QUERY = gql`
  query GetApplication($id: String!) {
    application(id: $id) {
      id
      userId
      jobId
      status
      appliedDate
      lastUpdated
      coverLetter
      notes
      optimizedResumeData
      aiSuggestions
      skillsAnalysis
      job {
        id
        title
        description
        locationText
        salaryMin
        salaryMax
        salaryCurrency
        jobType
        experienceLevel
        remoteType
        company {
          id
          name
          industry
        }
      }
    }
  }
`;

const GET_SAVED_JOBS_QUERY = gql`
  query GetSavedJobs(
    $userId: String
    $limit: Int
    $offset: Int
  ) {
    savedJobs(
      userId: $userId
      limit: $limit
      offset: $offset
    ) {
      id
      userId
      jobId
      savedDate
      notes
      job {
        id
        title
        description
        locationText
        salaryMin
        salaryMax
        salaryCurrency
        jobType
        experienceLevel
        remoteType
        company {
          id
          name
          industry
        }
      }
    }
  }
`;

// GraphQL Mutations
const CREATE_APPLICATION_MUTATION = gql`
  mutation CreateApplication($input: CreateApplicationInput!) {
    createApplication(input: $input) {
      success
      applicationId
      application {
        id
        status
        appliedDate
        coverLetter
        notes
        job {
          id
          title
          company {
            name
          }
        }
      }
      errors
    }
  }
`;

const UPDATE_APPLICATION_MUTATION = gql`
  mutation UpdateApplication($applicationId: String!, $input: UpdateApplicationInput!) {
    updateApplication(applicationId: $applicationId, input: $input) {
      success
      applicationId
      application {
        id
        status
        lastUpdated
        coverLetter
        notes
        job {
          id
          title
          company {
            name
          }
        }
      }
      errors
    }
  }
`;

const SAVE_JOB_MUTATION = gql`
  mutation SaveJob($input: SaveJobInput!) {
    saveJob(input: $input) {
      success
      savedJobId
      savedJob {
        id
        savedDate
        notes
        job {
          id
          title
          company {
            name
          }
        }
      }
      errors
    }
  }
`;

const UNSAVE_JOB_MUTATION = gql`
  mutation UnsaveJob($jobId: String!) {
    unsaveJob(jobId: $jobId) {
      success
      errors
    }
  }
`;

class GraphQLApplicationService {
  constructor() {
    this.client = apolloClient;
  }

  /**
   * Get user applications with filtering and pagination
   */
  async getApplications(filters = {}) {
    try {
      console.log('Fetching applications via GraphQL:', filters);
      
      const variables = {
        userId: filters.userId || null,
        status: filters.status || null,
        limit: filters.limit || 20,
        offset: filters.offset || 0,
      };

      const { data } = await this.client.query({
        query: GET_APPLICATIONS_QUERY,
        variables,
        fetchPolicy: 'cache-and-network',
      });

      const applications = data.applications || [];
      
      console.log(`✅ Fetched ${applications.length} applications via GraphQL`);
      
      return {
        results: applications.map(app => this.transformApplicationDataToFrontend(app)),
        count: applications.length,
        success: true
      };
    } catch (error) {
      console.error('GraphQL getApplications error:', error);
      console.log('🔄 Falling back to mock application data');
      
      // Return mock data as fallback to prevent UI crash
      const mockData = this.getMockApplicationData();
      return {
        results: mockData,
        count: mockData.length,
        success: true,
        isMockData: true
      };
    }
  }

  /**
   * Get a specific application by ID
   */
  async getApplication(applicationId) {
    try {
      console.log('Fetching application by ID via GraphQL:', applicationId);
      
      const { data } = await this.client.query({
        query: GET_APPLICATION_QUERY,
        variables: { id: applicationId },
        fetchPolicy: 'cache-first',
      });

      if (!data.application) {
        throw new Error(`Application with ID ${applicationId} not found`);
      }

      console.log('✅ Fetched application details via GraphQL');
      return this.transformApplicationDataToFrontend(data.application);
    } catch (error) {
      console.error('GraphQL getApplication error:', error);
      throw error;
    }
  }

  /**
   * Create a new job application
   */
  async createApplication(applicationData) {
    try {
      console.log('Creating application via GraphQL:', applicationData);
      
      const input = this.transformApplicationDataForGraphQL(applicationData);
      
      const { data } = await this.client.mutate({
        mutation: CREATE_APPLICATION_MUTATION,
        variables: { input },
        update: (cache, { data: mutationData }) => {
          // Update the cache to include the new application
          if (mutationData.createApplication.success) {
            // Invalidate applications query to refetch
            cache.evict({ fieldName: 'applications' });
          }
        }
      });

      const result = data.createApplication;
      
      if (result.success) {
        console.log('✅ Application created successfully via GraphQL');
        return {
          success: true,
          data: {
            id: result.applicationId,
            ...this.transformApplicationDataToFrontend(result.application)
          },
          message: 'Application submitted successfully'
        };
      } else {
        console.error('❌ Application creation failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'Application submission failed');
      }
    } catch (error) {
      console.error('GraphQL createApplication error:', error);
      throw error;
    }
  }

  /**
   * Update an application
   */
  async updateApplication(applicationId, applicationData) {
    try {
      console.log('Updating application via GraphQL:', applicationId, applicationData);
      
      const input = this.transformApplicationDataForGraphQL(applicationData);
      
      const { data } = await this.client.mutate({
        mutation: UPDATE_APPLICATION_MUTATION,
        variables: { applicationId, input },
        update: (cache, { data: mutationData }) => {
          // Update the cache with new application data
          if (mutationData.updateApplication.success) {
            cache.evict({ fieldName: 'applications' });
            cache.evict({ fieldName: 'application', args: { id: applicationId } });
          }
        }
      });

      const result = data.updateApplication;
      
      if (result.success) {
        console.log('✅ Application updated successfully via GraphQL');
        return {
          success: true,
          data: this.transformApplicationDataToFrontend(result.application),
          message: 'Application updated successfully'
        };
      } else {
        console.error('❌ Application update failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'Application update failed');
      }
    } catch (error) {
      console.error('GraphQL updateApplication error:', error);
      throw error;
    }
  }

  /**
   * Get saved jobs
   */
  async getSavedJobs(filters = {}) {
    try {
      console.log('Fetching saved jobs via GraphQL:', filters);
      
      const variables = {
        userId: filters.userId || null,
        limit: filters.limit || 20,
        offset: filters.offset || 0,
      };

      const { data } = await this.client.query({
        query: GET_SAVED_JOBS_QUERY,
        variables,
        fetchPolicy: 'cache-and-network',
      });

      const savedJobs = data.savedJobs || [];
      
      console.log(`✅ Fetched ${savedJobs.length} saved jobs via GraphQL`);
      
      return {
        results: savedJobs.map(savedJob => this.transformSavedJobDataToFrontend(savedJob)),
        count: savedJobs.length,
        success: true
      };
    } catch (error) {
      console.error('GraphQL getSavedJobs error:', error);
      throw error;
    }
  }

  /**
   * Save a job
   */
  async saveJob(jobId, notes = '') {
    try {
      console.log('Saving job via GraphQL:', jobId);
      
      const { data } = await this.client.mutate({
        mutation: SAVE_JOB_MUTATION,
        variables: { 
          input: { 
            jobId, 
            notes 
          } 
        },
        update: (cache, { data: mutationData }) => {
          if (mutationData.saveJob.success) {
            // Invalidate saved jobs query to refetch
            cache.evict({ fieldName: 'savedJobs' });
          }
        }
      });

      const result = data.saveJob;
      
      if (result.success) {
        console.log('✅ Job saved successfully via GraphQL');
        return {
          success: true,
          data: this.transformSavedJobDataToFrontend(result.savedJob),
          message: 'Job saved successfully'
        };
      } else {
        console.error('❌ Job save failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'Job save failed');
      }
    } catch (error) {
      console.error('GraphQL saveJob error:', error);
      throw error;
    }
  }

  /**
   * Unsave a job
   */
  async unsaveJob(jobId) {
    try {
      console.log('Unsaving job via GraphQL:', jobId);
      
      const { data } = await this.client.mutate({
        mutation: UNSAVE_JOB_MUTATION,
        variables: { jobId },
        update: (cache, { data: mutationData }) => {
          if (mutationData.unsaveJob.success) {
            // Invalidate saved jobs query to refetch
            cache.evict({ fieldName: 'savedJobs' });
          }
        }
      });

      const result = data.unsaveJob;
      
      if (result.success) {
        console.log('✅ Job unsaved successfully via GraphQL');
        return {
          success: true,
          message: 'Job removed from saved list'
        };
      } else {
        console.error('❌ Job unsave failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'Job unsave failed');
      }
    } catch (error) {
      console.error('GraphQL unsaveJob error:', error);
      throw error;
    }
  }

  /**
   * Transform frontend application data to GraphQL input format
   */
  transformApplicationDataForGraphQL(applicationData) {
    return {
      jobId: applicationData.job_id || applicationData.jobId,
      coverLetter: applicationData.cover_letter || applicationData.coverLetter || null,
      notes: applicationData.notes || null,
      status: applicationData.status || null,
    };
  }

  /**
   * Transform GraphQL application data to frontend format
   */
  transformApplicationDataToFrontend(application) {
    return {
      id: application.id,
      user_id: application.userId,
      job_id: application.jobId,
      status: application.status,
      applied_date: application.appliedDate,
      last_updated: application.lastUpdated,
      cover_letter: application.coverLetter,
      notes: application.notes,
      optimized_resume_data: application.optimizedResumeData,
      ai_suggestions: application.aiSuggestions,
      skills_analysis: application.skillsAnalysis,
      job: application.job ? {
        id: application.job.id,
        title: application.job.title,
        description: application.job.description,
        location_text: application.job.locationText,
        salary_min: application.job.salaryMin,
        salary_max: application.job.salaryMax,
        salary_currency: application.job.salaryCurrency,
        job_type: application.job.jobType,
        experience_level: application.job.experienceLevel,
        remote_type: application.job.remoteType,
        company: application.job.company ? {
          id: application.job.company.id,
          name: application.job.company.name,
          industry: application.job.company.industry,
        } : null,
      } : null,
      // Legacy format compatibility
      userId: application.userId,
      jobId: application.jobId,
      appliedDate: application.appliedDate,
      lastUpdated: application.lastUpdated,
      coverLetter: application.coverLetter,
    };
  }

  /**
   * Transform GraphQL saved job data to frontend format
   */
  transformSavedJobDataToFrontend(savedJob) {
    return {
      id: savedJob.id,
      user_id: savedJob.userId,
      job_id: savedJob.jobId,
      saved_date: savedJob.savedDate,
      notes: savedJob.notes,
      job: savedJob.job ? {
        id: savedJob.job.id,
        title: savedJob.job.title,
        description: savedJob.job.description,
        location_text: savedJob.job.locationText,
        salary_min: savedJob.job.salaryMin,
        salary_max: savedJob.job.salaryMax,
        salary_currency: savedJob.job.salaryCurrency,
        job_type: savedJob.job.jobType,
        experience_level: savedJob.job.experienceLevel,
        remote_type: savedJob.job.remoteType,
        company: savedJob.job.company ? {
          id: savedJob.job.company.id,
          name: savedJob.job.company.name,
          industry: savedJob.job.company.industry,
        } : null,
      } : null,
      // Legacy format compatibility
      userId: savedJob.userId,
      jobId: savedJob.jobId,
      savedDate: savedJob.savedDate,
    };
  }

  /**
   * Get mock application data for fallback
   */
  getMockApplicationData() {
    return [
      {
        id: 'mock-app-1',
        user_id: 'demo-user-id',
        job_id: 'mock-job-1',
        status: 'applied',
        applied_date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        last_updated: new Date().toISOString(),
        cover_letter: 'I am very interested in this position and believe my skills in React and Node.js would be a great fit.',
        notes: 'Applied through company website',
        job: {
          id: 'mock-job-1',
          title: 'Senior Frontend Developer',
          description: 'Build amazing user interfaces with React and TypeScript. Work with a dynamic team on cutting-edge projects using JavaScript, CSS, and modern web technologies.',
          requirements: 'Must have experience with React, JavaScript, TypeScript, HTML, CSS, and Git version control.',
          location_text: 'San Francisco, CA',
          job_type: 'FULL_TIME',
          experience_level: 'SENIOR',
          company: { 
            id: 'mock-company-1',
            name: 'TechCorp',
            industry: 'Technology'
          }
        }
      },
      {
        id: 'mock-app-2',
        user_id: 'demo-user-id',
        job_id: 'mock-job-2',
        status: 'interview',
        applied_date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
        last_updated: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        cover_letter: 'As a senior developer with experience in Node.js and Python, I would love to contribute to your backend team.',
        notes: 'Phone interview scheduled for next week',
        ai_suggestions: '{"keywords": ["Node.js", "Python", "API"], "improvements": ["Highlight database experience"]}',
        job: {
          id: 'mock-job-2',
          title: 'Full Stack Engineer',
          description: 'Join our engineering team to build scalable web applications using React, Node.js, Python, and cloud technologies. Experience with SQL databases and GraphQL preferred.',
          requirements: 'Strong experience with JavaScript, Node.js, Python, SQL, MongoDB, Docker, and AWS cloud services.',
          location_text: 'Austin, TX',
          job_type: 'FULL_TIME', 
          experience_level: 'MID_LEVEL',
          company: { 
            id: 'mock-company-2',
            name: 'StartupXYZ',
            industry: 'Technology'
          }
        }
      },
      {
        id: 'mock-app-3',
        user_id: 'demo-user-id',
        job_id: 'mock-job-3',
        status: 'offer',
        applied_date: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
        last_updated: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        cover_letter: 'I am excited about the opportunity to work with cutting-edge technologies at your company.',
        notes: 'Received offer, negotiating salary',
        skills_analysis: '{"match_score": 85, "missing_skills": ["Docker", "Kubernetes"], "strong_skills": ["Python", "FastAPI"]}',
        job: {
          id: 'mock-job-3',
          title: 'Python Backend Developer',
          description: 'Develop robust backend systems using Python, FastAPI, PostgreSQL, and Docker. Experience with cloud platforms like AWS and containerization technologies preferred.',
          requirements: 'Expert-level Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes, AWS, and DevOps experience required.',
          location_text: 'Remote',
          job_type: 'FULL_TIME',
          experience_level: 'MID_LEVEL',
          company: { 
            id: 'mock-company-3',
            name: 'CloudTech',
            industry: 'Technology'
          }
        }
      }
    ];
  }

  /**
   * Get mock saved job data for fallback
   */
  getMockSavedJobData() {
    return [
      {
        id: 'mock-saved-1',
        user_id: 'demo-user-id',
        job_id: 'mock-job-1',
        saved_date: new Date().toISOString(),
        notes: 'Interesting position to consider',
        job: {
          id: 'mock-job-1',
          title: 'Frontend Developer',
          company: { name: 'Demo Company' },
          location_text: 'Remote'
        }
      }
    ];
  }

  /**
   * Get application statistics
   */
  async getApplicationStats() {
    try {
      const allApplications = await this.getApplications({ limit: 1000 });
      const applications = allApplications.results;
      
      return {
        total: applications.length,
        byStatus: this.groupBy(applications, 'status'),
        recent: applications.filter(app => {
          const appliedDate = new Date(app.applied_date);
          const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
          return appliedDate > weekAgo;
        }).length,
      };
    } catch (error) {
      console.error('Error getting application statistics:', error);
      return {
        total: 0,
        byStatus: {},
        recent: 0,
      };
    }
  }

  /**
   * Utility function to group items by a property
   */
  groupBy(items, property) {
    return items.reduce((groups, item) => {
      const key = item[property] || 'Unknown';
      groups[key] = (groups[key] || 0) + 1;
      return groups;
    }, {});
  }
}

export default new GraphQLApplicationService();