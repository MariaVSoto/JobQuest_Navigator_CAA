# JobQuest Navigator v2 - Terraform Outputs
# Important information for deployment and operations

# ============================================================================
# NETWORKING OUTPUTS
# ============================================================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "database_subnet_ids" {
  description = "List of database subnet IDs"
  value       = module.vpc.database_subnet_ids
}

output "nat_gateway_ips" {
  description = "List of public Elastic IPs of NAT Gateways"
  value       = module.vpc.nat_gateway_ips
}

# ============================================================================
# LOAD BALANCER OUTPUTS
# ============================================================================

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = module.alb.alb_zone_id
}

output "alb_url" {
  description = "URL of the Application Load Balancer"
  value       = "https://${module.alb.alb_dns_name}"
}

output "backend_target_group_arn" {
  description = "ARN of the backend target group"
  value       = module.alb.backend_target_group_arn
}

output "frontend_target_group_arn" {
  description = "ARN of the frontend target group"
  value       = module.alb.frontend_target_group_arn
}

# ============================================================================
# DATABASE OUTPUTS
# ============================================================================

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = module.rds.port
}

output "rds_instance_id" {
  description = "RDS instance ID"
  value       = module.rds.instance_id
}

output "database_url" {
  description = "Database connection URL"
  value       = "postgresql+asyncpg://${var.database_username}:***@${module.rds.endpoint}:${module.rds.port}/${var.database_name}"
  sensitive   = true
}

# ============================================================================
# CACHE OUTPUTS
# ============================================================================

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.elasticache.primary_endpoint
}

output "redis_port" {
  description = "Redis cluster port"
  value       = module.elasticache.port
}

output "redis_url" {
  description = "Redis connection URL"
  value       = "redis://${module.elasticache.primary_endpoint}:${module.elasticache.port}/0"
}

# ============================================================================
# CONTAINER REGISTRY OUTPUTS
# ============================================================================

output "ecr_repository_urls" {
  description = "Map of ECR repository URLs"
  value       = module.ecr.repository_urls
}

output "ecr_repository_arns" {
  description = "Map of ECR repository ARNs"
  value       = module.ecr.repository_arns
}

# ============================================================================
# ECS OUTPUTS
# ============================================================================

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = module.ecs.cluster_id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.ecs.cluster_arn
}

output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = module.ecs.backend_service_name
}

output "frontend_service_name" {
  description = "Name of the frontend ECS service"
  value       = module.ecs.frontend_service_name
}

output "backend_task_definition_arn" {
  description = "ARN of the backend task definition"
  value       = module.ecs.backend_task_definition_arn
}

output "frontend_task_definition_arn" {
  description = "ARN of the frontend task definition"
  value       = module.ecs.frontend_task_definition_arn
}

# ============================================================================
# STORAGE OUTPUTS
# ============================================================================

output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = module.s3.bucket_name
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = module.s3.bucket_arn
}

output "s3_bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = module.s3.bucket_domain_name
}

# ============================================================================
# IAM OUTPUTS
# ============================================================================

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = module.iam.ecs_task_execution_role_arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = module.iam.ecs_task_role_arn
}

output "deployment_role_arn" {
  description = "ARN of the deployment role for CI/CD"
  value       = module.iam.deployment_role_arn
}

# ============================================================================
# SECURITY OUTPUTS
# ============================================================================

output "security_group_ids" {
  description = "Map of security group IDs"
  value = {
    alb      = module.security_groups.alb_security_group_id
    backend  = module.security_groups.backend_security_group_id
    frontend = module.security_groups.frontend_security_group_id
    rds      = module.security_groups.rds_security_group_id
    redis    = module.security_groups.redis_security_group_id
  }
}

# ============================================================================
# SECRETS OUTPUTS
# ============================================================================

output "secrets_manager_arns" {
  description = "ARNs of secrets in AWS Secrets Manager"
  value = {
    database_password = aws_secretsmanager_secret.db_password.arn
    app_secret_key    = aws_secretsmanager_secret.app_secret_key.arn
  }
}

# ============================================================================
# MONITORING OUTPUTS
# ============================================================================

output "cloudwatch_log_groups" {
  description = "CloudWatch log group names"
  value       = module.cloudwatch.log_group_names
}

output "cloudwatch_dashboard_url" {
  description = "URL to the CloudWatch dashboard"
  value       = module.cloudwatch.dashboard_url
}

# ============================================================================
# DEPLOYMENT INFORMATION
# ============================================================================

output "deployment_info" {
  description = "Key information for deployment scripts"
  value = {
    environment        = var.environment
    aws_region        = var.aws_region
    project_name      = var.project_name
    
    # Application URLs
    app_url           = "https://${module.alb.alb_dns_name}"
    backend_url       = "https://${module.alb.alb_dns_name}/api"
    graphql_url       = "https://${module.alb.alb_dns_name}/graphql"
    
    # Container registries
    backend_ecr_url   = module.ecr.repository_urls["jobquest-backend"]
    frontend_ecr_url  = module.ecr.repository_urls["jobquest-frontend"]
    
    # ECS information
    cluster_name      = module.ecs.cluster_name
    backend_service   = module.ecs.backend_service_name
    frontend_service  = module.ecs.frontend_service_name
    
    # Database information
    database_endpoint = module.rds.endpoint
    redis_endpoint    = module.elasticache.primary_endpoint
    
    # Storage
    s3_bucket        = module.s3.bucket_name
  }
}

# ============================================================================
# COST OPTIMIZATION OUTPUTS
# ============================================================================

output "cost_optimization_info" {
  description = "Information for cost optimization"
  value = {
    single_nat_gateway = var.single_nat_gateway
    rds_instance_class = var.rds_instance_class
    redis_node_type    = var.redis_node_type
    backup_enabled     = var.backup_retention_period > 0
    multi_az_enabled   = var.environment == "production"
  }
}