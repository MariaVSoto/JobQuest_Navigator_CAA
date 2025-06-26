#!/bin/bash

# JobQuest Navigator - Backend Deployment Script
# This script deploys the Django backend to AWS Lambda using Zappa

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

# Check if we're in the correct directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the backend directory."
    exit 1
fi

print_status "Starting JobQuest Navigator Backend Deployment..."

# Check prerequisites
print_status "Checking prerequisites..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if Python 3.9 is available
python_version=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
if [ "$python_version" != "3.9" ]; then
    print_warning "Python 3.9 recommended. Current version: $python_version"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Zappa if not present
if ! pip list | grep -q zappa; then
    print_status "Installing Zappa..."
    pip install zappa
fi

# Load environment variables
if [ -f "../configs/environment.env" ]; then
    print_status "Loading environment variables..."
    export $(cat ../configs/environment.env | grep -v '^#' | xargs)
else
    print_warning "Environment file not found. Using default values."
fi

# Check database connection
print_status "Testing database connection..."
if python manage.py check --database default --settings=core.settings_production; then
    print_success "Database connection successful"
else
    print_error "Database connection failed. Please check your database configuration."
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate --settings=core.settings_production

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --settings=core.settings_production

# Check if this is first deployment or update
if zappa status production > /dev/null 2>&1; then
    print_status "Updating existing Lambda deployment..."
    zappa update production
    deployment_type="update"
else
    print_status "Deploying Lambda function for the first time..."
    zappa deploy production
    deployment_type="deploy"
fi

# Wait a moment for deployment to complete
sleep 5

# Set environment variables in Lambda
if [ "$deployment_type" = "deploy" ]; then
    print_status "Setting Lambda environment variables..."
    
    # Set Django settings
    zappa set_env production DJANGO_SETTINGS_MODULE "core.settings_production"
    zappa set_env production DJANGO_SECRET_KEY "${DJANGO_SECRET_KEY:-change-me-in-production}"
    zappa set_env production DEBUG "False"
    
    # Set database configuration
    if [ ! -z "$RDS_HOSTNAME" ]; then
        zappa set_env production RDS_HOSTNAME "$RDS_HOSTNAME"
        zappa set_env production RDS_DB_NAME "$RDS_DB_NAME"
        zappa set_env production RDS_USERNAME "$RDS_USERNAME"
        zappa set_env production RDS_PASSWORD "$RDS_PASSWORD"
        zappa set_env production RDS_PORT "$RDS_PORT"
    fi
    
    # Set AWS S3 configuration
    if [ ! -z "$AWS_STORAGE_BUCKET_NAME" ]; then
        zappa set_env production AWS_STORAGE_BUCKET_NAME "$AWS_STORAGE_BUCKET_NAME"
        zappa set_env production AWS_S3_REGION_NAME "$AWS_S3_REGION_NAME"
    fi
    
    # Set CORS configuration
    if [ ! -z "$CORS_ALLOWED_ORIGINS" ]; then
        zappa set_env production CORS_ALLOWED_ORIGINS "$CORS_ALLOWED_ORIGINS"
    fi
fi

# Get API Gateway URL
print_status "Retrieving API Gateway URL..."
api_url=$(zappa status production | grep "API Gateway URL" | awk '{print $4}')

if [ ! -z "$api_url" ]; then
    print_success "API Gateway URL: $api_url"
    
    # Save API URL to file for frontend deployment
    echo "$api_url" > ../configs/api-gateway-url.txt
else
    print_warning "Could not retrieve API Gateway URL"
fi

# Test basic API endpoint
print_status "Testing deployed API..."
if [ ! -z "$api_url" ]; then
    health_check_url="${api_url}/api/health/"
    
    # Wait a moment for Lambda to be ready
    sleep 10
    
    # Test health endpoint
    if curl -f -s "$health_check_url" > /dev/null; then
        print_success "API health check passed"
    else
        print_warning "API health check failed. This might be normal for initial deployment."
    fi
else
    print_warning "Skipping API test due to missing URL"
fi

# Create superuser if this is first deployment
if [ "$deployment_type" = "deploy" ]; then
    read -p "Do you want to create a superuser account? (y/N): " create_superuser
    if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
        print_status "Creating superuser account..."
        python manage.py createsuperuser --settings=core.settings_production
    fi
fi

# Show deployment summary
print_success "Backend deployment completed successfully!"
echo
echo "=== Deployment Summary ==="
echo "Deployment Type: $deployment_type"
echo "Lambda Function: jobquest-navigator-api-production"
if [ ! -z "$api_url" ]; then
    echo "API Gateway URL: $api_url"
fi
echo "Environment: production"
echo "Settings Module: core.settings_production"
echo

# Show next steps
echo "=== Next Steps ==="
echo "1. Test API endpoints manually:"
if [ ! -z "$api_url" ]; then
    echo "   curl ${api_url}/api/health/"
    echo "   curl ${api_url}/api/auth/register/"
fi
echo "2. Deploy frontend using scripts/deploy-frontend.sh"
echo "3. Run end-to-end tests using scripts/verify-deployment.sh"
echo

# Show useful commands
echo "=== Useful Commands ==="
echo "View logs: zappa tail production"
echo "Update deployment: zappa update production"
echo "Check status: zappa status production"
echo "Rollback: zappa rollback production -n 1"
echo

print_success "Backend deployment script completed!"