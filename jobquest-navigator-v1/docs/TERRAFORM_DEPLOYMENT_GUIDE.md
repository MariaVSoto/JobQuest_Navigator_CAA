# JobQuest Navigator - Terraform Deployment Guide

## 🏗️ Overview

This guide describes how to use Terraform to deploy the AWS infrastructure for JobQuest Navigator. Terraform provides a more flexible and powerful infrastructure-as-code solution than CloudFormation.

**Advantages of Terraform:**
- 🔄 Multi-cloud platform support
- 📝 Cleaner syntax
- 🛠️ Powerful modular system
- 📊 Detailed execution plan
- 🔍 State management and drift detection

---

## 🛠️ Prerequisites

### Required Tools

1. **Terraform** (>= 1.0)
   ```bash
   # macOS
   brew install terraform
   
   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   
   # Windows
   # Download and install from https://www.terraform.io/downloads
   ```

2. **AWS CLI** (configured)
   ```bash
   aws configure
   aws sts get-caller-identity  # Verify configuration
   ```

3. **jq** (for JSON processing)
   ```bash
   # macOS
   brew install jq
   
   # Linux
   sudo apt install jq
   ```

### AWS Permission Requirements

Ensure your AWS credentials have the following permissions:
- EC2 (VPC, subnets, security groups)
- RDS (instance creation and management)
- S3 (bucket creation and policy)
- IAM (role and policy creation)
- Lambda (function creation)
- API Gateway (API creation)
- CloudWatch (logs and monitoring)
- Secrets Manager (secret management)

---

## 📁 Terraform Project Structure

```
infrastructure/terraform/
├── main.tf                    # Main configuration file
├── variables.tf               # Input variable definitions
├── outputs.tf                 # Output value definitions
├── terraform.tfvars.example   # Example variable values
├── terraform.tfvars           # Actual variable values (to be created)
└── modules/                   # Reusable modules
    ├── vpc/                   # VPC network module
    ├── security/              # Security group module
    ├── s3/                    # S3 storage module
    ├── rds/                   # Database module
    ├── iam/                   # IAM permission module
    └── monitoring/            # Monitoring and alarm module
```

---

## 🚀 Quick Start

### 1. Initialize Configuration

```bash
# Enter Terraform directory
cd prod/infrastructure/terraform

# Create variable configuration file
cp terraform.tfvars.example terraform.tfvars

# Edit configuration file
nano terraform.tfvars
```

### 2. Configure Key Variables

Edit the `terraform.tfvars` file:

```hcl
# Basic configuration
project_name = "jobquest-navigator"
environment  = "production"
aws_region   = "us-east-1"
project_owner = "Your Name"

# Required: alert email
alert_email = "your-email@domain.com"

# Database configuration
db_instance_class = "db.t3.micro"
db_allocated_storage = 20

# Lambda configuration
lambda_memory_size = 512
lambda_timeout = 300

# Cost optimization settings
enable_nat_gateway = false
enable_cloudfront = false
enable_detailed_monitoring = false
```

### 3. Deploy Infrastructure

```bash
# Use deployment script (recommended)
scripts/deploy-terraform.sh --action plan     # View execution plan
scripts/deploy-terraform.sh --action apply    # Deploy infrastructure

# Or run manually
terraform init
terraform plan
terraform apply
```

---

## 📋 Detailed Deployment Steps

### Step 1: Environment Preparation

```bash
# 1. Verify tool installation
terraform version
aws --version
jq --version

# 2. Verify AWS configuration
aws sts get-caller-identity

# 3. Enter Terraform directory
cd prod/infrastructure/terraform
```

### Step 2: Configuration Management

```bash
# Create configuration file
cp terraform.tfvars.example terraform.tfvars

# Key configuration item description
cat >> terraform.tfvars << EOF
# Project basic information
project_name = "jobquest-navigator"
environment  = "production"
project_owner = "JobQuest Team"

# AWS configuration
aws_region = "us-east-1"
alert_email = "admin@yourcompany.com"

# Network configuration
vpc_cidr = "10.0.0.0/16"

# Database configuration
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
enable_rds_encryption = true
rds_backup_retention_period = 7

# Lambda configuration
lambda_memory_size = 512
lambda_timeout = 300

# Cost optimization
enable_nat_gateway = false
enable_s3_endpoint = true
enable_detailed_monitoring = false
log_retention_days = 14
EOF
```

### Step 3: Initialization and Validation

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive

# View execution plan
terraform plan
```

### Step 4: Deploy Infrastructure

```bash
# Method 1: Use deployment script (recommended)
scripts/deploy-terraform.sh --action apply

# Method 2: Manual deployment
terraform apply

# Method 3: Auto-approve deployment
terraform apply -auto-approve
```

### Step 5: Verify Deployment

```bash
# View outputs
terraform output

# View specific output
terraform output database_endpoint
terraform output frontend_website_url

# Verify resource status
terraform show
```

---

## 🛠️ Advanced Configuration

### Workspace Management

Use Terraform workspaces to manage multiple environments:

```bash
# Create development environment
terraform workspace new development
terraform workspace select development
```

# Use different configuration files
cp terraform.tfvars terraform.tfvars.development
# Edit development environment specific configuration

# Deploy to development environment
terraform apply -var-file="terraform.tfvars.development"

# Switch to production environment
terraform workspace select production
terraform apply -var-file="terraform.tfvars"

# List all workspaces
terraform workspace list
```

### State Management

Configure remote state storage (recommended for production):

```hcl
# Add backend configuration in main.tf
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "jobquest-navigator/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### Modular Configuration

Create environment-specific configuration:

```hcl
# environments/production/main.tf
module "jobquest_navigator" {
  source = "../../"
  
  project_name = "jobquest-navigator"
  environment  = "production"
  
  # Production-specific configuration
  db_instance_class = "db.t3.small"
  enable_multi_az = true
  enable_rds_deletion_protection = true
  lambda_memory_size = 1024
  enable_detailed_monitoring = true
}
```

---

## 📊 Outputs and Integration

### Important Output Values

After deployment, Terraform provides the following outputs:

```bash
# Network info
terraform output vpc_id
terraform output private_subnet_ids
terraform output lambda_security_group_id

# Database info
terraform output database_endpoint
terraform output database_name
terraform output database_password_secret_name

# Storage info
terraform output static_bucket_name
terraform output frontend_bucket_name
terraform output frontend_website_url

# Deployment info
terraform output deployment_info
terraform output zappa_configuration
```

### Integration with Zappa

The infrastructure deployed by Terraform can be used directly for Zappa deployment:

```bash
# Get Zappa required configuration
terraform output -json zappa_configuration > zappa_config.json

# Update Zappa configuration
cat zappa_config.json | jq -r '.vpc_config'
```

### Integration with Deployment Scripts

```bash
# Terraform outputs can be used by other scripts
export DATABASE_ENDPOINT=$(terraform output -raw database_endpoint)
export STATIC_BUCKET=$(terraform output -raw static_bucket_name)
export FRONTEND_BUCKET=$(terraform output -raw frontend_bucket_name)

# Run subsequent deployment scripts
../scripts/deploy-backend.sh
../scripts/deploy-frontend.sh
```

---

## 🔍 Monitoring and Maintenance

### State Check

```bash
# Check resource drift
terraform plan -detailed-exitcode

# Refresh state
terraform refresh

# Import existing resources
terraform import aws_s3_bucket.existing bucket-name
```

### Update Infrastructure

```bash
# Update configuration
nano terraform.tfvars

# View change plan
terraform plan

# Apply changes
terraform apply

# For specific resources
terraform apply -target=module.rds
```

### Troubleshooting

```bash
# Debug mode
export TF_LOG=DEBUG
terraform apply

# View state file
terraform show

# Validate configuration
terraform validate

# Check format
terraform fmt -check -diff
```

---

## 💰 Cost Management

### Cost Optimization Configuration

**Development Environment:**
```hcl
# terraform.tfvars.development
db_instance_class = "db.t3.micro"
lambda_memory_size = 256
enable_detailed_monitoring = false
log_retention_days = 7
enable_nat_gateway = false
rds_backup_retention_period = 1
```

**Production Environment:**
```hcl
# terraform.tfvars.production
db_instance_class = "db.t3.small"
lambda_memory_size = 512
enable_detailed_monitoring = true
log_retention_days = 30
enable_multi_az = true
rds_backup_retention_period = 30
```

### Cost Monitoring

```bash
# Use AWS CLI to view costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# View estimated cost
terraform output estimated_monthly_cost
```

---

## 🔒 Security Best Practices

### State File Security

```bash
# Use remote state storage
# Enable state file encryption
# Configure state locking
# Restrict state file access
```

### Variable Management

```bash
# Sensitive variable management
export TF_VAR_db_password="your-secure-password"

# Use AWS Secrets Manager
# Terraform will automatically generate and store database password
```

### Network Security

```hcl
# Principle of least privilege
# Use private subnets
# Configure security group rules
# Enable VPC Flow Logs
```

---

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Terraform Deploy

on:
  push:
    branches: [main]
    paths: ['infrastructure/terraform/**']

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v2
      with:
        terraform_version: 1.6.0
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Terraform Init
      run: terraform init
      working-directory: infrastructure/terraform
    
    - name: Terraform Plan
      run: terraform plan -no-color
      working-directory: infrastructure/terraform
    
    - name: Terraform Apply
      if: github.ref == 'refs/heads/main'
      run: terraform apply -auto-approve -no-color
      working-directory: infrastructure/terraform
```

---

## 📚 Common Command Reference

### Basic Commands

```bash
# Initialize
terraform init

# Validate
terraform validate

# Plan
terraform plan

# Apply
terraform apply

# Destroy
terraform destroy

# Format
terraform fmt

# Show state
terraform show

# List resources
terraform state list

# Output values
terraform output
```

### Workspace Commands

```bash
# List workspaces
terraform workspace list

# Create workspace
terraform workspace new <name>

# Select workspace
terraform workspace select <name>

# Delete workspace
terraform workspace delete <name>
```

### State Management Commands

```bash
# Refresh state
terraform refresh

# Import resource
terraform import <resource_type>.<name> <id>

# Remove resource
terraform state rm <resource>

# Move resource
terraform state mv <source> <destination>
```

---

## 🔄 Terraform vs CloudFormation

| Feature | Terraform | CloudFormation |
|------|-----------|----------------|
| **Syntax** | HCL (concise) | JSON/YAML (verbose) |
| **Multi-cloud support** | ✅ Supported | ❌ AWS only |
| **State management** | ✅ Local/remote state | ✅ AWS managed |
| **Modularity** | ✅ Powerful module system | ⚠️ Nested stacks |
| **Execution plan** | ✅ Detailed change preview | ⚠️ Change sets |
| **Community** | ✅ Large community | ⚠️ AWS ecosystem |
| **Learning curve** | ⚠️ Need to learn HCL | ✅ AWS native |
| **Debugging** | ✅ Detailed logs | ⚠️ Limited debugging |

---

## 📞 Support and Resources

### Official Documentation
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Language](https://www.terraform.io/language)
- [Terraform CLI](https://www.terraform.io/cli)

### Community Resources
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [Terraform Modules Registry](https://registry.terraform.io/)

### Troubleshooting
- See `docs/TROUBLESHOOTING_GUIDE.md`
- Enable debug mode: `export TF_LOG=DEBUG`
- Check AWS CloudTrail logs

---

**Terraform Deployment Guide Version**: v1.0  
**Last Updated**: June 25, 2024  
**Maintenance Team**: JobQuest Navigator Development Team