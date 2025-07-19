#!/bin/bash

# JobQuest Navigator LocalStack Setup Script
# This script sets up the local AWS environment using LocalStack

set -e

echo "🚀 JobQuest Navigator LocalStack Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if LocalStack is running
check_localstack() {
    print_status "Checking LocalStack status..."
    if curl -s http://localhost:4566/health > /dev/null 2>&1; then
        print_status "LocalStack is running ✅"
        return 0
    else
        print_warning "LocalStack is not running"
        return 1
    fi
}

# Start LocalStack services
start_localstack() {
    print_status "Starting LocalStack services..."
    
    if [ -f "docker-compose.localstack.yml" ]; then
        docker-compose -f docker-compose.localstack.yml up -d
        print_status "Waiting for LocalStack to start..."
        sleep 10
        
        # Wait for LocalStack to be ready
        for i in {1..30}; do
            if check_localstack; then
                break
            fi
            print_status "Waiting for LocalStack... ($i/30)"
            sleep 2
        done
        
        if ! check_localstack; then
            print_error "LocalStack failed to start"
            exit 1
        fi
    else
        print_error "docker-compose.localstack.yml not found"
        exit 1
    fi
}

# Create S3 buckets
create_s3_buckets() {
    print_status "Creating S3 buckets..."
    
    # Frontend bucket
    aws --endpoint-url=http://localhost:4566 s3 mb s3://jobquest-navigator-frontend-local --region us-east-1
    aws --endpoint-url=http://localhost:4566 s3api put-bucket-policy --bucket jobquest-navigator-frontend-local --policy '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::jobquest-navigator-frontend-local/*"
            }
        ]
    }'
    
    # Static files bucket
    aws --endpoint-url=http://localhost:4566 s3 mb s3://jobquest-navigator-static-local --region us-east-1
    
    # Lambda deployment bucket
    aws --endpoint-url=http://localhost:4566 s3 mb s3://jobquest-navigator-lambda-local --region us-east-1
    
    print_status "S3 buckets created successfully ✅"
}

# Setup IAM roles
setup_iam() {
    print_status "Setting up IAM roles..."
    
    # Create Lambda execution role
    aws --endpoint-url=http://localhost:4566 iam create-role \
        --role-name lambda-execution-role \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }' || true
    
    # Attach policies
    aws --endpoint-url=http://localhost:4566 iam attach-role-policy \
        --role-name lambda-execution-role \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole || true
    
    print_status "IAM roles setup completed ✅"
}

# Configure AWS CLI for LocalStack
configure_aws_cli() {
    print_status "Configuring AWS CLI for LocalStack..."
    
    # Set environment variables for LocalStack
    export AWS_ACCESS_KEY_ID=test
    export AWS_SECRET_ACCESS_KEY=test
    export AWS_DEFAULT_REGION=us-east-1
    export AWS_ENDPOINT_URL=http://localhost:4566
    
    print_status "AWS CLI configured for LocalStack ✅"
}

# Setup database
setup_database() {
    print_status "Setting up MySQL database..."
    
    # Wait for MySQL to be ready
    for i in {1..30}; do
        if docker exec jobquest-mysql mysqladmin ping -h"localhost" --silent; then
            print_status "MySQL is ready ✅"
            break
        fi
        print_status "Waiting for MySQL... ($i/30)"
        sleep 2
    done
    
    # Run Django migrations
    print_status "Running Django migrations..."
    cd ..
    python manage.py migrate --settings=core.settings_local
    
    print_status "Database setup completed ✅"
}

# Create Django superuser
create_superuser() {
    print_status "Creating Django superuser..."
    cd ..
    
    # Create superuser non-interactively
    python manage.py shell --settings=core.settings_local << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@jobquest.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF
    
    print_status "Superuser setup completed ✅"
}

# Test local deployment
test_deployment() {
    print_status "Testing local deployment..."
    
    # Test API endpoint
    if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
        print_status "API is responding ✅"
    else
        print_warning "API is not responding, you may need to start Django server manually"
    fi
    
    # Test S3 buckets
    aws --endpoint-url=http://localhost:4566 s3 ls > /dev/null 2>&1 && print_status "S3 buckets accessible ✅"
    
    print_status "Local deployment test completed ✅"
}

# Main execution
main() {
    print_status "Starting JobQuest Navigator LocalStack setup..."
    
    # Configure AWS CLI first
    configure_aws_cli
    
    # Check and start LocalStack
    if ! check_localstack; then
        start_localstack
    fi
    
    # Setup AWS services
    create_s3_buckets
    setup_iam
    
    # Setup database
    setup_database
    create_superuser
    
    # Test deployment
    test_deployment
    
    echo ""
    echo "🎉 LocalStack setup completed successfully!"
    echo "======================================"
    echo "📍 LocalStack Dashboard: http://localhost:4566"
    echo "📍 S3 Console: http://localhost:4566/moto-ui/"
    echo "📍 MySQL: localhost:3306 (admin/adminpassword)"
    echo ""
    echo "Next steps:"
    echo "1. Start Django server: python manage.py runserver --settings=core.settings_local"
    echo "2. Access API: http://localhost:8000/api/"
    echo "3. Admin panel: http://localhost:8000/admin/ (admin/admin123)"
    echo ""
    echo "Environment variables set:"
    echo "export AWS_ACCESS_KEY_ID=test"
    echo "export AWS_SECRET_ACCESS_KEY=test"
    echo "export AWS_DEFAULT_REGION=us-east-1"
    echo "export AWS_ENDPOINT_URL=http://localhost:4566"
}

# Run main function
main "$@"