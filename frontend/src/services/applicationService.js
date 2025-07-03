/**
 * Enhanced Job Application service for Epic 5: Job Application Tracking with Resume Used
 * Comprehensive service for application tracking, resume versioning, notifications, and analytics
 */

import FallbackService from './fallbackService';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApplicationService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/application-tracking`;
    this.jobsURL = `${API_BASE_URL}/jobs`;
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
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
    
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

  // ==================== EPIC 5: Enhanced Application Tracking ====================

  /**
   * Get dashboard summary with metrics and recent activity
   */
  async getDashboard() {
    // Development bypass: return mock dashboard data
    if (FallbackService.isDevBypass()) {
      console.log('🔧 ApplicationService: Using mock dashboard data (dev bypass)');
      return {
        total_applications: 3,
        applications_by_status: {
          applied: 1,
          screening: 1,
          interview: 1,
          rejected: 0,
          offer: 0
        },
        response_rate: 75,
        average_time_to_response: 5,
        recent_activity: [
          {
            id: '1',
            type: 'status_change',
            message: 'Application status updated to Interview',
            timestamp: '2025-07-03T10:00:00Z'
          }
        ]
      };
    }

    const response = await this.makeRequest('/applications/dashboard/');
    return await response.json();
  }

  /**
   * Get user's tracked applications with advanced filtering
   */
  async getApplications(filters = {}) {
    // Development bypass: return mock applications data
    if (FallbackService.isDevBypass()) {
      console.log('🔧 ApplicationService: Using mock applications data (dev bypass)');
      const mockApplications = FallbackService.getMockApplications();
      return {
        count: mockApplications.length,
        next: null,
        previous: null,
        results: mockApplications
      };
    }

    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/applications/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific application tracker with full details
   */
  async getApplication(applicationId) {
    const response = await this.makeRequest(`/applications/${applicationId}/`);
    return await response.json();
  }

  /**
   * Create a new application tracker
   */
  async createApplication(applicationData) {
    const response = await this.makeRequest('/applications/', {
      method: 'POST',
      body: JSON.stringify(applicationData),
    });
    return await response.json();
  }

  /**
   * Update application tracker
   */
  async updateApplication(applicationId, applicationData) {
    const response = await this.makeRequest(`/applications/${applicationId}/`, {
      method: 'PATCH',
      body: JSON.stringify(applicationData),
    });
    return await response.json();
  }

  /**
   * Update application status with automatic history tracking
   */
  async updateStatus(applicationId, status, notes = '') {
    const response = await this.makeRequest(`/applications/${applicationId}/update_status/`, {
      method: 'POST',
      body: JSON.stringify({ status, notes }),
    });
    return await response.json();
  }

  /**
   * Bulk update status for multiple applications
   */
  async bulkUpdateStatus(applicationIds, newStatus, notes = '') {
    const response = await this.makeRequest('/applications/bulk_status_update/', {
      method: 'POST',
      body: JSON.stringify({
        application_ids: applicationIds,
        new_status: newStatus,
        notes
      }),
    });
    return await response.json();
  }

  /**
   * Get detailed analytics for applications
   */
  async getAnalytics() {
    const response = await this.makeRequest('/applications/analytics/');
    return await response.json();
  }

  /**
   * Delete an application tracker
   */
  async deleteApplication(applicationId) {
    await this.makeRequest(`/applications/${applicationId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  // ==================== INTERVIEW MANAGEMENT ====================

  /**
   * Get all interviews for the user
   */
  async getInterviews(filters = {}) {
    // Development bypass: return mock interviews data
    if (FallbackService.isDevBypass()) {
      console.log('🔧 ApplicationService: Using mock interviews data (dev bypass)');
      const mockInterviews = FallbackService.getMockInterviewData();
      return {
        count: mockInterviews.upcomingInterviews.length,
        next: null,
        previous: null,
        results: mockInterviews.upcomingInterviews
      };
    }

    const queryParams = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/interviews/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get upcoming interviews
   */
  async getUpcomingInterviews() {
    const response = await this.makeRequest('/interviews/upcoming/');
    return await response.json();
  }

  /**
   * Create/schedule a new interview
   */
  async createInterview(interviewData) {
    const response = await this.makeRequest('/interviews/', {
      method: 'POST',
      body: JSON.stringify(interviewData),
    });
    return await response.json();
  }

  /**
   * Update interview details
   */
  async updateInterview(interviewId, interviewData) {
    const response = await this.makeRequest(`/interviews/${interviewId}/`, {
      method: 'PATCH',
      body: JSON.stringify(interviewData),
    });
    return await response.json();
  }

  // ==================== NOTIFICATIONS ====================

  /**
   * Get user notifications
   */
  async getNotifications(filters = {}) {
    // Development bypass: return mock notifications data
    if (FallbackService.isDevBypass()) {
      console.log('🔧 ApplicationService: Using mock notifications data (dev bypass)');
      return {
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: '1',
            type: 'application_update',
            title: 'Application Status Updated',
            message: 'Your application for Frontend Developer has been updated to Interview stage',
            timestamp: '2025-07-03T10:00:00Z',
            is_read: false
          },
          {
            id: '2',
            type: 'new_job_match',
            title: 'New Job Match',
            message: 'A new job matching your profile has been posted',
            timestamp: '2025-07-02T15:30:00Z',
            is_read: true
          }
        ]
      };
    }

    const queryParams = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/notifications/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Mark notification as read
   */
  async markNotificationRead(notificationId) {
    const response = await this.makeRequest(`/notifications/${notificationId}/mark_read/`, {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Mark all notifications as read
   */
  async markAllNotificationsRead() {
    const response = await this.makeRequest('/notifications/mark_all_read/', {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Create a new notification/reminder
   */
  async createNotification(notificationData) {
    const response = await this.makeRequest('/notifications/', {
      method: 'POST',
      body: JSON.stringify(notificationData),
    });
    return await response.json();
  }

  // ==================== DOCUMENTS ====================

  /**
   * Get application documents
   */
  async getDocuments(applicationId = null) {
    const filters = applicationId ? { application_tracker: applicationId } : {};
    const queryParams = new URLSearchParams(filters);
    const endpoint = `/documents/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Upload application document
   */
  async uploadDocument(documentData) {
    const formData = new FormData();
    Object.entries(documentData).forEach(([key, value]) => {
      formData.append(key, value);
    });

    const response = await this.makeRequest('/documents/', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set content-type for FormData
    });
    return await response.json();
  }

  // ==================== METRICS & ANALYTICS ====================

  /**
   * Get application metrics for a specific period
   */
  async getMetrics() {
    const response = await this.makeRequest('/metrics/');
    return await response.json();
  }

  /**
   * Get application status history
   */
  async getStatusHistory(applicationId) {
    const response = await this.makeRequest(`/applications/${applicationId}/history/`);
    return await response.json();
  }

  // ==================== LEGACY COMPATIBILITY ====================

  /**
   * Apply to a job (creates basic application, then enhanced tracker)
   */
  async applyToJob(jobId, applicationData = {}) {
    // First create basic job application
    const response = await this.makeRequest(`${this.jobsURL}/${jobId}/apply/`, {
      method: 'POST',
      body: JSON.stringify(applicationData),
    });
    
    const basicApplication = await response.json();
    
    // Then create enhanced application tracker if resume version is provided
    if (applicationData.resume_version_id) {
      const trackerData = {
        job_application: basicApplication.id,
        resume_version: applicationData.resume_version_id,
        priority: applicationData.priority || 'medium',
        application_source: applicationData.application_source || 'direct',
        cover_letter_used: applicationData.cover_letter || '',
        salary_expectation: applicationData.salary_expectation,
        notes: applicationData.notes || '',
      };
      
      await this.createApplication(trackerData);
    }
    
    return basicApplication;
  }

  /**
   * Get application statistics (enhanced version)
   */
  async getApplicationStats() {
    try {
      const dashboard = await this.getDashboard();
      return {
        total: dashboard.total_applications,
        ...dashboard.applications_by_status,
        successRate: dashboard.response_rate,
        responseRate: dashboard.response_rate,
        averageResponseTime: dashboard.average_time_to_response,
      };
    } catch (error) {
      console.error('Error getting application stats:', error);
      return {
        total: 0,
        applied: 0,
        screening: 0,
        interview: 0,
        offer: 0,
        rejected: 0,
        withdrawn: 0,
        successRate: 0,
        responseRate: 0,
        averageResponseTime: 0,
      };
    }
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Get enhanced status choices for Epic 5
   */
  getStatusChoices() {
    return [
      { value: 'applied', label: 'Applied', color: '#3498db' },
      { value: 'screening', label: 'Application Screening', color: '#f39c12' },
      { value: 'phone_screening', label: 'Phone Screening', color: '#e67e22' },
      { value: 'technical_interview', label: 'Technical Interview', color: '#9b59b6' },
      { value: 'behavioral_interview', label: 'Behavioral Interview', color: '#8e44ad' },
      { value: 'final_interview', label: 'Final Interview', color: '#2c3e50' },
      { value: 'reference_check', label: 'Reference Check', color: '#16a085' },
      { value: 'offer_pending', label: 'Offer Pending', color: '#27ae60' },
      { value: 'offer_received', label: 'Offer Received', color: '#2ecc71' },
      { value: 'offer_accepted', label: 'Offer Accepted', color: '#27ae60' },
      { value: 'offer_declined', label: 'Offer Declined', color: '#f39c12' },
      { value: 'rejected', label: 'Rejected', color: '#e74c3c' },
      { value: 'withdrawn', label: 'Withdrawn', color: '#95a5a6' },
      { value: 'on_hold', label: 'On Hold', color: '#34495e' },
    ];
  }

  /**
   * Get priority choices
   */
  getPriorityChoices() {
    return [
      { value: 'low', label: 'Low', color: '#95a5a6' },
      { value: 'medium', label: 'Medium', color: '#3498db' },
      { value: 'high', label: 'High', color: '#f39c12' },
      { value: 'urgent', label: 'Urgent', color: '#e74c3c' },
    ];
  }

  /**
   * Get status display with color
   */
  getStatusDisplay(status) {
    const choice = this.getStatusChoices().find(c => c.value === status);
    return choice ? { label: choice.label, color: choice.color } : { label: status, color: '#95a5a6' };
  }

  /**
   * Get priority display with color
   */
  getPriorityDisplay(priority) {
    const choice = this.getPriorityChoices().find(c => c.value === priority);
    return choice ? { label: choice.label, color: choice.color } : { label: priority, color: '#95a5a6' };
  }

  /**
   * Format relative time (e.g., "2 days ago")
   */
  formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now - date;
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
    
    return date.toLocaleDateString();
  }

  /**
   * Get next steps suggestion based on enhanced status
   */
  getNextStepsSuggestion(application) {
    const daysSinceApplied = Math.floor(
      (new Date() - new Date(application.applied_date)) / (1000 * 60 * 60 * 24)
    );

    const suggestions = {
      'applied': daysSinceApplied > 14 
        ? 'Consider following up with the recruiter or hiring manager'
        : 'Wait for initial response from the company',
      'screening': 'Prepare for the next round of interviews',
      'phone_screening': 'Prepare for technical or behavioral interviews',
      'technical_interview': 'Review technical concepts and practice coding problems',
      'behavioral_interview': 'Prepare STAR method responses for common questions',
      'final_interview': 'Research the team and prepare thoughtful questions',
      'reference_check': 'Confirm your references are prepared and available',
      'offer_pending': 'Wait for the official offer and prepare for negotiation',
      'offer_received': 'Review the offer details and negotiate if necessary',
      'offer_accepted': 'Prepare for onboarding and your new role',
      'offer_declined': 'Consider maintaining relationships for future opportunities',
      'rejected': 'Request feedback and consider applying to similar roles',
      'withdrawn': 'Consider if you want to reapply in the future',
      'on_hold': 'Stay in touch and continue applying to other positions',
    };

    return suggestions[application.status] || 'Keep track of your application progress';
  }

  /**
   * Validate application data for Epic 5
   */
  validateApplicationData(applicationData) {
    const errors = [];

    if (!applicationData.job_application) {
      errors.push('Job application reference is required');
    }

    if (!applicationData.resume_version) {
      errors.push('Resume version is required');
    }

    const validStatuses = this.getStatusChoices().map(s => s.value);
    if (applicationData.status && !validStatuses.includes(applicationData.status)) {
      errors.push('Invalid application status');
    }

    const validPriorities = this.getPriorityChoices().map(p => p.value);
    if (applicationData.priority && !validPriorities.includes(applicationData.priority)) {
      errors.push('Invalid priority level');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

const applicationService = new ApplicationService();
export default applicationService;