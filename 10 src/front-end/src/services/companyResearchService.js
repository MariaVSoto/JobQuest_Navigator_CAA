/**
 * Company Research service for Epic 6: Company Research & Interview Preparation
 * Handles all API calls related to company research and interview preparation
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class CompanyResearchService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/company-research`;
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
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Company Research Methods

  /**
   * Get all company research for user
   */
  async getCompanyResearch(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/company-research/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get specific company research by ID
   */
  async getCompanyResearchById(id) {
    const response = await this.makeRequest(`/company-research/${id}/`);
    return await response.json();
  }

  /**
   * Create new company research
   */
  async createCompanyResearch(data) {
    const response = await this.makeRequest('/company-research/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Generate new company research
   */
  async generateCompanyResearch(companyId) {
    const response = await this.makeRequest('/company-research/generate/', {
      method: 'POST',
      body: JSON.stringify({ company_id: companyId }),
    });
    return await response.json();
  }

  /**
   * Update company research
   */
  async updateCompanyResearch(id, data) {
    const response = await this.makeRequest(`/company-research/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Partially update company research
   */
  async patchCompanyResearch(id, data) {
    const response = await this.makeRequest(`/company-research/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Delete company research
   */
  async deleteCompanyResearch(id) {
    await this.makeRequest(`/company-research/${id}/`, {
      method: 'DELETE',
    });
  }

  /**
   * Save research item
   */
  async saveResearchItem(id, notes = '', tags = []) {
    const response = await this.makeRequest(`/company-research/${id}/save/`, {
      method: 'POST',
      body: JSON.stringify({ notes, tags }),
    });
    return await response.json();
  }

  /**
   * Unsave research item
   */
  async unsaveResearchItem(id) {
    await this.makeRequest(`/company-research/${id}/unsave/`, {
      method: 'DELETE',
    });
  }

  /**
   * Get saved research
   */
  async getSavedResearch() {
    const response = await this.makeRequest('/company-research/saved/');
    return await response.json();
  }

  // Interview Preparation Methods

  /**
   * Get interview preparations
   */
  async getInterviewPreparations(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/interview-preparation/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get specific interview preparation by ID
   */
  async getInterviewPreparationById(id) {
    const response = await this.makeRequest(`/interview-preparation/${id}/`);
    return await response.json();
  }

  /**
   * Create interview preparation
   */
  async createInterviewPreparation(data) {
    const response = await this.makeRequest('/interview-preparation/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Generate interview preparation
   */
  async generateInterviewPreparation(researchId, positionTitle = '') {
    const response = await this.makeRequest('/interview-preparation/generate/', {
      method: 'POST',
      body: JSON.stringify({
        research_id: researchId,
        position_title: positionTitle,
      }),
    });
    return await response.json();
  }

  /**
   * Update interview preparation
   */
  async updateInterviewPreparation(id, data) {
    const response = await this.makeRequest(`/interview-preparation/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Partially update interview preparation
   */
  async patchInterviewPreparation(id, data) {
    const response = await this.makeRequest(`/interview-preparation/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Delete interview preparation
   */
  async deleteInterviewPreparation(id) {
    await this.makeRequest(`/interview-preparation/${id}/`, {
      method: 'DELETE',
    });
  }

  /**
   * Mark preparation as reviewed
   */
  async markPreparationReviewed(id) {
    const response = await this.makeRequest(`/interview-preparation/${id}/mark_reviewed/`, {
      method: 'POST',
    });
    return await response.json();
  }

  // Interview Questions Methods

  /**
   * Get interview questions
   */
  async getInterviewQuestions(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/questions/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get specific interview question by ID
   */
  async getInterviewQuestionById(id) {
    const response = await this.makeRequest(`/questions/${id}/`);
    return await response.json();
  }

  /**
   * Generate interview questions
   */
  async generateInterviewQuestions(questionType, difficulty = 'medium', companyId = null, positionType = '') {
    const response = await this.makeRequest('/questions/generate/', {
      method: 'POST',
      body: JSON.stringify({
        question_type: questionType,
        difficulty,
        company_id: companyId,
        position_type: positionType,
      }),
    });
    return await response.json();
  }

  // Practice Sessions Methods

  /**
   * Get practice sessions
   */
  async getPracticeSessions(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/practice/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get specific practice session by ID
   */
  async getPracticeSessionById(id) {
    const response = await this.makeRequest(`/practice/${id}/`);
    return await response.json();
  }

  /**
   * Start new practice session
   */
  async startPracticeSession(sessionType, companyId = null) {
    const response = await this.makeRequest('/practice/start/', {
      method: 'POST',
      body: JSON.stringify({
        session_type: sessionType,
        company_id: companyId,
      }),
    });
    return await response.json();
  }

  /**
   * Update practice session
   */
  async updatePracticeSession(id, data) {
    const response = await this.makeRequest(`/practice/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  // Company Insights Methods

  /**
   * Get company insights
   */
  async getCompanyInsights(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/insights/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get specific company insight by ID
   */
  async getCompanyInsightById(id) {
    const response = await this.makeRequest(`/insights/${id}/`);
    return await response.json();
  }

  // Company News Methods

  /**
   * Get company news
   */
  async getCompanyNews(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/news/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get specific news article by ID
   */
  async getCompanyNewsById(id) {
    const response = await this.makeRequest(`/news/${id}/`);
    return await response.json();
  }

  // Saved Research Methods

  /**
   * Get saved research
   */
  async getSavedResearch() {
    const response = await this.makeRequest('/saved/');
    return await response.json();
  }

  /**
   * Save research
   */
  async saveResearch(researchId, notes = '', tags = []) {
    const response = await this.makeRequest(`/${researchId}/save/`, {
      method: 'POST',
      body: JSON.stringify({ notes, tags }),
    });
    return await response.json();
  }

  /**
   * Unsave research
   */
  async unsaveResearch(researchId) {
    await this.makeRequest(`/${researchId}/unsave/`, {
      method: 'DELETE',
    });
  }

  // Utility Methods

  /**
   * Transform API data for frontend consumption
   */
  transformResearchData(research) {
    return {
      ...research,
      researchDate: new Date(research.research_date),
      createdAt: new Date(research.created_at),
      updatedAt: new Date(research.updated_at),
    };
  }

  /**
   * Transform interview question data
   */
  transformQuestionData(question) {
    return {
      ...question,
      createdAt: new Date(question.created_at),
      updatedAt: new Date(question.updated_at),
    };
  }

  /**
   * Transform practice session data
   */
  transformSessionData(session) {
    return {
      ...session,
      createdAt: new Date(session.created_at),
      updatedAt: new Date(session.updated_at),
      sessionData: typeof session.session_data === 'string' 
        ? JSON.parse(session.session_data) 
        : session.session_data,
    };
  }
}

export default new CompanyResearchService();