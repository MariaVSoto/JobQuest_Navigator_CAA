# Terraform Backend Configuration for JobQuest Navigator v2
# S3 backend with DynamoDB state locking

terraform {
  backend "s3" {
    # These values will be provided via terraform init -backend-config
    # or via backend config files
    
    # bucket         = "jobquest-navigator-v2-terraform-state"
    # key            = "environments/${var.environment}/terraform.tfstate"
    # region         = "us-east-1"
    # encrypt        = true
    # dynamodb_table = "jobquest-navigator-v2-terraform-locks"
    
    # Workspace-specific state files
    # workspace_key_prefix = "environments"
  }
}

# Backend configuration files for different environments
# Use with: terraform init -backend-config=backend-configs/development.hcl