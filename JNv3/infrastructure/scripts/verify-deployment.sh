#!/bin/bash
# JobQuest Navigator v2 - Deployment Verification Script
# Comprehensive testing of deployed infrastructure and application

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

# Default values
ENVIRONMENT="development"
TIMEOUT=300  # 5 minutes timeout for checks
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    ((TESTS_PASSED++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((TESTS_FAILED++))
    FAILED_TESTS+=("$1")
}

show_usage() {
    cat << EOF
JobQuest Navigator v2 - Deployment Verification Script

Usage: $0 [OPTIONS] ENVIRONMENT

ENVIRONMENT:
    development     Verify development environment
    staging         Verify staging environment
    production      Verify production environment

OPTIONS:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    --timeout N     Set timeout for checks in seconds (default: 300)

EXAMPLES:
    $0 development                    # Verify development deployment
    $0 --verbose staging             # Verify staging with verbose output
    $0 --timeout 600 production     # Verify production with 10min timeout

EOF
}

check_terraform_outputs() {
    log_info "Checking Terraform outputs..."
    
    cd "$TERRAFORM_DIR"
    
    # Check if terraform state exists
    if ! terraform show &> /dev/null; then
        log_error "Terraform state not found. Run deployment first."
        return 1
    fi
    
    # Get critical outputs
    ALB_DNS_NAME=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
    BACKEND_URL=$(terraform output -raw backend_url 2>/dev/null || echo "")
    ECS_CLUSTER_NAME=$(terraform output -raw ecs_cluster_name 2>/dev/null || echo "")
    RDS_ENDPOINT=$(terraform output -raw rds_endpoint 2>/dev/null || echo "")
    REDIS_ENDPOINT=$(terraform output -raw redis_endpoint 2>/dev/null || echo "")
    
    if [ -n "$ALB_DNS_NAME" ]; then
        log_success "ALB DNS name: $ALB_DNS_NAME"
    else
        log_error "ALB DNS name not available"
    fi
    
    if [ -n "$ECS_CLUSTER_NAME" ]; then
        log_success "ECS cluster: $ECS_CLUSTER_NAME"
    else
        log_error "ECS cluster name not available"
    fi
    
    cd "$PROJECT_ROOT"
}

check_aws_infrastructure() {
    log_info "Checking AWS infrastructure..."
    
    # Check ECS cluster status
    if [ -n "$ECS_CLUSTER_NAME" ]; then
        CLUSTER_STATUS=$(aws ecs describe-clusters --clusters "$ECS_CLUSTER_NAME" \
            --query 'clusters[0].status' --output text 2>/dev/null || echo "NOT_FOUND")
        
        if [ "$CLUSTER_STATUS" = "ACTIVE" ]; then
            log_success "ECS cluster is active"
        else
            log_error "ECS cluster status: $CLUSTER_STATUS"
        fi
        
        # Check ECS services
        SERVICES=$(aws ecs list-services --cluster "$ECS_CLUSTER_NAME" \
            --query 'serviceArns' --output text 2>/dev/null || echo "")
        
        if [ -n "$SERVICES" ]; then
            log_success "ECS services found: $(echo "$SERVICES" | wc -w)"
            
            # Check service status
            for service in $SERVICES; do
                SERVICE_NAME=$(basename "$service")
                RUNNING_COUNT=$(aws ecs describe-services --cluster "$ECS_CLUSTER_NAME" \
                    --services "$service" --query 'services[0].runningCount' --output text 2>/dev/null || echo "0")
                DESIRED_COUNT=$(aws ecs describe-services --cluster "$ECS_CLUSTER_NAME" \
                    --services "$service" --query 'services[0].desiredCount' --output text 2>/dev/null || echo "0")
                
                if [ "$RUNNING_COUNT" = "$DESIRED_COUNT" ] && [ "$RUNNING_COUNT" -gt 0 ]; then
                    log_success "$SERVICE_NAME: $RUNNING_COUNT/$DESIRED_COUNT tasks running"
                else
                    log_error "$SERVICE_NAME: $RUNNING_COUNT/$DESIRED_COUNT tasks running"
                fi
            done
        else
            log_error "No ECS services found"
        fi
    fi
    
    # Check RDS instance
    if [ -n "$RDS_ENDPOINT" ]; then
        RDS_STATUS=$(aws rds describe-db-instances \
            --query "DBInstances[?Endpoint.Address=='${RDS_ENDPOINT}'].DBInstanceStatus" \
            --output text 2>/dev/null || echo "NOT_FOUND")
        
        if [ "$RDS_STATUS" = "available" ]; then
            log_success "RDS instance is available"
        else
            log_error "RDS instance status: $RDS_STATUS"
        fi
    fi
    
    # Check ElastiCache cluster
    if [ -n "$REDIS_ENDPOINT" ]; then
        CACHE_STATUS=$(aws elasticache describe-cache-clusters \
            --query "CacheClusters[?CacheNodeType != null].CacheClusterStatus" \
            --output text 2>/dev/null | head -1 || echo "NOT_FOUND")
        
        if [ "$CACHE_STATUS" = "available" ]; then
            log_success "ElastiCache cluster is available"
        else
            log_error "ElastiCache cluster status: $CACHE_STATUS"
        fi
    fi
}

check_application_health() {
    log_info "Checking application health..."
    
    if [ -z "$ALB_DNS_NAME" ]; then
        log_error "ALB DNS name not available, skipping application checks"
        return 1
    fi
    
    # Build URLs
    if [ -n "$BACKEND_URL" ]; then
        HEALTH_URL="$BACKEND_URL/health"
        GRAPHQL_URL="$BACKEND_URL/graphql"
    else
        HEALTH_URL="http://$ALB_DNS_NAME/health"
        GRAPHQL_URL="http://$ALB_DNS_NAME/graphql"
    fi
    
    # Wait for application to be ready
    log_info "Waiting for application to be ready (timeout: ${TIMEOUT}s)..."
    
    local end_time=$((SECONDS + TIMEOUT))
    local health_check_passed=false
    
    while [ $SECONDS -lt $end_time ]; do
        if curl -f -s "$HEALTH_URL" > /dev/null 2>&1; then
            health_check_passed=true
            break
        fi
        
        if [ "$VERBOSE" = true ]; then
            log_info "Health check attempt failed, retrying..."
        fi
        
        sleep 10
    done
    
    if [ "$health_check_passed" = true ]; then
        log_success "Application health check endpoint is responding"
        
        # Get detailed health status
        HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" || echo "{}")
        
        if [ "$VERBOSE" = true ]; then
            echo "Health response: $HEALTH_RESPONSE"
        fi
        
        # Parse health status
        STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
        
        if [ "$STATUS" = "healthy" ]; then
            log_success "Application reports healthy status"
        elif [ "$STATUS" = "degraded" ]; then
            log_warning "Application reports degraded status"
        else
            log_error "Application status: $STATUS"
        fi
        
        # Check individual services
        DB_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.services.database // "unknown"' 2>/dev/null || echo "unknown")
        if [ "$DB_STATUS" = "connected" ]; then
            log_success "Database connectivity: OK"
        else
            log_error "Database connectivity: $DB_STATUS"
        fi
        
        CACHE_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.services.cache // "not_configured"' 2>/dev/null || echo "not_configured")
        if [ "$CACHE_STATUS" = "connected" ]; then
            log_success "Cache connectivity: OK"
        elif [ "$CACHE_STATUS" = "not_configured" ]; then
            log_info "Cache not configured (development mode)"
        else
            log_warning "Cache connectivity: $CACHE_STATUS"
        fi
    else
        log_error "Application health check failed after ${TIMEOUT}s timeout"
    fi
}

check_graphql_endpoint() {
    log_info "Checking GraphQL endpoint..."
    
    if [ -z "$GRAPHQL_URL" ]; then
        log_error "GraphQL URL not available"
        return 1
    fi
    
    # Test GraphQL introspection query
    INTROSPECTION_QUERY='{"query":"query IntrospectionQuery { __schema { types { name } } }"}'
    
    GRAPHQL_RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$INTROSPECTION_QUERY" \
        "$GRAPHQL_URL" 2>/dev/null || echo "")
    
    if echo "$GRAPHQL_RESPONSE" | grep -q "__schema"; then
        log_success "GraphQL introspection query successful"
    else
        log_error "GraphQL introspection query failed"
        if [ "$VERBOSE" = true ]; then
            echo "Response: $GRAPHQL_RESPONSE"
        fi
    fi
    
    # Test simple query
    SIMPLE_QUERY='{"query":"query { hello }"}'
    
    HELLO_RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$SIMPLE_QUERY" \
        "$GRAPHQL_URL" 2>/dev/null || echo "")
    
    if echo "$HELLO_RESPONSE" | grep -q "Hello"; then
        log_success "GraphQL hello query successful"
    else
        log_warning "GraphQL hello query failed (may not be implemented)"
        if [ "$VERBOSE" = true ]; then
            echo "Response: $HELLO_RESPONSE"
        fi
    fi
}

check_security_headers() {
    log_info "Checking security headers..."
    
    if [ -z "$ALB_DNS_NAME" ]; then
        log_error "ALB DNS name not available, skipping security checks"
        return 1
    fi
    
    HEADERS=$(curl -s -I "http://$ALB_DNS_NAME/health" 2>/dev/null || echo "")
    
    # Check for security headers
    if echo "$HEADERS" | grep -qi "x-content-type-options"; then
        log_success "X-Content-Type-Options header present"
    else
        log_warning "X-Content-Type-Options header missing"
    fi
    
    if echo "$HEADERS" | grep -qi "x-frame-options"; then
        log_success "X-Frame-Options header present"
    else
        log_warning "X-Frame-Options header missing"
    fi
    
    # Check response time
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "http://$ALB_DNS_NAME/health" 2>/dev/null || echo "0")
    RESPONSE_TIME_MS=$(echo "$RESPONSE_TIME * 1000" | bc 2>/dev/null || echo "0")
    
    if [ "$(echo "$RESPONSE_TIME < 2.0" | bc 2>/dev/null || echo 0)" = "1" ]; then
        log_success "Response time: ${RESPONSE_TIME_MS}ms (good)"
    else
        log_warning "Response time: ${RESPONSE_TIME_MS}ms (slow)"
    fi
}

check_monitoring() {
    log_info "Checking monitoring and logging..."
    
    # Check CloudWatch log groups
    LOG_GROUPS=$(aws logs describe-log-groups \
        --log-group-name-prefix "/ecs/$PROJECT_NAME-$ENVIRONMENT" \
        --query 'logGroups[].logGroupName' --output text 2>/dev/null || echo "")
    
    if [ -n "$LOG_GROUPS" ]; then
        log_success "CloudWatch log groups found: $(echo "$LOG_GROUPS" | wc -w)"
    else
        log_warning "No CloudWatch log groups found"
    fi
    
    # Check recent log entries
    if [ -n "$LOG_GROUPS" ]; then
        for log_group in $LOG_GROUPS; do
            RECENT_LOGS=$(aws logs describe-log-streams \
                --log-group-name "$log_group" \
                --order-by LastEventTime \
                --descending \
                --max-items 1 \
                --query 'logStreams[0].lastEventTime' --output text 2>/dev/null || echo "0")
            
            if [ "$RECENT_LOGS" != "0" ] && [ "$RECENT_LOGS" != "None" ]; then
                LAST_LOG_TIME=$(date -d "@$((RECENT_LOGS / 1000))" 2>/dev/null || echo "unknown")
                log_success "Recent logs in $log_group: $LAST_LOG_TIME"
            else
                log_warning "No recent logs in $log_group"
            fi
        done
    fi
}

generate_report() {
    echo ""
    echo "==============================================="
    echo "         DEPLOYMENT VERIFICATION REPORT"
    echo "==============================================="
    echo "Environment: $ENVIRONMENT"
    echo "Timestamp: $(date)"
    echo ""
    echo "Test Results:"
    echo "  ✅ Passed: $TESTS_PASSED"
    echo "  ❌ Failed: $TESTS_FAILED"
    echo ""
    
    if [ $TESTS_FAILED -gt 0 ]; then
        echo "Failed Tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - $test"
        done
        echo ""
    fi
    
    if [ -n "$ALB_DNS_NAME" ]; then
        echo "Application URLs:"
        echo "  Health Check: http://$ALB_DNS_NAME/health"
        echo "  GraphQL:      http://$ALB_DNS_NAME/graphql"
        echo "  API Docs:     http://$ALB_DNS_NAME/docs"
        echo ""
    fi
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log_success "All verification tests passed! 🎉"
        echo ""
        echo "Your $ENVIRONMENT environment is ready for use."
    else
        log_error "Some verification tests failed."
        echo ""
        echo "Please review the failed tests and fix any issues before using the environment."
        exit 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
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

# Set project name based on environment
PROJECT_NAME="jobquest-navigator-v2"

# Main verification process
main() {
    log_info "Starting deployment verification for $ENVIRONMENT environment"
    echo ""
    
    check_terraform_outputs
    check_aws_infrastructure
    check_application_health
    check_graphql_endpoint
    check_security_headers
    check_monitoring
    
    generate_report
}

# Run main function
main "$@"