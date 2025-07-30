# JobQuest Navigator v3 - Technical Documentation

## 🎯 Project Overview

JobQuest Navigator v3 is an enterprise-level reorganization featuring a comprehensive testing framework and modern architecture:

- ✅ **Modern Stack**: FastAPI + Strawberry GraphQL + React 19
- ✅ **Enterprise Architecture**: Professional project organization
- ✅ **Comprehensive Testing**: 230+ tests across unit, integration, E2E, performance, security
- ✅ **Type Safety**: Full TypeScript integration with shared types
- ✅ **Cloud Ready**: AWS Cognito + PostgreSQL + Redis
- ✅ **Docker Environment**: Complete local development stack

## 🏗️ Architecture

```text
JNv3/
├── apps/                       # Application Services
│   ├── backend-fastapi/        # FastAPI + Strawberry GraphQL API
│   ├── frontend-react/         # React 19 + Apollo Client
│   └── shared/                 # TypeScript shared types & utils
├── infrastructure/             # Deployment and Infrastructure
│   ├── docker/                 # Docker compose and configurations
│   ├── terraform/              # AWS infrastructure as code
│   └── scripts/                # Deployment automation scripts
├── config/                     # Environment Configurations
├── docs/                       # Documentation
│   ├── technical/              # Technical documentation
│   ├── api/                    # API documentation
│   └── deployment/             # Deployment guides
├── tools/                      # Development and Build Tools
├── project/                    # Project Management
└── test/                       # Comprehensive Testing Framework
    ├── backend/                # Backend tests (pytest)
    ├── frontend/               # Frontend tests (Jest/Playwright)
    ├── e2e/                    # End-to-end tests
    ├── performance/            # Performance tests (Locust)
    ├── security/               # Security tests
    └── scripts/                # Test execution scripts
```

## 🧪 Testing Framework

### Comprehensive Test Coverage

JobQuest Navigator v3 features a production-ready testing framework with:

- **230+ Test Cases** - Exceeding the 200+ target across all modules
- **Multi-Layer Testing** - Unit, Integration, E2E, Performance, Security
- **Professional Tools** - pytest, Jest, Playwright, Locust, Bandit/Safety
- **CI/CD Integration** - GitHub Actions with quality gates
- **Coverage Reporting** - 85%+ backend, 80%+ frontend targets

### Quick Testing Commands

```bash
# Navigate to test directory
cd test

# Setup test environment
./scripts/setup-test-env.sh

# Run all tests
./scripts/run-all-tests.sh

# Run specific test types
./scripts/run-all-tests.sh --backend-only
./scripts/run-all-tests.sh --frontend-only
./scripts/run-all-tests.sh --e2e-only
./scripts/run-all-tests.sh --quick
```

### Test Categories

| Test Category | Count | Coverage | Tools |
|---------------|-------|----------|-------|
| **Backend Unit Tests** | 60+ | 85%+ | pytest, Factory Boy |
| **Frontend Unit Tests** | 60+ | 80%+ | Jest, React Testing Library |
| **Integration Tests** | 60+ | - | pytest, MSW |
| **E2E Tests** | 25+ | - | Playwright |
| **Performance Tests** | 10+ | - | Locust |
| **Security Tests** | 15+ | - | Bandit, Safety, Semgrep |

### Technology Stack

**Backend:**
- FastAPI 0.104+ (Python 3.11)
- Strawberry GraphQL 0.213+
- SQLAlchemy 2.0 (async)
- PostgreSQL 15
- Redis 7
- AWS Cognito Authentication

**Frontend:**
- React 19
- Apollo Client 3.13
- TypeScript 5.3
- Modern CSS

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL + Redis
- MinIO (S3-compatible storage)
- Nginx (production)

## 🚀 Quick Start

### Prerequisites
- Docker Desktop 4.0+
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Start Development Environment

```bash
# Clone and navigate
git clone <repository>
cd jobquest-navigator-v2

# Start full Docker environment
cd infrastructure/docker
./scripts/start-dev.sh start

# Or start with storage
./scripts/start-dev.sh start --with-storage
```

### 2. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3001 | - |
| **Backend API** | http://localhost:8001 | - |
| **GraphQL Playground** | http://localhost:8001/graphql | - |
| **Database** | localhost:5433 | jobquest_user/jobquest_password_2024 |
| **Redis** | localhost:6380 | password: jobquest_redis_2024 |
| **MinIO Console** | http://localhost:9002 | minioadmin/minioadmin123 |

### 3. Development Commands

```bash
# Backend development
cd backend-fastapi-graphql
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend development  
cd frontend-react-minimal
npm install
npm start

# Shared module
cd shared
npm install
npm run build
```

## 📊 Migration Status

### ✅ Completed Features

1. **Architecture Migration** (100%)
   - ✅ FastAPI + Strawberry GraphQL backend
   - ✅ React 19 frontend with Apollo Client
   - ✅ PostgreSQL + Redis infrastructure
   - ✅ Docker development environment

2. **Core Features** (95%)
   - ✅ User authentication (Cognito ready)
   - ✅ User job creation and management
   - ✅ GraphQL queries and mutations
   - ✅ Type-safe shared components

3. **User Experience** (90%)
   - ✅ Job creation form with validation
   - ✅ Job listings and management
   - ✅ Responsive design
   - ✅ Error handling and loading states

4. **Development Tools** (100%)
   - ✅ Docker Compose configuration
   - ✅ Hot reload for development
   - ✅ Health checks and monitoring
   - ✅ Shared TypeScript types

### 🔄 Key Changes from v1

| Aspect | v1 (Django) | v2 (FastAPI) |
|--------|-------------|--------------|
| **Backend** | Django + Graphene | FastAPI + Strawberry |
| **Database** | SQLite/PostgreSQL | PostgreSQL (async) |
| **Auth** | Django JWT | AWS Cognito |
| **Job Data** | External APIs | User Input Only |
| **Location** | Google Maps + complex geo | Simple text location |
| **Deployment** | Zappa + Lambda | Docker + Lambda (ready) |
| **Types** | Python only | Shared TypeScript/Python |

## 🎯 Design Principles

### 1. **Simplification**
- ❌ Removed Google Maps complexity
- ❌ Removed external job APIs (Adzuna)
- ✅ Focus on user input and management

### 2. **Type Safety**
- ✅ Shared TypeScript types
- ✅ GraphQL schema first
- ✅ Runtime validation

### 3. **User-Centric**
- ✅ User creates and manages their job opportunities
- ✅ Skills assessment after job input
- ✅ Company research on-demand

### 4. **Cloud Native**
- ✅ Containerized development
- ✅ AWS Cognito authentication
- ✅ Scalable architecture

## 📁 Project Structure

### Backend (`backend-fastapi-graphql/`)
```
app/
├── main.py                 # FastAPI application entry
├── core/                   # Configuration and database
│   ├── config.py          # Settings management
│   └── database.py        # Database connection
├── models/                 # SQLAlchemy models
│   ├── user.py            # User, preferences, activity
│   ├── job.py             # Jobs, applications, skills
│   └── base.py            # Base model with common fields
├── graphql/                # GraphQL implementation
│   ├── schema.py          # Main schema
│   ├── queries/           # GraphQL queries
│   ├── mutations/         # GraphQL mutations
│   └── types/             # GraphQL type definitions
├── auth/                   # Authentication middleware
└── services/               # Business logic services
```

### Frontend (`frontend-react-minimal/`)
```
src/
├── pages/                  # Main application pages
├── components/             # Reusable UI components
├── context/                # React Context providers
├── services/               # API service layer
├── apolloClient.js         # GraphQL client config
└── utils/                  # Utility functions
```

### Shared (`shared/`)
```
src/
├── types/                  # TypeScript type definitions
├── constants/              # Enums and constants
├── utils/                  # Validation and formatting
└── index.ts                # Main exports
```

## 🔧 Development

### Backend Development
```bash
cd backend-fastapi-graphql

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Type checking
mypy app/
```

### Frontend Development
```bash
cd frontend-react-minimal

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Shared Module Development
```bash
cd shared

# Install dependencies
npm install

# Build TypeScript
npm run build

# Run tests
npm test

# Watch mode
npm run build:watch
```

## 🐳 Docker Development

### Available Profiles
```bash
# Core services only
docker-compose up -d

# With MinIO storage
docker-compose --profile storage up -d

# With development tools
docker-compose --profile development up -d

# Production-like with Nginx
docker-compose --profile production up -d
```

### Management Commands
```bash
# Database management
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic revision --autogenerate -m "description"

# Application commands
docker-compose exec backend python -c "from app.main import app; print('Backend ready')"
docker-compose exec frontend npm test

# Logs and debugging
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔒 Authentication

### AWS Cognito Integration
```python
# Backend configuration
COGNITO_USER_POOL_ID = "us-east-1_xxxxxxxxx"
COGNITO_CLIENT_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxx"
AWS_REGION = "us-east-1"
```

### JWT Token Flow
1. User authenticates with Cognito
2. Receives JWT token
3. Frontend stores token
4. Apollo Client includes token in GraphQL requests
5. Backend validates token with Cognito

## 🚀 Deployment

### Development
```bash
# Start all services
./infrastructure/docker/scripts/start-dev.sh start

# Check status
./infrastructure/docker/scripts/start-dev.sh status

# Stop all services
./infrastructure/docker/scripts/start-dev.sh stop
```

### Production (AWS Lambda)
```bash
# Build Docker images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy to AWS (future)
# TODO: Add Lambda deployment scripts
```

## 📚 Documentation Index

### Core Framework Documentation

- **[TESTING_FRAMEWORK.md](TESTING_FRAMEWORK.md)** - Comprehensive testing framework documentation
- **[TESTING_QUICK_START.md](TESTING_QUICK_START.md)** - Quick start guide for testing
- **[INSTALLATION.md](INSTALLATION.md)** - Installation and setup instructions
- **[DEPLOYMENT-STATUS.md](DEPLOYMENT-STATUS.md)** - Current deployment status

### Development Guides

- **[COGNITO_SETUP.md](COGNITO_SETUP.md)** - AWS Cognito authentication setup
- **[GRAPHQL_SCHEMA_FIXES.md](GRAPHQL_SCHEMA_FIXES.md)** - GraphQL schema implementation details
- **[FRONTEND_RESTRUCTURING_SUMMARY.md](FRONTEND_RESTRUCTURING_SUMMARY.md)** - Frontend architecture updates

### Testing Infrastructure

The project now includes a comprehensive testing framework with:

- **230+ Test Cases** - Unit, integration, E2E, performance, and security tests
- **Multi-Layer Testing** - Backend (pytest), Frontend (Jest), E2E (Playwright)
- **Coverage Reporting** - 85%+ backend, 80%+ frontend coverage targets
- **CI/CD Integration** - Automated testing with quality gates
- **Professional Tools** - Locust (performance), Bandit/Safety (security)

### Project Status Reports

- **[test_results_summary.md](test_results_summary.md)** - Historical test results
- **[PHASE3_PERFORMANCE_VALIDATION_REPORT.md](PHASE3_PERFORMANCE_VALIDATION_REPORT.md)** - Performance validation
- **[DEPLOYMENT_ERRORS_LOG.md](DEPLOYMENT_ERRORS_LOG.md)** - Deployment troubleshooting

## 🧪 Testing Framework Usage

### Complete Test Suite

```bash
# Execute all tests
cd test
./scripts/run-all-tests.sh
```

### Targeted Testing

```bash
# Backend tests only
./scripts/run-all-tests.sh --backend-only

# Frontend tests only
./scripts/run-all-tests.sh --frontend-only

# End-to-end tests only
./scripts/run-all-tests.sh --e2e-only

# Performance tests
./scripts/run-all-tests.sh --performance

# Security tests
./scripts/run-all-tests.sh --security

# Quick validation (unit tests only)
./scripts/run-all-tests.sh --quick

# CI/CD optimized run
./scripts/run-all-tests.sh --ci
```

### Test Environment Management

```bash
# Setup test environment
./scripts/setup-test-env.sh

# Cleanup test environment
./scripts/cleanup-test-env.sh

# View coverage reports
open test/reports/coverage/backend/html/index.html
open test/reports/coverage/frontend/html/index.html
```

## 📋 Migration Checklist

### ✅ Completed
- [x] FastAPI + Strawberry GraphQL backend
- [x] React 19 frontend with Apollo Client
- [x] Shared TypeScript types and utilities
- [x] Docker development environment
- [x] User job creation functionality
- [x] PostgreSQL + Redis infrastructure
- [x] Health checks and monitoring
- [x] CORS and security configuration

### 🔄 In Progress
- [ ] Complete authentication middleware
- [ ] Database migrations with Alembic
- [ ] Full service layer implementation
- [ ] Comprehensive error handling
- [ ] Production deployment scripts

### 📋 Future Enhancements
- [ ] GraphQL subscriptions for real-time updates
- [ ] Advanced caching strategies
- [ ] Monitoring and logging integration
- [ ] Performance optimization
- [ ] Security auditing

## 💡 Key Benefits

### For Developers
- **Type Safety**: Shared types prevent runtime errors
- **Modern Stack**: Latest versions of all frameworks
- **Hot Reload**: Fast development cycle
- **GraphQL**: Single endpoint, efficient queries

### For Users
- **Simplified UX**: Focus on user input vs external complexity
- **Fast Performance**: Optimized queries and caching
- **Reliable**: Reduced external dependencies
- **Responsive**: Modern React 19 features

### For Operations
- **Container Ready**: Docker-first development
- **Cloud Native**: AWS Cognito, Lambda ready
- **Monitoring**: Health checks and logging
- **Scalable**: Microservice-ready architecture

## 🆘 Support

### Documentation
- [Technical Design](docs/Technical-Design-Document-v2.md)
- [User Flow Design](docs/User-Flow-Design-v2.md)
- [Docker Setup Guide](infrastructure/docker/README.md)

### Getting Help
1. Check Docker services: `./scripts/start-dev.sh status`
2. View logs: `docker-compose logs -f [service]`
3. Health checks: `curl http://localhost:8001/health`
4. Database connection: `docker-compose exec backend python -c "from app.core.database import engine; print('DB OK')"`

### Common Issues
- **Port conflicts**: Use different ports in .env
- **Database connection**: Check PostgreSQL is running
- **CORS errors**: Verify allowed_hosts in config
- **GraphQL errors**: Check schema compilation

---

**JobQuest Navigator v2** - Modern, type-safe, user-focused job search platform with simplified architecture and enhanced developer experience. 🚀