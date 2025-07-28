import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import companyResearchService from '../services/companyResearchService';
import './InterviewPrep.css';

const InterviewPrep = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('tips');
  const [selectedCategory, setSelectedCategory] = useState('company_research');
  const [selectedQuestionCategory, setSelectedQuestionCategory] = useState('behavioral');
  const [interviewQuestions, setInterviewQuestions] = useState([]);
  const [interviewTips, setInterviewTips] = useState([]);
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
      // Structured Question Bank - Three Main Categories
      const mockQuestions = [
        // Behavioral Questions
        {
          id: 'b1',
          question_text: 'Tell me about a time when you had to work with a difficult team member.',
          question_type: 'behavioral',
          answer_points: 'Key points: 1) Specific situation and conflict details 2) Your listening and understanding efforts 3) Finding common ground approach 4) Final solution and positive outcomes',
          star_guidance: 'Situation: Team background and conflict origin; Task: Your role and objectives; Action: Communication, understanding, coordination steps; Result: Positive outcomes after conflict resolution',
          common_mistakes: 'Avoid: Criticizing team members, only describing problems without solutions, lacking specific details'
        },
        {
          id: 'b2',
          question_text: 'Describe a project where you faced a tight deadline.',
          question_type: 'behavioral',
          answer_points: 'Key points: 1) Project background and time pressure 2) Priority assessment and task breakdown 3) Resource coordination and team communication 4) Results delivery and lessons learned',
          star_guidance: 'Situation: Project urgency and importance; Task: Your specific responsibilities; Action: Time management, team coordination, efficiency improvements; Result: Project outcomes and personal growth',
          common_mistakes: 'Avoid: Emphasizing overtime work over smart work, only mentioning difficulties without solutions'
        },
        {
          id: 'b3',
          question_text: 'Share an experience where you had to learn a new skill or knowledge area.',
          question_type: 'behavioral',
          answer_points: 'Key points: 1) Learning motivation and background 2) Learning methods and resources 3) Practical application and feedback 4) Learning outcomes and value demonstration',
          star_guidance: 'Situation: Why this skill was needed; Task: Learning goals and requirements; Action: Learning plan, resource acquisition, practice process; Result: Skill mastery level and practical application',
          common_mistakes: 'Avoid: Choosing overly simple or work-unrelated learning content, only describing process without results'
        },
        {
          id: 'b4',
          question_text: 'Tell me about a time when you had to influence or persuade someone.',
          question_type: 'behavioral',
          answer_points: 'Key points: 1) Background and necessity 2) Other party\'s concerns and objections 3) Communication strategy and persuasion logic 4) Final results and relationship impact',
          star_guidance: 'Situation: Background requiring persuasion; Task: Your goals and their position; Action: Listen, understand, find common ground, gradual persuasion; Result: Final outcome and relationship effect',
          common_mistakes: 'Avoid: Using forceful or manipulative approaches, ignoring the other party\'s feelings and needs'
        },
        
        // Technical Questions
        {
          id: 't1',
          question_text: 'Describe a technical project you led, including technology choices and architecture decisions.',
          question_type: 'technical',
          answer_points: 'Key points: 1) Project background and technical requirements 2) Technology comparison and selection rationale 3) Architecture design and key decisions 4) Implementation challenges and solutions',
          star_guidance: 'Non-linear structure: Project overview → Technical architecture → Key implementation → Results and reflection, emphasizing technical judgment',
          common_mistakes: 'Avoid: Excessive technical details while ignoring business value, only saying what was done without explaining why'
        },
        {
          id: 't2',
          question_text: 'How do you handle system performance issues? Please provide a specific example.',
          question_type: 'technical',
          answer_points: 'Key points: 1) Performance issue identification and analysis methods 2) Common optimization strategies (caching, indexing, architecture optimization) 3) Monitoring and measurement approaches 4) Specific cases and results',
          star_guidance: 'Problem analysis → Solution design → Implementation process → Effect verification, demonstrating systematic thinking and problem-solving ability',
          common_mistakes: 'Avoid: Only theoretical discussion without practical examples, ignoring business impact and user experience'
        },
        {
          id: 't3',
          question_text: 'How do you ensure code quality? How do you promote best practices in your team?',
          question_type: 'technical',
          answer_points: 'Key points: 1) Basic practices like code review, unit testing, documentation 2) Team standards and toolchain 3) Technical sharing and knowledge transfer 4) Continuous improvement and effectiveness measurement',
          star_guidance: 'Current state analysis → Improvement plan → Implementation process → Effect validation, showing leadership and team influence',
          common_mistakes: 'Avoid: Only considering personal experience without team context, lacking specific measures and results'
        },
        {
          id: 't4',
          question_text: 'Describe a time when you had to learn a new technology or framework to solve a problem.',
          question_type: 'technical',
          answer_points: 'Key points: 1) Problem background and technology selection reasons 2) Learning process and methods 3) Practical application and lessons learned 4) Technical outcomes and business value',
          star_guidance: 'Problem identification → Technology research → Learning practice → Outcome delivery, demonstrating learning ability and technical awareness',
          common_mistakes: 'Avoid: Only describing learning process without application results, choosing overly simple technical examples'
        },
        
        // Culture Fit Questions
        {
          id: 'c1',
          question_text: 'Why do you want to work for our company? What do you know about us?',
          question_type: 'culture_fit',
          answer_points: 'Key points: 1) Understanding of company business and mission 2) Alignment with company culture and values 3) Career development fit 4) Value you can bring to the company',
          star_guidance: 'Non-standard structure: Company attractions → Personal match → Value contribution → Future development, showing rational choice and thorough research',
          common_mistakes: 'Avoid: Generic responses, only focusing on salary and benefits, showing lack of business understanding'
        },
        {
          id: 'c2',
          question_text: 'What is your ideal work environment and team atmosphere?',
          question_type: 'culture_fit',
          answer_points: 'Key points: 1) Work style preferences (collaboration, independence, communication style) 2) Learning and growth opportunities 3) Team culture expectations 4) Match with target company culture',
          star_guidance: 'Structured response: Work style → Team collaboration → Growth opportunities → Value alignment, showing mature thinking about work environment',
          common_mistakes: 'Avoid: Overly specific requirements (like must be remote work), negative comments about previous company environment'
        },
        {
          id: 'c3',
          question_text: 'What are your career goals? Where do you see yourself in 5 years?',
          question_type: 'culture_fit',
          answer_points: 'Key points: 1) Short-term goals and skill development plans 2) Medium-term career direction and growth path 3) Alignment with company development 4) Long-term commitment to industry and field',
          star_guidance: 'Progressive structure: Present → Short-term (1-2 years) → Medium-term (3-5 years) → Long-term vision, showing clear goals and planning ability',
          common_mistakes: 'Avoid: Vague or unrealistic goals, only considering personal development without company value'
        },
        {
          id: 'c4',
          question_text: 'What motivates you most in your work?',
          question_type: 'culture_fit',
          answer_points: 'Key points: 1) Specific work content or challenges 2) Team collaboration and sense of achievement 3) Learning growth and skill improvement 4) Impact on industry and users',
          star_guidance: 'Intrinsic motivation analysis: Work content → Team environment → Growth opportunities → Value realization, showing deep understanding of work',
          common_mistakes: 'Avoid: Only mentioning salary or promotion opportunities, overly generic answers, content not matching target position'
        }
      ];
      setInterviewQuestions(mockQuestions);
    } catch (err) {
      console.error('Error loading user data:', err);
      setError('Failed to load your interview preparation data');
    } finally {
      setLoading(false);
    }
  };

  const loadInterviewTips = async () => {
    try {
      // Pre-Interview Preparation - Practical Guidance
      const mockTips = [
        {
          id: '1',
          title: 'Company Research - 3-Step Method',
          content: 'Step 1: Visit company website and record mission, values, recent news; Step 2: Check LinkedIn for team backgrounds and company culture; Step 3: Prepare 2-3 research-based questions like "I saw the company recently launched X product, how does this impact the team?"\n\nCommon mistake: Only reading job postings without understanding the business and culture.',
          category: 'company_research',
          priority: 'high'
        },
        {
          id: '2',
          title: 'Personal Experience Organization - STAR Story Bank',
          content: 'Prepare 3-5 core stories: 1 successful teamwork example, 1 problem-solving experience, 1 learning new skills case, 1 handling challenges situation, 1 leadership/influence experience.\n\nStructure each story using STAR format: Situation (20s) + Task (10s) + Action (60s) + Result (30s).\n\nAvoid: Overly complex stories or those unrelated to the position.',
          category: 'story_preparation',
          priority: 'high'
        },
        {
          id: '3',
          title: 'Question Preparation Checklist - Two-Way Preparation',
          content: 'Must-prepare answers: "Tell me about yourself" (30-second elevator pitch), "Why choose our company", "What are your strengths", "Career goals".\n\nPrepare 5 questions for interviewer: team collaboration style, growth support for new hires, company future direction, work challenges, team culture.\n\nEmergency plan: Framework for unexpected questions - acknowledge unknown + demonstrate learning ability + ask for guidance.',
          category: 'question_prep',
          priority: 'high'
        },
        {
          id: '4',
          title: 'Resume Highlights - Match Analysis',
          content: 'Compare job description with your resume, highlight matching skills and experiences, prepare specific examples as proof.\n\nRefine 3-5 core achievements with quantified results: "Optimized system performance by 30%", "Led 5-person team to complete project".\n\nPrepare to explain every project and work experience on your resume, emphasizing your specific contributions and skills learned.',
          category: 'resume_prep',
          priority: 'medium'
        },
        {
          id: '5',
          title: 'Mental and Physical Preparation - Interview Day',
          content: 'Night before: Confirm interview location and route, prepare all materials, sleep early for good mental state.\n\nDay of: Arrive 30 minutes early, leave time for unexpected situations; bring resume copies, notebook, pen; turn off phone notifications.\n\nMental adjustment: Take 3 deep breaths, review key points, treat interview as mutual understanding opportunity, not an exam.',
          category: 'day_preparation',
          priority: 'medium'
        },
        {
          id: '6',
          title: 'Industry and Position Deep Understanding',
          content: 'Research industry trends and challenges, understand this position\'s role and importance in the company.\n\nPrepare to discuss: your views on industry development, main challenges facing this position, unique value you can bring.\n\nFollow competitors and market dynamics to show your understanding of the entire industry ecosystem.',
          category: 'industry_knowledge',
          priority: 'medium'
        }
      ];
      setInterviewTips(mockTips);
    } catch (err) {
      console.error('Error loading interview tips:', err);
      setError('Failed to load interview tips');
    }
  };

  const handleGenerateQuestions = async () => {
    setLoading(true);
    try {
      const questions = await companyResearchService.generateInterviewQuestions(selectedQuestionCategory, 'medium');
      setInterviewQuestions(prev => [...prev, ...questions]);
      setError(null);
    } catch (err) {
      console.error('Error generating questions:', err);
      setError('Failed to generate interview questions');
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
        </div>

        <div className="tab-content">
          {activeTab === 'tips' && (
            <div className="tips-section">
              <div className="category-selector">
                <button
                  className={selectedCategory === 'company_research' ? 'active' : ''}
                  onClick={() => setSelectedCategory('company_research')}
                >
                  Company Research
                </button>
                <button
                  className={selectedCategory === 'story_preparation' ? 'active' : ''}
                  onClick={() => setSelectedCategory('story_preparation')}
                >
                  Story Preparation
                </button>
                <button
                  className={selectedCategory === 'question_prep' ? 'active' : ''}
                  onClick={() => setSelectedCategory('question_prep')}
                >
                  Question Prep
                </button>
                <button
                  className={selectedCategory === 'resume_prep' ? 'active' : ''}
                  onClick={() => setSelectedCategory('resume_prep')}
                >
                  Resume Prep
                </button>
                <button
                  className={selectedCategory === 'day_preparation' ? 'active' : ''}
                  onClick={() => setSelectedCategory('day_preparation')}
                >
                  Day Preparation
                </button>
                <button
                  className={selectedCategory === 'industry_knowledge' ? 'active' : ''}
                  onClick={() => setSelectedCategory('industry_knowledge')}
                >
                  Industry Knowledge
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
                    className={selectedQuestionCategory === 'behavioral' ? 'active' : ''}
                    onClick={() => setSelectedQuestionCategory('behavioral')}
                  >
                    Behavioral Questions
                  </button>
                  <button
                    className={selectedQuestionCategory === 'technical' ? 'active' : ''}
                    onClick={() => setSelectedQuestionCategory('technical')}
                  >
                    Technical Questions
                  </button>
                  <button
                    className={selectedQuestionCategory === 'culture_fit' ? 'active' : ''}
                    onClick={() => setSelectedQuestionCategory('culture_fit')}
                  >
                    Culture Fit
                  </button>
                </div>
                
                {user && (
                  <button 
                    className="generate-questions-btn"
                    onClick={handleGenerateQuestions}
                    disabled={loading}
                  >
                    {loading ? 'Generating...' : `Generate ${selectedQuestionCategory === 'behavioral' ? 'Behavioral' : selectedQuestionCategory === 'technical' ? 'Technical' : 'Culture Fit'} Questions`}
                  </button>
                )}
              </div>

              <div className="questions-list">
                {interviewQuestions.length > 0 ? (
                  interviewQuestions
                    .filter(q => q.question_type === selectedQuestionCategory)
                    .map((question) => (
                      <div key={question.id} className="question-card">
                        <h3>{question.question_text}</h3>
                        
                        {question.answer_points && (
                          <div className="answer-points">
                            <h4>🎯 Answer Points:</h4>
                            <p>{question.answer_points}</p>
                          </div>
                        )}
                        
                        {question.star_guidance && (
                          <div className="star-guidance">
                            <h4>⭐ STAR Framework Guidance:</h4>
                            <p>{question.star_guidance}</p>
                          </div>
                        )}
                        
                        {question.common_mistakes && (
                          <div className="common-mistakes">
                            <h4>⚠️ Common Mistakes:</h4>
                            <p>{question.common_mistakes}</p>
                          </div>
                        )}
                      </div>
                    ))
                ) : (
                  <div className="no-questions">
                    <p>No {selectedQuestionCategory === 'behavioral' ? 'behavioral' : selectedQuestionCategory === 'technical' ? 'technical' : 'culture fit'} questions available yet.</p>
                    <p>Click "Generate {selectedQuestionCategory === 'behavioral' ? 'Behavioral' : selectedQuestionCategory === 'technical' ? 'Technical' : 'Culture Fit'} Questions" to get personalized questions!</p>
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