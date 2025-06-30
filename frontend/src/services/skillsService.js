/**
 * Skills and Certifications service for Phase 3 MVP
 * Handles all API calls related to skills management and certification tracking
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

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
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/categories/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching skill categories, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 1,
            name: 'Programming Languages',
            description: 'Programming and scripting languages',
            icon: '💻',
            skill_count: 25
          },
          {
            id: 2,
            name: 'Frontend Frameworks',
            description: 'Frontend development frameworks and libraries',
            icon: '🎨',
            skill_count: 15
          },
          {
            id: 3,
            name: 'Backend Frameworks',
            description: 'Backend development frameworks and tools',
            icon: '⚙️',
            skill_count: 18
          },
          {
            id: 4,
            name: 'Databases',
            description: 'Database technologies and tools',
            icon: '💾',
            skill_count: 12
          },
          {
            id: 5,
            name: 'Cloud Computing',
            description: 'Cloud platforms and services',
            icon: '☁️',
            skill_count: 20
          }
        ]
      };
    }
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
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/skills/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching skills, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 1,
            name: 'JavaScript',
            description: 'Dynamic programming language for web development',
            category: 1,
            market_demand: 'very_high',
            average_salary: 85000,
            is_trending: true,
            popularity_score: 95
          },
          {
            id: 2,
            name: 'React',
            description: 'JavaScript library for building user interfaces',
            category: 2,
            market_demand: 'high',
            average_salary: 90000,
            is_trending: true,
            popularity_score: 88
          },
          {
            id: 3,
            name: 'Python',
            description: 'High-level programming language for various applications',
            category: 1,
            market_demand: 'very_high',
            average_salary: 88000,
            is_trending: true,
            popularity_score: 92
          },
          {
            id: 4,
            name: 'Node.js',
            description: 'JavaScript runtime for server-side development',
            category: 3,
            market_demand: 'high',
            average_salary: 87000,
            is_trending: false,
            popularity_score: 82
          },
          {
            id: 5,
            name: 'PostgreSQL',
            description: 'Advanced open-source relational database',
            category: 4,
            market_demand: 'high',
            average_salary: 78000,
            is_trending: false,
            popularity_score: 75
          },
          {
            id: 6,
            name: 'AWS',
            description: 'Amazon Web Services cloud computing platform',
            category: 5,
            market_demand: 'very_high',
            average_salary: 95000,
            is_trending: true,
            popularity_score: 89
          }
        ]
      };
    }
  }

  /**
   * Get a specific skill
   */
  async getSkill(skillId) {
    const response = await this.makeRequest(`/skills/${skillId}/`);
    return await response.json();
  }

  /**
   * Search skills (using DRF's built-in search)
   */
  async searchSkills(query, filters = {}) {
    const queryParams = new URLSearchParams();
    queryParams.append('search', query);
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const response = await this.makeRequest(`/skills/?${queryParams}`);
    return await response.json();
  }

  /**
   * Create a new skill (admin only)
   */
  async createSkill(skillData) {
    const response = await this.makeRequest('/skills/', {
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
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/user-skills/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching user skills, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 'mock-skill-1',
            skill: {
              id: 1,
              name: 'JavaScript',
              category: 'Programming Languages'
            },
            proficiency_level: 'advanced',
            years_experience: 3,
            verified: true,
            last_updated: new Date().toISOString()
          },
          {
            id: 'mock-skill-2',
            skill: {
              id: 2,
              name: 'React',
              category: 'Frontend Frameworks'
            },
            proficiency_level: 'intermediate',
            years_experience: 2,
            verified: true,
            last_updated: new Date().toISOString()
          },
          {
            id: 'mock-skill-3',
            skill: {
              id: 3,
              name: 'Python',
              category: 'Programming Languages'
            },
            proficiency_level: 'beginner',
            years_experience: 1,
            verified: false,
            last_updated: new Date().toISOString()
          }
        ]
      };
    }
  }

  /**
   * Add a skill to user's profile
   */
  async addUserSkill(skillData) {
    const response = await this.makeRequest('/user-skills/', {
      method: 'POST',
      body: JSON.stringify(skillData),
    });
    return await response.json();
  }

  /**
   * Update user's skill
   */
  async updateUserSkill(userSkillId, skillData) {
    const response = await this.makeRequest(`/user-skills/${userSkillId}/`, {
      method: 'PUT',
      body: JSON.stringify(skillData),
    });
    return await response.json();
  }

  /**
   * Remove user's skill
   */
  async removeUserSkill(userSkillId) {
    await this.makeRequest(`/user-skills/${userSkillId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  // Certification Operations

  /**
   * Get available certifications
   */
  async getCertifications(filters = {}) {
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/certifications/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching certifications, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 1,
            name: 'AWS Certified Solutions Architect',
            issuing_organization: 'Amazon Web Services',
            description: 'Validates expertise in designing distributed systems on AWS',
            category: 'Cloud Computing',
            difficulty_level: 'intermediate',
            average_preparation_time: '120 hours',
            popularity_score: 95
          },
          {
            id: 2,
            name: 'Google Analytics Certified',
            issuing_organization: 'Google',
            description: 'Demonstrates proficiency in Google Analytics',
            category: 'Digital Marketing',
            difficulty_level: 'beginner',
            average_preparation_time: '40 hours',
            popularity_score: 88
          },
          {
            id: 3,
            name: 'Certified Scrum Master',
            issuing_organization: 'Scrum Alliance',
            description: 'Validates knowledge of Scrum framework and agile principles',
            category: 'Project Management',
            difficulty_level: 'intermediate',
            average_preparation_time: '60 hours',
            popularity_score: 82
          },
          {
            id: 4,
            name: 'React Developer Certification',
            issuing_organization: 'Meta',
            description: 'Validates skills in React development and best practices',
            category: 'Frontend Development',
            difficulty_level: 'intermediate',
            average_preparation_time: '80 hours',
            popularity_score: 79
          }
        ]
      };
    }
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
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/user-certifications/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching user certifications, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 'mock-cert-1',
            certification: {
              id: 1,
              name: 'AWS Certified Solutions Architect',
              provider: 'Amazon Web Services',
              category: 'Cloud Computing'
            },
            status: 'active',
            earned_date: '2023-01-15',
            expiry_date: '2026-01-15',
            verification_url: 'https://example.com/verify/cert1',
            score: 85
          },
          {
            id: 'mock-cert-2',
            certification: {
              id: 2,
              name: 'Google Analytics Certified',
              provider: 'Google',
              category: 'Digital Marketing'
            },
            status: 'active',
            earned_date: '2023-06-20',
            expiry_date: '2024-06-20',
            verification_url: 'https://example.com/verify/cert2',
            score: 92
          },
          {
            id: 'mock-cert-3',
            certification: {
              id: 3,
              name: 'Certified Scrum Master',
              provider: 'Scrum Alliance',
              category: 'Project Management'
            },
            status: 'in_progress',
            planned_date: '2024-03-01',
            progress_percentage: 65
          }
        ]
      };
    }
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
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/learning-paths/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching learning paths, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 1,
            name: 'Full Stack Web Developer',
            description: 'Comprehensive path to become a full stack web developer using modern technologies',
            difficulty_level: 'intermediate',
            estimated_duration_weeks: 24,
            target_role: 'Full Stack Developer',
            is_featured: true,
            completion_rate: 78
          },
          {
            id: 2,
            name: 'Cloud Infrastructure Specialist',
            description: 'Learn cloud computing fundamentals and advanced AWS services',
            difficulty_level: 'advanced',
            estimated_duration_weeks: 16,
            target_role: 'Cloud Engineer',
            is_featured: true,
            completion_rate: 65
          },
          {
            id: 3,
            name: 'Data Science Fundamentals',
            description: 'Introduction to data science with Python, statistics, and machine learning',
            difficulty_level: 'beginner',
            estimated_duration_weeks: 20,
            target_role: 'Data Scientist',
            is_featured: true,
            completion_rate: 72
          },
          {
            id: 4,
            name: 'DevOps Engineer Path',
            description: 'Master DevOps tools and practices for modern software delivery',
            difficulty_level: 'advanced',
            estimated_duration_weeks: 18,
            target_role: 'DevOps Engineer',
            is_featured: false,
            completion_rate: 69
          }
        ]
      };
    }
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
    try {
      const queryParams = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, value);
      });

      const endpoint = `/user-learning-paths/${queryParams.toString() ? `?${queryParams}` : ''}`;
      const response = await this.makeRequest(endpoint);
      return await response.json();
    } catch (error) {
      console.error('Error fetching user learning paths, using mock data:', error);
      // Return mock data for demo
      return {
        results: [
          {
            id: 'user-path-1',
            learning_path: {
              id: 1,
              name: 'Full Stack Web Developer',
              description: 'Comprehensive path to become a full stack web developer using modern technologies',
              difficulty_level: 'intermediate',
              estimated_duration_weeks: 24,
              target_role: 'Full Stack Developer'
            },
            status: 'in_progress',
            progress_percentage: 35,
            started_date: '2024-01-15',
            target_completion_date: '2024-07-15',
            total_study_hours: 45
          },
          {
            id: 'user-path-2',
            learning_path: {
              id: 3,
              name: 'Data Science Fundamentals',
              description: 'Introduction to data science with Python, statistics, and machine learning',
              difficulty_level: 'beginner',
              estimated_duration_weeks: 20,
              target_role: 'Data Scientist'
            },
            status: 'not_started',
            progress_percentage: 0,
            started_date: null,
            target_completion_date: '2024-09-01',
            total_study_hours: 0
          }
        ]
      };
    }
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
    const response = await this.makeRequest(`/user-learning-paths/${userLearningPathId}/update_progress/`, {
      method: 'POST',
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
  async takeSkillAssessment(assessmentId, assessmentData) {
    const response = await this.makeRequest(`/user-assessments/${assessmentId}/take_assessment/`, {
      method: 'POST',
      body: JSON.stringify(assessmentData),
    });
    return await response.json();
  }

  /**
   * Create a user assessment (for tracking purposes)
   */
  async createUserAssessment(assessmentData) {
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

  // ViewSets-specific methods for enhanced functionality

  /**
   * Get trending skills
   */
  async getTrendingSkills() {
    const response = await this.makeRequest('/skills/trending/');
    return await response.json();
  }

  /**
   * Get market demand data for skills
   */
  async getSkillMarketDemand() {
    const response = await this.makeRequest('/skills/market_demand/');
    return await response.json();
  }

  /**
   * Extract skills from text (resume or job description)
   */
  async extractSkillsFromText(extractionData) {
    const response = await this.makeRequest('/skills/extract_from_text/', {
      method: 'POST',
      body: JSON.stringify(extractionData),
    });
    return await response.json();
  }

  /**
   * Get skill gap analysis for a target role
   */
  async getSkillGapAnalysis(targetRole) {
    const response = await this.makeRequest(`/user-skills/gap_analysis/?role=${encodeURIComponent(targetRole)}`);
    return await response.json();
  }

  /**
   * Get personalized skill recommendations
   */
  async getSkillRecommendations() {
    const response = await this.makeRequest('/user-skills/recommendations/');
    return await response.json();
  }

  /**
   * Get user skills analytics
   */
  async getUserSkillsAnalytics() {
    const response = await this.makeRequest('/user-skills/analytics/');
    return await response.json();
  }

  /**
   * Get popular skill categories
   */
  async getPopularSkillCategories() {
    const response = await this.makeRequest('/categories/popular/');
    return await response.json();
  }

  /**
   * Get popular certifications
   */
  async getPopularCertifications() {
    const response = await this.makeRequest('/certifications/popular/');
    return await response.json();
  }

  /**
   * Generate certification plan
   */
  async generateCertificationPlan(planData) {
    const response = await this.makeRequest('/certifications/generate_plan/', {
      method: 'POST',
      body: JSON.stringify(planData),
    });
    return await response.json();
  }

  /**
   * Get user certification progress
   */
  async getUserCertificationProgress() {
    const response = await this.makeRequest('/user-certifications/progress/');
    return await response.json();
  }

  /**
   * Get user assessment analytics
   */
  async getUserAssessmentAnalytics() {
    const response = await this.makeRequest('/user-assessments/analytics/');
    return await response.json();
  }
}

const skillsService = new SkillsService();
export default skillsService;