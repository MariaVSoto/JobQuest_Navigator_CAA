import React, { useState } from 'react';
import './ResumeBuilder.css';

const ResumeBuilder = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [resumeData, setResumeData] = useState({
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
    ]
  });

  const [newSkill, setNewSkill] = useState('');

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
      experience: prev.experience.map(exp =>
        exp.id === id ? { ...exp, [field]: value } : exp
      )
    }));
  };

  const addExperience = () => {
    setResumeData(prev => ({
      ...prev,
      experience: [
        ...prev.experience,
        {
          id: prev.experience.length + 1,
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
      experience: prev.experience.filter(exp => exp.id !== id)
    }));
  };

  const handleEducationChange = (id, field, value) => {
    setResumeData(prev => ({
      ...prev,
      education: prev.education.map(edu =>
        edu.id === id ? { ...edu, [field]: value } : edu
      )
    }));
  };

  const addEducation = () => {
    setResumeData(prev => ({
      ...prev,
      education: [
        ...prev.education,
        {
          id: prev.education.length + 1,
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
      education: prev.education.filter(edu => edu.id !== id)
    }));
  };

  const handleSkillAdd = () => {
    if (newSkill.trim()) {
      setResumeData(prev => ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  const removeSkill = (skill) => {
    setResumeData(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill)
    }));
  };

  const handleProjectChange = (id, field, value) => {
    setResumeData(prev => ({
      ...prev,
      projects: prev.projects.map(proj =>
        proj.id === id ? { ...proj, [field]: value } : proj
      )
    }));
  };

  const addProject = () => {
    setResumeData(prev => ({
      ...prev,
      projects: [
        ...prev.projects,
        {
          id: prev.projects.length + 1,
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
      projects: prev.projects.filter(proj => proj.id !== id)
    }));
  };

  const handleSaveResume = () => {
    // TODO: Implement resume saving functionality
    console.log('Saving resume:', resumeData);
  };

  return (
    <div className="resume-builder-container">
      <div className="resume-builder-header">
        <h1>Resume Builder</h1>
        <p>Create and manage your professional resume</p>
      </div>

      <div className="resume-builder-content">
        <div className="resume-tabs">
          <button
            className={activeTab === 'create' ? 'active' : ''}
            onClick={() => setActiveTab('create')}
          >
            Create Resume
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
                {resumeData.experience.map((exp, index) => (
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
                {resumeData.education.map((edu, index) => (
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
                  {resumeData.skills.map((skill, index) => (
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
                {resumeData.projects.map((proj, index) => (
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
                <button className="save-button" onClick={handleSaveResume}>
                  Save Resume
                </button>
              </div>
            </div>
          )}

          {activeTab === 'templates' && (
            <div className="templates-section">
              <h2>Choose a Template</h2>
              <div className="templates-grid">
                {/* Template cards will be added here */}
                <p>Template selection coming soon...</p>
              </div>
            </div>
          )}

          {activeTab === 'saved' && (
            <div className="saved-resumes-section">
              <h2>Your Saved Resumes</h2>
              <div className="saved-resumes-list">
                {/* Saved resumes will be listed here */}
                <p>No saved resumes yet.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResumeBuilder; 