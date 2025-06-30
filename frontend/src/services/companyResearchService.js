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
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/interview-questions/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching interview questions, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 'mock-q-1',
            question_text: 'Tell me about yourself and your experience.',
            question_type: 'general',
            difficulty: 'easy',
            difficulty_display: 'Easy',
            sample_answer: 'Start with a brief professional summary, highlight key achievements, and connect your experience to the role.',
            answer_framework: 'Past-Present-Future structure',
            is_generated: false,
            times_used: 25
          },
          {
            id: 'mock-q-2',
            question_text: 'Explain the difference between var, let, and const in JavaScript.',
            question_type: 'technical',
            difficulty: 'medium',
            difficulty_display: 'Medium',
            sample_answer: 'var has function scope, let and const have block scope. const cannot be reassigned.',
            answer_framework: 'Definition + Examples + Use Cases',
            is_generated: true,
            times_used: 18
          },
          {
            id: 'mock-q-3',
            question_text: 'Describe a time when you had to work with a difficult team member.',
            question_type: 'behavioral',
            difficulty: 'medium',
            difficulty_display: 'Medium',
            sample_answer: 'Use the STAR method to structure your response with specific examples.',
            answer_framework: 'STAR (Situation, Task, Action, Result)',
            is_generated: false,
            times_used: 12
          }
        ]
      };
    }
  }

  /**
   * Get specific interview question by ID
   */
  async getInterviewQuestionById(id) {
    const response = await this.makeRequest(`/interview-questions/${id}/`);
    return await response.json();
  }

  /**
   * Create interview question
   */
  async createInterviewQuestion(data) {
    const response = await this.makeRequest('/interview-questions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Generate interview questions
   */
  async generateInterviewQuestions(questionType, difficulty = 'medium', companyId = null, positionType = '') {
    const response = await this.makeRequest('/interview-questions/generate/', {
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

  /**
   * Update interview question
   */
  async updateInterviewQuestion(id, data) {
    const response = await this.makeRequest(`/interview-questions/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Delete interview question
   */
  async deleteInterviewQuestion(id) {
    await this.makeRequest(`/interview-questions/${id}/`, {
      method: 'DELETE',
    });
  }

  /**
   * Rate an interview question
   */
  async rateInterviewQuestion(id, rating) {
    const response = await this.makeRequest(`/interview-questions/${id}/rate/`, {
      method: 'POST',
      body: JSON.stringify({ rating }),
    });
    return await response.json();
  }

  // Practice Sessions Methods

  /**
   * Get practice sessions
   */
  async getPracticeSessions(filters = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/practice-sessions/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching practice sessions, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 'mock-session-1',
            session_type: 'mock_interview',
            session_type_display: 'Mock Interview',
            completion_status: 'completed',
            completion_status_display: 'Completed',
            duration_minutes: 45,
            questions_attempted: 8,
            self_rating: 4,
            notes: 'Good overall performance, need to work on technical questions.',
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() // 2 days ago
          },
          {
            id: 'mock-session-2',
            session_type: 'question_practice',
            session_type_display: 'Question Practice',
            completion_status: 'completed',
            completion_status_display: 'Completed',
            duration_minutes: 30,
            questions_attempted: 12,
            self_rating: 3,
            notes: 'Focused on behavioral questions. Need more practice with STAR method.',
            created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString() // 5 days ago
          },
          {
            id: 'mock-session-3',
            session_type: 'mock_interview',
            session_type_display: 'Mock Interview',
            completion_status: 'in_progress',
            completion_status_display: 'In Progress',
            duration_minutes: 15,
            questions_attempted: 3,
            self_rating: null,
            notes: null,
            created_at: new Date().toISOString()
          }
        ]
      };
    }
  }

  /**
   * Get specific practice session by ID
   */
  async getPracticeSessionById(id) {
    const response = await this.makeRequest(`/practice-sessions/${id}/`);
    return await response.json();
  }

  /**
   * Create practice session
   */
  async createPracticeSession(data) {
    const response = await this.makeRequest('/practice-sessions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Start new practice session
   */
  async startPracticeSession(sessionType, companyId = null) {
    const response = await this.makeRequest('/practice-sessions/start/', {
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
    const response = await this.makeRequest(`/practice-sessions/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Delete practice session
   */
  async deletePracticeSession(id) {
    await this.makeRequest(`/practice-sessions/${id}/`, {
      method: 'DELETE',
    });
  }

  /**
   * Complete practice session
   */
  async completePracticeSession(id, sessionData) {
    const response = await this.makeRequest(`/practice-sessions/${id}/complete/`, {
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
    return await response.json();
  }

  /**
   * Get recent practice sessions for dashboard
   */
  async getRecentPracticeSessions() {
    const response = await this.makeRequest('/practice-sessions/recent/');
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

    const endpoint = `/company-insights/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get specific company insight by ID
   */
  async getCompanyInsightById(id) {
    const response = await this.makeRequest(`/company-insights/${id}/`);
    return await response.json();
  }

  /**
   * Create company insight
   */
  async createCompanyInsight(data) {
    const response = await this.makeRequest('/company-insights/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Update company insight
   */
  async updateCompanyInsight(id, data) {
    const response = await this.makeRequest(`/company-insights/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return await response.json();
  }

  /**
   * Delete company insight
   */
  async deleteCompanyInsight(id) {
    await this.makeRequest(`/company-insights/${id}/`, {
      method: 'DELETE',
    });
  }

  /**
   * Upvote company insight
   */
  async upvoteCompanyInsight(id) {
    const response = await this.makeRequest(`/company-insights/${id}/upvote/`, {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Downvote company insight
   */
  async downvoteCompanyInsight(id) {
    const response = await this.makeRequest(`/company-insights/${id}/downvote/`, {
      method: 'POST',
    });
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

    const endpoint = `/company-news/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get specific news article by ID
   */
  async getCompanyNewsById(id) {
    const response = await this.makeRequest(`/company-news/${id}/`);
    return await response.json();
  }

  /**
   * Get recent company news for dashboard
   */
  async getRecentCompanyNews() {
    const response = await this.makeRequest('/company-news/recent/');
    return await response.json();
  }

  /**
   * Get interview tips by category
   */
  async getInterviewTips(category = 'general') {
    try {
      const response = await this.makeRequest(`/interview-tips/?category=${category}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching interview tips, using mock data:', error);
      // Return mock data for demo
      const mockTips = {
        general: [
          {
            id: 'tip-g-1',
            title: 'Research the Company',
            content: 'Spend time researching the company\'s mission, values, recent news, and culture. This shows genuine interest and helps you ask informed questions.',
            category: 'general',
            priority: 'high'
          },
          {
            id: 'tip-g-2',
            title: 'Prepare Your STAR Stories',
            content: 'Have 3-5 specific examples ready using the STAR method (Situation, Task, Action, Result) to demonstrate your skills and experience.',
            category: 'general',
            priority: 'high'
          },
          {
            id: 'tip-g-3',
            title: 'Dress Appropriately',
            content: 'Dress slightly more formal than the company\'s usual dress code. When in doubt, business professional is usually safe.',
            category: 'general',
            priority: 'medium'
          }
        ],
        technical: [
          {
            id: 'tip-t-1',
            title: 'Practice Coding Problems',
            content: 'Review fundamental data structures and algorithms. Practice coding problems on platforms like LeetCode or HackerRank.',
            category: 'technical',
            priority: 'high'
          },
          {
            id: 'tip-t-2',
            title: 'Know Your Resume',
            content: 'Be prepared to discuss any technology, project, or experience mentioned on your resume in detail.',
            category: 'technical',
            priority: 'high'
          },
          {
            id: 'tip-t-3',
            title: 'Think Out Loud',
            content: 'During technical problems, verbalize your thought process. Interviewers want to see how you approach problems.',
            category: 'technical',
            priority: 'medium'
          }
        ],
        behavioral: [
          {
            id: 'tip-b-1',
            title: 'Use Specific Examples',
            content: 'Always provide concrete examples when answering behavioral questions. Avoid hypothetical scenarios.',
            category: 'behavioral',
            priority: 'high'
          },
          {
            id: 'tip-b-2',
            title: 'Show Self-Awareness',
            content: 'Demonstrate that you can reflect on your experiences and learn from both successes and failures.',
            category: 'behavioral',
            priority: 'medium'
          },
          {
            id: 'tip-b-3',
            title: 'Highlight Collaboration',
            content: 'Emphasize your ability to work well with others and contribute to team success.',
            category: 'behavioral',
            priority: 'medium'
          }
        ]
      };
      
      return {
        results: mockTips[category] || []
      };
    }
  }

  /**
   * Get interview resources
   */
  async getInterviewResources(filters = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/interview-resources/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching interview resources, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 'resource-1',
            resource_type: 'article',
            title: 'The Complete Guide to Technical Interviews',
            description: 'Comprehensive guide covering all aspects of technical interviews, from preparation to follow-up.',
            url: 'https://example.com/technical-interview-guide',
            category: 'technical',
            difficulty: 'intermediate'
          },
          {
            id: 'resource-2',
            resource_type: 'video',
            title: 'Behavioral Interview Mastery',
            description: 'Video series on answering behavioral questions using the STAR method with real examples.',
            url: 'https://example.com/behavioral-interviews',
            category: 'behavioral',
            difficulty: 'beginner'
          },
          {
            id: 'resource-3',
            resource_type: 'book',
            title: 'Cracking the Coding Interview',
            description: 'Classic resource for preparing for technical coding interviews at top tech companies.',
            file_url: 'https://example.com/download/coding-interview-book',
            category: 'technical',
            difficulty: 'advanced'
          },
          {
            id: 'resource-4',
            resource_type: 'checklist',
            title: 'Interview Day Preparation Checklist',
            description: 'Complete checklist to ensure you\'re fully prepared for your interview day.',
            url: 'https://example.com/interview-checklist',
            category: 'general',
            difficulty: 'beginner'
          }
        ]
      };
    }
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