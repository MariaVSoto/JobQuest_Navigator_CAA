# JobQuest Navigator - AWS Deployment Operations Manual

## 📋 Overview

This document provides a complete deployment guide for the JobQuest Navigator project on AWS, including infrastructure setup, application deployment, and configuration instructions.

**Target Environment**: AWS Production Environment  
**Deployment Architecture**: Serverless (Lambda + API Gateway + RDS + S3)  
**Estimated Deployment Time**: 30-45 minutes

---

## 🛠️ Prerequisites

### Required Tools
- **AWS CLI** (version 2.x)
- **Python 3.9+**
- **Node.js 18+**
- **Docker** (for local testing)
- **Git**

### AWS Account Preparation
- Valid AWS account
- Administrator or appropriate IAM permissions
- Budget setting (recommended monthly budget $30)

### Environment Check
```bash
# Verify tool installation
aws --version
python --version
node --version
docker --version

# Verify AWS configuration
aws sts get-caller-identity
```

---

## 🚀 Quick Deployment Steps

### Step 1: Clone and Prepare Code

```bash
# 1. Clone the prod directory locally
git clone <repository-url>
cd JobQuest_Navigator_CAA/prod

# 2. Set environment variables
cp configs/environment.env .env
# Edit the .env file and fill in actual AWS configuration
```

### Step 2: Deploy Infrastructure

```bash
# 1. Deploy CloudFormation stack
cd infrastructure
aws cloudformation create-stack \
  --stack-name jobquest-navigator-infra \
  --template-body file://cloudformation-template.yaml \
  --parameters ParameterKey=DatabasePassword,ParameterValue=YourSecurePassword123! \
               ParameterKey=AlertEmail,ParameterValue=your-email@domain.com \
  --capabilities CAPABILITY_IAM

# 2. Wait for stack creation to complete
aws cloudformation wait stack-create-complete \
  --stack-name jobquest-navigator-infra

# 3. Get output values
aws cloudformation describe-stacks \
  --stack-name jobquest-navigator-infra \
  --query 'Stacks[0].Outputs'
```

### Step 3: Backend Deployment

```bash
# 1. Enter backend directory
cd ../backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Database migration
python manage.py migrate --settings=core.settings_production

# 4. Collect static files
python manage.py collectstatic --noinput --settings=core.settings_production

# 5. Use deployment script
cd ../scripts
bash deploy-backend.sh
```

### Step 4: Frontend Deployment

```bash
# 1. Enter frontend directory
cd ../frontend

# 2. Install dependencies and build
npm install
npm run build

# 3. Deploy to S3
cd ../scripts
bash deploy-frontend.sh
```

### Step 5: Verify Deployment

```bash
# Run deployment verification script
cd ../scripts
bash verify-deployment.sh
```

---

## 📂 Detailed Deployment Instructions

### Infrastructure Components

#### 1. CloudFormation Stack Deployment

**Resources Created:**
- VPC and subnets (network infrastructure)
- RDS MySQL database (db.t3.micro)
- S3 buckets (frontend, static files, Lambda code)
- IAM roles and policies
- Security group configuration
- CloudWatch alarms

**Key Parameters:**
```yaml
Parameters:
  DatabasePassword: Database password (minimum 8 characters)
  AlertEmail: Alert email address
  ProjectName: Project name (default: jobquest-navigator)
  Environment: Environment name (default: production)
```

#### 2. Database Configuration

**Get Connection Info:**
```bash
# Get RDS endpoint
aws cloudformation describe-stacks \
  --stack-name jobquest-navigator-infra \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
  --output text
```

**Database Initialization:**
```bash
# Connect to database and create tables
python manage.py migrate --settings=core.settings_production

# Create superuser (optional)
python manage.py createsuperuser --settings=core.settings_production

# Load sample data (development environment)
python manage.py loaddata fixtures/sample_data.json
```

### Application Deployment

#### 1. Backend Lambda Deployment

**Zappa Configuration File** (`zappa_settings.json`):
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
      "DJANGO_SETTINGS_MODULE": "core.settings_production"
    }
  }
}
```

**Deployment Commands:**
```bash
# Install Zappa
pip install zappa

# First deployment
zappa deploy production

# Update deployment
zappa update production

# Set environment variables
zappa set_env production DATABASE_URL "mysql://admin:password@endpoint/dbname"
```

#### 2. Frontend S3 Deployment

**Build Configuration:**
```bash
# Set API endpoint
echo "REACT_APP_API_URL=https://api-gateway-url.amazonaws.com/prod" > .env.production

# Build production version
npm run build

# Deploy to S3
aws s3 sync build/ s3://jobquest-navigator-frontend-production \
  --delete --cache-control max-age=31536000
```

**S3 Website Configuration:**
```bash
# Enable static website hosting
aws s3 website s3://jobquest-navigator-frontend-production \
  --index-document index.html \
  --error-document index.html
```

---

## 🛠️ Configuration Management

### Environment Variable Configuration

**Django Production Settings:**
```python
# core/settings_production.py
import os
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['your-api-gateway-url.amazonaws.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
    }
}

# S3 Configuration
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
```

**Lambda Environment Variables:**
```bash
zappa set_env production RDS_HOSTNAME your-db-endpoint.amazonaws.com
zappa set_env production RDS_DB_NAME jobquest_navigator
zappa set_env production RDS_USERNAME admin
zappa set_env production RDS_PASSWORD your-secure-password
zappa set_env production AWS_STORAGE_BUCKET_NAME jobquest-navigator-static-production
```

### CORS Configuration

**Django CORS Settings:**
```python
CORS_ALLOWED_ORIGINS = [
    "https://jobquest-navigator-frontend-production.s3-website-us-east-1.amazonaws.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://jobquest-navigator-frontend-production.s3-website-us-east-1.amazonaws.com",
]
```

**S3 CORS Configuration:**
```json
{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedOrigins": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

---

## 🔍 Verification and Testing

### Deployment Verification Checklist

#### Infrastructure Verification
- [ ] CloudFormation stack status: CREATE_COMPLETE
- [ ] RDS instance status: available
- [ ] S3 bucket created successfully
- [ ] IAM roles and policies configured correctly

#### Application Verification
- [ ] Lambda function deployed successfully
- [ ] API Gateway endpoint responds normally
- [ ] Database connection test passed
- [ ] Static file upload successful

#### Functional Verification
- [ ] User registration and login
- [ ] Main API endpoint tests
- [ ] Frontend page loads normally
- [ ] File upload function works

### Automated Testing

**API Functionality Test:**
```bash
# Run API test suite
cd tests
python test_api_endpoints.py --env production
```

**End-to-End Test:**
```bash
# Use test script to verify entire deployment
cd scripts
bash run-e2e-tests.sh
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Lambda Deployment Failure

**Issue:** Permission error during Zappa deployment
```bash
Error: An error occurred (AccessDenied) when calling the CreateFunction operation
```

**Solution:**
```bash
# Check IAM permissions
aws iam get-user

# Ensure the following permissions:
# - lambda:CreateFunction
# - iam:CreateRole
# - apigateway:*
# - s3:*
```

#### 2. Database Connection Failure

**Issue:** Lambda cannot connect to RDS
```bash
Error: (2003, "Can't connect to MySQL server")
```

**Solution:**
```bash
# Check security group configuration
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# Ensure Lambda security group can access RDS security group's port 3306
```

#### 3. CORS Error

**Issue:** Frontend cannot access API
```bash
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
```python
# Update Django settings
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]

# Redeploy Lambda
zappa update production
```

#### 4. Static File Load Failure

**Issue:** CSS/JS file 404 error
```bash
GET https://bucket.s3.amazonaws.com/static/css/main.css 404
```

**Solution:**
```bash
# Re-collect static files
python manage.py collectstatic --noinput --settings=core.settings_production

# Check S3 bucket policy
aws s3api get-bucket-policy --bucket jobquest-navigator-static-production
```

### Log Debugging

**View Lambda Logs:**
```bash
# View Lambda logs in real time
zappa tail production

# Get logs for a specific time period
aws logs filter-log-events \
  --log-group-name /aws/lambda/jobquest-navigator-api-production \
  --start-time 1640995200000
```

**CloudWatch Monitoring:**
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=jobquest-navigator-api-production \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average
```

---

## 📊 Monitoring and Maintenance

### Performance Monitoring

**Key Metrics:**
- Lambda execution time and memory usage
- API Gateway request response time
- RDS connection count and CPU usage
- S3 storage usage and request count

**Alarm Configuration:**
```bash
# Create Lambda error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "Lambda-Errors-High" \
  --alarm-description "Lambda error rate is too high" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### Backup Strategy

**Database Backup:**
```bash
# Create RDS snapshot
aws rds create-db-snapshot \
  --db-instance-identifier jobquest-navigator-db \
  --db-snapshot-identifier jobquest-navigator-backup-$(date +%Y%m%d)

# Set automatic backup retention period
aws rds modify-db-instance \
  --db-instance-identifier jobquest-navigator-db \
  --backup-retention-period 7
```

**Code Backup:**
```bash
# S3 versioning enabled, Lambda code automatically backed up to S3
# Manually backup current deployment
zappa save-python-settings-file production
```

### Update Deployment

**Application Update Process:**
```bash
# 1. Pull latest code
git pull origin main

# 2. Update dependencies
pip install -r requirements.txt

# 3. Run database migration
python manage.py migrate --settings=core.settings_production

# 4. Update Lambda
zappa update production

# 5. Update frontend
npm run build
aws s3 sync build/ s3://jobquest-navigator-frontend-production
```

**Rollback Strategy:**
```bash
# Lambda version rollback
zappa rollback production -n 1

# RDS point-in-time restore
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier jobquest-navigator-db \
  --target-db-instance-identifier jobquest-navigator-db-restored \
  --restore-time 2024-01-01T12:00:00.000Z
```

---

## 💰 Cost Optimization

### Cost Monitoring

**Set Billing Alarm:**
```bash
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "JobQuest Navigator Monthly Budget",
    "BudgetLimit": {
      "Amount": "30",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

### Optimization Suggestions

1. **Lambda Optimization:**
   - Adjust memory size to optimize execution time
   - Enable reserved concurrency to reduce cold starts

2. **RDS Optimization:**
   - Use reserved instances to save costs
   - Regularly clean up unnecessary data

3. **S3 Optimization:**
   - Set lifecycle policies to delete old files
   - Use Standard-IA storage class to reduce storage costs

---

## 📞 Support and Contact

### Technical Support
- **Documentation**: Refer to detailed documents in prod/docs/
- **Issue Reporting**: Report issues via the project Issue system
- **Emergency Contact**: See ALERT_EMAIL in configs/environment.env

### Useful Links
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Zappa Documentation](https://github.com/zappa/Zappa)
- [Django Deployment Guide](https://docs.djangoproject.com/en/4.2/howto/deployment/)

---

**Deployment Manual Version**: v1.0  
**Last Updated**: June 25, 2024  
**Maintenance Team**: JobQuest Navigator Development Team