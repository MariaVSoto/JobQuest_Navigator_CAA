# JobQuest Navigator - Troubleshooting Guide

## 🛠️ Overview

This document provides diagnosis and solutions for common issues encountered during the JobQuest Navigator AWS deployment process.

---

## 🚨 Deployment Stage Issues

### 1. CloudFormation Deployment Failure

#### Issue: Stack Creation Failed
```
CREATE_FAILED: The account is not authorized to use this service
```

**Root Cause Analysis:**
- Insufficient AWS account permissions
- Service not available in the current region
- Account limits or quota issues

**Solution:**
```bash
# Check account permissions
aws sts get-caller-identity

# Check service availability
aws ec2 describe-availability-zones --region us-east-1

# Check service limits
aws support describe-service-limits
```

#### Issue: Parameter Validation Error
```
ValidationError: Template format error: [/Resources/Database/Properties/MasterUserPassword] 
'null' values are not allowed in templates
```

**Solution:**
```bash
# Ensure all required parameters have values
aws cloudformation create-stack \
  --stack-name jobquest-navigator-infra \
  --template-body file://cloudformation-template.yaml \
  --parameters ParameterKey=DatabasePassword,ParameterValue=SecurePass123! \
               ParameterKey=AlertEmail,ParameterValue=your-email@domain.com
```

### 2. RDS Database Issues

#### Issue: Database Creation Failed
```
DBSubnetGroupDoesNotCoverEnoughAZs: DB Subnet Group doesn't meet availability zone coverage requirement
```

**Solution:**
```bash
# Check available zones
aws ec2 describe-availability-zones --region us-east-1

# Ensure subnets are in different AZs
# Modify CloudFormation template to ensure subnets are distributed across at least two AZs
```

#### Issue: Database Connection Timeout
```
ERROR 2003 (HY000): Can't connect to MySQL server on 'xxx.amazonaws.com' (110)
```

**Diagnosis Steps:**
```bash
# 1. Check RDS instance status
aws rds describe-db-instances --db-instance-identifier jobquest-navigator-db

# 2. Check security group configuration
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# 3. Test network connectivity
telnet your-db-endpoint.amazonaws.com 3306
```

**Solution:**
```bash
# Modify security group rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 3306 \
  --source-group sg-yyyyyyyy
```

---

## 🐍 Lambda Deployment Issues

### 1. Zappa Deployment Error

#### Issue: Insufficient IAM Permissions
```
An error occurred (AccessDenied) when calling the CreateFunction operation: 
User is not authorized to perform: lambda:CreateFunction
```

**Required Permissions List:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "apigateway:*",
        "s3:*",
        "events:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Issue: Package Size Exceeded
```
An error occurred (InvalidParameterValueException): Unzipped size must be smaller than 262144000 bytes
```

**Solution:**
```bash
# 1. Exclude unnecessary files
echo "*.pyc
__pycache__/
.git/
tests/
*.sqlite3" > .zappaignore

# 2. Use Slim handler
pip install zappa[all]

# 3. Configure in zappa_settings.json
{
  "production": {
    "slim_handler": true,
    "exclude": ["*.pyc", "*.pyo"]
  }
}
```

### 2. Lambda Runtime Errors

#### Issue: Module Import Failure
```
Unable to import module 'core.wsgi': No module named 'django'
```

**Solution:**
```bash
# Ensure requirements.txt includes all dependencies
pip freeze > requirements.txt

# Check Zappa virtual environment
zappa status production

# Repackage and redeploy
zappa update production
```

#### Issue: Database Connection Pool Exhausted
```
(1040, 'Too many connections')
```

**Solution:**
```python
# Configure connection pool in Django settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 0,  # Do not persist connections
    }
}
```

### 3. API Gateway Issues

#### Issue: CORS Error
```
Access to XMLHttpRequest at 'api-url' from origin 'frontend-url' has been blocked by CORS policy
```

**Django CORS Configuration:**
```python
# settings_production.py
CORS_ALLOWED_ORIGINS = [
    "https://jobquest-navigator-frontend-production.s3-website-us-east-1.amazonaws.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Do not set to True in production
```

**API Gateway CORS Configuration:**
```bash
# Configure CORS automatically via Zappa
{
  "production": {
    "cors": true,
    "cors_origin": "https://your-frontend-domain.com"
  }
}
```

---

## 🌐 Frontend Deployment Issues

### 1. S3 Deployment Issues

#### Issue: Bucket Policy Error
```
AccessDenied: Access Denied when putting object
```

**Solution:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::jobquest-navigator-frontend-production/*"
    }
  ]
}
```

#### Issue: SPA Route 404
```
The specified key does not exist when accessing /dashboard
```

**Solution:**
```bash
# Set error document to index.html
aws s3 website s3://jobquest-navigator-frontend-production \
  --index-document index.html \
  --error-document index.html
```

### 2. Frontend Configuration Issues

#### Issue: API Endpoint Not Accessible
```
TypeError: Failed to fetch
```

**Check Steps:**
```bash
# 1. Verify API Gateway URL
curl -X GET "https://api-gateway-url.amazonaws.com/prod/api/health/"

# 2. Check frontend environment variables
cat build/static/js/main.*.js | grep -o 'REACT_APP_API_URL[^"']*'

# 3. Verify CORS configuration
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     "https://api-gateway-url.amazonaws.com/prod/api/health/"
```

---

## 📊 Performance Issues

### 1. Lambda Performance Optimization

#### Issue: Cold Start Too Long
```
Duration: 10000.00 ms    Billed Duration: 10000 ms    Memory Size: 128 MB
```

**Optimization:**
```json
{
  "production": {
    "memory_size": 512,
    "timeout_seconds": 30,
    "keep_warm": false,
    "provisioned_concurrency": 1
  }
}
```

#### Issue: Insufficient Memory
```
Runtime.ImportModuleError: Unable to import module 'core.wsgi': No module named 'PIL'
```

**Solution:**
```bash
# Increase memory allocation
zappa update production

# Use optimized dependency package
pip install Pillow-SIMD
```

### 2. Database Performance Issues

#### Issue: Query Timeout
```
(2006, 'MySQL server has gone away')
```

**Diagnosis and Optimization:**
```python
# 1. Enable query logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

# 2. Optimize database queries
# Use select_related and prefetch_related
queryset = Job.objects.select_related('company').prefetch_related('skills')

# 3. Add database indexes
class Job(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    location = models.CharField(max_length=100, db_index=True)
```

---

## 🔍 Monitoring and Diagnostic Tools

### 1. Log Analysis

#### CloudWatch Log Query
```bash
# View Lambda error logs
aws logs filter-log-events \
  --log-group-name "/aws/lambda/jobquest-navigator-api-production" \
  --filter-pattern "ERROR" \
  --start-time $(date -d "1 hour ago" +%s)000

# View database connection errors
aws logs filter-log-events \
  --log-group-name "/aws/lambda/jobquest-navigator-api-production" \
  --filter-pattern "Can't connect to MySQL" \
  --start-time $(date -d "24 hours ago" +%s)000
```

#### Zappa Log Tools
```bash
# View logs in real time
zappa tail production

# View logs of specific level
zappa tail production --http

# Save logs to file
zappa tail production > lambda-logs.txt
```

### 2. Performance Monitoring

#### CloudWatch Metrics
```bash
# Lambda execution time
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=jobquest-navigator-api-production \
  --start-time $(date -d "1 hour ago" -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Average,Maximum

# API Gateway error rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name 4XXError \
  --dimensions Name=ApiName,Value=jobquest-navigator-api \
  --start-time $(date -d "1 hour ago" -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Sum
```

### 3. Health Check Scripts

#### Automated Diagnostic Script
```bash
#!/bin/bash
# health-check.sh

echo "=== JobQuest Navigator Health Check ==="

# 1. Check Lambda function status
echo "Checking Lambda function..."
aws lambda get-function --function-name jobquest-navigator-api-production

# 2. Check RDS instance status
echo "Checking RDS instance..."
aws rds describe-db-instances --db-instance-identifier jobquest-navigator-db

# 3. Check S3 buckets
echo "Checking S3 buckets..."
aws s3 ls s3://jobquest-navigator-frontend-production
aws s3 ls s3://jobquest-navigator-static-production

# 4. Test API endpoints
echo "Testing API endpoints..."
curl -f "https://api-gateway-url.amazonaws.com/prod/api/health/" || echo "API health check failed"

# 5. Check frontend accessibility
echo "Testing frontend..."
curl -f "https://jobquest-navigator-frontend-production.s3-website-us-east-1.amazonaws.com" || echo "Frontend check failed"

echo "=== Health Check Complete ==="
```

---

## 🛠️ Common Fix Commands

### Quick Fix Scripts

#### Redeploy All Components
```bash
#!/bin/bash
# quick-redeploy.sh

echo "Starting quick redeploy..."

# 1. Update Lambda
cd backend
zappa update production

# 2. Rebuild and deploy frontend
cd ../frontend
npm run build
aws s3 sync build/ s3://jobquest-navigator-frontend-production --delete

# 3. Clear CloudFront cache (if used)
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"

echo "Redeploy complete!"
```

#### Database Connection Fix
```bash
#!/bin/bash
# fix-db-connection.sh

# 1. Reboot RDS instance
aws rds reboot-db-instance --db-instance-identifier jobquest-navigator-db

# 2. Wait for instance to be available
aws rds wait db-instance-available --db-instance-identifier jobquest-navigator-db

# 3. Test connection
python manage.py check --database default

# 4. Run migration
python manage.py migrate --settings=core.settings_production
```

---

## 📞 Getting Help

### Support Channels
1. **Technical Documentation**: See prod/docs/
2. **AWS Support**: Via AWS Support Center
3. **Community Support**: Django and Zappa community forums

### Information to Provide When Reporting Issues
- Full error message
- CloudFormation stack status
- Lambda function logs
- Steps to reproduce
- Environment configuration information

---

**Troubleshooting Guide Version**: v1.0  
**Last Updated**: June 25, 2024  
**Maintenance Team**: JobQuest Navigator Development Team