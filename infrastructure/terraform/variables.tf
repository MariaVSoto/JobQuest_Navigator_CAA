# JobQuest Navigator - Terraform Variables
# This file defines all input variables for the infrastructure

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "jobquest-navigator"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (e.g., production, staging, development)"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be one of: production, staging, development."
  }
}

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "project_owner" {
  description = "Owner of the project (for tagging)"
  type        = string
  default     = "JobQuest Navigator Team"
}

variable "alert_email" {
  description = "Email address for CloudWatch alarms and notifications"
  type        = string
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alert_email))
    error_message = "Alert email must be a valid email address."
  }
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
  
  validation {
    condition     = can(regex("^db\\.", var.db_instance_class))
    error_message = "DB instance class must start with 'db.'."
  }
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS instance (GB)"
  type        = number
  default     = 20
  
  validation {
    condition     = var.db_allocated_storage >= 20 && var.db_allocated_storage <= 100
    error_message = "DB allocated storage must be between 20 and 100 GB."
  }
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "jobquest_navigator"
  
  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_name))
    error_message = "Database name must start with a letter and contain only letters, numbers, and underscores."
  }
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "admin"
  
  validation {
    condition     = length(var.db_username) >= 1 && length(var.db_username) <= 16
    error_message = "Database username must be between 1 and 16 characters."
  }
}

# Lambda Configuration
variable "lambda_memory_size" {
  description = "Memory size for Lambda function (MB)"
  type        = number
  default     = 512
  
  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 3008
    error_message = "Lambda memory size must be between 128 and 3008 MB."
  }
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function (seconds)"
  type        = number
  default     = 300
  
  validation {
    condition     = var.lambda_timeout >= 1 && var.lambda_timeout <= 900
    error_message = "Lambda timeout must be between 1 and 900 seconds."
  }
}

# S3 Configuration
variable "enable_s3_versioning" {
  description = "Enable versioning on S3 buckets"
  type        = bool
  default     = true
}

variable "s3_lifecycle_expiration_days" {
  description = "Number of days after which to expire S3 objects"
  type        = number
  default     = 90
  
  validation {
    condition     = var.s3_lifecycle_expiration_days > 0
    error_message = "S3 lifecycle expiration days must be greater than 0."
  }
}

# Monitoring Configuration
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = false
}

variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 14
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

# Cost Optimization
variable "enable_rds_deletion_protection" {
  description = "Enable deletion protection for RDS instance"
  type        = bool
  default     = false
}

variable "rds_backup_retention_period" {
  description = "Backup retention period for RDS (days)"
  type        = number
  default     = 7
  
  validation {
    condition     = var.rds_backup_retention_period >= 0 && var.rds_backup_retention_period <= 35
    error_message = "RDS backup retention period must be between 0 and 35 days."
  }
}

# Security Configuration
variable "enable_rds_encryption" {
  description = "Enable encryption at rest for RDS"
  type        = bool
  default     = true
}

variable "enable_s3_encryption" {
  description = "Enable encryption for S3 buckets"
  type        = bool
  default     = true
}

# CORS Configuration for S3
variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_allowed_methods" {
  description = "List of allowed HTTP methods for CORS"
  type        = list(string)
  default     = ["GET", "PUT", "POST", "DELETE", "HEAD"]
}

variable "cors_max_age_seconds" {
  description = "Maximum age for CORS preflight requests (seconds)"
  type        = number
  default     = 3600
}

# CloudWatch Alarms Thresholds
variable "rds_cpu_threshold" {
  description = "CPU utilization threshold for RDS alarms (%)"
  type        = number
  default     = 80
  
  validation {
    condition     = var.rds_cpu_threshold > 0 && var.rds_cpu_threshold <= 100
    error_message = "RDS CPU threshold must be between 0 and 100."
  }
}

variable "lambda_error_threshold" {
  description = "Error count threshold for Lambda alarms"
  type        = number
  default     = 10
  
  validation {
    condition     = var.lambda_error_threshold > 0
    error_message = "Lambda error threshold must be greater than 0."
  }
}

variable "lambda_duration_threshold" {
  description = "Duration threshold for Lambda alarms (milliseconds)"
  type        = number
  default     = 10000
  
  validation {
    condition     = var.lambda_duration_threshold > 0
    error_message = "Lambda duration threshold must be greater than 0."
  }
}

# Feature Flags
variable "create_api_gateway" {
  description = "Create API Gateway resources (disable if using Zappa)"
  type        = bool
  default     = true
}

variable "create_lambda_function" {
  description = "Create Lambda function placeholder (disable if using Zappa)"
  type        = bool
  default     = true
}

variable "enable_cloudfront" {
  description = "Enable CloudFront distribution for frontend"
  type        = bool
  default     = false
}

# Multi-AZ Configuration
variable "enable_multi_az" {
  description = "Enable Multi-AZ for RDS (increases cost)"
  type        = bool
  default     = false
}