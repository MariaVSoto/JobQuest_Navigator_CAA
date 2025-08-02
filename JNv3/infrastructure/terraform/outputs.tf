# JobQuest Navigator v3 - Terraform Outputs
# Important information for deployment and operations

# ============================================================================
# NETWORKING OUTPUTS
# ============================================================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "List of database subnet IDs"
  value       = aws_subnet.database[*].id
}

output "nat_gateway_ip" {
  description = "Public IP of NAT Gateway"
  value       = aws_eip.nat.public_ip
}

# ============================================================================
# LOAD BALANCER OUTPUTS
# ============================================================================

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "application_url" {
  description = "URL of the deployed application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "backend_target_group_arn" {
  description = "ARN of the backend target group"
  value       = aws_lb_target_group.backend.arn
}

output "frontend_target_group_arn" {
  description = "ARN of the frontend target group"
  value       = aws_lb_target_group.frontend.arn
}

# ============================================================================
# DATABASE OUTPUTS
# ============================================================================

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS database port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

output "database_connection_string" {
  description = "Database connection string"
  value       = "postgresql://${aws_db_instance.main.username}:${random_password.db_password.result}@${aws_db_instance.main.endpoint}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
  sensitive   = true
}

# ============================================================================
# CONTAINER REGISTRY OUTPUTS
# ============================================================================

output "backend_ecr_repository_url" {
  description = "URL of the ECR repository for backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "frontend_ecr_repository_url" {
  description = "URL of the ECR repository for frontend"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecr_repository_arns" {
  description = "ARNs of ECR repositories"
  value = {
    backend  = aws_ecr_repository.backend.arn
    frontend = aws_ecr_repository.frontend.arn
  }
}

# ============================================================================
# ECS OUTPUTS
# ============================================================================

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = aws_ecs_service.backend.name
}

output "frontend_service_name" {
  description = "Name of the frontend ECS service"
  value       = aws_ecs_service.frontend.name
}

output "backend_task_definition_arn" {
  description = "ARN of the backend task definition"
  value       = aws_ecs_task_definition.backend.arn
}

output "frontend_task_definition_arn" {
  description = "ARN of the frontend task definition"
  value       = aws_ecs_task_definition.frontend.arn
}

# ============================================================================
# SECURITY OUTPUTS
# ============================================================================

output "security_group_ids" {
  description = "Map of security group IDs"
  value = {
    alb = aws_security_group.alb.id
    ecs = aws_security_group.ecs.id
    rds = aws_security_group.rds.id
  }
}

# ============================================================================
# IAM OUTPUTS
# ============================================================================

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

# ============================================================================
# LOGGING OUTPUTS
# ============================================================================

output "cloudwatch_log_groups" {
  description = "CloudWatch log group names"
  value = {
    backend  = aws_cloudwatch_log_group.backend.name
    frontend = aws_cloudwatch_log_group.frontend.name
  }
}

# ============================================================================
# DEPLOYMENT INFORMATION
# ============================================================================

output "deployment_info" {
  description = "Complete deployment information"
  value = {
    # Application URLs
    application_url  = "http://${aws_lb.main.dns_name}"
    backend_api_url  = "http://${aws_lb.main.dns_name}/api"
    health_check_url = "http://${aws_lb.main.dns_name}/health"

    # Container registries
    backend_repo_url  = aws_ecr_repository.backend.repository_url
    frontend_repo_url = aws_ecr_repository.frontend.repository_url

    # ECS information
    cluster_name     = aws_ecs_cluster.main.name
    backend_service  = aws_ecs_service.backend.name
    frontend_service = aws_ecs_service.frontend.name

    # Database information
    database_endpoint = aws_db_instance.main.endpoint

    # Environment
    environment  = var.environment
    aws_region   = var.aws_region
    project_name = var.project_name
  }
}

# ============================================================================
# RESOURCE IDENTIFIERS
# ============================================================================

output "resource_identifiers" {
  description = "Important resource identifiers for management"
  value = {
    vpc_id              = aws_vpc.main.id
    cluster_name        = aws_ecs_cluster.main.name
    load_balancer_arn   = aws_lb.main.arn
    database_identifier = aws_db_instance.main.identifier
    backend_repo_name   = aws_ecr_repository.backend.name
    frontend_repo_name  = aws_ecr_repository.frontend.name
  }
}