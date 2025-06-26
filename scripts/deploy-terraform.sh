#!/bin/bash

# JobQuest Navigator - Terraform Deployment Script
# This script deploys AWS infrastructure using Terraform

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
TERRAFORM_DIR="../infrastructure/terraform"
ACTION="plan"
AUTO_APPROVE=false
WORKSPACE="default"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -a, --action ACTION       Terraform action (plan, apply, destroy) [default: plan]"
    echo "  -w, --workspace NAME      Terraform workspace [default: default]"
    echo "  -y, --auto-approve        Auto approve terraform apply/destroy"
    echo "  -d, --dir DIR             Terraform directory [default: $TERRAFORM_DIR]"
    echo "  -h, --help                Show this help message"
    echo
    echo "Examples:"
    echo "  $0 --action plan                    # Show what would be created"
    echo "  $0 --action apply                   # Deploy infrastructure"
    echo "  $0 --action apply --auto-approve    # Deploy without confirmation"
    echo "  $0 --action destroy                 # Destroy infrastructure"
    echo "  $0 --workspace staging --action apply  # Deploy to staging workspace"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -w|--workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        -y|--auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        -d|--dir)
            TERRAFORM_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate action
case $ACTION in
    plan|apply|destroy|init|validate|fmt|show|output)
        ;;
    *)
        print_error "Invalid action: $ACTION"
        echo "Valid actions: plan, apply, destroy, init, validate, fmt, show, output"
        exit 1
        ;;
esac

print_status "Starting Terraform deployment for JobQuest Navigator..."
print_status "Action: $ACTION"
print_status "Workspace: $WORKSPACE"
print_status "Directory: $TERRAFORM_DIR"

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform not found. Please install Terraform first."
    echo "Visit: https://www.terraform.io/downloads"
    exit 1
fi

# Check Terraform version
TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version' 2>/dev/null || terraform version | head -1 | cut -d' ' -f2 | cut -d'v' -f2)
print_status "Terraform version: $TERRAFORM_VERSION"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS account info
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)
print_status "AWS Account: $AWS_ACCOUNT_ID"
print_status "AWS Region: $AWS_REGION"

# Check if terraform directory exists
if [ ! -d "$TERRAFORM_DIR" ]; then
    print_error "Terraform directory not found: $TERRAFORM_DIR"
    exit 1
fi

# Change to terraform directory
cd "$TERRAFORM_DIR"

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    print_warning "terraform.tfvars not found. Creating from example..."
    
    if [ -f "terraform.tfvars.example" ]; then
        cp terraform.tfvars.example terraform.tfvars
        print_warning "Please edit terraform.tfvars with your configuration before proceeding."
        
        # Check if alert_email is configured
        if grep -q "your-email@domain.com" terraform.tfvars; then
            print_error "Please update the alert_email in terraform.tfvars before proceeding."
            exit 1
        fi
    else
        print_error "terraform.tfvars.example not found. Cannot create terraform.tfvars."
        exit 1
    fi
fi

# Initialize Terraform if needed
if [ ! -d ".terraform" ] || [ "$ACTION" = "init" ]; then
    print_status "Initializing Terraform..."
    terraform init
fi

# Create or select workspace
if [ "$WORKSPACE" != "default" ]; then
    print_status "Managing workspace: $WORKSPACE"
    
    # Check if workspace exists
    if terraform workspace list | grep -q "$WORKSPACE"; then
        print_status "Selecting existing workspace: $WORKSPACE"
        terraform workspace select "$WORKSPACE"
    else
        print_status "Creating new workspace: $WORKSPACE"
        terraform workspace new "$WORKSPACE"
    fi
else
    terraform workspace select default
fi

# Format Terraform files
if [ "$ACTION" = "fmt" ]; then
    print_status "Formatting Terraform files..."
    terraform fmt -recursive
    print_success "Terraform files formatted"
    exit 0
fi

# Validate Terraform configuration
if [ "$ACTION" = "validate" ]; then
    print_status "Validating Terraform configuration..."
    terraform validate
    print_success "Terraform configuration is valid"
    exit 0
fi

# Show current state
if [ "$ACTION" = "show" ]; then
    print_status "Showing current Terraform state..."
    terraform show
    exit 0
fi

# Show outputs
if [ "$ACTION" = "output" ]; then
    print_status "Showing Terraform outputs..."
    terraform output
    exit 0
fi

# Validate configuration before proceeding
print_status "Validating Terraform configuration..."
if ! terraform validate; then
    print_error "Terraform configuration validation failed"
    exit 1
fi

# Run terraform plan
if [ "$ACTION" = "plan" ] || [ "$ACTION" = "apply" ]; then
    print_status "Creating Terraform execution plan..."
    
    # Create plan file
    PLAN_FILE="tfplan-$(date +%Y%m%d-%H%M%S)"
    
    if terraform plan -out="$PLAN_FILE"; then
        print_success "Terraform plan created successfully"
        
        if [ "$ACTION" = "plan" ]; then
            # Show plan summary
            print_status "Plan file created: $PLAN_FILE"
            echo
            echo "To apply this plan, run:"
            echo "  terraform apply \"$PLAN_FILE\""
            echo
            echo "Or use this script:"
            echo "  $0 --action apply"
            exit 0
        fi
    else
        print_error "Terraform plan failed"
        exit 1
    fi
fi

# Apply or destroy infrastructure
if [ "$ACTION" = "apply" ] || [ "$ACTION" = "destroy" ]; then
    
    # Show cost estimation warning
    if [ "$ACTION" = "apply" ]; then
        echo
        print_warning "=== COST WARNING ==="
        echo "This will create AWS resources that may incur charges:"
        echo "  - RDS MySQL instance (~\$15/month)"
        echo "  - Lambda functions (~\$2/month for 1M requests)"
        echo "  - S3 storage (~\$0.12/month for 5GB)"
        echo "  - Data transfer (~\$0.90/month for 10GB)"
        echo "  - Total estimated: ~\$18-25/month"
        echo
    fi
    
    # Show destruction warning
    if [ "$ACTION" = "destroy" ]; then
        echo
        print_error "=== DESTRUCTION WARNING ==="
        echo "This will PERMANENTLY DELETE all AWS resources including:"
        echo "  - Database and all data"
        echo "  - S3 buckets and files"
        echo "  - Lambda functions"
        echo "  - VPC and networking"
        echo
        print_error "This action CANNOT be undone!"
        echo
    fi
    
    # Confirmation prompt (unless auto-approve is set)
    if [ "$AUTO_APPROVE" = false ]; then
        if [ "$ACTION" = "apply" ]; then
            read -p "Do you want to proceed with creating these resources? (yes/no): " confirm
        else
            read -p "Are you absolutely sure you want to destroy all resources? Type 'yes' to confirm: " confirm
        fi
        
        if [ "$confirm" != "yes" ]; then
            print_status "Operation cancelled by user"
            exit 0
        fi
    fi
    
    # Execute the action
    print_status "Executing terraform $ACTION..."
    
    if [ "$ACTION" = "apply" ]; then
        if [ "$AUTO_APPROVE" = true ]; then
            terraform apply -auto-approve
        elif [ -f "$PLAN_FILE" ]; then
            terraform apply "$PLAN_FILE"
        else
            terraform apply
        fi
    else
        if [ "$AUTO_APPROVE" = true ]; then
            terraform destroy -auto-approve
        else
            terraform destroy
        fi
    fi
    
    # Check exit status
    if [ $? -eq 0 ]; then
        print_success "Terraform $ACTION completed successfully!"
        
        if [ "$ACTION" = "apply" ]; then
            echo
            print_status "=== DEPLOYMENT SUMMARY ==="
            
            # Show important outputs
            if terraform output database_endpoint &>/dev/null; then
                echo "Database Endpoint: $(terraform output -raw database_endpoint)"
            fi
            
            if terraform output frontend_website_url &>/dev/null; then
                echo "Frontend URL: $(terraform output -raw frontend_website_url)"
            fi
            
            if terraform output api_gateway_url &>/dev/null; then
                API_URL=$(terraform output -raw api_gateway_url)
                if [ "$API_URL" != "null" ]; then
                    echo "API Gateway URL: $API_URL"
                fi
            fi
            
            echo
            print_status "=== NEXT STEPS ==="
            echo "1. Wait for RDS instance to be fully available (5-10 minutes)"
            echo "2. Deploy backend: scripts/deploy-backend.sh"
            echo "3. Deploy frontend: scripts/deploy-frontend.sh"
            echo "4. Verify deployment: scripts/verify-deployment.sh"
            echo
            echo "=== IMPORTANT INFORMATION ==="
            echo "Database password is stored in AWS Secrets Manager:"
            SECRET_NAME=$(terraform output -raw database_password_secret_name)
            echo "Secret name: $SECRET_NAME"
            echo
            echo "To retrieve database password:"
            echo "aws secretsmanager get-secret-value --secret-id $SECRET_NAME --query SecretString --output text"
            echo
            echo "=== TERRAFORM OUTPUTS ==="
            echo "View all outputs: terraform output"
            echo "View specific output: terraform output <output_name>"
            echo "View outputs in JSON: terraform output -json"
        fi
        
    else
        print_error "Terraform $ACTION failed!"
        exit 1
    fi
fi

# Clean up plan files older than 7 days
find . -name "tfplan-*" -type f -mtime +7 -delete 2>/dev/null || true

print_success "Terraform deployment script completed!"

# Show workspace info
echo
print_status "Current workspace: $(terraform workspace show)"
print_status "Terraform state: $(pwd)/terraform.tfstate$([ "$(terraform workspace show)" != "default" ] && echo ".d/$(terraform workspace show)")"

# Show useful commands
echo
echo "=== USEFUL COMMANDS ==="
echo "View plan: terraform plan"
echo "Apply changes: terraform apply"
echo "Show current state: terraform show"
echo "List outputs: terraform output"
echo "Switch workspace: terraform workspace select <name>"
echo "Destroy infrastructure: terraform destroy"
echo
echo "=== FILES AND DIRECTORIES ==="
echo "Configuration: $(pwd)"
echo "State files: $(pwd)/.terraform/"
echo "Plan files: $(pwd)/tfplan-*"