#!/bin/bash
# JobQuest Navigator v2 - Complete AWS Deployment Script
# Orchestrates the full deployment process

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

# Default values
ENVIRONMENT="development"
SKIP_BUILD=false
SKIP_TERRAFORM=false
SKIP_DEPLOY=false
FORCE_APPLY=false
AUTO_APPROVE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

show_usage() {
    cat << EOF
JobQuest Navigator v2 - AWS Deployment Script

Usage: $0 [OPTIONS] ENVIRONMENT

ENVIRONMENT:
    development     Deploy to development environment
    staging         Deploy to staging environment  
    production      Deploy to production environment

OPTIONS:
    -h, --help              Show this help message
    --skip-build            Skip Docker image build step
    --skip-terraform        Skip Terraform infrastructure deployment
    --skip-deploy           Skip application deployment
    --force-apply           Force Terraform apply even if plan shows no changes
    --auto-approve          Auto-approve Terraform apply (use with caution)

EXAMPLES:
    $0 development                    # Full deployment to development
    $0 --skip-build staging          # Deploy to staging without rebuilding images
    $0 --auto-approve production     # Deploy to production with auto-approval

PREREQUISITES:
    - AWS CLI configured with appropriate permissions
    - Docker installed and running
    - Terraform installed
    - Backend infrastructure created (run terraform/scripts/setup-backend.sh)

EOF
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS CLI is not configured or lacks permissions"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f "$TERRAFORM_DIR/environments/$ENVIRONMENT.tfvars" ]; then
        log_error "Environment file not found: $TERRAFORM_DIR/environments/$ENVIRONMENT.tfvars"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

build_and_push_images() {
    if [ "$SKIP_BUILD" = true ]; then
        log_info "Skipping Docker build step"
        return 0
    fi
    
    log_info "Building and pushing Docker images..."
    
    # Get AWS account ID and region
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region || echo "us-east-1")
    ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Login to ECR
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$ECR_REGISTRY"
    
    # Build and push backend image
    log_info "Building backend image..."
    cd "$PROJECT_ROOT/backend-fastapi-graphql"
    
    docker build -t "jobquest-backend:latest" --target ecs-production .
    docker tag "jobquest-backend:latest" "$ECR_REGISTRY/jobquest-backend:latest"
    docker tag "jobquest-backend:latest" "$ECR_REGISTRY/jobquest-backend:$(git rev-parse --short HEAD)"
    
    docker push "$ECR_REGISTRY/jobquest-backend:latest"
    docker push "$ECR_REGISTRY/jobquest-backend:$(git rev-parse --short HEAD)"
    
    # Build and push frontend image
    log_info "Building frontend image..."
    cd "$PROJECT_ROOT/frontend-react-minimal"
    
    # Build React app first
    npm run build
    
    docker build -t "jobquest-frontend:latest" .
    docker tag "jobquest-frontend:latest" "$ECR_REGISTRY/jobquest-frontend:latest"
    docker tag "jobquest-frontend:latest" "$ECR_REGISTRY/jobquest-frontend:$(git rev-parse --short HEAD)"
    
    docker push "$ECR_REGISTRY/jobquest-frontend:latest"
    docker push "$ECR_REGISTRY/jobquest-frontend:$(git rev-parse --short HEAD)"
    
    cd "$PROJECT_ROOT"
    log_success "Docker images built and pushed successfully"
}

deploy_infrastructure() {
    if [ "$SKIP_TERRAFORM" = true ]; then
        log_info "Skipping Terraform infrastructure deployment"
        return 0
    fi
    
    log_info "Deploying infrastructure with Terraform..."
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform with environment-specific backend
    log_info "Initializing Terraform backend for $ENVIRONMENT..."
    terraform init -backend-config="backend-configs/$ENVIRONMENT.hcl" -reconfigure
    
    # Validate configuration
    log_info "Validating Terraform configuration..."
    terraform validate
    
    # Plan deployment
    log_info "Creating Terraform plan..."
    terraform plan -var-file="environments/$ENVIRONMENT.tfvars" -out="$ENVIRONMENT.tfplan"
    
    # Apply infrastructure changes
    if [ "$AUTO_APPROVE" = true ]; then
        log_warning "Auto-approving Terraform apply..."
        terraform apply -auto-approve "$ENVIRONMENT.tfplan"
    else
        log_info "Applying Terraform plan..."
        terraform apply "$ENVIRONMENT.tfplan"
    fi
    
    # Get outputs
    log_info "Getting Terraform outputs..."
    terraform output -json > "$ENVIRONMENT-outputs.json"
    
    cd "$PROJECT_ROOT"
    log_success "Infrastructure deployed successfully"
}

deploy_application() {
    if [ "$SKIP_DEPLOY" = true ]; then
        log_info "Skipping application deployment"
        return 0
    fi
    
    log_info "Deploying application services..."
    
    # Get cluster name from Terraform outputs
    CLUSTER_NAME=$(cd "$TERRAFORM_DIR" && terraform output -raw ecs_cluster_name 2>/dev/null || echo "jobquest-navigator-v2-$ENVIRONMENT")
    BACKEND_SERVICE_NAME=$(cd "$TERRAFORM_DIR" && terraform output -raw backend_service_name 2>/dev/null || echo "jobquest-navigator-v2-$ENVIRONMENT-backend")
    
    # Force new deployment to pick up new images
    log_info "Updating ECS backend service..."
    aws ecs update-service \
        --cluster "$CLUSTER_NAME" \
        --service "$BACKEND_SERVICE_NAME" \
        --force-new-deployment \
        --no-cli-pager
    
    # Wait for deployment to stabilize
    log_info "Waiting for deployment to stabilize..."
    aws ecs wait services-stable \
        --cluster "$CLUSTER_NAME" \
        --services "$BACKEND_SERVICE_NAME"
    
    log_success "Application deployed successfully"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Get ALB DNS name from Terraform outputs
    ALB_DNS_NAME=$(cd "$TERRAFORM_DIR" && terraform output -raw alb_dns_name 2>/dev/null || echo "")
    
    if [ -n "$ALB_DNS_NAME" ]; then
        # Test health endpoint
        log_info "Testing health endpoint..."
        if curl -f -s "http://$ALB_DNS_NAME/health" > /dev/null; then
            log_success "Health check passed"
        else
            log_warning "Health check failed - application may still be starting"
        fi
        
        # Test GraphQL endpoint
        log_info "Testing GraphQL endpoint..."
        GRAPHQL_RESPONSE=$(curl -s -X POST \
            -H "Content-Type: application/json" \
            -d '{"query":"query { hello }"}' \
            "http://$ALB_DNS_NAME/graphql" || echo "")
        
        if echo "$GRAPHQL_RESPONSE" | grep -q "Hello"; then
            log_success "GraphQL endpoint is working"
        else
            log_warning "GraphQL endpoint test failed"
        fi
        
        log_info "Application URLs:"
        echo "  Health Check: http://$ALB_DNS_NAME/health"
        echo "  GraphQL:      http://$ALB_DNS_NAME/graphql"
        echo "  API Docs:     http://$ALB_DNS_NAME/docs"
    else
        log_warning "Could not get ALB DNS name from Terraform outputs"
    fi
}

cleanup_on_error() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Deployment failed with exit code $exit_code"
        
        # Optionally rollback on failure for production
        if [ "$ENVIRONMENT" = "production" ]; then
            log_warning "Consider rolling back the deployment"
        fi
    fi
    exit $exit_code
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-terraform)
            SKIP_TERRAFORM=true
            shift
            ;;
        --skip-deploy)
            SKIP_DEPLOY=true
            shift
            ;;
        --force-apply)
            FORCE_APPLY=true
            shift
            ;;
        --auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        development|staging|production)
            ENVIRONMENT="$1"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    show_usage
    exit 1
fi

# Set error trap
trap cleanup_on_error ERR

# Main deployment process
main() {
    log_info "Starting deployment to $ENVIRONMENT environment"
    echo ""
    
    check_prerequisites
    build_and_push_images
    deploy_infrastructure
    deploy_application
    verify_deployment
    
    echo ""
    log_success "Deployment to $ENVIRONMENT completed successfully!"
    
    # Show next steps for development
    if [ "$ENVIRONMENT" = "development" ]; then
        echo ""
        log_info "Development environment is ready. You can now:"
        echo "  - Access the GraphQL playground"
        echo "  - Run integration tests"
        echo "  - Monitor application logs"
    fi
}

# Run main function
main "$@"