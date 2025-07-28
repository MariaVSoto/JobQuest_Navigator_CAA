/**
 * Optimized Skills Service with Unified Fallback Management
 * Demonstrates the new fallback pattern for skills and certifications management
 */

import { fallbackManager } from './fallbackManager';
import { fallbackService } from './fallbackService';
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

class OptimizedSkillsService {
  constructor() {
    console.log('🔧 OptimizedSkillsService initialized with FallbackManager');
  }

  // User Skills Management with unified fallback
  async getUserSkills(params = {}) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (params) => this.fetchUserSkillsGraphQL(params),
      fallbackOperation: null, // No REST API for this
      mockOperation: () => fallbackService.createMockListResponse(
        fallbackService.getMockSkills().userSkills.map(skill => ({
          id: `mock-skill-${skill.name.toLowerCase()}`,
          skill: { name: skill.name, category: 'technical' },
          proficiency_level: skill.level,
          years_experience: skill.years,
          is_verified: false
        })),
        'getUserSkills'
      ),
      operationName: 'getUserSkills',
      args: [params]
    });
  }

  async addUserSkill(skillData) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (data) => this.addUserSkillGraphQL(data),
      fallbackOperation: null,
      mockOperation: (data) => fallbackService.createMockResponse({
        id: `mock-skill-${Date.now()}`,
        skill: { name: data.skillName || 'New Skill', category: 'technical' },
        proficiency_level: data.proficiencyLevel || 'beginner',
        years_experience: data.yearsExperience || 0,
        is_verified: false
      }, 'addUserSkill'),
      operationName: 'addUserSkill',
      args: [skillData]
    });
  }

  async updateUserSkill(skillId, updateData) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (id, data) => this.updateUserSkillGraphQL(id, data),
      fallbackOperation: null,
      mockOperation: (id, data) => fallbackService.createMockResponse({
        id: id,
        ...data,
        updated_at: new Date().toISOString()
      }, 'updateUserSkill'),
      operationName: 'updateUserSkill',
      args: [skillId, updateData]
    });
  }

  async removeUserSkill(skillId) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (id) => this.removeUserSkillGraphQL(id),
      fallbackOperation: null,
      mockOperation: (id) => fallbackService.createMockResponse({
        id: id,
        deleted: true
      }, 'removeUserSkill'),
      operationName: 'removeUserSkill',
      args: [skillId]
    });
  }

  // User Certifications Management
  async getUserCertifications(params = {}) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (params) => this.fetchUserCertificationsGraphQL(params),
      fallbackOperation: null,
      mockOperation: () => fallbackService.createMockListResponse(
        fallbackService.getMockCertifications().results,
        'getUserCertifications'
      ),
      operationName: 'getUserCertifications',
      args: [params]
    });
  }

  async addUserCertification(certificationData) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (data) => this.addUserCertificationGraphQL(data),
      fallbackOperation: null,
      mockOperation: (data) => fallbackService.createMockResponse({
        id: `mock-cert-${Date.now()}`,
        name: data.name || 'New Certification',
        provider: data.provider || 'Unknown Provider',
        status: 'in_progress',
        completionDate: null
      }, 'addUserCertification'),
      operationName: 'addUserCertification',
      args: [certificationData]
    });
  }

  // Learning Paths Management
  async getUserLearningPaths(params = {}) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (params) => this.fetchUserLearningPathsGraphQL(params),
      fallbackOperation: null,
      mockOperation: () => fallbackService.createMockListResponse(
        fallbackService.getMockLearningPaths().results,
        'getUserLearningPaths'
      ),
      operationName: 'getUserLearningPaths',
      args: [params]
    });
  }

  async enrollInLearningPath(pathId) {
    return await fallbackManager.executeWithFallback({
      primaryOperation: (id) => this.enrollInLearningPathGraphQL(id),
      fallbackOperation: null,
      mockOperation: (id) => fallbackService.createMockResponse({
        pathId: id,
        enrolled: true,
        enrollmentDate: new Date().toISOString(),
        progress: 0
      }, 'enrollInLearningPath'),
      operationName: 'enrollInLearningPath',
      args: [pathId]
    });
  }

  // GraphQL Implementation methods
  async fetchUserSkillsGraphQL(params) {
    const { data } = await apolloClient.query({
      query: GET_USER_SKILLS,
      variables: params,
      fetchPolicy: 'cache-and-network'
    });

    const skills = data.userSkills || [];
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
      })),
      count: skills.length
    };
  }

  async addUserSkillGraphQL(skillData) {
    const { data } = await apolloClient.mutate({
      mutation: ADD_USER_SKILL,
      variables: {
        skillId: skillData.skillId,
        proficiencyLevel: skillData.proficiencyLevel,
        yearsExperience: skillData.yearsExperience,
        selfAssessedLevel: skillData.selfAssessedLevel,
        targetProficiency: skillData.targetProficiency,
        frequencyOfUse: skillData.frequencyOfUse,
        evidenceUrl: skillData.evidenceUrl,
        lastUsed: skillData.lastUsed
      },
      refetchQueries: [{ query: GET_USER_SKILLS }]
    });

    if (!data.addUserSkill.success) {
      throw new Error(data.addUserSkill.errors?.join(', ') || 'Failed to add skill');
    }

    return {
      success: true,
      data: data.addUserSkill.userSkill,
      message: 'Skill added successfully'
    };
  }

  async updateUserSkillGraphQL(skillId, updateData) {
    const { data } = await apolloClient.mutate({
      mutation: UPDATE_USER_SKILL,
      variables: {
        skillId: skillId,
        ...updateData
      },
      refetchQueries: [{ query: GET_USER_SKILLS }]
    });

    if (!data.updateUserSkill.success) {
      throw new Error(data.updateUserSkill.errors?.join(', ') || 'Failed to update skill');
    }

    return {
      success: true,
      data: data.updateUserSkill.userSkill,
      message: 'Skill updated successfully'
    };
  }

  async removeUserSkillGraphQL(skillId) {
    const { data } = await apolloClient.mutate({
      mutation: REMOVE_USER_SKILL,
      variables: { skillId },
      refetchQueries: [{ query: GET_USER_SKILLS }]
    });

    if (!data.removeUserSkill.success) {
      throw new Error(data.removeUserSkill.errors?.join(', ') || 'Failed to remove skill');
    }

    return {
      success: true,
      message: 'Skill removed successfully'
    };
  }

  async fetchUserCertificationsGraphQL(params) {
    const { data } = await apolloClient.query({
      query: GET_USER_CERTIFICATIONS,
      variables: params,
      fetchPolicy: 'cache-and-network'
    });

    return {
      results: data.userCertifications || [],
      count: data.userCertifications?.length || 0
    };
  }

  async addUserCertificationGraphQL(certificationData) {
    const { data } = await apolloClient.mutate({
      mutation: ADD_USER_CERTIFICATION,
      variables: certificationData,
      refetchQueries: [{ query: GET_USER_CERTIFICATIONS }]
    });

    if (!data.addUserCertification.success) {
      throw new Error(data.addUserCertification.errors?.join(', ') || 'Failed to add certification');
    }

    return {
      success: true,
      data: data.addUserCertification.certification,
      message: 'Certification added successfully'
    };
  }

  async fetchUserLearningPathsGraphQL(params) {
    const { data } = await apolloClient.query({
      query: GET_USER_LEARNING_PATHS,
      variables: params,
      fetchPolicy: 'cache-and-network'
    });

    return {
      results: data.userLearningPaths || [],
      count: data.userLearningPaths?.length || 0
    };
  }

  async enrollInLearningPathGraphQL(pathId) {
    const { data } = await apolloClient.mutate({
      mutation: ENROLL_IN_LEARNING_PATH,
      variables: { pathId },
      refetchQueries: [{ query: GET_USER_LEARNING_PATHS }]
    });

    if (!data.enrollInLearningPath.success) {
      throw new Error(data.enrollInLearningPath.errors?.join(', ') || 'Failed to enroll in learning path');
    }

    return {
      success: true,
      data: data.enrollInLearningPath.enrollment,
      message: 'Successfully enrolled in learning path'
    };
  }

  /**
   * Get service health status
   */
  getHealthStatus() {
    return {
      ...fallbackManager.getHealthStatus(),
      service: 'OptimizedSkillsService'
    };
  }
}

// Export singleton instance
export const optimizedSkillsService = new OptimizedSkillsService();
export default optimizedSkillsService;