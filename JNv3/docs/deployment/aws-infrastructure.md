# JobQuest Navigator v3 - AWS Infrastructure Guide

## Overview

Complete AWS infrastructure deployment guide for JobQuest Navigator v3's four core systems using Terraform Infrastructure as Code.

## 🏗️ Infrastructure Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        CloudFront CDN                          │
│                  (Global Content Delivery)                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                Application Load Balancer                       │
│              (SSL Termination & Routing)                       │
└─────────────────┬───────────────┬───────────────────────────────┘
                  │               │
          ┌───────▼────────┐  ┌───▼────────────────────────────────┐
          │   S3 Bucket    │  │           ECS Fargate              │
          │   (Frontend)   │  │      (Backend Services)            │
          └────────────────┘  └┬───────────────────────────────────┘
                              │
          ┌───────────────────▼───────────────────────────────────┐
          │              VPC Network                              │
          │  ┌─────────────────┐  ┌─────────────────────────────┐ │
          │  │  Public Subnet  │  │     Private Subnet          │ │
          │  │  (ALB, NAT GW)  │  │  (ECS, RDS, ElastiCache)   │ │
          │  └─────────────────┘  └─────────────────────────────┘ │
          └───────────────────────────────────────────────────────┘
```

### Core Services
```
Production Infrastructure:
├── Compute (ECS Fargate)
│   ├── Backend Service (FastAPI + GraphQL)
│   ├── Auto Scaling (2-10 instances)
│   └── Health Checks & Monitoring
├── Storage
│   ├── S3 Bucket (caa900resume) - File Storage
│   ├── S3 Frontend Bucket - Static Website
│   └── CloudFront Distribution - CDN
├── Database
│   ├── RDS MySQL (Multi-AZ)
│   ├── ElastiCache Redis (Cluster Mode)
│   └── Automated Backups
├── Networking
│   ├── VPC with Public/Private Subnets
│   ├── Application Load Balancer
│   ├── NAT Gateway
│   └── Route 53 DNS
└── Security & Auth
    ├── AWS Cognito User Pool
    ├── IAM Roles & Policies
    ├── Security Groups
    └── Secrets Manager
```

## 🔧 Terraform Configuration

### Directory Structure
```
infrastructure/terraform/
├── main.tf                     # Root module
├── variables.tf                # Input variables
├── outputs.tf                  # Output values
├── backend.tf                  # Terraform state backend
├── environments/
│   ├── development.tfvars      # Dev environment
│   ├── staging.tfvars          # Staging environment
│   └── production.tfvars       # Production environment
├── modules/
│   ├── networking/             # VPC, Subnets, Security Groups
│   ├── compute/                # ECS, ALB, Auto Scaling
│   ├── database/               # RDS, ElastiCache
│   ├── storage/                # S3, CloudFront
│   ├── security/               # IAM, Cognito, Secrets Manager
│   └── monitoring/             # CloudWatch, Alarms
└── scripts/
    ├── deploy.sh               # Deployment script
    ├── destroy.sh              # Cleanup script
    └── validate.sh             # Configuration validation
```

### Main Configuration (main.tf)
```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "caa900resume"
    key    = "terraform/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "JobQuest Navigator v3"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Local values for resource naming
locals {
  name_prefix = "jobquest-${var.environment}"
  
  common_tags = {
    Project     = "JobQuest Navigator v3"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Networking Module
module "networking" {
  source = "./modules/networking"
  
  name_prefix        = local.name_prefix
  vpc_cidr          = var.vpc_cidr
  availability_zones = data.aws_availability_zones.available.names
  
  tags = local.common_tags
}

# Security Module
module "security" {
  source = "./modules/security"
  
  name_prefix = local.name_prefix
  vpc_id      = module.networking.vpc_id
  
  # Cognito Configuration
  cognito_user_pool_name = "${local.name_prefix}-users"
  cognito_domain_prefix  = local.name_prefix
  
  tags = local.common_tags
}

# Storage Module
module "storage" {
  source = "./modules/storage"
  
  name_prefix = local.name_prefix
  
  # S3 Configuration
  s3_bucket_name         = var.s3_bucket_name != "" ? var.s3_bucket_name : "${local.name_prefix}-storage"
  s3_frontend_bucket     = "${local.name_prefix}-frontend"
  enable_versioning      = var.enable_s3_versioning
  enable_encryption      = var.enable_s3_encryption
  
  # CloudFront Configuration
  cloudfront_price_class = var.cloudfront_price_class
  
  tags = local.common_tags
}

# Database Module
module "database" {
  source = "./modules/database"
  
  name_prefix = local.name_prefix
  vpc_id      = module.networking.vpc_id
  subnet_ids  = module.networking.private_subnet_ids
  
  # RDS Configuration
  db_instance_class     = var.db_instance_class
  db_allocated_storage  = var.db_allocated_storage
  db_max_allocated_storage = var.db_max_allocated_storage
  multi_az             = var.db_multi_az
  backup_retention_period = var.db_backup_retention_period
  
  # ElastiCache Configuration
  elasticache_node_type = var.elasticache_node_type
  elasticache_num_cache_nodes = var.elasticache_num_cache_nodes
  
  # Security
  allowed_security_groups = [module.compute.ecs_security_group_id]
  
  tags = local.common_tags
}

# Compute Module
module "compute" {
  source = "./modules/compute"
  
  name_prefix = local.name_prefix
  vpc_id      = module.networking.vpc_id
  subnet_ids  = module.networking.private_subnet_ids
  public_subnet_ids = module.networking.public_subnet_ids
  
  # ECS Configuration
  ecs_desired_count = var.ecs_desired_count
  ecs_max_capacity  = var.ecs_max_capacity
  ecs_min_capacity  = var.ecs_min_capacity
  ecs_cpu          = var.ecs_cpu
  ecs_memory       = var.ecs_memory
  
  # Container Configuration
  container_image = var.container_image
  container_port  = var.container_port
  
  # Environment Variables
  environment_variables = {
    ENVIRONMENT = var.environment
    AWS_REGION  = var.aws_region
    
    # Database
    DATABASE_URL = module.database.database_endpoint
    REDIS_URL    = module.database.elasticache_endpoint
    
    # Storage
    AWS_STORAGE_BUCKET_NAME = module.storage.s3_bucket_name
    
    # Cognito
    COGNITO_USER_POOL_ID = module.security.cognito_user_pool_id
    COGNITO_CLIENT_ID    = module.security.cognito_client_id
  }
  
  # Secrets
  secrets = {
    SECRET_KEY     = module.security.app_secret_arn
    JWT_SECRET_KEY = module.security.jwt_secret_arn
    DB_PASSWORD    = module.database.db_password_secret_arn
  }
  
  # Dependencies
  depends_on = [
    module.networking,
    module.database,
    module.storage,
    module.security
  ]
  
  tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"
  
  name_prefix = local.name_prefix
  
  # Resources to monitor
  ecs_cluster_name = module.compute.ecs_cluster_name
  ecs_service_name = module.compute.ecs_service_name
  alb_arn_suffix   = module.compute.alb_arn_suffix
  rds_identifier   = module.database.db_instance_identifier
  
  # Notification settings
  sns_topic_arn = var.sns_topic_arn
  
  tags = local.common_tags
}
```

### Variables Configuration (variables.tf)
```hcl
# General Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "JobQuest Navigator v3"
}

# Networking Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# S3 Configuration
variable "s3_bucket_name" {
  description = "Name of the S3 bucket for file storage (production use)"
  type        = string
  default     = "caa900resume"
}

variable "enable_s3_versioning" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

variable "enable_s3_encryption" {
  description = "Enable S3 bucket encryption"
  type        = bool
  default     = true
}

variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage (GB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "RDS maximum allocated storage (GB)"
  type        = number
  default     = 100
}

variable "db_multi_az" {
  description = "Enable RDS Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "db_backup_retention_period" {
  description = "RDS backup retention period (days)"
  type        = number
  default     = 7
}

# ElastiCache Configuration
variable "elasticache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "elasticache_num_cache_nodes" {
  description = "Number of ElastiCache nodes"
  type        = number
  default     = 1
}

# ECS Configuration
variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "ecs_min_capacity" {
  description = "Minimum ECS capacity"
  type        = number
  default     = 2
}

variable "ecs_max_capacity" {
  description = "Maximum ECS capacity"
  type        = number
  default     = 10
}

variable "ecs_cpu" {
  description = "ECS task CPU units"
  type        = number
  default     = 1024
}

variable "ecs_memory" {
  description = "ECS task memory (MB)"
  type        = number
  default     = 2048
}

variable "container_image" {
  description = "Container image URI"
  type        = string
  default     = "jobquest-backend:latest"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8000
}

# Monitoring Configuration
variable "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  type        = string
  default     = ""
}
```

### Environment Configurations

#### Production Environment (environments/production.tfvars)
```hcl
# Environment
environment = "production"
aws_region  = "us-east-1"

# Networking
vpc_cidr = "10.0.0.0/16"

# Storage
s3_bucket_name = "caa900resume"
enable_s3_versioning = true
enable_s3_encryption = true
cloudfront_price_class = "PriceClass_All"

# Database
db_instance_class = "db.t3.small"
db_allocated_storage = 50
db_max_allocated_storage = 200
db_multi_az = true
db_backup_retention_period = 30

# ElastiCache
elasticache_node_type = "cache.t3.small"
elasticache_num_cache_nodes = 2

# ECS
ecs_desired_count = 3
ecs_min_capacity = 2
ecs_max_capacity = 10
ecs_cpu = 2048
ecs_memory = 4096
container_image = "your-account.dkr.ecr.us-east-1.amazonaws.com/jobquest-backend:latest"
```

#### Staging Environment (environments/staging.tfvars)
```hcl
# Environment
environment = "staging"
aws_region  = "us-east-1"

# Networking
vpc_cidr = "10.1.0.0/16"

# Storage
s3_bucket_name = "caa900resume-staging"
enable_s3_versioning = true
enable_s3_encryption = true
cloudfront_price_class = "PriceClass_100"

# Database
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_max_allocated_storage = 50
db_multi_az = false
db_backup_retention_period = 7

# ElastiCache
elasticache_node_type = "cache.t3.micro"
elasticache_num_cache_nodes = 1

# ECS
ecs_desired_count = 2
ecs_min_capacity = 1
ecs_max_capacity = 5
ecs_cpu = 1024
ecs_memory = 2048
container_image = "your-account.dkr.ecr.us-east-1.amazonaws.com/jobquest-backend:staging"
```

#### Development Environment (environments/development.tfvars)
```hcl
# Environment
environment = "development"
aws_region  = "us-east-1"

# Networking
vpc_cidr = "10.2.0.0/16"

# Storage
s3_bucket_name = "caa900resume-dev"
enable_s3_versioning = false
enable_s3_encryption = true
cloudfront_price_class = "PriceClass_100"

# Database
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_max_allocated_storage = 50
db_multi_az = false
db_backup_retention_period = 1

# ElastiCache
elasticache_node_type = "cache.t3.micro"
elasticache_num_cache_nodes = 1

# ECS
ecs_desired_count = 1
ecs_min_capacity = 1
ecs_max_capacity = 3
ecs_cpu = 512
ecs_memory = 1024
container_image = "your-account.dkr.ecr.us-east-1.amazonaws.com/jobquest-backend:dev"
```

## 🚀 Deployment Process

### Prerequisites
```bash
# Install Terraform
brew install terraform

# Install AWS CLI
brew install awscli

# Configure AWS credentials
aws configure
```

### Initial Deployment
```bash
# Navigate to Terraform directory
cd JNv3/infrastructure/terraform/

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment (production)
terraform plan -var-file="environments/production.tfvars"

# Apply infrastructure
terraform apply -var-file="environments/production.tfvars"
```

### Deployment Script (scripts/deploy.sh)
```bash
#!/bin/bash

set -e

ENVIRONMENT=${1:-development}
TERRAFORM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Deploying JobQuest Navigator v3 to ${ENVIRONMENT}..."

# Validate environment
if [[ ! -f "${TERRAFORM_DIR}/environments/${ENVIRONMENT}.tfvars" ]]; then
    echo "❌ Environment file not found: ${ENVIRONMENT}.tfvars"
    exit 1
fi

# Change to Terraform directory
cd "${TERRAFORM_DIR}"

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Validate configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -var-file="environments/${ENVIRONMENT}.tfvars" -out="${ENVIRONMENT}.tfplan"

# Ask for confirmation
read -p "Do you want to apply this plan? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Apply deployment
echo "🔨 Applying infrastructure..."
terraform apply "${ENVIRONMENT}.tfplan"

# Clean up plan file
rm -f "${ENVIRONMENT}.tfplan"

echo "✅ Deployment completed successfully!"

# Output important values
echo "📋 Important outputs:"
terraform output
```

### Update Deployment
```bash
# Update existing infrastructure
./scripts/deploy.sh production

# Or manual update
terraform plan -var-file="environments/production.tfvars"
terraform apply -var-file="environments/production.tfvars"
```

### Destroy Infrastructure
```bash
# Destroy development environment
terraform destroy -var-file="environments/development.tfvars"

# Using script
./scripts/destroy.sh development
```

## 📊 Monitoring & Alerting

### CloudWatch Dashboards
```hcl
# Custom Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", module.compute.ecs_service_name],
            [".", "MemoryUtilization", ".", "."],
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "ECS Performance"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", module.compute.alb_arn_suffix],
            [".", "TargetResponseTime", ".", "."],
            [".", "HTTPCode_Target_2XX_Count", ".", "."],
            [".", "HTTPCode_Target_4XX_Count", ".", "."],
            [".", "HTTPCode_Target_5XX_Count", ".", "."],
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Application Load Balancer"
          period  = 300
        }
      }
    ]
  })
}
```

### CloudWatch Alarms
```hcl
# High CPU Utilization
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${local.name_prefix}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ServiceName = module.compute.ecs_service_name
    ClusterName = module.compute.ecs_cluster_name
  }
}

# High Memory Utilization
resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "${local.name_prefix}-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "This metric monitors ECS memory utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ServiceName = module.compute.ecs_service_name
    ClusterName = module.compute.ecs_cluster_name
  }
}

# High Error Rate
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${local.name_prefix}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "This metric monitors application error rate"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = module.compute.alb_arn_suffix
  }
}
```

## 🔒 Security Configuration

### IAM Roles & Policies
```hcl
# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${local.name_prefix}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# S3 Access Policy
resource "aws_iam_role_policy" "s3_access" {
  name = "${local.name_prefix}-s3-access"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          module.storage.s3_bucket_arn,
          "${module.storage.s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Secrets Manager Access
resource "aws_iam_role_policy" "secrets_access" {
  name = "${local.name_prefix}-secrets-access"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          module.security.app_secret_arn,
          module.security.jwt_secret_arn,
          module.database.db_password_secret_arn
        ]
      }
    ]
  })
}
```

### Security Groups
```hcl
# ALB Security Group
resource "aws_security_group" "alb" {
  name_prefix = "${local.name_prefix}-alb-"
  vpc_id      = module.networking.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-sg"
  })
}

# ECS Security Group
resource "aws_security_group" "ecs" {
  name_prefix = "${local.name_prefix}-ecs-"
  vpc_id      = module.networking.vpc_id

  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-sg"
  })
}

# Database Security Group
resource "aws_security_group" "database" {
  name_prefix = "${local.name_prefix}-db-"
  vpc_id      = module.networking.vpc_id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-sg"
  })
}
```

## 📈 Cost Optimization

### Resource Sizing by Environment
```hcl
# Production - Optimized for performance
ecs_cpu    = 2048
ecs_memory = 4096
db_instance_class = "db.t3.small"
elasticache_node_type = "cache.t3.small"

# Staging - Balanced
ecs_cpu    = 1024
ecs_memory = 2048
db_instance_class = "db.t3.micro"
elasticache_node_type = "cache.t3.micro"

# Development - Minimal
ecs_cpu    = 512
ecs_memory = 1024
db_instance_class = "db.t3.micro"
elasticache_node_type = "cache.t3.micro"
```

### Auto Scaling Configuration
```hcl
# CPU-based scaling
resource "aws_appautoscaling_policy" "cpu_scaling" {
  name               = "${local.name_prefix}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}
```

## 🔄 Backup & Disaster Recovery

### RDS Automated Backups
```hcl
resource "aws_db_instance" "main" {
  # ... other configuration ...
  
  backup_retention_period = var.db_backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  # Point-in-time recovery
  delete_automated_backups = false
  
  # Final snapshot
  skip_final_snapshot       = false
  final_snapshot_identifier = "${local.name_prefix}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
}
```

### S3 Versioning & Lifecycle
```hcl
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "lifecycle"
    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_transition {
      noncurrent_days = 60
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }
}
```

This comprehensive AWS infrastructure guide provides complete Terraform configurations for deploying JobQuest Navigator v3's four core systems with enterprise-level security, monitoring, and cost optimization.