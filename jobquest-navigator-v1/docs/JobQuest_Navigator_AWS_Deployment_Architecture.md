# JobQuest Navigator - AWS Deployment Architecture Design Document

## 📋 Project Overview

**Project Name**: JobQuest Navigator  
**Project Type**: Graduation Design Project  
**Deployment Environment**: AWS Staging Environment  
**Design Goals**: Simplified deployment, cost optimization, academic demonstration

---

## 🏗️ Architecture Overview

### Design Principles
- **Simplicity First**: Focus on functional implementation, not considering high availability and elasticity
- **Cost Optimization**: Use the most economical AWS service combination
- **Academic Orientation**: Suitable for graduation design demonstration and testing needs
- **Ease of Management**: Minimize operational complexity

### Core Components
```
┌─────────────────────────────────────────────────────────────┐
│                     AWS Cloud Architecture                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React)          Backend (Django)                 │
│  ┌─────────────────┐      ┌─────────────────────────────┐   │
│  │   Amazon S3     │      │     AWS Lambda              │   │
│  │   Static Site   │◄────►│   Django REST API          │   │
│  │   Hosting       │      │   (Zappa Deployment)       │   │
│  └─────────────────┘      └─────────────────────────────┘   │
│                                      │                      │
│                                      ▼                      │
│                            ┌─────────────────────────────┐   │
│                            │     Amazon RDS              │   │
│                            │     MySQL Database          │   │
│                            │     (db.t3.micro)          │   │
│                            └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Detailed Component Design

### 1. Frontend Deployment - Amazon S3 Static Website

**Service**: Amazon S3 + CloudFormation (simplified CDN)
**Configuration**:
```yaml
Bucket Configuration:
  Name: jobquest-navigator-frontend
  Region: us-east-1
  Static Website Hosting: Enabled
  Public Read Access: Enabled
  Index Document: index.html
  Error Document: index.html (SPA routing)
```

**Deployment Process:**
1. Build React app: `npm run build`
2. Upload build artifacts to S3
3. Configure S3 Bucket policy to allow public read
4. Enable Static Website Hosting

### 2. Backend Deployment - AWS Lambda + Zappa

**Service**: AWS Lambda + API Gateway
**Configuration**:
```json
{
  "production": {
    "app_function": "core.wsgi.application",
    "aws_region": "us-east-1",
    "runtime": "python3.9",
    "timeout_seconds": 300,
    "memory_size": 512,
    "keep_warm": false,
    "environment_variables": {
      "DJANGO_SETTINGS_MODULE": "core.settings_production",
      "LAMBDA_DEPLOYMENT": "true"
    }
  }
}
```

**Features:**
- Pay-per-request, extremely low cost
- Automatic scaling, no server management
- API Gateway provides RESTful API endpoints
- Suitable for academic projects with medium/low traffic

### 3. Database - Amazon RDS MySQL

**Instance Specs:**
```yaml
Engine: MySQL 8.0
Instance Class: db.t3.micro (1 vCPU, 1GB RAM)
Storage: 20GB gp2 (General Purpose SSD)
Multi-AZ: Disabled (cost optimization)
Backup Retention: 7 days
Publicly Accessible: No (security consideration)
VPC: Default VPC
Security Group: Lambda-RDS-SG
```

**Connection Configuration:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jobquest_navigator',
        'USER': 'admin',
        'PASSWORD': '${RDS_PASSWORD}',
        'HOST': 'jobquest-db.cluster-xxxxx.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }
}
```

### 4. File Storage - Amazon S3

**Static File Storage:**
```yaml
Bucket: jobquest-navigator-static
Purpose: Django static files, user uploads
Access: Private with signed URLs
Lifecycle: Standard storage class
```

**Django Configuration:**
```python
STATIC_URL = 'https://jobquest-navigator-static.s3.amazonaws.com/static/'
MEDIA_URL = 'https://jobquest-navigator-static.s3.amazonaws.com/media/'
```

---

## 🌐 Network Architecture

### VPC Configuration
```yaml
VPC: Default VPC (simplified network management)
Subnets: 
  - Public Subnet (us-east-1a)
  - Public Subnet (us-east-1b)
Security Groups:
  - Lambda-RDS-SG: Lambda access to RDS
  - RDS-SG: RDS inbound rule (3306 from Lambda)
```

### Security Group Rules
```yaml
Lambda Security Group:
  Outbound: 
    - All traffic to 0.0.0.0/0 (HTTPS, MySQL)

RDS Security Group:
  Inbound:
    - Port 3306 from Lambda Security Group
  Outbound:
    - All traffic denied (default)
```

---

## 🔑 Environment Variable Configuration

### AWS Lambda Environment Variables
```bash
# Django configuration
DJANGO_SETTINGS_MODULE=core.settings_production
DJANGO_SECRET_KEY=${SECRET_KEY}
DEBUG=False
LAMBDA_DEPLOYMENT=True

# Database configuration
RDS_HOSTNAME=${RDS_ENDPOINT}
RDS_DB_NAME=jobquest_navigator
RDS_USERNAME=admin
RDS_PASSWORD=${RDS_PASSWORD}
RDS_PORT=3306

# AWS service configuration
AWS_STORAGE_BUCKET_NAME=jobquest-navigator-static
AWS_S3_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

# Frontend CORS configuration
CORS_ALLOWED_ORIGINS=https://jobquest-navigator-frontend.s3-website-us-east-1.amazonaws.com
```

---

## 📦 Deployment Process

### 1. Infrastructure Preparation

#### RDS Database Creation
```bash
# 1. Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier jobquest-navigator-db \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password ${RDS_PASSWORD} \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --db-name jobquest_navigator

# 2. Wait for instance to be available
aws rds wait db-instance-available \
  --db-instance-identifier jobquest-navigator-db
```

#### S3 Bucket Creation
```bash
# 1. Create frontend static website bucket
aws s3 mb s3://jobquest-navigator-frontend
aws s3 website s3://jobquest-navigator-frontend \
  --index-document index.html \
  --error-document index.html

# 2. Create static resource bucket
aws s3 mb s3://jobquest-navigator-static

# 3. Configure CORS and access policy
aws s3api put-bucket-cors --bucket jobquest-navigator-static \
  --cors-configuration file://cors-config.json
```

### 2. Backend Deployment

#### Django Application Preparation
```bash
# 1. Install dependencies
pip install -r requirements_production.txt

# 2. Database migration
python manage.py migrate --settings=core.settings_production

# 3. Collect static files
python manage.py collectstatic --noinput --settings=core.settings_production
```

# 4. Create superuser (optional)
python manage.py createsuperuser --settings=core.settings_production
```

#### Zappa Deployment Configuration
```bash
# 1. Initialize Zappa
zappa init

# 2. Deploy to Lambda
zappa deploy production

# 3. Update deployment
zappa update production

# 4. Set environment variables
zappa set_env production DJANGO_SECRET_KEY=${SECRET_KEY}
zappa set_env production RDS_HOSTNAME=${RDS_ENDPOINT}
# ... other environment variables
```

### 3. Frontend Deployment

#### React App Build
```bash
# 1. Install dependencies
npm install

# 2. Configure production environment variables
echo "REACT_APP_API_URL=${API_GATEWAY_URL}" > .env.production

# 3. Build production version
npm run build

# 4. Deploy to S3
aws s3 sync build/ s3://jobquest-navigator-frontend

# 5. Invalidate cache (if using CloudFront)
aws cloudfront create-invalidation \
  --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
  --paths "/*"
```

---

## 💰 Cost Estimation

### Monthly Cost Estimate (US East 1)

| Service | Specs | Monthly Cost (USD) |
|------|------|-------------|
| **RDS MySQL** | db.t3.micro | ~$15 |
| **Lambda** | 1M requests/month | ~$2 |
| **API Gateway** | 1M requests/month | ~$3 |
| **S3 Standard** | 5GB storage | ~$0.12 |
| **S3 Requests** | 10K requests | ~$0.05 |
| **Data Transfer** | 10GB outbound | ~$0.90 |
| **CloudWatch Logs** | 1GB logs | ~$0.50 |
| **Total** | | **~$21.57/month** |

### Annual Budget
```
Total annual fee: ~$259
AWS Free Tier Discount: -$120 (RDS and Lambda)
Actual annual fee: ~$139
```

**Note**: Costs can be further optimized by:
- Using AWS Free Tier
- Setting downtime schedules (pause RDS during development)
- Using reserved instances (for long-term projects)

---

## 🔄 CI/CD Pipeline (Optional)

### GitHub Actions Workflow
```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements_production.txt
        pip install zappa
    
    - name: Deploy to Lambda
      run: |
        zappa update production
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install and build
      run: |
        npm ci
        npm run build
    
    - name: Deploy to S3
      run: |
        aws s3 sync build/ s3://jobquest-navigator-frontend
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## 🔍 Monitoring and Logging

### CloudWatch Monitoring
```yaml
Monitoring metrics:
  - Lambda execution time and error rate
  - API Gateway request count and latency
  - RDS connection count and CPU usage
  - S3 storage usage

Alarm settings:
  - Lambda error rate > 5%
  - RDS CPU usage > 80%
  - API Gateway 5xx errors > 10/5min
```

### Logging Configuration
```python
# Django logging configuration
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

---

## 🔒 Security Configuration

### Access Control
```yaml
IAM roles and policies:
  Lambda execution role:
    - VPC access
    - RDS connection
    - S3 read/write
    - CloudWatch logs

S3 bucket policy:
  - Frontend bucket: public read
  - Static resource bucket: private access
  - CORS configuration allows frontend domain
```

### Network Security
```yaml
Security group configuration:
  - RDS only allows Lambda access
  - Lambda outbound access restricted
  - All sensitive ports closed

Environment variable encryption:
  - All keys encrypted with AWS KMS
  - Database password stored via Parameter Store
```

---

## 📝 Deployment Checklist

### Pre-deployment Check
- [ ] AWS CLI configured
- [ ] Environment variables ready
- [ ] Database migration files verified
- [ ] Static file collection tested
- [ ] CORS configuration checked
- [ ] Domain DNS set (if needed)

### Post-deployment Verification
- [ ] API endpoint responds normally
- [ ] Database connection successful
- [ ] Static files load correctly
- [ ] Frontend fully tested
- [ ] Error logs checked
- [ ] Performance benchmarked

### Production Readiness Check
- [ ] Backup strategy configured
- [ ] Monitoring alarms set
- [ ] Security scan passed
- [ ] Cost budget confirmed
- [ ] Documentation updated
- [ ] Team access configured

---

## 🎓 Graduation Design Considerations

### Demo Preparation
1. **Feature demo script**: Prepare a complete user journey demo
2. **Technical architecture diagram**: Visualize AWS architecture design
3. **Performance test report**: Basic load test results
4. **Cost analysis**: Detailed deployment cost analysis

### Documentation Deliverables
- [x] Architecture design document (this document)
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Deployment operations manual
- [ ] Troubleshooting guide
- [ ] User manual

### Technical Highlights
- **Modern architecture**: Serverless + microservices
- **Cloud-native design**: Fully utilizes AWS services
- **Cost-effective**: Economic solution for small-scale projects
- **Scalability**: Architecture supports future feature expansion

---

## 📞 Support and Maintenance

### Troubleshooting
```bash
# Common diagnostic commands
zappa tail production          # View Lambda logs
aws rds describe-db-instances  # Check RDS status
aws s3 ls s3://bucket-name     # Verify S3 contents
```

### Backup Strategy
```yaml
Database backup:
  - Automatic backup: 7-day retention
  - Manual snapshot: important node backup

Code backup:
  - Git repository: GitHub/GitLab
  - Deployment package: S3 storage
```

---

**Document Version**: v1.0  
**Last Updated**: June 2024  
**Author**: JobQuest Navigator Development Team  
**Project**: Graduation Design Project