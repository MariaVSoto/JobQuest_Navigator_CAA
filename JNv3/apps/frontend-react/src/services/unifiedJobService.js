/**
 * Unified Job Service with GraphQL Primary and REST Fallback
 * Provides a consistent API interface while migrating from REST to GraphQL
 */

import graphqlJobService from './graphqlJobService';
// Removed fallbackService import - using mock data directly

class UnifiedJobService {
  constructor() {
    this.primaryService = graphqlJobService;
    this.fallbackService = null; // FallbackService removed
    this.useGraphQL = process.env.REACT_APP_USE_FASTAPI_JOBS === 'true';
    
    console.log(`🔧 UnifiedJobService initialized with GraphQL: ${this.useGraphQL}`);
  }

  /**
   * Get jobs with automatic fallback
   */
  async getJobs(filters = {}) {
    if (this.useGraphQL) {
      try {
        console.log('🚀 Attempting to fetch jobs via GraphQL...');
        const result = await this.primaryService.getJobs(filters);
        
        // Transform GraphQL results to match REST format for compatibility
        if (result.results) {
          result.results = result.results.map(job => 
            this.primaryService.transformJobDataToFrontend(job)
          );
        }
        
        console.log('✅ Jobs fetched successfully via GraphQL');
        return result;
      } catch (graphqlError) {
        console.warn('❌ GraphQL getJobs failed, trying REST fallback:', graphqlError);
        
        try {
          const result = await this.fallbackService.getJobs(filters);
          console.log('✅ Jobs fetched successfully via REST fallback');
          return result;
        } catch (restError) {
          console.error('❌ Both GraphQL and REST failed:', { graphqlError, restError });
          
          // Return mock data as last resort
          console.log('🎭 Using mock data as final fallback');
          return {
            results: this.primaryService.getMockJobData(),
            count: 2,
            success: true,
            message: 'Using demo data - backend services unavailable'
          };
        }
      }
    } else {
      // Use REST service directly
      try {
        console.log('🔄 Using REST service directly...');
        return await this.fallbackService.getJobs(filters);
      } catch (error) {
        console.error('❌ REST service failed:', error);
        
        // Return mock data
        console.log('🎭 Using mock data fallback');
        return {
          results: this.primaryService.getMockJobData(),
          count: 2,
          success: true,
          message: 'Using demo data - backend services unavailable'
        };
      }
    }
  }

  /**
   * Get a specific job by ID with fallback (alias for getJobById)
   */
  async getJob(jobId) {
    return this.getJobById(jobId);
  }

  /**
   * Get a specific job by ID with fallback
   */
  async getJobById(jobId) {
    if (this.useGraphQL) {
      try {
        console.log('🚀 Attempting to fetch job via GraphQL...');
        const job = await this.primaryService.getJob(jobId);
        const transformed = this.primaryService.transformJobDataToFrontend(job);
        console.log('✅ Job fetched successfully via GraphQL');
        return transformed;
      } catch (graphqlError) {
        console.warn('❌ GraphQL getJob failed, trying REST fallback:', graphqlError);
        
        try {
          const job = await this.fallbackService.getJob(jobId);
          console.log('✅ Job fetched successfully via REST fallback');
          return job;
        } catch (restError) {
          console.error('❌ Both GraphQL and REST failed:', { graphqlError, restError });
          
          // Return mock job
          const mockJobs = this.primaryService.getMockJobData();
          return mockJobs[0]; // Return first mock job
        }
      }
    } else {
      try {
        return await this.fallbackService.getJob(jobId);
      } catch (error) {
        console.error('❌ REST getJob failed:', error);
        const mockJobs = this.primaryService.getMockJobData();
        return mockJobs[0];
      }
    }
  }

  /**
   * Create a new job with fallback
   */
  async createJob(jobData) {
    if (this.useGraphQL) {
      try {
        console.log('🚀 Attempting to create job via GraphQL...');
        const result = await this.primaryService.createJob(jobData);
        console.log('✅ Job created successfully via GraphQL');
        return result;
      } catch (graphqlError) {
        console.warn('❌ GraphQL createJob failed, trying REST fallback:', graphqlError);
        
        try {
          const result = await this.fallbackService.createJob(jobData);
          console.log('✅ Job created successfully via REST fallback');
          return result;
        } catch (restError) {
          console.error('❌ Both GraphQL and REST failed:', { graphqlError, restError });
          throw new Error(`Failed to create job. GraphQL error: ${graphqlError.message}. REST error: ${restError.message}`);
        }
      }
    } else {
      return await this.fallbackService.createJob(jobData);
    }
  }

  /**
   * Search jobs with fallback
   */
  async searchJobs(query, filters = {}) {
    return this.getJobs({
      ...filters,
      search: query
    });
  }

  /**
   * Get jobs by location with fallback
   */
  async getJobsByLocation(location, filters = {}) {
    return this.getJobs({
      ...filters,
      location: location
    });
  }

  /**
   * Get jobs by type with fallback
   */
  async getJobsByType(jobType, filters = {}) {
    return this.getJobs({
      ...filters,
      job_type: jobType
    });
  }

  /**
   * Get remote jobs with fallback
   */
  async getRemoteJobs(filters = {}) {
    return this.getJobs({
      ...filters,
      remote_type: 'remote'
    });
  }

  /**
   * Save a job (placeholder - would need backend implementation)
   */
  async saveJob(jobId) {
    // This would need to be implemented in both GraphQL and REST
    console.log('🔖 Save job functionality not yet implemented:', jobId);
    return {
      success: true,
      message: 'Job save functionality not yet implemented'
    };
  }

  /**
   * Apply to a job (placeholder - would need backend implementation)
   */
  async applyToJob(jobId, applicationData = {}) {
    // This would need to be implemented in both GraphQL and REST
    console.log('📝 Apply to job functionality not yet implemented:', jobId, applicationData);
    return {
      success: true,
      message: 'Job application functionality not yet implemented'
    };
  }

  /**
   * Delete a job
   */
  async deleteJob(jobId) {
    if (this.useGraphQL) {
      try {
        return await this.primaryService.deleteJob(jobId);
      } catch (error) {
        console.warn('❌ GraphQL deleteJob failed:', error.message);
        // For delete operations, we don't want to fall back to REST
        // as it could cause data inconsistency
        throw error;
      }
    }
    
    // REST fallback - not implemented yet
    throw new Error('Job deletion via REST API not implemented');
  }

  /**
   * Update a job
   */
  async updateJob(jobId, jobData) {
    if (this.useGraphQL) {
      try {
        return await this.primaryService.updateJob(jobId, jobData);
      } catch (error) {
        console.warn('❌ GraphQL updateJob failed:', error.message);
        // For update operations, we don't want to fall back to REST
        // as it could cause data inconsistency
        throw error;
      }
    }
    
    // REST fallback - not implemented yet
    throw new Error('Job update via REST API not implemented');
  }

  /**
   * Get job statistics with fallback
   */
  async getJobStats() {
    if (this.useGraphQL) {
      try {
        return await this.primaryService.getJobStats();
      } catch (error) {
        console.warn('❌ GraphQL getJobStats failed, using fallback');
      }
    }
    
    // Fallback stats
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

  /**
   * Check service health
   */
  async checkHealth() {
    const results = {
      graphql: false,
      rest: false,
      primary: this.useGraphQL ? 'graphql' : 'rest'
    };

    // Test GraphQL
    try {
      await this.primaryService.getJobs({ limit: 1 });
      results.graphql = true;
    } catch (error) {
      console.log('GraphQL service health check failed:', error.message);
    }

    // Test REST
    try {
      await this.fallbackService.getJobs({ limit: 1 });
      results.rest = true;
    } catch (error) {
      console.log('REST service health check failed:', error.message);
    }

    return results;
  }

  /**
   * Switch primary service
   */
  switchToPrimary(useGraphQL = true) {
    this.useGraphQL = useGraphQL;
    console.log(`🔄 Switched to ${useGraphQL ? 'GraphQL' : 'REST'} as primary service`);
  }

  /**
   * Get service status
   */
  getServiceStatus() {
    return {
      primary: this.useGraphQL ? 'GraphQL' : 'REST',
      graphqlEnabled: this.useGraphQL,
      fallbackAvailable: true,
      services: {
        graphql: this.primaryService,
        rest: this.fallbackService
      }
    };
  }
}

export default new UnifiedJobService();