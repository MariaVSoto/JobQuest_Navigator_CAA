Technical Design Document (TDD)

1. Technology Stack Selection

   : According to the functional requirements in the PRD (such as Geolocation-Based Job Mapping, AI Suggestion Engine, etc.), select appropriate frontend, backend, database, and third-party services.

   - Frontend: React.js
   - Backend: Django (supports API integration and AI models).
   - Database: MongoDB and MySQL (store job data, user resume versions, etc.).
   - Map Service: Google Maps API (for job map functionality).
   - AI Service: OpenAI API.
   - Third-party API: Canada Job Bank.

2. Architecture Design

   : Design the system architecture to ensure modular development (such as frontend-backend separation, microservice architecture supporting independent development for different Epics).

   - Draw a system architecture diagram to clarify the data flow and interactions between modules (e.g., when a user requests job data, how the map UI interacts with the backend API).

   ```mermaid
   flowchart LR
       %% Client Layer (Frontend)
       subgraph Client Layer
           Frontend[Frontend Application:React.js]
           MapUI[Job Map Interface]
           ResumeUI[Resume Management Interface]
           Dashboard[Dashboard]
           Frontend --> MapUI
           Frontend --> ResumeUI
           Frontend --> Dashboard
       end
   
       %% Application Layer (Backend)
       subgraph Application Layer
           Django[Django Backend:Django REST Framework]
           APIEndpoints[API Endpoints:jobs, resumes, etc.]
           BusinessLogic[Business Logic Modules:Job Processing, Resume Management, etc]
           AsyncTasks[Async Task Processor:Celery + Redis]
           Django --> APIEndpoints
           Django --> BusinessLogic
           Django --> AsyncTasks
       end
   
       %% Data Layer (Database)
       subgraph Data Layer
           MySQL[MySQL:Structured Data: Users, Jobs, Applications]
           MongoDB[MongoDB:Unstructured Data, Resume Versions, AI Suggestions]
       end
   
       %% External Services Layer
       subgraph External Services
           CanadaJobBank[Canada Job Bank API:Job Data]
           GoogleMaps[Google Maps API:Map & Geolocation]
           OpenAI[OpenAI API:AI Suggestions & Interview Questions]
       end
   
       %% Interactions
       %% Frontend to Backend
       Frontend -->|HTTP RESTful API| Django
       MapUI -->|Direct SDK Call| GoogleMaps
   
       %% Backend to Database
       Django -->|Read/Write Structured Data| MySQL
       Django -->|Read/Write Unstructured Data| MongoDB
   
       %% Backend to External Services
       Django -->|Fetch Job Data| CanadaJobBank
       Django -->|Generate AI Suggestions & Questions| OpenAI
       Django -->|Geocoding Support| GoogleMaps
   
       %% Data Flow Example Comments (not displayed in diagram, for reference only)
       %% Job Search Flow: Frontend -> Django -> CanadaJobBank -> MySQL -> Django -> Frontend -> GoogleMaps
       %% Resume Suggestion Flow: Frontend -> Django -> OpenAI -> MongoDB -> Django -> Frontend
   
   ```

3. Environment Setup

   : Set up development, testing, and production environments to ensure team members can work synchronously.

   - Use Docker for environment consistency management.
   - Configure CI/CD tools (such as Jenkins or GitHub Actions) to support continuous integration and deployment.