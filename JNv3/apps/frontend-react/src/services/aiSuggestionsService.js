/**
 * AI Suggestions Service - Handles AI-powered job suggestions and resume recommendations
 * Uses GraphQL when available, fallback to mock data for development
 */

// Removed fallbackService import - using mock data directly
import apolloClient from '../apolloClient';
import { gql } from '@apollo/client';

// GraphQL Queries for AI Suggestions (placeholder - would need backend implementation)
const GET_AI_SUGGESTIONS = gql`
  query GetAISuggestions($resumeId: ID) {
    aiSuggestions(resumeId: $resumeId) {
      id
      type
      title
      description
      priority
      confidence
      status
      content {
        suggestion
        keywords
        examples
      }
      createdAt
    }
  }
`;

const GET_JOB_RECOMMENDATIONS = gql`
  query GetJobRecommendations($userId: ID!) {
    jobRecommendations(userId: $userId) {
      id
      jobId
      jobTitle
      companyName
      matchScore
      reason
      matchingSkills
      missingSkills
      viewed
      saved
      dismissed
    }
  }
`;

const GET_AI_ANALYTICS = gql`
  query GetAIAnalytics {
    aiAnalytics {
      suggestions {
        total
        pending
        accepted
        rejected
      }
      recommendations {
        total
        saved
        dismissed
      }
    }
  }
`;

// GraphQL Mutations
const GENERATE_AI_SUGGESTIONS = gql`
  mutation GenerateAISuggestions($resumeId: ID!) {
    generateAISuggestions(resumeId: $resumeId) {
      success
      errors
      suggestions {
        id
        type
        title
        description
        priority
        confidence
        content {
          suggestion
          keywords
          examples
        }
      }
    }
  }
`;

const UPDATE_SUGGESTION_STATUS = gql`
  mutation UpdateSuggestionStatus($suggestionId: ID!, $status: String!) {
    updateSuggestionStatus(suggestionId: $suggestionId, status: $status) {
      success
      errors
    }
  }
`;

const UPDATE_RECOMMENDATION_STATUS = gql`
  mutation UpdateRecommendationStatus($recommendationId: ID!, $action: String!) {
    updateRecommendationStatus(recommendationId: $recommendationId, action: $action) {
      success
      errors
    }
  }
`;

class AISuggestionsService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
    this.useGraphQL = process.env.REACT_APP_USE_GRAPHQL === 'true';
    console.log('🔧 AISuggestionsService initialized with GraphQL:', this.useGraphQL);
  }

  // AI Suggestions
  async getAISuggestions(params = {}) {
    try {
      // For now, always use fallback data since backend AI suggestions are not implemented
      console.log('⚠️ AI Suggestions GraphQL not implemented in backend, using fallback data');
      return this.getFallbackAISuggestions();
    } catch (error) {
      console.warn('❌ Error in AI suggestions service, using fallback:', error);
      return this.getFallbackAISuggestions();
    }
  }

  async generateAISuggestions(resumeId) {
    try {
      console.log('⚠️ Generate AI Suggestions GraphQL not implemented in backend, using fallback data');
      return this.getFallbackGeneratedSuggestions(resumeId);
    } catch (error) {
      console.warn('❌ Error generating AI suggestions, using fallback:', error);
      return this.getFallbackGeneratedSuggestions(resumeId);
    }
  }

  async updateSuggestionStatus(suggestionId, status) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Updating suggestion status via GraphQL:', suggestionId, status);
        const { data } = await apolloClient.mutate({
          mutation: UPDATE_SUGGESTION_STATUS,
          variables: { suggestionId, status },
          refetchQueries: [{ query: GET_AI_SUGGESTIONS }]
        });

        if (data.updateSuggestionStatus.success) {
          console.log('✅ Suggestion status updated successfully');
          return { success: true };
        } else {
          throw new Error(data.updateSuggestionStatus.errors?.join(', ') || 'Failed to update suggestion');
        }
      }
      return { success: true };
    } catch (error) {
      console.warn('❌ GraphQL update suggestion status failed:', error);
      throw error;
    }
  }

  // Job Recommendations
  async getJobRecommendations(params = {}) {
    try {
      console.log('⚠️ Job Recommendations GraphQL not implemented in backend, using fallback data');
      return this.getFallbackJobRecommendations();
    } catch (error) {
      console.warn('❌ Error in job recommendations service, using fallback:', error);
      return this.getFallbackJobRecommendations();
    }
  }

  async generateJobRecommendations(userId) {
    try {
      console.log('⚠️ Generate Job Recommendations GraphQL not implemented in backend, using fallback data');
      return this.getFallbackJobRecommendations();
    } catch (error) {
      console.warn('❌ Error generating job recommendations, using fallback:', error);
      return this.getFallbackJobRecommendations();
    }
  }

  async updateRecommendationStatus(recommendationId, action) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Updating recommendation status via GraphQL:', recommendationId, action);
        const { data } = await apolloClient.mutate({
          mutation: UPDATE_RECOMMENDATION_STATUS,
          variables: { recommendationId, action },
          refetchQueries: [{ query: GET_JOB_RECOMMENDATIONS }]
        });

        if (data.updateRecommendationStatus.success) {
          console.log('✅ Recommendation status updated successfully');
          return { success: true };
        } else {
          throw new Error(data.updateRecommendationStatus.errors?.join(', ') || 'Failed to update recommendation');
        }
      }
      return { success: true };
    } catch (error) {
      console.warn('❌ GraphQL update recommendation status failed:', error);
      throw error;
    }
  }

  // Analytics
  async getAIAnalytics(params = {}) {
    try {
      console.log('⚠️ AI Analytics GraphQL not implemented in backend, using fallback data');
      return this.getFallbackAnalytics();
    } catch (error) {
      console.warn('❌ Error in AI analytics service, using fallback:', error);
      return this.getFallbackAnalytics();
    }
  }

  // Fallback Data Methods
  getFallbackAISuggestions() {
    return {
      suggestions: [
        {
          id: 'suggestion-1',
          type: 'keyword_optimization',
          title: 'Add Industry Keywords',
          description: 'Your resume could benefit from more industry-specific keywords to improve ATS compatibility.',
          priority: 'high',
          confidence: 0.87,
          status: 'pending',
          content: {
            suggestion: 'Add keywords like "React", "TypeScript", "REST APIs", and "Agile" to better match job requirements.',
            keywords: ['React', 'TypeScript', 'REST APIs', 'Agile', 'Unit Testing'],
            examples: [
              'Developed React applications using TypeScript',
              'Built RESTful APIs with Node.js and Express',
              'Followed Agile methodologies in team environment'
            ]
          }
        },
        {
          id: 'suggestion-2',
          type: 'content_enhancement',
          title: 'Quantify Achievements',
          description: 'Add specific numbers and metrics to make your achievements more impactful.',
          priority: 'high',
          confidence: 0.92,
          status: 'pending',
          content: {
            suggestion: 'Replace vague descriptions with specific metrics and results.',
            examples: [
              'Improved application performance by 40%',
              'Reduced bug reports by 60% through comprehensive testing',
              'Led team of 5 developers in project delivery'
            ]
          }
        },
        {
          id: 'suggestion-3',
          type: 'skill_highlight',
          title: 'Highlight Technical Skills',
          description: 'Your technical skills section needs better organization and more relevant technologies.',
          priority: 'medium',
          confidence: 0.78,
          status: 'pending',
          content: {
            suggestion: 'Reorganize skills by category and add trending technologies.',
            keywords: ['Docker', 'Kubernetes', 'AWS', 'GraphQL'],
            examples: [
              'Frontend: React, TypeScript, CSS3, HTML5',
              'Backend: Node.js, Python, PostgreSQL',
              'DevOps: Docker, AWS, CI/CD'
            ]
          }
        }
      ]
    };
  }

  getFallbackGeneratedSuggestions(resumeId) {
    return {
      suggestions: [
        {
          id: `generated-${Date.now()}`,
          type: 'resume_improvement',
          title: 'AI-Generated Resume Enhancement',
          description: 'Based on current job market trends, here are personalized improvements for your resume.',
          priority: 'high',
          confidence: 0.85,
          status: 'pending',
          content: {
            suggestion: 'Add cloud computing experience and modern framework expertise to match current market demands.',
            keywords: ['Cloud Computing', 'Microservices', 'React Hooks', 'DevOps'],
            examples: [
              'Deployed applications on AWS using Docker containers',
              'Implemented microservices architecture',
              'Used React Hooks for state management'
            ]
          }
        }
      ]
    };
  }

  getFallbackJobRecommendations() {
    return {
      recommendations: [
        {
          id: 'rec-1',
          job_id: 'job-1',
          job_title: 'Senior React Developer',
          company_name: 'Tech Innovations Inc',
          match_score: 0.92,
          reason: 'Your React expertise and full-stack experience are a perfect match for this role.',
          matching_skills: ['React', 'JavaScript', 'CSS', 'REST APIs'],
          missing_skills: ['TypeScript', 'GraphQL'],
          viewed: false,
          saved: false,
          dismissed: false
        },
        {
          id: 'rec-2',
          job_id: 'job-2',
          job_title: 'Full Stack Engineer',
          company_name: 'StartupXYZ',
          match_score: 0.85,
          reason: 'Your full-stack skills align well with this startup environment role.',
          matching_skills: ['React', 'Node.js', 'Python'],
          missing_skills: ['Docker', 'AWS'],
          viewed: true,
          saved: false,
          dismissed: false
        },
        {
          id: 'rec-3',
          job_id: 'job-3',
          job_title: 'Frontend Developer',
          company_name: 'Digital Agency Co',
          match_score: 0.78,
          reason: 'Your frontend skills match the requirements, though some modern tools would strengthen your profile.',
          matching_skills: ['React', 'CSS', 'JavaScript'],
          missing_skills: ['Vue.js', 'Webpack'],
          viewed: false,
          saved: true,
          dismissed: false
        }
      ]
    };
  }

  getFallbackAnalytics() {
    return {
      suggestions: {
        total: 3,
        pending: 3,
        accepted: 0,
        rejected: 0
      },
      recommendations: {
        total: 3,
        saved: 1,
        dismissed: 0
      }
    };
  }
}

const aiSuggestionsService = new AISuggestionsService();
export default aiSuggestionsService;