/**
 * GraphQL Queries for JobQuest Navigator
 * 
 * This file contains all GraphQL queries used throughout the application.
 * Organized by functionality for easy maintenance.
 */

import { gql } from '@apollo/client';

// ============================================================================
// JOB QUERIES
// ============================================================================

export const GET_JOBS = gql`
  query GetJobs(
    $limit: Int
    $offset: Int
    $search: String
    $location: String
    $company: String
    $jobType: String
    $experienceLevel: String
    $remoteType: String
  ) {
    jobs(
      limit: $limit
      offset: $offset
      search: $search
      location: $location
      company: $company
      jobType: $jobType
      experienceLevel: $experienceLevel
      remoteType: $remoteType
    ) {
      id
      title
      description
      requirements
      benefits
      salaryMin
      salaryMax
      salaryCurrency
      salaryPeriod
      jobType
      experienceLevel
      remoteType
      source
      externalUrl
      isActive
      postedDate
      expiresDate
      isSaved
      isApplied
      company {
        id
        name
        industry
        website
        logoUrl
        companySize
      }
      location {
        id
        name
        city
        state
        country
        latitude
        longitude
      }
      requiredSkills {
        skill {
          id
          name
          category
          isRequired
        }
        isRequired
        proficiencyLevel
      }
    }
  }
`;

export const GET_JOB_DETAILS = gql`
  query GetJobDetails($id: ID!) {
    job(id: $id) {
      id
      title
      description
      requirements
      benefits
      salaryMin
      salaryMax
      salaryCurrency
      salaryPeriod
      jobType
      experienceLevel
      remoteType
      source
      externalUrl
      isActive
      postedDate
      expiresDate
      createdAt
      isSaved
      isApplied
      company {
        id
        name
        slug
        description
        website
        logoUrl
        industry
        companySize
        foundedYear
        headquarters
        email
        phone
        linkedinUrl
        twitterHandle
        glassdoorRating
        glassdoorReviewCount
      }
      location {
        id
        name
        city
        state
        country
        countryCode
        latitude
        longitude
        postalCode
        timezone
        googlePlaceId
        googleFormattedAddress
        fullAddress
      }
      requiredSkills {
        skill {
          id
          name
          slug
          category
          description
          isTechnical
          popularityScore
        }
        isRequired
        proficiencyLevel
      }
    }
  }
`;

export const GET_JOBS_FOR_MAP = gql`
  query GetJobsForMap(
    $north: Float
    $south: Float
    $east: Float
    $west: Float
  ) {
    jobsForMap(
      north: $north
      south: $south
      east: $east
      west: $west
    ) {
      id
      title
      salaryMin
      salaryMax
      salaryCurrency
      jobType
      experienceLevel
      remoteType
      postedDate
      company {
        id
        name
        logoUrl
      }
      location {
        id
        name
        city
        state
        latitude
        longitude
      }
    }
  }
`;

// ============================================================================
// USER QUERIES
// ============================================================================

export const GET_CURRENT_USER = gql`
  query GetCurrentUser {
    me {
      id
      email
      username
      firstName
      lastName
      fullName
      dateOfBirth
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
`;

export const GET_USER_PROFILE = gql`
  query GetUserProfile($id: ID!) {
    user(id: $id) {
      id
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
      dateJoined
    }
  }
`;

// ============================================================================
// APPLICATION QUERIES
// ============================================================================

export const GET_MY_APPLICATIONS = gql`
  query GetMyApplications {
    myApplications {
      id
      status
      appliedDate
      lastUpdated
      coverLetter
      notes
      job {
        id
        title
        salaryMin
        salaryMax
        salaryCurrency
        jobType
        experienceLevel
        remoteType
        postedDate
        company {
          id
          name
          logoUrl
          industry
        }
        location {
          id
          name
          city
          state
        }
      }
    }
  }
`;

// ============================================================================
// LOCATION AND COMPANY QUERIES
// ============================================================================

export const GET_LOCATIONS = gql`
  query GetLocations {
    locations {
      id
      name
      city
      state
      country
      countryCode
    }
  }
`;

export const SEARCH_LOCATIONS = gql`
  query SearchLocations($query: String!, $limit: Int) {
    searchLocations(query: $query, limit: $limit) {
      id
      name
      city
      state
      country
      countryCode
    }
  }
`;

export const GET_COMPANIES = gql`
  query GetCompanies {
    companies {
      id
      name
      industry
      website
      logoUrl
      companySize
    }
  }
`;

export const SEARCH_COMPANIES = gql`
  query SearchCompanies($query: String!, $limit: Int) {
    searchCompanies(query: $query, limit: $limit) {
      id
      name
      industry
      website
      logoUrl
      companySize
    }
  }
`;

// ============================================================================
// SKILLS QUERIES
// ============================================================================

export const GET_SKILLS = gql`
  query GetSkills($category: String, $search: String, $limit: Int) {
    skills(category: $category, search: $search, limit: $limit) {
      id
      name
      slug
      category
      description
      isTechnical
      popularityScore
      marketDemand
      averageSalary
      isTrending
    }
  }
`;

export const GET_USER_SKILLS = gql`
  query GetUserSkills {
    userSkills {
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
        isTechnical
        popularityScore
        marketDemand
        averageSalary
      }
    }
  }
`;

export const GET_USER_CERTIFICATIONS = gql`
  query GetUserCertifications {
    userCertifications {
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
        validityPeriodMonths
        difficultyLevel
      }
    }
  }
`;

export const GET_USER_LEARNING_PATHS = gql`
  query GetUserLearningPaths {
    userLearningPaths {
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
        targetRole
        isFeatured
      }
    }
  }
`;

export const GET_SKILL_CATEGORIES = gql`
  query GetSkillCategories {
    skillCategories {
      id
      name
      description
      iconName
      skillCount
    }
  }
`;

export const GET_CERTIFICATIONS = gql`
  query GetCertifications($category: String, $search: String, $limit: Int) {
    certifications(category: $category, search: $search, limit: $limit) {
      id
      name
      issuingOrganization
      description
      validityPeriodMonths
      difficultyLevel
      averagePreparationHours
      marketValue
      isPopular
    }
  }
`;

export const GET_LEARNING_PATHS = gql`
  query GetLearningPaths($targetRole: String, $difficultyLevel: String, $limit: Int) {
    learningPaths(targetRole: $targetRole, difficultyLevel: $difficultyLevel, limit: $limit) {
      id
      name
      description
      estimatedDurationWeeks
      difficultyLevel
      targetRole
      totalModules
      completionRate
      averageRating
      isFeatured
      skills {
        id
        name
        category
      }
    }
  }
`;

// ============================================================================
// SAVED JOBS QUERIES
// ============================================================================

export const GET_SAVED_JOBS = gql`
  query GetSavedJobs {
    # This will need to be implemented in the backend schema
    # For now, we can use jobs with isSaved filter
    jobs(limit: 100) {
      id
      title
      description
      salaryMin
      salaryMax
      salaryCurrency
      jobType
      experienceLevel
      remoteType
      postedDate
      isSaved
      company {
        id
        name
        logoUrl
        industry
      }
      location {
        id
        name
        city
        state
      }
    }
  }
`;

// ============================================================================
// COMPANY DETAILS QUERY
// ============================================================================

export const GET_COMPANY_DETAILS = gql`
  query GetCompanyDetails($id: ID!) {
    company(id: $id) {
      id
      name
      slug
      description
      website
      logoUrl
      industry
      companySize
      foundedYear
      headquarters
      email
      phone
      linkedinUrl
      twitterHandle
      glassdoorRating
      glassdoorReviewCount
    }
  }
`;