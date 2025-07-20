import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import skillsService from '../services/skillsService';
import './SkillsAndCertifications.css';

const SkillsAndCertifications = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('skills');
  
  // Skills state
  const [userSkills, setUserSkills] = useState([]);
  const [availableSkills, setAvailableSkills] = useState([]);
  const [skillCategories, setSkillCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [skillSearchQuery, setSkillSearchQuery] = useState('');
  
  // Certifications state
  const [userCertifications, setUserCertifications] = useState([]);
  const [availableCertifications, setAvailableCertifications] = useState([]);
  const [certificationSearchQuery, setCertificationSearchQuery] = useState('');
  
  // Learning paths state
  const [userLearningPaths, setUserLearningPaths] = useState([]);
  const [availableLearningPaths, setAvailableLearningPaths] = useState([]);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showAddSkillModal, setShowAddSkillModal] = useState(false);
  const [showAddCertificationModal, setShowAddCertificationModal] = useState(false);
  const [editingSkill, setEditingSkill] = useState(null);
  const [editingCertification, setEditingCertification] = useState(null);

  // Load data on component mount
  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  // Clear messages after delay
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [
        userSkillsResponse,
        userCertificationsResponse,
        userLearningPathsResponse,
        skillCategoriesResponse,
        availableSkillsResponse,
        availableCertificationsResponse,
        availableLearningPathsResponse
      ] = await Promise.all([
        skillsService.getUserSkills({ limit: 50 }),
        skillsService.getUserCertifications({ limit: 50 }),
        skillsService.getUserLearningPaths({ limit: 20 }),
        skillsService.getSkillCategories({ limit: 50 }),
        skillsService.getSkills({ limit: 100, ordering: 'popularity_score' }),
        skillsService.getCertifications({ limit: 100, ordering: 'popularity_score' }),
        skillsService.getLearningPaths({ limit: 50, is_featured: true })
      ]);
      
      setUserSkills(userSkillsResponse.results || userSkillsResponse);
      setUserCertifications(userCertificationsResponse.results || userCertificationsResponse);
      setUserLearningPaths(userLearningPathsResponse.results || userLearningPathsResponse);
      setSkillCategories(skillCategoriesResponse.results || skillCategoriesResponse);
      setAvailableSkills(availableSkillsResponse.results || availableSkillsResponse);
      setAvailableCertifications(availableCertificationsResponse.results || availableCertificationsResponse);
      setAvailableLearningPaths(availableLearningPathsResponse.results || availableLearningPathsResponse);
      
    } catch (err) {
      console.error('Error loading skills data:', err);
      setError('Failed to load skills and certifications data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSkill = async (skillData) => {
    try {
      const newUserSkill = await skillsService.addUserSkill(skillData);
      setUserSkills(prev => [...prev, newUserSkill]);
      setShowAddSkillModal(false);
      setSuccess('Skill added successfully!');
    } catch (err) {
      console.error('Error adding skill:', err);
      setError(`Failed to add skill: ${err.message}`);
    }
  };

  const handleUpdateSkill = async (userSkillId, skillData) => {
    try {
      const updatedUserSkill = await skillsService.updateUserSkill(userSkillId, skillData);
      setUserSkills(prev => prev.map(skill => 
        skill.id === userSkillId ? updatedUserSkill : skill
      ));
      setEditingSkill(null);
      setSuccess('Skill updated successfully!');
    } catch (err) {
      console.error('Error updating skill:', err);
      setError(`Failed to update skill: ${err.message}`);
    }
  };

  const handleRemoveSkill = async (userSkillId) => {
    if (!window.confirm('Are you sure you want to remove this skill?')) {
      return;
    }

    try {
      await skillsService.removeUserSkill(userSkillId);
      setUserSkills(prev => prev.filter(skill => skill.id !== userSkillId));
      setSuccess('Skill removed successfully!');
    } catch (err) {
      console.error('Error removing skill:', err);
      setError(`Failed to remove skill: ${err.message}`);
    }
  };

  const handleAddCertification = async (certificationData) => {
    try {
      const newUserCertification = await skillsService.addUserCertification(certificationData);
      setUserCertifications(prev => [...prev, newUserCertification]);
      setShowAddCertificationModal(false);
      setSuccess('Certification added successfully!');
    } catch (err) {
      console.error('Error adding certification:', err);
      setError(`Failed to add certification: ${err.message}`);
    }
  };

  const handleUpdateCertification = async (userCertificationId, certificationData) => {
    try {
      const updatedUserCertification = await skillsService.updateUserCertification(userCertificationId, certificationData);
      setUserCertifications(prev => prev.map(cert => 
        cert.id === userCertificationId ? updatedUserCertification : cert
      ));
      setEditingCertification(null);
      setSuccess('Certification updated successfully!');
    } catch (err) {
      console.error('Error updating certification:', err);
      setError(`Failed to update certification: ${err.message}`);
    }
  };

  const handleRemoveCertification = async (userCertificationId) => {
    if (!window.confirm('Are you sure you want to remove this certification?')) {
      return;
    }

    try {
      await skillsService.removeUserCertification(userCertificationId);
      setUserCertifications(prev => prev.filter(cert => cert.id !== userCertificationId));
      setSuccess('Certification removed successfully!');
    } catch (err) {
      console.error('Error removing certification:', err);
      setError(`Failed to remove certification: ${err.message}`);
    }
  };

  const handleEnrollInLearningPath = async (learningPathId) => {
    try {
      const enrollment = await skillsService.enrollInLearningPath({ learning_path: learningPathId, status: 'not_started' });
      setUserLearningPaths(prev => [...prev, enrollment]);
      setSuccess('Enrolled in learning path successfully!');
    } catch (err) {
      console.error('Error enrolling in learning path:', err);
      setError(`Failed to enroll in learning path: ${err.message}`);
    }
  };

  const filteredSkills = availableSkills.filter(skill => {
    const matchesSearch = !skillSearchQuery || 
      skill.name.toLowerCase().includes(skillSearchQuery.toLowerCase()) ||
      skill.description.toLowerCase().includes(skillSearchQuery.toLowerCase());
    
    const matchesCategory = !selectedCategory || skill.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const filteredCertifications = availableCertifications.filter(cert => {
    return !certificationSearchQuery || 
      cert.name.toLowerCase().includes(certificationSearchQuery.toLowerCase()) ||
      cert.issuing_organization.toLowerCase().includes(certificationSearchQuery.toLowerCase()) ||
      cert.description.toLowerCase().includes(certificationSearchQuery.toLowerCase());
  });

  // Authentication check
  if (!user) {
    return (
      <div className="skills-certifications-container">
        <div className="auth-required">
          <h2>Login Required</h2>
          <p>Please log in to access your skills and certifications.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="skills-certifications-container">
      <div className="skills-certifications-header">
        <h1>Skills & Certifications</h1>
        <p>Manage your professional skills and track your certifications</p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading skills and certifications...</p>
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

      {/* Navigation Tabs */}
      <div className="skills-tabs">
        <button
          className={activeTab === 'skills' ? 'active' : ''}
          onClick={() => setActiveTab('skills')}
        >
          My Skills ({userSkills.length})
        </button>
        <button
          className={activeTab === 'certifications' ? 'active' : ''}
          onClick={() => setActiveTab('certifications')}
        >
          My Certifications ({userCertifications.length})
        </button>
        <button
          className={activeTab === 'learning-paths' ? 'active' : ''}
          onClick={() => setActiveTab('learning-paths')}
        >
          Learning Paths ({userLearningPaths.length})
        </button>
        <button
          className={activeTab === 'explore' ? 'active' : ''}
          onClick={() => setActiveTab('explore')}
        >
          Explore Skills
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* My Skills Tab */}
        {activeTab === 'skills' && (
          <div className="skills-section">
            <div className="section-header">
              <h2>My Skills</h2>
              <button 
                className="add-btn"
                onClick={() => setShowAddSkillModal(true)}
              >
                Add Skill
              </button>
            </div>

            <div className="skills-grid">
              {userSkills.length > 0 ? (
                userSkills.map((userSkill) => (
                  <div key={userSkill.id} className="skill-card">
                    <div className="skill-header">
                      <h3>{userSkill.skill?.name || userSkill.skill_name}</h3>
                      <div className="skill-actions">
                        <button 
                          className="edit-btn"
                          onClick={() => setEditingSkill(userSkill)}
                        >
                          Edit
                        </button>
                        <button 
                          className="remove-btn"
                          onClick={() => handleRemoveSkill(userSkill.id)}
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                    
                    <div className="skill-details">
                      <div className="proficiency">
                        <span 
                          className={`proficiency-badge proficiency-${userSkill.proficiency_level}`}
                          style={{ backgroundColor: skillsService.getProficiencyColor(userSkill.proficiency_level) }}
                        >
                          {skillsService.getProficiencyDisplay(userSkill.proficiency_level)}
                        </span>
                      </div>
                      
                      {userSkill.years_experience > 0 && (
                        <div className="experience">
                          <span>📅 {userSkill.years_experience} years experience</span>
                        </div>
                      )}
                      
                      {userSkill.is_verified && (
                        <div className="verified">
                          <span>✓ Verified</span>
                        </div>
                      )}
                      
                      {userSkill.last_used && (
                        <div className="last-used">
                          <span>Last used: {new Date(userSkill.last_used).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-items">
                  <h3>No skills added yet</h3>
                  <p>Add your first skill to get started with your professional profile.</p>
                  <button 
                    className="add-first-btn"
                    onClick={() => setShowAddSkillModal(true)}
                  >
                    Add Your First Skill
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* My Certifications Tab */}
        {activeTab === 'certifications' && (
          <div className="certifications-section">
            <div className="section-header">
              <h2>My Certifications</h2>
              <button 
                className="add-btn"
                onClick={() => setShowAddCertificationModal(true)}
              >
                Add Certification
              </button>
            </div>

            <div className="certifications-grid">
              {userCertifications.length > 0 ? (
                userCertifications.map((userCertification) => (
                  <div key={userCertification.id} className="certification-card">
                    <div className="certification-header">
                      <h3>{userCertification.certification?.name}</h3>
                      <div className="certification-actions">
                        <button 
                          className="edit-btn"
                          onClick={() => setEditingCertification(userCertification)}
                        >
                          Edit
                        </button>
                        <button 
                          className="remove-btn"
                          onClick={() => handleRemoveCertification(userCertification.id)}
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                    
                    <div className="certification-details">
                      <div className="issuer">
                        <span>🏢 {userCertification.certification?.issuing_organization}</span>
                      </div>
                      
                      <div className="status">
                        <span 
                          className={`status-badge status-${userCertification.status}`}
                          style={{ backgroundColor: skillsService.getCertificationStatusColor(userCertification.status) }}
                        >
                          {skillsService.getCertificationStatusDisplay(userCertification.status)}
                        </span>
                      </div>
                      
                      {userCertification.earned_date && (
                        <div className="earned-date">
                          <span>📅 Earned: {new Date(userCertification.earned_date).toLocaleDateString()}</span>
                        </div>
                      )}
                      
                      {userCertification.expiry_date && (
                        <div className="expiry-date">
                          <span>⏰ Expires: {new Date(userCertification.expiry_date).toLocaleDateString()}</span>
                        </div>
                      )}
                      
                      {userCertification.credential_id && (
                        <div className="credential-id">
                          <span>🆔 ID: {userCertification.credential_id}</span>
                        </div>
                      )}
                      
                      {userCertification.is_verified && (
                        <div className="verified">
                          <span>✓ Verified</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-items">
                  <h3>No certifications added yet</h3>
                  <p>Add your professional certifications to showcase your expertise.</p>
                  <button 
                    className="add-first-btn"
                    onClick={() => setShowAddCertificationModal(true)}
                  >
                    Add Your First Certification
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Learning Paths Tab */}
        {activeTab === 'learning-paths' && (
          <div className="learning-paths-section">
            <div className="section-header">
              <h2>My Learning Paths</h2>
            </div>

            <div className="learning-paths-grid">
              {userLearningPaths.length > 0 ? (
                userLearningPaths.map((userLearningPath) => (
                  <div key={userLearningPath.id} className="learning-path-card">
                    <div className="learning-path-header">
                      <h3>{userLearningPath.learning_path?.name}</h3>
                      <div className="progress-circle">
                        <span>{userLearningPath.progress_percentage || 0}%</span>
                      </div>
                    </div>
                    
                    <div className="learning-path-details">
                      <div className="status">
                        <span 
                          className={`status-badge status-${userLearningPath.status}`}
                          style={{ backgroundColor: skillsService.getLearningPathStatusColor(userLearningPath.status) }}
                        >
                          {userLearningPath.status?.replace('_', ' ')}
                        </span>
                      </div>
                      
                      {userLearningPath.started_date && (
                        <div className="started-date">
                          <span>📅 Started: {new Date(userLearningPath.started_date).toLocaleDateString()}</span>
                        </div>
                      )}
                      
                      {userLearningPath.target_completion_date && (
                        <div className="target-date">
                          <span>🎯 Target: {new Date(userLearningPath.target_completion_date).toLocaleDateString()}</span>
                        </div>
                      )}
                      
                      <div className="study-hours">
                        <span>⏱️ {userLearningPath.total_study_hours || 0} hours studied</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-items">
                  <h3>No learning paths enrolled</h3>
                  <p>Explore our curated learning paths to advance your career.</p>
                  <button 
                    className="explore-btn"
                    onClick={() => setActiveTab('explore')}
                  >
                    Explore Learning Paths
                  </button>
                </div>
              )}
            </div>

            {/* Available Learning Paths */}
            {availableLearningPaths.length > 0 && (
              <div className="available-learning-paths">
                <h3>Featured Learning Paths</h3>
                <div className="learning-paths-grid">
                  {availableLearningPaths
                    .filter(path => !userLearningPaths.some(userPath => 
                      userPath.learning_path?.id === path.id
                    ))
                    .slice(0, 6)
                    .map((learningPath) => (
                      <div key={learningPath.id} className="learning-path-card available">
                        <div className="learning-path-header">
                          <h3>{learningPath.name}</h3>
                          <button 
                            className="enroll-btn"
                            onClick={() => handleEnrollInLearningPath(learningPath.id)}
                          >
                            Enroll
                          </button>
                        </div>
                        
                        <div className="learning-path-details">
                          <p className="description">{learningPath.description}</p>
                          
                          <div className="duration">
                            <span>⏱️ {learningPath.estimated_duration_weeks} weeks</span>
                          </div>
                          
                          <div className="difficulty">
                            <span 
                              className={`difficulty-badge difficulty-${learningPath.difficulty_level}`}
                            >
                              {skillsService.getProficiencyDisplay(learningPath.difficulty_level)}
                            </span>
                          </div>
                          
                          {learningPath.target_role && (
                            <div className="target-role">
                              <span>🎯 Target: {learningPath.target_role}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Explore Skills Tab */}
        {activeTab === 'explore' && (
          <div className="explore-section">
            <div className="section-header">
              <h2>Explore Skills</h2>
            </div>

            {/* Search and Filters */}
            <div className="explore-filters">
              <div className="search-bar">
                <input
                  type="text"
                  placeholder="Search skills..."
                  value={skillSearchQuery}
                  onChange={(e) => setSkillSearchQuery(e.target.value)}
                />
              </div>
              
              <div className="category-filter">
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="">All Categories</option>
                  {skillCategories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Skills Grid */}
            <div className="explore-skills-grid">
              {filteredSkills.map((skill) => (
                <div key={skill.id} className="explore-skill-card">
                  <div className="skill-info">
                    <h3>{skill.name}</h3>
                    {skill.description && (
                      <p className="description">{skill.description}</p>
                    )}
                    
                    <div className="skill-meta">
                      <div className="market-demand">
                        <span 
                          className="demand-badge"
                          style={{ backgroundColor: skillsService.getMarketDemandColor(skill.market_demand) }}
                        >
                          {skillsService.getMarketDemandDisplay(skill.market_demand)} Demand
                        </span>
                      </div>
                      
                      {skill.average_salary && (
                        <div className="salary">
                          <span>💰 Avg: {skillsService.formatSalary(skill.average_salary)}</span>
                        </div>
                      )}
                      
                      {skill.is_trending && (
                        <div className="trending">
                          <span>🔥 Trending</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="skill-actions">
                    <button 
                      className="add-skill-btn"
                      onClick={() => {
                        setEditingSkill({
                          skill: skill.id,
                          skill_name: skill.name,
                          proficiency_level: 'beginner',
                          years_experience: 0
                        });
                        setShowAddSkillModal(true);
                      }}
                      disabled={userSkills.some(userSkill => 
                        userSkill.skill?.id === skill.id || userSkill.skill_name === skill.name
                      )}
                    >
                      {userSkills.some(userSkill => 
                        userSkill.skill?.id === skill.id || userSkill.skill_name === skill.name
                      ) ? 'Already Added' : 'Add to Profile'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Add Skill Modal */}
      {showAddSkillModal && (
        <SkillModal
          skill={editingSkill}
          availableSkills={availableSkills}
          onSave={editingSkill?.id ? 
            (data) => handleUpdateSkill(editingSkill.id, data) : 
            handleAddSkill
          }
          onClose={() => {
            setShowAddSkillModal(false);
            setEditingSkill(null);
          }}
        />
      )}

      {/* Add Certification Modal */}
      {showAddCertificationModal && (
        <CertificationModal
          certification={editingCertification}
          availableCertifications={availableCertifications}
          onSave={editingCertification?.id ? 
            (data) => handleUpdateCertification(editingCertification.id, data) : 
            handleAddCertification
          }
          onClose={() => {
            setShowAddCertificationModal(false);
            setEditingCertification(null);
          }}
        />
      )}
    </div>
  );
};

// Skill Modal Component
const SkillModal = ({ skill, availableSkills, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    skill: skill?.skill || '',
    skill_name: skill?.skill_name || '',
    proficiency_level: skill?.proficiency_level || 'beginner',
    years_experience: skill?.years_experience || 0,
    self_assessed_level: skill?.self_assessed_level || 'beginner',
    target_proficiency: skill?.target_proficiency || 'advanced',
    frequency_of_use: skill?.frequency_of_use || 'occasionally',
    evidence_url: skill?.evidence_url || '',
    last_used: skill?.last_used || ''
  });

  const [errors, setErrors] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const validation = skillsService.validateSkillData(formData);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    onSave(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>{skill?.id ? 'Edit Skill' : 'Add Skill'}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          {errors.length > 0 && (
            <div className="error-message">
              {errors.join(', ')}
            </div>
          )}
          
          <div className="form-group">
            <label>Skill *</label>
            {skill?.skill ? (
              <input
                type="text"
                value={formData.skill_name}
                disabled
              />
            ) : (
              <select
                value={formData.skill}
                onChange={(e) => {
                  const selectedSkill = availableSkills.find(s => s.id === e.target.value);
                  setFormData(prev => ({
                    ...prev,
                    skill: e.target.value,
                    skill_name: selectedSkill?.name || ''
                  }));
                }}
                required
              >
                <option value="">Select a skill</option>
                {availableSkills.map((availableSkill) => (
                  <option key={availableSkill.id} value={availableSkill.id}>
                    {availableSkill.name}
                  </option>
                ))}
              </select>
            )}
          </div>
          
          <div className="form-group">
            <label>Proficiency Level *</label>
            <select
              value={formData.proficiency_level}
              onChange={(e) => setFormData(prev => ({ ...prev, proficiency_level: e.target.value }))}
              required
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Years of Experience</label>
            <input
              type="number"
              min="0"
              value={formData.years_experience}
              onChange={(e) => setFormData(prev => ({ ...prev, years_experience: parseInt(e.target.value) || 0 }))}
            />
          </div>
          
          <div className="form-group">
            <label>Target Proficiency</label>
            <select
              value={formData.target_proficiency}
              onChange={(e) => setFormData(prev => ({ ...prev, target_proficiency: e.target.value }))}
            >
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Frequency of Use</label>
            <select
              value={formData.frequency_of_use}
              onChange={(e) => setFormData(prev => ({ ...prev, frequency_of_use: e.target.value }))}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="occasionally">Occasionally</option>
              <option value="rarely">Rarely</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Evidence URL</label>
            <input
              type="url"
              value={formData.evidence_url}
              onChange={(e) => setFormData(prev => ({ ...prev, evidence_url: e.target.value }))}
              placeholder="Link to portfolio, certification, etc."
            />
          </div>
          
          <div className="form-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="save-btn">
              {skill?.id ? 'Update' : 'Add'} Skill
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Certification Modal Component
const CertificationModal = ({ certification, availableCertifications, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    certification: certification?.certification?.id || '',
    status: certification?.status || 'planned',
    earned_date: certification?.earned_date || '',
    expiry_date: certification?.expiry_date || '',
    credential_id: certification?.credential_id || '',
    credential_url: certification?.credential_url || '',
    target_completion_date: certification?.target_completion_date || '',
    study_progress: certification?.study_progress || 0,
    notes: certification?.notes || ''
  });

  const [errors, setErrors] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const validation = skillsService.validateCertificationData(formData);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    onSave(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>{certification?.id ? 'Edit Certification' : 'Add Certification'}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          {errors.length > 0 && (
            <div className="error-message">
              {errors.join(', ')}
            </div>
          )}
          
          <div className="form-group">
            <label>Certification *</label>
            <select
              value={formData.certification}
              onChange={(e) => setFormData(prev => ({ ...prev, certification: e.target.value }))}
              required
            >
              <option value="">Select a certification</option>
              {availableCertifications.map((cert) => (
                <option key={cert.id} value={cert.id}>
                  {cert.name} ({cert.issuing_organization})
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Status *</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
              required
            >
              <option value="planned">Planned</option>
              <option value="in_progress">In Progress</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
            </select>
          </div>
          
          {(formData.status === 'active' || formData.status === 'expired') && (
            <div className="form-group">
              <label>Earned Date</label>
              <input
                type="date"
                value={formData.earned_date}
                onChange={(e) => setFormData(prev => ({ ...prev, earned_date: e.target.value }))}
              />
            </div>
          )}
          
          {(formData.status === 'active' || formData.status === 'expired') && (
            <div className="form-group">
              <label>Expiry Date</label>
              <input
                type="date"
                value={formData.expiry_date}
                onChange={(e) => setFormData(prev => ({ ...prev, expiry_date: e.target.value }))}
              />
            </div>
          )}
          
          {formData.status === 'in_progress' && (
            <div className="form-group">
              <label>Target Completion Date</label>
              <input
                type="date"
                value={formData.target_completion_date}
                onChange={(e) => setFormData(prev => ({ ...prev, target_completion_date: e.target.value }))}
              />
            </div>
          )}
          
          {formData.status === 'in_progress' && (
            <div className="form-group">
              <label>Study Progress (%)</label>
              <input
                type="range"
                min="0"
                max="100"
                value={formData.study_progress}
                onChange={(e) => setFormData(prev => ({ ...prev, study_progress: parseInt(e.target.value) }))}
              />
              <span>{formData.study_progress}%</span>
            </div>
          )}
          
          <div className="form-group">
            <label>Credential ID</label>
            <input
              type="text"
              value={formData.credential_id}
              onChange={(e) => setFormData(prev => ({ ...prev, credential_id: e.target.value }))}
              placeholder="Certificate ID or license number"
            />
          </div>
          
          <div className="form-group">
            <label>Credential URL</label>
            <input
              type="url"
              value={formData.credential_url}
              onChange={(e) => setFormData(prev => ({ ...prev, credential_url: e.target.value }))}
              placeholder="Link to verify certification"
            />
          </div>
          
          <div className="form-group">
            <label>Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              placeholder="Additional notes about this certification"
              rows="3"
            />
          </div>
          
          <div className="form-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="save-btn">
              {certification?.id ? 'Update' : 'Add'} Certification
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SkillsAndCertifications;