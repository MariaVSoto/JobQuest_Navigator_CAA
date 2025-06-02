# API Architecture Diagram

This diagram illustrates the main API endpoints exposed by each microservice in JobQuest Navigator, and their relationships. Core services are highlighted.

```mermaid
flowchart TD
    subgraph API_Gateway
        GW[API Gateway - Gateway Layer]
    end

    subgraph Microservices
        MS1[Job Data Service - core_jobs, core_jobs_id]
        MS2[Resume Management Service - core_resumes, core_resumes_id]
        MS3[AI Suggestion Service - core_suggestions, core_suggestions_id]
        MS4[Certification Service - certifications, certifications_id]
        MS5[Application Tracking Service - applications, applications_id]
        MS6[Notification Service - notifications]
        MS7[Interview Prep Service - interview_prep, interview_prep_id]
        MS8[User Profile Service - users, users_id]
        MS9[Auth Service - auth_login, auth_register, auth_refresh]
    end

    GW --> MS1
    GW --> MS2
    GW --> MS3
    GW --> MS4
    GW --> MS5
    GW --> MS6
    GW --> MS7
    GW --> MS8
    GW --> MS9

    %% Inter-service API calls (examples)
    MS5 -- resumeId --> MS2
    MS2 -- suggestionId --> MS3
    MS5 -- notify --> MS6
    MS8 -- auth --> MS9

    %% External APIs (not shown in detail)
    %% Each microservice may call external APIs as needed

```

---

**API Design Notes:**
- All client requests go through the API Gateway, which routes to the appropriate microservice.
- Each microservice exposes RESTful endpoints for its domain.
- Inter-service communication is handled via internal APIs or message queues.
- Core services' endpoints are prefixed with `/core/` for clarity.
- Authentication and authorization are managed by the Auth Service.

> This architecture ensures clear separation of concerns, scalability, and maintainability for the platform's APIs. 