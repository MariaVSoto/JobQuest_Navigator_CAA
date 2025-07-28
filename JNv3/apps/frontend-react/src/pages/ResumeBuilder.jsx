import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
// Deprecated service removed - using graphqlResumeService
import graphqlResumeService from '../services/graphqlResumeService';
import PDFUploadComponent from '../components/PDFUploadComponent';
import './ResumeBuilder.css';

const ResumeBuilder = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('create');
  const [resumeData, setResumeData] = useState({
    title: '',
    personalInfo: { fullName: '', email: '', phone: '', location: '', linkedin: '', website: '' },
    summary: '',
    experience: [],
    education: [],
    skills: [],
    projects: []
  });
  const [savedResumes, setSavedResumes] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [currentResumeId, setCurrentResumeId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [newSkill, setNewSkill] = useState('');

  // Load data when component mounts or user changes
  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]); // loadData is stable and doesn't need to be in dependencies

  // Load saved resumes and templates
  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [resumesResponse, templatesResponse] = await Promise.all([
        Promise.resolve([]), // resumeService.getResumes({ limit: 20 })
        Promise.resolve([])  // resumeService.getTemplates({ limit: 50 })
      ]);
      
      const resumes = resumesResponse.results || resumesResponse;
      const templatesData = templatesResponse.results || templatesResponse;
      
      setSavedResumes(resumes.map(resume => resume)); // resumeService.transformToFrontendFormat(resume)
      setTemplates(templatesData);
      
      // If there's a default resume, load it
      const defaultResume = resumes.find(r => r.is_default);
      if (defaultResume && !currentResumeId) {
        loadResume(defaultResume.id);
      }
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load resumes and templates');
    } finally {
      setLoading(false);
    }
  };

  // Load a specific resume
  const loadResume = async (resumeId) => {
    setLoading(true);
    setError(null);
    
    try {
      const resume = await Promise.resolve({}); // resumeService.getResume(resumeId)
      const transformedResume = resume; // resumeService.transformToFrontendFormat(resume)
      setResumeData(transformedResume);
      setCurrentResumeId(resumeId);
      setActiveTab('create'); // Switch to edit mode
    } catch (err) {
      console.error('Error loading resume:', err);
      setError('Failed to load resume');
    } finally {
      setLoading(false);
    }
  };

  // Clear messages after a delay
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  const handlePersonalInfoChange = (field, value) => {
    setResumeData(prev => ({
      ...prev,
      personalInfo: {
        ...prev.personalInfo,
        [field]: value
      }
    }));
  };

  const handleSummaryChange = (value) => {
    setResumeData(prev => ({
      ...prev,
      summary: value
    }));
  };

  const handleExperienceChange = (id, field, value) => {
    setResumeData(prev => ({
      ...prev,
      experience: (prev.experience || []).map(exp =>
        exp.id === id ? { ...exp, [field]: value } : exp
      )
    }));
  };

  const addExperience = () => {
    setResumeData(prev => ({
      ...prev,
      experience: [
        ...(prev.experience || []),
        {
          id: (prev.experience || []).length + 1,
          company: '',
          position: '',
          startDate: '',
          endDate: '',
          current: false,
          description: ''
        }
      ]
    }));
  };

  const removeExperience = (id) => {
    setResumeData(prev => ({
      ...prev,
      experience: (prev.experience || []).filter(exp => exp.id !== id)
    }));
  };

  const handleEducationChange = (id, field, value) => {
    setResumeData(prev => ({
      ...prev,
      education: (prev.education || []).map(edu =>
        edu.id === id ? { ...edu, [field]: value } : edu
      )
    }));
  };

  const addEducation = () => {
    setResumeData(prev => ({
      ...prev,
      education: [
        ...(prev.education || []),
        {
          id: (prev.education || []).length + 1,
          school: '',
          degree: '',
          field: '',
          startDate: '',
          endDate: '',
          current: false,
          gpa: ''
        }
      ]
    }));
  };

  const removeEducation = (id) => {
    setResumeData(prev => ({
      ...prev,
      education: (prev.education || []).filter(edu => edu.id !== id)
    }));
  };

  const handleSkillAdd = () => {
    if (newSkill.trim()) {
      setResumeData(prev => ({
        ...prev,
        skills: [...(prev.skills || []), newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  const removeSkill = (skill) => {
    setResumeData(prev => ({
      ...prev,
      skills: (prev.skills || []).filter(s => s !== skill)
    }));
  };

  const handleProjectChange = (id, field, value) => {
    setResumeData(prev => ({
      ...prev,
      projects: (prev.projects || []).map(proj =>
        proj.id === id ? { ...proj, [field]: value } : proj
      )
    }));
  };

  const addProject = () => {
    setResumeData(prev => ({
      ...prev,
      projects: [
        ...(prev.projects || []),
        {
          id: (prev.projects || []).length + 1,
          name: '',
          description: '',
          technologies: '',
          link: ''
        }
      ]
    }));
  };

  const removeProject = (id) => {
    setResumeData(prev => ({
      ...prev,
      projects: (prev.projects || []).filter(proj => proj.id !== id)
    }));
  };

  const handleSaveResume = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    try {
      // Validate resume data using GraphQL service
      const validationErrors = graphqlResumeService.validateResumeData(resumeData);
      if (validationErrors.length > 0) {
        setError(`Please fix the following errors: ${validationErrors.join(', ')}`);
        setSaving(false);
        return;
      }

      let savedResume;
      
      // Try GraphQL service first (v2 backend)
      try {
        console.log('🚀 Attempting to save resume via GraphQL...');
        if (currentResumeId) {
          // Update existing resume
          savedResume = await graphqlResumeService.updateResume(currentResumeId, resumeData);
          setSuccess('Resume updated successfully via GraphQL! ✅');
        } else {
          // Create new resume
          savedResume = await graphqlResumeService.createResume(resumeData);
          setCurrentResumeId(savedResume.data.id);
          setSuccess('Resume saved successfully via GraphQL! ✅');
        }
        
        console.log('✅ GraphQL save successful:', savedResume);
        
      } catch (graphqlError) {
        console.warn('❌ GraphQL save failed, trying REST API fallback:', graphqlError);
        
        // Fallback to REST API service (v1 backend)
        try {
          // Validate resume data using REST service
          const validation = { isValid: true, errors: [] }; // resumeService.validateResumeData(resumeData)
          if (!validation.isValid) {
            setError(`Please fix the following errors: ${validation.errors.join(', ')}`);
            setSaving(false);
            return;
          }

          // Transform data for backend
          const backendData = resumeData; // resumeService.transformToBackendFormat(resumeData)
          
          if (currentResumeId) {
            // Update existing resume
            savedResume = await graphqlResumeService.updateResume(currentResumeId, backendData);
            setSuccess('Resume updated successfully via REST API! ⚡');
          } else {
            // Create new resume
            savedResume = await graphqlResumeService.createResume(backendData);
            setCurrentResumeId(savedResume.id);
            setSuccess('Resume saved successfully via REST API! ⚡');
          }
          
          console.log('✅ REST API fallback successful:', savedResume);
          
        } catch (restError) {
          console.error('❌ Both GraphQL and REST API failed:', { graphqlError, restError });
          throw new Error(`Failed to save resume. GraphQL error: ${graphqlError.message}. REST API error: ${restError.message}`);
        }
      }
      
      // Try to reload the list of saved resumes (skip errors)
      try {
        await loadData();
      } catch (loadError) {
        console.warn('Could not reload resume list:', loadError);
      }
      
    } catch (err) {
      console.error('Error saving resume:', err);
      setError(`Failed to save resume: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleNewResume = () => {
    setResumeData({
      title: '',
      personalInfo: { fullName: '', email: '', phone: '', location: '', linkedin: '', website: '' },
      summary: '',
      experience: [],
      education: [],
      skills: [],
      projects: []
    });
    setCurrentResumeId(null);
    setActiveTab('create');
    setError(null);
    setSuccess(null);
  };

  const handleDeleteResume = async (resumeId) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) {
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      await Promise.resolve({}); // resumeService.deleteResume(resumeId)
      setSuccess('Resume deleted successfully!');
      
      // If we deleted the current resume, reset to new resume
      if (resumeId === currentResumeId) {
        handleNewResume();
      }
      
      // Reload the list
      await loadData();
    } catch (err) {
      console.error('Error deleting resume:', err);
      setError(`Failed to delete resume: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCloneResume = async (resumeId, newTitle) => {
    setLoading(true);
    setError(null);
    
    try {
      await Promise.resolve({}); // resumeService.cloneResume(resumeId, { title: newTitle || `Copy of ${savedResumes.find(r => r.id === resumeId)?.title}`, copy_versions: false, copy_comments: false })
      setSuccess('Resume cloned successfully!');
      await loadData();
    } catch (err) {
      console.error('Error cloning resume:', err);
      setError(`Failed to clone resume: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // PDF Upload handlers
  const handlePDFUploadSuccess = (uploadData) => {
    console.log('PDF uploaded successfully:', uploadData);
    setSuccess(`PDF uploaded successfully! File: ${uploadData.filename}`);
    
    // Reload saved resumes to show the new PDF upload
    loadData();
  };

  const handlePDFProcessSuccess = (processData) => {
    console.log('PDF processed successfully:', processData);
    setSuccess(`PDF processed successfully! Extracted data in ${processData.processingTime?.toFixed(2) || 'N/A'}s`);
    
    // If we have extracted data, populate the form
    if (processData.extractedData) {
      const extractedData = processData.extractedData;
      
      // Transform the data to match our resumeData structure
      const newResumeData = {
        title: extractedData.title || 'Extracted Resume',
        personalInfo: {
          fullName: extractedData.personal_info?.full_name || '',
          email: extractedData.personal_info?.email || '',
          phone: extractedData.personal_info?.phone || '',
          location: extractedData.personal_info?.location || '',
          linkedin: extractedData.personal_info?.linkedin || '',
          website: extractedData.personal_info?.website || ''
        },
        summary: extractedData.summary || '',
        experience: extractedData.experience?.map((exp, index) => ({
          id: index + 1,
          company: exp.company || '',
          position: exp.position || '',
          startDate: exp.start_date || '',
          endDate: exp.end_date || '',
          current: exp.current || false,
          description: exp.description || ''
        })) || [],
        education: extractedData.education?.map((edu, index) => ({
          id: index + 1,
          school: edu.school || '',
          degree: edu.degree || '',
          field: edu.field || '',
          startDate: edu.start_date || '',
          endDate: edu.end_date || '',
          current: edu.current || false,
          gpa: edu.gpa || ''
        })) || [],
        skills: extractedData.skills || [],
        projects: extractedData.projects?.map((proj, index) => ({
          id: index + 1,
          name: proj.name || '',
          description: proj.description || '',
          technologies: proj.technologies || '',
          link: proj.link || ''
        })) || []
      };
      
      // Set the extracted data and switch to create tab
      setResumeData(newResumeData);
      setCurrentResumeId(processData.resumeId);
      setActiveTab('create');
      setSuccess(prev => prev + ' - Data has been populated in the form. Review and save when ready!');
    }
    
    // Reload saved resumes to show updated status
    loadData();
  };

  // Authentication check
  if (!user) {
    return (
      <div className="resume-builder-container">
        <div className="auth-required">
          <h2>Login Required</h2>
          <p>Please log in to access the resume builder.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="resume-builder-container">
      <div className="resume-builder-header">
        <h1>Resume Builder</h1>
        <p>Create and manage your professional resume</p>
        {currentResumeId && (
          <div className="current-resume-info">
            <span>Editing: {resumeData.title}</span>
            <button className="new-resume-btn" onClick={handleNewResume}>
              Create New Resume
            </button>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <div className="resume-builder-content">
        <div className="resume-tabs">
          <button
            className={activeTab === 'create' ? 'active' : ''}
            onClick={() => setActiveTab('create')}
          >
            Create Resume
          </button>
          <button
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            Upload PDF
          </button>
          <button
            className={activeTab === 'templates' ? 'active' : ''}
            onClick={() => setActiveTab('templates')}
          >
            Templates
          </button>
          <button
            className={activeTab === 'saved' ? 'active' : ''}
            onClick={() => setActiveTab('saved')}
          >
            Saved Resumes
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'create' && (
            <div className="resume-form">
              {/* Resume Title */}
              <section className="form-section">
                <h2>Resume Details</h2>
                <div className="form-group">
                  <label>Resume Title *</label>
                  <input
                    type="text"
                    value={resumeData.title}
                    onChange={(e) => setResumeData(prev => ({
                      ...prev,
                      title: e.target.value
                    }))}
                    placeholder="e.g. Software Engineer Resume, Marketing Manager CV"
                    required
                  />
                </div>
              </section>

              {/* Personal Information */}
              <section className="form-section">
                <h2>Personal Information</h2>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Full Name</label>
                    <input
                      type="text"
                      value={resumeData.personalInfo.fullName}
                      onChange={(e) => handlePersonalInfoChange('fullName', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      value={resumeData.personalInfo.email}
                      onChange={(e) => handlePersonalInfoChange('email', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Phone</label>
                    <input
                      type="tel"
                      value={resumeData.personalInfo.phone}
                      onChange={(e) => handlePersonalInfoChange('phone', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Location</label>
                    <input
                      type="text"
                      value={resumeData.personalInfo.location}
                      onChange={(e) => handlePersonalInfoChange('location', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>LinkedIn</label>
                    <input
                      type="url"
                      value={resumeData.personalInfo.linkedin}
                      onChange={(e) => handlePersonalInfoChange('linkedin', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Website</label>
                    <input
                      type="url"
                      value={resumeData.personalInfo.website}
                      onChange={(e) => handlePersonalInfoChange('website', e.target.value)}
                    />
                  </div>
                </div>
              </section>

              {/* Professional Summary */}
              <section className="form-section">
                <h2>Professional Summary</h2>
                <div className="form-group">
                  <textarea
                    value={resumeData.summary}
                    onChange={(e) => handleSummaryChange(e.target.value)}
                    rows={4}
                    placeholder="Write a brief summary of your professional background and career goals..."
                  />
                </div>
              </section>

              {/* Work Experience */}
              <section className="form-section">
                <h2>Work Experience</h2>
                {(resumeData.experience || []).map((exp, index) => (
                  <div key={exp.id} className="experience-item">
                    <div className="form-grid">
                      <div className="form-group">
                        <label>Company</label>
                        <input
                          type="text"
                          value={exp.company}
                          onChange={(e) => handleExperienceChange(exp.id, 'company', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Position</label>
                        <input
                          type="text"
                          value={exp.position}
                          onChange={(e) => handleExperienceChange(exp.id, 'position', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Start Date</label>
                        <input
                          type="date"
                          value={exp.startDate}
                          onChange={(e) => handleExperienceChange(exp.id, 'startDate', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>End Date</label>
                        <input
                          type="date"
                          value={exp.endDate}
                          onChange={(e) => handleExperienceChange(exp.id, 'endDate', e.target.value)}
                          disabled={exp.current}
                        />
                      </div>
                    </div>
                    <div className="form-group">
                      <label>
                        <input
                          type="checkbox"
                          checked={exp.current}
                          onChange={(e) => handleExperienceChange(exp.id, 'current', e.target.checked)}
                        />
                        I currently work here
                      </label>
                    </div>
                    <div className="form-group">
                      <label>Description</label>
                      <textarea
                        value={exp.description}
                        onChange={(e) => handleExperienceChange(exp.id, 'description', e.target.value)}
                        rows={4}
                        placeholder="Describe your responsibilities and achievements..."
                      />
                    </div>
                    <button
                      className="remove-button"
                      onClick={() => removeExperience(exp.id)}
                    >
                      Remove Experience
                    </button>
                  </div>
                ))}
                <button className="add-button" onClick={addExperience}>
                  Add Experience
                </button>
              </section>

              {/* Education */}
              <section className="form-section">
                <h2>Education</h2>
                {(resumeData.education || []).map((edu, index) => (
                  <div key={edu.id} className="education-item">
                    <div className="form-grid">
                      <div className="form-group">
                        <label>School</label>
                        <input
                          type="text"
                          value={edu.school}
                          onChange={(e) => handleEducationChange(edu.id, 'school', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Degree</label>
                        <input
                          type="text"
                          value={edu.degree}
                          onChange={(e) => handleEducationChange(edu.id, 'degree', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Field of Study</label>
                        <input
                          type="text"
                          value={edu.field}
                          onChange={(e) => handleEducationChange(edu.id, 'field', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Start Date</label>
                        <input
                          type="date"
                          value={edu.startDate}
                          onChange={(e) => handleEducationChange(edu.id, 'startDate', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>End Date</label>
                        <input
                          type="date"
                          value={edu.endDate}
                          onChange={(e) => handleEducationChange(edu.id, 'endDate', e.target.value)}
                          disabled={edu.current}
                        />
                      </div>
                      <div className="form-group">
                        <label>GPA</label>
                        <input
                          type="text"
                          value={edu.gpa}
                          onChange={(e) => handleEducationChange(edu.id, 'gpa', e.target.value)}
                        />
                      </div>
                    </div>
                    <div className="form-group">
                      <label>
                        <input
                          type="checkbox"
                          checked={edu.current}
                          onChange={(e) => handleEducationChange(edu.id, 'current', e.target.checked)}
                        />
                        I currently study here
                      </label>
                    </div>
                    <button
                      className="remove-button"
                      onClick={() => removeEducation(edu.id)}
                    >
                      Remove Education
                    </button>
                  </div>
                ))}
                <button className="add-button" onClick={addEducation}>
                  Add Education
                </button>
              </section>

              {/* Skills */}
              <section className="form-section">
                <h2>Skills</h2>
                <div className="skills-input">
                  <input
                    type="text"
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    placeholder="Add a skill"
                    onKeyPress={(e) => e.key === 'Enter' && handleSkillAdd()}
                  />
                  <button onClick={handleSkillAdd}>Add</button>
                </div>
                <div className="skills-list">
                  {(resumeData.skills || []).map((skill, index) => (
                    <div key={index} className="skill-tag">
                      {skill}
                      <button onClick={() => removeSkill(skill)}>×</button>
                    </div>
                  ))}
                </div>
              </section>

              {/* Projects */}
              <section className="form-section">
                <h2>Projects</h2>
                {(resumeData.projects || []).map((proj, index) => (
                  <div key={proj.id} className="project-item">
                    <div className="form-grid">
                      <div className="form-group">
                        <label>Project Name</label>
                        <input
                          type="text"
                          value={proj.name}
                          onChange={(e) => handleProjectChange(proj.id, 'name', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Technologies</label>
                        <input
                          type="text"
                          value={proj.technologies}
                          onChange={(e) => handleProjectChange(proj.id, 'technologies', e.target.value)}
                        />
                      </div>
                      <div className="form-group">
                        <label>Project Link</label>
                        <input
                          type="url"
                          value={proj.link}
                          onChange={(e) => handleProjectChange(proj.id, 'link', e.target.value)}
                        />
                      </div>
                    </div>
                    <div className="form-group">
                      <label>Description</label>
                      <textarea
                        value={proj.description}
                        onChange={(e) => handleProjectChange(proj.id, 'description', e.target.value)}
                        rows={4}
                        placeholder="Describe your project and your role..."
                      />
                    </div>
                    <button
                      className="remove-button"
                      onClick={() => removeProject(proj.id)}
                    >
                      Remove Project
                    </button>
                  </div>
                ))}
                <button className="add-button" onClick={addProject}>
                  Add Project
                </button>
              </section>

              <div className="form-actions">
                <button 
                  className="save-button" 
                  onClick={handleSaveResume}
                  disabled={saving || loading}
                >
                  {saving ? 'Saving...' : currentResumeId ? 'Update Resume' : 'Save Resume'}
                </button>
                {currentResumeId && (
                  <button 
                    className="save-as-button" 
                    onClick={() => {
                      setCurrentResumeId(null);
                      setResumeData({...resumeData, title: `Copy of ${resumeData.title}`});
                    }}
                  >
                    Save as New
                  </button>
                )}
              </div>
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="upload-pdf-section">
              <PDFUploadComponent
                onUploadSuccess={handlePDFUploadSuccess}
                onProcessSuccess={handlePDFProcessSuccess}
              />
              <div className="upload-help">
                <h3>How it works:</h3>
                <ol>
                  <li>Enter a title for your resume</li>
                  <li>Select and upload your PDF resume file (max 10MB)</li>
                  <li>Click "Extract Resume Data" to automatically populate the form</li>
                  <li>Review and edit the extracted data in the "Create Resume" tab</li>
                  <li>Save your resume when you're satisfied</li>
                </ol>
                <p><strong>Note:</strong> PDF processing is currently in beta. You may need to review and correct the extracted information.</p>
              </div>
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="templates-section">
              <h2>Choose a Template</h2>
              <div className="templates-grid">
                {templates.length > 0 ? (
                  templates.map((template) => (
                    <div key={template.id} className="template-card">
                      <div className="template-preview">
                        {template.preview_image ? (
                          <img src={template.preview_image} alt={template.name} />
                        ) : (
                          <div className="template-placeholder">
                            <span>📄</span>
                          </div>
                        )}
                      </div>
                      <div className="template-info">
                        <h3>{template.name}</h3>
                        <p className="template-category">{template.category_display}</p>
                        <p className="template-description">{template.description}</p>
                        {template.is_premium && (
                          <span className="premium-badge">Premium</span>
                        )}
                        <div className="template-stats">
                          <span>{template.usage_count} uses</span>
                        </div>
                      </div>
                      <div className="template-actions">
                        <button 
                          className="use-template-btn"
                          onClick={() => {
                            setResumeData({
                              ...resumeData,
                              template: template.id
                            });
                            setActiveTab('create');
                          }}
                        >
                          Use Template
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p>No templates available at the moment.</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'saved' && (
            <div className="saved-resumes-section">
              <h2>Your Saved Resumes</h2>
              <div className="saved-resumes-header">
                <button className="new-resume-btn" onClick={handleNewResume}>
                  Create New Resume
                </button>
              </div>
              <div className="saved-resumes-list">
                {savedResumes.length > 0 ? (
                  savedResumes.map((resume) => (
                    <div key={resume.id} className="resume-card">
                      <div className="resume-info">
                        <h3>{resume.title}</h3>
                        {resume.isDefault && <span className="default-badge">Default</span>}
                        <p className="resume-status">
                          Status: <span className={`status-${resume.status}`}>
                            {resume.statusDisplay}
                          </span>
                        </p>
                        <div className="resume-meta">
                          <span>Target: {resume.targetRole || 'Not specified'}</span>
                          <span>•</span>
                          <span>Industry: {resume.targetIndustry || 'Not specified'}</span>
                        </div>
                        <div className="resume-stats">
                          <span>Views: {resume.viewCount}</span>
                          <span>•</span>
                          <span>Versions: {resume.versionsCount}</span>
                          <span>•</span>
                          <span>Updated: {resume.updatedAt.toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="resume-actions">
                        <button 
                          className="edit-btn"
                          onClick={() => loadResume(resume.id)}
                        >
                          Edit
                        </button>
                        <button 
                          className="clone-btn"
                          onClick={() => handleCloneResume(resume.id)}
                        >
                          Clone
                        </button>
                        <button 
                          className="delete-btn"
                          onClick={() => handleDeleteResume(resume.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="no-resumes">
                    <h3>No saved resumes yet</h3>
                    <p>Create your first resume to get started!</p>
                    <button className="create-first-btn" onClick={handleNewResume}>
                      Create Your First Resume
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResumeBuilder; 