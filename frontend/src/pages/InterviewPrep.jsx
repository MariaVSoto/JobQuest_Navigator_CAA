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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      loadUserData();
    }
  }, [user]);

  const loadUserData = async () => {
    setLoading(true);
    try {
      // Load interview questions
      const questionsResponse = await companyResearchService.getInterviewQuestions();
      setInterviewQuestions(questionsResponse.results || []);

      // Load practice sessions
      const sessionsResponse = await companyResearchService.getPracticeSessions();
      setPracticeSessions(sessionsResponse.results || []);
    } catch (err) {
      console.error('Error loading user data:', err);
      setError('Failed to load your interview preparation data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuestions = async () => {
    setLoading(true);
    try {
      const questions = await companyResearchService.generateInterviewQuestions(
        selectedCategory,
        'medium'
      );
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

  const interviewTips = {
    general: [
      {
        title: "Research the Company",
        content: "Learn about the company's history, mission, values, and recent news. This shows your interest and helps you tailor your responses."
      },
      {
        title: "Practice Common Questions",
        content: "Prepare answers for common interview questions like 'Tell me about yourself' and 'Why do you want to work here?'"
      },
      {
        title: "Dress Appropriately",
        content: "Choose professional attire that matches the company culture. When in doubt, it's better to be slightly overdressed."
      }
    ],
    technical: [
      {
        title: "Review Technical Concepts",
        content: "Brush up on key technical concepts and be prepared to explain your thought process during problem-solving."
      },
      {
        title: "Prepare Your Portfolio",
        content: "Have your projects and code samples ready to discuss. Be prepared to explain your technical decisions."
      },
      {
        title: "Practice Coding",
        content: "Practice coding problems and system design questions. Focus on explaining your approach clearly."
      }
    ],
    behavioral: [
      {
        title: "Use the STAR Method",
        content: "Structure your answers using Situation, Task, Action, and Result to provide clear, concise responses."
      },
      {
        title: "Prepare Examples",
        content: "Have specific examples ready that demonstrate your skills, achievements, and how you handle challenges."
      },
      {
        title: "Show Enthusiasm",
        content: "Express genuine interest in the role and company. Ask thoughtful questions about the position."
      }
    ]
  };

  const commonQuestions = {
    general: [
      {
        question: "Tell me about yourself.",
        answer: "Focus on your professional background, key achievements, and what makes you a good fit for the role."
      },
      {
        question: "Why do you want to work here?",
        answer: "Show your research and explain how your skills and values align with the company's mission."
      },
      {
        question: "Where do you see yourself in 5 years?",
        answer: "Discuss your career goals and how they align with the company's growth opportunities."
      }
    ],
    technical: [
      {
        question: "Explain a technical concept to a non-technical person.",
        answer: "Use analogies and simple language to break down complex concepts."
      },
      {
        question: "How do you handle technical challenges?",
        answer: "Describe your problem-solving process and how you learn from difficult situations."
      },
      {
        question: "What's your approach to learning new technologies?",
        answer: "Explain your learning process and how you stay updated with industry trends."
      }
    ],
    behavioral: [
      {
        question: "Tell me about a time you faced a challenge at work.",
        answer: "Use the STAR method to describe the situation, your actions, and the positive outcome."
      },
      {
        question: "How do you handle conflict in the workplace?",
        answer: "Focus on communication, collaboration, and finding mutually beneficial solutions."
      },
      {
        question: "Describe a successful project you worked on.",
        answer: "Highlight your role, the challenges overcome, and the impact of the project."
      }
    ]
  };

  const resources = [
    {
      title: "Interview Preparation Guide",
      type: "PDF",
      description: "Comprehensive guide covering all aspects of interview preparation",
      link: "#"
    },
    {
      title: "Common Interview Questions",
      type: "PDF",
      description: "List of frequently asked questions with sample answers",
      link: "#"
    },
    {
      title: "Technical Interview Tips",
      type: "Video",
      description: "Video series on preparing for technical interviews",
      link: "#"
    },
    {
      title: "Behavioral Interview Workshop",
      type: "Video",
      description: "Workshop on mastering behavioral interview questions",
      link: "#"
    }
  ];

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
                {interviewTips[selectedCategory].map((tip, index) => (
                  <div key={index} className="tip-card">
                    <h3>{tip.title}</h3>
                    <p>{tip.content}</p>
                  </div>
                ))}
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
                {/* Show static questions */}
                {commonQuestions[selectedCategory].map((item, index) => (
                  <div key={index} className="question-card static">
                    <h3>{item.question}</h3>
                    <p>{item.answer}</p>
                    <span className="question-type">Static</span>
                  </div>
                ))}

                {/* Show generated questions */}
                {interviewQuestions
                  .filter(q => q.question_type === selectedCategory)
                  .map((question) => (
                    <div key={question.id} className="question-card generated">
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
                        <span className="question-type">AI Generated</span>
                        <span className="difficulty">{question.difficulty_display}</span>
                        {question.times_used > 0 && (
                          <span className="usage">Used {question.times_used} times</span>
                        )}
                      </div>
                    </div>
                  ))}
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
                {resources.map((resource, index) => (
                  <div key={index} className="resource-card">
                    <div className="resource-type">{resource.type}</div>
                    <h3>{resource.title}</h3>
                    <p>{resource.description}</p>
                    <a href={resource.link} className="resource-link">
                      View Resource
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterviewPrep; 