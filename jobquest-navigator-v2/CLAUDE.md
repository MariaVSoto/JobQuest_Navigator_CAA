# CLAUDE.md

This file provides guidance to Claude Code when working with JobQuest Navigator v2.


## Standard Workflow

1. First think through the problem , read the codebase for relevant files , and write a plan to tasks / todo.md .

2. The plan should have a list of todo items that you can check off as you complete them

3. Before you begin working , check in with me and I will verify the plan .

4. Then , begin working on the todo items , marking them as complete as you go .

5. Please every step of the way just give me a high level explanation of what changes you made

6. Make every task and code change you do as simple as possible . We want to avoid making any massive or complex changes . Every change should impact as little code as possible . Everything is about simplicity .

7. Finally , add a review section to the todo.md file with a summary of the changes you made and any other relevant information .

## Project Overview

JobQuest Navigator v2 is a **complete migration** from Django/GraphQL to FastAPI/Strawberry GraphQL, featuring:
- **Backend**: FastAPI + Strawberry GraphQL + SQLAlchemy 2.0 + PostgreSQL
- **Frontend**: React 19 + Apollo Client + TypeScript
- **Infrastructure**: Docker + PostgreSQL + Redis + MinIO
- **Shared**: TypeScript types and utilities

## Architecture

```
jobquest-navigator-v2/
├── backend-fastapi-graphql/    # FastAPI + Strawberry GraphQL API
├── frontend-react-minimal/     # React 19 + Apollo Client
├── infrastructure/             # Docker, deployment configs  
├── shared/                     # TypeScript shared types & utils
└── docs/                       # Documentation
```

## Development Commands

### Backend (FastAPI + Strawberry GraphQL)
```bash
cd backend-fastapi-graphql/

# Development server
uvicorn app.main:app --reload --port 8000

# Install dependencies
pip install -r requirements.txt

# Database migrations (Alembic)
alembic upgrade head
alembic revision --autogenerate -m "description"

# Testing
pytest app/tests/
pytest --cov=app --cov-report=html

# Type checking
mypy app/
```

### Frontend (React 19)
```bash
cd frontend-react-minimal/

# Development server
npm start                       # http://localhost:3000

# Install dependencies
npm install

# Build for production
npm run build

# Testing
npm test
npm run test:coverage

# Linting
npm run lint
npm run lint:fix
```

### Shared Module (TypeScript)
```bash
cd shared/

# Build TypeScript
npm run build
npm run build:watch

# Testing
npm test
npm run test:watch

# Install in other modules
cd ../frontend-react-minimal && npm install ../shared
cd ../backend-fastapi-graphql && pip install -e ../shared
```

### Docker Development Environment
```bash
cd infrastructure/docker/

# Start complete development environment
./scripts/start-dev.sh start

# Start with MinIO storage
./scripts/start-dev.sh start --with-storage

# Start minimal (core services only)
./scripts/start-dev.sh start --minimal

# Management commands
./scripts/start-dev.sh status           # Check service status
./scripts/start-dev.sh logs backend     # View backend logs
./scripts/start-dev.sh stop             # Stop all services
./scripts/start-dev.sh clean            # Clean up containers and volumes

# Database management
docker-compose exec db psql -U jobquest_user -d jobquest_navigator_v2
docker-compose exec backend alembic upgrade head

# Backend shell
docker-compose exec backend python
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend npm test
docker-compose exec frontend sh
```

## Service URLs (Development)

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3001 | - |
| **Backend API** | http://localhost:8001 | - |
| **GraphQL Playground** | http://localhost:8001/graphql | - |
| **Database** | localhost:5433 | jobquest_user/jobquest_password_2024 |
| **Redis** | localhost:6380 | password: jobquest_redis_2024 |
| **MinIO Console** | http://localhost:9002 | minioadmin/minioadmin123 |

## Key Changes from v1

### Architecture Migration
- **Django → FastAPI**: REST framework to modern async API
- **Graphene → Strawberry**: GraphQL library upgrade
- **Django ORM → SQLAlchemy 2.0**: Modern async ORM
- **Django Auth → AWS Cognito**: Cloud-native authentication
- **SQLite → PostgreSQL**: Production-ready database

### Simplification
- **Removed Google Maps**: Complex geo features removed
- **Removed External APIs**: No more Adzuna API integration
- **User Input Focus**: Users create and manage their own job data
- **Simplified Location**: Text-based location instead of coordinates

### Type Safety
- **Shared Types**: TypeScript types shared between frontend/backend
- **GraphQL Schema**: Schema-first development
- **Runtime Validation**: Pydantic models for data validation

## File Structure

### Backend (`backend-fastapi-graphql/`)
```
app/
├── main.py                     # FastAPI application entry
├── core/
│   ├── config.py              # Settings with Pydantic
│   └── database.py            # SQLAlchemy async setup
├── models/
│   ├── base.py                # Base model with UUID, timestamps
│   ├── user.py                # User, UserPreference, ActivityLog
│   └── job.py                 # Job, Company, Skill, Application
├── graphql/
│   ├── schema.py              # Main Strawberry schema
│   ├── queries/               # GraphQL query resolvers
│   ├── mutations/             # GraphQL mutation resolvers
│   ├── types/                 # GraphQL type definitions
│   └── auth.py                # Authentication decorators
├── auth/                      # Authentication middleware
└── services/                  # Business logic layer
```

### Frontend (`frontend-react-minimal/`)
```
src/
├── pages/                     # Main application pages
│   ├── CreateJob.jsx          # User job creation (key feature)
│   ├── JobListings.jsx        # Job management
│   ├── Dashboard.jsx          # User dashboard
│   └── ...
├── components/                # Reusable UI components
│   ├── NavBar.jsx             # Navigation
│   └── ProtectedRoute.jsx     # Route protection
├── context/
│   ├── AuthContext.jsx        # Authentication state
│   └── JobContext.jsx         # Job management state
├── services/
│   ├── graphqlAuthService.js  # GraphQL authentication
│   ├── jobService.js          # Job-related API calls
│   └── fallbackService.js     # Mock data for demos
├── apolloClient.js            # GraphQL client configuration
└── utils/                     # Utility functions
```

### Shared (`shared/`)
```
src/
├── types/
│   ├── common.ts              # Base types (UUID, ApiResponse, etc.)
│   ├── user.ts                # User-related types
│   └── job.ts                 # Job-related types (TODO)
├── constants/
│   └── enums.ts               # Shared enums (JobStatus, WorkType, etc.)
├── utils/
│   ├── validation.ts          # Data validation functions
│   └── formatting.ts          # Data formatting utilities
└── index.ts                   # Main exports
```

## Core Features Implementation

### 1. User Job Creation
- **Frontend**: `src/pages/CreateJob.jsx` - Complete form with validation
- **Backend**: `app/graphql/mutations/user_job.py` - GraphQL mutation
- **Types**: `shared/src/types/` - Shared type definitions

### 2. Authentication
- **Frontend**: `src/context/AuthContext.jsx` - React Context
- **Backend**: `app/auth/` - Cognito integration (TODO: complete implementation)
- **GraphQL**: `app/graphql/auth.py` - Authentication decorators

### 3. Job Management
- **Frontend**: `src/pages/JobListings.jsx` - List and manage jobs
- **Backend**: `app/models/job.py` - SQLAlchemy models
- **GraphQL**: `app/graphql/queries/job.py` - Query resolvers

## GraphQL Implementation

### Schema Structure (Strawberry)
```python
@strawberry.type
class User:
    id: UUID
    email: str
    full_name: Optional[str]

@strawberry.type
class Job:
    id: UUID
    title: str
    company: Company
    location_text: Optional[str]
    user_input: bool = True

@strawberry.type
class Query:
    users: List[User]
    jobs: List[Job]

@strawberry.type  
class Mutation:
    create_user_job: UserJobResponse
    update_user: UserResponse
```

### Apollo Client Configuration
```javascript
const client = new ApolloClient({
  uri: process.env.REACT_APP_GRAPHQL_URL || 'http://localhost:8001/graphql',
  cache: new InMemoryCache(),
  headers: {
    Authorization: `Bearer ${token}`
  }
});
```

## Development Workflow

### 1. Start Development Environment
```bash
# Start all services
cd infrastructure/docker
./scripts/start-dev.sh start --with-storage

# Verify services are running
./scripts/start-dev.sh status
```

### 2. Backend Development
```bash
# Work on backend
cd backend-fastapi-graphql

# Install dependencies (if not using Docker)
pip install -r requirements.txt

# Run development server (if not using Docker)
uvicorn app.main:app --reload

# Make database changes
alembic revision --autogenerate -m "add new field"
alembic upgrade head

# Test GraphQL endpoint
curl http://localhost:8001/graphql
```

### 3. Frontend Development
```bash
# Work on frontend
cd frontend-react-minimal

# Install dependencies (if not using Docker)
npm install

# Run development server (if not using Docker)
npm start

# Test GraphQL queries
# Use GraphQL Playground at http://localhost:8001/graphql
```

### 4. Shared Module Development
```bash
# Work on shared types
cd shared

# Build TypeScript
npm run build:watch

# Install in frontend (when types change)
cd ../frontend-react-minimal
npm install ../shared
```

## Database Management

### SQLAlchemy Models
- **BaseModel**: UUID primary key, created_at, updated_at, is_active
- **User**: Extended user model with career info and preferences
- **Job**: User-created jobs with simple location handling
- **Company**: Company information with AI research data
- **Application**: Job application tracking

### Migrations (Alembic)
```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Check current version
docker-compose exec backend alembic current

# Migration history
docker-compose exec backend alembic history
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U jobquest_user -d jobquest_navigator_v2

# Backup database
docker-compose exec db pg_dump -U jobquest_user jobquest_navigator_v2 > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U jobquest_user jobquest_navigator_v2
```

## Authentication System

### Current Implementation
- **Frontend**: JWT token storage in localStorage
- **Apollo Client**: Automatic token injection in headers
- **Backend**: Cognito token validation (TODO: complete)

### AWS Cognito Integration
```python
# Backend configuration (已配置)
COGNITO_USER_POOL_ID = "us-east-1_bISZREFys"
COGNITO_CLIENT_ID = ""  # 运行 ./scripts/setup-cognito.sh 配置

# Middleware for token validation
@strawberry.field
async def protected_field(self, info) -> str:
    user = await get_current_user(info.context.request)
    return f"Hello {user.email}"
```

#### 配置 Cognito App Client
```bash
# 自动配置脚本
./scripts/setup-cognito.sh

# 或手动在 AWS 控制台创建 App Client:
# 1. 访问 AWS Cognito 控制台
# 2. 选择 User pool: us-east-1_bISZREFys
# 3. 创建 App Client
# 4. 复制 Client ID 到配置文件
```

## Testing

### Backend Testing
```bash
# Unit tests
pytest app/tests/

# Integration tests  
pytest app/tests/integration/

# GraphQL tests
pytest app/tests/graphql/

# Coverage
pytest --cov=app --cov-report=html
```

### Frontend Testing
```bash
# Unit tests
npm test

# Component tests
npm test -- --testPathPattern=components

# Integration tests
npm test -- --testPathPattern=integration
```

### End-to-End Testing
```bash
# Basic functionality test
python test_simple_functionality.py

# Full verification
python end_to_end_verification.py
```

## Configuration

### Environment Variables

**Backend** (`.env` in backend-fastapi-graphql/):
```bash
DATABASE_URL=postgresql+asyncpg://jobquest_user:jobquest_password_2024@localhost:5433/jobquest_navigator_v2
REDIS_URL=redis://localhost:6380/0
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# AWS Cognito
COGNITO_USER_POOL_ID=
COGNITO_CLIENT_ID=
AWS_REGION=us-east-1

# CORS
ALLOWED_HOSTS=["http://localhost:3000", "http://localhost:3001"]
```

**Frontend** (`.env` in frontend-react-minimal/):
```bash
REACT_APP_GRAPHQL_URL=http://localhost:8001/graphql
REACT_APP_USE_FASTAPI_JOBS=true
REACT_APP_USE_FASTAPI_AUTH=true
REACT_APP_ENV=development
REACT_APP_DEBUG_MODE=true
```

**Docker** (`.env` in infrastructure/docker/):
```bash
POSTGRES_DB=jobquest_navigator_v2
POSTGRES_USER=jobquest_user
POSTGRES_PASSWORD=jobquest_password_2024
REDIS_PASSWORD=jobquest_redis_2024
```

## Deployment

### Development Deployment
```bash
# Docker development environment
cd infrastructure/docker
./scripts/start-dev.sh start

# Manual development (without Docker)
# Terminal 1: Backend
cd backend-fastapi-graphql
uvicorn app.main:app --reload

# Terminal 2: Frontend  
cd frontend-react-minimal
npm start

# Terminal 3: Database (if needed)
docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
```

### Production Deployment (TODO)
- AWS Lambda deployment with Docker containers
- S3 static website hosting for frontend
- RDS PostgreSQL for database
- ElastiCache Redis for caching

## Key Implementation Notes

### 1. User Job Creation (Core Feature)
This is the **primary feature** replacing external job APIs:
- Users manually input job opportunities they're interested in
- Location is simple text (no Google Maps integration)
- Skills assessment is triggered after job creation
- Company research is available on-demand

### 2. GraphQL Schema Evolution
- Migrated from Graphene (Django) to Strawberry (FastAPI)
- Maintained schema compatibility where possible
- Added user_input field to distinguish user-created jobs

### 3. Authentication Migration
- Moving from Django's built-in auth to AWS Cognito
- JWT tokens for stateless authentication
- Apollo Client handles token management

### 4. Database Simplification
- Removed complex Location models
- Simplified to text-based location handling
- Maintained UUID primary keys for consistency

## Troubleshooting

### Common Issues

1. **Docker Services Not Starting**
   ```bash
   # Check port conflicts
   lsof -i :3001 :8001 :5433 :6380
   
   # Stop conflicting services
   ./scripts/start-dev.sh stop
   
   # Clean up and restart
   ./scripts/start-dev.sh clean
   ./scripts/start-dev.sh start
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   docker-compose ps db
   
   # Check database logs
   docker-compose logs db
   
   # Connect manually
   docker-compose exec db psql -U jobquest_user -d jobquest_navigator_v2
   ```

3. **GraphQL Schema Errors**
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Test GraphQL endpoint
   curl http://localhost:8001/health
   curl http://localhost:8001/graphql
   ```

4. **Frontend Build Issues**
   ```bash
   # Clear node_modules
   cd frontend-react-minimal
   rm -rf node_modules package-lock.json
   npm install
   
   # Check for TypeScript errors
   npm run type-check
   ```

### Health Checks
```bash
# Backend health
curl http://localhost:8001/health

# Database health  
docker-compose exec db pg_isready -U jobquest_user

# Redis health
docker-compose exec redis redis-cli ping

# Frontend health
curl http://localhost:3001
```

## Recent Updates

### Migration Completion Status
- ✅ **Backend Architecture**: FastAPI + Strawberry GraphQL
- ✅ **Frontend Architecture**: React 19 + Apollo Client  
- ✅ **Database**: PostgreSQL + SQLAlchemy 2.0
- ✅ **Docker Environment**: Complete development stack
- ✅ **User Job Creation**: Core feature implemented
- ✅ **Shared Types**: TypeScript type system
- 🔄 **Authentication**: Cognito integration in progress
- 🔄 **Service Layer**: Business logic implementation needed
- 📋 **Deployment**: AWS Lambda deployment scripts needed

### Next Development Priorities
1. Complete authentication middleware implementation
2. Implement remaining service layer business logic
3. Add comprehensive error handling
4. Create production deployment scripts
5. Add monitoring and logging integration

---

**JobQuest Navigator v2** - Modern FastAPI + React architecture with simplified user-focused design. 🚀