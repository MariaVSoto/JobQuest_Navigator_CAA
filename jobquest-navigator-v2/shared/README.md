# JobQuest Navigator v2 - Shared Components

## Overview

This `shared` directory contains common code, types, utilities, and configurations that are used across both frontend and backend components of JobQuest Navigator v2.

## Purpose

The shared module serves several key purposes:

1. **Type Safety**: Common TypeScript interfaces and types
2. **Consistency**: Shared constants, enums, and validation rules
3. **Reusability**: Utility functions used by both frontend and backend
4. **Maintainability**: Single source of truth for common data structures
5. **GraphQL Schema**: Shared GraphQL types and schema definitions

## Module Structure

```
shared/
├── types/              # TypeScript type definitions
│   ├── user.ts         # User-related types
│   ├── job.ts          # Job-related types
│   ├── application.ts  # Application types
│   ├── skill.ts        # Skills and certifications
│   ├── company.ts      # Company types
│   └── common.ts       # Common/base types
├── constants/          # Application constants
│   ├── enums.ts        # Enumeration values
│   ├── config.ts       # Configuration constants
│   ├── validation.ts   # Validation rules
│   └── messages.ts     # Error/success messages
├── utils/              # Utility functions
│   ├── validation.ts   # Data validation helpers
│   ├── formatting.ts   # Data formatting utilities
│   ├── date.ts         # Date manipulation
│   ├── string.ts       # String utilities
│   └── uuid.ts         # UUID generation/validation
├── graphql/            # GraphQL schema definitions
│   ├── schema.graphql  # Main GraphQL schema
│   ├── fragments/      # Reusable GraphQL fragments
│   └── types.ts        # Generated TypeScript from GraphQL
├── errors/             # Error handling
│   ├── codes.ts        # Error codes
│   ├── messages.ts     # Error messages
│   └── types.ts        # Error types
└── package.json        # Shared module dependencies
```

## Key Features

### 1. Type Definitions
- **User Types**: Authentication, profile, preferences
- **Job Types**: Job listings, applications, saved jobs
- **Skill Types**: Skills, certifications, assessments
- **Company Types**: Company profiles, research data

### 2. Constants & Enums
- **Job Status**: draft, published, closed, expired
- **Application Status**: applied, screening, interview, offer, rejected
- **Work Types**: remote, hybrid, onsite, flexible
- **Experience Levels**: entry, junior, mid, senior, lead, manager

### 3. Validation Rules
- **Email Validation**: RFC-compliant email checking
- **Password Strength**: Complexity requirements
- **Data Formats**: Phone, URLs, dates
- **Business Rules**: Salary ranges, experience validation

### 4. Utility Functions
- **Date Formatting**: Consistent date/time display
- **String Processing**: Slugification, sanitization
- **UUID Handling**: Generation and validation
- **Data Transformation**: Format conversion helpers

## Usage Examples

### Frontend (React)
```typescript
import { JobType, ApplicationStatus } from '@jobquest/shared/types';
import { validateEmail, formatSalary } from '@jobquest/shared/utils';
import { JOB_STATUS, WORK_TYPES } from '@jobquest/shared/constants';

// Type-safe job creation
const job: JobType = {
  title: "Senior Python Developer",
  workType: WORK_TYPES.REMOTE,
  status: JOB_STATUS.PUBLISHED
};

// Validation
const isValid = validateEmail("user@example.com");
const displaySalary = formatSalary(120000, "USD");
```

### Backend (FastAPI)
```python
from shared.types import JobStatus, WorkType
from shared.utils import validate_uuid, format_currency
from shared.constants import APPLICATION_STATUSES

# Using shared enums
@strawberry.type
class Job:
    status: JobStatus
    work_type: WorkType
    
# Using shared utilities
def create_job(data: dict):
    if not validate_uuid(data.get('user_id')):
        raise ValueError("Invalid user ID")
```

### GraphQL Schema Sharing
```graphql
# shared/graphql/schema.graphql
enum JobStatus {
  DRAFT
  PUBLISHED
  CLOSED
  EXPIRED
}

type Job {
  id: ID!
  title: String!
  status: JobStatus!
  workType: WorkType!
}
```

## Development Guidelines

### Adding New Shared Components

1. **Types**: Add to appropriate type file in `types/`
2. **Constants**: Add to relevant constant file in `constants/`
3. **Utils**: Create focused utility functions in `utils/`
4. **Validation**: Add validation rules in `utils/validation.ts`

### Best Practices

1. **Immutability**: Prefer immutable data structures
2. **Type Safety**: Use strict TypeScript typing
3. **Documentation**: Document all public interfaces
4. **Testing**: Include unit tests for utilities
5. **Versioning**: Use semantic versioning for changes

### Integration

#### Frontend Integration
```bash
# Install shared module in frontend
cd frontend-react-minimal
npm install ../shared
```

#### Backend Integration
```bash
# Install shared module in backend
cd backend-fastapi-graphql
pip install -e ../shared
```

## Architecture Benefits

### Type Safety
- **Frontend**: TypeScript compilation catches type errors
- **Backend**: Pydantic models ensure data validation
- **GraphQL**: Schema-first development with type generation

### Consistency
- **Data Models**: Same structure across all layers
- **Validation**: Identical rules frontend and backend
- **Error Handling**: Consistent error codes and messages

### Maintainability
- **Single Source**: One place to update shared logic
- **Versioning**: Controlled updates across components
- **Testing**: Centralized testing of common functions

## Dependencies

### Runtime Dependencies
- **TypeScript**: Type definitions
- **GraphQL**: Schema definitions
- **Validator**: Data validation

### Development Dependencies
- **Jest**: Testing framework
- **TSC**: TypeScript compiler
- **ESLint**: Code linting

## Future Enhancements

1. **Multi-language Support**: Internationalization constants
2. **Schema Evolution**: GraphQL schema versioning
3. **Custom Validators**: Business-specific validation rules
4. **Middleware Utilities**: Common request/response handlers
5. **Event Types**: Shared event definitions for real-time features

---

**JobQuest Navigator v2 Shared Module** - Providing type safety, consistency, and reusability across the entire application stack.