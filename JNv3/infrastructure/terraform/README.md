# JobQuest Navigator v3 - Infrastructure Deployment

## 🚀 Overview

This directory contains the complete Terraform infrastructure configuration for deploying JobQuest Navigator v3 to AWS using ECS Fargate, RDS PostgreSQL, and Application Load Balancer.

## 🏗️ Architecture

- **VPC**: Custom VPC with public/private subnets across 2 AZs
- **ECS Fargate**: Containerized microservices for backend and frontend
- **RDS PostgreSQL**: Production database with automated backups
- **Application Load Balancer**: Public endpoint with path-based routing
- **ECR**: Container registry for Docker images
- **CloudWatch**: Centralized logging and monitoring

## 🔧 Prerequisites

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- Terraform installed (version 1.6.0+)

### 2. Required AWS Permissions
The deploying user/role needs the following permissions:
- EC2 (VPC, Subnets, Security Groups, etc.)
- ECS (Clusters, Services, Task Definitions)
- RDS (Database instances, Subnet Groups)
- ELB (Application Load Balancers, Target Groups)
- ECR (Repositories, Image management)
- IAM (Roles, Policies for ECS tasks)
- CloudWatch (Log Groups)

### 3. S3 Backend Setup
Create an S3 bucket for Terraform state storage:
```bash
aws s3 mb s3://caa900resume
```

Create DynamoDB table for state locking (optional but recommended):
```bash
aws dynamodb create-table \
    --table-name terraform-state-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

## 🛠️ Local Development Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd JNv3/infrastructure/terraform
```

### 2. Initialize Terraform
```bash
terraform init -backend-config=backend-configs/production.hcl
```

### 3. Validate Configuration
```bash
terraform fmt -check
terraform validate
```

### 4. Plan Deployment
```bash
terraform plan -var="project_name=jobquest-navigator-v3"
```

### 5. Deploy Infrastructure
```bash
terraform apply -var="project_name=jobquest-navigator-v3"
```

## 🔐 GitHub Actions Setup

### Required GitHub Secrets

Add these secrets to your GitHub repository settings:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |

### Repository Settings

1. **Environments**: Create a `production` environment in GitHub
2. **Protection Rules**: Configure branch protection for `main` branch
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

### Workflow Overview

#### 1. Pull Request Workflow (`terraform-pr-check.yml`)
- **Triggers**: PRs to main branch
- **Actions**: Format check, validate, plan (no apply)
- **Purpose**: Validate changes before merge

#### 2. Production Deployment (`deploy-full-app.yml`)
- **Triggers**: Push to main branch, manual dispatch
- **Actions**: Complete infrastructure + application deployment
- **Purpose**: Full production deployment

## 🔄 Deployment Process

### 1. Development Workflow
```mermaid
graph LR
    A[Create Feature Branch] --> B[Make Changes]
    B --> C[Create Pull Request]
    C --> D[PR Validation Runs]
    D --> E[Code Review]
    E --> F[Merge to Main]
    F --> G[Production Deployment]
```

### 2. PR Validation Process
1. **Format Check**: Ensures code formatting
2. **Terraform Init**: Initializes with remote backend
3. **Terraform Validate**: Validates configuration syntax
4. **Terraform Plan**: Shows planned changes
5. **Comment Results**: Posts results to PR

### 3. Production Deployment Process
1. **Infrastructure Deployment**: Terraform plan + apply
2. **Docker Image Build**: Build and push to ECR
3. **Service Update**: Update ECS services with new images
4. **Health Verification**: Wait for services to stabilize

## 📊 Monitoring and Verification

### Health Checks
After deployment, verify these endpoints:
- **Frontend**: `https://<alb-dns-name>/`
- **Backend API**: `https://<alb-dns-name>/api/status`
- **Health Check**: `https://<alb-dns-name>/health`

### AWS Console Verification
1. **ECS Console**: Check service status and task health
2. **RDS Console**: Verify database availability
3. **CloudWatch**: Monitor logs and metrics
4. **Load Balancer**: Check target group health

## 🚨 Troubleshooting

### Common Issues

#### 1. State Lock Errors
```bash
# Force unlock if needed (use carefully)
terraform force-unlock <lock-id>
```

#### 2. Resource Already Exists
```bash
# Import existing resources
terraform import aws_vpc.main vpc-xxxxxxxxx
```

#### 3. ECS Service Not Starting
- Check CloudWatch logs: `/ecs/jobquest-navigator-v3/backend`
- Verify ECR image exists and is accessible
- Check security group rules

#### 4. Database Connection Issues
- Verify RDS security group allows traffic from ECS
- Check database credentials in task definition
- Ensure database is in correct subnet group

### Debug Commands
```bash
# Check ECS service status
aws ecs describe-services --cluster jobquest-navigator-v3-cluster --services jobquest-navigator-v3-backend-service

# View ECS logs
aws logs tail /ecs/jobquest-navigator-v3/backend --follow

# Check RDS status
aws rds describe-db-instances --db-instance-identifier jobquest-navigator-v3-db-*
```

## 🔧 Configuration Details

### Environment Variables
The deployment uses these environment variables:
- `PROJECT_NAME`: jobquest-navigator-v3
- `AWS_REGION`: us-east-1
- `ENVIRONMENT`: production

### Resource Naming Convention
All resources follow the pattern: `${PROJECT_NAME}-${RESOURCE_TYPE}`

### Cost Optimization
- **ECS**: Fargate Spot pricing where applicable
- **RDS**: db.t3.micro for development/testing
- **Load Balancer**: Single ALB for both services

## 📋 Post-Deployment Tasks

1. **DNS Configuration**: Point domain to ALB DNS name
2. **SSL Certificate**: Add ACM certificate to load balancer
3. **Database Migration**: Run initial database setup
4. **Monitoring Setup**: Configure CloudWatch alarms
5. **Backup Verification**: Test RDS backup restore

## 🔄 Updates and Maintenance

### Rolling Updates
ECS services support rolling updates:
1. Push new Docker image to ECR
2. Update task definition
3. ECS automatically replaces tasks

### Infrastructure Updates
1. Make changes in feature branch
2. Create PR for review
3. Merge to trigger deployment

### Scaling
```bash
# Scale services manually
aws ecs update-service --cluster jobquest-navigator-v3-cluster \
    --service jobquest-navigator-v3-backend-service \
    --desired-count 2
```

## 📚 Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**📞 Support**: For issues or questions, create a GitHub issue or contact the development team.