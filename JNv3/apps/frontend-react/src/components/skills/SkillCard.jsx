import React, { useState } from 'react';
import './SkillCard.css';

const SkillCard = ({ userSkill, onEdit, onRemove, onViewDetails }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { skill } = userSkill;

  const formatProficiencyLevel = (level) => {
    const levels = {
      'beginner': { label: 'Beginner', color: '#f59e0b' },
      'intermediate': { label: 'Intermediate', color: '#3b82f6' },
      'advanced': { label: 'Advanced', color: '#10b981' },
      'expert': { label: 'Expert', color: '#8b5cf6' }
    };
    return levels[level] || levels['beginner'];
  };

  const getFrequencyIcon = (frequency) => {
    const icons = {
      'daily': '🔥',
      'weekly': '📅',
      'monthly': '🗓️',
      'occasionally': '⏰',
      'rarely': '💤'
    };
    return icons[frequency] || '⏰';
  };

  const proficiency = formatProficiencyLevel(userSkill.proficiency_level);

  return (
    <div className={`skill-card ${isExpanded ? 'expanded' : ''}`}>
      <div className="skill-card-header">
        <div className="skill-info">
          <div className="skill-title-section">
            <h3 className="skill-name">{skill?.name || userSkill.skill_name}</h3>
            <div className="skill-badges">
              <span 
                className="proficiency-badge"
                style={{ backgroundColor: proficiency.color }}
              >
                {proficiency.label}
              </span>
              {userSkill.is_verified && (
                <span className="verified-badge">
                  <span className="verified-icon">✓</span> Verified
                </span>
              )}
            </div>
          </div>
          
          <div className="skill-meta">
            {userSkill.years_experience > 0 && (
              <div className="experience-indicator">
                <span className="meta-icon">📈</span>
                <span>{userSkill.years_experience} {userSkill.years_experience === 1 ? 'year' : 'years'}</span>
              </div>
            )}
            
            {userSkill.frequency_of_use && (
              <div className="frequency-indicator">
                <span className="meta-icon">{getFrequencyIcon(userSkill.frequency_of_use)}</span>
                <span className="frequency-text">
                  {userSkill.frequency_of_use.replace('_', ' ')}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="skill-actions">
          <button 
            className="action-btn edit-btn"
            onClick={() => onEdit(userSkill)}
            title="Edit skill"
            aria-label="Edit skill"
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
              <button 
                className="dropdown-item"
                onClick={() => onViewDetails && onViewDetails(skill)}
              >
                <span className="dropdown-icon">👁️</span>
                View Details
              </button>
              <button 
                className="dropdown-item delete-item"
                onClick={() => onRemove(userSkill.id)}
              >
                <span className="dropdown-icon">🗑️</span>
                Remove Skill
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Expandable Content */}
      <div className={`skill-details ${isExpanded ? 'visible' : ''}`}>
        {userSkill.last_used && (
          <div className="detail-item">
            <span className="detail-label">Last Used:</span>
            <span className="detail-value">
              {new Date(userSkill.last_used).toLocaleDateString()}
            </span>
          </div>
        )}
        
        {userSkill.target_proficiency && userSkill.target_proficiency !== userSkill.proficiency_level && (
          <div className="detail-item">
            <span className="detail-label">Goal:</span>
            <span className="detail-value">
              {formatProficiencyLevel(userSkill.target_proficiency).label}
            </span>
          </div>
        )}
        
        {userSkill.evidence_url && (
          <div className="detail-item">
            <span className="detail-label">Evidence:</span>
            <a 
              href={userSkill.evidence_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="evidence-link"
            >
              View Portfolio
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15,3 21,3 21,9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
            </a>
          </div>
        )}

        {/* Skill Progress Visualization */}
        <div className="skill-progress">
          <div className="progress-header">
            <span className="progress-label">Progress to Goal</span>
            <span className="progress-percentage">75%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: '75%', backgroundColor: proficiency.color }}
            ></div>
          </div>
        </div>
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

export default SkillCard;