# Technical Design Document (TDD) – JobQuest Navigator

## Executive Summary
JobQuest Navigator is a modular, microservices-oriented job search and career management platform. The system is built with a clear separation of concerns, leveraging Django REST Framework for backend APIs, React/Next.js for the frontend, and deep AI integration for resume optimization and job recommendations. The architecture supports scalability, maintainability, and future extensibility.

## Tech Stack
- **Backend:** Django REST Framework (DRF), Python 3
- **Frontend:** React, Next.js
- **Database:** MySQL
- **AI Integration:** OpenAI API (for resume suggestions, recommendations, and feedback)
- **Maps:** Google Maps API (for geolocation-based job mapping)

## Epic Progress Overview
- **Epic 1: Geolocation-Based Job Mapping**
  - Status: Implemented
  - Highlights: Adzuna API integration, geospatial queries, map UI, distance filtering, job application/bookmarking.
- **Epic 2: Automated Resume Versioning System**
  - Status: Implemented
  - Highlights: Multi-version resume management, templates, export, sharing, comments, version comparison.
- **Epic 3: AI-Powered Resume Optimization and Smart Recommendations**
  - Status: Implemented
  - Highlights: AI-driven resume suggestions, job matching, user feedback loop, batch operations.
- **Epic 4: Dynamic Certification Roadmap with Market Demand Alerts**
  - Status: Implemented
  - Highlights: Skill analysis, certification mapping, learning paths, market demand alerts, data migration to MySQL.
- **Epic 5: Job Application Tracking with Resume Used**
  - Status: Not implemented (planned for future release)
  - Highlights: Will enable application tracking, resume linkage, and notification system.
- **Epic 6: AI-Driven Company Research and Interview Prep**
  - Status: Implemented
  - Highlights: Company research, AI-generated interview questions, company insights, interview tracking.

## API & Data Layer
- All APIs are unified under `/api/v1/` using DRF ViewSets and Serializers.
- Legacy function-based views are being phased out in favor of class-based views.
- Database schema is standardized across all modules, using UUIDs as primary keys where possible.
- Automated migration scripts are provided for data import/export and schema evolution.

## Security & Testing
- API endpoints are protected with JWT authentication and granular permission checks.
- Sensitive operations are logged and require elevated permissions.
- Automated unit and integration tests are implemented for core modules; test coverage is being improved.
- Security testing includes SQL injection, XSS, and authentication bypass scenarios.

## CI/CD & Environments
- Current: Manual deployment, single environment (production).
- Recommendations: Implement multi-environment support (dev/staging/prod), automated migration/rollback scripts, and CI/CD pipelines for build, test, and deploy.

## Future Work
- Implement Epic 5 (Job Application Tracking) as per PRD.
- Expand end-to-end (E2E) testing coverage.
- Enhance CI/CD automation and environment isolation.
- Continue to optimize AI integration and feedback-driven improvements.

---

*This document reflects the current technical state and future direction of the JobQuest Navigator project. All content is written in English for international collaboration and maintainability.*