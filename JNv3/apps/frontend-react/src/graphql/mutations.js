/**
 * GraphQL Mutations for JobQuest Navigator
 * 
 * This file contains all GraphQL mutations used throughout the application.
 * Organized by functionality for easy maintenance.
 */

import { gql } from '@apollo/client';

// ============================================================================
// AUTHENTICATION MUTATIONS
// ============================================================================

export const TOKEN_AUTH = gql`
  mutation TokenAuth($username: String!, $password: String!) {
    tokenAuth(username: $username, password: $password) {
      success
      token
      message
      errors
      user {
        id
        username
        email
        fullName
        bio
        currentJobTitle
        yearsOfExperience
        industry
        careerLevel
        jobSearchStatus
        preferredWorkType
      }
    }
  }
`;

export const VERIFY_TOKEN = gql`
  mutation VerifyToken($token: String!) {
    verifyToken(token: $token) {
      payload
    }
  }
`;

export const REFRESH_TOKEN = gql`
  mutation RefreshToken($token: String!) {
    refreshToken(token: $token) {
      token
      payload
      refreshExpiresIn
    }
  }
`;

export const REGISTER_USER = gql`
  mutation RegisterUser($email: String!, $username: String!, $password: String!, $firstName: String, $lastName: String) {
    registerUser(email: $email, username: $username, password: $password, firstName: $firstName, lastName: $lastName) {
      success
      errors
      user {
        id
        email
        username
        fullName
      }
    }
  }
`;

// ============================================================================
// USER PROFILE MUTATIONS
// ============================================================================

export const UPDATE_USER_PROFILE = gql`
  mutation UpdateUserProfile(
    $fullName: String
    $bio: String
    $phoneNumber: String
    $currentJobTitle: String
    $yearsOfExperience: Int
    $industry: String
    $careerLevel: String
    $jobSearchStatus: String
    $preferredWorkType: String
  ) {
    updateProfile(
      fullName: $fullName
      bio: $bio
      phoneNumber: $phoneNumber
      currentJobTitle: $currentJobTitle
      yearsOfExperience: $yearsOfExperience
      industry: $industry
      careerLevel: $careerLevel
      jobSearchStatus: $jobSearchStatus
      preferredWorkType: $preferredWorkType
    ) {
      success
      errors
      user {
        id
        email
        username
        firstName
        lastName
        fullName
        bio
        phoneNumber
        currentJobTitle
        yearsOfExperience
        industry
        careerLevel
        jobSearchStatus
        preferredWorkType
        dateJoined
        lastLogin
      }
    }
  }
`;

// ============================================================================
// JOB & APPLICATION MUTATIONS
// ============================================================================

/**
 * Saves a job for the logged-in user.
 * Returns the job's ID and its new `isSaved` status to facilitate easy cache updates.
 */
export const SAVE_JOB = gql`
  mutation SaveJob($jobId: ID!) {
    saveJob(jobId: $jobId) {
      success
      errors
      savedJob {
        id
        job {
          id
          isSaved
        }
      }
    }
  }
`;

/**
 * Unsaves a job for the logged-in user.
 * Returns the `jobId` of the unsaved job so we can find it in the cache and update it.
 */
export const UNSAVE_JOB = gql`
  mutation UnsaveJob($jobId: ID!) {
    unsaveJob(jobId: $jobId) {
      success
      errors
      jobId
    }
  }
`;

/**
 * Applies to a job.
 * Returns the new application object, including the job's ID and its new `isApplied` status.
 */
export const APPLY_TO_JOB = gql`
  mutation ApplyToJob($jobId: ID!, $coverLetter: String, $notes: String) {
    applyToJob(jobId: $jobId, coverLetter: $coverLetter, notes: $notes) {
      success
      errors
      application {
        id
        status
        appliedDate
        coverLetter
        notes
        job {
          id
          isApplied
        }
      }
    }
  }
`;

/**
 * Updates the status of an existing job application.
 */
export const UPDATE_APPLICATION_STATUS = gql`
  mutation UpdateApplicationStatus($applicationId: ID!, $status: String!, $notes: String) {
    updateApplicationStatus(applicationId: $applicationId, status: $status, notes: $notes) {
      success
      errors
      application {
        id
        status
        notes
        lastUpdated
        job {
          id
          title
        }
      }
    }
  }
`;

// ============================================================================
// SKILLS & CERTIFICATIONS MUTATIONS
// ============================================================================

export const ADD_USER_SKILL = gql`
  mutation AddUserSkill(
    $skillId: ID!
    $proficiencyLevel: String!
    $yearsExperience: Int
    $selfAssessedLevel: String
    $targetProficiency: String
    $frequencyOfUse: String
    $evidenceUrl: String
    $lastUsed: String
  ) {
    addUserSkill(
      skillId: $skillId
      proficiencyLevel: $proficiencyLevel
      yearsExperience: $yearsExperience
      selfAssessedLevel: $selfAssessedLevel
      targetProficiency: $targetProficiency
      frequencyOfUse: $frequencyOfUse
      evidenceUrl: $evidenceUrl
      lastUsed: $lastUsed
    ) {
      success
      errors
      userSkill {
        id
        proficiencyLevel
        yearsExperience
        selfAssessedLevel
        targetProficiency
        frequencyOfUse
        evidenceUrl
        lastUsed
        isVerified
        skill {
          id
          name
          category
          description
        }
      }
    }
  }
`;

export const UPDATE_USER_SKILL = gql`
  mutation UpdateUserSkill(
    $userSkillId: ID!
    $proficiencyLevel: String
    $yearsExperience: Int
    $selfAssessedLevel: String
    $targetProficiency: String
    $frequencyOfUse: String
    $evidenceUrl: String
    $lastUsed: String
  ) {
    updateUserSkill(
      userSkillId: $userSkillId
      proficiencyLevel: $proficiencyLevel
      yearsExperience: $yearsExperience
      selfAssessedLevel: $selfAssessedLevel
      targetProficiency: $targetProficiency
      frequencyOfUse: $frequencyOfUse
      evidenceUrl: $evidenceUrl
      lastUsed: $lastUsed
    ) {
      success
      errors
      userSkill {
        id
        proficiencyLevel
        yearsExperience
        selfAssessedLevel
        targetProficiency
        frequencyOfUse
        evidenceUrl
        lastUsed
        isVerified
        skill {
          id
          name
          category
          description
        }
      }
    }
  }
`;

export const REMOVE_USER_SKILL = gql`
  mutation RemoveUserSkill($userSkillId: ID!) {
    removeUserSkill(userSkillId: $userSkillId) {
      success
      errors
    }
  }
`;

export const ADD_USER_CERTIFICATION = gql`
  mutation AddUserCertification(
    $certificationId: ID!
    $status: String!
    $earnedDate: String
    $expiryDate: String
    $credentialId: String
    $credentialUrl: String
    $targetCompletionDate: String
    $studyProgress: Int
    $notes: String
  ) {
    addUserCertification(
      certificationId: $certificationId
      status: $status
      earnedDate: $earnedDate
      expiryDate: $expiryDate
      credentialId: $credentialId
      credentialUrl: $credentialUrl
      targetCompletionDate: $targetCompletionDate
      studyProgress: $studyProgress
      notes: $notes
    ) {
      success
      errors
      userCertification {
        id
        status
        earnedDate
        expiryDate
        credentialId
        credentialUrl
        targetCompletionDate
        studyProgress
        notes
        isVerified
        certification {
          id
          name
          issuingOrganization
          description
        }
      }
    }
  }
`;

export const UPDATE_USER_CERTIFICATION = gql`
  mutation UpdateUserCertification(
    $userCertificationId: ID!
    $status: String
    $earnedDate: String
    $expiryDate: String
    $credentialId: String
    $credentialUrl: String
    $targetCompletionDate: String
    $studyProgress: Int
    $notes: String
  ) {
    updateUserCertification(
      userCertificationId: $userCertificationId
      status: $status
      earnedDate: $earnedDate
      expiryDate: $expiryDate
      credentialId: $credentialId
      credentialUrl: $credentialUrl
      targetCompletionDate: $targetCompletionDate
      studyProgress: $studyProgress
      notes: $notes
    ) {
      success
      errors
      userCertification {
        id
        status
        earnedDate
        expiryDate
        credentialId
        credentialUrl
        targetCompletionDate
        studyProgress
        notes
        isVerified
        certification {
          id
          name
          issuingOrganization
          description
        }
      }
    }
  }
`;

export const REMOVE_USER_CERTIFICATION = gql`
  mutation RemoveUserCertification($userCertificationId: ID!) {
    removeUserCertification(userCertificationId: $userCertificationId) {
      success
      errors
    }
  }
`;

export const ENROLL_IN_LEARNING_PATH = gql`
  mutation EnrollInLearningPath($learningPathId: ID!) {
    enrollInLearningPath(learningPathId: $learningPathId) {
      success
      errors
      enrollment {
        id
        status
        progressPercentage
        startedDate
        targetCompletionDate
        totalStudyHours
        learningPath {
          id
          name
          description
          estimatedDurationWeeks
          difficultyLevel
        }
      }
    }
  }
`;