# Microservices Architecture Diagram

This diagram shows the microservices required to support the business architecture of JobQuest Navigator. Core services are marked with **[Core]**.

```mermaid
flowchart TD
    subgraph User
        A[User: Emily Michael]
    end

    subgraph Frontend
        B[Web/Mobile Client]
    end

    subgraph Microservices
        MS1[Job Data Service Core]
        MS2[Resume Management Service Core]
        MS3[AI Suggestion Service Core]
        MS4[Certification Service]
        MS5[Application Tracking Service Core]
        MS6[Notification Service]
        MS7[Interview Prep Service]
        MS8[User Profile Service Core]
        MS9[Auth Service Core]
    end

    subgraph External Services
        Q[Google for Jobs API]
        R[Jobscan API]
        S[Careerflow API]
        T[Indeed API]
        U[LinkedIn API]
        V[OpenAI API]
    end

    %% User to Frontend
    A --> B

    %% Frontend to Microservices (API Gateway or direct)
    B --> MS1
    B --> MS2
    B --> MS3
    B --> MS4
    B --> MS5
    B --> MS6
    B --> MS7
    B --> MS8
    B --> MS9

    %% Microservices to External Services
    MS1 --> Q
    MS2 --> R
    MS3 --> V
    MS4 --> S
    MS4 --> T
    MS5 --> MS2
    MS5 --> MS6
    MS7 --> U
    MS8 --> MS9

    %% Notification Service can be triggered by others
    MS4 --> MS6
    MS5 --> MS6

    %% Resume Management <-> AI Suggestion
    MS2 --> MS3

    %% Application Tracking <-> Resume Management
    MS5 --> MS2

    %% User Profile <-> Auth
    MS8 --> MS9
```

---

**Core Microservices:**
- **Job Data Service**: Handles job data aggregation and search.
- **Resume Management Service**: Manages resume versions and storage.
- **AI Suggestion Service**: Provides AI-driven resume and job suggestions.
- **Application Tracking Service**: Tracks job applications and statuses.
- **User Profile Service**: Manages user accounts and profiles.
- **Auth Service**: Handles authentication and authorization.

**Supporting Microservices:**
- **Certification Service**: Manages certification roadmap and recommendations.
- **Notification Service**: Sends alerts and updates to users.
- **Interview Prep Service**: Provides company research and interview preparation tools.

> Core services are essential for the platform's main value proposition and user flows. Supporting services enhance user experience and platform functionality. 