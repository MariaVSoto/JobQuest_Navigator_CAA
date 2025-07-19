/**
 * Job Service for JobQuest Navigator Frontend
 * Handles all job-related API calls to Django backend
 */

import authService from './authService';
import FallbackService from './fallbackService';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

class JobService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Get authorization headers
   */
  getAuthHeaders() {
    const token = authService.getAccessToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  /**
   * Make API request with error handling
   */
  async makeRequest(url, options = {}) {
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...options.headers,
      };

      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        // Try to refresh token
        const refreshed = await authService.refreshToken();
        if (refreshed) {
          // Retry with new token
          const newHeaders = {
            'Content-Type': 'application/json',
            ...this.getAuthHeaders(),
            ...options.headers,
          };
          
          const retryResponse = await fetch(url, {
            ...options,
            headers: newHeaders,
          });
          
          if (!retryResponse.ok) {
            throw new Error(`HTTP ${retryResponse.status}: ${retryResponse.statusText}`);
          }
          
          return await retryResponse.json();
        } else {
          // Don't redirect automatically, let components handle authentication
          console.log('Authentication failed, throwing error instead of redirecting');
          throw new Error('Authentication required');
        }
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Search jobs with filters
   */
  async searchJobs(filters = {}) {
    // Development bypass: return filtered mock data
    if (FallbackService.isDevBypass()) {
      console.log('🔧 JobService: Using mock search data (dev bypass)');
      let mockJobs = FallbackService.getMockJobs();
      
      // Apply basic filters to mock data
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        mockJobs = mockJobs.filter(job => 
          job.title.toLowerCase().includes(searchTerm) ||
          job.company.display_name.toLowerCase().includes(searchTerm) ||
          job.description.toLowerCase().includes(searchTerm)
        );
      }
      
      return {
        count: mockJobs.length,
        next: null,
        previous: null,
        results: mockJobs
      };
    }

    const params = new URLSearchParams();
    
    // Map frontend filters to backend parameters correctly
    if (filters.search) params.append('search', filters.search);
    if (filters.location) params.append('location', filters.location);
    if (filters.company) params.append('company', filters.company);
    
    // Job type mapping
    if (filters.type) {
      params.append('job_type', filters.type);
    }
    
    // Experience level
    if (filters.experience_level) {
      params.append('experience_level', filters.experience_level);
    }
    
    // Remote type
    if (filters.remote_type) {
      params.append('remote_type', filters.remote_type);
    }
    
    // Salary filters
    if (filters.salary_min) {
      params.append('salary_min', filters.salary_min);
    }
    
    // Sort parameter
    if (filters.sort) {
      params.append('ordering', filters.sort);
    }
    
    // Page and page size for pagination
    if (filters.page) {
      params.append('page', filters.page);
    }
    
    if (filters.page_size) {
      params.append('page_size', filters.page_size);
    }

    const url = `${this.baseURL}/jobs/jobs/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Get all jobs with pagination
   */
  async getJobs(page = 1, pageSize = 20) {
    // Development bypass: return mock data
    if (FallbackService.isDevBypass()) {
      console.log('🔧 JobService: Using mock data (dev bypass)');
      const mockJobs = FallbackService.getMockJobs();
      return {
        count: mockJobs.length,
        next: null,
        previous: null,
        results: mockJobs
      };
    }

    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const url = `${this.baseURL}/jobs/jobs/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Get job by ID
   */
  async getJobById(jobId) {
    const url = `${this.baseURL}/jobs/jobs/${jobId}/`;
    return await this.makeRequest(url);
  }

  /**
   * Get company by ID
   */
  async getCompanyById(companyId) {
    const url = `${this.baseURL}/jobs/companies/${companyId}/`;
    return await this.makeRequest(url);
  }

  /**
   * Get all companies
   */
  async getCompanies(filters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value.toString());
      }
    });

    const url = `${this.baseURL}/jobs/companies/${params.toString() ? `?${params}` : ''}`;
    return await this.makeRequest(url);
  }

  /**
   * Advanced job search
   */
  async advancedJobSearch(searchParams = {}) {
    const params = new URLSearchParams();
    
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value.toString());
      }
    });

    const url = `${this.baseURL}/jobs/jobs/search/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  // Location-based methods removed as per project requirements
  // Jobs are now based on user input only, not geographic data

  /**
   * Save a job
   */
  async saveJob(jobId, notes = '') {
    const url = `${this.baseURL}/jobs/jobs/${jobId}/save/`;
    return await this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  /**
   * Unsave a job
   */
  async unsaveJob(jobId) {
    const url = `${this.baseURL}/jobs/jobs/${jobId}/unsave/`;
    return await this.makeRequest(url, {
      method: 'DELETE',
    });
  }

  /**
   * Get saved jobs
   */
  async getSavedJobs(page = 1, pageSize = 20) {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const url = `${this.baseURL}/jobs/saved-jobs/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Apply to a job
   */
  async applyToJob(jobId, applicationData) {
    const url = `${this.baseURL}/jobs/jobs/${jobId}/apply/`;
    return await this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify(applicationData),
    });
  }

  /**
   * Get job applications
   */
  async getJobApplications(page = 1, pageSize = 20) {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const url = `${this.baseURL}/jobs/applications/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Update job application
   */
  async updateJobApplication(applicationId, updateData) {
    const url = `${this.baseURL}/jobs/applications/${applicationId}/`;
    return await this.makeRequest(url, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  }

  /**
   * Get job alerts
   */
  async getJobAlerts() {
    const url = `${this.baseURL}/jobs/alerts/`;
    return await this.makeRequest(url);
  }

  /**
   * Create job alert
   */
  async createJobAlert(alertData) {
    const url = `${this.baseURL}/jobs/alerts/`;
    return await this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify(alertData),
    });
  }

  /**
   * Update job alert
   */
  async updateJobAlert(alertId, updateData) {
    const url = `${this.baseURL}/jobs/alerts/${alertId}/`;
    return await this.makeRequest(url, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  }

  /**
   * Delete job alert
   */
  async deleteJobAlert(alertId) {
    const url = `${this.baseURL}/jobs/alerts/${alertId}/`;
    return await this.makeRequest(url, {
      method: 'DELETE',
    });
  }

  /**
   * Get skills
   */
  async getSkills(category = null, search = null) {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);

    const url = `${this.baseURL}/jobs/skills/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Get user skills
   */
  async getUserSkills() {
    const url = `${this.baseURL}/jobs/user-skills/`;
    return await this.makeRequest(url);
  }

  /**
   * Add user skill
   */
  async addUserSkill(skillData) {
    const url = `${this.baseURL}/jobs/user-skills/`;
    return await this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify(skillData),
    });
  }

  /**
   * Update user skill
   */
  async updateUserSkill(userSkillId, updateData) {
    const url = `${this.baseURL}/jobs/user-skills/${userSkillId}/`;
    return await this.makeRequest(url, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  }

  /**
   * Delete user skill
   */
  async deleteUserSkill(userSkillId) {
    const url = `${this.baseURL}/jobs/user-skills/${userSkillId}/`;
    return await this.makeRequest(url, {
      method: 'DELETE',
    });
  }

  /**
   * Transform job data from backend format to frontend format
   * This ensures compatibility with existing frontend components
   */
  transformJobData(backendJob) {
    return {
      id: backendJob.id,
      __unique_id: backendJob.id, // For backwards compatibility
      title: backendJob.title,
      company: {
        display_name: backendJob.company?.name || 'Unknown Company',
        name: backendJob.company?.name || 'Unknown Company'
      },
      location: {
        display_name: backendJob.location_text || 'Remote/Flexible',
        full_address: backendJob.location_text || 'Remote/Flexible',
        text: backendJob.location_text
      },
      // Geographic coordinates removed - jobs are user input based
      description: backendJob.description,
      requirements: backendJob.requirements,
      benefits: backendJob.benefits,
      job_type: backendJob.job_type, // Keep original format
      contract_type: backendJob.job_type?.replace('_', '-'), // Transform backend format for compatibility
      salary_min: backendJob.salary_min,
      salary_max: backendJob.salary_max,
      salary_currency: backendJob.salary_currency,
      salary_period: backendJob.salary_period,
      remote_type: backendJob.remote_type,
      experience_level: backendJob.experience_level,
      posted_date: backendJob.posted_date,
      created_at: backendJob.created_at,
      external_url: backendJob.external_url,
      required_skills: backendJob.required_skills || [],
      // Add save/apply status fields from backend
      is_saved: backendJob.is_saved || false,
      is_applied: backendJob.is_applied || false,
      salary_is_predicted: '0' // Backend doesn't have this field
    };
  }

  /**
   * Transform jobs list response
   */
  transformJobsResponse(response) {
    if (response.results) {
      // Paginated response
      return {
        ...response,
        results: response.results.map(job => this.transformJobData(job))
      };
    } else if (Array.isArray(response)) {
      // Simple array response
      return response.map(job => this.transformJobData(job));
    } else {
      // Single job response
      return this.transformJobData(response);
    }
  }

  /**
   * Get saved jobs for current user (updated method - replaces line 280 version)
   */
  async getSavedJobsWithFilters(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.page) params.append('page', filters.page);
    if (filters.page_size) params.append('page_size', filters.page_size);
    if (filters.ordering) params.append('ordering', filters.ordering);
    
    const url = `${this.baseURL}/jobs/saved-jobs/${params.toString() ? `?${params}` : ''}`;
    return await this.makeRequest(url);
  }
}

export const jobService = new JobService();
export default jobService;