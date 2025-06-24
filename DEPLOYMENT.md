# JobQuest Navigator Deployment Guide

## 📋 Overview

This guide covers deployment options for JobQuest Navigator, from development setup to production deployment with Docker, cloud platforms, and CI/CD pipelines.

## 🚀 Quick Deploy Options

### Option 1: Local Development
- ⏱️ **Setup Time**: 10-15 minutes
- 🎯 **Use Case**: Development and testing
- 📦 **Requirements**: Node.js, Python, PostgreSQL

### Option 2: Docker Compose
- ⏱️ **Setup Time**: 5-10 minutes
- 🎯 **Use Case**: Local production simulation
- 📦 **Requirements**: Docker, Docker Compose

### Option 3: Cloud Deployment
- ⏱️ **Setup Time**: 30-60 minutes
- 🎯 **Use Case**: Production deployment
- 📦 **Requirements**: Cloud provider account, domain name

## 🔧 Development Deployment

### Prerequisites
```bash
# System Requirements
- Node.js 16+ and npm
- Python 3.9+ and pip
- PostgreSQL 13+
- Redis (optional, for caching)
- Git
```

### Step 1: Environment Setup
```bash
# Clone repository
git clone https://github.com/your-org/jobquest-navigator.git
cd jobquest-navigator

# Copy environment files
cp .env.example backend/.env
cp .env.example frontend/.env
```

### Step 2: Backend Setup
```bash
cd "10 src/1010main/backend"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database
export DATABASE_URL="postgresql://username:password@localhost:5432/jobquest_dev"

# Run migrations
python manage.py migrate
python manage.py createsuperuser

# Start backend
python manage.py runserver 8000
```

### Step 3: Frontend Setup
```bash
cd "../front-end"

# Install dependencies
npm install

# Configure environment
echo "REACT_APP_GRAPHQL_ENDPOINT=http://localhost:8000/graphql/" > .env

# Start frontend
npm start
```

### Step 4: Verification
```bash
# Test GraphQL endpoint
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'

# Test frontend
open http://localhost:3000
```

## 🐳 Docker Deployment

### Docker Compose Setup

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: jobquest_navigator
      POSTGRES_USER: jobquest_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: 
      context: "./10 src/1010main/backend"
      dockerfile: Dockerfile
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn jobquest_backend.wsgi:application --bind 0.0.0.0:8000"
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://jobquest_user:secure_password@db:5432/jobquest_navigator
      - REDIS_URL=redis://redis:6379/0

  frontend:
    build:
      context: "./10 src/1010main/front-end"
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_GRAPHQL_ENDPOINT=http://localhost:8000/graphql/

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Backend Dockerfile
Create `10 src/1010main/backend/Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run gunicorn
CMD ["gunicorn", "jobquest_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Frontend Dockerfile
Create `10 src/1010main/front-end/Dockerfile`:
```dockerfile
# Build stage
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
```

### Deploy with Docker
```bash
# Build and start services
docker-compose up --build -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# View logs
docker-compose logs -f backend
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Prepare ECR Repositories**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name jobquest-backend
aws ecr create-repository --repository-name jobquest-frontend

# Build and push images
docker build -t jobquest-backend ./backend
docker tag jobquest-backend:latest your-account.dkr.ecr.region.amazonaws.com/jobquest-backend:latest
docker push your-account.dkr.ecr.region.amazonaws.com/jobquest-backend:latest
```

2. **Create ECS Task Definition**
```json
{
  "family": "jobquest-navigator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/jobquest-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/jobquest"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/jobquest-navigator",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster jobquest-cluster \
  --service-name jobquest-service \
  --task-definition jobquest-navigator:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Platform Deployment

#### Using Cloud Run

1. **Prepare Project**
```bash
# Set up gcloud
gcloud config set project your-project-id
gcloud auth configure-docker

# Build and push to GCR
docker build -t gcr.io/your-project-id/jobquest-backend ./backend
docker push gcr.io/your-project-id/jobquest-backend
```

2. **Deploy to Cloud Run**
```bash
# Deploy backend
gcloud run deploy jobquest-backend \
  --image gcr.io/your-project-id/jobquest-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://user:pass@/jobquest?host=/cloudsql/project:region:instance"

# Deploy frontend
gcloud run deploy jobquest-frontend \
  --image gcr.io/your-project-id/jobquest-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku Deployment

1. **Prepare Heroku App**
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create jobquest-navigator

# Add buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs
```

2. **Configure Environment**
```bash
# Set environment variables
heroku config:set DEBUG=False
heroku config:set DATABASE_URL="postgresql://..."
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set OPENAI_API_KEY="your-openai-key"
```

3. **Create Procfile**
```bash
# Create Procfile in root directory
echo "web: gunicorn --pythonpath backend jobquest_backend.wsgi" > Procfile
echo "release: python backend/manage.py migrate" >> Procfile
```

4. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy JobQuest Navigator

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_jobquest
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
    
    - name: Install Python dependencies
      run: |
        cd "10 src/1010main/backend"
        pip install -r requirements.txt
    
    - name: Install Node dependencies
      run: |
        cd "10 src/1010main/front-end"
        npm ci
    
    - name: Run Python tests
      run: |
        cd "10 src/1010main/backend"
        python manage.py test
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_jobquest
    
    - name: Run JavaScript tests
      run: |
        cd "10 src/1010main/front-end"
        npm test -- --coverage --watchAll=false
    
    - name: Build frontend
      run: |
        cd "10 src/1010main/front-end"
        npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push backend image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: jobquest-backend
        IMAGE_TAG: ${{ github.sha }}
      run: |
        cd "10 src/1010main/backend"
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster jobquest-cluster \
          --service jobquest-service \
          --force-new-deployment
```

## 🔒 Production Security

### SSL/TLS Configuration

#### Nginx SSL Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /graphql/ {
        proxy_pass http://backend:8000/graphql/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment Security
```bash
# Production environment variables
DEBUG=False
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

## 📊 Monitoring & Logging

### Application Monitoring

#### Sentry Integration
```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

#### Prometheus Metrics
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### Log Management

#### Structured Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'jobquest.log',
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Issues
```bash
# Database connection errors
python manage.py dbshell  # Test database connection
python manage.py migrate --dry-run  # Check migrations

# Static files not loading
python manage.py collectstatic --clear
python manage.py findstatic filename.css  # Find static file location

# GraphQL schema errors
python manage.py graphql_schema --out schema.json  # Export schema
```

#### Frontend Issues
```bash
# Apollo Client cache issues
localStorage.clear()  # Clear Apollo cache in browser

# Build errors
npm run build -- --verbose  # Verbose build output
npm audit  # Check for vulnerable packages

# GraphQL connection issues
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

#### Docker Issues
```bash
# Container logs
docker-compose logs backend
docker-compose logs frontend

# Container shell access
docker-compose exec backend bash
docker-compose exec frontend sh

# Volume issues
docker-compose down -v  # Remove volumes
docker system prune -a  # Clean up Docker
```

### Performance Optimization

#### Database Optimization
```python
# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'jobquest_navigator',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'MAX_CONNS': 20
        }
    }
}
```

#### Caching Configuration
```python
# Redis caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 📞 Support

### Getting Help
- 📖 **Documentation**: Check README.md and API documentation
- 🐛 **Bug Reports**: Create GitHub issues with detailed reproduction steps
- 💬 **Community**: Join our Discord/Slack community
- 📧 **Email Support**: support@jobquest-navigator.com

### Maintenance Schedule
- **Automated Backups**: Daily at 2 AM UTC
- **Security Updates**: Weekly (Sundays)
- **Feature Deployments**: Bi-weekly (Fridays)
- **Maintenance Windows**: First Sunday of each month, 2-4 AM UTC

---

**Built with ❤️ by the JobQuest Navigator Team**

Last updated: January 2024