# JobQuest Navigator v2 - Frontend (React)

## Overview

This is the migrated frontend for JobQuest Navigator v2, featuring:
- **FastAPI + Strawberry GraphQL** backend integration
- **User input-based** job management (no external APIs)
- **Apollo Client** for GraphQL queries and mutations
- **Simplified architecture** without Google Maps or external job APIs

## Architecture Changes

### ✅ Completed Migrations
- **Backend Integration**: Apollo Client configured for FastAPI GraphQL endpoint
- **Authentication**: Support for AWS Cognito tokens 
- **Job Management**: User input job creation and management
- **External APIs Removed**: Google Maps and Adzuna API dependencies removed
- **Dual Endpoint Support**: Can switch between Django/FastAPI during migration

### Key Features
- **User Job Creation**: Complete job input system with validation
- **GraphQL Integration**: All features use GraphQL mutations/queries
- **Fallback System**: Mock data for development and demos
- **Authentication**: JWT/Cognito token management
- **Responsive Design**: Modern UI with CSS styling

## Quick Start

### Prerequisites
- Node.js 18+
- FastAPI backend running on port 8001

### Installation & Setup
```bash
cd jobquest-navigator-v2/frontend-react-minimal
npm install
npm start
```

The application will start on `http://localhost:3000`

### Environment Configuration

Key environment variables in `.env`:
```bash
# FastAPI GraphQL endpoint
REACT_APP_GRAPHQL_URL=http://localhost:8001/graphql

# Enable FastAPI features (v2 mode)
REACT_APP_USE_FASTAPI_JOBS=true
REACT_APP_USE_FASTAPI_AUTH=true

# Development settings
REACT_APP_DEBUG_MODE=true
```

## Project Structure

```
src/
├── components/          # Reusable UI components
├── context/            # React Context providers (Auth, Job)
├── pages/              # Main application pages
├── services/           # API service layer
├── utils/              # Utility functions
├── graphql/            # GraphQL queries and mutations
├── apolloClient.js     # Apollo Client configuration
└── App.js              # Main application component
```

## Key Files & Changes

### Apollo Client (`src/apolloClient.js`)
- **Dual endpoint support**: Django + FastAPI
- **Authentication**: JWT + Cognito token injection
- **Error handling**: GraphQL error logging
- **Caching**: Intelligent data caching

### Services Layer
- **`jobService.js`**: User job CRUD operations
- **`graphqlAuthService.js`**: GraphQL-based authentication
- **`fallbackService.js`**: Mock data for development

### User Job Creation (`src/pages/CreateJob.jsx`)
- **Complete form**: Job title, company, description, salary
- **GraphQL mutations**: `CREATE_USER_JOB` mutation
- **Validation**: Form validation and error handling
- **Location handling**: Simple text-based location input

## Development Features

### Feature Flags
- Switch between Django and FastAPI backends
- Enable/disable specific features during migration
- Debug mode for enhanced logging

### Mock Data System
- Comprehensive fallback data for all features
- Demo mode for presentations
- Development bypass for authentication

### Authentication Modes
- **Production**: AWS Cognito integration
- **Development**: Bypass mode available
- **Migration**: Support for both JWT and Cognito

## API Integration

### GraphQL Queries & Mutations
- **Jobs**: `GET_JOBS`, `CREATE_USER_JOB`, `UPDATE_JOB`
- **Auth**: `LOGIN`, `REGISTER`, `REFRESH_TOKEN`
- **Applications**: `APPLY_TO_JOB`, `GET_APPLICATIONS`

### Error Handling
- GraphQL error catching and display
- Fallback to mock data on API failures
- User-friendly error messages

## Build & Deployment

### Development Build
```bash
npm start                 # Development server
npm run lint             # Code linting
npm run format           # Code formatting
```

### Production Build
```bash
npm run build            # Create production build
npm run test             # Run test suite
```

### Docker Support
- Dockerfile included for containerization
- Nginx configuration for production serving
- Environment variable injection

## Migration Status

### ✅ Completed
- FastAPI GraphQL integration
- User job input system
- Authentication migration
- External API removal
- Frontend service layer

### 🚧 In Progress
- Complete AI features integration
- Skills assessment GraphQL mutations
- Company research user-triggered features

## Dependencies

### Core Dependencies
- **React 19**: Latest React version
- **Apollo Client 3.13**: GraphQL client
- **React Router 6**: Navigation
- **GraphQL 16**: GraphQL support

### Removed Dependencies
- ~~@react-google-maps/api~~ (Removed in v2)
- ~~External job APIs~~ (User input only)

## Configuration

### Environment Variables
All configuration through `.env` file:
- **Backend URLs**: GraphQL endpoint configuration
- **Feature flags**: Enable/disable features
- **Debug settings**: Development mode controls

### Apollo Client Configuration
- **Endpoint selection**: Dynamic backend switching
- **Authentication**: Automatic token injection
- **Caching**: Optimized data management
- **Error handling**: Comprehensive error catching

## Support & Documentation

For additional documentation:
- Backend API: `/docs` endpoint on FastAPI
- GraphQL Schema: GraphQL Playground available
- Component docs: Inline JSDoc comments

---

**JobQuest Navigator v2** - Simplified, user-focused job search platform with modern React architecture.