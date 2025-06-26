#!/bin/bash

# JobQuest Navigator - Infrastructure Deployment Script
# This script deploys AWS infrastructure using CloudFormation

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
STACK_NAME="jobquest-navigator-infra"
TEMPLATE_FILE="../infrastructure/cloudformation-template.yaml"
PROJECT_NAME="jobquest-navigator"
ENVIRONMENT="production"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -s, --stack-name NAME     CloudFormation stack name (default: $STACK_NAME)"
    echo "  -p, --project-name NAME   Project name (default: $PROJECT_NAME)"
    echo "  -e, --environment ENV     Environment (default: $ENVIRONMENT)"
    echo "  -d, --delete             Delete the stack instead of creating/updating"
    echo "  -h, --help               Show this help message"
    echo
    echo "Required environment variables:"
    echo "  DATABASE_PASSWORD        Password for RDS database"
    echo "  ALERT_EMAIL             Email address for CloudWatch alarms"
}

# Parse command line arguments
DELETE_STACK=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        -p|--project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -d|--delete)
            DELETE_STACK=true
            shift
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

print_status "Starting JobQuest Navigator Infrastructure Deployment..."

# Check prerequisites
print_status "Checking prerequisites..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if CloudFormation template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    print_error "CloudFormation template not found: $TEMPLATE_FILE"
    exit 1
fi

# Load environment variables
if [ -f "../configs/environment.env" ]; then
    print_status "Loading environment variables..."
    export $(cat ../configs/environment.env | grep -v '^#' | xargs)
else
    print_warning "Environment file not found. Please set environment variables manually."
fi

# Handle stack deletion
if [ "$DELETE_STACK" = true ]; then
    print_warning "You are about to DELETE the CloudFormation stack: $STACK_NAME"
    read -p "Are you sure? This will destroy all resources. (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_status "Deletion cancelled."
        exit 0
    fi
    
    print_status "Deleting CloudFormation stack: $STACK_NAME"
    aws cloudformation delete-stack --stack-name "$STACK_NAME"
    
    print_status "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"
    
    print_success "Stack deleted successfully!"
    exit 0
fi

# Validate required parameters
if [ -z "$DATABASE_PASSWORD" ]; then
    print_error "DATABASE_PASSWORD environment variable is required."
    echo "Please set DATABASE_PASSWORD or add it to configs/environment.env"
    exit 1
fi

if [ -z "$ALERT_EMAIL" ]; then
    print_error "ALERT_EMAIL environment variable is required."
    echo "Please set ALERT_EMAIL or add it to configs/environment.env"
    exit 1
fi

# Validate CloudFormation template
print_status "Validating CloudFormation template..."
if aws cloudformation validate-template --template-body file://"$TEMPLATE_FILE" > /dev/null; then
    print_success "Template validation passed"
else
    print_error "Template validation failed"
    exit 1
fi

# Check if stack already exists
print_status "Checking if stack exists..."
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" > /dev/null 2>&1; then
    STACK_EXISTS=true
    print_status "Stack exists. Will update existing stack."
else
    STACK_EXISTS=false
    print_status "Stack does not exist. Will create new stack."
fi

# Prepare parameters
PARAMETERS="ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME"
PARAMETERS="$PARAMETERS ParameterKey=Environment,ParameterValue=$ENVIRONMENT"
PARAMETERS="$PARAMETERS ParameterKey=DatabasePassword,ParameterValue=$DATABASE_PASSWORD"
PARAMETERS="$PARAMETERS ParameterKey=AlertEmail,ParameterValue=$ALERT_EMAIL"

# Deploy or update stack
if [ "$STACK_EXISTS" = true ]; then
    print_status "Updating CloudFormation stack: $STACK_NAME"
    
    # Create change set first to preview changes
    CHANGE_SET_NAME="update-$(date +%Y%m%d-%H%M%S)"
    
    aws cloudformation create-change-set \
      --stack-name "$STACK_NAME" \
      --change-set-name "$CHANGE_SET_NAME" \
      --template-body file://"$TEMPLATE_FILE" \
      --parameters $PARAMETERS \
      --capabilities CAPABILITY_IAM \
      --description "Update JobQuest Navigator infrastructure"
    
    # Wait for change set to be created
    print_status "Waiting for change set to be created..."
    aws cloudformation wait change-set-create-complete \
      --stack-name "$STACK_NAME" \
      --change-set-name "$CHANGE_SET_NAME"
    
    # Describe changes
    print_status "Proposed changes:"
    aws cloudformation describe-change-set \
      --stack-name "$STACK_NAME" \
      --change-set-name "$CHANGE_SET_NAME" \
      --query 'Changes[].{Action:Action,Resource:ResourceChange.LogicalResourceId,Type:ResourceChange.ResourceType}' \
      --output table
    
    # Confirm execution
    read -p "Do you want to execute these changes? (y/N): " execute_changes
    if [ "$execute_changes" != "y" ] && [ "$execute_changes" != "Y" ]; then
        print_status "Update cancelled. Deleting change set."
        aws cloudformation delete-change-set \
          --stack-name "$STACK_NAME" \
          --change-set-name "$CHANGE_SET_NAME"
        exit 0
    fi
    
    # Execute change set
    aws cloudformation execute-change-set \
      --stack-name "$STACK_NAME" \
      --change-set-name "$CHANGE_SET_NAME"
    
    print_status "Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME"
    
else
    print_status "Creating CloudFormation stack: $STACK_NAME"
    
    aws cloudformation create-stack \
      --stack-name "$STACK_NAME" \
      --template-body file://"$TEMPLATE_FILE" \
      --parameters $PARAMETERS \
      --capabilities CAPABILITY_IAM \
      --on-failure ROLLBACK \
      --tags Key=Project,Value="JobQuest Navigator" \
             Key=Environment,Value="$ENVIRONMENT" \
             Key=Purpose,Value="Graduation Project"
    
    print_status "Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME"
fi

# Check stack status
STACK_STATUS=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].StackStatus' \
  --output text)

if [[ "$STACK_STATUS" == *"COMPLETE"* ]]; then
    print_success "Stack deployment completed successfully!"
else
    print_error "Stack deployment failed with status: $STACK_STATUS"
    exit 1
fi

# Get stack outputs
print_status "Retrieving stack outputs..."
OUTPUTS=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs')

if [ "$OUTPUTS" != "null" ]; then
    print_success "Stack outputs:"
    echo "$OUTPUTS" | jq -r '.[] | "\(.OutputKey): \(.OutputValue)"'
    
    # Save important outputs to files for other scripts
    mkdir -p ../configs/outputs
    
    # Save database endpoint
    DB_ENDPOINT=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="DatabaseEndpoint") | .OutputValue')
    if [ "$DB_ENDPOINT" != "null" ]; then
        echo "$DB_ENDPOINT" > ../configs/outputs/database-endpoint.txt
        print_status "Database endpoint saved to configs/outputs/database-endpoint.txt"
    fi
    
    # Save S3 bucket names
    STATIC_BUCKET=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="StaticBucketName") | .OutputValue')
    if [ "$STATIC_BUCKET" != "null" ]; then
        echo "$STATIC_BUCKET" > ../configs/outputs/static-bucket-name.txt
        print_status "Static bucket name saved to configs/outputs/static-bucket-name.txt"
    fi
    
    FRONTEND_BUCKET=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="FrontendBucketName") | .OutputValue')
    if [ "$FRONTEND_BUCKET" != "null" ]; then
        echo "$FRONTEND_BUCKET" > ../configs/outputs/frontend-bucket-name.txt
        print_status "Frontend bucket name saved to configs/outputs/frontend-bucket-name.txt"
    fi
    
    # Save VPC and security group IDs
    VPC_ID=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="VPCId") | .OutputValue')
    if [ "$VPC_ID" != "null" ]; then
        echo "$VPC_ID" > ../configs/outputs/vpc-id.txt
        print_status "VPC ID saved to configs/outputs/vpc-id.txt"
    fi
    
    LAMBDA_SG_ID=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="LambdaSecurityGroupId") | .OutputValue')
    if [ "$LAMBDA_SG_ID" != "null" ]; then
        echo "$LAMBDA_SG_ID" > ../configs/outputs/lambda-sg-id.txt
        print_status "Lambda security group ID saved to configs/outputs/lambda-sg-id.txt"
    fi
    
else
    print_warning "No outputs found in stack"
fi

# Show deployment summary
echo
echo "=== Infrastructure Deployment Summary ==="
echo "Stack Name: $STACK_NAME"
echo "Project Name: $PROJECT_NAME"
echo "Environment: $ENVIRONMENT"
echo "Stack Status: $STACK_STATUS"
echo "Region: $(aws configure get region)"
echo

# Show next steps
echo "=== Next Steps ==="
echo "1. Wait for RDS instance to be fully available (may take 5-10 minutes)"
echo "2. Deploy backend using: scripts/deploy-backend.sh"
echo "3. Deploy frontend using: scripts/deploy-frontend.sh"
echo "4. Run verification tests using: scripts/verify-deployment.sh"
echo

# Show useful commands
echo "=== Useful Commands ==="
echo "View stack events: aws cloudformation describe-stack-events --stack-name $STACK_NAME"
echo "View stack resources: aws cloudformation describe-stack-resources --stack-name $STACK_NAME"
echo "Delete stack: $0 --delete"
echo "Update stack: $0 (will create change set for review)"
echo

print_success "Infrastructure deployment script completed!"

# Optional: Verify RDS instance is available
if [ "$DB_ENDPOINT" != "null" ] && [ "$DB_ENDPOINT" != "" ]; then
    print_status "Waiting for RDS instance to be available..."
    DB_INSTANCE_ID=$(echo "$PROJECT_NAME-db")
    
    if aws rds wait db-instance-available --db-instance-identifier "$DB_INSTANCE_ID" --cli-read-timeout 600; then
        print_success "RDS instance is now available"
    else
        print_warning "Timeout waiting for RDS instance. Please check manually."
    fi
fi