import React, { useState } from 'react';
import './CertificationCard.css';

const CertificationCard = ({ userCertification, onEdit, onRemove, onViewDetails }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { certification } = userCertification;

  const getStatusInfo = (status) => {
    const statusMap = {
      'planned': { label: 'Planned', color: '#64748b', icon: '📋' },
      'in_progress': { label: 'In Progress', color: '#f59e0b', icon: '⏳' },
      'active': { label: 'Active', color: '#10b981', icon: '✅' },
      'expired': { label: 'Expired', color: '#ef4444', icon: '⚠️' }
    };
    return statusMap[status] || statusMap['planned'];
  };

  const isExpiringSoon = () => {
    if (!userCertification.expiry_date) return false;
    const expiryDate = new Date(userCertification.expiry_date);
    const today = new Date();
    const daysUntilExpiry = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  };

  const statusInfo = getStatusInfo(userCertification.status);

  return (
    <div className={`certification-card ${isExpanded ? 'expanded' : ''} ${userCertification.status}`}>
      <div className="certification-card-header">
        <div className="certification-info">
          <div className="certification-title-section">
            <h3 className="certification-name">
              {certification?.name || userCertification.certification_name}
            </h3>
            <div className="certification-badges">
              <span 
                className="status-badge"
                style={{ backgroundColor: statusInfo.color }}
              >
                <span className="status-icon">{statusInfo.icon}</span>
                {statusInfo.label}
              </span>
              
              {userCertification.is_verified && (
                <span className="verified-badge">
                  <span className="verified-icon">✓</span> Verified
                </span>
              )}
              
              {isExpiringSoon() && (
                <span className="warning-badge">
                  <span className="warning-icon">⚠️</span> Expires Soon
                </span>
              )}
            </div>
          </div>

          <div className="certification-meta">
            <div className="issuer-info">
              <span className="meta-icon">🏢</span>
              <span className="issuer-name">
                {certification?.issuing_organization || 'Organization'}
              </span>
            </div>
            
            {userCertification.earned_date && (
              <div className="earned-info">
                <span className="meta-icon">📅</span>
                <span>Earned {new Date(userCertification.earned_date).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>

        <div className="certification-actions">
          <button 
            className="action-btn edit-btn"
            onClick={() => onEdit(userCertification)}
            title="Edit certification"
            aria-label="Edit certification"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          
          <div className="dropdown-menu">
            <button className="action-btn more-btn" title="More options">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="1"/>
                <circle cx="12" cy="5" r="1"/>
                <circle cx="12" cy="19" r="1"/>
              </svg>
            </button>
            
            <div className="dropdown-content">
              {userCertification.credential_url && (
                <a 
                  href={userCertification.credential_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="dropdown-item"
                >
                  <span className="dropdown-icon">🔗</span>
                  View Certificate
                </a>
              )}
              
              <button 
                className="dropdown-item"
                onClick={() => onViewDetails && onViewDetails(certification)}
              >
                <span className="dropdown-icon">👁️</span>
                View Details
              </button>
              
              <button 
                className="dropdown-item delete-item"
                onClick={() => onRemove(userCertification.id)}
              >
                <span className="dropdown-icon">🗑️</span>
                Remove
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Expandable Content */}
      <div className={`certification-details ${isExpanded ? 'visible' : ''}`}>
        {userCertification.credential_id && (
          <div className="detail-item">
            <span className="detail-label">Credential ID:</span>
            <span className="detail-value credential-id">
              {userCertification.credential_id}
            </span>
          </div>
        )}
        
        {userCertification.expiry_date && (
          <div className="detail-item">
            <span className="detail-label">Expires:</span>
            <span className={`detail-value ${isExpiringSoon() ? 'warning-text' : ''}`}>
              {new Date(userCertification.expiry_date).toLocaleDateString()}
              {isExpiringSoon() && (
                <span className="days-remaining">
                  ({Math.ceil((new Date(userCertification.expiry_date) - new Date()) / (1000 * 60 * 60 * 24))} days)
                </span>
              )}
            </span>
          </div>
        )}
        
        {userCertification.target_completion_date && userCertification.status === 'in_progress' && (
          <div className="detail-item">
            <span className="detail-label">Target Date:</span>
            <span className="detail-value">
              {new Date(userCertification.target_completion_date).toLocaleDateString()}
            </span>
          </div>
        )}

        {userCertification.status === 'in_progress' && userCertification.study_progress !== undefined && (
          <div className="study-progress">
            <div className="progress-header">
              <span className="progress-label">Study Progress</span>
              <span className="progress-percentage">{userCertification.study_progress}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ 
                  width: `${userCertification.study_progress}%`,
                  backgroundColor: statusInfo.color 
                }}
              ></div>
            </div>
          </div>
        )}

        {userCertification.notes && (
          <div className="certification-notes">
            <span className="notes-label">Notes:</span>
            <p className="notes-content">{userCertification.notes}</p>
          </div>
        )}

        {certification?.description && (
          <div className="certification-description">
            <span className="description-label">About this certification:</span>
            <p className="description-content">{certification.description}</p>
          </div>
        )}
      </div>

      <button 
        className="expand-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-label={isExpanded ? 'Show less details' : 'Show more details'}
      >
        <span className="toggle-text">
          {isExpanded ? 'Show Less' : 'Show More'}
        </span>
        <svg 
          className={`chevron-icon ${isExpanded ? 'rotated' : ''}`}
          width="16" 
          height="16" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2"
        >
          <polyline points="6,9 12,15 18,9"/>
        </svg>
      </button>
    </div>
  );
};

export default CertificationCard;