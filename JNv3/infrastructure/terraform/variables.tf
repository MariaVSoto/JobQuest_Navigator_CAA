# JobQuest Navigator v2 - Terraform Variables
# All configurable parameters for the infrastructure

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "jobquest-navigator-v2"
}

variable "project_owner" {
  description = "Owner of the project"
  type        = string
  default     = "JobQuest Team"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  
  validation {
    condition = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

# ============================================================================
# NETWORKING CONFIGURATION
# ============================================================================

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to use"
  type        = number
  default     = 2
  
  validation {
    condition = var.az_count >= 2 && var.az_count <= 6
    error_message = "AZ count must be between 2 and 6."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.30.0/24", "10.0.40.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for cost optimization"
  type        = bool
  default     = true
}

# ============================================================================
# DATABASE CONFIGURATION (RDS PostgreSQL)
# ============================================================================

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15.4"
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "Initial allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "rds_max_allocated_storage" {
  description = "Maximum allocated storage for RDS auto scaling in GB"
  type        = number
  default     = 100
}

variable "database_name" {
  description = "Name of the initial database"
  type        = string
  default     = "jobquest_navigator_v2"
}

variable "database_username" {
  description = "Master username for the database"
  type        = string
  default     = "jobquest_user"
}

variable "backup_retention_period" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Preferred backup window (UTC)"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window (UTC)"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

# ============================================================================
# CACHE CONFIGURATION (ElastiCache Redis)
# ============================================================================

variable "redis_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

variable "redis_parameter_group" {
  description = "Parameter group for Redis"
  type        = string
  default     = "default.redis7"
}

# ============================================================================
# CONTAINER CONFIGURATION (ECS)
# ============================================================================

variable "backend_cpu" {
  description = "CPU units for backend container (1024 = 1 vCPU)"
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Memory for backend container in MB"
  type        = number
  default     = 1024
}

variable "backend_desired_count" {
  description = "Desired number of backend containers"
  type        = number
  default     = 2
}

variable "frontend_cpu" {
  description = "CPU units for frontend container (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Memory for frontend container in MB"
  type        = number
  default     = 512
}

variable "frontend_desired_count" {
  description = "Desired number of frontend containers"
  type        = number
  default     = 2
}

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

variable "cognito_user_pool_id" {
  description = "AWS Cognito User Pool ID"
  type        = string
  default     = ""
}

variable "cognito_client_id" {
  description = "AWS Cognito Client ID"
  type        = string
  default     = ""
}

variable "cors_origins" {
  description = "Allowed CORS origins"
  type        = string
  default     = "*"
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate for HTTPS"
  type        = string
  default     = ""
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for file storage (production use)"
  type        = string
  default     = "caa900resume"
}

# ============================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# ============================================================================

variable "environment_config" {
  description = "Environment-specific configuration overrides"
  type = map(object({
    rds_instance_class    = string
    redis_node_type      = string
    backend_cpu          = number
    backend_memory       = number
    backend_desired_count = number
    frontend_cpu         = number
    frontend_memory      = number
    frontend_desired_count = number
    enable_backup        = bool
    multi_az            = bool
  }))
  
  default = {
    development = {
      rds_instance_class     = "db.t3.micro"
      redis_node_type       = "cache.t3.micro"
      backend_cpu           = 256
      backend_memory        = 512
      backend_desired_count  = 1
      frontend_cpu          = 256
      frontend_memory       = 512
      frontend_desired_count = 1
      enable_backup         = false
      multi_az             = false
    }
    
    staging = {
      rds_instance_class     = "db.t3.small"
      redis_node_type       = "cache.t3.small"
      backend_cpu           = 512
      backend_memory        = 1024
      backend_desired_count  = 2
      frontend_cpu          = 256
      frontend_memory       = 512
      frontend_desired_count = 2
      enable_backup         = true
      multi_az             = false
    }
    
    production = {
      rds_instance_class     = "db.t3.medium"
      redis_node_type       = "cache.t3.medium"
      backend_cpu           = 1024
      backend_memory        = 2048
      backend_desired_count  = 3
      frontend_cpu          = 512
      frontend_memory       = 1024
      frontend_desired_count = 3
      enable_backup         = true
      multi_az             = true
    }
  }
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_auto_scaling" {
  description = "Enable auto scaling for ECS services"
  type        = bool
  default     = true
}

variable "enable_container_insights" {
  description = "Enable ECS Container Insights"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

# ============================================================================
# COST OPTIMIZATION
# ============================================================================

variable "enable_spot_instances" {
  description = "Use spot instances for cost optimization (non-production)"
  type        = bool
  default     = false
}

variable "enable_scheduled_scaling" {
  description = "Enable scheduled scaling to reduce costs during off-hours"
  type        = bool
  default     = false
}