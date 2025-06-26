# JobQuest Navigator - Terraform Outputs
# This file defines outputs that will be available after terraform apply

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

# Security Group Outputs
output "lambda_security_group_id" {
  description = "ID of the Lambda security group"
  value       = module.security.lambda_sg_id
}

output "database_security_group_id" {
  description = "ID of the database security group"
  value       = module.security.database_sg_id
}

# S3 Outputs
output "static_bucket_name" {
  description = "Name of the S3 bucket for static files"
  value       = module.s3.static_bucket_name
}

output "static_bucket_arn" {
  description = "ARN of the S3 bucket for static files"
  value       = module.s3.static_bucket_arn
}

output "static_bucket_domain_name" {
  description = "Domain name of the S3 bucket for static files"
  value       = module.s3.static_bucket_domain_name
}

output "frontend_bucket_name" {
  description = "Name of the S3 bucket for frontend hosting"
  value       = module.s3.frontend_bucket_name
}

output "frontend_bucket_arn" {
  description = "ARN of the S3 bucket for frontend hosting"
  value       = module.s3.frontend_bucket_arn
}

output "frontend_website_url" {
  description = "Website URL of the frontend S3 bucket"
  value       = module.s3.frontend_website_url
}

output "lambda_deployment_bucket_name" {
  description = "Name of the S3 bucket for Lambda deployments"
  value       = module.s3.lambda_deployment_bucket_name
}

# RDS Outputs
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_endpoint
  sensitive   = false
}

output "database_port" {
  description = "RDS instance port"
  value       = module.rds.db_port
}

output "database_name" {
  description = "Database name"
  value       = module.rds.db_name
}

output "database_username" {
  description = "Database master username"
  value       = module.rds.db_username
  sensitive   = true
}

output "database_instance_id" {
  description = "RDS instance ID"
  value       = module.rds.db_instance_id
}

# Secrets Manager Outputs
output "database_password_secret_arn" {
  description = "ARN of the database password secret in Secrets Manager"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "database_password_secret_name" {
  description = "Name of the database password secret in Secrets Manager"
  value       = aws_secretsmanager_secret.db_password.name
}

# IAM Outputs
output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = module.iam.lambda_execution_role_arn
}

output "lambda_execution_role_name" {
  description = "Name of the Lambda execution role"
  value       = module.iam.lambda_execution_role_name
}

# Lambda Outputs (if created)
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = var.create_lambda_function ? aws_lambda_function.api_placeholder[0].function_name : null
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = var.create_lambda_function ? aws_lambda_function.api_placeholder[0].arn : null
}

# API Gateway Outputs (if created)
output "api_gateway_rest_api_id" {
  description = "ID of the API Gateway REST API"
  value       = var.create_api_gateway ? aws_api_gateway_rest_api.api[0].id : null
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = var.create_api_gateway ? "https://${aws_api_gateway_rest_api.api[0].id}.execute-api.${var.aws_region}.amazonaws.com/${var.environment}" : null
}

# CloudWatch Outputs
output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = module.monitoring.sns_topic_arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for Lambda"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

# Environment Configuration Outputs
output "environment_variables" {
  description = "Environment variables for Lambda function"
  value = {
    DJANGO_SETTINGS_MODULE  = "core.settings_production"
    RDS_HOSTNAME           = module.rds.db_endpoint
    RDS_DB_NAME            = module.rds.db_name
    RDS_USERNAME           = module.rds.db_username
    RDS_PORT               = tostring(module.rds.db_port)
    AWS_STORAGE_BUCKET_NAME = module.s3.static_bucket_name
    AWS_S3_REGION_NAME     = var.aws_region
    AWS_DEFAULT_REGION     = var.aws_region
  }
  sensitive = false
}

# Deployment Information
output "deployment_info" {
  description = "Information needed for application deployment"
  value = {
    project_name = var.project_name
    environment  = var.environment
    aws_region   = var.aws_region
    
    # Database connection
    database_endpoint = module.rds.db_endpoint
    database_name     = module.rds.db_name
    database_username = module.rds.db_username
    database_port     = module.rds.db_port
    
    # S3 buckets
    static_bucket_name   = module.s3.static_bucket_name
    frontend_bucket_name = module.s3.frontend_bucket_name
    lambda_bucket_name   = module.s3.lambda_deployment_bucket_name
    
    # Network configuration
    vpc_id              = module.vpc.vpc_id
    lambda_sg_id        = module.security.lambda_sg_id
    private_subnet_ids  = module.vpc.private_subnet_ids
    
    # IAM
    lambda_role_arn = module.iam.lambda_execution_role_arn
    
    # Secrets
    db_password_secret_name = aws_secretsmanager_secret.db_password.name
  }
}

# Cost Information
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown (USD)"
  value = {
    rds_db_instance = "~$15 (db.t3.micro)"
    lambda_requests = "~$2 (1M requests)"
    api_gateway     = "~$3 (1M requests)"
    s3_storage      = "~$0.12 (5GB)"
    data_transfer   = "~$0.90 (10GB)"
    cloudwatch      = "~$0.50 (basic monitoring)"
    total_estimated = "~$21.52"
    note           = "Costs may vary based on actual usage. Free tier benefits may apply."
  }
}

# Quick Setup Commands
output "quick_setup_commands" {
  description = "Commands to quickly set up the deployment"
  value = {
    # Get database password
    get_db_password = "aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_password.name} --query SecretString --output text"
    
    # Test database connection
    test_db_connection = "mysql -h ${module.rds.db_endpoint} -u ${module.rds.db_username} -p ${module.rds.db_name}"
    
    # Sync frontend to S3
    sync_frontend = "aws s3 sync build/ s3://${module.s3.frontend_bucket_name}"
    
    # View Lambda logs
    view_logs = var.create_lambda_function ? "aws logs tail /aws/lambda/${aws_lambda_function.api_placeholder[0].function_name}" : "N/A - Lambda not created by Terraform"
  }
}

# Zappa Configuration
output "zappa_configuration" {
  description = "Configuration values for Zappa deployment"
  value = {
    aws_region = var.aws_region
    vpc_config = {
      SubnetIds        = module.vpc.private_subnet_ids
      SecurityGroupIds = [module.security.lambda_sg_id]
    }
    environment_variables = {
      RDS_HOSTNAME           = module.rds.db_endpoint
      RDS_DB_NAME            = module.rds.db_name
      RDS_USERNAME           = module.rds.db_username
      RDS_PORT               = tostring(module.rds.db_port)
      AWS_STORAGE_BUCKET_NAME = module.s3.static_bucket_name
      AWS_S3_REGION_NAME     = var.aws_region
    }
    s3_bucket = module.s3.lambda_deployment_bucket_name
    role_arn  = module.iam.lambda_execution_role_arn
  }
}