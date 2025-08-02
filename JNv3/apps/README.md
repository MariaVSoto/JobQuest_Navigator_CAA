# Applications

This directory contains all application services for JobQuest Navigator v3.

## Structure

```
apps/
├── backend-fastapi/     # FastAPI + Strawberry GraphQL API
├── frontend-react/      # React 19 + Apollo Client
└── shared/              # Shared TypeScript types & utilities
```

## Applications

### Backend FastAPI (`backend-fastapi/`)
- **Technology**: FastAPI + Strawberry GraphQL + SQLAlchemy 2.0
- **Database**: PostgreSQL with async support
- **Authentication**: AWS Cognito JWT validation
- **Features**: User management, job creation, GraphQL API

### Frontend React (`frontend-react/`)
- **Technology**: React 19 + Apollo Client + TypeScript
- **Features**: Job management UI, authentication, responsive design
- **GraphQL**: Apollo Client integration with caching

### Shared Module (`shared/`)
- **Technology**: TypeScript
- **Purpose**: Shared types, constants, and utilities
- **Usage**: Imported by both frontend and backend

## Development

### Quick Start
```bash
# Backend
cd backend-fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend  
cd frontend-react
npm install
npm start

# Shared
cd shared
npm install
npm run build
```

### Docker Development
```bash
# Start all applications with Docker
cd ../infrastructure/docker
./scripts/start-dev.sh start
```

See individual application READMEs for detailed development instructions.