# JobQuest Navigator v2 - Development Environment Configuration
# Optimized for cost and development workflow

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================
project_name = "jobquest-navigator-v2"
environment  = "development"
aws_region   = "us-east-1"

# ============================================================================
# NETWORKING CONFIGURATION
# ============================================================================
vpc_cidr = "10.0.0.0/16"
az_count = 2

public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs  = ["10.0.10.0/24", "10.0.20.0/24"]
database_subnet_cidrs = ["10.0.30.0/24", "10.0.40.0/24"]

# Cost optimization: Single NAT gateway
enable_nat_gateway = true
single_nat_gateway = true

# ============================================================================
# DATABASE CONFIGURATION (Cost-optimized)
# ============================================================================
postgres_version        = "15.4"
rds_instance_class     = "db.t3.micro"
rds_allocated_storage  = 20
rds_max_allocated_storage = 50

database_name    = "jobquest_navigator_v2_dev"
database_username = "jobquest_dev_user"

# Minimal backup for development
backup_retention_period = 1
backup_window          = "03:00-04:00"
maintenance_window     = "sun:04:00-sun:05:00"

# ============================================================================
# CACHE CONFIGURATION (Cost-optimized)
# ============================================================================
redis_version         = "7.0"
redis_node_type      = "cache.t3.micro"
redis_num_nodes      = 1
redis_parameter_group = "default.redis7"

# ============================================================================
# CONTAINER CONFIGURATION (Resource-optimized for dev)
# ============================================================================
# Backend containers
backend_cpu           = 256
backend_memory        = 512
backend_desired_count = 1

# Frontend containers
frontend_cpu           = 256
frontend_memory        = 512
frontend_desired_count = 1

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================
# These will be provided via environment variables or during terraform apply
cognito_user_pool_id = "us-east-1_blSZREFys"
cognito_client_id    = "5iui547bod6sqgsi1a4heidpep"

# Development CORS - Allow all origins
cors_origins = "http://localhost:3000,http://localhost:3001,http://localhost:3002,https://*.amazonaws.com"

# SSL certificate (optional for development)
ssl_certificate_arn = ""

# S3 bucket configuration - use generated name for development
s3_bucket_name = ""  # Empty means use generated name

# ============================================================================
# FEATURE FLAGS (Development-specific)
# ============================================================================
enable_monitoring         = true
enable_auto_scaling       = false  # Disable auto-scaling for predictable costs
enable_container_insights = true
enable_backup             = false  # Disable automated backups for cost savings

# ============================================================================
# COST OPTIMIZATION FLAGS
# ============================================================================
enable_spot_instances      = false  # Can be enabled for further cost savings
enable_scheduled_scaling   = false  # Not needed for development

# ============================================================================
# DEVELOPMENT-SPECIFIC OVERRIDES
# ============================================================================
# Override default environment configuration for development
environment_config = {
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
}