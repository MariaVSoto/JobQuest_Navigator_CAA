import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import companyResearchService from '../services/companyResearchService';
import './InterviewPrepEnhanced.css';

// Enhanced Interview Preparation with improved UX
const InterviewPrepEnhanced = () => {
  const { user } = useAuth();
  
  // Navigation state
  const [activeSection, setActiveSection] = useState('dashboard');
  const [selectedCategory, setSelectedCategory] = useState('company_research');
  const [selectedQuestionCategory, setSelectedQuestionCategory] = useState('behavioral');
  
  // Data state
  const [interviewQuestions, setInterviewQuestions] = useState([]);
  const [interviewTips, setInterviewTips] = useState([]);
  const [userProgress, setUserProgress] = useState({
    completedQuestions: new Set(),
    bookmarkedQuestions: new Set(),
    practiceTime: 0,
    streakDays: 0
  });
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [practiceMode, setPracticeMode] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [practiceTimer, setPracticeTimer] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [showAIFeedback, setShowAIFeedback] = useState(false);
  
  // Refs
  const timerRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Load data on component mount
  useEffect(() => {
    if (user) {
      loadInitialData();
      loadUserProgress();
    }
  }, [user]);

  // Practice timer effect
  useEffect(() => {
    if (practiceMode && practiceTimer > 0) {
      timerRef.current = setInterval(() => {
        setPracticeTimer(prev => {
          if (prev <= 1) {
            handleTimerComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }

    return () => clearInterval(timerRef.current);
  }, [practiceMode, practiceTimer]);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      // Enhanced question bank with more structure
      const enhancedQuestions = [
        // Behavioral Questions - STAR Method focused
        {
          id: 'b1',
          question_text: 'Tell me about a time when you had to work with a difficult team member.',
          question_type: 'behavioral',
          difficulty: 'medium',
          estimatedTime: 180, // 3 minutes
          tags: ['teamwork', 'conflict-resolution', 'communication'],
          answer_points: 'Key points: 1) Specific situation and conflict details 2) Your listening and understanding efforts 3) Finding common ground approach 4) Final solution and positive outcomes',
          star_guidance: 'Situation: Team background and conflict origin; Task: Your role and objectives; Action: Communication, understanding, coordination steps; Result: Positive outcomes after conflict resolution',
          common_mistakes: 'Avoid: Criticizing team members, only describing problems without solutions, lacking specific details',
          followUpQuestions: [
            'How did you handle similar situations after this experience?',
            'What would you do differently if faced with this situation again?'
          ]
        },
        {
          id: 'b2',
          question_text: 'Describe a project where you faced a tight deadline.',
          question_type: 'behavioral',
          difficulty: 'medium',
          estimatedTime: 180,
          tags: ['time-management', 'pressure', 'prioritization'],
          answer_points: 'Key points: 1) Project background and time pressure 2) Priority assessment and task breakdown 3) Resource coordination and team communication 4) Results delivery and lessons learned',
          star_guidance: 'Situation: Project urgency and importance; Task: Your specific responsibilities; Action: Time management, team coordination, efficiency improvements; Result: Project outcomes and personal growth',
          common_mistakes: 'Avoid: Emphasizing overtime work over smart work, only mentioning difficulties without solutions'
        },
        {
          id: 'b3',
          question_text: 'Share an experience where you had to learn a new skill quickly.',
          question_type: 'behavioral',
          difficulty: 'easy',
          estimatedTime: 150,
          tags: ['learning', 'adaptability', 'growth'],
          answer_points: 'Key points: 1) Learning motivation and background 2) Learning methods and resources 3) Practical application and feedback 4) Learning outcomes and value demonstration',
          star_guidance: 'Situation: Why this skill was needed; Task: Learning goals and requirements; Action: Learning plan, resource acquisition, practice process; Result: Skill mastery level and practical application',
          common_mistakes: 'Avoid: Choosing overly simple or work-unrelated learning content, only describing process without results'
        },

        // Technical Questions - Problem-solving focused
        {
          id: 't1',
          question_text: 'Walk me through how you would design a scalable web application.',
          question_type: 'technical',
          difficulty: 'hard',
          estimatedTime: 300, // 5 minutes
          tags: ['system-design', 'scalability', 'architecture'],
          answer_points: 'Key points: 1) Requirements gathering and constraints 2) High-level architecture and components 3) Database design and data flow 4) Scalability considerations and trade-offs',
          star_guidance: 'Problem understanding → Architecture design → Implementation considerations → Scalability planning',
          common_mistakes: 'Avoid: Jumping to implementation details without understanding requirements, ignoring scalability from the start'
        },
        {
          id: 't2',
          question_text: 'How would you debug a performance issue in production?',
          question_type: 'technical',
          difficulty: 'medium',
          estimatedTime: 240,
          tags: ['debugging', 'performance', 'monitoring'],
          answer_points: 'Key points: 1) Initial assessment and data gathering 2) Monitoring and profiling tools 3) Systematic investigation approach 4) Solution implementation and validation',
          star_guidance: 'Problem identification → Data collection → Root cause analysis → Solution implementation',
          common_mistakes: 'Avoid: Making changes without proper investigation, not considering user impact'
        },

        // Culture Fit Questions - Values alignment
        {
          id: 'c1',
          question_text: 'Why do you want to work for our company?',
          question_type: 'culture_fit',
          difficulty: 'medium',
          estimatedTime: 120,
          tags: ['motivation', 'research', 'alignment'],
          answer_points: 'Key points: 1) Specific company research and understanding 2) Alignment with personal values and goals 3) Unique value you bring 4) Long-term commitment and growth',
          star_guidance: 'Company research → Personal alignment → Value proposition → Future vision',
          common_mistakes: 'Avoid: Generic responses, only focusing on salary/benefits, showing lack of company knowledge'
        },
        {
          id: 'c2',
          question_text: 'What are your career goals for the next 5 years?',
          question_type: 'culture_fit',
          difficulty: 'easy',
          estimatedTime: 150,
          tags: ['career-planning', 'ambition', 'growth'],
          answer_points: 'Key points: 1) Short-term skill development goals 2) Medium-term career progression 3) Alignment with company growth 4) Long-term industry impact',
          star_guidance: 'Current state → 1-2 year goals → 3-5 year vision → Long-term aspirations',
          common_mistakes: 'Avoid: Vague or unrealistic goals, not connecting to the specific role/company'
        }
      ];

      setInterviewQuestions(enhancedQuestions);
      await loadInterviewTips();
    } catch (err) {
      console.error('Error loading initial data:', err);
      setError('Failed to load interview preparation data');
    } finally {
      setLoading(false);
    }
  };

  const loadInterviewTips = async () => {
    try {
      const enhancedTips = [
        {
          id: '1',
          title: 'Company Research Deep Dive',
          content: 'Go beyond the website: Check recent news, LinkedIn posts, employee reviews on Glassdoor, and industry reports. Create a company profile document with mission, values, recent achievements, and challenges.',
          category: 'company_research',
          priority: 'high',
          timeToRead: 5,
          actionItems: [
            'Visit company website and social media',
            'Read recent news and press releases',
            'Check employee reviews and culture insights',
            'Prepare 3-5 thoughtful questions about the company'
          ]
        },
        {
          id: '2',
          title: 'STAR Method Mastery',
          content: 'Prepare 5-7 compelling stories using STAR framework. Each story should be 2-3 minutes long and demonstrate different skills. Practice timing and smooth transitions between sections.',
          category: 'story_preparation',
          priority: 'high',
          timeToRead: 8,
          actionItems: [
            'Choose diverse examples showcasing different skills',
            'Write out each story in STAR format',
            'Practice timing (30s Situation, 20s Task, 90s Action, 20s Result)',
            'Prepare for follow-up questions on each story'
          ]
        },
        {
          id: '3',
          title: 'Technical Interview Strategy',
          content: 'For technical roles, prepare system design basics, coding problems, and be ready to discuss your past projects in detail. Focus on your thought process and problem-solving approach.',
          category: 'technical_prep',
          priority: 'high',
          timeToRead: 12,
          actionItems: [
            'Review fundamental algorithms and data structures',
            'Practice explaining technical concepts clearly',
            'Prepare detailed project discussions',
            'Practice coding on whiteboard or shared screen'
          ]
        },
        {
          id: '4',
          title: 'Question Bank Strategy',
          content: 'Prepare intelligent questions that show your interest and research. Focus on role-specific challenges, team dynamics, and company culture.',
          category: 'question_prep',
          priority: 'medium',
          timeToRead: 6,
          actionItems: [
            'Prepare 5-7 thoughtful questions',
            'Mix questions about role, team, and company',
            'Avoid questions easily answered by website research',
            'Prepare follow-up questions based on their responses'
          ]
        }
      ];

      setInterviewTips(enhancedTips);
    } catch (err) {
      console.error('Error loading interview tips:', err);
    }
  };

  const loadUserProgress = () => {
    // Load from localStorage or API
    const savedProgress = localStorage.getItem('interviewPrepProgress');
    if (savedProgress) {
      const parsed = JSON.parse(savedProgress);
      setUserProgress({
        ...parsed,
        completedQuestions: new Set(parsed.completedQuestions),
        bookmarkedQuestions: new Set(parsed.bookmarkedQuestions)
      });
    }
  };

  const saveUserProgress = useCallback((newProgress) => {
    const progressToSave = {
      ...newProgress,
      completedQuestions: Array.from(newProgress.completedQuestions),
      bookmarkedQuestions: Array.from(newProgress.bookmarkedQuestions)
    };
    localStorage.setItem('interviewPrepProgress', JSON.stringify(progressToSave));
    setUserProgress(newProgress);
  }, []);

  // Practice mode functions
  const startPracticeMode = (questionIndex = 0) => {
    const question = filteredQuestions[questionIndex];
    setPracticeMode(true);
    setCurrentQuestionIndex(questionIndex);
    setPracticeTimer(question?.estimatedTime || 180);
    setActiveSection('practice');
  };

  const exitPracticeMode = () => {
    setPracticeMode(false);
    setPracticeTimer(0);
    setIsRecording(false);
    setActiveSection('questions');
  };

  const handleTimerComplete = () => {
    // Auto-stop recording if active
    if (isRecording) {
      stopRecording();
    }
    setShowAIFeedback(true);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to start recording. Please check microphone permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        // Here you could send the audio to an API for analysis
        console.log('Recording completed:', audioBlob);
      };
    }
  };

  const markQuestionComplete = (questionId) => {
    const newProgress = {
      ...userProgress,
      completedQuestions: new Set([...userProgress.completedQuestions, questionId])
    };
    saveUserProgress(newProgress);
  };

  const toggleBookmark = (questionId) => {
    const newBookmarks = new Set(userProgress.bookmarkedQuestions);
    if (newBookmarks.has(questionId)) {
      newBookmarks.delete(questionId);
    } else {
      newBookmarks.add(questionId);
    }
    
    const newProgress = {
      ...userProgress,
      bookmarkedQuestions: newBookmarks
    };
    saveUserProgress(newProgress);
  };

  // Filter functions
  const filteredQuestions = interviewQuestions.filter(q => {
    const matchesCategory = q.question_type === selectedQuestionCategory;
    const matchesSearch = searchQuery === '' || 
      q.question_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      q.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const filteredTips = interviewTips.filter(tip => tip.category === selectedCategory);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressStats = () => {
    const totalQuestions = interviewQuestions.length;
    const completedCount = userProgress.completedQuestions.size;
    const completionRate = totalQuestions > 0 ? (completedCount / totalQuestions) * 100 : 0;
    
    return {
      totalQuestions,
      completedCount,
      completionRate: Math.round(completionRate),
      bookmarkedCount: userProgress.bookmarkedQuestions.size,
      practiceTime: userProgress.practiceTime,
      streakDays: userProgress.streakDays
    };
  };

  // Render functions for different sections
  const renderDashboard = () => {
    const stats = getProgressStats();
    
    return (
      <div className="interview-dashboard">
        <div className="dashboard-header">
          <h2>Your Interview Preparation Journey</h2>
          <p>Track your progress and improve your interview skills</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{stats.completedCount}</div>
            <div className="stat-label">Questions Practiced</div>
            <div className="stat-progress">
              <div 
                className="stat-progress-bar" 
                style={{ width: `${stats.completionRate}%` }}
              ></div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.bookmarkedCount}</div>
            <div className="stat-label">Bookmarked Questions</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{Math.floor(stats.practiceTime / 60)}</div>
            <div className="stat-label">Practice Hours</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.streakDays}</div>
            <div className="stat-label">Day Streak</div>
          </div>
        </div>

        <div className="quick-actions">
          <h3>Quick Actions</h3>
          <div className="action-buttons">
            <button 
              className="action-btn primary"
              onClick={() => startPracticeMode(0)}
              disabled={filteredQuestions.length === 0}
            >
              🎯 Start Practice Session
            </button>
            <button 
              className="action-btn secondary"
              onClick={() => setActiveSection('questions')}
            >
              📝 Browse Questions
            </button>
            <button 
              className="action-btn secondary"
              onClick={() => setActiveSection('tips')}
            >
              💡 Study Tips
            </button>
            <button 
              className="action-btn secondary"
              onClick={() => setActiveSection('bookmarks')}
            >
              ⭐ My Bookmarks
            </button>
          </div>
        </div>

        <div className="recent-activity">
          <h3>Continue Where You Left Off</h3>
          <div className="activity-list">
            {filteredQuestions.slice(0, 3).map((question, index) => (
              <div key={question.id} className="activity-item">
                <div className="activity-content">
                  <h4>{question.question_text}</h4>
                  <div className="activity-meta">
                    <span className={`difficulty difficulty-${question.difficulty}`}>
                      {question.difficulty}
                    </span>
                    <span className="estimated-time">
                      ~{Math.floor(question.estimatedTime / 60)} min
                    </span>
                  </div>
                </div>
                <button 
                  className="practice-btn"
                  onClick={() => startPracticeMode(index)}
                >
                  Practice
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderQuestionBank = () => (
    <div className="questions-section">
      <div className="questions-header">
        <div className="questions-controls">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search questions or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="category-filters">
            {['behavioral', 'technical', 'culture_fit'].map(category => (
              <button
                key={category}
                className={`filter-btn ${selectedQuestionCategory === category ? 'active' : ''}`}
                onClick={() => setSelectedQuestionCategory(category)}
              >
                {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="questions-list">
        {filteredQuestions.length > 0 ? (
          filteredQuestions.map((question, index) => (
            <div key={question.id} className="question-card enhanced">
              <div className="question-header">
                <div className="question-meta">
                  <span className={`difficulty difficulty-${question.difficulty}`}>
                    {question.difficulty}
                  </span>
                  <span className="estimated-time">
                    ~{Math.floor(question.estimatedTime / 60)} min
                  </span>
                  <div className="question-tags">
                    {question.tags.slice(0, 3).map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                </div>
                
                <div className="question-actions">
                  <button
                    className={`bookmark-btn ${userProgress.bookmarkedQuestions.has(question.id) ? 'bookmarked' : ''}`}
                    onClick={() => toggleBookmark(question.id)}
                    title="Bookmark question"
                  >
                    ⭐
                  </button>
                  <button
                    className="practice-btn"
                    onClick={() => startPracticeMode(index)}
                  >
                    Practice
                  </button>
                </div>
              </div>

              <h3 className="question-text">{question.question_text}</h3>
              
              <div className="question-details">
                <div className="answer-framework">
                  <h4>🎯 Key Points to Cover:</h4>
                  <p>{question.answer_points}</p>
                </div>
                
                <div className="star-framework">
                  <h4>⭐ STAR Framework Guidance:</h4>
                  <p>{question.star_guidance}</p>
                </div>
                
                <div className="common-pitfalls">
                  <h4>⚠️ Common Mistakes to Avoid:</h4>
                  <p>{question.common_mistakes}</p>
                </div>
              </div>
              
              {userProgress.completedQuestions.has(question.id) && (
                <div className="completion-badge">
                  ✅ Completed
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="no-questions">
            <p>No questions found matching your criteria.</p>
            <p>Try adjusting your search or category filters.</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderPracticeMode = () => {
    const currentQuestion = filteredQuestions[currentQuestionIndex];
    if (!currentQuestion) return null;

    return (
      <div className="practice-mode">
        <div className="practice-header">
          <div className="practice-info">
            <h2>Practice Session</h2>
            <div className="practice-meta">
              Question {currentQuestionIndex + 1} of {filteredQuestions.length}
              <span className="practice-category">
                {currentQuestion.question_type.replace('_', ' ')}
              </span>
            </div>
          </div>
          
          <div className="practice-controls">
            <div className="timer">
              <span className={`timer-display ${practiceTimer <= 30 ? 'warning' : ''}`}>
                {formatTime(practiceTimer)}
              </span>
            </div>
            <button className="exit-practice" onClick={exitPracticeMode}>
              Exit Practice
            </button>
          </div>
        </div>

        <div className="practice-content">
          <div className="question-display">
            <h3>{currentQuestion.question_text}</h3>
            <div className="question-context">
              <span className={`difficulty difficulty-${currentQuestion.difficulty}`}>
                {currentQuestion.difficulty}
              </span>
              <span className="tags">
                {currentQuestion.tags.join(', ')}
              </span>
            </div>
          </div>

          <div className="practice-tools">
            <div className="recording-section">
              <h4>Record Your Answer</h4>
              <div className="recording-controls">
                {!isRecording ? (
                  <button 
                    className="record-btn start"
                    onClick={startRecording}
                  >
                    🎤 Start Recording
                  </button>
                ) : (
                  <button 
                    className="record-btn stop"
                    onClick={stopRecording}
                  >
                    ⏹️ Stop Recording
                  </button>
                )}
                
                {isRecording && (
                  <div className="recording-indicator">
                    <span className="recording-dot"></span>
                    Recording...
                  </div>
                )}
              </div>
            </div>

            <div className="practice-notes">
              <h4>Quick Notes</h4>
              <textarea 
                placeholder="Jot down key points as you practice..."
                rows={4}
                className="notes-input"
              />
            </div>
          </div>

          <div className="practice-guidance">
            <div className="guidance-section">
              <h4>💡 STAR Framework Guide</h4>
              <p>{currentQuestion.star_guidance}</p>
            </div>
            
            <div className="guidance-section">
              <h4>🎯 Key Points to Cover</h4>
              <p>{currentQuestion.answer_points}</p>
            </div>
          </div>
        </div>

        <div className="practice-footer">
          <button 
            className="complete-btn"
            onClick={() => {
              markQuestionComplete(currentQuestion.id);
              if (currentQuestionIndex < filteredQuestions.length - 1) {
                setCurrentQuestionIndex(prev => prev + 1);
                setPracticeTimer(filteredQuestions[currentQuestionIndex + 1]?.estimatedTime || 180);
              } else {
                exitPracticeMode();
              }
            }}
          >
            {currentQuestionIndex < filteredQuestions.length - 1 ? 'Next Question' : 'Complete Session'}
          </button>
        </div>
      </div>
    );
  };

  const renderTipsSection = () => (
    <div className="tips-section">
      <div className="tips-header">
        <h2>Interview Preparation Tips</h2>
        <div className="category-selector">
          {['company_research', 'story_preparation', 'technical_prep', 'question_prep'].map(category => (
            <button
              key={category}
              className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category)}
            >
              {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>
      </div>

      <div className="tips-list">
        {filteredTips.map(tip => (
          <div key={tip.id} className="tip-card enhanced">
            <div className="tip-header">
              <h3>{tip.title}</h3>
              <div className="tip-meta">
                <span className={`priority priority-${tip.priority}`}>
                  {tip.priority} priority
                </span>
                <span className="read-time">
                  {tip.timeToRead} min read
                </span>
              </div>
            </div>
            
            <div className="tip-content">
              <p>{tip.content}</p>
              
              {tip.actionItems && (
                <div className="action-items">
                  <h4>Action Items:</h4>
                  <ul>
                    {tip.actionItems.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="interview-prep-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading your interview preparation materials...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="interview-prep-container enhanced">
      {/* Enhanced Sidebar Navigation */}
      <div className="interview-sidebar">
        <div className="sidebar-header">
          <h2>Interview Prep</h2>
          <div className="progress-indicator">
            <div 
              className="progress-bar" 
              style={{ width: `${getProgressStats().completionRate}%` }}
            ></div>
            <span className="progress-text">
              {getProgressStats().completionRate}% Complete
            </span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeSection === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveSection('dashboard')}
          >
            <span className="nav-icon">📊</span>
            Dashboard
          </button>
          <button
            className={`nav-item ${activeSection === 'questions' ? 'active' : ''}`}
            onClick={() => setActiveSection('questions')}
          >
            <span className="nav-icon">❓</span>
            Question Bank
          </button>
          <button
            className={`nav-item ${activeSection === 'tips' ? 'active' : ''}`}
            onClick={() => setActiveSection('tips')}
          >
            <span className="nav-icon">💡</span>
            Tips & Strategies
          </button>
          <button
            className={`nav-item ${activeSection === 'bookmarks' ? 'active' : ''}`}
            onClick={() => setActiveSection('bookmarks')}
          >
            <span className="nav-icon">⭐</span>
            Bookmarks
            {userProgress.bookmarkedQuestions.size > 0 && (
              <span className="badge">{userProgress.bookmarkedQuestions.size}</span>
            )}
          </button>
          {practiceMode && (
            <button
              className={`nav-item ${activeSection === 'practice' ? 'active' : ''}`}
              onClick={() => setActiveSection('practice')}
            >
              <span className="nav-icon">🎯</span>
              Practice Mode
            </button>
          )}
        </nav>
      </div>

      {/* Main Content Area */}
      <div className="interview-main">
        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            {error}
            <button 
              className="error-close"
              onClick={() => setError(null)}
            >
              ×
            </button>
          </div>
        )}

        {activeSection === 'dashboard' && renderDashboard()}
        {activeSection === 'questions' && renderQuestionBank()}
        {activeSection === 'practice' && practiceMode && renderPracticeMode()}
        {activeSection === 'tips' && renderTipsSection()}
        {activeSection === 'bookmarks' && (
          <div className="bookmarks-section">
            <h2>Bookmarked Questions</h2>
            {userProgress.bookmarkedQuestions.size > 0 ? (
              <div className="questions-list">
                {interviewQuestions
                  .filter(q => userProgress.bookmarkedQuestions.has(q.id))
                  .map((question, index) => (
                    <div key={question.id} className="question-card enhanced bookmarked">
                      {/* Same question card structure as question bank */}
                      <div className="question-header">
                        <div className="question-meta">
                          <span className={`difficulty difficulty-${question.difficulty}`}>
                            {question.difficulty}
                          </span>
                          <span className="estimated-time">
                            ~{Math.floor(question.estimatedTime / 60)} min
                          </span>
                        </div>
                        <div className="question-actions">
                          <button
                            className="bookmark-btn bookmarked"
                            onClick={() => toggleBookmark(question.id)}
                            title="Remove bookmark"
                          >
                            ⭐
                          </button>
                          <button
                            className="practice-btn"
                            onClick={() => startPracticeMode(index)}
                          >
                            Practice
                          </button>
                        </div>
                      </div>
                      <h3>{question.question_text}</h3>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="empty-bookmarks">
                <p>No bookmarked questions yet.</p>
                <p>Star questions from the Question Bank to save them here!</p>
                <button 
                  className="browse-questions-btn"
                  onClick={() => setActiveSection('questions')}
                >
                  Browse Questions
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewPrepEnhanced;