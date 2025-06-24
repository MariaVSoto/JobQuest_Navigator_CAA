/**
 * Skills and Certifications service for Phase 3 MVP
 * Handles all API calls related to skills management and certification tracking
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class SkillsService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/skills`;
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
      console.error('Skills API request failed:', error);
      throw error;
    }
  }

  // Skill Category Operations

  /**
   * Get skill categories
   */
  async getSkillCategories(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/categories/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific skill category
   */
  async getSkillCategory(categoryId) {
    const response = await this.makeRequest(`/categories/${categoryId}/`);
    return await response.json();
  }

  // Skill Operations

  /**
   * Get skills with filtering and search
   */
  async getSkills(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific skill
   */
  async getSkill(skillId) {
    const response = await this.makeRequest(`/${skillId}/`);
    return await response.json();
  }

  /**
   * Search skills
   */
  async searchSkills(query, filters = {}) {
    const queryParams = new URLSearchParams();
    queryParams.append('search', query);
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const response = await this.makeRequest(`/search/?${queryParams}`);
    return await response.json();
  }

  /**
   * Create a new skill (admin only)
   */
  async createSkill(skillData) {
    const response = await this.makeRequest('/create/', {
      method: 'POST',
      body: JSON.stringify(skillData),
    });
    return await response.json();
  }

  // User Skills Operations

  /**
   * Get user's skills
   */
  async getUserSkills(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/user/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Add a skill to user's profile
   */
  async addUserSkill(skillData) {
    const response = await this.makeRequest('/user/', {
      method: 'POST',
      body: JSON.stringify(skillData),
    });
    return await response.json();
  }

  /**
   * Update user's skill
   */
  async updateUserSkill(userSkillId, skillData) {
    const response = await this.makeRequest(`/user/${userSkillId}/`, {
      method: 'PUT',
      body: JSON.stringify(skillData),
    });
    return await response.json();
  }

  /**
   * Remove user's skill
   */
  async removeUserSkill(userSkillId) {
    await this.makeRequest(`/user/${userSkillId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  // Certification Operations

  /**
   * Get available certifications
   */
  async getCertifications(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/certifications/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific certification
   */
  async getCertification(certificationId) {
    const response = await this.makeRequest(`/certifications/${certificationId}/`);
    return await response.json();
  }

  // User Certification Operations

  /**
   * Get user's certifications
   */
  async getUserCertifications(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/user-certifications/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Add a certification to user's profile
   */
  async addUserCertification(certificationData) {
    const response = await this.makeRequest('/user-certifications/', {
      method: 'POST',
      body: JSON.stringify(certificationData),
    });
    return await response.json();
  }

  /**
   * Update user's certification
   */
  async updateUserCertification(userCertificationId, certificationData) {
    const response = await this.makeRequest(`/user-certifications/${userCertificationId}/`, {
      method: 'PUT',
      body: JSON.stringify(certificationData),
    });
    return await response.json();
  }

  /**
   * Remove user's certification
   */
  async removeUserCertification(userCertificationId) {
    await this.makeRequest(`/user-certifications/${userCertificationId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  // Learning Path Operations

  /**
   * Get learning paths
   */
  async getLearningPaths(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/learning-paths/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific learning path
   */
  async getLearningPath(learningPathId) {
    const response = await this.makeRequest(`/learning-paths/${learningPathId}/`);
    return await response.json();
  }

  /**
   * Get user's learning paths
   */
  async getUserLearningPaths(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/user-learning-paths/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Enroll in a learning path
   */
  async enrollInLearningPath(learningPathData) {
    const response = await this.makeRequest('/user-learning-paths/', {
      method: 'POST',
      body: JSON.stringify(learningPathData),
    });
    return await response.json();
  }

  /**
   * Update learning path progress
   */
  async updateLearningPathProgress(userLearningPathId, progressData) {
    const response = await this.makeRequest(`/user-learning-paths/${userLearningPathId}/`, {
      method: 'PUT',
      body: JSON.stringify(progressData),
    });
    return await response.json();
  }

  // Skill Assessment Operations

  /**
   * Get skill assessments
   */
  async getSkillAssessments(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/assessments/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get user's skill assessments
   */
  async getUserSkillAssessments(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/user-assessments/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Take a skill assessment
   */
  async takeSkillAssessment(assessmentData) {
    const response = await this.makeRequest('/user-assessments/', {
      method: 'POST',
      body: JSON.stringify(assessmentData),
    });
    return await response.json();
  }

  // Utility Methods

  /**
   * Get proficiency level display
   */
  getProficiencyDisplay(level) {
    const levelMap = {
      'beginner': 'Beginner',
      'intermediate': 'Intermediate', 
      'advanced': 'Advanced',
      'expert': 'Expert'
    };
    return levelMap[level] || level;
  }

  /**
   * Get proficiency level color
   */
  getProficiencyColor(level) {
    const colorMap = {
      'beginner': '#ffc107',
      'intermediate': '#17a2b8',
      'advanced': '#28a745',
      'expert': '#6f42c1'
    };
    return colorMap[level] || '#6c757d';
  }

  /**
   * Get certification status display
   */
  getCertificationStatusDisplay(status) {
    const statusMap = {
      'active': 'Active',
      'expired': 'Expired',
      'in_progress': 'In Progress',
      'planned': 'Planned'
    };
    return statusMap[status] || status;
  }

  /**
   * Get certification status color
   */
  getCertificationStatusColor(status) {
    const colorMap = {
      'active': '#28a745',
      'expired': '#dc3545',
      'in_progress': '#ffc107',
      'planned': '#6c757d'
    };
    return colorMap[status] || '#6c757d';
  }

  /**
   * Get market demand display
   */
  getMarketDemandDisplay(demand) {
    const demandMap = {
      'very_low': 'Very Low',
      'low': 'Low',
      'moderate': 'Moderate',
      'high': 'High',
      'very_high': 'Very High'
    };
    return demandMap[demand] || demand;
  }

  /**
   * Get market demand color
   */
  getMarketDemandColor(demand) {
    const colorMap = {
      'very_low': '#dc3545',
      'low': '#fd7e14',
      'moderate': '#ffc107',
      'high': '#28a745',
      'very_high': '#007bff'
    };
    return colorMap[demand] || '#6c757d';
  }

  /**
   * Calculate skill completion percentage
   */
  calculateSkillCompletion(userSkill) {
    const weights = {
      'beginner': 25,
      'intermediate': 50,
      'advanced': 75,
      'expert': 100
    };
    
    const currentLevel = weights[userSkill.proficiency_level] || 0;
    const targetLevel = weights[userSkill.target_proficiency] || 100;
    
    return Math.min(100, Math.round((currentLevel / targetLevel) * 100));
  }

  /**
   * Format salary range
   */
  formatSalary(amount) {
    if (!amount) return 'Not specified';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }

  /**
   * Calculate learning path progress
   */
  calculateLearningPathProgress(userLearningPath) {
    if (!userLearningPath) return 0;
    return userLearningPath.progress_percentage || 0;
  }

  /**
   * Get learning path status color
   */
  getLearningPathStatusColor(status) {
    const colorMap = {
      'not_started': '#6c757d',
      'in_progress': '#ffc107',
      'completed': '#28a745',
      'paused': '#fd7e14'
    };
    return colorMap[status] || '#6c757d';
  }

  /**
   * Validate skill data
   */
  validateSkillData(skillData) {
    const errors = [];

    if (!skillData.skill && !skillData.skill_name) {
      errors.push('Skill is required');
    }

    if (!skillData.proficiency_level) {
      errors.push('Proficiency level is required');
    }

    const validProficiencyLevels = ['beginner', 'intermediate', 'advanced', 'expert'];
    if (skillData.proficiency_level && !validProficiencyLevels.includes(skillData.proficiency_level)) {
      errors.push('Invalid proficiency level');
    }

    if (skillData.years_experience && skillData.years_experience < 0) {
      errors.push('Years of experience cannot be negative');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Validate certification data
   */
  validateCertificationData(certificationData) {
    const errors = [];

    if (!certificationData.certification) {
      errors.push('Certification is required');
    }

    if (!certificationData.status) {
      errors.push('Status is required');
    }

    const validStatuses = ['active', 'expired', 'in_progress', 'planned'];
    if (certificationData.status && !validStatuses.includes(certificationData.status)) {
      errors.push('Invalid certification status');
    }

    if (certificationData.earned_date && certificationData.expiry_date) {
      const earnedDate = new Date(certificationData.earned_date);
      const expiryDate = new Date(certificationData.expiry_date);
      if (earnedDate >= expiryDate) {
        errors.push('Expiry date must be after earned date');
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

const skillsService = new SkillsService();
export default skillsService;