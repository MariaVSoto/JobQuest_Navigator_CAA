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
      // 结构化问题库 - 三大类型
      const mockQuestions = [
        // 行为问题 (Behavioral Questions)
        {
          id: 'b1',
          question_text: '请讲述一次你在团队合作中遇到分歧的经历。',
          question_type: 'behavioral',
          answer_points: '回答要点：1)具体情况和分歧内容 2)你的倾听和理解努力 3)寻找共同点的做法 4)最终的解决方案和结果',
          star_guidance: 'Situation:团队背景和分歧原因；Task:你的角色和目标；Action:沟通、理解、协调的具体步骤；Result:分歧解决后的积极成果',
          common_mistakes: '避免：批评团队成员、只描述问题不说解决方案、缺乏具体细节'
        },
        {
          id: 'b2',
          question_text: '描述一个你面临紧急截止日期的项目。',
          question_type: 'behavioral',
          answer_points: '回答要点：1)项目背景和时间压力 2)优先级判断和任务分解 3)资源协调和团队沟通 4)结果交付和经验总结',
          star_guidance: 'Situation:项目紧急程度和重要性；Task:你的具体责任；Action:时间管理、团队协调、效率提升措施；Result:项目成果和个人成长',
          common_mistakes: '避免：强调密集加班而非智能工作、只说困难不说解决方案'
        },
        {
          id: 'b3',
          question_text: '请分享一次你学习新技能或知识的经历。',
          question_type: 'behavioral',
          answer_points: '回答要点：1)学习动机和背景 2)学习方法和资源 3)实践应用和反馈 4)学习成果和价值体现',
          star_guidance: 'Situation:为什么需要学习这项技能；Task:学习目标和要求；Action:学习计划、资源获取、实践过程；Result:技能掌握程度和实际应用',
          common_mistakes: '避免：选择过于简单或与工作无关的学习内容、只说过程不说结果'
        },
        {
          id: 'b4',
          question_text: '讲述一次你需要影响或说服他人的经历。',
          question_type: 'behavioral',
          answer_points: '回答要点：1)背景和必要性 2)对方的关切和须抗 3)沟通策略和说服逻辑 4)最终结果和关系影响',
          star_guidance: 'Situation:需要说服的背景和原因；Task:你的目标和对方的立场；Action:倾听、理解、找共同点、逐步说服；Result:最终结果和双方关系',
          common_mistakes: '避免：使用强制或操纵的方式、忽略对方的感受和需求'
        },
        
        // 技术问题 (Technical Questions)
        {
          id: 't1',
          question_text: '请介绍一个你负责的技术项目，包括技术选型和架构决策。',
          question_type: 'technical',
          answer_points: '回答要点：1)项目背景和技术要求 2)技本方案对比和选择理由 3)架构设计和关键决策 4)实现挑战和解决方案',
          star_guidance: '非线性描述：项目概述→技术架构→关键实现→结果与反思，重点展示技术判断力',
          common_mistakes: '避免：过度技术细节而忽略业务价值、只说做了什么不说为什么这么做'
        },
        {
          id: 't2',
          question_text: '如何处理系统性能问题？请结合具体例子说明。',
          question_type: 'technical',
          answer_points: '回答要点：1)性能问题识别和分析方法 2)常见优化策略(缓存、索引、架构优化) 3)监控和测量方法 4)具体案例和效果',
          star_guidance: '问题分析→解决方案→实现过程→效果验证，体现系统性思维和问题解决能力',
          common_mistakes: '避免：只说理论不说实践、忽略业务影响和用户体验'
        },
        {
          id: 't3',
          question_text: '如何保证代码质量？你在团队中如何推动最佳实践？',
          question_type: 'technical',
          answer_points: '回答要点：1)代码审查、单元测试、文档等基础实践 2)团队规范和工具链 3)技术分享和知识传承 4)持续改进和效果衡量',
          star_guidance: '现状分析→改进方案→推动过程→效果验证，展示领导力和团队影响力',
          common_mistakes: '避免：只按个人经验而不考虑团队现状、缺乏具体措施和效果'
        },
        {
          id: 't4',
          question_text: '描述一次你需要学习新技术或框架来解决问题的经历。',
          question_type: 'technical',
          answer_points: '回答要点：1)问题背景和技术选型原因 2)学习过程和方法 3)实践应用和踩坑经验 4)技术成果和业务价值',
          star_guidance: '问题识别→技术调研→学习实践→成果交付，体现学习能力和技术敏感度',
          common_mistakes: '避免：只说学习过程不说应用效果、选择过于简单的技术案例'
        },
        
        // 公司文化问题 (Culture Fit Questions)
        {
          id: 'c1',
          question_text: '为什么选择我们公司？你对我们公司有什么了解？',
          question_type: 'culture_fit',
          answer_points: '回答要点：1)对公司业务和使命的理解 2)公司文化和价值观的认同 3)职业发展的匹配度 4)个人能为公司带来的价值',
          star_guidance: '非常变结构：公司吸引点→个人匹配→价值贡献→未来发展，显示理性选择和深度研究',
          common_mistakes: '避免：只说空话套话、只关注薪资福利、表现出对公司业务不了解'
        },
        {
          id: 'c2',
          question_text: '你理想的工作环境和团队氛围是怎样的？',
          question_type: 'culture_fit',
          answer_points: '回答要点：1)工作方式偏好(协作、独立、沟通风格) 2)学习成长机会 3)团队文化期望 4)与目标公司文化的匹配',
          star_guidance: '结构化回答：工作方式→团队协作→成长机会→价值匹配，展示对工作环境的成熟思考',
          common_mistakes: '避免：过于具体的要求(如必须远程工作)、负面评价前公司环境'
        },
        {
          id: 'c3',
          question_text: '你的职业规划是什么？5年后你希望在哪里？',
          question_type: 'culture_fit',
          answer_points: '回答要点：1)短期目标和技能发展计划 2)中期职业方向和成长路径 3)与公司发展的匹配度 4)对行业和领域的长期承诺',
          star_guidance: '递进式结构：现在→短期(1-2年)→中期(3-5年)→长期愿景，展示目标清晰和规划能力',
          common_mistakes: '避免：目标过于模糊或不切实际、只说个人发展不考虑公司价值'
        },
        {
          id: 'c4',
          question_text: '在工作中什么最能激发你的工作热情？',
          question_type: 'culture_fit',
          answer_points: '回答要点：1)具体的工作内容或挑战 2)团队协作和成就感 3)学习成长和能力提升 4)对行业和用户的影响',
          star_guidance: '内在动机分析：工作内容→团队环境→成长机会→价值实现，体现对工作的深度理解',
          common_mistakes: '避免：只说薪资或升职机会、过于笛统的回答、与目标职位不匹配的内容'
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
                    行为问题
                  </button>
                  <button
                    className={selectedQuestionCategory === 'technical' ? 'active' : ''}
                    onClick={() => setSelectedQuestionCategory('technical')}
                  >
                    技术问题
                  </button>
                  <button
                    className={selectedQuestionCategory === 'culture_fit' ? 'active' : ''}
                    onClick={() => setSelectedQuestionCategory('culture_fit')}
                  >
                    文化匹配
                  </button>
                </div>
                
                {user && (
                  <button 
                    className="generate-questions-btn"
                    onClick={handleGenerateQuestions}
                    disabled={loading}
                  >
                    {loading ? '生成中...' : `生成${selectedQuestionCategory === 'behavioral' ? '行为' : selectedQuestionCategory === 'technical' ? '技术' : '文化匹配'}问题`}
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
                            <h4>🎯 回答要点：</h4>
                            <p>{question.answer_points}</p>
                          </div>
                        )}
                        
                        {question.star_guidance && (
                          <div className="star-guidance">
                            <h4>⭐ STAR框架指导：</h4>
                            <p>{question.star_guidance}</p>
                          </div>
                        )}
                        
                        {question.common_mistakes && (
                          <div className="common-mistakes">
                            <h4>⚠️ 常见错误：</h4>
                            <p>{question.common_mistakes}</p>
                          </div>
                        )}
                      </div>
                    ))
                ) : (
                  <div className="no-questions">
                    <p>暂无{selectedQuestionCategory === 'behavioral' ? '行为' : selectedQuestionCategory === 'technical' ? '技术' : '文化匹配'}问题。</p>
                    <p>点击“生成{selectedQuestionCategory === 'behavioral' ? '行为' : selectedQuestionCategory === 'technical' ? '技术' : '文化匹配'}问题”获取个性化问题！</p>
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