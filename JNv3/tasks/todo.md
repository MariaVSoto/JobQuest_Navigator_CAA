# PDF Resume Upload Implementation Plan

## Phase 1: Infrastructure Setup (Priority 1)

### Docker and Storage Infrastructure
- [ ] 1.1 Enable MinIO storage in docker-compose.yml (move from storage profile to default)
- [ ] 1.2 Configure MinIO environment variables for resume storage
- [ ] 1.3 Add MinIO dependency to backend service

### Backend Models and Storage
- [ ] 1.4 Create Resume model in backend (app/models/resume.py)
- [ ] 1.5 Create file storage service abstraction layer 
- [ ] 1.6 Add Resume model to SQLAlchemy initialization
- [ ] 1.7 Create database migration for Resume model

### GraphQL API Foundation
- [ ] 1.8 Create resume GraphQL schema types
- [ ] 1.9 Implement PDF upload mutation
- [ ] 1.10 Implement resume file queries
- [ ] 1.11 Add GraphQL resolvers for resume operations

## Phase 2: Frontend Upload Interface (Priority 1)

### React Components
- [ ] 2.1 Create PDFUploadComponent for file selection and upload
- [ ] 2.2 Add file validation (PDF only, size limits)
- [ ] 2.3 Implement upload progress indicator
- [ ] 2.4 Integrate upload component into ResumeBuilder page

### GraphQL Integration
- [ ] 2.5 Add PDF upload mutations to graphqlResumeService
- [ ] 2.6 Update ResumeBuilder to support uploaded PDFs
- [ ] 2.7 Add error handling for upload failures

## Phase 3: PDF Processing (Priority 2)

### Backend PDF Processing
- [ ] 3.1 Add PDF text extraction library (PyPDF2 or pdfplumber)
- [ ] 3.2 Create PDF parsing service for resume data extraction
- [ ] 3.3 Implement basic resume data mapping (name, email, skills, experience)
- [ ] 3.4 Add mutation for processing uploaded PDF

### Frontend Integration
- [ ] 3.5 Add "Process PDF" button for uploaded files
- [ ] 3.6 Implement form auto-fill from processed PDF data
- [ ] 3.7 Allow users to review and edit extracted data

## Phase 4: Storage Architecture Optimization (Priority 2)

### Environment Configuration
- [ ] 4.1 Create storage configuration system (MinIO dev / S3 prod)
- [ ] 4.2 Add environment-based storage switching
- [ ] 4.3 Implement proper file organization (users/{id}/resumes/)
- [ ] 4.4 Add file cleanup and management features

## Testing and Documentation
- [ ] 5.1 Test PDF upload end-to-end workflow
- [ ] 5.2 Test PDF processing and data extraction
- [ ] 5.3 Verify MinIO integration works correctly
- [ ] 5.4 Document usage instructions for team

## Implementation Notes
- Keep compatibility with existing ResumeBuilder functionality
- Use existing authentication system (AWS Cognito + JWT)
- Follow established patterns in the codebase
- Implement proper error handling throughout
- Start with MVP features, iterate based on feedback

## Technical Stack Compatibility
- Backend: FastAPI + SQLAlchemy + PostgreSQL + MinIO
- Frontend: React 19 + Apollo GraphQL + Material UI components
- Storage: MinIO (development) with S3 migration path (production)
- Authentication: AWS Cognito integration maintained