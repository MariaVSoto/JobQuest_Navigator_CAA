#!/bin/bash

# JobQuest Navigator - Deployment Verification Script
# This script verifies that all components are deployed and working correctly

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

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_test "Testing: $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        print_success "✓ $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        print_error "✗ $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to test HTTP endpoint
test_http_endpoint() {
    local url="$1"
    local expected_status="${2:-200}"
    local timeout="${3:-10}"
    
    local response=$(curl -s -w "%{http_code}" --max-time "$timeout" "$url" -o /dev/null)
    [ "$response" = "$expected_status" ]
}

print_status "Starting JobQuest Navigator Deployment Verification..."

# Load environment variables
if [ -f "../configs/environment.env" ]; then
    export $(cat ../configs/environment.env | grep -v '^#' | xargs)
fi

# =============================================================================
# Infrastructure Tests
# =============================================================================

print_status "=== Testing Infrastructure ==="

# Test AWS CLI configuration
run_test "AWS CLI Configuration" "aws sts get-caller-identity"

# Test CloudFormation stack
STACK_NAME="jobquest-navigator-infra"
run_test "CloudFormation Stack Status" "aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].StackStatus' --output text | grep -E 'CREATE_COMPLETE|UPDATE_COMPLETE'"

# Get stack outputs
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" > /dev/null 2>&1; then
    OUTPUTS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].Outputs')
    
    # Extract important values
    DB_ENDPOINT=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="DatabaseEndpoint") | .OutputValue' 2>/dev/null || echo "")
    STATIC_BUCKET=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="StaticBucketName") | .OutputValue' 2>/dev/null || echo "")
    FRONTEND_BUCKET=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="FrontendBucketName") | .OutputValue' 2>/dev/null || echo "")
    FRONTEND_URL=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="FrontendURL") | .OutputValue' 2>/dev/null || echo "")
    VPC_ID=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="VPCId") | .OutputValue' 2>/dev/null || echo "")
fi

# Test RDS Database
if [ ! -z "$DB_ENDPOINT" ]; then
    run_test "RDS Database Instance" "aws rds describe-db-instances --db-instance-identifier jobquest-navigator-db --query 'DBInstances[0].DBInstanceStatus' --output text | grep available"
else
    print_warning "Database endpoint not found in stack outputs"
fi

# Test S3 Buckets
if [ ! -z "$STATIC_BUCKET" ]; then
    run_test "S3 Static Files Bucket" "aws s3 ls s3://$STATIC_BUCKET"
else
    print_warning "Static bucket name not found in stack outputs"
fi

if [ ! -z "$FRONTEND_BUCKET" ]; then
    run_test "S3 Frontend Bucket" "aws s3 ls s3://$FRONTEND_BUCKET"
else
    print_warning "Frontend bucket name not found in stack outputs"
fi

# Test VPC and Security Groups
if [ ! -z "$VPC_ID" ]; then
    run_test "VPC Configuration" "aws ec2 describe-vpcs --vpc-ids $VPC_ID --query 'Vpcs[0].State' --output text | grep available"
else
    print_warning "VPC ID not found in stack outputs"
fi

# =============================================================================
# Backend Tests
# =============================================================================

print_status "=== Testing Backend ==="

# Test Lambda function
run_test "Lambda Function Exists" "aws lambda get-function --function-name jobquest-navigator-api-production"

# Get API Gateway URL
if [ -f "../configs/api-gateway-url.txt" ]; then
    API_URL=$(cat ../configs/api-gateway-url.txt)
elif command -v zappa &> /dev/null; then
    API_URL=$(zappa status production 2>/dev/null | grep "API Gateway URL" | awk '{print $4}' || echo "")
fi

if [ ! -z "$API_URL" ]; then
    print_status "Testing API Gateway URL: $API_URL"
    
    # Test health endpoint
    run_test "API Health Endpoint" "test_http_endpoint '$API_URL/api/health/'"
    
    # Test authentication endpoints
    run_test "API Auth Register Endpoint" "test_http_endpoint '$API_URL/api/auth/register/' 405"  # Method not allowed is expected for GET
    
    # Test main API endpoints
    run_test "API Jobs Endpoint" "test_http_endpoint '$API_URL/api/jobs/' 401"  # Unauthorized expected without token
    run_test "API Resumes Endpoint" "test_http_endpoint '$API_URL/api/resumes/resumes/' 401"
    run_test "API Skills Endpoint" "test_http_endpoint '$API_URL/api/skills/' 401"
    
else
    print_warning "API Gateway URL not found. Skipping API tests."
fi

# Test Lambda logs
run_test "Lambda Function Logs" "aws logs describe-log-groups --log-group-name-prefix '/aws/lambda/jobquest-navigator-api-production'"

# =============================================================================
# Frontend Tests
# =============================================================================

print_status "=== Testing Frontend ==="

# Test frontend S3 website
if [ ! -z "$FRONTEND_URL" ]; then
    print_status "Testing Frontend URL: $FRONTEND_URL"
    run_test "Frontend Website" "test_http_endpoint '$FRONTEND_URL'"
    run_test "Frontend Index Page" "curl -s '$FRONTEND_URL' | grep -q 'JobQuest Navigator'"
elif [ ! -z "$FRONTEND_BUCKET" ]; then
    # Construct URL from bucket name
    AWS_REGION=$(aws configure get region)
    FRONTEND_URL="https://$FRONTEND_BUCKET.s3-website-$AWS_REGION.amazonaws.com"
    print_status "Testing constructed Frontend URL: $FRONTEND_URL"
    run_test "Frontend Website" "test_http_endpoint '$FRONTEND_URL'"
else
    print_warning "Frontend URL not available. Skipping frontend tests."
fi

# Test frontend files in S3
if [ ! -z "$FRONTEND_BUCKET" ]; then
    run_test "Frontend index.html exists" "aws s3 ls s3://$FRONTEND_BUCKET/index.html"
    run_test "Frontend static files exist" "aws s3 ls s3://$FRONTEND_BUCKET/static/"
fi

# =============================================================================
# Integration Tests
# =============================================================================

print_status "=== Testing Integration ==="

# Test CORS configuration
if [ ! -z "$API_URL" ] && [ ! -z "$FRONTEND_URL" ]; then
    print_test "Testing CORS Configuration"
    CORS_TEST=$(curl -s -H "Origin: $FRONTEND_URL" \
                     -H "Access-Control-Request-Method: GET" \
                     -X OPTIONS \
                     "$API_URL/api/health/" \
                     -w "%{http_code}" -o /dev/null)
    
    if [ "$CORS_TEST" = "200" ] || [ "$CORS_TEST" = "204" ]; then
        print_success "✓ CORS Configuration"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_error "✗ CORS Configuration (Response: $CORS_TEST)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# Test database connectivity from Lambda
if [ ! -z "$API_URL" ]; then
    print_test "Testing Database Connectivity through API"
    # This would require a specific health check endpoint that tests DB connection
    DB_TEST=$(curl -s "$API_URL/api/health/" | grep -o '"database":[^,]*' || echo "")
    if [[ "$DB_TEST" == *"true"* ]] || [[ "$DB_TEST" == *"ok"* ]]; then
        print_success "✓ Database Connectivity"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_warning "△ Database Connectivity (Could not verify)"
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# =============================================================================
# Performance Tests
# =============================================================================

print_status "=== Testing Performance ==="

# Test API response time
if [ ! -z "$API_URL" ]; then
    print_test "API Response Time"
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "$API_URL/api/health/")
    if (( $(echo "$RESPONSE_TIME < 5.0" | bc -l) )); then
        print_success "✓ API Response Time ($RESPONSE_TIME seconds)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_warning "△ API Response Time slow ($RESPONSE_TIME seconds)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# Test frontend loading time
if [ ! -z "$FRONTEND_URL" ]; then
    print_test "Frontend Loading Time"
    FRONTEND_TIME=$(curl -s -w "%{time_total}" -o /dev/null "$FRONTEND_URL")
    if (( $(echo "$FRONTEND_TIME < 3.0" | bc -l) )); then
        print_success "✓ Frontend Loading Time ($FRONTEND_TIME seconds)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_warning "△ Frontend Loading Time slow ($FRONTEND_TIME seconds)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# =============================================================================
# Security Tests
# =============================================================================

print_status "=== Testing Security ==="

# Test S3 bucket security
if [ ! -z "$STATIC_BUCKET" ]; then
    print_test "S3 Static Bucket Security"
    # Check if bucket has public read access but not public write
    BUCKET_ACL=$(aws s3api get-bucket-acl --bucket "$STATIC_BUCKET" 2>/dev/null || echo "")
    if [[ "$BUCKET_ACL" != *"AllUsers"* ]] || aws s3api get-bucket-policy --bucket "$STATIC_BUCKET" > /dev/null 2>&1; then
        print_success "✓ S3 Static Bucket Security"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_warning "△ S3 Static Bucket Security (Check bucket policy)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# Test RDS security
if [ ! -z "$DB_ENDPOINT" ]; then
    print_test "RDS Security Configuration"
    PUBLIC_ACCESS=$(aws rds describe-db-instances \
        --db-instance-identifier jobquest-navigator-db \
        --query 'DBInstances[0].PubliclyAccessible' \
        --output text 2>/dev/null || echo "")
    
    if [ "$PUBLIC_ACCESS" = "False" ]; then
        print_success "✓ RDS Security Configuration (Not publicly accessible)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_error "✗ RDS Security Configuration (Publicly accessible)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# =============================================================================
# Cost Optimization Tests
# =============================================================================

print_status "=== Testing Cost Optimization ==="

# Check RDS instance class
if [ ! -z "$DB_ENDPOINT" ]; then
    print_test "RDS Instance Size"
    DB_CLASS=$(aws rds describe-db-instances \
        --db-instance-identifier jobquest-navigator-db \
        --query 'DBInstances[0].DBInstanceClass' \
        --output text 2>/dev/null || echo "")
    
    if [ "$DB_CLASS" = "db.t3.micro" ]; then
        print_success "✓ RDS Instance Size (Cost optimized: $DB_CLASS)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_warning "△ RDS Instance Size (Consider db.t3.micro for cost optimization: $DB_CLASS)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# Check Lambda memory allocation
print_test "Lambda Memory Configuration"
LAMBDA_MEMORY=$(aws lambda get-function-configuration \
    --function-name jobquest-navigator-api-production \
    --query 'MemorySize' \
    --output text 2>/dev/null || echo "")

if [ "$LAMBDA_MEMORY" -le 512 ]; then
    print_success "✓ Lambda Memory Configuration (Cost optimized: ${LAMBDA_MEMORY}MB)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    print_warning "△ Lambda Memory Configuration (Consider reducing for cost optimization: ${LAMBDA_MEMORY}MB)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# =============================================================================
# Generate Test Report
# =============================================================================

echo
echo "================================================================================"
echo "                          DEPLOYMENT VERIFICATION REPORT"
echo "================================================================================"
echo
echo "Test Summary:"
echo "  Total Tests: $TOTAL_TESTS"
echo "  Passed: $PASSED_TESTS"
echo "  Failed: $FAILED_TESTS"
echo "  Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
echo

# Show deployment information
echo "Deployment Information:"
if [ ! -z "$API_URL" ]; then
    echo "  Backend API: $API_URL"
fi
if [ ! -z "$FRONTEND_URL" ]; then
    echo "  Frontend: $FRONTEND_URL"
fi
if [ ! -z "$DB_ENDPOINT" ]; then
    echo "  Database: $DB_ENDPOINT"
fi
echo "  AWS Region: $(aws configure get region)"
echo "  Stack: $STACK_NAME"
echo

# Generate recommendations
echo "Recommendations:"
if [ "$FAILED_TESTS" -gt 0 ]; then
    echo "  - Review failed tests and fix any issues"
    echo "  - Check CloudWatch logs for error details"
    echo "  - Verify environment variables are correctly set"
fi

if [ "$PASSED_TESTS" -eq "$TOTAL_TESTS" ]; then
    print_success "All tests passed! Deployment verification successful."
    echo "  - Your application is ready for use"
    echo "  - Consider setting up monitoring and alerts"
    echo "  - Review the security configuration regularly"
else
    print_warning "Some tests failed. Please review and fix issues before production use."
fi

echo
echo "Useful commands for further testing:"
echo "  - View Lambda logs: zappa tail production"
echo "  - Check CloudFormation events: aws cloudformation describe-stack-events --stack-name $STACK_NAME"
echo "  - Monitor costs: aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-12-31 --granularity MONTHLY --metrics BlendedCost"
echo

# Save report to file
REPORT_FILE="../docs/deployment-verification-$(date +%Y%m%d-%H%M%S).txt"
{
    echo "JobQuest Navigator Deployment Verification Report"
    echo "Generated: $(date)"
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo "Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    echo
    echo "Backend API: ${API_URL:-'Not available'}"
    echo "Frontend URL: ${FRONTEND_URL:-'Not available'}"
    echo "Database Endpoint: ${DB_ENDPOINT:-'Not available'}"
} > "$REPORT_FILE"

print_status "Verification report saved to: $REPORT_FILE"

# Exit with appropriate code
if [ "$FAILED_TESTS" -gt 0 ]; then
    exit 1
else
    exit 0
fi