# Business Architecture Diagram

This diagram illustrates the main business modules and their relationships in JobQuest Navigator, based on the user flows for job seekers (Emily and Michael).

```mermaid
flowchart TD
    subgraph User
        A[User： EmilyMichael]
    end

    subgraph Frontend
        B[Dashboard]
        C[Job Map]
        D[Resume Management]
        E[Certification Roadmap]
        F[Application Tracker]
        G[Interview Prep Module]
        H[Notifications]
    end

    subgraph Backend
        I[Job Data Service]
        J[Resume Service]
        K[AI Suggestion Engine]
        L[Certification Service]
        M[Application Service]
        N[Notification Service]
        O[Interview Prep Service]
        P[User Profile Service]
    end

    subgraph External Services
        Q[Google for Jobs API]
        R[Jobscan API]
        S[Careerflow API]
        T[Indeed API]
        U[LinkedIn API]
        V[OpenAI API]
    end

    %% User interactions
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    B --> H

    %% Frontend to Backend
    C --> I
    D --> J
    D --> K
    E --> L
    F --> M
    G --> O
    H --> N
    B --> P

    %% Backend to External Services
    I --> Q
    J --> R
    L --> S
    L --> T
    O --> U
    K --> V

    %% Application Service to Resume Service
    M --> J
    %% Application Service to Notification Service
    M --> N

    %% Resume Service to AI Suggestion Engine
    J --> K

    %% Certification Service to Notification Service
    L --> N
```

---

**Key Modules:**
- **Dashboard**: Central hub for navigation.
- **Job Map**: Visual job discovery.
- **Resume Management**: Versioning, editing, and AI suggestions.
- **Certification Roadmap**: Skill gap analysis and certification planning.
- **Application Tracker**: Track job applications and statuses.
- **Interview Prep Module**: Company research and interview practice.
- **Notifications**: Alerts and updates for users.

**Backend Services:**
- Each frontend module communicates with a dedicated backend service, which may integrate with external APIs for data and AI capabilities.

**External Services:**
- Third-party APIs provide job data, resume templates, skill analysis, certification info, company insights, and AI-powered features. 