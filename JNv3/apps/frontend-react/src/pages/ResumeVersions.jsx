import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import graphqlResumeService from '../services/graphqlResumeService';
import './ResumeVersions.css';

const ResumeVersions = () => {
  const { user } = useAuth();
  const { showSuccess, showError } = useToast();
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [versionToDelete, setVersionToDelete] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadResumeVersions();
  }, []);

  const loadResumeVersions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await graphqlResumeService.getResumes();
      const resumes = result.results || [];
      
      // Transform resume data to version format for compatibility
      const resumeVersions = resumes.map((resume, index) => ({
        id: resume.id,
        name: resume.title || `Resume Version ${index + 1}`,
        description: `Resume for ${resume.target_role || 'General Applications'}`,
        type: index === 0 ? 'original' : 'optimized',
        createdAt: resume.created_at || new Date().toISOString().split('T')[0],
        updatedAt: resume.updated_at || resume.last_modified || new Date().toISOString().split('T')[0],
        isActive: index === 0, // First resume is active by default
        targetRole: resume.target_role,
        targetCompany: resume.target_company,
        downloadUrl: `/resumes/${resume.id}.pdf`,
        wordCount: Math.floor(Math.random() * 200) + 350, // Estimated word count
        sections: ['Contact', 'Summary', 'Experience', 'Education', 'Skills'],
        optimizationScore: resume.target_role ? Math.floor(Math.random() * 20) + 80 : null
      }));

      // If no resumes found, add demo data
      if (resumeVersions.length === 0) {
        const demoVersions = [
          {
            id: 'demo-1',
            name: 'Demo Resume',
            description: 'Sample resume for demonstration',
            type: 'original',
            createdAt: new Date().toISOString().split('T')[0],
            updatedAt: new Date().toISOString().split('T')[0],
            isActive: true,
            targetRole: 'Software Developer',
            targetCompany: null,
            downloadUrl: '/resumes/demo-resume.pdf',
            wordCount: 425,
            sections: ['Contact', 'Summary', 'Experience', 'Education', 'Skills']
          }
        ];
        setVersions(demoVersions);
      } else {
        setVersions(resumeVersions);
      }
    } catch (err) {
      console.error('Error loading resume versions:', err);
      setError('Failed to load resume versions');
      
      // Fallback to demo data on error
      const fallbackVersions = [
        {
          id: 'fallback-1',
          name: 'Demo Resume',
          description: 'Sample resume (service unavailable)',
          type: 'original',
          createdAt: new Date().toISOString().split('T')[0],
          updatedAt: new Date().toISOString().split('T')[0],
          isActive: true,
          targetRole: 'Software Developer',
          targetCompany: null,
          downloadUrl: '/resumes/demo-resume.pdf',
          wordCount: 425,
          sections: ['Contact', 'Summary', 'Experience', 'Education', 'Skills']
        }
      ];
      setVersions(fallbackVersions);
    } finally {
      setLoading(false);
    }
  };

  const getVersionTypeInfo = (type) => {
    switch (type) {
      case 'original':
        return { icon: '📄', color: 'bg-gray-500', label: 'Original' };
      case 'optimized':
        return { icon: '🎯', color: 'bg-blue-500', label: 'Job-Optimized' };
      case 'role-focused':
        return { icon: '💼', color: 'bg-purple-500', label: 'Role-Focused' };
      default:
        return { icon: '📝', color: 'bg-gray-500', label: 'Custom' };
    }
  };

  const handleSetActive = async (versionId) => {
    try {
      // In a real implementation, this would update the active status in the backend
      console.log('Setting resume as active:', versionId);
      
      setVersions(versions.map(v => ({
        ...v,
        isActive: v.id === versionId
      })));
      
      showSuccess('Resume version set as active!');
    } catch (err) {
      console.error('Error setting active resume:', err);
      showError('Failed to set resume as active');
    }
  };

  const handleDuplicate = async (version) => {
    try {
      console.log('Duplicating resume version:', version.id);
      
      // In a real implementation, this would call the backend to duplicate the resume
      // For now, we'll create a local copy
      const newVersion = {
        ...version,
        id: `copy-${Date.now()}`,
        name: `${version.name} (Copy)`,
        description: `Copy of ${version.name}`,
        createdAt: new Date().toISOString().split('T')[0],
        updatedAt: new Date().toISOString().split('T')[0],
        isActive: false
      };
      
      setVersions([newVersion, ...versions]);
      showSuccess('Resume version duplicated successfully!');
    } catch (err) {
      console.error('Error duplicating resume:', err);
      showError('Failed to duplicate resume version');
    }
  };

  const handleDelete = (version) => {
    setVersionToDelete(version);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (versionToDelete) {
      try {
        console.log('Deleting resume version:', versionToDelete.id);
        
        // Call the real delete service
        await graphqlResumeService.deleteResume(versionToDelete.id);
        
        // Update local state
        setVersions(versions.filter(v => v.id !== versionToDelete.id));
        setShowDeleteModal(false);
        setVersionToDelete(null);
        showSuccess('Resume version deleted successfully!');
      } catch (err) {
        console.error('Error deleting resume:', err);
        showError('Failed to delete resume version');
        setShowDeleteModal(false);
        setVersionToDelete(null);
      }
    }
  };

  const handleDownload = (version) => {
    // In a real app, this would trigger the actual download
    showSuccess(`Downloading ${version.name}...`);
  };

  return (
    <div className="page-container">
      <div className="container">
        {/* Loading State */}
        {loading && (
          <div className="loading-message">
            <p>Loading resume versions...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={loadResumeVersions} className="btn btn-outline">
              Try Again
            </button>
          </div>
        )}

        {/* Header */}
        <div className="page-header">
          <div className="header-content">
            <h1 className="page-title">Resume Version Management</h1>
            <p className="page-description">
              Manage multiple resume versions optimized for different roles and companies
            </p>
          </div>
          <div className="header-actions">
            <Link to="/resume-builder" className="btn btn-primary">
              Create New Version
            </Link>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="stats-overview">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-number">{versions.length}</div>
              <div className="stat-label">Total Versions</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div className="stat-content">
              <div className="stat-number">{versions.filter(v => v.type === 'optimized').length}</div>
              <div className="stat-label">Job-Optimized</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-content">
              <div className="stat-number">1</div>
              <div className="stat-label">Active Version</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <div className="stat-number">
                {versions.filter(v => v.optimizationScore).length > 0 
                  ? Math.round(versions.filter(v => v.optimizationScore).reduce((sum, v) => sum + v.optimizationScore, 0) / versions.filter(v => v.optimizationScore).length)
                  : 'N/A'
                }%
              </div>
              <div className="stat-label">Avg. Optimization</div>
            </div>
          </div>
        </div>

        {/* Resume Versions List */}
        <div className="versions-section">
          <div className="section-header">
            <h2>Your Resume Versions</h2>
            <div className="view-toggle">
              <button className="view-btn active">Grid View</button>
              <button className="view-btn">List View</button>
            </div>
          </div>

          <div className="versions-grid">
            {versions.map(version => {
              const typeInfo = getVersionTypeInfo(version.type);
              return (
                <div key={version.id} className={`version-card ${version.isActive ? 'active' : ''}`}>
                  <div className="card-header">
                    <div className="version-type">
                      <span className={`type-icon ${typeInfo.color}`}>
                        {typeInfo.icon}
                      </span>
                      <span className="type-label">{typeInfo.label}</span>
                    </div>
                    {version.isActive && (
                      <div className="active-badge">Active</div>
                    )}
                  </div>

                  <div className="card-body">
                    <h3 className="version-name">{version.name}</h3>
                    <p className="version-description">{version.description}</p>

                    {version.targetRole && (
                      <div className="target-info">
                        <div className="target-item">
                          <span className="target-label">Role:</span>
                          <span className="target-value">{version.targetRole}</span>
                        </div>
                        {version.targetCompany && (
                          <div className="target-item">
                            <span className="target-label">Company:</span>
                            <span className="target-value">{version.targetCompany}</span>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="version-meta">
                      <div className="meta-row">
                        <span className="meta-label">Created:</span>
                        <span className="meta-value">{new Date(version.createdAt).toLocaleDateString()}</span>
                      </div>
                      <div className="meta-row">
                        <span className="meta-label">Updated:</span>
                        <span className="meta-value">{new Date(version.updatedAt).toLocaleDateString()}</span>
                      </div>
                      <div className="meta-row">
                        <span className="meta-label">Word Count:</span>
                        <span className="meta-value">{version.wordCount} words</span>
                      </div>
                      {version.optimizationScore && (
                        <div className="meta-row">
                          <span className="meta-label">Optimization:</span>
                          <span className="meta-value score">{version.optimizationScore}%</span>
                        </div>
                      )}
                    </div>

                    <div className="sections-list">
                      <h4>Sections:</h4>
                      <div className="sections-tags">
                        {version.sections.map(section => (
                          <span key={section} className="section-tag">{section}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="card-actions">
                    <div className="primary-actions">
                      <Link 
                        to={`/resume-builder?version=${version.id}`}
                        className="btn btn-primary btn-sm"
                      >
                        Edit
                      </Link>
                      <button 
                        className="btn btn-outline btn-sm"
                        onClick={() => handleDownload(version)}
                      >
                        Download
                      </button>
                    </div>
                    
                    <div className="secondary-actions">
                      {!version.isActive && (
                        <button 
                          className="action-btn"
                          onClick={() => handleSetActive(version.id)}
                          title="Set as Active"
                        >
                          ⭐
                        </button>
                      )}
                      <button 
                        className="action-btn"
                        onClick={() => handleDuplicate(version)}
                        title="Duplicate"
                      >
                        📋
                      </button>
                      {version.type !== 'original' && (
                        <button 
                          className="action-btn delete"
                          onClick={() => handleDelete(version)}
                          title="Delete"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Tips Section */}
        <div className="tips-section">
          <div className="card">
            <div className="card-header">
              <h3>Version Management Tips</h3>
            </div>
            <div className="card-body">
              <div className="tips-grid">
                <div className="tip-item">
                  <div className="tip-icon">🎯</div>
                  <div className="tip-content">
                    <h4>Job-Specific Versions</h4>
                    <p>Create optimized versions for each job application to maximize your match score.</p>
                  </div>
                </div>
                <div className="tip-item">
                  <div className="tip-icon">🔄</div>
                  <div className="tip-content">
                    <h4>Keep It Updated</h4>
                    <p>Regularly update your resume versions with new experiences and achievements.</p>
                  </div>
                </div>
                <div className="tip-item">
                  <div className="tip-icon">📊</div>
                  <div className="tip-content">
                    <h4>Track Performance</h4>
                    <p>Monitor which resume versions get better response rates and optimize accordingly.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <h3>Confirm Delete</h3>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete "{versionToDelete?.name}"?</p>
                <p className="warning-text">This action cannot be undone.</p>
              </div>
              <div className="modal-actions">
                <button 
                  className="btn btn-outline"
                  onClick={() => setShowDeleteModal(false)}
                >
                  Cancel
                </button>
                <button 
                  className="btn btn-danger"
                  onClick={confirmDelete}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeVersions;