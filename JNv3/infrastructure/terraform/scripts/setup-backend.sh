#!/bin/bash
# JobQuest Navigator v2 - Terraform Backend Setup
# Creates S3 bucket and DynamoDB table for Terraform state management

set -e

# Configuration
PROJECT_NAME="jobquest-navigator-v2"
AWS_REGION="us-east-1"
BUCKET_NAME="${PROJECT_NAME}-terraform-state"
DYNAMODB_TABLE="${PROJECT_NAME}-terraform-locks"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS CLI is not configured or you don't have permissions."
        exit 1
    fi
    
    log_success "AWS CLI is configured and working"
}

create_s3_bucket() {
    log_info "Creating S3 bucket: $BUCKET_NAME"
    
    # Check if bucket already exists
    if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
        log_warning "S3 bucket $BUCKET_NAME already exists"
        return 0
    fi
    
    # Create bucket
    if [ "$AWS_REGION" = "us-east-1" ]; then
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$AWS_REGION"
    else
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$AWS_REGION" \
            --create-bucket-configuration LocationConstraint="$AWS_REGION"
    fi
    
    # Enable versioning
    aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled
    
    # Enable server-side encryption
    aws s3api put-bucket-encryption --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    },
                    "BucketKeyEnabled": true
                }
            ]
        }'
    
    # Block public access
    aws s3api put-public-access-block --bucket "$BUCKET_NAME" \
        --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
    
    # Add lifecycle policy to manage costs
    aws s3api put-bucket-lifecycle-configuration --bucket "$BUCKET_NAME" \
        --lifecycle-configuration '{
            "Rules": [
                {
                    "ID": "StateFileManagement",
                    "Status": "Enabled",
                    "Filter": {"Prefix": ""},
                    "NoncurrentVersionTransitions": [
                        {
                            "NoncurrentDays": 30,
                            "StorageClass": "STANDARD_IA"
                        },
                        {
                            "NoncurrentDays": 90,
                            "StorageClass": "GLACIER"
                        }
                    ],
                    "NoncurrentVersionExpiration": {
                        "NoncurrentDays": 365
                    }
                }
            ]
        }'
    
    log_success "S3 bucket $BUCKET_NAME created and configured"
}

create_dynamodb_table() {
    log_info "Creating DynamoDB table: $DYNAMODB_TABLE"
    
    # Check if table already exists
    if aws dynamodb describe-table --table-name "$DYNAMODB_TABLE" &> /dev/null; then
        log_warning "DynamoDB table $DYNAMODB_TABLE already exists"
        return 0
    fi
    
    # Create table
    aws dynamodb create-table \
        --table-name "$DYNAMODB_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --tags Key=Project,Value="$PROJECT_NAME" Key=Purpose,Value="Terraform State Locking"
    
    # Wait for table to be active
    log_info "Waiting for DynamoDB table to be active..."
    aws dynamodb wait table-exists --table-name "$DYNAMODB_TABLE"
    
    log_success "DynamoDB table $DYNAMODB_TABLE created"
}

setup_backend_configs() {
    log_info "Backend infrastructure is ready!"
    echo ""
    echo "To initialize Terraform with the backend, run:"
    echo ""
    echo "# For development:"
    echo "terraform init -backend-config=backend-configs/development.hcl"
    echo ""
    echo "# For staging:"
    echo "terraform init -backend-config=backend-configs/staging.hcl"
    echo ""
    echo "# For production:"
    echo "terraform init -backend-config=backend-configs/production.hcl"
    echo ""
    
    log_success "Backend setup completed successfully!"
}

# Main execution
main() {
    log_info "Setting up Terraform backend for $PROJECT_NAME"
    echo ""
    
    # Verify prerequisites
    check_aws_cli
    
    # Create infrastructure
    create_s3_bucket
    create_dynamodb_table
    
    # Provide next steps
    setup_backend_configs
}

# Check if running with --help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "JobQuest Navigator v2 - Terraform Backend Setup"
    echo ""
    echo "This script creates the S3 bucket and DynamoDB table required for"
    echo "Terraform remote state management."
    echo ""
    echo "Prerequisites:"
    echo "  - AWS CLI installed and configured"
    echo "  - Appropriate AWS permissions for S3 and DynamoDB"
    echo ""
    echo "Usage:"
    echo "  $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo ""
    exit 0
fi

# Run main function
main "$@"