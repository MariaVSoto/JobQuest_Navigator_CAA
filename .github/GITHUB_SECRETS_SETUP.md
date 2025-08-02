# GitHub Secrets Management for JobQuest Navigator v3

## Overview
This document outlines the required GitHub repository and environment secrets for the JobQuest Navigator v3 project deployment and CI/CD workflows.

## Repository Secrets (Settings > Secrets and Variables > Actions)

### Core Application Secrets
```bash
# Application Security
SECRET_KEY=your-production-secret-key-256-bit
JWT_SECRET_KEY=your-jwt-signing-key

# Database Configuration  
DATABASE_URL=postgresql://username:password@hostname:5432/database
DB_USERNAME=your-db-username
DB_PASSWORD=your-db-password

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_DEFAULT_REGION=us-east-1
```

### External API Keys
```bash
# External Service APIs
ADZUNA_API_ID=your-adzuna-api-id
ADZUNA_API_KEY=your-adzuna-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
OPENAI_API_KEY=your-openai-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

### Storage & Infrastructure
```bash
# S3/Storage Configuration
S3_BUCKET_NAME=caa900resume
AWS_STORAGE_BUCKET_NAME=caa900resume
AWS_S3_REGION_NAME=us-east-1

# MinIO (Development/Testing)
MINIO_ACCESS_KEY=development-minio-key
MINIO_SECRET_KEY=development-minio-secret
```

### Notification & Monitoring
```bash
# Alerts and Notifications
ALERT_EMAIL=alerts@yourcompany.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Environment-Specific Secrets

### Production Environment
Set these in **Settings > Environments > production**:
```bash
# Production Database
DATABASE_URL=postgresql://prod_user:prod_pass@prod-db:5432/jobquest_prod
SECRET_KEY=production-secret-key-change-monthly

# Production APIs
ADZUNA_API_KEY=production-adzuna-key
GOOGLE_MAPS_API_KEY=production-google-maps-key
OPENAI_API_KEY=production-openai-key
```

### Staging Environment  
Set these in **Settings > Environments > staging**:
```bash
# Staging Database
DATABASE_URL=postgresql://staging_user:staging_pass@staging-db:5432/jobquest_staging
SECRET_KEY=staging-secret-key

# Staging APIs (can use production keys with quotas)
ADZUNA_API_KEY=staging-adzuna-key
GOOGLE_MAPS_API_KEY=staging-google-maps-key
OPENAI_API_KEY=staging-openai-key
```

### Test Environment
Set these in **Settings > Environments > test**:
```bash
# Test Database
DATABASE_URL=postgresql://test_user:test_pass@test-db:5432/jobquest_test
SECRET_KEY=test-secret-key-for-ci
```

## AWS Secrets Manager Integration

For production deployments, some secrets are managed via AWS Secrets Manager:

### Required AWS Secrets
```bash
# Create these secrets in AWS Secrets Manager
jobquest-navigator-v3-production-app-secret-key
jobquest-production-database-credentials
jobquest-production-adzuna-api-key  
jobquest-production-google-maps-api-key
jobquest-production-openai-api-key
jobquest-production-stripe-credentials
```

### Terraform Integration
The infrastructure automatically creates and manages these AWS secrets:
```hcl
# Terraform will create these resources
resource "aws_secretsmanager_secret" "app_secret_key"
resource "aws_secretsmanager_secret" "database_credentials"
resource "aws_secretsmanager_secret" "external_api_keys"
```

## Security Best Practices

### 1. Secret Rotation
- **Monthly**: Rotate `SECRET_KEY` and `JWT_SECRET_KEY`
- **Quarterly**: Rotate database passwords and AWS keys
- **Annually**: Rotate external API keys (where possible)

### 2. Environment Separation
- Use different secrets for each environment
- Never use production secrets in staging/development
- Test environments should use dedicated test accounts

### 3. Access Control
- Limit repository access to essential team members
- Use GitHub environment protection rules
- Enable required reviewers for production deployments

### 4. Monitoring & Auditing
- Monitor secret usage in GitHub Actions logs (secrets are masked)
- Set up alerts for failed authentication attempts
- Regular audit of who has access to secrets

## Setup Instructions

### 1. Repository Secrets
1. Go to **Settings > Secrets and Variables > Actions**
2. Click **New repository secret**
3. Add each secret from the "Repository Secrets" section above

### 2. Environment Secrets
1. Go to **Settings > Environments**
2. Create environments: `production`, `staging`, `test`
3. For each environment:
   - Click **Add secret**
   - Add environment-specific secrets
   - Configure protection rules as needed

### 3. AWS Secrets Manager (Production)
```bash
# Create secrets using AWS CLI
aws secretsmanager create-secret \
  --name "jobquest-navigator-v3-production-app-secret-key" \
  --secret-string "your-production-secret-key"

aws secretsmanager create-secret \
  --name "jobquest-production-database-credentials" \
  --secret-string '{"username":"prod_user","password":"prod_password"}'
```

### 4. Verify Setup
Run the verification workflow to ensure all secrets are properly configured:
```bash
# This will be triggered automatically in CI/CD
name: Verify Secrets Configuration
```

## Troubleshooting

### Common Issues

1. **Secret Not Found**: Ensure secret name matches exactly (case-sensitive)
2. **Environment Secret Not Available**: Check environment configuration
3. **AWS Access Denied**: Verify IAM permissions for Secrets Manager
4. **Masked Secret in Logs**: This is expected behavior for security

### Testing Secrets Locally
```bash
# For local development, create .env files (never commit!)
cp JNv3/config/environments/development.env.example .env
# Edit .env with your development values
```

## Migration from Hardcoded Values

### Current Hardcoded Issues to Fix:
1. `SECRET_KEY=dev-secret-key-change-in-production` → Use `${{ secrets.SECRET_KEY }}`
2. `minioadmin/minioadmin123` → Use `${{ secrets.MINIO_ACCESS_KEY }}`
3. AWS credentials in config files → Use GitHub secrets
4. API keys in environment files → Use GitHub secrets

### Migration Steps:
1. ✅ Create GitHub secrets (this document)
2. 🔄 Update CI/CD workflows to use secrets
3. 🔄 Update application configuration
4. 🔄 Remove hardcoded values from codebase
5. ✅ Test deployment with new secret management

## Support
For questions about secret management or setup issues, contact the DevOps team or create an issue in this repository.