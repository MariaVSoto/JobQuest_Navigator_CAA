# JobQuest Navigator v3 - Terraform Variables
# All configurable parameters for production infrastructure

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "jobquest-navigator-v3"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "secret_key" {
  description = "Secret key for application security"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.secret_key) >= 32
    error_message = "Secret key must be at least 32 characters long."
  }
}

# ============================================================================
# NETWORKING CONFIGURATION
# ============================================================================

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
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
  default     = ["10.0.21.0/24", "10.0.30.0/24"]
}

# ============================================================================
# DATABASE CONFIGURATION (RDS PostgreSQL)
# ============================================================================

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15.13"
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
  default     = "jobquest"
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
  default     = "07:00-09:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window (UTC)"
  type        = string
  default     = "sun:09:00-sun:11:00"
}

# ============================================================================
# CONTAINER CONFIGURATION (ECS)
# ============================================================================

variable "backend_cpu" {
  description = "CPU units for backend container (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Memory for backend container in MB"
  type        = number
  default     = 512
}

variable "backend_desired_count" {
  description = "Desired number of backend containers"
  type        = number
  default     = 1
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
  default     = 1
}

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

variable "backend_port" {
  description = "Port for backend container"
  type        = number
  default     = 8000
}

variable "frontend_port" {
  description = "Port for frontend container"
  type        = number
  default     = 3000
}

variable "alb_port" {
  description = "Port for Application Load Balancer"
  type        = number
  default     = 80
}

variable "backend_target_group_name" {
  description = "Name for backend target group"
  type        = string
  default     = "jqnav-v3-backend-tg"
}

variable "frontend_target_group_name" {
  description = "Name for frontend target group"
  type        = string
  default     = "jqnav-v3-frontend-tg"
}

variable "health_check_path" {
  description = "Health check path for backend"
  type        = string
  default     = "/health"
}

variable "api_path_patterns" {
  description = "Path patterns for API routing"
  type        = list(string)
  default     = ["/api/*", "/graphql/*", "/health"]
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

variable "enable_container_insights" {
  description = "Enable ECS Container Insights"
  type        = bool
  default     = true
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when deleting RDS instance"
  type        = bool
  default     = true
}