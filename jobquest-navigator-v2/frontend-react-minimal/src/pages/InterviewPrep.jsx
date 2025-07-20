import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import companyResearchService from '../services/companyResearchService';
import './InterviewPrep.css';

const InterviewPrep = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('tips');
  const [selectedCategory, setSelectedCategory] = useState('general');
  const [interviewQuestions, setInterviewQuestions] = useState([]);
  const [practiceSessions, setPracticeSessions] = useState([]);
  const [interviewTips, setInterviewTips] = useState([]);
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      loadUserData();
    }
  }, [user]);

  useEffect(() => {
    if (user && activeTab === 'tips') {
      loadInterviewTips();
    }
  }, [selectedCategory, user, activeTab]);

  const loadUserData = async () => {
    setLoading(true);
    try {
      // Load interview questions
      const questionsResponse = await companyResearchService.getInterviewQuestions();
      setInterviewQuestions(questionsResponse.results || []);

      // Load practice sessions
      const sessionsResponse = await companyResearchService.getPracticeSessions();
      setPracticeSessions(sessionsResponse.results || []);

      // Load interview resources
      const resourcesResponse = await companyResearchService.getInterviewResources();
      setResources(resourcesResponse.results || resourcesResponse || []);
    } catch (err) {
      console.error('Error loading user data:', err);
      setError('Failed to load your interview preparation data');
    } finally {
      setLoading(false);
    }
  };

  const loadInterviewTips = async () => {
    try {
      const tipsResponse = await companyResearchService.getInterviewTips(selectedCategory);
      setInterviewTips(tipsResponse.results || tipsResponse || []);
    } catch (err) {
      console.error('Error loading interview tips:', err);
      setError('Failed to load interview tips');
    }
  };

  const handleGenerateQuestions = async () => {
    setLoading(true);
    try {
      const questions = await companyResearchService.generateInterviewQuestions(selectedCategory, 'medium');
      setInterviewQuestions(prev => [...prev, ...questions]);
      setError(null);
    } catch (err) {
      console.error('Error generating questions:', err);
      setError('Failed to generate interview questions');
    } finally {
      setLoading(false);
    }
  };

  const handleStartPractice = async (sessionType) => {
    setLoading(true);
    try {
      const session = await companyResearchService.startPracticeSession(sessionType);
      setPracticeSessions(prev => [session, ...prev]);
      setError(null);
      // Could redirect to practice session page here
    } catch (err) {
      console.error('Error starting practice session:', err);
      setError('Failed to start practice session');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="interview-prep-container">
      <div className="interview-prep-header">
        <h1>Interview Preparation</h1>
        <p>Get ready for your next interview with our comprehensive resources</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="interview-prep-content">
        <div className="interview-tabs">
          <button
            className={activeTab === 'tips' ? 'active' : ''}
            onClick={() => setActiveTab('tips')}
          >
            Interview Tips
          </button>
          <button
            className={activeTab === 'questions' ? 'active' : ''}
            onClick={() => setActiveTab('questions')}
          >
            Questions Bank
          </button>
          <button
            className={activeTab === 'practice' ? 'active' : ''}
            onClick={() => setActiveTab('practice')}
          >
            Practice Sessions
          </button>
          <button
            className={activeTab === 'resources' ? 'active' : ''}
            onClick={() => setActiveTab('resources')}
          >
            Resources
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'tips' && (
            <div className="tips-section">
              <div className="category-selector">
                <button
                  className={selectedCategory === 'general' ? 'active' : ''}
                  onClick={() => setSelectedCategory('general')}
                >
                  General
                </button>
                <button
                  className={selectedCategory === 'technical' ? 'active' : ''}
                  onClick={() => setSelectedCategory('technical')}
                >
                  Technical
                </button>
                <button
                  className={selectedCategory === 'behavioral' ? 'active' : ''}
                  onClick={() => setSelectedCategory('behavioral')}
                >
                  Behavioral
                </button>
              </div>

              <div className="tips-list">
                {interviewTips.length > 0 ? (
                  interviewTips
                    .filter(tip => tip.category === selectedCategory)
                    .map((tip) => (
                      <div key={tip.id} className="tip-card">
                        <h3>{tip.title}</h3>
                        <p>{tip.content}</p>
                        {tip.priority && (
                          <span className={`priority priority-${tip.priority}`}>
                            {tip.priority} priority
                          </span>
                        )}
                      </div>
                    ))
                ) : (
                  <div className="no-tips">
                    <p>No interview tips available for {selectedCategory} category yet.</p>
                    <p>Check back later for personalized tips!</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'questions' && (
            <div className="questions-section">
              <div className="questions-header">
                <div className="category-selector">
                  <button
                    className={selectedCategory === 'general' ? 'active' : ''}
                    onClick={() => setSelectedCategory('general')}
                  >
                    General
                  </button>
                  <button
                    className={selectedCategory === 'technical' ? 'active' : ''}
                    onClick={() => setSelectedCategory('technical')}
                  >
                    Technical
                  </button>
                  <button
                    className={selectedCategory === 'behavioral' ? 'active' : ''}
                    onClick={() => setSelectedCategory('behavioral')}
                  >
                    Behavioral
                  </button>
                </div>
                
                {user && (
                  <button 
                    className="generate-questions-btn"
                    onClick={handleGenerateQuestions}
                    disabled={loading}
                  >
                    {loading ? 'Generating...' : `Generate ${selectedCategory} Questions`}
                  </button>
                )}
              </div>

              <div className="questions-list">
                {interviewQuestions.length > 0 ? (
                  interviewQuestions
                    .filter(q => q.question_type === selectedCategory)
                    .map((question) => (
                      <div key={question.id} className="question-card">
                        <h3>{question.question_text}</h3>
                        {question.sample_answer && (
                          <p>{question.sample_answer}</p>
                        )}
                        {question.answer_framework && (
                          <div className="answer-framework">
                            <strong>Framework:</strong> {question.answer_framework}
                          </div>
                        )}
                        <div className="question-meta">
                          <span className="question-type">
                            {question.is_generated ? 'AI Generated' : 'Standard'}
                          </span>
                          <span className="difficulty">{question.difficulty_display}</span>
                          {question.times_used > 0 && (
                            <span className="usage">Used {question.times_used} times</span>
                          )}
                        </div>
                      </div>
                    ))
                ) : (
                  <div className="no-questions">
                    <p>No {selectedCategory} questions available yet.</p>
                    <p>Click "Generate {selectedCategory} Questions" to get personalized questions!</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'practice' && (
            <div className="practice-section">
              <div className="practice-header">
                <h2>Practice Sessions</h2>
                <div className="practice-actions">
                  <button 
                    className="start-practice-btn"
                    onClick={() => handleStartPractice('mock_interview')}
                    disabled={loading}
                  >
                    Start Mock Interview
                  </button>
                  <button 
                    className="start-practice-btn"
                    onClick={() => handleStartPractice('question_practice')}
                    disabled={loading}
                  >
                    Practice Questions
                  </button>
                </div>
              </div>

              <div className="sessions-list">
                {practiceSessions.length > 0 ? (
                  practiceSessions.map((session) => (
                    <div key={session.id} className="session-card">
                      <div className="session-header">
                        <h3>{session.session_type_display}</h3>
                        <span className={`status ${session.completion_status}`}>
                          {session.completion_status_display}
                        </span>
                      </div>
                      
                      <div className="session-details">
                        <div className="session-stat">
                          <strong>Duration:</strong> {session.duration_minutes} minutes
                        </div>
                        <div className="session-stat">
                          <strong>Questions:</strong> {session.questions_attempted}
                        </div>
                        {session.self_rating && (
                          <div className="session-stat">
                            <strong>Self Rating:</strong> {session.self_rating}/5
                          </div>
                        )}
                      </div>

                      {session.notes && (
                        <div className="session-notes">
                          <strong>Notes:</strong> {session.notes}
                        </div>
                      )}

                      <div className="session-date">
                        {new Date(session.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="no-sessions">
                    <p>No practice sessions yet. Start your first session above!</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'resources' && (
            <div className="resources-section">
              <div className="resources-list">
                {resources.length > 0 ? (
                  resources.map((resource) => (
                    <div key={resource.id} className="resource-card">
                      <div className="resource-type">{resource.resource_type}</div>
                      <h3>{resource.title}</h3>
                      <p>{resource.description}</p>
                      {resource.url && (
                        <a href={resource.url} className="resource-link" target="_blank" rel="noopener noreferrer">
                          View Resource
                        </a>
                      )}
                      {resource.file_url && (
                        <a href={resource.file_url} className="resource-link" target="_blank" rel="noopener noreferrer">
                          Download Resource
                        </a>
                      )}
                      <div className="resource-meta">
                        {resource.category && (
                          <span className="resource-category">{resource.category}</span>
                        )}
                        {resource.difficulty && (
                          <span className="resource-difficulty">{resource.difficulty}</span>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="no-resources">
                    <h3>No resources available yet</h3>
                    <p>Interview preparation resources will be added soon!</p>
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

export default InterviewPrep; 