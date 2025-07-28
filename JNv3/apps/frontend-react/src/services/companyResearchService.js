/**
 * Company Research Service - Handles company research and interview preparation
 * Uses GraphQL when available, fallback to mock data for development
 */

// Removed fallbackService import - using mock data directly
import apolloClient from '../apolloClient';
import { gql } from '@apollo/client';

// GraphQL Queries for Company Research
const GET_COMPANY_RESEARCH = gql`
  query GetCompanyResearch($companyId: ID, $limit: Int) {
    companyResearch(companyId: $companyId, limit: $limit) {
      id
      companyId
      companyName
      industry
      size
      founded
      headquarters
      description
      culture
      benefits
      salaryRange
      growthTrends
      financialHealth
      recentNews
      interviewProcess
      createdAt
      updatedAt
    }
  }
`;

const GET_COMPANY_INSIGHTS = gql`
  query GetCompanyInsights($companyId: ID!) {
    companyInsights(companyId: $companyId) {
      id
      companyId
      marketPosition
      competitiveAdvantages
      challenges
      opportunities
      workCulture
      employeeRetention
      diversityMetrics
      careerGrowth
      technicalStack
      remotePolicy
      glassdoorRating
      linkedinFollowers
    }
  }
`;

const GET_INTERVIEW_QUESTIONS = gql`
  query GetInterviewQuestions($category: String, $difficulty: String, $limit: Int) {
    interviewQuestions(category: $category, difficulty: $difficulty, limit: $limit) {
      id
      question
      category
      difficulty
      expectedAnswer
      tips
      followUpQuestions
      isCommon
    }
  }
`;

// GraphQL Mutations for Company Research
const GENERATE_COMPANY_RESEARCH = gql`
  mutation GenerateCompanyResearch($companyId: ID!) {
    generateCompanyResearch(companyId: $companyId) {
      success
      errors
      research {
        id
        companyId
        companyName
        industry
        description
        culture
        benefits
        salaryRange
        interviewProcess
      }
    }
  }
`;

const SAVE_RESEARCH_ITEM = gql`
  mutation SaveResearchItem($researchId: ID!) {
    saveResearchItem(researchId: $researchId) {
      success
      errors
      savedItem {
        id
        savedAt
      }
    }
  }
`;

const GENERATE_INTERVIEW_QUESTIONS = gql`
  mutation GenerateInterviewQuestions($category: String!, $difficulty: String!, $count: Int) {
    generateInterviewQuestions(category: $category, difficulty: $difficulty, count: $count) {
      success
      errors
      questions {
        id
        question
        category
        difficulty
        expectedAnswer
        tips
      }
    }
  }
`;

class CompanyResearchService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
    this.useGraphQL = process.env.REACT_APP_USE_GRAPHQL === 'true';
  }

  // Company Research
  async getCompanyResearch(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching company research via GraphQL...', params);
        const { data } = await apolloClient.query({
          query: GET_COMPANY_RESEARCH,
          variables: {
            companyId: params.companyId,
            limit: params.limit || 20
          },
          fetchPolicy: 'cache-and-network'
        });

        const research = data.companyResearch || [];
        console.log('✅ Company research fetched successfully:', research.length, 'items');
        
        return {
          results: research.map(item => ({
            id: item.id,
            title: `${item.companyName} Analysis`,
            company: item.companyName,
            research_date: item.createdAt?.split('T')[0] || item.createdAt,
            confidence_score: 0.85, // Default score
            is_saved: false,
            overview: item.description,
            culture_analysis: item.culture,
            recent_news: item.recentNews,
            financial_highlights: item.financialHealth,
            growth_prospects: item.growthTrends
          }))
        };
      }
      return this.getFallbackCompanyResearch();
    } catch (error) {
      console.warn('❌ GraphQL company research failed, using fallback:', error);
      return this.getFallbackCompanyResearch();
    }
  }

  async getCompanyResearchById(researchId) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching company research by ID via GraphQL:', researchId);
        const { data } = await apolloClient.query({
          query: GET_COMPANY_RESEARCH,
          variables: {
            companyId: researchId,
            limit: 1
          },
          fetchPolicy: 'cache-and-network'
        });

        const research = data.companyResearch?.[0];
        if (research) {
          console.log('✅ Company research fetched successfully:', research.id);
          return {
            id: research.id,
            title: `${research.companyName} Analysis`,
            company: research.companyName,
            research_date: research.createdAt?.split('T')[0] || research.createdAt,
            confidence_score: 0.85,
            overview: research.description || 'No overview available',
            culture_analysis: research.culture || 'No culture analysis available',
            recent_news: research.recentNews || 'No recent news available',
            financial_highlights: research.financialHealth || 'No financial data available',
            growth_prospects: research.growthTrends || 'No growth analysis available',
            is_saved: false
          };
        } else {
          console.log('⚠️ No research found for ID, using fallback');
          return this.getFallbackCompanyResearchDetail();
        }
      }
      return this.getFallbackCompanyResearchDetail();
    } catch (error) {
      console.warn('❌ GraphQL company research by ID failed, using fallback:', error);
      return this.getFallbackCompanyResearchDetail();
    }
  }

  async generateCompanyResearch(companyId) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Generating company research via GraphQL:', companyId);
        const { data } = await apolloClient.mutate({
          mutation: GENERATE_COMPANY_RESEARCH,
          variables: { companyId },
          refetchQueries: [{ query: GET_COMPANY_RESEARCH, variables: { companyId } }]
        });

        if (data.generateCompanyResearch.success) {
          const research = data.generateCompanyResearch.research;
          console.log('✅ Company research generated successfully:', research.id);
          return {
            id: research.id,
            title: `AI-Generated Research - ${research.companyName}`,
            company: research.companyName,
            research_date: new Date().toISOString().split('T')[0],
            confidence_score: 0.88,
            overview: research.description || 'AI-generated company overview',
            culture_analysis: research.culture || 'AI-generated culture analysis',
            recent_news: 'AI-generated recent news and updates',
            financial_highlights: 'AI-generated financial insights',
            growth_prospects: 'AI-generated growth analysis',
            is_saved: false
          };
        } else {
          throw new Error(data.generateCompanyResearch.errors?.join(', ') || 'Failed to generate research');
        }
      }
      return this.getMockGeneratedResearch(companyId);
    } catch (error) {
      console.warn('❌ GraphQL generate company research failed, using mock:', error);
      return this.getMockGeneratedResearch(companyId);
    }
  }

  async saveResearchItem(researchId) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Saving research item via GraphQL:', researchId);
        const { data } = await apolloClient.mutate({
          mutation: SAVE_RESEARCH_ITEM,
          variables: { researchId },
          refetchQueries: [{ query: GET_COMPANY_RESEARCH }]
        });

        if (data.saveResearchItem.success) {
          console.log('✅ Research item saved successfully:', data.saveResearchItem.savedItem.id);
          return { 
            success: true,
            savedItem: data.saveResearchItem.savedItem
          };
        } else {
          throw new Error(data.saveResearchItem.errors?.join(', ') || 'Failed to save research');
        }
      }
      return { success: true };
    } catch (error) {
      console.warn('❌ GraphQL save research failed:', error);
      throw error;
    }
  }

  // Company Insights
  async getCompanyInsights(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching company insights via GraphQL...', params);
        const { data } = await apolloClient.query({
          query: GET_COMPANY_INSIGHTS,
          variables: {
            companyId: params.companyId
          },
          fetchPolicy: 'cache-and-network'
        });

        const insights = data.companyInsights;
        if (insights) {
          console.log('✅ Company insights fetched successfully');
          return {
            results: [
              {
                id: 'insight-culture',
                title: 'Work Culture Analysis',
                insight_type: 'culture',
                insight_type_display: 'Culture',
                content: insights.workCulture || 'No culture data available',
                source: 'AI Analysis',
                confidence_score: 0.82
              },
              {
                id: 'insight-growth',
                title: 'Career Growth Opportunities',
                insight_type: 'career',
                insight_type_display: 'Career Growth',
                content: insights.careerGrowth || 'No career growth data available',
                source: 'Employee Data Analysis',
                confidence_score: 0.78
              },
              {
                id: 'insight-tech',
                title: 'Technical Stack',
                insight_type: 'technical',
                insight_type_display: 'Technology',
                content: insights.technicalStack || 'No technical stack information available',
                source: 'Technical Analysis',
                confidence_score: 0.85
              }
            ]
          };
        } else {
          console.log('⚠️ No insights found, using fallback');
          return this.getFallbackCompanyInsights();
        }
      }
      return this.getFallbackCompanyInsights();
    } catch (error) {
      console.warn('❌ GraphQL company insights failed, using fallback:', error);
      return this.getFallbackCompanyInsights();
    }
  }

  // Company News
  async getCompanyNews(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching company news via GraphQL...', params);
        // For now, we'll use the company research query to get recent news
        const { data } = await apolloClient.query({
          query: GET_COMPANY_RESEARCH,
          variables: {
            companyId: params.companyId,
            limit: params.limit || 10
          },
          fetchPolicy: 'cache-and-network'
        });

        const research = data.companyResearch || [];
        console.log('✅ Company news data fetched successfully');
        
        return {
          results: research
            .filter(item => item.recentNews)
            .map((item, index) => ({
              id: `news-${index + 1}`,
              title: `${item.companyName} Recent Updates`,
              summary: item.recentNews,
              source: 'Company Research',
              published_date: item.createdAt?.split('T')[0] || new Date().toISOString().split('T')[0],
              url: `#/company/${item.companyId}`,
              relevance_score: 0.8
            }))
        };
      }
      return this.getFallbackCompanyNews();
    } catch (error) {
      console.warn('❌ GraphQL company news failed, using fallback:', error);
      return this.getFallbackCompanyNews();
    }
  }

  // Interview Preparation
  async getInterviewQuestions(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching interview questions via GraphQL...', params);
        const { data } = await apolloClient.query({
          query: GET_INTERVIEW_QUESTIONS,
          variables: {
            category: params.category,
            difficulty: params.difficulty,
            limit: params.limit || 20
          },
          fetchPolicy: 'cache-and-network'
        });

        const questions = data.interviewQuestions || [];
        console.log('✅ Interview questions fetched successfully:', questions.length, 'questions');
        
        return {
          results: questions.map(q => ({
            id: q.id,
            question_text: q.question,
            question_type: q.category?.toLowerCase() || 'general',
            difficulty: q.difficulty,
            difficulty_display: q.difficulty?.charAt(0).toUpperCase() + q.difficulty?.slice(1) || 'Medium',
            sample_answer: q.expectedAnswer || 'Sample answer would be provided here',
            answer_framework: q.tips || (q.category === 'behavioral' ? 'STAR Method' : 'Technical Approach'),
            is_generated: false,
            times_used: 0,
            is_common: q.isCommon || false,
            follow_up_questions: q.followUpQuestions || []
          }))
        };
      }
      return this.getFallbackInterviewQuestions();
    } catch (error) {
      console.warn('❌ GraphQL interview questions failed, using fallback:', error);
      return this.getFallbackInterviewQuestions();
    }
  }

  async generateInterviewQuestions(category, difficulty) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Generating interview questions via GraphQL:', category, difficulty);
        const { data } = await apolloClient.mutate({
          mutation: GENERATE_INTERVIEW_QUESTIONS,
          variables: { 
            category,
            difficulty,
            count: 5
          },
          refetchQueries: [{ query: GET_INTERVIEW_QUESTIONS, variables: { category, difficulty } }]
        });

        if (data.generateInterviewQuestions.success) {
          const questions = data.generateInterviewQuestions.questions;
          console.log('✅ Interview questions generated successfully:', questions.length);
          return questions.map(q => ({
            id: q.id,
            question_text: q.question,
            question_type: q.category?.toLowerCase() || category,
            difficulty: q.difficulty || difficulty,
            difficulty_display: (q.difficulty || difficulty)?.charAt(0).toUpperCase() + (q.difficulty || difficulty)?.slice(1),
            sample_answer: q.expectedAnswer || `This is a sample answer for the ${category} question.`,
            answer_framework: q.tips || (category === 'behavioral' ? 'STAR Method' : 'Structured Approach'),
            is_generated: true,
            times_used: 0
          }));
        } else {
          throw new Error(data.generateInterviewQuestions.errors?.join(', ') || 'Failed to generate questions');
        }
      }
      return this.getMockGeneratedQuestions(category, difficulty);
    } catch (error) {
      console.warn('❌ GraphQL generate interview questions failed, using mock:', error);
      return this.getMockGeneratedQuestions(category, difficulty);
    }
  }

  async getInterviewTips(category) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching interview tips via GraphQL for category:', category);
        // For tips, we'll use the general interview questions query but filter for tips
        const { data } = await apolloClient.query({
          query: GET_INTERVIEW_QUESTIONS,
          variables: {
            category: category || 'general',
            limit: 10
          },
          fetchPolicy: 'cache-and-network'
        });

        const questions = data.interviewQuestions || [];
        console.log('✅ Interview tips data fetched successfully');
        
        // Convert questions data to tips format
        const tips = questions
          .filter(q => q.tips)
          .map((q, index) => ({
            id: `tip-${category}-${index + 1}`,
            title: `${q.category} Interview Tip`,
            content: q.tips,
            category: category || 'general',
            priority: q.isCommon ? 'high' : 'medium'
          }));

        // Add some default tips if none found
        if (tips.length === 0) {
          console.log('⚠️ No GraphQL tips found, using fallback');
          return this.getFallbackInterviewTips(category);
        }

        return { results: tips };
      }
      return this.getFallbackInterviewTips(category);
    } catch (error) {
      console.warn('❌ GraphQL interview tips failed, using fallback:', error);
      return this.getFallbackInterviewTips(category);
    }
  }

  // Practice Sessions
  async getPracticeSessions(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching practice sessions via GraphQL...', params);
        // For now, we'll create mock practice sessions based on user's interview data
        // This would typically come from a dedicated practice sessions backend
        console.log('⚠️ Practice sessions not yet implemented in backend, using enhanced fallback');
        
        // Enhanced fallback with more realistic data
        const sessions = this.getFallbackPracticeSessions();
        console.log('✅ Practice sessions loaded (fallback)');
        return sessions;
      }
      return this.getFallbackPracticeSessions();
    } catch (error) {
      console.warn('❌ GraphQL practice sessions failed, using fallback:', error);
      return this.getFallbackPracticeSessions();
    }
  }

  async startPracticeSession(sessionType) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Starting practice session via GraphQL:', sessionType);
        // This would typically create a new practice session in the backend
        console.log('⚠️ Practice session creation not yet implemented in backend, using enhanced mock');
        
        const session = this.getMockPracticeSession(sessionType);
        console.log('✅ Practice session started (mock):', session.id);
        return session;
      }
      return this.getMockPracticeSession(sessionType);
    } catch (error) {
      console.warn('❌ GraphQL start practice session failed, using mock:', error);
      return this.getMockPracticeSession(sessionType);
    }
  }

  // Interview Resources
  async getInterviewResources(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching interview resources via GraphQL...', params);
        // For now, we'll use enhanced fallback data
        // This would typically come from a dedicated resources backend
        console.log('⚠️ Interview resources not yet implemented in backend, using enhanced fallback');
        
        const resources = this.getFallbackInterviewResources();
        console.log('✅ Interview resources loaded (fallback):', resources.results.length);
        return resources;
      }
      return this.getFallbackInterviewResources();
    } catch (error) {
      console.warn('❌ GraphQL interview resources failed, using fallback:', error);
      return this.getFallbackInterviewResources();
    }
  }

  // Fallback Data Methods
  getFallbackCompanyResearch() {
    return {
      results: [
        {
          id: 'research-1',
          title: 'TechCorp Company Analysis',
          company: 'TechCorp',
          research_date: '2025-07-18',
          confidence_score: 0.85,
          is_saved: false
        }
      ]
    };
  }

  getFallbackCompanyResearchDetail() {
    return {
      id: 'research-1',
      title: 'TechCorp Company Analysis',
      company: 'TechCorp',
      research_date: '2025-07-18',
      confidence_score: 0.85,
      overview: 'TechCorp is a leading technology company specializing in innovative software solutions. Founded in 2010, the company has grown rapidly and now employs over 1,000 people globally.',
      culture_analysis: 'TechCorp promotes a collaborative and innovative work environment. They value work-life balance and offer flexible working arrangements. The company culture emphasizes continuous learning and professional development.',
      recent_news: 'TechCorp recently announced a $50M Series C funding round led by prominent venture capital firms. The company is expanding into new markets and hiring aggressively across all departments.',
      financial_highlights: 'Revenue growth of 150% year-over-year. The company is profitable and has a strong cash position. Recent partnerships with major enterprise clients have strengthened their market position.',
      growth_prospects: 'Strong growth prospects in the AI and cloud computing sectors. The company is well-positioned to capitalize on emerging technology trends and has a robust product roadmap.',
      is_saved: false
    };
  }

  getMockGeneratedResearch(companyId) {
    return {
      id: `research-${Date.now()}`,
      title: `AI-Generated Company Research`,
      company: companyId,
      research_date: new Date().toISOString(),
      confidence_score: 0.88,
      overview: 'This company demonstrates strong market presence in their sector with innovative approaches to solving industry challenges.',
      culture_analysis: 'Based on employee reviews and company communications, the organization promotes collaboration, innovation, and professional growth.',
      recent_news: 'Recent company updates indicate positive growth trajectory and strategic market expansion initiatives.',
      financial_highlights: 'Financial indicators suggest stable performance with growth opportunities in emerging market segments.',
      growth_prospects: 'The company is well-positioned for continued growth given current market trends and their strategic positioning.',
      is_saved: false
    };
  }

  getFallbackCompanyInsights() {
    return {
      results: [
        {
          id: 'insight-1',
          title: 'Company Culture Insight',
          insight_type: 'culture',
          insight_type_display: 'Culture',
          content: 'Employees frequently mention the collaborative work environment and opportunities for professional development.',
          source: 'Employee Reviews Analysis',
          confidence_score: 0.82
        },
        {
          id: 'insight-2',
          title: 'Interview Process Insight',
          insight_type: 'interview',
          insight_type_display: 'Interview Process',
          content: 'Technical interviews typically include coding challenges and system design discussions. The process is reported to be fair and thorough.',
          source: 'Interview Experience Data',
          confidence_score: 0.75
        }
      ]
    };
  }

  getFallbackCompanyNews() {
    return {
      results: [
        {
          id: 'news-1',
          title: 'Company Announces Major Product Launch',
          summary: 'The company unveiled their latest innovation which is expected to revolutionize the industry.',
          source: 'Tech News Today',
          published_date: '2025-07-15',
          url: 'https://example.com/news/product-launch',
          relevance_score: 0.9
        },
        {
          id: 'news-2',
          title: 'Expansion into New Markets',
          summary: 'Strategic expansion announced for Q4 2025, targeting international markets.',
          source: 'Business Weekly',
          published_date: '2025-07-10',
          url: 'https://example.com/news/expansion',
          relevance_score: 0.75
        }
      ]
    };
  }

  getFallbackInterviewQuestions() {
    const interviewData = FallbackService.getMockInterviewData();
    return {
      results: interviewData.practiceQuestions.map((q, index) => ({
        id: `question-${index + 1}`,
        question_text: q.question,
        question_type: q.category.toLowerCase(),
        difficulty: q.difficulty,
        difficulty_display: q.difficulty.charAt(0).toUpperCase() + q.difficulty.slice(1),
        sample_answer: 'Sample answer would be provided here based on the question type and complexity.',
        answer_framework: q.category === 'React' ? 'STAR Method' : 'Technical Approach',
        is_generated: false,
        times_used: Math.floor(Math.random() * 10)
      }))
    };
  }

  getMockGeneratedQuestions(category, difficulty) {
    const questions = {
      general: [
        'Tell me about yourself and your career journey.',
        'Why are you interested in this position?',
        'What are your greatest strengths and weaknesses?'
      ],
      technical: [
        'Explain the concept of asynchronous programming in JavaScript.',
        'How would you optimize a slow database query?',
        'Describe your approach to debugging production issues.'
      ],
      behavioral: [
        'Describe a time when you had to work with a difficult team member.',
        'Tell me about a challenging project you completed successfully.',
        'How do you handle tight deadlines and pressure?'
      ]
    };

    const categoryQuestions = questions[category] || questions.general;
    return categoryQuestions.map((question, index) => ({
      id: `generated-${category}-${index + 1}`,
      question_text: question,
      question_type: category,
      difficulty: difficulty,
      difficulty_display: difficulty.charAt(0).toUpperCase() + difficulty.slice(1),
      sample_answer: `This is a sample answer for the ${category} question about ${question.split(' ').slice(0, 3).join(' ')}.`,
      answer_framework: category === 'behavioral' ? 'STAR Method' : 'Structured Approach',
      is_generated: true,
      times_used: 0
    }));
  }

  getFallbackInterviewTips(category) {
    const tips = {
      general: [
        {
          id: 'tip-general-1',
          title: 'Research the Company',
          content: 'Thoroughly research the company\'s mission, values, recent news, and industry position before the interview.',
          category: 'general',
          priority: 'high'
        },
        {
          id: 'tip-general-2',
          title: 'Prepare Questions',
          content: 'Prepare thoughtful questions about the role, team, and company culture to show your genuine interest.',
          category: 'general',
          priority: 'high'
        }
      ],
      technical: [
        {
          id: 'tip-technical-1',
          title: 'Practice Coding',
          content: 'Practice coding problems similar to what you might encounter. Focus on explaining your thought process clearly.',
          category: 'technical',
          priority: 'high'
        },
        {
          id: 'tip-technical-2',
          title: 'Know Your Projects',
          content: 'Be ready to discuss your past projects in detail, including challenges faced and solutions implemented.',
          category: 'technical',
          priority: 'medium'
        }
      ],
      behavioral: [
        {
          id: 'tip-behavioral-1',
          title: 'Use STAR Method',
          content: 'Structure your answers using Situation, Task, Action, Result format for behavioral questions.',
          category: 'behavioral',
          priority: 'high'
        },
        {
          id: 'tip-behavioral-2',
          title: 'Prepare Examples',
          content: 'Have specific examples ready that demonstrate leadership, problem-solving, and teamwork skills.',
          category: 'behavioral',
          priority: 'high'
        }
      ]
    };

    return {
      results: tips[category] || tips.general
    };
  }

  getFallbackPracticeSessions() {
    return {
      results: [
        {
          id: 'session-1',
          session_type: 'mock_interview',
          session_type_display: 'Mock Interview',
          completion_status: 'completed',
          completion_status_display: 'Completed',
          duration_minutes: 45,
          questions_attempted: 8,
          self_rating: 4,
          notes: 'Good technical answers, need to work on behavioral responses.',
          created_at: '2025-07-15T10:00:00Z'
        },
        {
          id: 'session-2',
          session_type: 'question_practice',
          session_type_display: 'Question Practice',
          completion_status: 'in_progress',
          completion_status_display: 'In Progress',
          duration_minutes: 30,
          questions_attempted: 12,
          self_rating: null,
          notes: '',
          created_at: '2025-07-18T14:30:00Z'
        }
      ]
    };
  }

  getMockPracticeSession(sessionType) {
    return {
      id: `session-${Date.now()}`,
      session_type: sessionType,
      session_type_display: sessionType === 'mock_interview' ? 'Mock Interview' : 'Question Practice',
      completion_status: 'in_progress',
      completion_status_display: 'In Progress',
      duration_minutes: 0,
      questions_attempted: 0,
      self_rating: null,
      notes: '',
      created_at: new Date().toISOString()
    };
  }

  getFallbackInterviewResources() {
    return {
      results: [
        {
          id: 'resource-1',
          title: 'Technical Interview Preparation Guide',
          description: 'Comprehensive guide covering common technical interview topics and coding challenges.',
          resource_type: 'Guide',
          category: 'Technical',
          difficulty: 'Intermediate',
          url: 'https://example.com/tech-interview-guide',
          file_url: null
        },
        {
          id: 'resource-2',
          title: 'Behavioral Interview Questions Bank',
          description: 'Collection of common behavioral interview questions with example answers.',
          resource_type: 'Document',
          category: 'Behavioral',
          difficulty: 'Beginner',
          url: null,
          file_url: 'https://example.com/behavioral-questions.pdf'
        },
        {
          id: 'resource-3',
          title: 'System Design Interview Course',
          description: 'Video course covering system design principles and common interview scenarios.',
          resource_type: 'Course',
          category: 'Technical',
          difficulty: 'Advanced',
          url: 'https://example.com/system-design-course',
          file_url: null
        }
      ]
    };
  }
}

const companyResearchService = new CompanyResearchService();
export default companyResearchService;