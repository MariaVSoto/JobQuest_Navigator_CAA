# JobQuest Navigator v3 - API Documentation

## Overview

JobQuest Navigator v3 provides a comprehensive GraphQL API built with FastAPI and Strawberry GraphQL, designed around four core systems for complete career management.

## 🎯 Four Core Systems API

### 1. Resume Management System API

#### GraphQL Types
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
}
```

#### Core Mutations
```graphql
type Mutation {
  createResume(input: CreateResumeInput!): CreateResumeResult!
  updateResume(id: ID!, input: UpdateResumeInput!): UpdateResumeResult!
  deleteResume(id: ID!): DeleteResumeResult!
  uploadResumePDF(file: Upload!, userId: ID!): UploadResumeResult!
  parseResumePDF(filePath: String!): ParseResumeResult!
}
```

#### Core Queries
```graphql
type Query {
  resume(id: ID!): Resume
  resumes(userId: ID!, limit: Int, offset: Int): ResumeListResult!
  resumeVersions(userId: ID!): [Resume!]!
}
```

### 2. Job Optimization System API

#### GraphQL Types
```graphql
type Job {
  id: ID!
  title: String!
  company: String!
  location: String
  description: String!
  requirements: String
  salary: String
  type: JobType!
  remote: Boolean!
  skills: [String!]!
  createdAt: DateTime!
}

type JobMatch {
  jobId: ID!
  resumeId: ID!
  matchScore: Float!
  matchingSkills: [String!]!
  missingSkills: [String!]!
  suggestions: [String!]!
}
```

#### Core Mutations
```graphql
type Mutation {
  createJob(input: CreateJobInput!): CreateJobResult!
  updateJob(id: ID!, input: UpdateJobInput!): UpdateJobResult!
  analyzeJobMatch(jobId: ID!, resumeId: ID!): JobMatchResult!
  generateOptimizationSuggestions(jobId: ID!, resumeId: ID!): OptimizationResult!
}
```

#### Core Queries
```graphql
type Query {
  job(id: ID!): Job
  jobs(filters: JobFilters, limit: Int, offset: Int): JobListResult!
  jobMatches(resumeId: ID!): [JobMatch!]!
  optimizationSuggestions(jobId: ID!, resumeId: ID!): [OptimizationSuggestion!]!
}
```

### 3. Skills & Learning System API

#### GraphQL Types
```graphql
type UserSkill {
  id: ID!
  userId: ID!
  skillId: ID!
  skill: Skill!
  proficiency: ProficiencyLevel!
  verified: Boolean!
  certifications: [Certification!]!
}

type Skill {
  id: ID!
  name: String!
  category: SkillCategory!
  description: String
  trending: Boolean!
}

type LearningPath {
  id: ID!
  title: String!
  description: String!
  duration: String!
  level: SkillLevel!
  skills: [Skill!]!
  modules: [LearningModule!]!
  progress: Float
}
```

#### Core Mutations
```graphql
type Mutation {
  addUserSkill(input: AddSkillInput!): AddSkillResult!
  updateSkillProficiency(skillId: ID!, proficiency: ProficiencyLevel!): UpdateSkillResult!
  startLearningPath(pathId: ID!): StartLearningResult!
  completeModule(moduleId: ID!): CompleteModuleResult!
  addCertification(input: CertificationInput!): CertificationResult!
}
```

#### Core Queries
```graphql
type Query {
  userSkills(userId: ID!): [UserSkill!]!
  skillGapAnalysis(userId: ID!, targetJobId: ID!): SkillGapResult!
  learningPaths(filters: LearningPathFilters): [LearningPath!]!
  skillTrends: [SkillTrend!]!
  certifications(userId: ID!): [Certification!]!
}
```

### 4. Interview Guidance System API

#### GraphQL Types
```graphql
type InterviewQuestion {
  id: ID!
  category: QuestionCategory!
  question: String!
  expectedAnswer: String
  tips: [String!]!
  difficulty: DifficultyLevel!
}

type MockInterview {
  id: ID!
  userId: ID!
  companyId: ID
  questions: [InterviewQuestion!]!
  responses: [InterviewResponse!]!
  feedback: InterviewFeedback
  score: Float
  completedAt: DateTime
}

type CompanyResearch {
  id: ID!
  companyName: String!
  industry: String!
  size: String
  culture: String
  recentNews: [NewsItem!]!
  interviewTips: [String!]!
}
```

#### Core Mutations
```graphql
type Mutation {
  startMockInterview(input: StartInterviewInput!): MockInterviewResult!
  submitInterviewResponse(interviewId: ID!, questionId: ID!, response: String!): ResponseResult!
  completeInterview(interviewId: ID!): CompleteInterviewResult!
  generateAIFeedback(interviewId: ID!): AIFeedbackResult!
  researchCompany(companyName: String!): CompanyResearchResult!
}
```

#### Core Queries
```graphql
type Query {
  interviewQuestions(category: QuestionCategory, difficulty: DifficultyLevel): [InterviewQuestion!]!
  mockInterviews(userId: ID!): [MockInterview!]!
  companyResearch(companyName: String!): CompanyResearch
  interviewProgress(userId: ID!): InterviewProgressResult!
}
```

## 🔧 API Configuration

### GraphQL Endpoint
```
Development: http://localhost:8001/graphql
Production: https://api.jobquest-navigator.com/graphql
```

### Authentication
```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Rate Limiting
```
- Authenticated: 1000 requests/hour
- Anonymous: 100 requests/hour
- File Upload: 10 files/hour
```

## 📋 Common API Patterns

### Error Handling
```graphql
type BaseResult {
  success: Boolean!
  errors: [String!]!
  message: String
}

type CreateResumeResult implements BaseResult {
  success: Boolean!
  errors: [String!]!
  message: String
  resume: Resume
}
```

### Pagination
```graphql
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
```

### File Upload
```graphql
scalar Upload

type Mutation {
  uploadResumePDF(file: Upload!, userId: ID!): UploadResult!
  uploadProfilePicture(file: Upload!): UploadResult!
}
```

## 🔍 GraphQL Schema Introspection

### Development Tools
- **GraphQL Playground**: http://localhost:8001/graphql (development only)
- **Schema Download**: http://localhost:8001/graphql/schema.graphql
- **Health Check**: http://localhost:8001/health

### Query Examples

#### Resume Management
```graphql
query GetUserResumes($userId: ID!) {
  resumes(userId: $userId) {
    total
    results {
      id
      title
      personalInfo {
        fullName
        email
      }
      skills {
        name
        category
      }
      isDefault
      updatedAt
    }
  }
}

mutation CreateResume($input: CreateResumeInput!) {
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

#### Job Optimization
```graphql
query AnalyzeJobMatch($jobId: ID!, $resumeId: ID!) {
  jobMatch: analyzeJobMatch(jobId: $jobId, resumeId: $resumeId) {
    matchScore
    matchingSkills
    missingSkills
    suggestions
  }
}

mutation CreateJob($input: CreateJobInput!) {
  createJob(input: $input) {
    success
    errors
    jobId
  }
}
```

#### Skills & Learning
```graphql
query GetSkillGapAnalysis($userId: ID!, $targetJobId: ID!) {
  skillGapAnalysis(userId: $userId, targetJobId: $targetJobId) {
    missingSkills {
      name
      importance
      recommendedPaths {
        title
        duration
      }
    }
    matchingSkills {
      name
      proficiency
    }
  }
}

mutation StartLearningPath($pathId: ID!) {
  startLearningPath(pathId: $pathId) {
    success
    progress {
      completedModules
      totalModules
      estimatedCompletion
    }
  }
}
```

#### Interview Guidance
```graphql
query GetInterviewQuestions($category: QuestionCategory!) {
  interviewQuestions(category: $category) {
    id
    question
    tips
    difficulty
  }
}

mutation StartMockInterview($input: StartInterviewInput!) {
  startMockInterview(input: $input) {
    success
    interview {
      id
      questions {
        id
        question
      }
    }
  }
}
```

## 🚀 Integration Examples

### React + Apollo Client
```typescript
import { gql, useQuery, useMutation } from '@apollo/client';

const GET_RESUMES = gql`
  query GetResumes($userId: ID!) {
    resumes(userId: $userId) {
      results {
        id
        title
        updatedAt
      }
    }
  }
`;

const CREATE_RESUME = gql`
  mutation CreateResume($input: CreateResumeInput!) {
    createResume(input: $input) {
      success
      errors
      resume {
        id
        title
      }
    }
  }
`;

export const ResumeManager = ({ userId }) => {
  const { data, loading } = useQuery(GET_RESUMES, { variables: { userId } });
  const [createResume] = useMutation(CREATE_RESUME);
  
  // Component implementation
};
```

### Python Client
```python
import requests

class JobQuestAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}' if token else ''
        }
    
    def create_resume(self, resume_data):
        query = """
        mutation CreateResume($input: CreateResumeInput!) {
          createResume(input: $input) {
            success
            errors
            resume { id title }
          }
        }
        """
        response = requests.post(
            f"{self.base_url}/graphql",
            json={"query": query, "variables": {"input": resume_data}},
            headers=self.headers
        )
        return response.json()
```

## 📊 Performance Considerations

### Query Optimization
- Use DataLoader for N+1 query prevention
- Implement field-level caching
- Limit query depth and complexity
- Use pagination for large datasets

### Caching Strategy
- Redis for session and temporary data
- CloudFront for static content
- GraphQL query result caching
- S3 for file storage with CDN

### Monitoring
- GraphQL query performance tracking
- Error rate monitoring
- Rate limiting analytics
- Usage pattern analysis

---

For implementation details and code examples, see the [technical documentation](../technical/README.md).