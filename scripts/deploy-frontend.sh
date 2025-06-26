#!/bin/bash

# JobQuest Navigator - Frontend Deployment Script
# This script builds and deploys the React frontend to AWS S3

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
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the frontend directory."
    exit 1
fi

print_status "Starting JobQuest Navigator Frontend Deployment..."

# Check prerequisites
print_status "Checking prerequisites..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    print_error "Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$node_version" -lt 16 ]; then
    print_error "Node.js 16+ required. Current version: $(node --version)"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    print_error "npm not found. Please install npm first."
    exit 1
fi

# Load environment variables
if [ -f "../configs/environment.env" ]; then
    print_status "Loading environment variables..."
    export $(cat ../configs/environment.env | grep -v '^#' | xargs)
else
    print_warning "Environment file not found. Using default values."
fi

# Get API Gateway URL
if [ -f "../configs/api-gateway-url.txt" ]; then
    API_URL=$(cat ../configs/api-gateway-url.txt)
    print_status "Using API URL from file: $API_URL"
elif [ ! -z "$REACT_APP_API_URL" ]; then
    API_URL="$REACT_APP_API_URL"
    print_status "Using API URL from environment: $API_URL"
else
    print_warning "API Gateway URL not found. Please deploy backend first or set REACT_APP_API_URL."
    read -p "Enter API Gateway URL: " API_URL
fi

# Set environment variables for build
export REACT_APP_API_URL="$API_URL"
export REACT_APP_ENVIRONMENT="production"
export NODE_ENV="production"

# Determine S3 bucket name
FRONTEND_BUCKET="${AWS_FRONTEND_BUCKET:-jobquest-navigator-frontend-production}"

print_status "Frontend bucket: $FRONTEND_BUCKET"

# Check if S3 bucket exists
if ! aws s3 ls "s3://$FRONTEND_BUCKET" > /dev/null 2>&1; then
    print_error "S3 bucket '$FRONTEND_BUCKET' not found. Please create it first or run CloudFormation stack."
    exit 1
fi

# Install dependencies
print_status "Installing npm dependencies..."
npm ci --production=false

# Run tests (optional)
if [ "$RUN_TESTS" = "true" ]; then
    print_status "Running tests..."
    npm test -- --coverage --watchAll=false
fi

# Build the application
print_status "Building React application for production..."
print_status "API URL: $REACT_APP_API_URL"

# Clean previous build
rm -rf build/

# Build the app
npm run build

# Verify build was successful
if [ ! -d "build" ]; then
    print_error "Build directory not found. Build failed."
    exit 1
fi

if [ ! -f "build/index.html" ]; then
    print_error "index.html not found in build directory. Build failed."
    exit 1
fi

print_success "Build completed successfully"

# Deploy to S3
print_status "Deploying to S3 bucket: $FRONTEND_BUCKET"

# Sync build directory to S3 with appropriate cache headers
aws s3 sync build/ "s3://$FRONTEND_BUCKET" \
  --delete \
  --cache-control "public,max-age=31536000" \
  --exclude "*.html" \
  --exclude "service-worker.js" \
  --exclude "manifest.json"

# Upload HTML files with no-cache headers
aws s3 sync build/ "s3://$FRONTEND_BUCKET" \
  --cache-control "no-cache,no-store,must-revalidate" \
  --include "*.html" \
  --include "service-worker.js" \
  --include "manifest.json"

# Set content type for specific files
print_status "Setting content types..."

# Set content type for CSS files
aws s3 cp "s3://$FRONTEND_BUCKET" "s3://$FRONTEND_BUCKET" \
  --recursive \
  --exclude "*" \
  --include "*.css" \
  --metadata-directive REPLACE \
  --content-type "text/css"

# Set content type for JS files
aws s3 cp "s3://$FRONTEND_BUCKET" "s3://$FRONTEND_BUCKET" \
  --recursive \
  --exclude "*" \
  --include "*.js" \
  --metadata-directive REPLACE \
  --content-type "application/javascript"

# Configure S3 bucket for static website hosting
print_status "Configuring S3 bucket for static website hosting..."
aws s3 website "s3://$FRONTEND_BUCKET" \
  --index-document index.html \
  --error-document index.html

# Ensure bucket policy allows public read access
print_status "Setting bucket policy for public access..."
cat > /tmp/bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$FRONTEND_BUCKET/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket "$FRONTEND_BUCKET" \
  --policy file:///tmp/bucket-policy.json

# Clean up temporary file
rm /tmp/bucket-policy.json

# Get website URL
WEBSITE_URL="https://$FRONTEND_BUCKET.s3-website-$(aws configure get region).amazonaws.com"

# Test deployment
print_status "Testing deployed website..."
if curl -f -s "$WEBSITE_URL" > /dev/null; then
    print_success "Website is accessible"
else
    print_warning "Website test failed. This might be due to propagation delay."
fi

# Save website URL for reference
echo "$WEBSITE_URL" > ../configs/frontend-url.txt

# Show deployment summary
print_success "Frontend deployment completed successfully!"
echo
echo "=== Deployment Summary ==="
echo "S3 Bucket: $FRONTEND_BUCKET"
echo "Website URL: $WEBSITE_URL"
echo "API URL: $REACT_APP_API_URL"
echo "Environment: production"
echo

# Show deployment statistics
print_status "Deployment Statistics:"
echo "Build size: $(du -sh build/ | cut -f1)"
echo "Files uploaded: $(find build/ -type f | wc -l)"

# List uploaded files
print_status "Uploaded files:"
aws s3 ls "s3://$FRONTEND_BUCKET" --recursive --human-readable --summarize

echo
echo "=== Next Steps ==="
echo "1. Test the website: $WEBSITE_URL"
echo "2. Test API connectivity from frontend"
echo "3. Run end-to-end tests using scripts/verify-deployment.sh"
echo

# Show useful commands
echo "=== Useful Commands ==="
echo "Check bucket contents: aws s3 ls s3://$FRONTEND_BUCKET --recursive"
echo "Download deployment: aws s3 sync s3://$FRONTEND_BUCKET ./downloaded-build"
echo "View bucket policy: aws s3api get-bucket-policy --bucket $FRONTEND_BUCKET"
echo "Website configuration: aws s3api get-bucket-website --bucket $FRONTEND_BUCKET"
echo

# Optional: CloudFront invalidation
if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    print_status "Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
      --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
      --paths "/*"
    print_success "CloudFront invalidation created"
fi

print_success "Frontend deployment script completed!"
print_status "You can now access your application at: $WEBSITE_URL"