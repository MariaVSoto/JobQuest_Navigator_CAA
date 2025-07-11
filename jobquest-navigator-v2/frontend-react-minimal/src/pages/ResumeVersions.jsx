import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './ResumeVersions.css';

const ResumeVersions = () => {
  const { user } = useAuth();
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [versionToDelete, setVersionToDelete] = useState(null);

  useEffect(() => {
    // Mock resume versions data
    const mockVersions = [
      {
        id: 'v1',
        name: 'Original Resume',
        description: 'My first uploaded resume',
        type: 'original',
        createdAt: '2024-06-15',
        updatedAt: '2024-06-15',
        isActive: false,
        targetRole: null,
        targetCompany: null,
        downloadUrl: '/resumes/original-resume.pdf',
        wordCount: 425,
        sections: ['Contact', 'Summary', 'Experience', 'Education', 'Skills']
      },
      {
        id: 'v2',
        name: 'Senior Developer - TechCorp',
        description: 'Optimized for Senior Developer position at TechCorp',
        type: 'optimized',
        createdAt: '2024-06-20',
        updatedAt: '2024-06-22',
        isActive: true,
        targetRole: 'Senior Software Engineer',
        targetCompany: 'TechCorp Inc.',
        downloadUrl: '/resumes/techcorp-optimized.pdf',
        wordCount: 445,
        sections: ['Contact', 'Summary', 'Experience', 'Education', 'Skills', 'Projects'],
        optimizationScore: 92
      },
      {
        id: 'v3',
        name: 'Full Stack - StartupXYZ',
        description: 'Tailored for Full Stack Developer role at StartupXYZ',
        type: 'optimized',
        createdAt: '2024-06-25',
        updatedAt: '2024-06-25',
        isActive: false,
        targetRole: 'Full Stack Developer',
        targetCompany: 'StartupXYZ',
        downloadUrl: '/resumes/startupxyz-optimized.pdf',
        wordCount: 398,
        sections: ['Contact', 'Summary', 'Experience', 'Education', 'Skills'],
        optimizationScore: 87
      },
      {
        id: 'v4',
        name: 'Product Manager Focus',
        description: 'Resume version highlighting product management experience',
        type: 'role-focused',
        createdAt: '2024-07-01',
        updatedAt: '2024-07-05',
        isActive: false,
        targetRole: 'Product Manager',
        targetCompany: null,
        downloadUrl: '/resumes/product-manager-focus.pdf',
        wordCount: 412,
        sections: ['Contact', 'Summary', 'Experience', 'Education', 'Skills', 'Achievements'],
        optimizationScore: null
      }
    ];
    
    setVersions(mockVersions);
  }, []);

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

  const handleSetActive = (versionId) => {
    setVersions(versions.map(v => ({
      ...v,
      isActive: v.id === versionId
    })));
    alert('Resume version set as active!');
  };

  const handleDuplicate = (version) => {
    const newVersion = {
      ...version,
      id: `v${Date.now()}`,
      name: `${version.name} (Copy)`,
      description: `Copy of ${version.name}`,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0],
      isActive: false
    };
    
    setVersions([newVersion, ...versions]);
    alert('Resume version duplicated successfully!');
  };

  const handleDelete = (version) => {
    setVersionToDelete(version);
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    if (versionToDelete) {
      setVersions(versions.filter(v => v.id !== versionToDelete.id));
      setShowDeleteModal(false);
      setVersionToDelete(null);
      alert('Resume version deleted successfully!');
    }
  };

  const handleDownload = (version) => {
    // In a real app, this would trigger the actual download
    alert(`Downloading ${version.name}...`);
  };

  return (
    <div className="page-container">
      <div className="container">
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