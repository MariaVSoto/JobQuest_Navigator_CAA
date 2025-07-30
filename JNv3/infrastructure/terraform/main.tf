# JobQuest Navigator v2 - Main Terraform Configuration
# Container-first Hybrid Architecture for AWS Deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration for state management
  backend "s3" {
    # This will be configured via terraform init -backend-config
    # bucket = "jobquest-terraform-state"
    # key    = "main/terraform.tfstate"
    # region = "us-east-1"
    # encrypt = true
    # dynamodb_table = "jobquest-terraform-locks"
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.project_owner
    }
  }
}

# Local values for resource naming and configuration
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  # Common tags for all resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.project_owner
  }
  
  # AZ configuration
  azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  vpc_cidr             = var.vpc_cidr
  availability_zones   = local.azs
  public_subnets       = var.public_subnet_cidrs
  private_subnets      = var.private_subnet_cidrs
  database_subnets     = var.database_subnet_cidrs
  
  enable_nat_gateway   = var.enable_nat_gateway
  single_nat_gateway   = var.single_nat_gateway
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = local.common_tags
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security"
  
  name_prefix = local.name_prefix
  environment = var.environment
  vpc_id      = module.vpc.vpc_id
  
  tags = local.common_tags
}

# ECR Module (for container images)
module "ecr" {
  source = "./modules/ecr"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  repositories = [
    "jobquest-backend",
    "jobquest-frontend"
  ]
  
  tags = local.common_tags
}

# RDS Module (PostgreSQL database)
module "rds" {
  source = "./modules/rds"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  vpc_id                = module.vpc.vpc_id
  database_subnet_ids   = module.vpc.database_subnet_ids
  security_group_ids    = [module.security_groups.rds_security_group_id]
  
  # Database configuration
  engine                = "postgres"
  engine_version        = var.postgres_version
  instance_class        = var.rds_instance_class
  allocated_storage     = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage
  storage_encrypted     = true
  
  # Database credentials
  database_name = var.database_name
  master_username = var.database_username
  
  # Backup and maintenance
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window
  
  # High availability
  multi_az = var.environment == "production"
  
  tags = local.common_tags
}

# ElastiCache Module (Redis)
module "elasticache" {
  source = "./modules/elasticache"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  vpc_id               = module.vpc.vpc_id
  subnet_ids           = module.vpc.private_subnet_ids
  security_group_ids   = [module.security_groups.redis_security_group_id]
  
  # Redis configuration
  node_type           = var.redis_node_type
  num_cache_nodes     = var.redis_num_nodes
  parameter_group_name = var.redis_parameter_group
  engine_version      = var.redis_version
  port                = 6379
  
  tags = local.common_tags
}

# Application Load Balancer Module
module "alb" {
  source = "./modules/alb"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  security_group_ids  = [module.security_groups.alb_security_group_id]
  
  # SSL certificate
  certificate_arn = var.ssl_certificate_arn
  
  tags = local.common_tags
}

# ECS Cluster Module
module "ecs" {
  source = "./modules/ecs"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  # Networking
  vpc_id            = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  
  # Load balancer
  target_group_arn = module.alb.backend_target_group_arn
  
  # Security groups
  backend_security_group_id  = module.security_groups.backend_security_group_id
  frontend_security_group_id = module.security_groups.frontend_security_group_id
  
  # Container images
  backend_image_uri  = "${module.ecr.repository_urls["jobquest-backend"]}:latest"
  frontend_image_uri = "${module.ecr.repository_urls["jobquest-frontend"]}:latest"
  
  # Environment variables
  environment_variables = {
    DATABASE_URL = "postgresql+asyncpg://${var.database_username}:${random_password.db_password.result}@${module.rds.endpoint}:5432/${var.database_name}"
    REDIS_URL    = "redis://${module.elasticache.primary_endpoint}:6379/0"
    
    # Application settings
    ENVIRONMENT  = var.environment
    DEBUG        = var.environment != "production" ? "true" : "false"
    SECRET_KEY   = random_password.secret_key.result
    
    # AWS Cognito
    COGNITO_USER_POOL_ID = var.cognito_user_pool_id
    COGNITO_CLIENT_ID    = var.cognito_client_id
    AWS_REGION          = var.aws_region
    
    # CORS
    CORS_ORIGINS = var.cors_origins
  }
  
  # Service configuration
  backend_cpu    = var.backend_cpu
  backend_memory = var.backend_memory
  backend_count  = var.backend_desired_count
  
  frontend_cpu    = var.frontend_cpu
  frontend_memory = var.frontend_memory
  frontend_count  = var.frontend_desired_count
  
  tags = local.common_tags
  
  depends_on = [module.rds, module.elasticache]
}

# S3 Bucket for file storage
module "s3" {
  source = "./modules/s3"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  # Use specific bucket name if provided, otherwise generate name
  bucket_name = var.s3_bucket_name != "" ? var.s3_bucket_name : "${local.name_prefix}-storage"
  
  # Enable versioning for production
  versioning_enabled = var.environment == "production"
  
  tags = local.common_tags
}

# CloudWatch Module for monitoring
module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  # ECS resources for monitoring
  ecs_cluster_name = module.ecs.cluster_name
  ecs_service_names = [
    module.ecs.backend_service_name,
    module.ecs.frontend_service_name
  ]
  
  # RDS and ElastiCache for monitoring
  rds_instance_id = module.rds.instance_id
  elasticache_cluster_id = module.elasticache.cluster_id
  
  # ALB for monitoring
  alb_arn_suffix = module.alb.alb_arn_suffix
  target_group_arn_suffix = module.alb.backend_target_group_arn_suffix
  
  tags = local.common_tags
}

# IAM Module for roles and policies
module "iam" {
  source = "./modules/iam"
  
  name_prefix = local.name_prefix
  environment = var.environment
  
  # Account ID for ARN construction
  account_id = data.aws_caller_identity.current.account_id
  aws_region = var.aws_region
  
  # ECR repository ARNs
  ecr_repository_arns = [for repo in module.ecr.repository_arns : repo]
  
  # S3 bucket ARN
  s3_bucket_arn = module.s3.bucket_arn
  
  tags = local.common_tags
}

# Random passwords for sensitive data
resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "random_password" "secret_key" {
  length  = 32
  special = true
}

# Store secrets in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name        = "${local.name_prefix}-db-password"
  description = "Database password for ${var.project_name}"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}

resource "aws_secretsmanager_secret" "app_secret_key" {
  name        = "${local.name_prefix}-app-secret-key"
  description = "Application secret key for ${var.project_name}"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "app_secret_key" {
  secret_id     = aws_secretsmanager_secret.app_secret_key.id
  secret_string = random_password.secret_key.result
}