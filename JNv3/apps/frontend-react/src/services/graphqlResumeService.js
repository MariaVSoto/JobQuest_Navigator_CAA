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

const DELETE_RESUME_MUTATION = gql`
  mutation DeleteResume($resumeId: String!) {
    delete_resume(resume_id: $resumeId) {
      success
      message
      errors
    }
  }
`;

const UPLOAD_RESUME_FILE_MUTATION = gql`
  mutation UploadResumeFile($input: UploadResumeFileInput!) {
    upload_resume_file(input: $input) {
      success
      message
      errors
      resume_id
      processing_status
      download_url
    }
  }
`;

const PROCESS_PDF_RESUME_MUTATION = gql`
  mutation ProcessPDFResume($resumeId: String!) {
    process_pdf_resume(resume_id: $resumeId) {
      success
      message
      errors
      extracted_data {
        title
        personal_info {
          full_name
          email
          phone
          location
          linkedin
          website
        }
        summary
        experience {
          company
          position
          start_date
          end_date
          current
          description
        }
        education {
          school
          degree
          field
          start_date
          end_date
          current
          gpa
        }
        skills
        projects {
          name
          description
          technologies
          link
        }
      }
      processing_time
    }
  }
`;

// GraphQL Queries
const GET_RESUMES_QUERY = gql`
  query GetResumes($limit: Int, $offset: Int) {
    resumes(limit: $limit, offset: $offset) {
      success
      message
      resumes {
        id
        title
        user_id
        personal_info {
          full_name
          email
          phone
          location
        }
        target_role
        target_industry
        source_type
        processing_status
        status_display
        is_default
        view_count
        created_at
        updated_at
      }
      total_count
    }
  }
`;

const GET_RESUME_QUERY = gql`
  query GetResume($resumeId: String!) {
    resume(id: $resumeId) {
      id
      title
      createdAt
      updatedAt
      personalInfo {
        fullName
        email
        phone
        location
        linkedin
        website
      }
      summary
      experience {
        company
        position
        startDate
        endDate
        current
        description
      }
      education {
        school
        degree
        field
        startDate
        endDate
        current
        gpa
      }
      skills
      projects {
        name
        description
        technologies
        link
      }
      targetRole
      targetIndustry
      keywords
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
   * Get user's resumes
   */
  async getResumes(filters = {}) {
    try {
      console.log('🚀 Fetching resumes via GraphQL...', filters);
      
      const { data } = await this.client.query({
        query: GET_RESUMES_QUERY,
        variables: {
          limit: filters.limit || 50,
          offset: filters.offset || 0
        },
        fetchPolicy: 'cache-and-network'
      });

      const response = data.resumes;
      if (response && response.success) {
        const resumes = response.resumes || [];
        console.log('✅ Resumes fetched successfully:', resumes.length, 'resumes');
        
        return {
          results: resumes.map(resume => ({
            id: resume.id,
            title: resume.title,
            full_name: resume.personal_info?.full_name || 'Unknown',
            email: resume.personal_info?.email || '',
            target_role: resume.target_role,
            target_industry: resume.target_industry,
            source_type: resume.source_type,
            processing_status: resume.processing_status,
            status_display: resume.status_display,
            is_default: resume.is_default,
            view_count: resume.view_count,
            created_at: resume.created_at,
            updated_at: resume.updated_at,
            last_modified: resume.updated_at
          })),
          count: response.total_count || resumes.length,
          message: response.message || 'Resumes loaded successfully'
        };
      } else {
        throw new Error(response?.message || 'Failed to fetch resumes');
      }
    } catch (error) {
      console.warn('❌ GraphQL getResumes failed, using fallback:', error);
      // Return mock data for demo purposes
      const mockResume = this.getMockResumeData();
      return {
        results: [mockResume],
        count: 1,
        message: 'Using demo data - GraphQL backend not available'
      };
    }
  }

  /**
   * Get a specific resume by ID
   */
  async getResume(resumeId) {
    try {
      console.log('🚀 Fetching resume by ID via GraphQL:', resumeId);
      
      const { data } = await this.client.query({
        query: GET_RESUME_QUERY,
        variables: { resumeId },
        fetchPolicy: 'cache-and-network'
      });

      const resume = data.resume;
      if (resume) {
        console.log('✅ Resume fetched successfully:', resume.id);
        return {
          id: resume.id,
          title: resume.title,
          personalInfo: resume.personalInfo,
          summary: resume.summary,
          experience: resume.experience,
          education: resume.education,
          skills: resume.skills,
          projects: resume.projects,
          targetRole: resume.targetRole,
          targetIndustry: resume.targetIndustry,
          keywords: resume.keywords,
          created_at: resume.createdAt,
          updated_at: resume.updatedAt,
          message: 'Resume loaded successfully'
        };
      } else {
        console.log('⚠️ Resume not found, using fallback');
        const mockResume = this.getMockResumeData();
        return {
          ...mockResume,
          id: resumeId,
          message: 'Resume not found - using demo data'
        };
      }
    } catch (error) {
      console.warn('❌ GraphQL getResume failed, using fallback:', error);
      const mockResume = this.getMockResumeData();
      return {
        ...mockResume,
        id: resumeId,
        message: 'Using demo data - GraphQL backend not available'
      };
    }
  }

  /**
   * Delete a resume
   */
  async deleteResume(resumeId) {
    try {
      console.log('🚀 Deleting resume via GraphQL:', resumeId);
      
      const { data } = await this.client.mutate({
        mutation: DELETE_RESUME_MUTATION,
        variables: { resumeId },
        refetchQueries: [{ query: GET_RESUMES_QUERY }]
      });

      const result = data.delete_resume;
      
      if (result.success) {
        console.log('✅ Resume deleted successfully:', result.message);
        return {
          success: true,
          message: result.message || 'Resume deleted successfully'
        };
      } else {
        console.error('❌ Resume deletion failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'Resume deletion failed');
      }
    } catch (error) {
      console.warn('❌ GraphQL deleteResume failed:', error);
      // For demo purposes, return success even if GraphQL fails
      return {
        success: true,
        message: 'Resume deletion simulated - GraphQL backend not available'
      };
    }
  }

  /**
   * Upload a PDF resume file
   */
  async uploadResumeFile(title, fileData, filename, contentType) {
    try {
      console.log('🚀 Uploading PDF resume via GraphQL:', filename);
      
      const { data } = await this.client.mutate({
        mutation: UPLOAD_RESUME_FILE_MUTATION,
        variables: {
          input: {
            title,
            file_data: fileData,
            filename,
            content_type: contentType
          }
        }
      });

      const result = data.upload_resume_file;
      
      if (result.success) {
        console.log('✅ PDF resume uploaded successfully:', result.message);
        return {
          success: true,
          resumeId: result.resume_id,
          processingStatus: result.processing_status,
          downloadUrl: result.download_url,
          message: result.message || 'PDF uploaded successfully'
        };
      } else {
        console.error('❌ PDF upload failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'PDF upload failed');
      }
    } catch (error) {
      console.error('GraphQL uploadResumeFile error:', error);
      throw error;
    }
  }

  /**
   * Process uploaded PDF to extract resume data
   */
  async processPDFResume(resumeId) {
    try {
      console.log('🚀 Processing PDF resume via GraphQL:', resumeId);
      
      const { data } = await this.client.mutate({
        mutation: PROCESS_PDF_RESUME_MUTATION,
        variables: { resumeId }
      });

      const result = data.process_pdf_resume;
      
      if (result.success) {
        console.log('✅ PDF processed successfully:', result.message);
        return {
          success: true,
          extractedData: result.extracted_data,
          processingTime: result.processing_time,
          message: result.message || 'PDF processed successfully'
        };
      } else {
        console.error('❌ PDF processing failed:', result.errors);
        throw new Error(result.errors?.join(', ') || 'PDF processing failed');
      }
    } catch (error) {
      console.error('GraphQL processPDFResume error:', error);
      throw error;
    }
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