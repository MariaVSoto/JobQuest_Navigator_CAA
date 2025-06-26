/**
 * Resume service for Phase 2 MVP
 * Handles all API calls related to resume management
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

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

    const endpoint = `/resumes/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific resume by ID
   */
  async getResume(resumeId) {
    const response = await this.makeRequest(`/resumes/${resumeId}/`);
    return await response.json();
  }

  /**
   * Create a new resume
   */
  async createResume(resumeData) {
    const response = await this.makeRequest('/resumes/', {
      method: 'POST',
      body: JSON.stringify(resumeData),
    });
    return await response.json();
  }

  /**
   * Update an existing resume
   */
  async updateResume(resumeId, resumeData) {
    const response = await this.makeRequest(`/resumes/${resumeId}/`, {
      method: 'PUT',
      body: JSON.stringify(resumeData),
    });
    return await response.json();
  }

  /**
   * Partially update an existing resume
   */
  async patchResume(resumeId, resumeData) {
    const response = await this.makeRequest(`/resumes/${resumeId}/`, {
      method: 'PATCH',
      body: JSON.stringify(resumeData),
    });
    return await response.json();
  }

  /**
   * Delete a resume
   */
  async deleteResume(resumeId) {
    await this.makeRequest(`/resumes/${resumeId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  /**
   * Clone a resume
   */
  async cloneResume(resumeId, cloneData = {}) {
    const response = await this.makeRequest(`/resumes/${resumeId}/clone/`, {
      method: 'POST',
      body: JSON.stringify(cloneData),
    });
    return await response.json();
  }

  /**
   * Set resume as default
   */
  async setDefaultResume(resumeId) {
    const response = await this.makeRequest(`/resumes/${resumeId}/set_default/`, {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Get user's default resume
   */
  async getDefaultResume() {
    const response = await this.makeRequest('/resumes/default/');
    return await response.json();
  }

  /**
   * Get resume analytics
   */
  async getResumeAnalytics() {
    const response = await this.makeRequest('/resumes/analytics/');
    return await response.json();
  }

  /**
   * Duplicate resume for specific job
   */
  async duplicateForJob(resumeId, jobData) {
    const response = await this.makeRequest(`/resumes/${resumeId}/duplicate_for_job/`, {
      method: 'POST',
      body: JSON.stringify(jobData),
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

    const endpoint = `/resume-templates/${queryParams.toString() ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest(endpoint);
    return await response.json();
  }

  /**
   * Get a specific template by ID
   */
  async getTemplate(templateId) {
    const response = await this.makeRequest(`/resume-templates/${templateId}/`);
    return await response.json();
  }

  /**
   * Track template usage
   */
  async useTemplate(templateId) {
    const response = await this.makeRequest(`/resume-templates/${templateId}/use_template/`, {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Get popular templates
   */
  async getPopularTemplates() {
    const response = await this.makeRequest('/resume-templates/popular/');
    return await response.json();
  }

  /**
   * Get templates by category
   */
  async getTemplatesByCategory() {
    const response = await this.makeRequest('/resume-templates/by_category/');
    return await response.json();
  }

  // Resume Versions

  /**
   * Get versions of a resume
   */
  async getResumeVersions(resumeId) {
    const response = await this.makeRequest(`/resume-versions/by_resume/?resume_id=${resumeId}`);
    return await response.json();
  }

  /**
   * Get a specific version
   */
  async getResumeVersion(versionId) {
    const response = await this.makeRequest(`/resume-versions/${versionId}/`);
    return await response.json();
  }

  /**
   * Create a new version
   */
  async createResumeVersion(versionData) {
    const response = await this.makeRequest('/resume-versions/', {
      method: 'POST',
      body: JSON.stringify(versionData),
    });
    return await response.json();
  }

  /**
   * Update a version
   */
  async updateResumeVersion(versionId, versionData) {
    const response = await this.makeRequest(`/resume-versions/${versionId}/`, {
      method: 'PUT',
      body: JSON.stringify(versionData),
    });
    return await response.json();
  }

  /**
   * Delete a version
   */
  async deleteResumeVersion(versionId) {
    await this.makeRequest(`/resume-versions/${versionId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  /**
   * Restore resume to a specific version
   */
  async restoreResumeVersion(versionId) {
    const response = await this.makeRequest(`/resume-versions/${versionId}/restore/`, {
      method: 'POST',
    });
    return await response.json();
  }

  /**
   * Compare two versions
   */
  async compareVersions(version1Id, version2Id) {
    const response = await this.makeRequest('/resume-versions/compare/', {
      method: 'POST',
      body: JSON.stringify({
        version1_id: version1Id,
        version2_id: version2Id,
      }),
    });
    return await response.json();
  }

  // Resume Sharing

  /**
   * Get shares for a resume
   */
  async getResumeShares(resumeId) {
    const response = await this.makeRequest(`/resume-shares/by_resume/?resume_id=${resumeId}`);
    return await response.json();
  }

  /**
   * Create a new share
   */
  async shareResume(shareData) {
    const response = await this.makeRequest('/resume-shares/', {
      method: 'POST',
      body: JSON.stringify(shareData),
    });
    return await response.json();
  }

  /**
   * Update a share
   */
  async updateResumeShare(shareId, shareData) {
    const response = await this.makeRequest(`/resume-shares/${shareId}/`, {
      method: 'PUT',
      body: JSON.stringify(shareData),
    });
    return await response.json();
  }

  /**
   * Delete a share
   */
  async deleteResumeShare(shareId) {
    await this.makeRequest(`/resume-shares/${shareId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  /**
   * Revoke share access
   */
  async revokeResumeShare(shareId) {
    const response = await this.makeRequest(`/resume-shares/${shareId}/revoke/`, {
      method: 'POST',
    });
    return await response.json();
  }

  // Resume Comments

  /**
   * Get comments for a resume
   */
  async getResumeComments(resumeId) {
    const response = await this.makeRequest(`/resume-comments/by_resume/?resume_id=${resumeId}`);
    return await response.json();
  }

  /**
   * Create a new comment
   */
  async createResumeComment(commentData) {
    const response = await this.makeRequest('/resume-comments/', {
      method: 'POST',
      body: JSON.stringify(commentData),
    });
    return await response.json();
  }

  /**
   * Update a comment
   */
  async updateResumeComment(commentId, commentData) {
    const response = await this.makeRequest(`/resume-comments/${commentId}/`, {
      method: 'PUT',
      body: JSON.stringify(commentData),
    });
    return await response.json();
  }

  /**
   * Delete a comment
   */
  async deleteResumeComment(commentId) {
    await this.makeRequest(`/resume-comments/${commentId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  /**
   * Resolve a comment
   */
  async resolveResumeComment(commentId) {
    const response = await this.makeRequest(`/resume-comments/${commentId}/resolve/`, {
      method: 'POST',
    });
    return await response.json();
  }

  // Resume Exports

  /**
   * Get exports for a resume
   */
  async getResumeExports(resumeId) {
    const response = await this.makeRequest(`/resume-exports/by_resume/?resume_id=${resumeId}`);
    return await response.json();
  }

  /**
   * Generate a new export
   */
  async generateResumeExport(exportData) {
    const response = await this.makeRequest('/resume-exports/generate/', {
      method: 'POST',
      body: JSON.stringify(exportData),
    });
    return await response.json();
  }

  /**
   * Download an export
   */
  async downloadResumeExport(exportId) {
    const response = await this.makeRequest(`/resume-exports/${exportId}/download/`);
    return await response.json();
  }

  /**
   * Delete an export
   */
  async deleteResumeExport(exportId) {
    await this.makeRequest(`/resume-exports/${exportId}/`, {
      method: 'DELETE',
    });
    return true;
  }

  // Utility Methods for Data Transformation

  /**
   * Get all user resumes with skill matches
   */
  async getResumesWithSkills() {
    const resumes = await this.getResumes();
    return resumes;
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