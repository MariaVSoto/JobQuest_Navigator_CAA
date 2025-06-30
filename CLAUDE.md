# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JobQuest Navigator is a full-stack job search navigation and career management platform built for AWS serverless deployment. The project uses a Django REST API backend deployed on AWS Lambda with Zappa, and a React frontend hosted on S3.

## Development Commands

### Backend (Django)
```bash
cd backend/
python manage.py runserver                    # Start development server
python manage.py makemigrations              # Create database migrations
python manage.py migrate                     # Apply database migrations
python manage.py collectstatic               # Collect static files
python manage.py test                        # Run Django tests
python manage.py createsuperuser             # Create admin user

# Zappa deployment commands
zappa deploy production                       # Initial Lambda deployment
zappa update production                       # Update Lambda deployment
zappa tail production                         # View Lambda logs
zappa undeploy production                     # Remove Lambda deployment
```

### Frontend (React)
```bash
cd frontend/
npm start                                     # Start development server
npm run build                                # Build for production
npm test                                     # Run tests
npm run eject                                # Eject from create-react-app
```

### Docker Local Development
```bash
cd infrastructure/docker/
./scripts/start-local-env.sh --dev           # Start development environment
./scripts/start-local-env.sh --dev --with-storage     # Start with MinIO storage
./scripts/start-local-env.sh --dev --with-localstack  # Start with LocalStack AWS emulation
./scripts/start-local-env.sh --prod          # Start production-like environment
./scripts/start-local-env.sh --full          # Start with all services (monitoring, etc.)
./scripts/manage.sh migrate                  # Run Django migrations
./scripts/manage.sh createsuperuser          # Create superuser
./scripts/manage.sh test                     # Run tests
./scripts/stop-local-env.sh --clean          # Stop and clean up

# Storage Commands
# MinIO (S3-compatible storage)
docker-compose --profile storage up minio   # Start MinIO only
docker-compose exec backend python manage.py setup_minio_test_data --create-bucket  # Setup test data
docker-compose exec backend python manage.py test_s3_connection  # Test storage connection

# LocalStack (AWS services emulation)
docker-compose --profile localstack up localstack  # Start LocalStack only
docker-compose exec backend python manage.py setup_localstack_test_data --create-bucket  # Setup test data
docker-compose exec backend python manage.py test_localstack_connection  # Test AWS services connection
```

### Full Deployment
```bash
scripts/deploy-infrastructure.sh             # Deploy AWS infrastructure
scripts/deploy-backend.sh                    # Deploy Django backend to Lambda
scripts/deploy-frontend.sh                   # Deploy React frontend to S3
scripts/verify-deployment.sh                 # Verify deployment status
```

## Architecture Overview

### Backend Architecture
- **Framework**: Django 4.2 with Django REST Framework
- **Database**: Uses custom User model in core.models extending AbstractUser
- **Apps Structure**:
  - `core/`: Base models (User, Company, Location), settings, AI services
  - `jobs/`: Job listings, applications, saved jobs, skills
  - `ai_suggestions/`: AI-powered job recommendations
  - `application_tracking/`: Application status tracking
  - `company_research/`: Company research and analysis
  - `resumes/`: Resume builder and management
  - `skills/`: Skills assessment and certification tracking

### Frontend Architecture
- **Framework**: React 19 with React Router for routing
- **State Management**: Context API (AuthContext, JobContext)
- **GraphQL**: Apollo Client for API communication
- **Key Components**:
  - Authentication system with protected routes
  - Job search and mapping functionality
  - Resume builder interface
  - AI suggestions dashboard
  - Company research profiles

### Key Models
- `User`: Extended user model with career info and preferences (core/models.py:31)
- `Job`: Job listings with location, skills, and application tracking (jobs/models.py:125)
- `Company`: Company profiles with AI research integration (core/models.py:205)
- `JobApplication`: User job applications with status tracking (jobs/models.py:189)

## Configuration Files

### Environment Configuration
- `configs/environment.env`: Template for AWS environment variables
- `backend/core/settings.py`: Development Django settings
- `backend/core/settings_production.py`: Production Django settings
- `backend/zappa_settings.json`: Lambda deployment configuration

### Database Setup
The project uses SQLite for development and AWS RDS MySQL for production. Custom User model is defined in `core.models.User`.

## CI/CD Pipeline

### GitHub Actions Workflows
- **Main CI/CD Pipeline** (`.github/workflows/ci-cd-pipeline.yml`): Triggered on push/PR to main/develop
- **Pull Request Checks** (`.github/workflows/pr-checks.yml`): Comprehensive PR validation
- **Security Scanning** (`.github/workflows/security-comprehensive.yml`): Multi-layer security analysis
- **CodeQL Analysis** (`.github/workflows/codeql-analysis.yml`): Static code security scanning
- **Test Environment Deploy** (`.github/workflows/test-environment-deploy.yml`): Automated test environment deployment
- **Manual Deployment** (`.github/workflows/manual-deploy.yml`): Manual deployment workflow

### Security Scanning
- **CodeQL**: Automated code security analysis for Python and JavaScript
- **Dependabot**: Automated dependency vulnerability scanning and updates
- **Bandit**: Python security linting
- **Safety**: Python dependency vulnerability checking
- **Trivy**: Container and filesystem vulnerability scanning
- **Semgrep**: Static Application Security Testing (SAST)
- **TruffleHog**: Secrets detection in git history

### Build & Test Automation
- **Backend**: Django tests with MySQL, coverage reporting, code quality checks
- **Frontend**: React tests with coverage, ESLint, build validation
- **Infrastructure**: Terraform validation, CloudFormation linting

### Deployment Environments
- **Test Environment**: Auto-deployed on develop branch pushes
- **Staging Environment**: Deployed from develop branch after all checks pass
- **Production Environment**: Deployed from main branch with manual approval

### Quality Gates
- Code formatting (Black, isort, Prettier)
- Linting (flake8, ESLint)
- Security scanning must pass
- Test coverage thresholds (80% backend, 70% frontend)
- All tests must pass before deployment

## Docker Local Environment

### Service Architecture
- **Database**: PostgreSQL 15 with extensions (uuid-ossp, pg_trgm, unaccent)
- **Cache**: Redis 7 with persistence
- **Backend**: Django in development/production containers
- **Frontend**: React with Nginx reverse proxy
- **Optional Services**: MailHog, MinIO, Elasticsearch, Prometheus, Grafana

### Development Modes
- **Development Mode**: Hot reload, development tools, source mounting
- **Production Mode**: Optimized builds, production configurations
- **Full Mode**: All services including monitoring and external tools
- **Minimal Mode**: Core services only (database, backend, frontend)

### Service URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Django Admin: http://localhost:8000/admin/
- Database: localhost:5432
- Redis: localhost:6379
- MailHog (email testing): http://localhost:8025
- MinIO Web UI: http://localhost:9001 (minioadmin/minioadmin123)
- MinIO API: http://localhost:9000
- LocalStack (AWS services): http://localhost:4566
- LocalStack Web UI: http://localhost:4566/_localstack/health
- Grafana (monitoring): http://localhost:3001

### Storage Configuration

#### MinIO Storage Configuration
The project uses MinIO as an S3-compatible object storage service for local development:

- **Bucket Name**: `jobquest-resumes`
- **Endpoint**: `http://minio:9000` (Docker network) / `http://localhost:9000` (host)
- **Web UI**: `http://localhost:9001`
- **Credentials**: minioadmin / minioadmin123
- **File Structure**:
  ```
  jobquest-resumes/
  ├── resumes/samples/     # Sample PDF resume files
  ├── resumes/data/        # JSON resume data
  ├── resumes/users/{id}/  # User uploaded files organized by user ID
  └── resumes/config.json  # Storage metadata
  ```

#### LocalStack AWS Services Configuration
The project can use LocalStack for complete AWS services emulation:

- **Endpoint**: `http://localstack:4566` (Docker network) / `http://localhost:4566` (host)
- **Web UI**: `http://localhost:4566/_localstack/health`
- **S3 Console**: `http://localhost:4566/_localstack/s3`
- **Access Key**: `test`
- **Secret Key**: `test`
- **Region**: `us-east-1`
- **Services**: S3, Lambda, API Gateway, RDS, CloudFormation, IAM, STS, CloudWatch
- **File Structure**: Same as MinIO but using LocalStack S3 service

## Development Workflow

1. **Local Development**: 
   - **Traditional**: Use SQLite database with Django runserver for backend and npm start for frontend
   - **Docker with MinIO**: Use `./scripts/start-local-env.sh --dev --with-storage` for S3-compatible storage
   - **Docker with LocalStack**: Use `./scripts/start-local-env.sh --dev --with-localstack` for AWS services emulation
   - **Docker Basic**: Use `./scripts/start-local-env.sh --dev` for complete containerized environment
2. **Pull Request Process**: 
   - Create feature branch from develop
   - All PR checks must pass (tests, security, code quality)
   - Manual review required before merge
3. **Testing**: 
   - Local testing with Docker environment
   - Automated test environment deployment for integration testing
4. **Deployment**: Automated pipeline handles staging and production deployments

## Important Notes

- The project uses UUID primary keys for all models
- Authentication uses Django's built-in system with custom User model
- AI features integrate with OpenAI API for job suggestions and company research
- Frontend uses Apollo Client for GraphQL API communication
- Production deployment uses AWS Lambda with Zappa for serverless architecture
- Security scanning runs on every push/PR and weekly schedules
- Test environments auto-cleanup after 24 hours to save costs
- Docker environment provides full local development stack with PostgreSQL, Redis, and optional services
- Use `infrastructure/docker/scripts/` scripts for easy Docker environment management