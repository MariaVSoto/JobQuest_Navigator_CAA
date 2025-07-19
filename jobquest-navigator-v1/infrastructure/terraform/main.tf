# JobQuest Navigator - Terraform Main Configuration
# This file defines the main infrastructure for JobQuest Navigator

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Owner       = var.project_owner
      Purpose     = "Graduation Project"
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Random password for RDS
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store database password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name        = "${var.project_name}-db-password-${var.environment}"
  description = "Database password for ${var.project_name}"

  recovery_window_in_days = 0 # For easy cleanup in development
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  
  vpc_cidr = var.vpc_cidr
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 2)
}

# Security Groups Module
module "security" {
  source = "./modules/security"

  project_name = var.project_name
  environment  = var.environment
  
  vpc_id = module.vpc.vpc_id
}

# S3 Module
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
}

# RDS Module
module "rds" {
  source = "./modules/rds"

  project_name = var.project_name
  environment  = var.environment
  
  vpc_id               = module.vpc.vpc_id
  private_subnet_ids   = module.vpc.private_subnet_ids
  database_sg_id       = module.security.database_sg_id
  
  db_password = random_password.db_password.result
  db_instance_class = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  project_name = var.project_name
  environment  = var.environment
  
  static_bucket_arn = module.s3.static_bucket_arn
}

# CloudWatch Module
module "monitoring" {
  source = "./modules/monitoring"

  project_name = var.project_name
  environment  = var.environment
  
  alert_email = var.alert_email
  db_instance_id = module.rds.db_instance_id
}

# Lambda function placeholder (will be deployed by Zappa)
# This creates the necessary IAM role and policies
resource "aws_lambda_function" "api_placeholder" {
  function_name = "${var.project_name}-api-${var.environment}"
  role         = module.iam.lambda_execution_role_arn
  handler      = "index.handler"
  runtime      = "python3.9"
  timeout      = 300
  memory_size  = 512

  # Placeholder code
  filename         = "${path.module}/lambda_placeholder.zip"
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  vpc_config {
    subnet_ids         = module.vpc.private_subnet_ids
    security_group_ids = [module.security.lambda_sg_id]
  }

  environment {
    variables = {
      DJANGO_SETTINGS_MODULE = "core.settings_production"
      RDS_HOSTNAME          = module.rds.db_endpoint
      RDS_DB_NAME           = module.rds.db_name
      RDS_USERNAME          = module.rds.db_username
      AWS_STORAGE_BUCKET_NAME = module.s3.static_bucket_name
      AWS_S3_REGION_NAME    = var.aws_region
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_vpc_access,
    aws_cloudwatch_log_group.lambda_logs,
  ]

  lifecycle {
    ignore_changes = [
      # Zappa will manage these
      filename,
      source_code_hash,
      last_modified,
    ]
  }
}

# Create placeholder Lambda zip
data "archive_file" "lambda_placeholder" {
  type        = "zip"
  output_path = "${path.module}/lambda_placeholder.zip"
  source {
    content  = "def handler(event, context): return {'statusCode': 200, 'body': 'Placeholder'}"
    filename = "index.py"
  }
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.project_name}-api-${var.environment}"
  retention_in_days = 14
}

# IAM role policy attachment for VPC access
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = module.iam.lambda_execution_role_name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# API Gateway placeholder (will be managed by Zappa)
resource "aws_api_gateway_rest_api" "api" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "JobQuest Navigator REST API"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    ignore_changes = [
      # Zappa will manage the API Gateway configuration
      body,
    ]
  }
}

resource "aws_api_gateway_deployment" "api" {
  depends_on = [aws_api_gateway_rest_api.api]

  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
    ignore_changes = [
      # Zappa will handle deployments
      deployment_id,
    ]
  }
}