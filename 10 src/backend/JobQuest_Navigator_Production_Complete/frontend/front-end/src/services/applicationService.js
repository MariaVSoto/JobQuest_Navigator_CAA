/**
 * Job Application service for tracking job applications
 * Handles all API calls related to job application management
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApplicationService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/jobs`;
  }

  /**
   * Get authentication token from localStorage
   */
  getAuthToken() {
    return localStorage.getItem('jobquest_access_token');
  }

  /**
   * Make authenticated API request
   */
  async makeRequest(endpoint, options = {}) {
    const token = this.getAuthToken();
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}`);
      }

      return response;
    } catch (error) {
      console.error('Application API request failed:', error);
      throw error;
    }
  }

  /**
   * Get user's job applications
   */
  async getApplications(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/applications/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific job application
   */
  async getApplication(applicationId) {
    const response = await this.makeRequest(`/applications/${applicationId}/`);
    return await response.json();
  }

  /**
   * Create a new job application
   */
  async createApplication(applicationData) {
    const response = await this.makeRequest('/applications/', {
      method: 'POST',
      body: JSON.stringify(applicationData),
    });
    return await response.json();
  }

  /**
   * Update job application status and notes
   */
  async updateApplication(applicationId, applicationData) {
    const response = await this.makeRequest(`/applications/${applicationId}/`, {
      method: 'PUT',
      body: JSON.stringify(applicationData),
    });
    return await response.json();
  }

  /**
   * Delete a job application
   */
  async deleteApplication(applicationId) {
    await this.makeRequest(`/applications/${applicationId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  /**
   * Apply to a job (creates application)
   */
  async applyToJob(jobId, applicationData = {}) {
    const response = await this.makeRequest(`/${jobId}/apply/`, {
      method: 'POST',
      body: JSON.stringify(applicationData),
    });
    return await response.json();
  }

  /**
   * Get application statistics
   */
  async getApplicationStats() {
    try {
      const applications = await this.getApplications({ limit: 1000 });
      const allApplications = applications.results || applications;
      
      const stats = {
        total: allApplications.length,
        applied: 0,
        screening: 0,
        interview: 0,
        offer: 0,
        rejected: 0,
        withdrawn: 0
      };

      allApplications.forEach(app => {
        if (stats.hasOwnProperty(app.status)) {
          stats[app.status]++;
        }
      });

      // Calculate success rate
      const totalProcessed = stats.screening + stats.interview + stats.offer + stats.rejected;
      stats.successRate = totalProcessed > 0 ? 
        Math.round(((stats.screening + stats.interview + stats.offer) / totalProcessed) * 100) : 0;

      return stats;
    } catch (error) {
      console.error('Error calculating application stats:', error);
      return {
        total: 0,
        applied: 0,
        screening: 0,
        interview: 0,
        offer: 0,
        rejected: 0,
        withdrawn: 0,
        successRate: 0
      };
    }
  }

  /**
   * Get applications by status
   */
  async getApplicationsByStatus(status) {
    return await this.getApplications({ status });
  }

  /**
   * Get recent applications (last 30 days)
   */
  async getRecentApplications(days = 30) {
    const applications = await this.getApplications();
    const allApplications = applications.results || applications;
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    return allApplications.filter(app => 
      new Date(app.applied_date) >= cutoffDate
    );
  }

  /**
   * Search applications by job title or company
   */
  async searchApplications(query) {
    const applications = await this.getApplications();
    const allApplications = applications.results || applications;
    
    const normalizedQuery = query.toLowerCase();
    return allApplications.filter(app => 
      app.job.title.toLowerCase().includes(normalizedQuery) ||
      app.job.company.name.toLowerCase().includes(normalizedQuery)
    );
  }

  /**
   * Get application status display
   */
  getStatusDisplay(status) {
    const statusMap = {
      'applied': 'Applied',
      'screening': 'Screening',
      'interview': 'Interview',
      'offer': 'Offer',
      'rejected': 'Rejected',
      'withdrawn': 'Withdrawn'
    };
    return statusMap[status] || status;
  }

  /**
   * Get application status color
   */
  getStatusColor(status) {
    const colorMap = {
      'applied': '#3498db',      // Blue
      'screening': '#f39c12',    // Orange
      'interview': '#9b59b6',    // Purple
      'offer': '#27ae60',        // Green
      'rejected': '#e74c3c',     // Red
      'withdrawn': '#95a5a6'     // Gray
    };
    return colorMap[status] || '#95a5a6';
  }

  /**
   * Get application priority based on status and date
   */
  getApplicationPriority(application) {
    const daysSinceApplied = Math.floor(
      (new Date() - new Date(application.applied_date)) / (1000 * 60 * 60 * 24)
    );

    if (application.status === 'interview') return { level: 'high', color: '#9b59b6' };
    if (application.status === 'offer') return { level: 'urgent', color: '#27ae60' };
    if (application.status === 'screening') return { level: 'medium', color: '#f39c12' };
    if (application.status === 'applied' && daysSinceApplied > 14) return { level: 'follow-up', color: '#e67e22' };
    
    return { level: 'normal', color: '#3498db' };
  }

  /**
   * Format application date for display
   */
  formatApplicationDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
    
    return date.toLocaleDateString();
  }

  /**
   * Validate application data
   */
  validateApplicationData(applicationData) {
    const errors = [];

    if (!applicationData.job_id) {
      errors.push('Job ID is required');
    }

    if (applicationData.status && !['applied', 'screening', 'interview', 'offer', 'rejected', 'withdrawn'].includes(applicationData.status)) {
      errors.push('Invalid application status');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Get next steps suggestion based on status
   */
  getNextStepsSuggestion(application) {
    const daysSinceApplied = Math.floor(
      (new Date() - new Date(application.applied_date)) / (1000 * 60 * 60 * 24)
    );

    switch (application.status) {
      case 'applied':
        if (daysSinceApplied > 14) {
          return 'Consider following up with the recruiter or hiring manager';
        }
        return 'Wait for initial response from the company';
      
      case 'screening':
        return 'Prepare for the next round of interviews';
      
      case 'interview':
        return 'Send a thank you email and wait for feedback';
      
      case 'offer':
        return 'Review the offer details and negotiate if necessary';
      
      case 'rejected':
        return 'Request feedback and consider applying to similar roles';
      
      case 'withdrawn':
        return 'Consider if you want to reapply in the future';
      
      default:
        return 'Keep track of your application progress';
    }
  }

  /**
   * Export applications data for backup/analysis
   */
  async exportApplications(format = 'json') {
    const applications = await this.getApplications({ limit: 1000 });
    const allApplications = applications.results || applications;

    if (format === 'csv') {
      const headers = ['Job Title', 'Company', 'Status', 'Applied Date', 'Last Updated', 'Location'];
      const csvData = allApplications.map(app => [
        app.job.title,
        app.job.company.name,
        app.status,
        new Date(app.applied_date).toLocaleDateString(),
        new Date(app.last_updated).toLocaleDateString(),
        app.job.location.city
      ]);

      return [headers, ...csvData];
    }

    return allApplications;
  }
}

const applicationService = new ApplicationService();
export default applicationService;