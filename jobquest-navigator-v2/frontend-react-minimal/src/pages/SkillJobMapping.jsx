import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import graphqlApplicationService from '../services/graphqlApplicationService';
// import unifiedJobService from '../services/unifiedJobService'; // TODO: May be needed for future features
import './SkillJobMapping.css';

const SkillJobMapping = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [skillAnalysis, setSkillAnalysis] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedView, setSelectedView] = useState('overview'); // overview, detailed, gaps
  const [filterSkillLevel, setFilterSkillLevel] = useState('all');

  // Mock user skills - in real app this would come from user profile/skills service
  const [userSkills] = useState([
    { name: 'JavaScript', level: 'advanced', experience: '5+ years' },
    { name: 'React', level: 'advanced', experience: '4+ years' },
    { name: 'Node.js', level: 'intermediate', experience: '3+ years' },
    { name: 'Python', level: 'intermediate', experience: '2+ years' },
    { name: 'SQL', level: 'intermediate', experience: '3+ years' },
    { name: 'AWS', level: 'beginner', experience: '1+ years' },
    { name: 'Docker', level: 'beginner', experience: '1+ years' },
    { name: 'GraphQL', level: 'intermediate', experience: '2+ years' },
    { name: 'TypeScript', level: 'intermediate', experience: '2+ years' },
    { name: 'MongoDB', level: 'beginner', experience: '1+ years' }
  ]);

  useEffect(() => {
    if (user) {
      fetchApplicationsAndAnalyze();
    }
  }, [user]); // fetchApplicationsAndAnalyze is defined inside effect, so no dependency needed

  const fetchApplicationsAndAnalyze = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch user applications
      const response = await graphqlApplicationService.getApplications();
      const applicationsData = response.results || [];
      setApplications(applicationsData);

      // Analyze skills for each application
      const analysis = [];
      for (const app of applicationsData) {
        if (app.job) {
          const jobSkillAnalysis = await analyzeJobSkills(app.job, app);
          analysis.push({
            applicationId: app.id,
            jobId: app.job.id,
            jobTitle: app.job.title,
            company: app.job.company?.name || 'Unknown Company',
            status: app.status,
            appliedDate: app.applied_date,
            ...jobSkillAnalysis
          });
        }
      }
      
      setSkillAnalysis(analysis);
    } catch (err) {
      console.error('Error fetching applications:', err);
      setError('Failed to load skill analysis. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const analyzeJobSkills = async (job, application) => {
    // Extract skills from job description and requirements
    const jobText = `${job.title} ${job.description || ''} ${job.requirements || ''}`.toLowerCase();
    
    // Define skill keywords to look for
    const skillKeywords = {
      'JavaScript': ['javascript', 'js', 'ecmascript'],
      'React': ['react', 'reactjs', 'react.js'],
      'Node.js': ['node', 'nodejs', 'node.js'],
      'Python': ['python', 'django', 'flask'],
      'SQL': ['sql', 'mysql', 'postgresql', 'database'],
      'AWS': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
      'Docker': ['docker', 'container', 'kubernetes'],
      'GraphQL': ['graphql', 'gql'],
      'TypeScript': ['typescript', 'ts'],
      'MongoDB': ['mongodb', 'mongo', 'nosql'],
      'Java': ['java', 'spring', 'hibernate'],
      'C++': ['c++', 'cpp'],
      'Machine Learning': ['machine learning', 'ml', 'ai', 'tensorflow', 'pytorch'],
      'DevOps': ['devops', 'ci/cd', 'jenkins'],
      'Agile': ['agile', 'scrum', 'kanban'],
      'Git': ['git', 'github', 'version control']
    };

    const requiredSkills = [];
    const matchedSkills = [];
    const missingSkills = [];
    
    // Find required skills in job description
    Object.entries(skillKeywords).forEach(([skill, keywords]) => {
      const isRequired = keywords.some(keyword => jobText.includes(keyword));
      if (isRequired) {
        requiredSkills.push(skill);
        
        // Check if user has this skill
        const userSkill = userSkills.find(us => us.name.toLowerCase() === skill.toLowerCase());
        if (userSkill) {
          matchedSkills.push({
            skill: skill,
            userLevel: userSkill.level,
            experience: userSkill.experience,
            matchStrength: calculateMatchStrength(userSkill.level)
          });
        } else {
          missingSkills.push(skill);
        }
      }
    });

    // Calculate overall match percentage
    const matchPercentage = requiredSkills.length > 0 
      ? Math.round((matchedSkills.length / requiredSkills.length) * 100)
      : 0;

    // Generate recommendations
    const recommendations = generateRecommendations(missingSkills, matchedSkills);

    return {
      requiredSkills,
      matchedSkills,
      missingSkills,
      matchPercentage,
      recommendations,
      skillsAnalysis: application.skills_analysis || null
    };
  };

  const calculateMatchStrength = (level) => {
    switch (level) {
      case 'advanced': return 100;
      case 'intermediate': return 75;
      case 'beginner': return 50;
      default: return 25;
    }
  };

  const generateRecommendations = (missingSkills, matchedSkills) => {
    const recommendations = [];
    
    if (missingSkills.length > 0) {
      recommendations.push({
        type: 'skill_gap',
        priority: 'high',
        message: `Consider learning: ${missingSkills.slice(0, 3).join(', ')}`,
        skills: missingSkills
      });
    }

    const beginnerSkills = matchedSkills.filter(s => s.userLevel === 'beginner');
    if (beginnerSkills.length > 0) {
      recommendations.push({
        type: 'improvement',
        priority: 'medium',
        message: `Strengthen your skills in: ${beginnerSkills.map(s => s.skill).join(', ')}`,
        skills: beginnerSkills.map(s => s.skill)
      });
    }

    return recommendations;
  };

  const getMatchColor = (percentage) => {
    if (percentage >= 80) return '#22c55e'; // green
    if (percentage >= 60) return '#f59e0b'; // yellow
    if (percentage >= 40) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const filteredAnalysis = skillAnalysis.filter(analysis => {
    if (filterSkillLevel === 'all') return true;
    if (filterSkillLevel === 'high') return analysis.matchPercentage >= 80;
    if (filterSkillLevel === 'medium') return analysis.matchPercentage >= 60 && analysis.matchPercentage < 80;
    if (filterSkillLevel === 'low') return analysis.matchPercentage < 60;
    return true;
  });

  if (isLoading) {
    return (
      <div className="skill-mapping-container">
        <div className="loading">Loading skill analysis...</div>
      </div>
    );
  }

  return (
    <div className="skill-mapping-container">
      <div className="skill-mapping-header">
        <div className="header-content">
          <h1>Skills & Job Mapping</h1>
          <p className="header-subtitle">Analyze how your skills match with job applications</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn btn-secondary"
            onClick={() => navigate('/skills')}
          >
            Manage Skills
          </button>
        </div>
      </div>

      <div className="view-controls">
        <div className="view-tabs">
          <button 
            className={`tab ${selectedView === 'overview' ? 'active' : ''}`}
            onClick={() => setSelectedView('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab ${selectedView === 'detailed' ? 'active' : ''}`}
            onClick={() => setSelectedView('detailed')}
          >
            Detailed Analysis
          </button>
          <button 
            className={`tab ${selectedView === 'gaps' ? 'active' : ''}`}
            onClick={() => setSelectedView('gaps')}
          >
            Skill Gaps
          </button>
        </div>
        
        <div className="filter-controls">
          <select 
            value={filterSkillLevel} 
            onChange={(e) => setFilterSkillLevel(e.target.value)}
          >
            <option value="all">All Matches</option>
            <option value="high">High Match (80%+)</option>
            <option value="medium">Medium Match (60-79%)</option>
            <option value="low">Low Match (&lt;60%)</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {selectedView === 'overview' && (
        <div className="overview-section">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">{skillAnalysis.length}</div>
              <div className="stat-label">Job Applications</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">
                {skillAnalysis.length > 0 
                  ? Math.round(skillAnalysis.reduce((sum, a) => sum + a.matchPercentage, 0) / skillAnalysis.length)
                  : 0}%
              </div>
              <div className="stat-label">Average Match</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{userSkills.length}</div>
              <div className="stat-label">Your Skills</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">
                {skillAnalysis.filter(a => a.matchPercentage >= 80).length}
              </div>
              <div className="stat-label">High Matches</div>
            </div>
          </div>

          <div className="applications-overview">
            <h2>Application Skill Matches</h2>
            <div className="applications-grid">
              {filteredAnalysis.map(analysis => (
                <div key={analysis.applicationId} className="application-card">
                  <div className="application-header">
                    <h3>{analysis.jobTitle}</h3>
                    <div className="company">{analysis.company}</div>
                    <div className="status-badge">{analysis.status}</div>
                  </div>
                  
                  <div className="match-indicator">
                    <div className="match-percentage">
                      <span 
                        className="percentage-text"
                        style={{ color: getMatchColor(analysis.matchPercentage) }}
                      >
                        {analysis.matchPercentage}%
                      </span>
                      <span className="match-label">Skill Match</span>
                    </div>
                    <div 
                      className="match-bar"
                      style={{ 
                        '--match-percentage': `${analysis.matchPercentage}%`,
                        '--match-color': getMatchColor(analysis.matchPercentage)
                      }}
                    ></div>
                  </div>

                  <div className="skills-summary">
                    <div className="matched-skills">
                      <span className="skills-count">{analysis.matchedSkills.length}</span>
                      <span className="skills-label">Matched</span>
                    </div>
                    <div className="missing-skills">
                      <span className="skills-count">{analysis.missingSkills.length}</span>
                      <span className="skills-label">Missing</span>
                    </div>
                  </div>

                  <button 
                    className="view-details-btn"
                    onClick={() => setSelectedView('detailed')}
                  >
                    View Details
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {selectedView === 'detailed' && (
        <div className="detailed-section">
          <h2>Detailed Skill Analysis</h2>
          {filteredAnalysis.map(analysis => (
            <div key={analysis.applicationId} className="detailed-analysis-card">
              <div className="analysis-header">
                <div className="job-info">
                  <h3>{analysis.jobTitle}</h3>
                  <div className="company">{analysis.company}</div>
                  <div className="applied-date">
                    Applied: {new Date(analysis.appliedDate).toLocaleDateString()}
                  </div>
                </div>
                <div className="match-score">
                  <div 
                    className="score-circle"
                    style={{ '--score': analysis.matchPercentage }}
                  >
                    <span className="score-text">{analysis.matchPercentage}%</span>
                  </div>
                </div>
              </div>

              <div className="skills-breakdown">
                <div className="skills-section">
                  <h4>✅ Matched Skills ({analysis.matchedSkills.length})</h4>
                  <div className="skills-list">
                    {analysis.matchedSkills.map(skill => (
                      <div key={skill.skill} className="skill-item matched">
                        <span className="skill-name">{skill.skill}</span>
                        <span className={`skill-level ${skill.userLevel}`}>
                          {skill.userLevel}
                        </span>
                        <span className="skill-experience">{skill.experience}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {analysis.missingSkills.length > 0 && (
                  <div className="skills-section">
                    <h4>❌ Missing Skills ({analysis.missingSkills.length})</h4>
                    <div className="skills-list">
                      {analysis.missingSkills.map(skill => (
                        <div key={skill} className="skill-item missing">
                          <span className="skill-name">{skill}</span>
                          <span className="skill-action">Recommended to learn</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {analysis.recommendations.length > 0 && (
                  <div className="recommendations-section">
                    <h4>💡 Recommendations</h4>
                    {analysis.recommendations.map((rec, index) => (
                      <div key={index} className={`recommendation ${rec.priority}`}>
                        <div className="rec-message">{rec.message}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedView === 'gaps' && (
        <div className="gaps-section">
          <h2>Skill Gap Analysis</h2>
          <div className="gaps-overview">
            <p>Identify the most common missing skills across your job applications</p>
          </div>
          
          <div className="skill-gaps-analysis">
            {(() => {
              // Aggregate missing skills across all applications
              const skillCounts = {};
              skillAnalysis.forEach(analysis => {
                analysis.missingSkills.forEach(skill => {
                  skillCounts[skill] = (skillCounts[skill] || 0) + 1;
                });
              });

              const sortedSkills = Object.entries(skillCounts)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 10);

              return sortedSkills.length > 0 ? (
                <div className="top-missing-skills">
                  <h3>Most Requested Missing Skills</h3>
                  <div className="skills-chart">
                    {sortedSkills.map(([skill, count]) => (
                      <div key={skill} className="skill-bar">
                        <div className="skill-info">
                          <span className="skill-name">{skill}</span>
                          <span className="skill-count">{count} jobs</span>
                        </div>
                        <div className="bar-container">
                          <div 
                            className="bar-fill"
                            style={{ 
                              width: `${(count / Math.max(...Object.values(skillCounts))) * 100}%` 
                            }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="learning-recommendations">
                    <h3>Learning Priority Recommendations</h3>
                    <div className="priority-skills">
                      {sortedSkills.slice(0, 3).map(([skill, count]) => (
                        <div key={skill} className="priority-skill-card">
                          <h4>{skill}</h4>
                          <p>Requested in {count} of your job applications</p>
                          <button className="btn btn-primary">
                            Find Learning Resources
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="no-gaps">
                  <h3>Great job! 🎉</h3>
                  <p>You have all the skills required for your job applications.</p>
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {skillAnalysis.length === 0 && !isLoading && (
        <div className="no-applications">
          <div className="no-data-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </div>
          <h3>No job applications found</h3>
          <p>Apply to some jobs to see skill mapping analysis.</p>
          <button 
            onClick={() => navigate('/jobs')}
            className="btn btn-primary"
          >
            Browse Jobs
          </button>
        </div>
      )}
    </div>
  );
};

export default SkillJobMapping;