/**
 * GraphQL Resume Service for JobQuest Navigator v2
 * Handles all resume operations via GraphQL mutations and queries
 */

import { gql } from '@apollo/client';
import apolloClient from '../apolloClient';

// GraphQL Mutations
const CREATE_RESUME_MUTATION = gql`
  mutation CreateResume($input: CreateResumeInput!) {
    createResume(input: $input) {
      success
      resumeId
      message
      errors
    }
  }
`;

const UPDATE_RESUME_MUTATION = gql`
  mutation UpdateResume($resumeId: String!, $input: CreateResumeInput!) {
    updateResume(resumeId: $resumeId, input: $input) {
      success
      resumeId
      message
      errors
    }
  }
`;

class GraphQLResumeService {
  constructor() {
    this.client = apolloClient;
  }

  /**
   * Transform frontend resume data to GraphQL input format
   */
  transformResumeDataForGraphQL(resumeData) {
    return {
      title: resumeData.title || 'Untitled Resume',
      personalInfo: {
        fullName: resumeData.personalInfo?.fullName || '',
        email: resumeData.personalInfo?.email || '',
        phone: resumeData.personalInfo?.phone || null,
        location: resumeData.personalInfo?.location || null,
        linkedin: resumeData.personalInfo?.linkedin || null,
        website: resumeData.personalInfo?.website || null,
      },
      summary: resumeData.summary || null,
      experience: resumeData.experience?.map(exp => ({
        company: exp.company || '',
        position: exp.position || '',
        startDate: exp.startDate || '',
        endDate: exp.endDate || null,
        current: exp.current || false,
        description: exp.description || null,
      })) || null,
      education: resumeData.education?.map(edu => ({
        school: edu.school || '',
        degree: edu.degree || '',
        field: edu.field || null,
        startDate: edu.startDate || '',
        endDate: edu.endDate || null,
        current: edu.current || false,
        gpa: edu.gpa || null,
      })) || null,
      skills: resumeData.skills || null,
      projects: resumeData.projects?.map(project => ({
        name: project.name || '',
        description: project.description || null,
        technologies: project.technologies || null,
        link: project.link || null,
      })) || null,
      targetRole: resumeData.targetRole || null,
      targetIndustry: resumeData.targetIndustry || null,
      keywords: resumeData.keywords || null,
    };
  }

  /**
   * Create a new resume
   */
  async createResume(resumeData) {
    try {
      console.log('Creating resume via GraphQL:', resumeData);
      
      const input = this.transformResumeDataForGraphQL(resumeData);
      
      const { data } = await this.client.mutate({
        mutation: CREATE_RESUME_MUTATION,
        variables: { input },
      });

      const result = data.createResume;
      
      if (result.success) {
        console.log('✅ Resume created successfully:', result.message);
        return {
          success: true,
          data: {
            id: result.resumeId,
            ...resumeData
          },
          message: result.message
        };
      } else {
        console.error('❌ Resume creation failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'Resume creation failed');
      }
    } catch (error) {
      console.error('GraphQL createResume error:', error);
      throw error;
    }
  }

  /**
   * Update an existing resume
   */
  async updateResume(resumeId, resumeData) {
    try {
      console.log('Updating resume via GraphQL:', resumeId, resumeData);
      
      const input = this.transformResumeDataForGraphQL(resumeData);
      
      const { data } = await this.client.mutate({
        mutation: UPDATE_RESUME_MUTATION,
        variables: { resumeId, input },
      });

      const result = data.updateResume;
      
      if (result.success) {
        console.log('✅ Resume updated successfully:', result.message);
        return {
          success: true,
          data: {
            id: resumeId,
            ...resumeData
          },
          message: result.message
        };
      } else {
        console.error('❌ Resume update failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'Resume update failed');
      }
    } catch (error) {
      console.error('GraphQL updateResume error:', error);
      throw error;
    }
  }

  /**
   * Get user's resumes (placeholder - would need backend query implementation)
   */
  async getResumes(filters = {}) {
    // TODO: Implement GraphQL query for getting resumes
    console.log('getResumes not yet implemented in GraphQL schema');
    return {
      results: [],
      count: 0,
      message: 'Resume listing not yet implemented in GraphQL backend'
    };
  }

  /**
   * Get a specific resume by ID (placeholder - would need backend query implementation)
   */
  async getResume(resumeId) {
    // TODO: Implement GraphQL query for getting single resume
    console.log('getResume not yet implemented in GraphQL schema');
    return {
      id: resumeId,
      message: 'Resume retrieval not yet implemented in GraphQL backend'
    };
  }

  /**
   * Delete a resume (placeholder - would need backend mutation implementation)
   */
  async deleteResume(resumeId) {
    // TODO: Implement GraphQL mutation for deleting resume
    console.log('deleteResume not yet implemented in GraphQL schema');
    return {
      success: true,
      message: 'Resume deletion not yet implemented in GraphQL backend'
    };
  }

  /**
   * Validate resume data before submission
   */
  validateResumeData(resumeData) {
    const errors = [];

    // Personal info validation
    if (!resumeData.personalInfo?.fullName?.trim()) {
      errors.push('Full name is required');
    }
    if (!resumeData.personalInfo?.email?.trim()) {
      errors.push('Email is required');
    }
    
    // Email format validation
    if (resumeData.personalInfo?.email) {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(resumeData.personalInfo.email)) {
        errors.push('Please enter a valid email address');
      }
    }

    // Experience validation
    if (resumeData.experience && resumeData.experience.length > 0) {
      resumeData.experience.forEach((exp, index) => {
        if (!exp.company?.trim()) {
          errors.push(`Company name is required for experience #${index + 1}`);
        }
        if (!exp.position?.trim()) {
          errors.push(`Position is required for experience #${index + 1}`);
        }
      });
    }

    return errors;
  }

  /**
   * Get fallback/mock data for demo purposes
   */
  getMockResumeData() {
    return {
      id: 'mock-resume-1',
      title: 'Software Developer Resume',
      personalInfo: {
        fullName: 'Demo User',
        email: 'demo@example.com',
        phone: '+1-555-0123',
        location: 'Los Angeles, CA'
      },
      summary: 'Experienced software developer with expertise in web technologies.',
      experience: [
        {
          company: 'Tech Company',
          position: 'Software Developer',
          startDate: '2020-01-01',
          endDate: '2024-01-01',
          current: false,
          description: 'Developed web applications using modern technologies.'
        }
      ],
      education: [
        {
          school: 'University of Technology',
          degree: 'Bachelor of Science',
          field: 'Computer Science',
          startDate: '2016-09-01',
          endDate: '2020-05-01',
          current: false,
          gpa: '3.8'
        }
      ],
      skills: ['JavaScript', 'React', 'Node.js', 'Python'],
      projects: [
        {
          name: 'Portfolio Website',
          description: 'Personal portfolio built with React and Node.js',
          technologies: 'React, Node.js, Express',
          link: 'https://github.com/demo/portfolio'
        }
      ],
      targetRole: 'Senior Software Developer',
      targetIndustry: 'Technology'
    };
  }
}

export default new GraphQLResumeService();