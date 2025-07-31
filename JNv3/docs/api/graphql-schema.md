# JobQuest Navigator v3 - GraphQL Schema Documentation

## Overview

Complete GraphQL schema for JobQuest Navigator v3's four core systems, built with FastAPI and Strawberry GraphQL.

## 🎯 Core System Schemas

### 1. Resume Management System Schema

#### Resume Types
```graphql
type Resume {
  id: ID!
  title: String!
  userId: ID!
  personalInfo: PersonalInfo!
  summary: String
  experience: [Experience!]!
  education: [Education!]!
  skills: [Skill!]!
  projects: [Project!]!
  isDefault: Boolean!
  isPrimary: Boolean!
  version: Int!
  filePath: String
  fileSize: Int
  contentType: String
  createdAt: DateTime!
  updatedAt: DateTime!
}

type PersonalInfo {
  fullName: String!
  email: String!
  phone: String
  location: String
  linkedin: String
  website: String
  github: String
  portfolio: String
}

type Experience {
  id: ID!
  company: String!
  position: String!
  startDate: Date!
  endDate: Date
  current: Boolean!
  description: String!
  achievements: [String!]!
  skills: [String!]!
}

type Education {
  id: ID!
  institution: String!
  degree: String!
  fieldOfStudy: String!
  startDate: Date!
  endDate: Date
  gpa: Float
  honors: [String!]!
}

type Project {
  id: ID!
  name: String!
  description: String!
  technologies: [String!]!
  url: String
  githubUrl: String
  startDate: Date
  endDate: Date
}
```

#### Resume Mutations
```graphql
type Mutation {
  createResume(input: CreateResumeInput!): CreateResumeResult!
  updateResume(id: ID!, input: UpdateResumeInput!): UpdateResumeResult!
  deleteResume(id: ID!): DeleteResumeResult!
  duplicateResume(id: ID!, title: String!): DuplicateResumeResult!
  setDefaultResume(id: ID!): SetDefaultResumeResult!
  uploadResumePDF(file: Upload!, userId: ID!): UploadResumeResult!
  parseResumePDF(filePath: String!): ParseResumeResult!
  generateResumeFromProfile(userId: ID!, template: String!): GenerateResumeResult!
}

input CreateResumeInput {
  title: String!
  personalInfo: PersonalInfoInput!
  summary: String
  experience: [ExperienceInput!]!
  education: [EducationInput!]!
  skills: [SkillInput!]!
  projects: [ProjectInput!]!
}

input UpdateResumeInput {
  title: String
  personalInfo: PersonalInfoInput
  summary: String
  experience: [ExperienceInput!]
  education: [EducationInput!]
  skills: [SkillInput!]
  projects: [ProjectInput!]
}
```

#### Resume Queries
```graphql
type Query {
  resume(id: ID!): Resume
  resumes(userId: ID!, filters: ResumeFilters): ResumeListResult!
  resumeVersions(userId: ID!): [Resume!]!
  resumeAnalysis(id: ID!): ResumeAnalysisResult!
  resumePreview(id: ID!): ResumePreviewResult!
}

input ResumeFilters {
  title: String
  isDefault: Boolean
  dateRange: DateRangeInput
  orderBy: ResumeOrderBy
  orderDirection: OrderDirection
}

enum ResumeOrderBy {
  TITLE
  CREATED_AT
  UPDATED_AT
  VERSION
}
```

### 2. Job Optimization System Schema

#### Job Types
```graphql
type Job {
  id: ID!
  title: String!
  company: Company!
  location: String
  locationType: LocationType!
  employmentType: EmploymentType!
  experienceLevel: ExperienceLevel!
  description: String!
  requirements: String!
  responsibilities: String
  benefits: String
  salary: SalaryRange
  skills: [String!]!
  industryTags: [String!]!
  postedDate: Date
  applicationDeadline: Date
  externalUrl: String
  applicationInstructions: String
  userId: ID!
  isActive: Boolean!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Company {
  id: ID!
  name: String!
  industry: String
  size: CompanySize
  website: String
  description: String
  logo: String
  location: String
  founded: Int
  culture: String
  benefits: [String!]!
}

type SalaryRange {
  min: Int
  max: Int
  currency: String!
  period: SalaryPeriod!
}

type JobMatch {
  jobId: ID!
  resumeId: ID!
  matchScore: Float!
  matchingSkills: [SkillMatch!]!
  missingSkills: [SkillGap!]!
  recommendations: [OptimizationRecommendation!]!
  strengthAreas: [String!]!
  improvementAreas: [String!]!
  overallFeedback: String!
  confidenceLevel: Float!
}

type SkillMatch {
  skill: String!
  relevance: Float!
  proficiencyMatch: Boolean!
  experience: String
}

type SkillGap {
  skill: String!
  importance: Float!
  alternativeSkills: [String!]!
  learningResources: [LearningResource!]!
}

type OptimizationRecommendation {
  type: RecommendationType!
  category: String!
  suggestion: String!
  impact: ImpactLevel!
  effort: EffortLevel!
  examples: [String!]!
}

enum LocationType {
  REMOTE
  ON_SITE
  HYBRID
}

enum EmploymentType {
  FULL_TIME
  PART_TIME
  CONTRACT
  INTERNSHIP
  FREELANCE
}

enum ExperienceLevel {
  ENTRY_LEVEL
  MID_LEVEL
  SENIOR_LEVEL
  EXECUTIVE
}

enum CompanySize {
  STARTUP
  SMALL
  MEDIUM
  LARGE
  ENTERPRISE
}

enum SalaryPeriod {
  HOURLY
  DAILY
  WEEKLY
  MONTHLY
  YEARLY
}

enum RecommendationType {
  KEYWORD_OPTIMIZATION
  SKILL_HIGHLIGHTING
  EXPERIENCE_EMPHASIS
  FORMAT_IMPROVEMENT
  CONTENT_ENHANCEMENT
}

enum ImpactLevel {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum EffortLevel {
  MINIMAL
  LOW
  MEDIUM
  HIGH
}
```

#### Job Mutations
```graphql
type Mutation {
  createJob(input: CreateJobInput!): CreateJobResult!
  updateJob(id: ID!, input: UpdateJobInput!): UpdateJobResult!
  deleteJob(id: ID!): DeleteJobResult!
  importJobFromUrl(url: String!, userId: ID!): ImportJobResult!
  importJobFromText(text: String!, userId: ID!): ImportJobResult!
  analyzeJobMatch(jobId: ID!, resumeId: ID!): JobMatchResult!
  generateOptimizationSuggestions(jobId: ID!, resumeId: ID!): OptimizationResult!
  applyOptimizationSuggestion(suggestionId: ID!, resumeId: ID!): ApplyOptimizationResult!
  saveJobForLater(jobId: ID!): SaveJobResult!
  createJobApplication(jobId: ID!, resumeId: ID!, coverLetter: String): CreateApplicationResult!
}

input CreateJobInput {
  title: String!
  companyName: String!
  location: String
  locationType: LocationType!
  employmentType: EmploymentType!
  experienceLevel: ExperienceLevel!
  description: String!
  requirements: String!
  responsibilities: String
  benefits: String
  salary: SalaryRangeInput
  skills: [String!]!
  industryTags: [String!]!
  applicationDeadline: Date
  externalUrl: String
  applicationInstructions: String
}

input SalaryRangeInput {
  min: Int
  max: Int
  currency: String!
  period: SalaryPeriod!
}
```

#### Job Queries
```graphql
type Query {
  job(id: ID!): Job
  jobs(filters: JobFilters, pagination: PaginationInput): JobListResult!
  jobsByUser(userId: ID!, filters: JobFilters): JobListResult!
  jobMatch(jobId: ID!, resumeId: ID!): JobMatch
  jobMatches(resumeId: ID!, limit: Int): [JobMatch!]!
  optimizationSuggestions(jobId: ID!, resumeId: ID!): [OptimizationRecommendation!]!
  savedJobs(userId: ID!): [Job!]!
  jobApplications(userId: ID!): [JobApplication!]!
  jobTrends(industry: String, location: String): JobTrendsResult!
}

input JobFilters {
  title: String
  company: String
  location: String
  locationType: LocationType
  employmentType: EmploymentType
  experienceLevel: ExperienceLevel
  skills: [String!]
  salaryMin: Int
  salaryMax: Int
  postedWithin: Int # days
  industryTags: [String!]
  isActive: Boolean
}
```

### 3. Skills & Learning System Schema

#### Skills Types
```graphql
type UserSkill {
  id: ID!
  userId: ID!
  skill: Skill!
  proficiency: ProficiencyLevel!
  verified: Boolean!
  verificationSource: String
  yearsOfExperience: Float
  lastUsed: Date
  certifications: [Certification!]!
  projects: [Project!]!
  endorsements: [SkillEndorsement!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Skill {
  id: ID!
  name: String!
  category: SkillCategory!
  subcategory: String
  description: String
  aliases: [String!]!
  relatedSkills: [Skill!]!
  prerequisites: [Skill!]!
  trending: Boolean!
  demandScore: Float
  averageSalary: Int
  jobCount: Int
  learningResources: [LearningResource!]!
}

type SkillCategory {
  id: ID!
  name: String!
  description: String
  icon: String
  color: String
  subcategories: [String!]!
}

type Certification {
  id: ID!
  name: String!
  issuer: String!
  issueDate: Date!
  expiryDate: Date
  credentialId: String
  credentialUrl: String
  skills: [Skill!]!
  verified: Boolean!
  verificationMethod: String
}

type LearningPath {
  id: ID!
  title: String!
  description: String!
  category: SkillCategory!
  targetRole: String
  difficulty: DifficultyLevel!
  estimatedDuration: String!
  prerequisites: [Skill!]!
  targetSkills: [Skill!]!
  modules: [LearningModule!]!
  milestones: [Milestone!]!
  isPublic: Boolean!
  createdBy: ID
  rating: Float
  reviewCount: Int
  enrollmentCount: Int
}

type LearningModule {
  id: ID!
  title: String!
  description: String!
  type: ModuleType!
  duration: String!
  difficulty: DifficultyLevel!
  content: ModuleContent!
  skills: [Skill!]!
  prerequisites: [LearningModule!]!
  order: Int!
  isCompleted: Boolean
  completedAt: DateTime
}

type ModuleContent {
  type: ContentType!
  url: String
  text: String
  resources: [LearningResource!]!
  quiz: Quiz
  assignment: Assignment
}

type LearningResource {
  id: ID!
  title: String!
  description: String
  type: ResourceType!
  url: String!
  provider: String!
  duration: String
  cost: CostInfo
  rating: Float
  difficulty: DifficultyLevel!
  skills: [Skill!]!
  prerequisites: [Skill!]!
}

type SkillGapAnalysis {
  userId: ID!
  targetJobId: ID
  targetRole: String
  currentSkills: [UserSkill!]!
  requiredSkills: [SkillRequirement!]!
  skillGaps: [SkillGap!]!
  strengthAreas: [String!]!
  recommendedLearningPaths: [LearningPath!]!
  estimatedLearningTime: String!
  priorityOrder: [String!]!
}

type SkillRequirement {
  skill: Skill!
  importance: ImportanceLevel!
  minimumProficiency: ProficiencyLevel!
  preferred: Boolean!
}

enum ProficiencyLevel {
  BEGINNER
  INTERMEDIATE
  ADVANCED
  EXPERT
}

enum DifficultyLevel {
  BEGINNER
  INTERMEDIATE
  ADVANCED
  EXPERT
}

enum ModuleType {
  VIDEO
  READING
  INTERACTIVE
  QUIZ
  ASSIGNMENT
  PROJECT
  PRACTICE
}

enum ContentType {
  VIDEO
  TEXT
  INTERACTIVE
  QUIZ
  ASSIGNMENT
  PROJECT
  EXTERNAL_LINK
}

enum ResourceType {
  COURSE
  TUTORIAL
  BOOK
  ARTICLE
  VIDEO
  PODCAST
  TOOL
  CERTIFICATION
}

enum ImportanceLevel {
  NICE_TO_HAVE
  IMPORTANT
  REQUIRED
  CRITICAL
}
```

#### Skills Mutations
```graphql
type Mutation {
  addUserSkill(input: AddSkillInput!): AddSkillResult!
  updateUserSkill(id: ID!, input: UpdateSkillInput!): UpdateSkillResult!
  removeUserSkill(id: ID!): RemoveSkillResult!
  verifySkill(skillId: ID!, verificationData: SkillVerificationInput!): VerifySkillResult!
  addCertification(input: CertificationInput!): CertificationResult!
  updateCertification(id: ID!, input: UpdateCertificationInput!): UpdateCertificationResult!
  enrollInLearningPath(pathId: ID!): LearningPathEnrollmentResult!
  completeModule(moduleId: ID!, completionData: ModuleCompletionInput!): ModuleCompletionResult!
  createCustomLearningPath(input: CreateLearningPathInput!): CreateLearningPathResult!
  rateResource(resourceId: ID!, rating: Int!, review: String): RateResourceResult!
  endorseSkill(userId: ID!, skillId: ID!, endorsement: SkillEndorsementInput!): SkillEndorsementResult!
}

input AddSkillInput {
  skillName: String!
  proficiency: ProficiencyLevel!
  yearsOfExperience: Float
  lastUsed: Date
  context: String
}

input CertificationInput {
  name: String!
  issuer: String!
  issueDate: Date!
  expiryDate: Date
  credentialId: String
  credentialUrl: String
  skillIds: [ID!]!
}
```

#### Skills Queries
```graphql
type Query {
  userSkills(userId: ID!, filters: SkillFilters): [UserSkill!]!
  skillSuggestions(userId: ID!, context: String): [Skill!]!
  skillGapAnalysis(userId: ID!, targetJobId: ID!, targetRole: String): SkillGapAnalysis!
  learningPaths(filters: LearningPathFilters): [LearningPath!]!
  recommendedLearningPaths(userId: ID!, targetRole: String): [LearningPath!]!
  learningProgress(userId: ID!): LearningProgressResult!
  skillTrends(timeframe: TimeFrame, industry: String): SkillTrendsResult!
  certifications(userId: ID!): [Certification!]!
  learningResources(skillId: ID!, type: ResourceType): [LearningResource!]!
  skillCategories: [SkillCategory!]!
}

input SkillFilters {
  category: ID
  proficiency: ProficiencyLevel
  verified: Boolean
  trending: Boolean
  searchTerm: String
}

input LearningPathFilters {
  category: ID
  difficulty: DifficultyLevel
  duration: String
  targetRole: String
  isPublic: Boolean
  searchTerm: String
}

enum TimeFrame {
  LAST_MONTH
  LAST_QUARTER
  LAST_YEAR
  ALL_TIME
}
```

### 4. Interview Guidance System Schema

#### Interview Types
```graphql
type InterviewQuestion {
  id: ID!
  category: QuestionCategory!
  subcategory: String
  question: String!
  expectedAnswer: String
  keyPoints: [String!]!
  tips: [String!]!
  followUpQuestions: [String!]!
  difficulty: DifficultyLevel!
  skills: [String!]!
  industries: [String!]!
  roles: [String!]!
  timeToAnswer: Int # seconds
  rating: Float
  usageCount: Int
}

type MockInterview {
  id: ID!
  userId: ID!
  title: String!
  type: InterviewType!
  targetRole: String
  targetCompany: String
  difficulty: DifficultyLevel!
  questions: [InterviewQuestion!]!
  responses: [InterviewResponse!]!
  status: InterviewStatus!
  duration: Int # seconds
  score: Float
  feedback: InterviewFeedback
  scheduledAt: DateTime
  startedAt: DateTime
  completedAt: DateTime
  createdAt: DateTime!
}

type InterviewResponse {
  id: ID!
  questionId: ID!
  response: String!
  audioUrl: String
  duration: Int # seconds
  confidence: Float
  clarity: Float
  relevance: Float
  completeness: Float
  keywordMatches: [String!]!
  improvements: [String!]!
  strengths: [String!]!
  timestamp: DateTime!
}

type InterviewFeedback {
  overallScore: Float!
  categoryScores: [CategoryScore!]!
  strengths: [String!]!
  improvements: [String!]!
  specificFeedback: [QuestionFeedback!]!
  recommendations: [String!]!
  nextSteps: [String!]!
  estimatedImprovement: String
}

type CategoryScore {
  category: String!
  score: Float!
  description: String!
}

type QuestionFeedback {
  questionId: ID!
  score: Float!
  feedback: String!
  improvements: [String!]!
  strengths: [String!]!
}

type CompanyResearch {
  id: ID!
  companyName: String!
  industry: String!
  size: CompanySize!
  headquarters: String
  founded: Int
  website: String
  description: String!
  mission: String
  values: [String!]!
  culture: CompanyCulture!
  recentNews: [NewsItem!]!
  financials: CompanyFinancials
  leadership: [LeadershipMember!]!
  interviewProcess: InterviewProcess
  commonQuestions: [InterviewQuestion!]!
  salaryInfo: SalaryInfo
  benefits: [String!]!
  workEnvironment: WorkEnvironment
  reviews: CompanyReviews
  competitorAnalysis: [CompetitorInfo!]!
  updatedAt: DateTime!
}

type CompanyCulture {
  workLifeBalance: Float
  diversity: Float
  innovation: Float
  collaboration: Float
  growth: Float
  stability: Float
  description: String
  highlights: [String!]!
}

type InterviewProcess {
  stages: [InterviewStage!]!
  averageDuration: String
  difficultyLevel: DifficultyLevel!
  commonFormats: [InterviewFormat!]!
  tips: [String!]!
  preparation: [String!]!
}

type InterviewStage {
  name: String!
  description: String!
  duration: String
  format: InterviewFormat!
  participants: [String!]!
  focus: [String!]!
}

enum QuestionCategory {
  BEHAVIORAL
  TECHNICAL
  SITUATIONAL
  COMPANY_SPECIFIC
  ROLE_SPECIFIC
  PROBLEM_SOLVING
  LEADERSHIP
  COMMUNICATION
  CULTURAL_FIT
}

enum InterviewType {
  TECHNICAL
  BEHAVIORAL
  CASE_STUDY
  SYSTEM_DESIGN
  CODING
  PRODUCT
  LEADERSHIP
  CULTURAL_FIT
  PHONE_SCREENING
  FINAL_ROUND
}

enum InterviewStatus {
  SCHEDULED
  IN_PROGRESS
  COMPLETED
  CANCELLED
  PAUSED
}

enum InterviewFormat {
  PHONE
  VIDEO
  IN_PERSON
  PANEL
  GROUP
  WHITEBOARD
  PRACTICAL
  PRESENTATION
}
```

#### Interview Mutations
```graphql
type Mutation {
  createMockInterview(input: CreateMockInterviewInput!): CreateMockInterviewResult!
  startMockInterview(interviewId: ID!): StartMockInterviewResult!
  submitInterviewResponse(
    interviewId: ID!
    questionId: ID!
    response: String!
    audioFile: Upload
  ): SubmitResponseResult!
  completeMockInterview(interviewId: ID!): CompleteMockInterviewResult!
  pauseMockInterview(interviewId: ID!): PauseMockInterviewResult!
  generateAIFeedback(interviewId: ID!): GenerateAIFeedbackResult!
  scheduleInterview(input: ScheduleInterviewInput!): ScheduleInterviewResult!
  researchCompany(companyName: String!, userId: ID!): CompanyResearchResult!
  saveCompanyNotes(companyId: ID!, notes: String!): SaveNotesResult!
  rateInterviewQuestion(questionId: ID!, rating: Int!, feedback: String): RateQuestionResult!
  createCustomQuestion(input: CreateQuestionInput!): CreateQuestionResult!
}

input CreateMockInterviewInput {
  title: String!
  type: InterviewType!
  targetRole: String
  targetCompany: String
  difficulty: DifficultyLevel!
  duration: Int # minutes
  questionCategories: [QuestionCategory!]!
  customQuestions: [ID!]
}

input ScheduleInterviewInput {
  title: String!
  type: InterviewType!
  scheduledAt: DateTime!
  targetRole: String
  targetCompany: String
  notes: String
}

input CreateQuestionInput {
  category: QuestionCategory!
  question: String!
  expectedAnswer: String
  tips: [String!]!
  difficulty: DifficultyLevel!
  skills: [String!]
  isPublic: Boolean!
}
```

#### Interview Queries
```graphql
type Query {
  mockInterviews(userId: ID!, filters: InterviewFilters): [MockInterview!]!
  mockInterview(id: ID!): MockInterview
  interviewQuestions(filters: QuestionFilters): [InterviewQuestion!]!
  questionsByCategory(category: QuestionCategory!, limit: Int): [InterviewQuestion!]!
  companyResearch(companyName: String!): CompanyResearch
  savedCompanies(userId: ID!): [CompanyResearch!]!
  interviewProgress(userId: ID!): InterviewProgressResult!
  interviewStats(userId: ID!, timeframe: TimeFrame): InterviewStatsResult!
  recommendedQuestions(userId: ID!, targetRole: String, targetCompany: String): [InterviewQuestion!]!
  practiceHistory(userId: ID!): [InterviewResponse!]!
}

input InterviewFilters {
  type: InterviewType
  status: InterviewStatus
  targetRole: String
  targetCompany: String
  dateRange: DateRangeInput
}

input QuestionFilters {
  category: QuestionCategory
  difficulty: DifficultyLevel
  skills: [String!]
  industries: [String!]
  roles: [String!]
  searchTerm: String
}
```

## 🔧 Common Types & Utilities

### Shared Types
```graphql
scalar DateTime
scalar Date
scalar Upload
scalar JSON

type PaginationInput {
  limit: Int = 20
  offset: Int = 0
  orderBy: String
  orderDirection: OrderDirection = ASC
}

type PaginatedResult {
  total: Int!
  limit: Int!
  offset: Int!
  hasMore: Boolean!
}

input DateRangeInput {
  startDate: Date!
  endDate: Date!
}

enum OrderDirection {
  ASC
  DESC
}

type BaseResult {
  success: Boolean!
  errors: [String!]!
  message: String
}

type FileUploadResult {
  success: Boolean!
  errors: [String!]!
  filePath: String
  fileSize: Int
  contentType: String
  url: String
}
```

### Error Types
```graphql
enum ErrorCode {
  VALIDATION_ERROR
  AUTHENTICATION_ERROR
  AUTHORIZATION_ERROR
  NOT_FOUND
  DUPLICATE_ENTRY
  RATE_LIMIT_EXCEEDED
  INTERNAL_ERROR
  EXTERNAL_SERVICE_ERROR
}

type GraphQLError {
  message: String!
  code: ErrorCode!
  path: [String!]
  details: JSON
}
```

## 🔍 Query Examples

### Complete Resume Management Query
```graphql
query GetUserResumeComplete($userId: ID!, $resumeId: ID!) {
  # Get user's resumes
  resumes(userId: $userId) {
    total
    results {
      id
      title
      isDefault
      version
      updatedAt
    }
  }
  
  # Get specific resume details
  resume(id: $resumeId) {
    id
    title
    personalInfo {
      fullName
      email
      phone
      location
      linkedin
    }
    summary
    experience {
      company
      position
      startDate
      endDate
      current
      description
      skills
    }
    skills {
      name
      category
      proficiency
    }
  }
}

mutation CreateResumeWithAnalysis($input: CreateResumeInput!) {
  createResume(input: $input) {
    success
    errors
    resume {
      id
      title
    }
  }
}
```

### Job Optimization with Matching
```graphql
query JobOptimizationComplete($jobId: ID!, $resumeId: ID!) {
  job(id: $jobId) {
    id
    title
    company {
      name
      industry
    }
    requirements
    skills
  }
  
  jobMatch(jobId: $jobId, resumeId: $resumeId) {
    matchScore
    matchingSkills {
      skill
      relevance
      proficiencyMatch
    }
    missingSkills {
      skill
      importance
      alternativeSkills
    }
    recommendations {
      type
      suggestion
      impact
      effort
    }
    strengthAreas
    improvementAreas
    overallFeedback
  }
}

mutation OptimizeResumeForJob($jobId: ID!, $resumeId: ID!) {
  generateOptimizationSuggestions(jobId: $jobId, resumeId: $resumeId) {
    success
    suggestions {
      type
      category
      suggestion
      impact
      effort
      examples
    }
  }
}
```

### Skills & Learning Complete Query
```graphql
query SkillsLearningComplete($userId: ID!, $targetJobId: ID!) {
  userSkills(userId: $userId) {
    skill {
      name
      category {
        name
      }
    }
    proficiency
    verified
    yearsOfExperience
    certifications {
      name
      issuer
      issueDate
    }
  }
  
  skillGapAnalysis(userId: $userId, targetJobId: $targetJobId) {
    skillGaps {
      skill
      importance
      learningResources {
        title
        type
        url
        duration
        difficulty
      }
    }
    recommendedLearningPaths {
      title
      description
      estimatedDuration
      difficulty
      targetSkills {
        name
      }
    }
  }
}
```

### Interview Guidance Complete Query
```graphql
query InterviewGuidanceComplete($userId: ID!, $companyName: String!) {
  interviewQuestions(filters: { category: BEHAVIORAL }) {
    id
    question
    tips
    difficulty
    keyPoints
  }
  
  companyResearch(companyName: $companyName) {
    companyName
    industry
    culture {
      workLifeBalance
      diversity
      description
    }
    interviewProcess {
      stages {
        name
        description
        format
        focus
      }
      tips
    }
    commonQuestions {
      question
      tips
    }
  }
  
  mockInterviews(userId: $userId) {
    id
    title
    type
    score
    completedAt
    feedback {
      overallScore
      strengths
      improvements
    }
  }
}
```

This comprehensive GraphQL schema documentation covers all four core systems with complete type definitions, queries, mutations, and real-world usage examples.