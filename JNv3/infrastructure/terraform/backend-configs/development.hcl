# Development Environment Backend Configuration
bucket         = "jobquest-navigator-v2-terraform-state"
key            = "environments/development/terraform.tfstate"
region         = "us-east-1"
encrypt        = true
dynamodb_table = "jobquest-navigator-v2-terraform-locks"