/**
 * Job Service for JobQuest Navigator Frontend
 * Handles all job-related API calls to Django backend
 */

import authService from './authService';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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
          // Redirect to login
          window.location.href = '/login';
          return null;
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
    const params = new URLSearchParams();
    
    // Map frontend filters to backend parameters
    if (filters.search) params.append('search', filters.search);
    if (filters.location) params.append('location', filters.location);
    if (filters.company) params.append('company', filters.company);
    if (filters.type) {
      // Map frontend types to backend types
      const typeMap = {
        'Full-time': 'full_time',
        'Part-time': 'part_time',
        'Contract': 'contract',
        'Freelance': 'freelance',
        'Internship': 'internship'
      };
      params.append('job_type', typeMap[filters.type] || filters.type.toLowerCase());
    }
    if (filters.remote) params.append('remote_type', 'remote');

    const url = `${this.baseURL}/jobs/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Get all jobs with pagination
   */
  async getJobs(page = 1, pageSize = 20) {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const url = `${this.baseURL}/jobs/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Get job by ID
   */
  async getJobById(jobId) {
    const url = `${this.baseURL}/jobs/${jobId}/`;
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

    const url = `${this.baseURL}/jobs/search/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Get nearby jobs
   */
  async getNearbyJobs(location, radius = 25) {
    const params = new URLSearchParams({
      location,
      radius: radius.toString(),
    });

    const url = `${this.baseURL}/jobs/nearby/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Get jobs for map view
   */
  async getJobsForMap(bounds = null) {
    let url = `${this.baseURL}/jobs/map/`;
    
    if (bounds) {
      const params = new URLSearchParams({
        north: bounds.north.toString(),
        south: bounds.south.toString(),
        east: bounds.east.toString(),
        west: bounds.west.toString(),
      });
      url += `?${params.toString()}`;
    }

    return await this.makeRequest(url);
  }

  /**
   * Save a job
   */
  async saveJob(jobId, notes = '') {
    const url = `${this.baseURL}/jobs/${jobId}/save/`;
    return await this.makeRequest(url, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  /**
   * Unsave a job
   */
  async unsaveJob(jobId) {
    const url = `${this.baseURL}/jobs/${jobId}/unsave/`;
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

    const url = `${this.baseURL}/jobs/saved/?${params.toString()}`;
    return await this.makeRequest(url);
  }

  /**
   * Apply to a job
   */
  async applyToJob(jobId, applicationData) {
    const url = `${this.baseURL}/jobs/${jobId}/apply/`;
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
        display_name: backendJob.location ? 
          `${backendJob.location.city}, ${backendJob.location.state || backendJob.location.country}` : 
          'Unknown Location',
        city: backendJob.location?.city,
        state: backendJob.location?.state,
        country: backendJob.location?.country
      },
      // Add latitude and longitude for map functionality
      latitude: backendJob.location?.latitude ? parseFloat(backendJob.location.latitude) : null,
      longitude: backendJob.location?.longitude ? parseFloat(backendJob.location.longitude) : null,
      description: backendJob.description,
      requirements: backendJob.requirements,
      benefits: backendJob.benefits,
      contract_type: backendJob.job_type?.replace('_', '-'), // Transform backend format
      salary_min: backendJob.salary_min,
      salary_max: backendJob.salary_max,
      salary_currency: backendJob.salary_currency,
      salary_period: backendJob.salary_period,
      remote_type: backendJob.remote_type,
      experience_level: backendJob.experience_level,
      posted_date: backendJob.posted_date,
      external_url: backendJob.external_url,
      required_skills: backendJob.required_skills || [],
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
}

export const jobService = new JobService();
export default jobService;