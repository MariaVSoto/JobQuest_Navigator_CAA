# JobQuest Navigator v3 - Deployment Documentation

## Overview

JobQuest Navigator v3 deployment guide for the four-core-system architecture with FastAPI + Strawberry GraphQL backend and React 19 frontend.

## 🎯 Deployment Architecture

### Four Core Systems Infrastructure
```
Production Environment:
├── Resume Management System
│   ├── FastAPI Resume API
│   ├── AWS S3 Storage (caa900resume bucket)
│   └── PDF Processing Service
├── Job Optimization System
│   ├── Job Matching Algorithm
│   ├── AI Analysis Service
│   └── External Job Data Integration
├── Skills & Learning System
│   ├── Skills Database
│   ├── Learning Path Engine
│   └── Certification Tracking
└── Interview Guidance System
    ├── Mock Interview Service
    ├── Company Research API
    └── AI Feedback Engine
```

### Technology Stack
```
Backend:
├── FastAPI + Strawberry GraphQL
├── PostgreSQL (Primary Database)
├── Redis (Caching)
├── AWS S3 (File Storage)
└── AWS Cognito (Authentication)

Frontend:
├── React 19 + TypeScript
├── Apollo Client (GraphQL)
├── PWA Support
└── Mobile-First Design

Infrastructure:
├── AWS ECS Fargate
├── Application Load Balancer
├── Route 53 DNS
├── CloudFront CDN
└── Terraform IaC
```

## 🚀 Deployment Environments

### 1. Development Environment

#### Docker Compose Setup
```bash
# Navigate to infrastructure directory
cd JNv3/infrastructure/docker/

# Start development environment
./scripts/start-dev.sh start

# Start with storage services
./scripts/start-dev.sh start --with-storage

# Check service status
./scripts/start-dev.sh status
```

#### Environment Configuration
```env
# Development Environment (.env.development)
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://jobquest_user:jobquest_password_2024@db:5432/jobquest_navigator_v2

# Redis
REDIS_URL=redis://:jobquest_redis_2024@redis:6379/0

# Storage (Development - MinIO)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET_NAME=jobquest-resumes

# Frontend
REACT_APP_GRAPHQL_URL=http://localhost:8001/graphql
REACT_APP_ENVIRONMENT=development
```

#### Service URLs
```
Frontend:     http://localhost:3001
Backend API:  http://localhost:8001
GraphQL:      http://localhost:8001/graphql
Database:     localhost:5433
Redis:        localhost:6380
MinIO:        http://localhost:9002 (Console)
```

### 2. Production Environment

#### AWS Infrastructure
```
Production Stack:
├── ECS Fargate Cluster
│   ├── Backend Service (2-10 instances)
│   └── Frontend Service (2-5 instances)
├── RDS MySQL (Multi-AZ)
├── ElastiCache Redis
├── S3 Bucket (caa900resume)
├── CloudFront Distribution
└── Application Load Balancer
```

#### Terraform Deployment
```bash
# Navigate to Terraform directory
cd JNv3/infrastructure/terraform/

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="environments/production.tfvars"

# Apply infrastructure
terraform apply -var-file="environments/production.tfvars"
```

#### Production Configuration
```env
# Production Environment (.env.production)
ENVIRONMENT=production
DEBUG=false

# Database (RDS)
DATABASE_URL=${AWS_SECRET_MANAGER:jobquest-navigator-v3-production-database-url}
DB_USERNAME=${AWS_SECRET_MANAGER:jobquest-navigator-v3-production-db-username}
DB_PASSWORD=${AWS_SECRET_MANAGER:jobquest-navigator-v3-production-db-password}

# Redis (ElastiCache)
REDIS_URL=${AWS_SECRET_MANAGER:jobquest-navigator-v3-production-redis-url}

# Storage (S3)
AWS_STORAGE_BUCKET_NAME=caa900resume
AWS_S3_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=${AWS_SECRET_MANAGER:jobquest-navigator-v3-production-aws-access-key-id}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_MANAGER:jobquest-navigator-v3-production-aws-secret-access-key}

# Frontend
REACT_APP_GRAPHQL_URL=https://api.jobquest-navigator.com/graphql
REACT_APP_ENVIRONMENT=production
```

## 🔧 Deployment Procedures

### 1. Backend Deployment (FastAPI)

#### Container Build
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### ECS Task Definition
```json
{
  "family": "jobquest-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "jobquest-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:jobquest-production-app-secret-key"
        }
      ]
    }
  ]
}
```

### 2. Frontend Deployment (React)

#### Build Process
```bash
# Frontend build
cd JNv3/apps/frontend-react/

# Install dependencies
npm install

# Build for production
npm run build

# Build Docker image
docker build -t jobquest-frontend .
```

#### CloudFront Distribution
```yaml
# CloudFront Configuration
Origins:
  - Id: S3Origin
    DomainName: jobquest-frontend.s3.amazonaws.com
    S3OriginConfig:
      OriginAccessIdentity: !Ref OriginAccessIdentity
  - Id: APIOrigin
    DomainName: api.jobquest-navigator.com
    CustomOriginConfig:
      HTTPPort: 443
      OriginProtocolPolicy: https-only

Behaviors:
  - PathPattern: "/graphql*"
    TargetOriginId: APIOrigin
    ViewerProtocolPolicy: redirect-to-https
  - PathPattern: "/api/*"
    TargetOriginId: APIOrigin
    ViewerProtocolPolicy: redirect-to-https
  - PathPattern: "*"
    TargetOriginId: S3Origin
    ViewerProtocolPolicy: redirect-to-https
```

### 3. Database Deployment

#### PostgreSQL Setup (RDS)
```sql
-- Database initialization
CREATE DATABASE jobquest_navigator_v3;
CREATE USER jobquest_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE jobquest_navigator_v3 TO jobquest_user;

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
```

#### Migration Process
```bash
# Backend migrations with Alembic
cd JNv3/apps/backend-fastapi/

# Generate migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Verify migration
alembic current
```

### 4. Storage Deployment (AWS S3)

#### S3 Bucket Configuration
```yaml
# S3 Bucket Policy
BucketName: caa900resume
VersioningConfiguration:
  Status: Enabled
LifecycleConfiguration:
  Rules:
    - Id: DeleteIncompleteMultipartUploads
      Status: Enabled
      AbortIncompleteMultipartUpload:
        DaysAfterInitiation: 7
    - Id: MoveToIA
      Status: Enabled
      Transition:
        Days: 30
        StorageClass: STANDARD_IA
CorsConfiguration:
  CorsRules:
    - AllowedHeaders: ['*']
      AllowedMethods: [GET, PUT, POST, DELETE]
      AllowedOrigins: ['https://jobquest-navigator.com']
```

## 🔒 Security Configuration

### 1. AWS Secrets Manager

#### Secret Configuration
```json
{
  "jobquest-navigator-v3-production": {
    "SECRET_KEY": "production-secret-key-256-bit",
    "JWT_SECRET_KEY": "jwt-signing-key",
    "DATABASE_URL": "postgresql://user:pass@rds-endpoint/db",
    "REDIS_URL": "redis://elasticache-endpoint:6379/0",
    "AWS_ACCESS_KEY_ID": "AKIA...",
    "AWS_SECRET_ACCESS_KEY": "...",
    "OPENAI_API_KEY": "sk-...",
    "ADZUNA_API_KEY": "...",
    "GOOGLE_MAPS_API_KEY": "..."
  }
}
```

### 2. GitHub Secrets

#### Repository Secrets
```bash
# Required GitHub Secrets
SECRET_KEY=production-secret-key-256-bit
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=caa900resume
OPENAI_API_KEY=sk-...
ADZUNA_API_KEY=...
GOOGLE_MAPS_API_KEY=...
```

### 3. Network Security

#### VPC Configuration
```yaml
VPC:
  CidrBlock: 10.0.0.0/16
  
Subnets:
  Public:
    - 10.0.1.0/24 (AZ-1)
    - 10.0.2.0/24 (AZ-2)
  Private:
    - 10.0.10.0/24 (AZ-1)
    - 10.0.20.0/24 (AZ-2)

SecurityGroups:
  ALB:
    - Port 80 (HTTP) -> 443 redirect
    - Port 443 (HTTPS) -> ECS
  ECS:
    - Port 8000 -> ALB only
  RDS:
    - Port 5432 -> ECS only
  Redis:
    - Port 6379 -> ECS only
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

#### Backend Pipeline
```yaml
name: Backend CI/CD

on:
  push:
    paths: ['JNv3/apps/backend-fastapi/**']
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd JNv3/apps/backend-fastapi
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd JNv3/apps/backend-fastapi
          pytest --cov=app --cov-report=html
      - name: Security scan
        run: |
          bandit -r JNv3/apps/backend-fastapi/app/
          safety check -r JNv3/apps/backend-fastapi/requirements.txt

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster jobquest-production \
            --service backend-service \
            --force-new-deployment
```

#### Frontend Pipeline
```yaml
name: Frontend CI/CD

on:
  push:
    paths: ['JNv3/apps/frontend-react/**']
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd JNv3/apps/frontend-react
          npm ci
      - name: Run tests
        run: |
          cd JNv3/apps/frontend-react
          npm test -- --coverage --watchAll=false
      - name: Build
        run: |
          cd JNv3/apps/frontend-react
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to S3
        run: |
          aws s3 sync JNv3/apps/frontend-react/build/ \
            s3://jobquest-frontend-bucket/ --delete
      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id E1234567890 --paths "/*"
```

## 📊 Monitoring & Health Checks

### 1. Application Health

#### Health Check Endpoints
```python
# Backend health check
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": await check_database_health(),
            "redis": await check_redis_health(),
            "s3": await check_s3_health()
        }
    }
```

### 2. CloudWatch Monitoring

#### Key Metrics
```yaml
Metrics:
  Application:
    - RequestCount
    - ResponseTime
    - ErrorRate
    - CPUUtilization
    - MemoryUtilization
  
  Database:
    - ConnectionCount
    - QueryPerformance
    - Storage Utilization
  
  Storage:
    - S3 RequestCount
    - S3 ErrorRate
    - Storage Usage
```

### 3. Alerting

#### CloudWatch Alarms
```yaml
Alarms:
  - Name: HighErrorRate
    MetricName: ErrorRate
    Threshold: 5
    ComparisonOperator: GreaterThanThreshold
    EvaluationPeriods: 2
    
  - Name: HighResponseTime
    MetricName: ResponseTime
    Threshold: 2000
    ComparisonOperator: GreaterThanThreshold
    EvaluationPeriods: 3
    
  - Name: DatabaseConnectionHigh
    MetricName: DatabaseConnections
    Threshold: 80
    ComparisonOperator: GreaterThanThreshold
    EvaluationPeriods: 2
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend Service Issues
```bash
# Check ECS service status
aws ecs describe-services --cluster jobquest-production --services backend-service

# Check CloudWatch logs
aws logs get-log-events --log-group-name /ecs/jobquest-backend

# Check health endpoint
curl https://api.jobquest-navigator.com/health
```

#### 2. Database Connection Issues
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier jobquest-production

# Test connection
psql -h rds-endpoint -U jobquest_user -d jobquest_navigator_v3
```

#### 3. Storage Issues
```bash
# Check S3 bucket access
aws s3 ls s3://caa900resume/

# Test upload
aws s3 cp test.txt s3://caa900resume/test/
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_jobs_skills ON jobs USING gin(skills);
CREATE INDEX idx_applications_status ON applications(status);
```

#### 2. Redis Caching
```python
# Cache configuration
CACHE_CONFIG = {
    "resume_cache_ttl": 3600,  # 1 hour
    "job_cache_ttl": 1800,     # 30 minutes
    "skill_cache_ttl": 7200,   # 2 hours
}
```

#### 3. CDN Optimization
```yaml
# CloudFront caching rules
CacheBehaviors:
  - PathPattern: "*.js"
    CachePolicyId: managed-caching-optimized
    TTL: 31536000  # 1 year
  - PathPattern: "*.css"
    CachePolicyId: managed-caching-optimized
    TTL: 31536000  # 1 year
  - PathPattern: "/api/*"
    CachePolicyId: managed-caching-disabled
```

---

For additional deployment details and troubleshooting, see the [technical documentation](../technical/README.md).