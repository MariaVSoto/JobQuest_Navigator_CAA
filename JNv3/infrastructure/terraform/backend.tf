# Terraform Backend Configuration for JobQuest Navigator v3
# S3 backend without state locking (simplified for development)

terraform {
  backend "s3" {
    bucket  = "caa900resume"
    key     = "jobquest-navigator-v3/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true

    # Workspace-specific state files
    workspace_key_prefix = "environments"
  }
}

# Backend configuration files for different environments
# Use with: terraform init -backend-config=backend-configs/development.hcl