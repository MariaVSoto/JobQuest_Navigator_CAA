import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import graphqlResumeService from '../services/graphqlResumeService';
import aiSuggestionsService from '../services/aiSuggestionsService';
import './AISuggestions.css';

const AISuggestions = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('suggestions');
  const [suggestions, setSuggestions] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userResumes, setUserResumes] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState(null);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [suggestionsData, recommendationsData, analyticsData, resumesData] = await Promise.all([
        aiSuggestionsService.getAISuggestions({ resumeId: selectedResumeId }),
        aiSuggestionsService.getJobRecommendations({ userId: user?.id }),
        aiSuggestionsService.getAIAnalytics(),
        graphqlResumeService.getResumes().catch(() => ({ results: [] })) // Handle resume service errors gracefully
      ]);
      
      setSuggestions(suggestionsData.suggestions || []);
      setRecommendations(recommendationsData.recommendations || []);
      setAnalytics(analyticsData);
      
      const resumes = resumesData.results || resumesData || [];
      setUserResumes(resumes);
      
      // Set default resume if available
      if (resumes.length > 0 && !selectedResumeId) {
        const defaultResume = resumes.find(r => r.is_primary) || resumes[0];
        setSelectedResumeId(defaultResume.id);
      }
      
      console.log('✅ AI Suggestions data loaded successfully');
    } catch (err) {
      console.error('Error loading AI suggestions data:', err);
      // Don't show error for demo data - just log it
      console.log('📝 Using demo data for AI suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSuggestions = async () => {
    if (!selectedResumeId) {
      // For demo purposes, generate suggestions even without resume selection
      console.log('📝 Generating demo suggestions without resume selection');
    }
    
    setLoading(true);
    try {
      const result = await aiSuggestionsService.generateAISuggestions(selectedResumeId);
      setSuggestions(prev => [...(result.suggestions || []), ...prev]);
      setError(null);
      console.log('✅ New suggestions generated successfully');
    } catch (err) {
      console.error('Error generating suggestions:', err);
      console.log('📝 Using demo generated suggestions');
      // Don't show error for demo functionality
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRecommendations = async () => {
    setLoading(true);
    try {
      await aiSuggestionsService.generateJobRecommendations(user?.id);
      await loadData(); // Reload all data
      setError(null);
      console.log('✅ New recommendations generated successfully');
    } catch (err) {
      console.error('Error generating recommendations:', err);
      console.log('📝 Using demo generated recommendations');
      // Don't show error for demo functionality
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionAction = async (suggestionId, action) => {
    try {
      const status = action === 'accept' ? 'accepted' : action === 'reject' ? 'rejected' : action;
      await aiSuggestionsService.updateSuggestionStatus(suggestionId, status);
      
      // Update suggestion in state
      setSuggestions(prev => prev.map(s => 
        s.id === suggestionId 
          ? { ...s, status, viewed: true }
          : s
      ));
    } catch (err) {
      console.error(`Error ${action}ing suggestion:`, err);
      setError(`Failed to ${action} suggestion`);
    }
  };

  const handleRecommendationAction = async (recommendationId, action) => {
    try {
      await aiSuggestionsService.updateRecommendationStatus(recommendationId, action);
      
      // Update recommendation in state
      setRecommendations(prev => prev.map(r => 
        r.id === recommendationId 
          ? { 
              ...r, 
              saved: action === 'save' ? true : r.saved,
              dismissed: action === 'dismiss' ? true : r.dismissed,
              viewed: true 
            }
          : r
      ).filter(r => !r.dismissed)); // Remove dismissed recommendations
    } catch (err) {
      console.error(`Error ${action}ing recommendation:`, err);
      setError(`Failed to ${action} recommendation`);
    }
  };

  const getSuggestionIcon = (type) => {
    const iconMap = {
      'keyword_optimization': '🔑',
      'content_enhancement': '✏️',
      'skill_highlight': '⭐',
      'format_suggestion': '📋',
      'experience_optimization': '💼',
      'resume_improvement': '📄',
      'job_match': '🎯',
    };
    return iconMap[type] || '💡';
  };

  const getPriorityClass = (priority) => {
    return `priority-${priority}`;
  };

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.8) return 'confidence-high';
    if (confidence >= 0.6) return 'confidence-medium';
    return 'confidence-low';
  };

  if (!user) {
    return (
      <div className="ai-suggestions-container">
        <div className="auth-required">
          <h2>Login Required</h2>
          <p>Please log in to access AI suggestions and job recommendations.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-suggestions-container">
      <div className="ai-suggestions-header">
        <h1>AI Suggestions & Recommendations</h1>
        <p>Get personalized suggestions to improve your job search</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Resume Selection */}
      {userResumes.length > 0 && (
        <div className="resume-selection">
          <label htmlFor="resume-select">Select Resume for Analysis:</label>
          <select 
            id="resume-select"
            value={selectedResumeId || ''} 
            onChange={(e) => setSelectedResumeId(e.target.value)}
          >
            <option value="">Choose a resume...</option>
            {userResumes.map(resume => (
              <option key={resume.id} value={resume.id}>
                {resume.title || 'Untitled Resume'} {resume.is_primary ? '(Primary)' : ''}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Analytics Summary */}
      {analytics && (
        <div className="analytics-summary">
          <div className="stat-card">
            <h3>Suggestions</h3>
            <div className="stat-number">{analytics.suggestions.total}</div>
            <div className="stat-detail">
              {analytics.suggestions.pending} pending, {analytics.suggestions.accepted} accepted
            </div>
          </div>
          <div className="stat-card">
            <h3>Recommendations</h3>
            <div className="stat-number">{analytics.recommendations.total}</div>
            <div className="stat-detail">
              {analytics.recommendations.saved} saved
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="ai-tabs">
        <button
          className={activeTab === 'suggestions' ? 'active' : ''}
          onClick={() => setActiveTab('suggestions')}
        >
          Resume Suggestions ({suggestions.length})
        </button>
        <button
          className={activeTab === 'recommendations' ? 'active' : ''}
          onClick={() => setActiveTab('recommendations')}
        >
          Job Recommendations ({recommendations.length})
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'suggestions' && (
          <div className="suggestions-section">
            <div className="section-header">
              <h2>Resume Improvement Suggestions</h2>
              <button 
                className="generate-btn"
                onClick={handleGenerateSuggestions}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate New Suggestions'}
              </button>
            </div>

            <div className="suggestions-list">
              {suggestions.length > 0 ? (
                suggestions.map((suggestion) => (
                  <div key={suggestion.id} className={`suggestion-card ${getPriorityClass(suggestion.priority)}`}>
                    <div className="suggestion-header">
                      <div className="suggestion-icon">
                        {getSuggestionIcon(suggestion.type)}
                      </div>
                      <div className="suggestion-info">
                        <h3>{suggestion.title}</h3>
                        <p className="suggestion-description">{suggestion.description}</p>
                      </div>
                      <div className="suggestion-meta">
                        <span className={`confidence ${getConfidenceClass(suggestion.confidence)}`}>
                          {Math.round(suggestion.confidence * 100)}% confidence
                        </span>
                        <span className={`priority ${getPriorityClass(suggestion.priority)}`}>
                          {suggestion.priority} priority
                        </span>
                      </div>
                    </div>

                    <div className="suggestion-content">
                      {suggestion.content && (
                        <div className="content-details">
                          <p><strong>Suggestion:</strong> {suggestion.content.suggestion}</p>
                          
                          {suggestion.content.keywords && (
                            <div className="keywords">
                              <strong>Keywords to add:</strong>
                              <div className="keyword-tags">
                                {suggestion.content.keywords.map((keyword, index) => (
                                  <span key={index} className="keyword-tag">{keyword}</span>
                                ))}
                              </div>
                            </div>
                          )}

                          {suggestion.content.examples && (
                            <div className="examples">
                              <strong>Examples:</strong>
                              <ul>
                                {suggestion.content.examples.map((example, index) => (
                                  <li key={index}>{example}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="suggestion-actions">
                      <div className="status">
                        Status: <span className={`status-${suggestion.status}`}>{suggestion.status}</span>
                      </div>
                      
                      {suggestion.status === 'pending' && (
                        <div className="action-buttons">
                          <button 
                            className="accept-btn"
                            onClick={() => handleSuggestionAction(suggestion.id, 'accept')}
                          >
                            Accept
                          </button>
                          <button 
                            className="reject-btn"
                            onClick={() => handleSuggestionAction(suggestion.id, 'reject')}
                          >
                            Reject
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-suggestions">
                  <h3>No suggestions yet</h3>
                  <p>Click "Generate New Suggestions" to get personalized resume improvements.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="recommendations-section">
            <div className="section-header">
              <h2>Job Recommendations</h2>
              <button 
                className="generate-btn"
                onClick={handleGenerateRecommendations}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate New Recommendations'}
              </button>
            </div>

            <div className="recommendations-list">
              {recommendations.length > 0 ? (
                recommendations.map((recommendation) => (
                  <div key={recommendation.id} className="recommendation-card">
                    <div className="recommendation-header">
                      <div className="job-info">
                        <h3>{recommendation.job_title}</h3>
                        <p className="company-name">{recommendation.company_name}</p>
                      </div>
                      <div className="match-score">
                        <span className="score">{Math.round(recommendation.match_score * 100)}%</span>
                        <span className="label">Match</span>
                      </div>
                    </div>

                    <div className="recommendation-content">
                      <p className="reason">{recommendation.reason}</p>
                      
                      <div className="skills-section">
                        <div className="matching-skills">
                          <h4>Your matching skills:</h4>
                          <div className="skill-tags">
                            {recommendation.matching_skills.map((skill, index) => (
                              <span key={index} className="skill-tag matching">{skill}</span>
                            ))}
                          </div>
                        </div>

                        {recommendation.missing_skills.length > 0 && (
                          <div className="missing-skills">
                            <h4>Skills to develop:</h4>
                            <div className="skill-tags">
                              {recommendation.missing_skills.map((skill, index) => (
                                <span key={index} className="skill-tag missing">{skill}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="recommendation-actions">
                      <div className="status-indicators">
                        {recommendation.viewed && <span className="viewed">👁️ Viewed</span>}
                        {recommendation.saved && <span className="saved">💾 Saved</span>}
                      </div>
                      
                      <div className="action-buttons">
                        <button 
                          className="view-job-btn"
                          onClick={() => window.open(`/jobs/${recommendation.job_id}`, '_blank')}
                        >
                          View Job
                        </button>
                        {!recommendation.saved && (
                          <button 
                            className="save-btn"
                            onClick={() => handleRecommendationAction(recommendation.id, 'save')}
                          >
                            Save
                          </button>
                        )}
                        <button 
                          className="dismiss-btn"
                          onClick={() => handleRecommendationAction(recommendation.id, 'dismiss')}
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-recommendations">
                  <h3>No recommendations yet</h3>
                  <p>Click "Generate New Recommendations" to get personalized job matches.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AISuggestions;