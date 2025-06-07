# Technical Design Document (TDD)

## 1. Technology Stack Selection

Based on project requirements and your preferences, the following technology stack is selected:

- **Frontend:** React.js  
- **Backend:** Django (Python, full-featured, powerful ORM, suitable for rapid development and robust microservices)  
- **Backend runtime:** Lambda (serverless deployment for backend services; enables automatic scaling, pay-per-use billing, and simplified infrastructure management. Each microservice or API endpoint can be deployed as an independent Lambda function, integrated with API Gateway for HTTP access. This approach reduces operational overhead and is well-suited for event-driven or microservice architectures.)
- **Database:** MySQL (for all structured data, including users, jobs, applications, certifications, interviews, etc.)  
- **File/Object Storage:** AWS S3 (for all resume files and version history, only metadata stored in MySQL)  
- **Map/Geo Service:** Google Maps API (for geolocation display and geocoding)  
- **AI Service:** OpenAI API (for AI-powered suggestions, interview preparation, etc.)  
- **Job Data API:** Adzuna (the only job data aggregation source for now, extensible in the future)  
- **CI/CD:** GitHub Actions (for automated testing, building, and deployment)
- **CD Environment & Infrastructure:** Provisioned and managed using Terraform
- **API Debugging & Testing:** Performed using Postman

---

## 2. Architecture Design

The system adopts a frontend-backend separation and an API Gateway + microservices architecture. The boundaries of each microservice, external dependencies, and database types are as follows:

- All APIs are uniformly prefixed with `/api/v1/` and routed to each microservice by the API Gateway.
- Authentication is handled by the Auth Service and enforced at the API Gateway.
- All resume files and version history are stored in S3, with only metadata in MySQL.
- Only Adzuna (job data), Google Maps (geolocation), and OpenAI (AI suggestions/interview) are integrated. There is no MongoDB, Canada Job Bank, LinkedIn, Indeed, etc.

```mermaid
flowchart TD
    %% User and Frontend
    User[User]
    Frontend[Web/Mobile Client]
    User --> Frontend

    %% API Gateway
    APIGW[API Gateway]
    Frontend --> APIGW

    %% Microservices
    MS1[Job Data Service]
    MS2[Resume Management Service]
    MS3[AI Suggestion Service]
    MS4[Certification Service]
    MS5[Application Tracking Service]
    MS6[Notification Service]
    MS7[Interview Prep Service]
    MS8[User Profile Service]
    MS9[Auth Service]

    %% API Gateway to Microservices
    APIGW --> MS1
    APIGW --> MS2
    APIGW --> MS3
    APIGW --> MS4
    APIGW --> MS5
    APIGW --> MS6
    APIGW --> MS7
    APIGW --> MS8
    APIGW --> MS9

    %% Databases
    DB1[MySQL DB]
    S3[S3 Storage]

    %% Microservices to Databases
    MS1 --> DB1
    MS2 --> S3
    MS3 --> DB1
    MS4 --> DB1
    MS5 --> DB1
    MS6 --> DB1
    MS7 --> DB1
    MS8 --> DB1
    MS9 --> DB1

    %% External Services
    Ext1[Adzuna API]
    Ext2[Google Map API]
    Ext3[OpenAI API]

    MS1 --> Ext1
    MS1 --> Ext2
    MS7 --> Ext3
    MS3 --> Ext3

    %% Inter-service communication
    MS2 --> MS3
    MS3 --> MS2
    MS5 --> MS2
    MS5 --> MS6
    MS4 --> MS6
    MS8 --> MS9
    MS9 --> MS8

    %% Authorization (dashed line)
    MS1 -.->|auth| MS9
    MS2 -.->|auth| MS9
    MS3 -.->|auth| MS9
    MS4 -.->|auth| MS9
    MS5 -.->|auth| MS9
    MS7 -.->|auth| MS9
    MS8 -.->|auth| MS9
```

For detailed microservice responsibilities, API endpoints, database schema, and S3 path conventions, please refer to the "Detailed Microservices Architecture design.md".

---

## 3. Environment Setup

- Use Docker for consistent development, testing, and production environments.
- Use GitHub Actions for CI/CD automation.
- All services support containerized deployment, making it easy to switch between local and cloud environments.

---

If you need further details for each microservice (API, DB schema, etc.), just let me know!