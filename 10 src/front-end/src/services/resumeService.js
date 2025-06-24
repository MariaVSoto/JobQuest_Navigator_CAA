/**
 * Resume service for Phase 2 MVP
 * Handles all API calls related to resume management
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ResumeService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/resumes`;
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
      console.error('Resume API request failed:', error);
      throw error;
    }
  }

  // Resume CRUD Operations

  /**
   * Get user's resumes with filtering
   */
  async getResumes(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific resume by ID
   */
  async getResume(resumeId) {
    const response = await this.makeRequest(`/${resumeId}/`);
    return await response.json();
  }

  /**
   * Create a new resume
   */
  async createResume(resumeData) {
    const response = await this.makeRequest('/create/', {
      method: 'POST',
      body: JSON.stringify(resumeData),
    });
    return await response.json();
  }

  /**
   * Update an existing resume
   */
  async updateResume(resumeId, resumeData) {
    const response = await this.makeRequest(`/${resumeId}/update/`, {
      method: 'PUT',
      body: JSON.stringify(resumeData),
    });
    return await response.json();
  }

  /**
   * Delete a resume
   */
  async deleteResume(resumeId) {
    await this.makeRequest(`/${resumeId}/delete/`, {
      method: 'DELETE',
    });
    return true;
  }

  /**
   * Clone a resume
   */
  async cloneResume(resumeId, cloneData) {
    const response = await this.makeRequest(`/${resumeId}/clone/`, {
      method: 'POST',
      body: JSON.stringify(cloneData),
    });
    return await response.json();
  }

  /**
   * Set resume as default
   */
  async setDefaultResume(resumeId) {
    const response = await this.makeRequest(`/${resumeId}/set-default/`, {
      method: 'POST',
    });
    return await response.json();
  }

  // Resume Templates

  /**
   * Get available resume templates
   */
  async getTemplates(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value) queryParams.append(key, value);
    });

    const endpoint = `/templates/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific template by ID
   */
  async getTemplate(templateId) {
    const response = await this.makeRequest(`/templates/${templateId}/`);
    return await response.json();
  }

  // Resume Versions

  /**
   * Get versions of a resume
   */
  async getResumeVersions(resumeId) {
    const response = await this.makeRequest(`/${resumeId}/versions/`);
    return await response.json();
  }

  /**
   * Get a specific version
   */
  async getResumeVersion(resumeId, versionId) {
    const response = await this.makeRequest(`/${resumeId}/versions/${versionId}/`);
    return await response.json();
  }

  /**
   * Restore resume to a specific version
   */
  async restoreResumeVersion(resumeId, versionId) {
    const response = await this.makeRequest(`/${resumeId}/versions/${versionId}/restore/`, {
      method: 'POST',
    });
    return await response.json();
  }

  // Resume Analytics

  /**
   * Get resume analytics
   */
  async getAnalytics() {
    const response = await this.makeRequest('/analytics/');
    return await response.json();
  }

  // Resume Skills

  /**
   * Get skill matches for a resume
   */
  async getResumeSkills(resumeId) {
    const response = await this.makeRequest(`/${resumeId}/skills/`);
    return await response.json();
  }

  // Utility Methods

  /**
   * Transform frontend resume data to backend format
   */
  transformToBackendFormat(frontendData) {
    return {
      title: frontendData.title || 'My Resume',
      full_name: frontendData.personalInfo?.fullName || '',
      email: frontendData.personalInfo?.email || '',
      phone: frontendData.personalInfo?.phone || '',
      location: frontendData.personalInfo?.location || '',
      website: frontendData.personalInfo?.website || '',
      linkedin_url: frontendData.personalInfo?.linkedin || '',
      professional_summary: frontendData.summary || '',
      target_role: frontendData.targetRole || '',
      target_industry: frontendData.targetIndustry || '',
      keywords: frontendData.keywords || '',
      resume_data: {
        personalInfo: frontendData.personalInfo || {},
        summary: frontendData.summary || '',
        experience: frontendData.experience || [],
        education: frontendData.education || [],
        skills: frontendData.skills || [],
        projects: frontendData.projects || [],
        additionalSections: frontendData.additionalSections || {}
      }
    };
  }

  /**
   * Transform backend resume data to frontend format
   */
  transformToFrontendFormat(backendData) {
    const resumeData = backendData.resume_data || {};
    return {
      id: backendData.id,
      title: backendData.title,
      personalInfo: {
        fullName: backendData.full_name || '',
        email: backendData.email || '',
        phone: backendData.phone || '',
        location: backendData.location || '',
        linkedin: backendData.linkedin_url || '',
        website: backendData.website || ''
      },
      summary: backendData.professional_summary || '',
      experience: resumeData.experience || [],
      education: resumeData.education || [],
      skills: resumeData.skills || [],
      projects: resumeData.projects || [],
      template: backendData.template,
      templateName: backendData.template_name,
      status: backendData.status,
      statusDisplay: backendData.status_display,
      isDefault: backendData.is_default,
      targetRole: backendData.target_role,
      targetIndustry: backendData.target_industry,
      keywords: backendData.keywords,
      viewCount: backendData.view_count,
      downloadCount: backendData.download_count,
      versionsCount: backendData.versions_count,
      createdAt: new Date(backendData.created_at),
      updatedAt: new Date(backendData.updated_at)
    };
  }

  /**
   * Get default resume structure for new resumes
   */
  getDefaultResumeData() {
    return {
      title: 'My Resume',
      personalInfo: {
        fullName: '',
        email: '',
        phone: '',
        location: '',
        linkedin: '',
        website: ''
      },
      summary: '',
      experience: [
        {
          id: 1,
          company: '',
          position: '',
          startDate: '',
          endDate: '',
          current: false,
          description: ''
        }
      ],
      education: [
        {
          id: 1,
          school: '',
          degree: '',
          field: '',
          startDate: '',
          endDate: '',
          current: false,
          gpa: ''
        }
      ],
      skills: [],
      projects: [
        {
          id: 1,
          name: '',
          description: '',
          technologies: '',
          link: ''
        }
      ],
      targetRole: '',
      targetIndustry: '',
      keywords: ''
    };
  }

  /**
   * Validate resume data before saving
   */
  validateResumeData(resumeData) {
    const errors = [];

    // Check required fields
    if (!resumeData.personalInfo?.fullName?.trim()) {
      errors.push('Full name is required');
    }

    if (!resumeData.personalInfo?.email?.trim()) {
      errors.push('Email is required');
    }

    // Validate email format
    if (resumeData.personalInfo?.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(resumeData.personalInfo.email)) {
        errors.push('Please enter a valid email address');
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

const resumeService = new ResumeService();
export default resumeService;