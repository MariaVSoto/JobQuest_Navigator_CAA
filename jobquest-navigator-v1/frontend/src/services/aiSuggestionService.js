/**
 * AI Suggestions service for Phase 3 implementation
 * Updated to work with ViewSets architecture for comprehensive AI suggestions management
 */

import FallbackService from './fallbackService';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

class AISuggestionService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/ai-suggestions`;
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
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      return response;
    } catch (error) {
      console.error('AI Suggestion API request failed:', error);
      throw error;
    }
  }

  // Suggestion Template Operations

  /**
   * Get suggestion templates
   */
  async getSuggestionTemplates(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/templates/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific suggestion template
   */
  async getSuggestionTemplate(templateId) {
    const response = await this.makeRequest(`/templates/${templateId}/`);
    return await response.json();
  }

  /**
   * Get popular suggestion templates
   */
  async getPopularTemplates() {
    const response = await this.makeRequest('/templates/popular/');
    return await response.json();
  }

  /**
   * Get templates by type
   */
  async getTemplatesByType(type) {
    const response = await this.makeRequest(`/templates/by_type/?type=${encodeURIComponent(type)}`);
    return await response.json();
  }

  // AI Suggestions Operations

  /**
   * Get user's AI suggestions with comprehensive filtering
   */
  async getSuggestions(filters = {}) {
    // Development bypass: return mock suggestions data
    if (FallbackService.isDevBypass()) {
      console.log('🔧 AISuggestionService: Using mock suggestions data (dev bypass)');
      const mockData = FallbackService.getMockAISuggestions();
      return {
        count: mockData.jobMatches.length + mockData.skillImprovements.length,
        next: null,
        previous: null,
        results: [
          ...mockData.jobMatches.map(match => ({
            id: `job-match-${match.job.id}`,
            suggestion_type: 'job_match',
            title: `Perfect Match: ${match.job.title}`,
            description: `Match score: ${match.job.matchScore}%. Reasons: ${match.reasons.join(', ')}`,
            confidence_score: match.job.matchScore / 100,
            priority: match.job.matchScore > 90 ? 'high' : 'medium',
            status: 'pending',
            action_url: `/jobs/${match.job.id}`,
            created_at: new Date().toISOString()
          })),
          ...mockData.skillImprovements.map((skill, index) => ({
            id: `skill-improvement-${index}`,
            suggestion_type: 'skill_improvement',
            title: `Learn ${skill.skill}`,
            description: `${skill.reason}. Priority: ${skill.priority}`,
            confidence_score: skill.priority === 'high' ? 0.9 : 0.7,
            priority: skill.priority,
            status: 'pending',
            action_url: '/skills',
            created_at: new Date().toISOString()
          }))
        ]
      };
    }

    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value);
        }
      });

      const endpoint = `/suggestions/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching AI suggestions, using mock data:', error);
      // Return mock data for demo
      return {
        suggestions: [
          {
            id: 'mock-1',
            type: 'job_match',
            title: 'Perfect Match: Frontend Developer',
            description: 'Based on your React and JavaScript skills, this position at TechCorp would be an excellent fit.',
            confidence: 0.92,
            action_url: '/jobs/mock-frontend-dev',
            created_at: new Date().toISOString()
          },
          {
            id: 'mock-2', 
            type: 'skill_improvement',
            title: 'Improve Your Profile',
            description: 'Consider adding TypeScript to your skillset to increase your job match score by 15%.',
            confidence: 0.87,
            action_url: '/skills',
            created_at: new Date().toISOString()
          },
          {
            id: 'mock-3',
            type: 'interview_prep',
            title: 'Interview Preparation',
            description: 'Practice common React interview questions to improve your success rate.',
            confidence: 0.83,
            action_url: '/interview-prep',
            created_at: new Date().toISOString()
          }
        ]
      };
    }
  }

  /**
   * Get a specific AI suggestion (marks as viewed)
   */
  async getSuggestion(suggestionId) {
    const response = await this.makeRequest(`/suggestions/${suggestionId}/`);
    return await response.json();
  }

  /**
   * Create a new AI suggestion
   */
  async createSuggestion(suggestionData) {
    const response = await this.makeRequest('/suggestions/', {
      method: 'POST',
      body: JSON.stringify(suggestionData),
    });
    return await response.json();
  }

  /**
   * Update an AI suggestion
   */
  async updateSuggestion(suggestionId, suggestionData) {
    const response = await this.makeRequest(`/suggestions/${suggestionId}/`, {
      method: 'PUT',
      body: JSON.stringify(suggestionData),
    });
    return await response.json();
  }

  /**
   * Delete an AI suggestion
   */
  async deleteSuggestion(suggestionId) {
    await this.makeRequest(`/suggestions/${suggestionId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  /**
   * Advanced search for AI suggestions
   */
  async searchSuggestions(searchParams = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });

    const response = await this.makeRequest(`/suggestions/search/?${queryParams}`);
    return await response.json();
  }

  /**
   * Take action on a suggestion (accept/reject/partially_accept)
   */
  async suggestionAction(suggestionId, action, notes = '', implementationDetails = null) {
    const response = await this.makeRequest(`/suggestions/${suggestionId}/action/`, {
      method: 'POST',
      body: JSON.stringify({ 
        action, 
        notes, 
        ...(implementationDetails && { implementation_details: implementationDetails })
      }),
    });
    return await response.json();
  }

  /**
   * Bulk action on multiple suggestions
   */
  async bulkSuggestionAction(suggestionIds, action, notes = '') {
    const response = await this.makeRequest('/suggestions/bulk_action/', {
      method: 'POST',
      body: JSON.stringify({
        suggestion_ids: suggestionIds,
        action,
        notes
      }),
    });
    return await response.json();
  }

  /**
   * Generate AI suggestions for resume optimization
   */
  async optimizeResume(optimizationData) {
    const response = await this.makeRequest('/suggestions/optimize_resume/', {
      method: 'POST',
      body: JSON.stringify(optimizationData),
    });
    return await response.json();
  }

  /**
   * Analyze job match and generate improvement suggestions
   */
  async analyzeJobMatch(analysisData) {
    const response = await this.makeRequest('/suggestions/analyze_job_match/', {
      method: 'POST',
      body: JSON.stringify(analysisData),
    });
    return await response.json();
  }

  /**
   * Get AI suggestions analytics
   */
  async getSuggestionsAnalytics() {
    const response = await this.makeRequest('/suggestions/analytics/');
    return await response.json();
  }

  /**
   * Generate daily suggestions
   */
  async generateDailySuggestions() {
    const response = await this.makeRequest('/suggestions/generate_daily/', {
      method: 'POST',
    });
    return await response.json();
  }

  // Job Recommendations Operations

  /**
   * Get user's job recommendations
   */
  async getJobRecommendations(filters = {}) {
    // Development bypass: return mock job recommendations
    if (FallbackService.isDevBypass()) {
      console.log('🔧 AISuggestionService: Using mock job recommendations (dev bypass)');
      const mockJobs = FallbackService.getMockJobs();
      return {
        count: mockJobs.length,
        next: null,
        previous: null,
        results: mockJobs.map((job, index) => ({
          id: `rec-${job.id}`,
          job: job,
          match_score: 0.85 - (index * 0.05),
          relevance_score: 0.9 - (index * 0.03),
          reasons: ['Skills match', 'Location preference', 'Salary range'],
          created_at: new Date().toISOString(),
          viewed_at: null,
          saved: false,
          dismissed: false
        }))
      };
    }

    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/job-recommendations/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific job recommendation (marks as viewed)
   */
  async getJobRecommendation(recommendationId) {
    const response = await this.makeRequest(`/job-recommendations/${recommendationId}/`);
    return await response.json();
  }

  /**
   * Get active (non-dismissed) job recommendations
   */
  async getActiveJobRecommendations() {
    const response = await this.makeRequest('/job-recommendations/active/');
    return await response.json();
  }

  /**
   * Get saved job recommendations
   */
  async getSavedJobRecommendations() {
    const response = await this.makeRequest('/job-recommendations/saved/');
    return await response.json();
  }

  /**
   * Dismiss a job recommendation
   */
  async dismissJobRecommendation(recommendationId) {
    const response = await this.makeRequest(`/job-recommendations/${recommendationId}/dismiss/`, {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Save a job recommendation
   */
  async saveJobRecommendation(recommendationId) {
    const response = await this.makeRequest(`/job-recommendations/${recommendationId}/save/`, {
      method: 'POST',
    });
    return await response.json();
  }

  // Suggestion Feedback Operations

  /**
   * Get feedback for a suggestion
   */
  async getSuggestionFeedback(suggestionId, filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/suggestions/${suggestionId}/feedback/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Create feedback for a suggestion
   */
  async createSuggestionFeedback(suggestionId, feedbackData) {
    const response = await this.makeRequest(`/suggestions/${suggestionId}/feedback/`, {
      method: 'POST',
      body: JSON.stringify(feedbackData),
    });
    return await response.json();
  }

  /**
   * Get specific feedback
   */
  async getFeedback(suggestionId, feedbackId) {
    const response = await this.makeRequest(`/suggestions/${suggestionId}/feedback/${feedbackId}/`);
    return await response.json();
  }

  /**
   * Update specific feedback
   */
  async updateFeedback(suggestionId, feedbackId, feedbackData) {
    const response = await this.makeRequest(`/suggestions/${suggestionId}/feedback/${feedbackId}/`, {
      method: 'PUT',
      body: JSON.stringify(feedbackData),
    });
    return await response.json();
  }

  /**
   * Delete specific feedback
   */
  async deleteFeedback(suggestionId, feedbackId) {
    await this.makeRequest(`/suggestions/${suggestionId}/feedback/${feedbackId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  // Suggestion Batch Operations

  /**
   * Get suggestion batches
   */
  async getSuggestionBatches(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/batches/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific suggestion batch
   */
  async getSuggestionBatch(batchId) {
    const response = await this.makeRequest(`/batches/${batchId}/`);
    return await response.json();
  }

  /**
   * Get recent suggestion batches
   */
  async getRecentBatches() {
    const response = await this.makeRequest('/batches/recent/');
    return await response.json();
  }

  /**
   * Get batches by type
   */
  async getBatchesByType(type) {
    const response = await this.makeRequest(`/batches/by_type/?type=${encodeURIComponent(type)}`);
    return await response.json();
  }

  // Convenience Methods

  /**
   * Accept suggestion
   */
  async acceptSuggestion(suggestionId, notes = '', implementationDetails = null) {
    return await this.suggestionAction(suggestionId, 'accept', notes, implementationDetails);
  }

  /**
   * Reject suggestion
   */
  async rejectSuggestion(suggestionId, notes = '') {
    return await this.suggestionAction(suggestionId, 'reject', notes);
  }

  /**
   * Partially accept suggestion
   */
  async partiallyAcceptSuggestion(suggestionId, notes = '', implementationDetails = null) {
    return await this.suggestionAction(suggestionId, 'partially_accept', notes, implementationDetails);
  }

  /**
   * Get suggestions by type
   */
  async getSuggestionsByType(suggestionType, limit = 20) {
    return await this.getSuggestions({ suggestion_type: suggestionType, page_size: limit });
  }

  /**
   * Get suggestions by status
   */
  async getSuggestionsByStatus(status, limit = 20) {
    return await this.getSuggestions({ status, page_size: limit });
  }

  /**
   * Get pending suggestions
   */
  async getPendingSuggestions(limit = 20) {
    return await this.getSuggestionsByStatus('pending', limit);
  }

  /**
   * Get accepted suggestions
   */
  async getAcceptedSuggestions(limit = 20) {
    return await this.getSuggestionsByStatus('accepted', limit);
  }

  /**
   * Get rejected suggestions
   */
  async getRejectedSuggestions(limit = 20) {
    return await this.getSuggestionsByStatus('rejected', limit);
  }

  /**
   * Get high priority suggestions
   */
  async getHighPrioritySuggestions(limit = 20) {
    return await this.getSuggestions({ priority: 'high', page_size: limit });
  }

  /**
   * Get suggestions for specific resume
   */
  async getSuggestionsForResume(resumeId, limit = 20) {
    return await this.getSuggestions({ target_resume_id: resumeId, page_size: limit });
  }

  /**
   * Get suggestions for specific job
   */
  async getSuggestionsForJob(jobId, limit = 20) {
    return await this.getSuggestions({ target_job_id: jobId, page_size: limit });
  }

  /**
   * Mark multiple suggestions as viewed
   */
  async markSuggestionsViewed(suggestionIds) {
    return await this.bulkSuggestionAction(suggestionIds, 'mark_viewed');
  }

  /**
   * Generate resume optimization with specific focus areas
   */
  async generateResumeOptimization(resumeId, focusAreas = ['keywords', 'content'], targetJobId = null, priority = 'medium') {
    return await this.optimizeResume({
      resume_id: resumeId,
      target_job_id: targetJobId,
      optimization_focus: focusAreas,
      priority
    });
  }

  /**
   * Analyze resume-job match with suggestions
   */
  async analyzeResumeJobMatch(resumeId, jobId, analysisType = 'basic', includeSuggestions = true) {
    return await this.analyzeJobMatch({
      resume_id: resumeId,
      job_id: jobId,
      analysis_type: analysisType,
      include_suggestions: includeSuggestions
    });
  }

  // Data Transformation & Utility Methods

  /**
   * Transform suggestion data for frontend display
   */
  transformSuggestion(suggestion) {
    return {
      ...suggestion,
      createdAt: new Date(suggestion.created_at),
      updatedAt: suggestion.updated_at ? new Date(suggestion.updated_at) : null,
      viewedAt: suggestion.viewed_at ? new Date(suggestion.viewed_at) : null,
      actedOnAt: suggestion.acted_on_at ? new Date(suggestion.acted_on_at) : null,
      expiresAt: suggestion.expires_at ? new Date(suggestion.expires_at) : null,
      isViewed: !!suggestion.viewed_at,
      isActedOn: !!suggestion.acted_on_at,
      isExpired: suggestion.expires_at ? new Date(suggestion.expires_at) < new Date() : false,
      priority: suggestion.priority || 'medium',
      confidencePercentage: Math.round((suggestion.confidence_score || 0) * 100),
      typeDisplay: this.getSuggestionTypeDisplay(suggestion.suggestion_type),
      priorityColor: this.getPriorityColor(suggestion.priority),
      confidenceColor: this.getConfidenceColor(suggestion.confidence_score || 0),
      statusDisplay: this.getStatusDisplay(suggestion.status),
      statusColor: this.getStatusColor(suggestion.status)
    };
  }

  /**
   * Transform recommendation data for frontend display
   */
  transformRecommendation(recommendation) {
    return {
      ...recommendation,
      createdAt: new Date(recommendation.created_at),
      updatedAt: recommendation.updated_at ? new Date(recommendation.updated_at) : null,
      viewedAt: recommendation.viewed_at ? new Date(recommendation.viewed_at) : null,
      isViewed: !!recommendation.viewed_at,
      isSaved: !!recommendation.saved,
      isDismissed: !!recommendation.dismissed,
      matchPercentage: Math.round((recommendation.match_score || 0) * 100),
      relevancePercentage: Math.round((recommendation.relevance_score || 0) * 100),
      matchColor: this.getMatchColor(recommendation.match_score || 0)
    };
  }

  /**
   * Transform batch data for frontend display
   */
  transformBatch(batch) {
    return {
      ...batch,
      createdAt: new Date(batch.created_at),
      startedAt: batch.started_at ? new Date(batch.started_at) : null,
      completedAt: batch.completed_at ? new Date(batch.completed_at) : null,
      isCompleted: batch.status === 'completed',
      isFailed: batch.status === 'failed',
      isProcessing: batch.status === 'processing',
      successRate: batch.total_suggestions > 0 ? 
        Math.round((batch.successful_suggestions / batch.total_suggestions) * 100) : 0,
      statusDisplay: this.getBatchStatusDisplay(batch.status),
      statusColor: this.getBatchStatusColor(batch.status),
      typeDisplay: this.getBatchTypeDisplay(batch.batch_type)
    };
  }

  /**
   * Get suggestion type display name
   */
  getSuggestionTypeDisplay(type) {
    const typeMap = {
      'keyword_optimization': 'Keyword Optimization',
      'content_enhancement': 'Content Enhancement',
      'skill_highlight': 'Skill Highlighting',
      'format_suggestion': 'Format Improvement',
      'experience_optimization': 'Experience Optimization',
      'resume_improvement': 'Resume Improvement',
      'job_match': 'Job Matching',
      'career_guidance': 'Career Guidance',
      'interview_preparation': 'Interview Preparation',
      'networking_suggestion': 'Networking Suggestion',
      'learning_recommendation': 'Learning Recommendation'
    };
    return typeMap[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
   * Get status display name
   */
  getStatusDisplay(status) {
    const statusMap = {
      'pending': 'Pending',
      'viewed': 'Viewed',
      'accepted': 'Accepted',
      'rejected': 'Rejected',
      'partially_accepted': 'Partially Accepted',
      'expired': 'Expired'
    };
    return statusMap[status] || status;
  }

  /**
   * Get batch type display name
   */
  getBatchTypeDisplay(type) {
    const typeMap = {
      'resume_optimization': 'Resume Optimization',
      'daily_suggestions': 'Daily Suggestions',
      'job_match_analysis': 'Job Match Analysis',
      'skill_assessment': 'Skill Assessment',
      'manual_generation': 'Manual Generation'
    };
    return typeMap[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
   * Get batch status display name
   */
  getBatchStatusDisplay(status) {
    const statusMap = {
      'pending': 'Pending',
      'processing': 'Processing',
      'completed': 'Completed',
      'failed': 'Failed',
      'cancelled': 'Cancelled'
    };
    return statusMap[status] || status;
  }

  /**
   * Get priority color for UI
   */
  getPriorityColor(priority) {
    const colorMap = {
      high: '#dc3545',
      medium: '#ffc107', 
      low: '#28a745'
    };
    return colorMap[priority] || colorMap.medium;
  }

  /**
   * Get confidence color for UI
   */
  getConfidenceColor(confidence) {
    if (confidence >= 0.8) return '#28a745'; // green
    if (confidence >= 0.6) return '#ffc107'; // yellow
    if (confidence >= 0.4) return '#fd7e14'; // orange
    return '#dc3545'; // red
  }

  /**
   * Get status color for UI
   */
  getStatusColor(status) {
    const colorMap = {
      'pending': '#6c757d',
      'viewed': '#17a2b8',
      'accepted': '#28a745',
      'rejected': '#dc3545',
      'partially_accepted': '#ffc107',
      'expired': '#6c757d'
    };
    return colorMap[status] || '#6c757d';
  }

  /**
   * Get match score color for UI
   */
  getMatchColor(score) {
    if (score >= 0.8) return '#28a745'; // green
    if (score >= 0.6) return '#ffc107'; // yellow
    if (score >= 0.4) return '#fd7e14'; // orange
    return '#dc3545'; // red
  }

  /**
   * Get batch status color for UI
   */
  getBatchStatusColor(status) {
    const colorMap = {
      'pending': '#6c757d',
      'processing': '#17a2b8',
      'completed': '#28a745',
      'failed': '#dc3545',
      'cancelled': '#6c757d'
    };
    return colorMap[status] || '#6c757d';
  }

  /**
   * Validate suggestion data before creation
   */
  validateSuggestionData(suggestionData) {
    const errors = [];

    if (!suggestionData.suggestion_type) {
      errors.push('Suggestion type is required');
    }

    if (!suggestionData.title || suggestionData.title.trim().length === 0) {
      errors.push('Title is required');
    }

    if (!suggestionData.description || suggestionData.description.trim().length === 0) {
      errors.push('Description is required');
    }

    if (suggestionData.confidence_score !== undefined) {
      if (suggestionData.confidence_score < 0 || suggestionData.confidence_score > 1) {
        errors.push('Confidence score must be between 0 and 1');
      }
    }

    if (suggestionData.priority && !['low', 'medium', 'high'].includes(suggestionData.priority)) {
      errors.push('Priority must be low, medium, or high');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Validate feedback data before creation
   */
  validateFeedbackData(feedbackData) {
    const errors = [];

    if (!feedbackData.feedback_type) {
      errors.push('Feedback type is required');
    }

    if (!['helpful', 'not_helpful', 'neutral'].includes(feedbackData.feedback_type)) {
      errors.push('Feedback type must be helpful, not_helpful, or neutral');
    }

    if (feedbackData.rating !== undefined) {
      if (feedbackData.rating < 1 || feedbackData.rating > 5) {
        errors.push('Rating must be between 1 and 5');
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Format processing time for display
   */
  formatProcessingTime(timeInSeconds) {
    if (!timeInSeconds || timeInSeconds < 0) return 'N/A';
    
    if (timeInSeconds < 1) {
      return `${Math.round(timeInSeconds * 1000)}ms`;
    } else if (timeInSeconds < 60) {
      return `${timeInSeconds.toFixed(1)}s`;
    } else {
      const minutes = Math.floor(timeInSeconds / 60);
      const seconds = Math.round(timeInSeconds % 60);
      return `${minutes}m ${seconds}s`;
    }
  }

  /**
   * Format confidence score for display
   */
  formatConfidence(confidence) {
    if (confidence === undefined || confidence === null) return 'N/A';
    return `${Math.round(confidence * 100)}%`;
  }

  /**
   * Get suggestion urgency level
   */
  getSuggestionUrgency(suggestion) {
    if (suggestion.priority === 'high') return 'urgent';
    if (suggestion.expires_at) {
      const now = new Date();
      const expires = new Date(suggestion.expires_at);
      const hoursUntilExpiry = (expires - now) / (1000 * 60 * 60);
      if (hoursUntilExpiry < 24) return 'urgent';
      if (hoursUntilExpiry < 72) return 'moderate';
    }
    return 'normal';
  }

  /**
   * Check if suggestion needs attention
   */
  needsAttention(suggestion) {
    return suggestion.priority === 'high' && 
           suggestion.status === 'pending' && 
           !suggestion.viewed_at;
  }

  /**
   * Sort suggestions by relevance
   */
  sortSuggestionsByRelevance(suggestions) {
    return [...suggestions].sort((a, b) => {
      // Priority: high > medium > low
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      const priorityDiff = (priorityOrder[b.priority] || 2) - (priorityOrder[a.priority] || 2);
      if (priorityDiff !== 0) return priorityDiff;

      // Confidence score: higher is better
      const confidenceDiff = (b.confidence_score || 0) - (a.confidence_score || 0);
      if (Math.abs(confidenceDiff) > 0.05) return confidenceDiff;

      // Created date: newer is better
      return new Date(b.created_at) - new Date(a.created_at);
    });
  }
}

const aiSuggestionService = new AISuggestionService();
export default aiSuggestionService;