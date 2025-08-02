# JobQuest Navigator v2 - Production Environment Configuration
# Optimized for reliability, performance, and security

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================
project_name = "jobquest-navigator-v2"
environment  = "production"
aws_region   = "us-east-1"

# ============================================================================
# NETWORKING CONFIGURATION
# ============================================================================
vpc_cidr = "10.0.0.0/16"
az_count = 3  # Use 3 AZs for high availability

public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs  = ["10.0.10.0/24", "10.0.20.0/24", "10.0.30.0/24"]
database_subnet_cidrs = ["10.0.40.0/24", "10.0.50.0/24", "10.0.60.0/24"]

# High availability: Multiple NAT gateways
enable_nat_gateway = true
single_nat_gateway = false  # Multiple NAT gateways for redundancy

# ============================================================================
# DATABASE CONFIGURATION (Production-grade)
# ============================================================================
postgres_version        = "15.4"
rds_instance_class     = "db.t3.medium"  # More powerful for production
rds_allocated_storage  = 100
rds_max_allocated_storage = 1000

database_name    = "jobquest_navigator_v2_prod"
database_username = "jobquest_prod_user"

# Production backup strategy
backup_retention_period = 30  # 30 days backup retention
backup_window          = "03:00-04:00"
maintenance_window     = "sun:04:00-sun:05:00"

# ============================================================================
# CACHE CONFIGURATION (Production-grade)
# ============================================================================
redis_version         = "7.0"
redis_node_type      = "cache.t3.medium"  # More powerful for production
redis_num_nodes      = 2  # Redundancy
redis_parameter_group = "default.redis7"

# ============================================================================
# CONTAINER CONFIGURATION (Production scale)
# ============================================================================
# Backend containers - Higher resources and count
backend_cpu           = 1024  # 1 vCPU
backend_memory        = 2048  # 2GB RAM
backend_desired_count = 3     # 3 instances for load distribution

# Frontend containers - Optimized for serving static content
frontend_cpu           = 512   # 0.5 vCPU
frontend_memory        = 1024  # 1GB RAM
frontend_desired_count = 3     # 3 instances for high availability

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================
# Production Cognito configuration (to be provided during deployment)
cognito_user_pool_id = ""  # Set via environment variable or terraform apply
cognito_client_id    = ""  # Set via environment variable or terraform apply

# Production CORS - Restrict to specific domains
cors_origins = "https://jobquest-navigator.com,https://www.jobquest-navigator.com,https://api.jobquest-navigator.com"

# SSL certificate required for production HTTPS
ssl_certificate_arn = ""  # Set via environment variable or terraform apply

# S3 bucket configuration
s3_bucket_name = "caa900resume"  # Manually created S3 bucket

# ============================================================================
# FEATURE FLAGS (Production-enabled)
# ============================================================================
enable_monitoring         = true
enable_auto_scaling       = true   # Enable auto-scaling for production
enable_container_insights = true
enable_backup             = true   # Full backup strategy

# ============================================================================
# COST OPTIMIZATION FLAGS (Production balance)
# ============================================================================
enable_spot_instances      = false  # Use on-demand for reliability
enable_scheduled_scaling   = true   # Scale down during off-hours

# ============================================================================
# PRODUCTION-SPECIFIC OVERRIDES
# ============================================================================
environment_config = {
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
    multi_az             = true  # Multi-AZ for high availability
  }
}