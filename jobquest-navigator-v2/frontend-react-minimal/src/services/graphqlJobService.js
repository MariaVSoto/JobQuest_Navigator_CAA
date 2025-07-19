/**
 * GraphQL Job Service for JobQuest Navigator v2
 * Handles all job-related operations via GraphQL queries and mutations
 */

import { gql } from '@apollo/client';
import apolloClient from '../apolloClient';

// GraphQL Queries
const GET_JOBS_QUERY = gql`
  query GetJobs(
    $limit: Int
    $offset: Int
    $search: String
    $location: String
    $jobType: String
    $experienceLevel: String
    $remoteType: String
  ) {
    jobs(
      limit: $limit
      offset: $offset
      search: $search
      location: $location
      jobType: $jobType
      experienceLevel: $experienceLevel
      remoteType: $remoteType
    ) {
      id
      title
      description
      requirements
      benefits
      locationText
      salaryMin
      salaryMax
      salaryCurrency
      salaryPeriod
      jobType
      contractType
      experienceLevel
      remoteType
      userInput
      source
      postedDate
      expiresDate
      company {
        id
        name
        description
        website
        logoUrl
        industry
        companySize
        foundedYear
      }
      isSaved
      isApplied
    }
  }
`;

const GET_JOB_QUERY = gql`
  query GetJob($id: String!) {
    job(id: $id) {
      id
      title
      description
      requirements
      benefits
      locationText
      salaryMin
      salaryMax
      salaryCurrency
      salaryPeriod
      jobType
      contractType
      experienceLevel
      remoteType
      userInput
      source
      postedDate
      expiresDate
      company {
        id
        name
        description
        website
        logoUrl
        industry
        companySize
        foundedYear
      }
      isSaved
      isApplied
    }
  }
`;

// GraphQL Mutations
const CREATE_JOB_MUTATION = gql`
  mutation CreateJob($input: CreateJobInput!) {
    createJob(input: $input) {
      success
      jobId
      errors
    }
  }
`;

class GraphQLJobService {
  constructor() {
    this.client = apolloClient;
  }

  /**
   * Get jobs with filtering and pagination
   */
  async getJobs(filters = {}) {
    try {
      console.log('Fetching jobs via GraphQL:', filters);
      
      const variables = {
        limit: filters.limit || 20,
        offset: filters.offset || 0,
        search: filters.search || null,
        location: filters.location || null,
        jobType: filters.jobType || null,
        experienceLevel: filters.experienceLevel || null,
        remoteType: filters.remoteType || null,
      };

      const { data } = await this.client.query({
        query: GET_JOBS_QUERY,
        variables,
        fetchPolicy: 'cache-and-network', // Always fetch fresh data but use cache while loading
      });

      const jobs = data.jobs || [];
      
      console.log(`✅ Fetched ${jobs.length} jobs via GraphQL`);
      
      return {
        results: jobs,
        count: jobs.length,
        success: true
      };
    } catch (error) {
      console.error('GraphQL getJobs error:', error);
      throw error;
    }
  }

  /**
   * Get a specific job by ID
   */
  async getJob(jobId) {
    try {
      console.log('Fetching job by ID via GraphQL:', jobId);
      
      const { data } = await this.client.query({
        query: GET_JOB_QUERY,
        variables: { id: jobId },
        fetchPolicy: 'cache-first',
      });

      if (!data.job) {
        throw new Error(`Job with ID ${jobId} not found`);
      }

      console.log('✅ Fetched job details via GraphQL');
      return data.job;
    } catch (error) {
      console.error('GraphQL getJob error:', error);
      throw error;
    }
  }

  /**
   * Create a new job
   */
  async createJob(jobData) {
    try {
      console.log('Creating job via GraphQL:', jobData);
      
      const input = this.transformJobDataForGraphQL(jobData);
      
      const { data } = await this.client.mutate({
        mutation: CREATE_JOB_MUTATION,
        variables: { input },
        update: (cache, { data: mutationData }) => {
          // Update the cache to include the new job
          if (mutationData.createJob.success) {
            // Invalidate jobs query to refetch
            cache.evict({ fieldName: 'jobs' });
          }
        }
      });

      const result = data.createJob;
      
      if (result.success) {
        console.log('✅ Job created successfully via GraphQL');
        return {
          success: true,
          data: {
            id: result.jobId,
            ...jobData
          },
          message: 'Job created successfully'
        };
      } else {
        console.error('❌ Job creation failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'Job creation failed');
      }
    } catch (error) {
      console.error('GraphQL createJob error:', error);
      throw error;
    }
  }

  /**
   * Search jobs with text query
   */
  async searchJobs(query, filters = {}) {
    return this.getJobs({
      ...filters,
      search: query
    });
  }

  /**
   * Get jobs by location
   */
  async getJobsByLocation(location, filters = {}) {
    return this.getJobs({
      ...filters,
      location: location
    });
  }

  /**
   * Get jobs by type (full_time, part_time, contract, etc.)
   */
  async getJobsByType(jobType, filters = {}) {
    return this.getJobs({
      ...filters,
      jobType: jobType
    });
  }

  /**
   * Get remote jobs
   */
  async getRemoteJobs(filters = {}) {
    return this.getJobs({
      ...filters,
      remoteType: 'remote'
    });
  }

  /**
   * Transform frontend job data to GraphQL input format
   */
  transformJobDataForGraphQL(jobData) {
    return {
      title: jobData.title || '',
      company_name: jobData.company_name || jobData.company?.name || '',
      location_text: jobData.location_text || jobData.location || '',
      description: jobData.description || '',
      requirements: jobData.requirements || null,
      benefits: jobData.benefits || null,
      salary_min: jobData.salary_min || null,
      salary_max: jobData.salary_max || null,
      salary_currency: jobData.salary_currency || 'USD',
      salary_period: jobData.salary_period || 'yearly',
      job_type: jobData.job_type || 'full_time',
      contract_type: jobData.contract_type || 'permanent',
      experience_level: jobData.experience_level || null,
      remote_type: jobData.remote_type || 'on_site',
    };
  }

  /**
   * Transform GraphQL job data to frontend format
   */
  transformJobDataToFrontend(job) {
    return {
      id: job.id,
      title: job.title,
      description: job.description,
      requirements: job.requirements,
      benefits: job.benefits,
      location: job.locationText,
      location_text: job.locationText,
      salary_min: job.salaryMin,
      salary_max: job.salaryMax,
      salary_currency: job.salaryCurrency,
      salary_period: job.salaryPeriod,
      job_type: job.jobType,
      contract_type: job.contractType,
      experience_level: job.experienceLevel,
      remote_type: job.remoteType,
      user_input: job.userInput,
      source: job.source,
      posted_date: job.postedDate,
      expires_date: job.expiresDate,
      company: job.company ? {
        id: job.company.id,
        name: job.company.name,
        display_name: job.company.name,
        description: job.company.description,
        website: job.company.website,
        logo_url: job.company.logoUrl,
        industry: job.company.industry,
        company_size: job.company.companySize,
        founded_year: job.company.foundedYear,
      } : null,
      is_saved: job.isSaved,
      is_applied: job.isApplied,
      // Legacy format compatibility
      isSaved: job.isSaved,
      isApplied: job.isApplied,
    };
  }

  /**
   * Get job statistics
   */
  async getJobStats() {
    try {
      const allJobs = await this.getJobs({ limit: 1000 }); // Get all jobs for stats
      const jobs = allJobs.results;
      
      return {
        total: jobs.length,
        byType: this.groupBy(jobs, 'jobType'),
        byLocation: this.groupBy(jobs, 'locationText'),
        byExperience: this.groupBy(jobs, 'experienceLevel'),
        byRemoteType: this.groupBy(jobs, 'remoteType'),
        saved: jobs.filter(job => job.isSaved).length,
        applied: jobs.filter(job => job.isApplied).length,
      };
    } catch (error) {
      console.error('Error getting job statistics:', error);
      return {
        total: 0,
        byType: {},
        byLocation: {},
        byExperience: {},
        byRemoteType: {},
        saved: 0,
        applied: 0,
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

  /**
   * Get mock job data for fallback
   */
  getMockJobData() {
    return [
      {
        id: 'mock-job-1',
        title: 'Frontend Developer',
        description: 'Build amazing user interfaces with React and TypeScript.',
        location: 'Los Angeles, CA',
        salary_min: 70000,
        salary_max: 95000,
        job_type: 'full_time',
        experience_level: 'mid',
        remote_type: 'hybrid',
        company: {
          name: 'TechCorp Inc',
          industry: 'Technology'
        },
        is_saved: false,
        is_applied: false,
        posted_date: new Date().toISOString()
      },
      {
        id: 'mock-job-2',
        title: 'Backend Engineer',
        description: 'Design and build scalable backend systems.',
        location: 'Remote',
        salary_min: 80000,
        salary_max: 120000,
        job_type: 'full_time',
        experience_level: 'senior',
        remote_type: 'remote',
        company: {
          name: 'StartupXYZ',
          industry: 'Technology'
        },
        is_saved: true,
        is_applied: false,
        posted_date: new Date().toISOString()
      }
    ];
  }
}

export default new GraphQLJobService();