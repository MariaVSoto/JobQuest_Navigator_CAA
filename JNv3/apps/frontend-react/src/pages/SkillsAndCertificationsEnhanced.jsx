import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import skillsService from '../services/skillsService';
import SkillCard from '../components/skills/SkillCard';
import CertificationCard from '../components/skills/CertificationCard';
import SkillsAnalytics from '../components/skills/SkillsAnalytics';
import './SkillsAndCertificationsEnhanced.css';

const SkillsAndCertificationsEnhanced = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  
  // Data state
  const [userSkills, setUserSkills] = useState([]);
  const [availableSkills, setAvailableSkills] = useState([]);
  const [skillCategories, setSkillCategories] = useState([]);
  const [userCertifications, setUserCertifications] = useState([]);
  const [availableCertifications, setAvailableCertifications] = useState([]);
  const [userLearningPaths, setUserLearningPaths] = useState([]);
  const [availableLearningPaths, setAvailableLearningPaths] = useState([]);
  
  // Filter state
  const [selectedCategory, setSelectedCategory] = useState('');
  const [skillSearchQuery, setSkillSearchQuery] = useState('');
  const [certificationSearchQuery, setCertificationSearchQuery] = useState('');
  const [proficiencyFilter, setProficiencyFilter] = useState('');
  
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

  // Skills handlers
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

  // Certification handlers
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

  // Filter functions
  const getFilteredSkills = () => {
    return userSkills.filter(skill => {
      const matchesSearch = !skillSearchQuery || 
        (skill.skill?.name || skill.skill_name).toLowerCase().includes(skillSearchQuery.toLowerCase());
      
      const matchesCategory = !selectedCategory || skill.skill?.category === selectedCategory;
      const matchesProficiency = !proficiencyFilter || skill.proficiency_level === proficiencyFilter;
      
      return matchesSearch && matchesCategory && matchesProficiency;
    });
  };

  const getFilteredCertifications = () => {
    return userCertifications.filter(cert => {
      return !certificationSearchQuery || 
        cert.certification?.name.toLowerCase().includes(certificationSearchQuery.toLowerCase()) ||
        cert.certification?.issuing_organization.toLowerCase().includes(certificationSearchQuery.toLowerCase());
    });
  };

  // Tab configuration
  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'skills', label: `Skills (${userSkills.length})`, icon: '🛠️' },
    { id: 'certifications', label: `Certifications (${userCertifications.length})`, icon: '🏆' },
    { id: 'learning-paths', label: `Learning (${userLearningPaths.length})`, icon: '📚' },
    { id: 'explore', label: 'Explore', icon: '🔍' }
  ];

  // Authentication check
  if (!user) {
    return (
      <div className="skills-certifications-enhanced">
        <div className="auth-required">
          <div className="auth-icon">🔐</div>
          <h2>Login Required</h2>
          <p>Please log in to access your skills and certifications.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="skills-certifications-enhanced">
      {/* Header */}
      <div className="page-header">
        <div className="header-content">
          <h1>Skills & Certifications</h1>
          <p>Manage your professional skills, track certifications, and accelerate your career growth</p>
        </div>
        
        <div className="header-stats">
          <div className="stat-item">
            <div className="stat-value">{userSkills.length}</div>
            <div className="stat-label">Skills</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{userCertifications.length}</div>
            <div className="stat-label">Certifications</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{userLearningPaths.length}</div>
            <div className="stat-label">Learning Paths</div>
          </div>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="message error-message">
          <span className="message-icon">⚠️</span>
          {error}
        </div>
      )}

      {success && (
        <div className="message success-message">
          <span className="message-icon">✅</span>
          {success}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Loading your skills data...</p>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="enhanced-tabs">
        <div className="tabs-container">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="tab-content-enhanced">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-section">
            <SkillsAnalytics 
              userSkills={userSkills} 
              userCertifications={userCertifications} 
            />
            
            <div className="overview-grid">
              {/* Recent Skills */}
              <div className="overview-card">
                <div className="card-header">
                  <h3>Recent Skills</h3>
                  <button 
                    className="view-all-btn"
                    onClick={() => setActiveTab('skills')}
                  >
                    View All
                  </button>
                </div>
                <div className="recent-items">
                  {userSkills.slice(0, 3).map(skill => (
                    <div key={skill.id} className="recent-item">
                      <div className="item-info">
                        <h4>{skill.skill?.name || skill.skill_name}</h4>
                        <span className="proficiency">
                          {skill.proficiency_level}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Certifications */}
              <div className="overview-card">
                <div className="card-header">
                  <h3>Active Certifications</h3>
                  <button 
                    className="view-all-btn"
                    onClick={() => setActiveTab('certifications')}
                  >
                    View All
                  </button>
                </div>
                <div className="recent-items">
                  {userCertifications
                    .filter(cert => cert.status === 'active')
                    .slice(0, 3)
                    .map(cert => (
                      <div key={cert.id} className="recent-item">
                        <div className="item-info">
                          <h4>{cert.certification?.name}</h4>
                          <span className="issuer">
                            {cert.certification?.issuing_organization}
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Skills Tab */}
        {activeTab === 'skills' && (
          <div className="skills-section">
            <div className="section-header">
              <h2>My Skills</h2>
              <button 
                className="add-btn primary"
                onClick={() => setShowAddSkillModal(true)}
              >
                <span className="btn-icon">➕</span>
                Add Skill
              </button>
            </div>

            {/* Filters */}
            <div className="filters-section">
              <div className="search-filter">
                <input
                  type="text"
                  placeholder="Search skills..."
                  value={skillSearchQuery}
                  onChange={(e) => setSkillSearchQuery(e.target.value)}
                  className="search-input"
                />
              </div>
              
              <div className="dropdown-filters">
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="filter-select"
                >
                  <option value="">All Categories</option>
                  {skillCategories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
                
                <select
                  value={proficiencyFilter}
                  onChange={(e) => setProficiencyFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="">All Levels</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="expert">Expert</option>
                </select>
              </div>
            </div>

            {/* Skills Grid */}
            <div className="enhanced-grid">
              {getFilteredSkills().length > 0 ? (
                getFilteredSkills().map((userSkill) => (
                  <SkillCard
                    key={userSkill.id}
                    userSkill={userSkill}
                    onEdit={setEditingSkill}
                    onRemove={handleRemoveSkill}
                  />
                ))
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">🛠️</div>
                  <h3>No skills found</h3>
                  <p>
                    {skillSearchQuery || selectedCategory || proficiencyFilter
                      ? 'Try adjusting your filters or search terms.'
                      : 'Add your first skill to get started with your professional profile.'
                    }
                  </p>
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

        {/* Certifications Tab */}
        {activeTab === 'certifications' && (
          <div className="certifications-section">
            <div className="section-header">
              <h2>My Certifications</h2>
              <button 
                className="add-btn primary"
                onClick={() => setShowAddCertificationModal(true)}
              >
                <span className="btn-icon">🏆</span>
                Add Certification
              </button>
            </div>

            {/* Filters */}
            <div className="filters-section">
              <div className="search-filter">
                <input
                  type="text"
                  placeholder="Search certifications..."
                  value={certificationSearchQuery}
                  onChange={(e) => setCertificationSearchQuery(e.target.value)}
                  className="search-input"
                />
              </div>
            </div>

            {/* Certifications Grid */}
            <div className="enhanced-grid">
              {getFilteredCertifications().length > 0 ? (
                getFilteredCertifications().map((userCertification) => (
                  <CertificationCard
                    key={userCertification.id}
                    userCertification={userCertification}
                    onEdit={setEditingCertification}
                    onRemove={handleRemoveCertification}
                  />
                ))
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">🏆</div>
                  <h3>No certifications found</h3>
                  <p>
                    {certificationSearchQuery
                      ? 'Try adjusting your search terms.'
                      : 'Add your professional certifications to showcase your expertise.'
                    }
                  </p>
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

        {/* Other tabs content remains similar but with enhanced styling */}
        {/* Learning Paths and Explore tabs would be implemented here */}
      </div>

      {/* Modals remain the same as in original component */}
      {/* ... Modal implementations ... */}
    </div>
  );
};

export default SkillsAndCertificationsEnhanced;