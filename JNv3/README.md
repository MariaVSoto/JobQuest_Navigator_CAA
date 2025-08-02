# JobQuest Navigator v3 (JNv3)

Enterprise-level reorganization of the JobQuest Navigator project with improved architecture, maintainability, and professional project structure.

## Architecture Overview

```
JNv3/
├── apps/                    # Application Services
│   ├── backend-fastapi/     # FastAPI + Strawberry GraphQL API
│   ├── frontend-react/      # React 19 + Apollo Client
│   └── shared/              # Shared TypeScript types & utilities
├── infrastructure/          # Deployment and Infrastructure
│   ├── docker/              # Docker compose and configurations
│   ├── terraform/           # AWS infrastructure as code
│   ├── k8s/                 # Kubernetes manifests (future)
│   └── scripts/             # Deployment automation scripts
├── config/                  # Environment Configurations
│   ├── environments/        # Environment-specific configs
│   └── secrets/             # Secret management templates
├── docs/                    # Documentation
│   ├── technical/           # Technical documentation
│   ├── api/                 # API documentation
│   ├── deployment/          # Deployment guides
│   └── project-management/  # Sprint docs, deliverables
├── tools/                   # Development and Build Tools
│   ├── ci-cd/              # CI/CD pipeline configurations
│   ├── monitoring/         # Monitoring and logging configs
│   └── testing/            # Testing utilities and configs
└── project/                # Project Management
    ├── deliverables/       # Weekly deliverables and reports
    ├── tasks/              # Task tracking and phase reports
    └── planning/           # Project planning documents
```

## Quick Start

### Prerequisites
- Docker Desktop 4.0+
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Start Development Environment

```bash
# Navigate to infrastructure
cd infrastructure/docker

# Start development environment
./scripts/start-dev.sh start

# Or start with MinIO storage
./scripts/start-dev.sh start --with-storage
```

### Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3001 | - |
| **Backend API** | http://localhost:8001 | - |
| **GraphQL Playground** | http://localhost:8001/graphql | - |
| **Database** | localhost:5433 | jobquest_user/jobquest_password_2024 |
| **Redis** | localhost:6380 | password: jobquest_redis_2024 |
| **MinIO Console** | http://localhost:9002 | minioadmin/minioadmin123 |

## Application Development

### Backend (FastAPI + GraphQL)
```bash
cd apps/backend-fastapi

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Database migrations
alembic upgrade head
```

### Frontend (React 19)
```bash
cd apps/frontend-react

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Shared Module (TypeScript)
```bash
cd apps/shared

# Install dependencies
npm install

# Build TypeScript
npm run build

# Watch mode
npm run build:watch
```

## Key Features

### Technology Stack
- **Backend**: FastAPI + Strawberry GraphQL + SQLAlchemy 2.0 + PostgreSQL
- **Frontend**: React 19 + Apollo Client + TypeScript
- **Infrastructure**: Docker + PostgreSQL + Redis + MinIO
- **Deployment**: AWS Lambda + S3 + RDS + Terraform

### Core Functionality
- User-created job management (no external APIs)
- GraphQL-based API architecture
- JWT authentication with AWS Cognito
- Type-safe shared components
- Comprehensive development environment

## Documentation

### Technical Documentation
- [Setup Guide](docs/technical/README.md)
- [Development Guide](docs/technical/CLAUDE.md)
- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)

### Project Management
- [Weekly Deliverables](docs/project-management/)
- [Task Tracking](project/tasks/)
- [Project Planning](project/planning/)

## Development Workflow

1. **Local Development**: Use Docker environment for full stack development
2. **Code Changes**: Follow architectural patterns and maintain type safety
3. **Testing**: Run comprehensive test suites for both frontend and backend
4. **Documentation**: Update relevant documentation for changes
5. **Deployment**: Use infrastructure scripts for deployment

## Support

### Health Checks
```bash
# Backend health
curl http://localhost:8001/health

# Database connection
docker-compose exec db pg_isready -U jobquest_user

# Frontend health
curl http://localhost:3001
```

### Common Commands
```bash
# View service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Database management
docker-compose exec db psql -U jobquest_user -d jobquest_navigator_v2

# Service status
./infrastructure/docker/scripts/start-dev.sh status
```

---

**JobQuest Navigator v3** - Professional, scalable, enterprise-level job search platform with modern architecture and enhanced developer experience.