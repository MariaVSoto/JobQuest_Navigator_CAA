# CLAUDE.md - JNv3 Development Guide

This file provides guidance to Claude Code when working with JobQuest Navigator v3 (JNv3).

## Standard Workflow

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan
4. Then, begin working on the todo items, marking them as complete as you go
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity
7. Finally, add a review section to the todo.md file with a summary of the changes you made and any other relevant information

## Project Overview

JobQuest Navigator v3 (JNv3) is an enterprise-level reorganization of the JobQuest Navigator project featuring:

- **Enterprise Architecture**: Professional project structure with clear separation of concerns
- **Modern Stack**: FastAPI + Strawberry GraphQL + React 19 + TypeScript
- **Infrastructure**: Docker + PostgreSQL + Redis + AWS deployment
- **Documentation**: Centralized and organized technical documentation
- **Development**: Streamlined development workflow with proper tooling

## Architecture Structure

```
JNv3/
├── apps/                    # Application Services
│   ├── backend-fastapi/     # FastAPI + Strawberry GraphQL API
│   ├── frontend-react/      # React 19 + Apollo Client
│   └── shared/              # Shared TypeScript types & utilities
├── infrastructure/          # Deployment and Infrastructure
│   ├── docker/              # Docker compose and configurations
│   ├── terraform/           # AWS infrastructure as code
│   ├── scripts/             # Deployment automation scripts
│   └── k8s/                 # Kubernetes manifests (future)
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

## Development Commands

### Backend (FastAPI + Strawberry GraphQL)
```bash
cd apps/backend-fastapi/

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
cd apps/frontend-react/

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
cd apps/shared/

# Build TypeScript
npm run build
npm run build:watch

# Testing
npm test
npm run test:watch

# Install in other modules
cd ../frontend-react && npm install ../shared
cd ../backend-fastapi && pip install -e ../shared
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

## Key Implementation Notes

### 1. Enterprise-Level Organization
- **Separation of Concerns**: Applications, infrastructure, documentation, and tools are clearly separated
- **Scalable Structure**: Project structure supports multiple applications and services
- **Professional Standards**: Follows enterprise software engineering best practices
- **Maintainability**: Clear organization improves long-term maintenance

### 2. Application Architecture
- **Backend**: FastAPI + Strawberry GraphQL in `apps/backend-fastapi/`
- **Frontend**: React 19 + Apollo Client in `apps/frontend-react/`
- **Shared**: TypeScript types and utilities in `apps/shared/`
- **Type Safety**: Full type safety across the stack

### 3. Infrastructure Management
- **Docker**: Complete development environment in `infrastructure/docker/`
- **Terraform**: AWS infrastructure as code in `infrastructure/terraform/`
- **Scripts**: Deployment automation in `infrastructure/scripts/`
- **Configuration**: Environment configs in `config/environments/`

### 4. Documentation Organization
- **Technical**: Development documentation in `docs/technical/`
- **API**: API documentation in `docs/api/`
- **Deployment**: Deployment guides in `docs/deployment/`
- **Project Management**: Sprint docs in `docs/project-management/`

### 5. Development Workflow
- **Local Development**: Use Docker environment for consistent development
- **Code Quality**: Follow TypeScript/Python best practices
- **Testing**: Comprehensive test coverage across all applications
- **Documentation**: Maintain up-to-date documentation for all changes

## Configuration Files

### Environment Configuration
- **Development**: `config/environments/development.env`
- **Staging**: `config/environments/staging.env`
- **Production**: `config/environments/production.env`

### Application Configuration
- **Backend**: `apps/backend-fastapi/app/core/config.py`
- **Frontend**: `apps/frontend-react/.env`
- **Docker**: `infrastructure/docker/.env`

## File Organization Guidelines

### Application Development
- **Backend changes**: Work in `apps/backend-fastapi/`
- **Frontend changes**: Work in `apps/frontend-react/`
- **Shared types**: Update in `apps/shared/`
- **Tests**: Maintain tests alongside code

### Infrastructure Changes
- **Docker**: Update `infrastructure/docker/`
- **AWS**: Update `infrastructure/terraform/`
- **Deployment**: Update `infrastructure/scripts/`

### Documentation Updates
- **Technical docs**: Update `docs/technical/`
- **API docs**: Update `docs/api/`
- **Deployment**: Update `docs/deployment/`

## Troubleshooting

### Common Issues

1. **Docker Services Not Starting**
   ```bash
   # Check port conflicts
   lsof -i :3001 :8001 :5433 :6380
   
   # Stop and clean
   cd infrastructure/docker
   ./scripts/start-dev.sh stop
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

### JNv3 Migration Status
- ✅ **Enterprise Structure**: Complete professional project organization
- ✅ **Application Migration**: All applications moved to apps/ directory
- ✅ **Infrastructure Organization**: Infrastructure properly separated and organized
- ✅ **Documentation Centralization**: All documentation centralized and categorized
- ✅ **Configuration Management**: Environment configurations properly organized
- ✅ **Project Management**: Deliverables and tasks properly organized

### Next Development Priorities
1. Update import paths and references to new structure
2. Validate all functionality works with new organization
3. Update CI/CD pipeline configurations
4. Create development environment validation scripts
5. Update team documentation and workflows

---

**JobQuest Navigator v3** - Enterprise-level project organization with modern architecture and professional development practices.