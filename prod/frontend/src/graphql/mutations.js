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
  mutation TokenAuth($email: String!, $password: String!) {
    tokenAuth(email: $email, password: $password) {
      token
      payload
      refreshExpiresIn
      user {
        id
        email
        username
        firstName
        lastName
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