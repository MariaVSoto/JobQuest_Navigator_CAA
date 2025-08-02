/**
 * Skills Service - Handles skills and certifications management
 * Uses GraphQL when available, fallback to mock data for development
 */

// Removed fallbackService import - using mock data directly
import apolloClient from '../apolloClient';
import {
  GET_USER_SKILLS,
  GET_USER_CERTIFICATIONS,
  GET_USER_LEARNING_PATHS,
  GET_SKILLS,
  GET_SKILL_CATEGORIES,
  GET_CERTIFICATIONS,
  GET_LEARNING_PATHS
} from '../graphql/queries';
import {
  ADD_USER_SKILL,
  UPDATE_USER_SKILL,
  REMOVE_USER_SKILL,
  ADD_USER_CERTIFICATION,
  UPDATE_USER_CERTIFICATION,
  REMOVE_USER_CERTIFICATION,
  ENROLL_IN_LEARNING_PATH
} from '../graphql/mutations';

class SkillsService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
    this.useGraphQL = process.env.REACT_APP_USE_GRAPHQL === 'true';
  }

  // User Skills Management
  async getUserSkills(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching user skills via GraphQL...');
        const { data } = await apolloClient.query({
          query: GET_USER_SKILLS,
          fetchPolicy: 'cache-and-network'
        });

        const skills = data.userSkills || [];
        console.log('✅ User skills fetched successfully:', skills.length, 'skills');
        
        return {
          results: skills.map(userSkill => ({
            id: userSkill.id,
            skill: userSkill.skill,
            skill_name: userSkill.skill.name,
            proficiency_level: userSkill.proficiencyLevel,
            years_experience: userSkill.yearsExperience,
            self_assessed_level: userSkill.selfAssessedLevel,
            target_proficiency: userSkill.targetProficiency,
            frequency_of_use: userSkill.frequencyOfUse,
            evidence_url: userSkill.evidenceUrl,
            is_verified: userSkill.isVerified,
            last_used: userSkill.lastUsed
          }))
        };
      }
      return this.getFallbackUserSkills();
    } catch (error) {
      console.warn('❌ GraphQL user skills failed, using fallback:', error);
      return this.getFallbackUserSkills();
    }
  }

  async addUserSkill(skillData) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Adding user skill via GraphQL:', skillData);
        const { data } = await apolloClient.mutate({
          mutation: ADD_USER_SKILL,
          variables: {
            skillId: skillData.skill || skillData.skillId,
            proficiencyLevel: skillData.proficiency_level || skillData.proficiencyLevel,
            yearsExperience: skillData.years_experience || skillData.yearsExperience,
            selfAssessedLevel: skillData.self_assessed_level || skillData.selfAssessedLevel,
            targetProficiency: skillData.target_proficiency || skillData.targetProficiency,
            frequencyOfUse: skillData.frequency_of_use || skillData.frequencyOfUse,
            evidenceUrl: skillData.evidence_url || skillData.evidenceUrl,
            lastUsed: skillData.last_used || skillData.lastUsed
          },
          refetchQueries: [{ query: GET_USER_SKILLS }]
        });

        if (data.addUserSkill.success) {
          console.log('✅ User skill added successfully:', data.addUserSkill.userSkill);
          return data.addUserSkill.userSkill;
        } else {
          throw new Error(data.addUserSkill.errors?.join(', ') || 'Failed to add skill');
        }
      }
      return this.getMockUserSkill(skillData);
    } catch (error) {
      console.warn('❌ GraphQL add skill failed, using mock:', error);
      return this.getMockUserSkill(skillData);
    }
  }

  async updateUserSkill(userSkillId, skillData) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Updating user skill via GraphQL:', userSkillId, skillData);
        const { data } = await apolloClient.mutate({
          mutation: UPDATE_USER_SKILL,
          variables: {
            userSkillId,
            proficiencyLevel: skillData.proficiency_level || skillData.proficiencyLevel,
            yearsExperience: skillData.years_experience || skillData.yearsExperience,
            selfAssessedLevel: skillData.self_assessed_level || skillData.selfAssessedLevel,
            targetProficiency: skillData.target_proficiency || skillData.targetProficiency,
            frequencyOfUse: skillData.frequency_of_use || skillData.frequencyOfUse,
            evidenceUrl: skillData.evidence_url || skillData.evidenceUrl,
            lastUsed: skillData.last_used || skillData.lastUsed
          },
          refetchQueries: [{ query: GET_USER_SKILLS }]
        });

        if (data.updateUserSkill.success) {
          console.log('✅ User skill updated successfully:', data.updateUserSkill.userSkill);
          return data.updateUserSkill.userSkill;
        } else {
          throw new Error(data.updateUserSkill.errors?.join(', ') || 'Failed to update skill');
        }
      }
      return this.getMockUserSkill(skillData, userSkillId);
    } catch (error) {
      console.warn('❌ GraphQL update skill failed, using mock:', error);
      return this.getMockUserSkill(skillData, userSkillId);
    }
  }

  async removeUserSkill(userSkillId) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Removing user skill via GraphQL:', userSkillId);
        const { data } = await apolloClient.mutate({
          mutation: REMOVE_USER_SKILL,
          variables: { userSkillId },
          refetchQueries: [{ query: GET_USER_SKILLS }]
        });

        if (data.removeUserSkill.success) {
          console.log('✅ User skill removed successfully');
          return { success: true };
        } else {
          throw new Error(data.removeUserSkill.errors?.join(', ') || 'Failed to remove skill');
        }
      }
      return { success: true };
    } catch (error) {
      console.warn('❌ GraphQL remove skill failed:', error);
      throw error;
    }
  }

  // Certifications Management
  async getUserCertifications(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching user certifications via GraphQL...');
        const { data } = await apolloClient.query({
          query: GET_USER_CERTIFICATIONS,
          fetchPolicy: 'cache-and-network'
        });

        const certifications = data.userCertifications || [];
        console.log('✅ User certifications fetched successfully:', certifications.length, 'certifications');
        
        return {
          results: certifications.map(userCert => ({
            id: userCert.id,
            certification: userCert.certification,
            status: userCert.status,
            earned_date: userCert.earnedDate,
            expiry_date: userCert.expiryDate,
            credential_id: userCert.credentialId,
            credential_url: userCert.credentialUrl,
            target_completion_date: userCert.targetCompletionDate,
            study_progress: userCert.studyProgress,
            notes: userCert.notes,
            is_verified: userCert.isVerified
          }))
        };
      }
      return this.getFallbackUserCertifications();
    } catch (error) {
      console.warn('❌ GraphQL user certifications failed, using fallback:', error);
      return this.getFallbackUserCertifications();
    }
  }

  async addUserCertification(certificationData) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Adding user certification via GraphQL:', certificationData);
        const { data } = await apolloClient.mutate({
          mutation: ADD_USER_CERTIFICATION,
          variables: {
            certificationId: certificationData.certification || certificationData.certificationId,
            status: certificationData.status,
            earnedDate: certificationData.earned_date || certificationData.earnedDate,
            expiryDate: certificationData.expiry_date || certificationData.expiryDate,
            credentialId: certificationData.credential_id || certificationData.credentialId,
            credentialUrl: certificationData.credential_url || certificationData.credentialUrl,
            targetCompletionDate: certificationData.target_completion_date || certificationData.targetCompletionDate,
            studyProgress: certificationData.study_progress || certificationData.studyProgress,
            notes: certificationData.notes
          },
          refetchQueries: [{ query: GET_USER_CERTIFICATIONS }]
        });

        if (data.addUserCertification.success) {
          console.log('✅ User certification added successfully:', data.addUserCertification.userCertification);
          return data.addUserCertification.userCertification;
        } else {
          throw new Error(data.addUserCertification.errors?.join(', ') || 'Failed to add certification');
        }
      }
      return this.getMockUserCertification(certificationData);
    } catch (error) {
      console.warn('❌ GraphQL add certification failed, using mock:', error);
      return this.getMockUserCertification(certificationData);
    }
  }

  async updateUserCertification(userCertificationId, certificationData) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Updating user certification via GraphQL:', userCertificationId, certificationData);
        const { data } = await apolloClient.mutate({
          mutation: UPDATE_USER_CERTIFICATION,
          variables: {
            userCertificationId,
            status: certificationData.status,
            earnedDate: certificationData.earned_date || certificationData.earnedDate,
            expiryDate: certificationData.expiry_date || certificationData.expiryDate,
            credentialId: certificationData.credential_id || certificationData.credentialId,
            credentialUrl: certificationData.credential_url || certificationData.credentialUrl,
            targetCompletionDate: certificationData.target_completion_date || certificationData.targetCompletionDate,
            studyProgress: certificationData.study_progress || certificationData.studyProgress,
            notes: certificationData.notes
          },
          refetchQueries: [{ query: GET_USER_CERTIFICATIONS }]
        });

        if (data.updateUserCertification.success) {
          console.log('✅ User certification updated successfully:', data.updateUserCertification.userCertification);
          return data.updateUserCertification.userCertification;
        } else {
          throw new Error(data.updateUserCertification.errors?.join(', ') || 'Failed to update certification');
        }
      }
      return this.getMockUserCertification(certificationData, userCertificationId);
    } catch (error) {
      console.warn('❌ GraphQL update certification failed, using mock:', error);
      return this.getMockUserCertification(certificationData, userCertificationId);
    }
  }

  async removeUserCertification(userCertificationId) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Removing user certification via GraphQL:', userCertificationId);
        const { data } = await apolloClient.mutate({
          mutation: REMOVE_USER_CERTIFICATION,
          variables: { userCertificationId },
          refetchQueries: [{ query: GET_USER_CERTIFICATIONS }]
        });

        if (data.removeUserCertification.success) {
          console.log('✅ User certification removed successfully');
          return { success: true };
        } else {
          throw new Error(data.removeUserCertification.errors?.join(', ') || 'Failed to remove certification');
        }
      }
      return { success: true };
    } catch (error) {
      console.warn('❌ GraphQL remove certification failed:', error);
      throw error;
    }
  }

  // Learning Paths Management
  async getUserLearningPaths(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching user learning paths via GraphQL...');
        const { data } = await apolloClient.query({
          query: GET_USER_LEARNING_PATHS,
          fetchPolicy: 'cache-and-network'
        });

        const learningPaths = data.userLearningPaths || [];
        console.log('✅ User learning paths fetched successfully:', learningPaths.length, 'paths');
        
        return {
          results: learningPaths.map(userPath => ({
            id: userPath.id,
            learning_path: userPath.learningPath,
            status: userPath.status,
            progress_percentage: userPath.progressPercentage,
            started_date: userPath.startedDate,
            target_completion_date: userPath.targetCompletionDate,
            total_study_hours: userPath.totalStudyHours
          }))
        };
      }
      return this.getFallbackUserLearningPaths();
    } catch (error) {
      console.warn('❌ GraphQL user learning paths failed, using fallback:', error);
      return this.getFallbackUserLearningPaths();
    }
  }

  async enrollInLearningPath(enrollmentData) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Enrolling in learning path via GraphQL:', enrollmentData);
        const { data } = await apolloClient.mutate({
          mutation: ENROLL_IN_LEARNING_PATH,
          variables: {
            learningPathId: enrollmentData.learning_path || enrollmentData.learningPathId
          },
          refetchQueries: [{ query: GET_USER_LEARNING_PATHS }]
        });

        if (data.enrollInLearningPath.success) {
          console.log('✅ Learning path enrollment successful:', data.enrollInLearningPath.enrollment);
          return data.enrollInLearningPath.enrollment;
        } else {
          throw new Error(data.enrollInLearningPath.errors?.join(', ') || 'Failed to enroll in learning path');
        }
      }
      return this.getMockLearningPathEnrollment(enrollmentData);
    } catch (error) {
      console.warn('❌ GraphQL enroll learning path failed, using mock:', error);
      return this.getMockLearningPathEnrollment(enrollmentData);
    }
  }

  // Skills Catalog
  async getSkills(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching available skills via GraphQL...');
        const { data } = await apolloClient.query({
          query: GET_SKILLS,
          variables: {
            category: params.category,
            search: params.search,
            limit: params.limit || 50
          },
          fetchPolicy: 'cache-and-network'
        });

        const skills = data.skills || [];
        console.log('✅ Available skills fetched successfully:', skills.length, 'skills');
        
        return {
          results: skills.map(skill => ({
            id: skill.id,
            name: skill.name,
            slug: skill.slug,
            category: skill.category,
            description: skill.description,
            is_technical: skill.isTechnical,
            popularity_score: skill.popularityScore,
            market_demand: skill.marketDemand,
            average_salary: skill.averageSalary,
            is_trending: skill.isTrending
          }))
        };
      }
      return this.getFallbackSkills();
    } catch (error) {
      console.warn('❌ GraphQL available skills failed, using fallback:', error);
      return this.getFallbackSkills();
    }
  }

  async getSkillCategories(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching skill categories via GraphQL...');
        const { data } = await apolloClient.query({
          query: GET_SKILL_CATEGORIES,
          fetchPolicy: 'cache-and-network'
        });

        const categories = data.skillCategories || [];
        console.log('✅ Skill categories fetched successfully:', categories.length, 'categories');
        
        return {
          results: categories.map(category => ({
            id: category.id,
            name: category.name,
            description: category.description,
            icon_name: category.iconName,
            skill_count: category.skillCount
          }))
        };
      }
      return this.getFallbackSkillCategories();
    } catch (error) {
      console.warn('❌ GraphQL skill categories failed, using fallback:', error);
      return this.getFallbackSkillCategories();
    }
  }

  async getCertifications(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching available certifications via GraphQL...');
        const { data } = await apolloClient.query({
          query: GET_CERTIFICATIONS,
          variables: {
            category: params.category,
            search: params.search,
            limit: params.limit || 50
          },
          fetchPolicy: 'cache-and-network'
        });

        const certifications = data.certifications || [];
        console.log('✅ Available certifications fetched successfully:', certifications.length, 'certifications');
        
        return {
          results: certifications.map(cert => ({
            id: cert.id,
            name: cert.name,
            issuing_organization: cert.issuingOrganization,
            description: cert.description,
            validity_period_months: cert.validityPeriodMonths,
            difficulty_level: cert.difficultyLevel,
            average_preparation_hours: cert.averagePreparationHours,
            market_value: cert.marketValue,
            is_popular: cert.isPopular
          }))
        };
      }
      return this.getFallbackCertifications();
    } catch (error) {
      console.warn('❌ GraphQL available certifications failed, using fallback:', error);
      return this.getFallbackCertifications();
    }
  }

  async getLearningPaths(params = {}) {
    try {
      if (this.useGraphQL) {
        console.log('🚀 Fetching available learning paths via GraphQL...');
        const { data } = await apolloClient.query({
          query: GET_LEARNING_PATHS,
          variables: {
            targetRole: params.targetRole,
            difficultyLevel: params.difficultyLevel,
            limit: params.limit || 20
          },
          fetchPolicy: 'cache-and-network'
        });

        const learningPaths = data.learningPaths || [];
        console.log('✅ Available learning paths fetched successfully:', learningPaths.length, 'paths');
        
        return {
          results: learningPaths.map(path => ({
            id: path.id,
            name: path.name,
            description: path.description,
            estimated_duration_weeks: path.estimatedDurationWeeks,
            difficulty_level: path.difficultyLevel,
            target_role: path.targetRole,
            total_modules: path.totalModules,
            completion_rate: path.completionRate,
            average_rating: path.averageRating,
            is_featured: path.isFeatured,
            skills: path.skills
          }))
        };
      }
      return this.getFallbackLearningPaths();
    } catch (error) {
      console.warn('❌ GraphQL available learning paths failed, using fallback:', error);
      return this.getFallbackLearningPaths();
    }
  }

  // Validation
  validateSkillData(skillData) {
    const errors = [];
    
    if (!skillData.skill && !skillData.skill_name) {
      errors.push('Skill is required');
    }
    
    if (!skillData.proficiency_level) {
      errors.push('Proficiency level is required');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  validateCertificationData(certificationData) {
    const errors = [];
    
    if (!certificationData.certification) {
      errors.push('Certification is required');
    }
    
    if (!certificationData.status) {
      errors.push('Status is required');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Fallback Data Methods
  getFallbackUserSkills() {
    // Mock skills data directly defined
    const skillsData = {
      userSkills: [
        { name: "JavaScript", level: "Advanced", experience: "5 years" },
        { name: "React", level: "Advanced", experience: "4 years" },
        { name: "Python", level: "Intermediate", experience: "3 years" },
        { name: "Node.js", level: "Intermediate", experience: "3 years" },
        { name: "SQL", level: "Intermediate", experience: "2 years" }
      ]
    };
    return {
      results: skillsData.userSkills.map((skill, index) => ({
        id: `user-skill-${index + 1}`,
        skill: { 
          id: `skill-${index + 1}`,
          name: skill.name,
          category: this.getSkillCategory(skill.name)
        },
        skill_name: skill.name,
        proficiency_level: skill.level,
        years_experience: skill.years,
        self_assessed_level: skill.level,
        target_proficiency: 'expert',
        frequency_of_use: 'daily',
        is_verified: Math.random() > 0.5,
        last_used: new Date().toISOString()
      }))
    };
  }

  getFallbackUserCertifications() {
    return {
      results: [
        {
          id: 'user-cert-1',
          certification: {
            id: 'cert-1',
            name: 'AWS Certified Developer',
            issuing_organization: 'Amazon Web Services'
          },
          status: 'active',
          earned_date: '2024-06-15',
          expiry_date: '2027-06-15',
          credential_id: 'AWS-DEV-123456',
          is_verified: true
        },
        {
          id: 'user-cert-2',
          certification: {
            id: 'cert-2',
            name: 'React Developer Certification',
            issuing_organization: 'Meta'
          },
          status: 'active',
          earned_date: '2024-03-20',
          expiry_date: '2026-03-20',
          credential_id: 'META-REACT-789012',
          is_verified: true
        }
      ]
    };
  }

  getFallbackUserLearningPaths() {
    return {
      results: [
        {
          id: 'user-path-1',
          learning_path: {
            id: 'path-1',
            name: 'Full Stack JavaScript Developer',
            description: 'Master modern JavaScript development',
            estimated_duration_weeks: 12,
            difficulty_level: 'intermediate'
          },
          status: 'in_progress',
          progress_percentage: 65,
          started_date: '2024-05-01',
          target_completion_date: '2024-08-01',
          total_study_hours: 78
        }
      ]
    };
  }

  getFallbackSkills() {
    return {
      results: [
        { id: 'skill-1', name: 'React', description: 'JavaScript library for building user interfaces', category: 'frontend', market_demand: 'high', average_salary: 95000, is_trending: true },
        { id: 'skill-2', name: 'Node.js', description: 'JavaScript runtime for server-side development', category: 'backend', market_demand: 'high', average_salary: 90000, is_trending: true },
        { id: 'skill-3', name: 'Python', description: 'High-level programming language', category: 'programming', market_demand: 'high', average_salary: 85000, is_trending: false },
        { id: 'skill-4', name: 'TypeScript', description: 'Typed superset of JavaScript', category: 'programming', market_demand: 'high', average_salary: 100000, is_trending: true },
        { id: 'skill-5', name: 'AWS', description: 'Amazon Web Services cloud platform', category: 'cloud', market_demand: 'high', average_salary: 110000, is_trending: true }
      ]
    };
  }

  getFallbackSkillCategories() {
    return {
      results: [
        { id: 'frontend', name: 'Frontend Development' },
        { id: 'backend', name: 'Backend Development' },
        { id: 'programming', name: 'Programming Languages' },
        { id: 'cloud', name: 'Cloud Services' },
        { id: 'database', name: 'Database Management' }
      ]
    };
  }

  getFallbackCertifications() {
    return {
      results: [
        { id: 'cert-1', name: 'AWS Certified Developer', issuing_organization: 'Amazon Web Services', description: 'Associate-level certification for AWS developers' },
        { id: 'cert-2', name: 'React Developer Certification', issuing_organization: 'Meta', description: 'Official React certification from Meta' },
        { id: 'cert-3', name: 'Google Cloud Professional', issuing_organization: 'Google Cloud', description: 'Professional cloud architect certification' }
      ]
    };
  }

  getFallbackLearningPaths() {
    return {
      results: [
        {
          id: 'path-1',
          name: 'Full Stack JavaScript Developer',
          description: 'Master modern JavaScript development from frontend to backend',
          estimated_duration_weeks: 12,
          difficulty_level: 'intermediate',
          target_role: 'Full Stack Developer',
          is_featured: true
        },
        {
          id: 'path-2',
          name: 'React Mastery',
          description: 'Become an expert in React and its ecosystem',
          estimated_duration_weeks: 8,
          difficulty_level: 'beginner',
          target_role: 'Frontend Developer',
          is_featured: true
        }
      ]
    };
  }

  // Helper methods
  getMockUserSkill(skillData, id = null) {
    return {
      id: id || `user-skill-${Date.now()}`,
      skill: skillData.skill ? { id: skillData.skill, name: skillData.skill_name } : null,
      skill_name: skillData.skill_name,
      proficiency_level: skillData.proficiency_level,
      years_experience: skillData.years_experience || 0,
      self_assessed_level: skillData.self_assessed_level,
      target_proficiency: skillData.target_proficiency,
      frequency_of_use: skillData.frequency_of_use,
      evidence_url: skillData.evidence_url,
      is_verified: false,
      last_used: skillData.last_used || new Date().toISOString()
    };
  }

  getMockUserCertification(certificationData, id = null) {
    return {
      id: id || `user-cert-${Date.now()}`,
      certification: certificationData.certification ? { id: certificationData.certification } : null,
      status: certificationData.status,
      earned_date: certificationData.earned_date,
      expiry_date: certificationData.expiry_date,
      credential_id: certificationData.credential_id,
      credential_url: certificationData.credential_url,
      target_completion_date: certificationData.target_completion_date,
      study_progress: certificationData.study_progress || 0,
      notes: certificationData.notes,
      is_verified: false
    };
  }

  getMockLearningPathEnrollment(enrollmentData) {
    return {
      id: `enrollment-${Date.now()}`,
      learning_path: { id: enrollmentData.learning_path },
      status: enrollmentData.status || 'not_started',
      progress_percentage: 0,
      started_date: new Date().toISOString(),
      total_study_hours: 0
    };
  }

  getSkillCategory(skillName) {
    const categoryMap = {
      'React': 'frontend',
      'JavaScript': 'programming', 
      'CSS': 'frontend',
      'Python': 'programming',
      'Django': 'backend',
      'Node.js': 'backend',
      'TypeScript': 'programming',
      'AWS': 'cloud'
    };
    return categoryMap[skillName] || 'programming';
  }

  // Display helper methods (used in components)
  getProficiencyColor(level) {
    const colors = {
      'beginner': '#ff6b6b',
      'intermediate': '#4ecdc4', 
      'advanced': '#45b7d1',
      'expert': '#96ceb4'
    };
    return colors[level] || '#gray';
  }

  getProficiencyDisplay(level) {
    const displays = {
      'beginner': 'Beginner',
      'intermediate': 'Intermediate',
      'advanced': 'Advanced', 
      'expert': 'Expert'
    };
    return displays[level] || level;
  }

  getCertificationStatusColor(status) {
    const colors = {
      'planned': '#feca57',
      'in_progress': '#48dbfb',
      'active': '#1dd1a1',
      'expired': '#ff6b6b'
    };
    return colors[status] || '#gray';
  }

  getCertificationStatusDisplay(status) {
    const displays = {
      'planned': 'Planned',
      'in_progress': 'In Progress',
      'active': 'Active',
      'expired': 'Expired'
    };
    return displays[status] || status;
  }

  getLearningPathStatusColor(status) {
    const colors = {
      'not_started': '#feca57',
      'in_progress': '#48dbfb',
      'completed': '#1dd1a1',
      'paused': '#ff9ff3'
    };
    return colors[status] || '#gray';
  }

  getMarketDemandColor(demand) {
    const colors = {
      'low': '#ff6b6b',
      'medium': '#feca57',
      'high': '#1dd1a1'
    };
    return colors[demand] || '#gray';
  }

  getMarketDemandDisplay(demand) {
    const displays = {
      'low': 'Low',
      'medium': 'Medium', 
      'high': 'High'
    };
    return displays[demand] || demand;
  }

  formatSalary(salary) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(salary);
  }
}

const skillsService = new SkillsService();
export default skillsService;