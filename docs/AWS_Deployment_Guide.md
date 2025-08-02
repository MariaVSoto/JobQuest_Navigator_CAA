# JobQuest Navigator - AWS Production Deployment Guide

## 🚀 **Pre-Deployment Checklist**

### Required Tools & Credentials
```bash
# 1. Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 2. Install Terraform
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# 3. Install Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# 4. Verify installations
aws --version
terraform --version
docker --version
```

### AWS Account Setup
```bash
# Configure AWS credentials
aws configure
# AWS Access Key ID: [Your Key]
# AWS Secret Access Key: [Your Secret]
# Default region name: us-east-1
# Default output format: json

# Verify AWS access
aws sts get-caller-identity
```

## 📋 **Step-by-Step Deployment Process**

### Phase 1: Infrastructure Deployment (30-45 minutes)

#### 1.1 Prepare Terraform Backend
```bash
cd JNv3/infrastructure/terraform/

# Create S3 bucket for Terraform state (one-time setup)
aws s3 mb s3://jobquest-terraform-state-$(date +%s)
aws s3api put-bucket-versioning \
  --bucket jobquest-terraform-state-$(date +%s) \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name jobquest-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

#### 1.2 Initialize Terraform
```bash
# Initialize Terraform with backend configuration
terraform init \
  -backend-config="bucket=jobquest-terraform-state-TIMESTAMP" \
  -backend-config="key=production/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="encrypt=true" \
  -backend-config="dynamodb_table=jobquest-terraform-locks"
```

#### 1.3 Create SSL Certificate (Manual Step)
```bash
# Request SSL certificate via AWS Certificate Manager
aws acm request-certificate \
  --domain-name "api.jobquest-navigator.com" \
  --subject-alternative-names "*.jobquest-navigator.com" \
  --validation-method DNS

# Note: Save the certificate ARN for terraform variables
```

#### 1.4 Deploy Infrastructure
```bash
# Plan deployment
terraform plan -var-file="environments/production.tfvars"

# Apply infrastructure
terraform apply -var-file="environments/production.tfvars" -auto-approve

# Save outputs for later use
terraform output > ../../../terraform_outputs.txt
```

### Phase 2: Container Images (20-30 minutes)

#### 2.1 Build and Push Backend Image
```bash
cd ../../../JNv3/apps/backend-fastapi/

# Get ECR login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build backend image
docker build -t jobquest-backend .

# Tag and push to ECR
ECR_URI=$(aws ecr describe-repositories --repository-names jobquest-navigator-v2-production-jobquest-backend --query 'repositories[0].repositoryUri' --output text)
docker tag jobquest-backend:latest $ECR_URI:latest
docker push $ECR_URI:latest
```

#### 2.2 Build and Push Frontend Image
```bash
cd ../frontend-react/

# Build frontend
npm install
npm run build

# Build frontend image
docker build -t jobquest-frontend .

# Tag and push to ECR
ECR_FRONTEND_URI=$(aws ecr describe-repositories --repository-names jobquest-navigator-v2-production-jobquest-frontend --query 'repositories[0].repositoryUri' --output text)
docker tag jobquest-frontend:latest $ECR_FRONTEND_URI:latest
docker push $ECR_FRONTEND_URI:latest
```

### Phase 3: Service Deployment (15-20 minutes)

#### 3.1 Update ECS Services
```bash
# Force new deployment with updated images
aws ecs update-service \
  --cluster jobquest-navigator-v2-production \
  --service backend-service \
  --force-new-deployment

aws ecs update-service \
  --cluster jobquest-navigator-v2-production \
  --service frontend-service \
  --force-new-deployment

# Wait for services to stabilize
aws ecs wait services-stable \
  --cluster jobquest-navigator-v2-production \
  --services backend-service frontend-service
```

#### 3.2 Setup Database
```bash
# Get RDS endpoint from Terraform outputs
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Run database migrations (from a local machine or bastion host)
# Note: This requires network access to RDS in private subnet
DATABASE_URL="postgresql://jobquest_prod_user:$(terraform output -raw db_password)@${RDS_ENDPOINT}:5432/jobquest_navigator_v2_prod"

# Alternative: Run migrations from ECS task
aws ecs run-task \
  --cluster jobquest-navigator-v2-production \
  --task-definition backend-task \
  --overrides '{
    "containerOverrides": [{
      "name": "backend",
      "command": ["alembic", "upgrade", "head"]
    }]
  }'
```

## 🔗 **DNS and Domain Configuration**

### Option A: Use AWS Route 53
```bash
# Create hosted zone
aws route53 create-hosted-zone --name jobquest-navigator.com --caller-reference $(date +%s)

# Get ALB DNS name from Terraform outputs
ALB_DNS=$(terraform output -raw alb_dns_name)

# Create CNAME records
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "api.jobquest-navigator.com",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "'$ALB_DNS'"}]
    }
  }]
}'
```

### Option B: Use Alternative Domain Service
```bash
# If you have an existing domain, create CNAME records:
# api.yourdomain.com -> [ALB_DNS_NAME from terraform output]
# www.yourdomain.com -> [CloudFront Distribution Domain]
```

## 🧪 **Testing and Verification**

### Health Check Script
```bash
#!/bin/bash
# save as test_deployment.sh

set -e

echo "🔍 Testing JobQuest Navigator Deployment..."

# Get endpoints from Terraform outputs
ALB_DNS=$(terraform output -raw alb_dns_name)
API_URL="https://${ALB_DNS}"

echo "📡 Testing Backend Health..."
curl -f "${API_URL}/health" || {
  echo "❌ Backend health check failed"
  exit 1
}

echo "🗄️ Testing Database Connection..."
curl -f "${API_URL}/api/health/database" || {
  echo "❌ Database connection failed"
  exit 1
}

echo "🚀 Testing GraphQL Endpoint..."
curl -f -X POST "${API_URL}/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}' || {
  echo "❌ GraphQL endpoint failed"
  exit 1
}

echo "✅ All health checks passed!"
echo "🌐 Your API is live at: ${API_URL}"
```

## 💰 **Cost Monitoring Setup**

### CloudWatch Budget Alert
```bash
# Create cost budget
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget '{
    "BudgetName": "JobQuest-Monthly-Budget",
    "BudgetLimit": {
      "Amount": "50.00",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "your-email@example.com"
    }]
  }]'
```

## 🔒 **Security Configuration**

### Environment Variables Setup
```bash
# Store sensitive configuration in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "jobquest-navigator-v2-production-config" \
  --description "Production configuration for JobQuest Navigator" \
  --secret-string '{
    "OPENAI_API_KEY": "sk-your-openai-key",
    "ADZUNA_API_KEY": "your-adzuna-key",
    "GOOGLE_MAPS_API_KEY": "your-google-maps-key",
    "JWT_SECRET_KEY": "your-jwt-secret"
  }'
```

## 📊 **Production URLs**

After successful deployment, your services will be available at:

```
🌐 API Endpoint: https://[ALB-DNS-NAME]/
📊 Health Check: https://[ALB-DNS-NAME]/health
🔍 GraphQL Playground: https://[ALB-DNS-NAME]/graphql
📈 Monitoring: AWS CloudWatch Console
💾 Database: [RDS-ENDPOINT]:5432 (private)
🗂️ Storage: s3://caa900resume/
```

## 🚨 **Common Issues & Solutions**

### Issue 1: ECS Tasks Not Starting
```bash
# Check ECS service events
aws ecs describe-services \
  --cluster jobquest-navigator-v2-production \
  --services backend-service \
  --query 'services[0].events[0:5]'

# Check task definition
aws ecs describe-task-definition \
  --task-definition backend-task \
  --query 'taskDefinition.containerDefinitions[0].environment'
```

### Issue 2: Database Connection Errors
```bash
# Verify security group rules
aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=*rds*" \
  --query 'SecurityGroups[0].IpPermissions'

# Test database connectivity from ECS
aws ecs run-task \
  --cluster jobquest-navigator-v2-production \
  --task-definition backend-task \
  --overrides '{
    "containerOverrides": [{
      "name": "backend",
      "command": ["python", "-c", "import psycopg2; print(\"DB OK\")"]
    }]
  }'
```

### Issue 3: SSL Certificate Validation
```bash
# Check certificate status
aws acm list-certificates --query 'CertificateSummaryList[?DomainName==`api.jobquest-navigator.com`]'

# If validation is pending, check DNS records
aws route53 list-resource-record-sets --hosted-zone-id Z123456789
```

## 📋 **Monthly Estimated Costs**

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **ECS Fargate** | 3 backend + 3 frontend tasks | ~$35 |
| **RDS PostgreSQL** | db.t3.medium, Multi-AZ | ~$45 |
| **ElastiCache Redis** | cache.t3.medium, 2 nodes | ~$25 |
| **Application Load Balancer** | 1 ALB with SSL | ~$20 |
| **S3 Storage** | 10GB storage + requests | ~$2 |
| **Data Transfer** | 50GB outbound | ~$4.50 |
| **CloudWatch** | Logs + monitoring | ~$10 |
| **NAT Gateway** | 2 NAT gateways | ~$65 |
| **Route 53** | 1 hosted zone | ~$0.50 |
| **Total** | | **~$207/month** |

### Cost Optimization Tips
1. **Use Single NAT Gateway**: Save ~$32/month (reduce redundancy)
2. **Scheduled Scaling**: Scale down during off-hours (save ~20%)
3. **Reserved Instances**: For long-term deployment (save ~30-40%)
4. **Spot Instances**: For non-critical workloads (save ~50-90%)

## 🎯 **Success Criteria**

✅ **Infrastructure**: All AWS resources created successfully  
✅ **Backend**: API responding with 200 status  
✅ **Database**: PostgreSQL accepting connections  
✅ **Redis**: Cache service operational  
✅ **HTTPS**: SSL certificate valid and working  
✅ **Monitoring**: CloudWatch dashboards active  
✅ **Security**: All security groups configured properly  

## 🔄 **CI/CD Integration (Optional)**

### GitHub Actions Deployment
```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
          
      - name: Deploy Infrastructure
        run: |
          cd JNv3/infrastructure/terraform
          terraform init
          terraform apply -var-file="environments/production.tfvars" -auto-approve
          
      - name: Build and Push Images
        run: |
          # Build and push backend
          cd JNv3/apps/backend-fastapi
          docker build -t jobquest-backend .
          # Push to ECR
          
          # Build and push frontend
          cd ../frontend-react
          docker build -t jobquest-frontend .
          # Push to ECR
          
      - name: Update ECS Services
        run: |
          aws ecs update-service --cluster jobquest-navigator-v2-production --service backend-service --force-new-deployment
          aws ecs update-service --cluster jobquest-navigator-v2-production --service frontend-service --force-new-deployment
```

---

## 🏁 **Ready to Deploy?**

**Estimated Total Time**: 1.5-2 hours  
**Prerequisites**: AWS account with admin access, domain name (optional)  
**Total Setup Cost**: ~$207/month  

**Start deployment with:**
```bash
cd JNv3/infrastructure/terraform/
./deploy-production.sh
```

Good luck with your AWS deployment! 🚀