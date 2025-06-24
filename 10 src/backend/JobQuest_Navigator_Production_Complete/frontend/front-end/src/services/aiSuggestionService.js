/**
 * Simplified AI Suggestions service for Phase 2 MVP
 * Handles all API calls related to AI suggestions and job recommendations
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class AISuggestionService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/ai-simple`;
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

  // AI Suggestions Methods

  /**
   * Get user's AI suggestions
   */
  async getSuggestions(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/suggestions/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Generate AI suggestions for resume
   */
  async generateResumeSuggestions(resumeId) {
    const response = await this.makeRequest('/suggestions/generate/', {
      method: 'POST',
      body: JSON.stringify({ resume_id: resumeId }),
    });
    return await response.json();
  }

  /**
   * Take action on a suggestion (accept/reject/viewed)
   */
  async suggestionAction(suggestionId, action, notes = '') {
    const response = await this.makeRequest(`/suggestions/${suggestionId}/action/`, {
      method: 'POST',
      body: JSON.stringify({ action, notes }),
    });
    return await response.json();
  }

  // Job Recommendations Methods

  /**
   * Get user's job recommendations
   */
  async getJobRecommendations(limit = 10) {
    const response = await this.makeRequest(`/recommendations/?limit=${limit}`);
    return await response.json();
  }

  /**
   * Generate new job recommendations
   */
  async generateJobRecommendations() {
    const response = await this.makeRequest('/recommendations/generate/', {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Take action on a recommendation (save/dismiss/viewed)
   */
  async recommendationAction(recommendationId, action) {
    const response = await this.makeRequest(`/recommendations/${recommendationId}/action/`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
    return await response.json();
  }

  // Analytics Methods

  /**
   * Get simple analytics
   */
  async getAnalytics() {
    const response = await this.makeRequest('/analytics/');
    return await response.json();
  }

  // Utility Methods

  /**
   * Mark suggestion as viewed
   */
  async markSuggestionViewed(suggestionId) {
    return await this.suggestionAction(suggestionId, 'viewed');
  }

  /**
   * Accept suggestion
   */
  async acceptSuggestion(suggestionId, notes = '') {
    return await this.suggestionAction(suggestionId, 'accept', notes);
  }

  /**
   * Reject suggestion
   */
  async rejectSuggestion(suggestionId, notes = '') {
    return await this.suggestionAction(suggestionId, 'reject', notes);
  }

  /**
   * Save job recommendation
   */
  async saveRecommendation(recommendationId) {
    return await this.recommendationAction(recommendationId, 'save');
  }

  /**
   * Dismiss job recommendation
   */
  async dismissRecommendation(recommendationId) {
    return await this.recommendationAction(recommendationId, 'dismiss');
  }

  /**
   * Mark recommendation as viewed
   */
  async markRecommendationViewed(recommendationId) {
    return await this.recommendationAction(recommendationId, 'viewed');
  }

  /**
   * Get suggestions by type
   */
  async getSuggestionsByType(type, limit = 10) {
    return await this.getSuggestions({ type, limit });
  }

  /**
   * Get pending suggestions
   */
  async getPendingSuggestions(limit = 10) {
    return await this.getSuggestions({ status: 'pending', limit });
  }

  /**
   * Get accepted suggestions
   */
  async getAcceptedSuggestions(limit = 10) {
    return await this.getSuggestions({ status: 'accepted', limit });
  }

  /**
   * Transform suggestion data for frontend
   */
  transformSuggestion(suggestion) {
    return {
      ...suggestion,
      createdAt: new Date(suggestion.created_at),
      isViewed: suggestion.viewed,
      isActedOn: suggestion.acted_on,
      priority: suggestion.priority || 'medium',
      confidencePercentage: Math.round(suggestion.confidence * 100),
    };
  }

  /**
   * Transform recommendation data for frontend
   */
  transformRecommendation(recommendation) {
    return {
      ...recommendation,
      createdAt: new Date(recommendation.created_at),
      matchPercentage: Math.round(recommendation.match_score * 100),
      isViewed: recommendation.viewed,
      isSaved: recommendation.saved,
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
    };
    return typeMap[type] || type;
  }

  /**
   * Get priority color for UI
   */
  getPriorityColor(priority) {
    const colorMap = {
      high: '#ff4757',
      medium: '#ffa502',
      low: '#2ed573',
    };
    return colorMap[priority] || colorMap.medium;
  }

  /**
   * Get confidence color for UI
   */
  getConfidenceColor(confidence) {
    if (confidence >= 0.8) return '#2ed573'; // green
    if (confidence >= 0.6) return '#ffa502'; // orange
    return '#ff4757'; // red
  }
}

const aiSuggestionService = new AISuggestionService();
export default aiSuggestionService;