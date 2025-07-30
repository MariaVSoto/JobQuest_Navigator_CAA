# JobQuest Navigator v2 - Staging Environment Configuration
# Balanced configuration between development and production

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================
project_name = "jobquest-navigator-v2"
environment  = "staging"
aws_region   = "us-east-1"

# ============================================================================
# NETWORKING CONFIGURATION
# ============================================================================
vpc_cidr = "10.1.0.0/16"  # Different CIDR from production
az_count = 2  # Use 2 AZs for staging

public_subnet_cidrs   = ["10.1.1.0/24", "10.1.2.0/24"]
private_subnet_cidrs  = ["10.1.10.0/24", "10.1.20.0/24"]
database_subnet_cidrs = ["10.1.30.0/24", "10.1.40.0/24"]

# Staging: Single NAT gateway for cost optimization
enable_nat_gateway = true
single_nat_gateway = true

# ============================================================================
# DATABASE CONFIGURATION (Staging-optimized)
# ============================================================================
postgres_version        = "15.4"
rds_instance_class     = "db.t3.small"  # Mid-tier for staging
rds_allocated_storage  = 50
rds_max_allocated_storage = 200

database_name    = "jobquest_navigator_v2_staging"
database_username = "jobquest_staging_user"

# Staging backup strategy
backup_retention_period = 7   # 7 days backup retention
backup_window          = "03:00-04:00"
maintenance_window     = "sun:04:00-sun:05:00"

# ============================================================================
# CACHE CONFIGURATION (Staging-optimized)
# ============================================================================
redis_version         = "7.0"
redis_node_type      = "cache.t3.small"  # Mid-tier for staging
redis_num_nodes      = 1
redis_parameter_group = "default.redis7"

# ============================================================================
# CONTAINER CONFIGURATION (Staging scale)
# ============================================================================
# Backend containers - Production-like but smaller scale
backend_cpu           = 512   # 0.5 vCPU
backend_memory        = 1024  # 1GB RAM
backend_desired_count = 2     # 2 instances for load testing

# Frontend containers
frontend_cpu           = 256   # 0.25 vCPU
frontend_memory        = 512   # 512MB RAM
frontend_desired_count = 2     # 2 instances for redundancy

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================
# Staging Cognito configuration
cognito_user_pool_id = "us-east-1_bISZREFys"  # Staging pool
cognito_client_id    = "5iui547bod6sqgsi1a4heidpep"  # Staging client

# Staging CORS - Allow development and staging domains
cors_origins = "http://localhost:3000,http://localhost:3001,https://staging.jobquest-navigator.com,https://staging-api.jobquest-navigator.com"

# SSL certificate for staging HTTPS
ssl_certificate_arn = ""  # Set via environment variable or terraform apply

# S3 bucket configuration - use generated name for staging
s3_bucket_name = ""  # Empty means use generated name

# ============================================================================
# FEATURE FLAGS (Staging-enabled)
# ============================================================================
enable_monitoring         = true
enable_auto_scaling       = true   # Test auto-scaling in staging
enable_container_insights = true
enable_backup             = true   # Enable backup for data protection

# ============================================================================
# COST OPTIMIZATION FLAGS (Staging balance)
# ============================================================================
enable_spot_instances      = false  # Use on-demand for stability
enable_scheduled_scaling   = false  # Keep consistent for testing

# ============================================================================
# STAGING-SPECIFIC OVERRIDES
# ============================================================================
environment_config = {
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
    multi_az             = false  # Single AZ for cost optimization
  }
}