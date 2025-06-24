# JobQuest Navigator Backend

Unified Django REST API backend for JobQuest Navigator - Career Application Assistant.

## Project Overview

This Django backend provides a unified API architecture supporting all 5 epics:

- **Epic 1**: Job Search & Geolocation Mapping
- **Epic 2**: Resume Management & Versioning  
- **Epic 3**: AI-Powered Resume Suggestions
- **Epic 4**: Skills Analysis & Certification Roadmap
- **Epic 6**: Company Research & Interview Preparation

## Architecture

### Django Apps Structure

```
backend/
├── jobquest_backend/          # Main Django project
│   ├── settings.py           # Unified configuration
│   ├── urls.py              # API routing
│   └── wsgi.py              # WSGI application
├── core/                    # Shared models & authentication
│   ├── models.py           # User, Location, Company models
│   ├── views.py            # Auth & shared endpoints
│   └── urls.py             # Core API routes
├── jobs/                   # Epic 1: Job Search
├── resumes/               # Epic 2: Resume Management
├── ai_suggestions/        # Epic 3: AI Suggestions
├── skills/               # Epic 4: Skills Analysis
├── certifications/       # Epic 4: Certification Roadmap
└── company_research/     # Epic 6: Company Research
```

### Key Features

- **Unified Database Schema**: UUID-based models with proper relationships
- **JWT Authentication**: Secure token-based authentication
- **API Documentation**: Auto-generated with drf-spectacular
- **Environment Configuration**: Flexible settings for dev/staging/prod
- **CORS Support**: Frontend integration ready
- **Health Checks**: Monitoring endpoints

## API Endpoints

### Core Endpoints
- `POST /api/v1/auth/login/` - User authentication
- `POST /api/v1/auth/register/` - User registration
- `GET /api/v1/user/profile/` - User profile
- `GET /api/v1/locations/` - Location management
- `GET /api/v1/companies/` - Company data

### Epic-Specific Endpoints
- `/api/v1/jobs/` - Job search and management
- `/api/v1/resumes/` - Resume operations
- `/api/v1/ai-suggestions/` - AI-powered suggestions
- `/api/v1/skills/` - Skills analysis
- `/api/v1/certifications/` - Certification roadmaps
- `/api/v1/company-research/` - Company research

### Documentation
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc documentation
- `GET /health/` - Health check

## Setup Instructions

### Prerequisites
- Python 3.9+
- Virtual environment
- SQLite (default) or PostgreSQL/MySQL

### Installation

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment configuration**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Database setup**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Key environment variables (see `env.example`):

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# External APIs
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

## Database Schema

### Core Models
- **User**: Extended user model with career information
- **Location**: Geographic data with coordinates
- **Company**: Company information for jobs and research
- **UserPreference**: User settings and preferences
- **ActivityLog**: User action tracking

### Epic-Specific Models
- **Jobs**: Job postings, applications, alerts
- **Resumes**: Resume data and versioning
- **AI Suggestions**: ML-generated recommendations
- **Skills**: Skill taxonomy and user skills
- **Certifications**: Certification data and roadmaps
- **Company Research**: Research data and insights

## Development Status

### ✅ Completed (Task 3)
- Django project structure setup
- Core models and authentication
- URL routing configuration
- Basic API endpoints (placeholders)
- Database migrations
- Environment configuration
- Health check endpoints

### 🚧 In Progress
- Task 4: Core model implementations
- Task 5: API serializers and views
- Task 6: External API integrations

### 📋 Planned
- Epic-specific model implementations
- AI service integrations
- File upload handling
- Caching with Redis
- Background tasks with Celery
- Production deployment configuration

## Testing

```bash
# Run Django checks
python manage.py check

# Run tests (when implemented)
python manage.py test

# Check migrations
python manage.py showmigrations
```

## API Testing

Access the API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Health Check: http://localhost:8000/health/

## Contributing

1. Follow Django best practices
2. Use proper model relationships
3. Implement comprehensive error handling
4. Add API documentation
5. Write unit tests for new features

## Technology Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: JWT with djangorestframework-simplejwt
- **Documentation**: drf-spectacular
- **File Storage**: Local (dev) / AWS S3 (prod)
- **Caching**: Local memory (dev) / Redis (prod)
- **Background Tasks**: Celery (planned)

## License

This project is part of the JobQuest Navigator application suite. 