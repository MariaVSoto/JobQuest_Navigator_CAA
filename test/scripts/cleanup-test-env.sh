#!/bin/bash

# JobQuest Navigator v3 - Test Environment Cleanup Script
# This script cleans up the test environment after running tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Default values
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
TEST_ROOT="${PROJECT_ROOT}/test"
KEEP_REPORTS=${KEEP_REPORTS:-false}
KEEP_LOGS=${KEEP_LOGS:-false}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-reports)
            KEEP_REPORTS=true
            shift
            ;;
        --keep-logs)
            KEEP_LOGS=true
            shift
            ;;
        --keep-all)
            KEEP_REPORTS=true
            KEEP_LOGS=true
            shift
            ;;
        -h|--help)
            echo "Test Environment Cleanup Script"
            echo ""
            echo "USAGE:"
            echo "    $0 [OPTIONS]"
            echo ""
            echo "OPTIONS:"
            echo "    --keep-reports    Keep test reports after cleanup"
            echo "    --keep-logs      Keep test logs after cleanup"
            echo "    --keep-all       Keep all artifacts after cleanup"
            echo "    -h, --help       Show this help message"
            echo ""
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Stop test containers
stop_test_containers() {
    log_info "Stopping test containers..."
    
    if command -v docker-compose &> /dev/null; then
        cd "${PROJECT_ROOT}/JNv3/infrastructure/docker"
        
        # Stop test-specific containers
        docker-compose stop db redis minio 2>/dev/null || true
        
        # Remove test containers if they exist
        docker-compose rm -f db redis minio 2>/dev/null || true
        
        log_success "Test containers stopped"
    else
        log_warning "Docker Compose not found, skipping container cleanup"
    fi
}

# Kill test processes
kill_test_processes() {
    log_info "Killing test processes..."
    
    # Kill any remaining test processes
    pkill -f "pytest" 2>/dev/null || true
    pkill -f "jest" 2>/dev/null || true
    pkill -f "playwright" 2>/dev/null || true
    pkill -f "locust" 2>/dev/null || true
    
    # Kill any remaining Node.js test processes
    pkill -f "node.*test" 2>/dev/null || true
    
    # Kill any Django test server processes
    pkill -f "django.*runserver.*test" 2>/dev/null || true
    
    log_success "Test processes terminated"
}

# Cleanup test artifacts
cleanup_test_artifacts() {
    log_info "Cleaning up test artifacts..."
    
    # Remove temporary test files
    if [ -d "${TEST_ROOT}/tmp" ]; then
        rm -rf "${TEST_ROOT}/tmp/"*
        log_info "Temporary test files removed"
    fi
    
    # Remove test database files
    find "${PROJECT_ROOT}" -name "test*.db" -type f -delete 2>/dev/null || true
    find "${PROJECT_ROOT}" -name "*.db-journal" -type f -delete 2>/dev/null || true
    
    # Remove Python cache files
    find "${PROJECT_ROOT}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "${PROJECT_ROOT}" -name "*.pyc" -type f -delete 2>/dev/null || true
    find "${PROJECT_ROOT}" -name "*.pyo" -type f -delete 2>/dev/null || true
    
    # Remove Node.js cache files
    if [ -d "${PROJECT_ROOT}/frontend/node_modules/.cache" ]; then
        rm -rf "${PROJECT_ROOT}/frontend/node_modules/.cache"
    fi
    
    if [ -d "${TEST_ROOT}/e2e/node_modules/.cache" ]; then
        rm -rf "${TEST_ROOT}/e2e/node_modules/.cache"
    fi
    
    # Remove Jest cache
    find "${PROJECT_ROOT}" -name ".jest" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Remove coverage files if not keeping reports
    if [ "$KEEP_REPORTS" != "true" ]; then
        find "${PROJECT_ROOT}" -name ".coverage" -type f -delete 2>/dev/null || true
        find "${PROJECT_ROOT}" -name "coverage.xml" -type f -delete 2>/dev/null || true
        find "${PROJECT_ROOT}" -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
        find "${PROJECT_ROOT}" -name ".nyc_output" -type d -exec rm -rf {} + 2>/dev/null || true
    fi
    
    # Remove Playwright artifacts
    rm -rf "${TEST_ROOT}/e2e/test-results" 2>/dev/null || true
    if [ "$KEEP_REPORTS" != "true" ]; then
        rm -rf "${TEST_ROOT}/e2e/playwright-report" 2>/dev/null || true
    fi
    
    # Remove performance test artifacts
    rm -rf "${TEST_ROOT}/performance/locust_reports" 2>/dev/null || true
    
    log_success "Test artifacts cleaned up"
}

# Cleanup test reports
cleanup_test_reports() {
    if [ "$KEEP_REPORTS" != "true" ]; then
        log_info "Cleaning up test reports..."
        
        rm -rf "${TEST_ROOT}/reports/"* 2>/dev/null || true
        
        log_success "Test reports cleaned up"
    else
        log_info "Keeping test reports as requested"
    fi
}

# Cleanup test logs
cleanup_test_logs() {
    if [ "$KEEP_LOGS" != "true" ]; then
        log_info "Cleaning up test logs..."
        
        rm -rf "${TEST_ROOT}/logs/"* 2>/dev/null || true
        
        # Remove application logs from test runs
        rm -rf "${PROJECT_ROOT}/backend/logs/test_*.log" 2>/dev/null || true
        rm -rf "${PROJECT_ROOT}/frontend/logs/test_*.log" 2>/dev/null || true
        
        log_success "Test logs cleaned up"
    else
        log_info "Keeping test logs as requested"
    fi
}

# Cleanup test environment variables
cleanup_test_env_vars() {
    log_info "Cleaning up test environment variables..."
    
    # Remove test environment file
    rm -f "${TEST_ROOT}/.env.test" 2>/dev/null || true
    
    # Unset test environment variables
    unset NODE_ENV
    unset DJANGO_SETTINGS_MODULE
    unset TEST_DATABASE_URL
    unset COVERAGE_THRESHOLD
    unset MAX_PARALLEL_JOBS
    unset TEST_TIMEOUT
    
    log_success "Test environment variables cleaned up"
}

# Cleanup test network interfaces
cleanup_test_network() {
    log_info "Cleaning up test network interfaces..."
    
    if command -v docker &> /dev/null; then
        # Remove test Docker networks
        docker network ls --filter name=test --format "{{.Name}}" | xargs -r docker network rm 2>/dev/null || true
        
        # Prune unused Docker networks
        docker network prune -f 2>/dev/null || true
        
        log_success "Test network interfaces cleaned up"
    else
        log_warning "Docker not found, skipping network cleanup"
    fi
}

# Reset test database
reset_test_database() {
    log_info "Resetting test database..."
    
    # Drop test databases if they exist
    if command -v psql &> /dev/null; then
        PGPASSWORD=password psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS jobquest_test;" 2>/dev/null || true
        PGPASSWORD=password psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS jobquest_test_performance;" 2>/dev/null || true
    fi
    
    # Remove SQLite test databases
    find "${PROJECT_ROOT}" -name "test*.sqlite*" -type f -delete 2>/dev/null || true
    
    log_success "Test database reset completed"
}

# Generate cleanup summary
generate_cleanup_summary() {
    log_info "Generating cleanup summary..."
    
    local summary_file="${TEST_ROOT}/cleanup-summary.txt"
    
    cat > "$summary_file" << EOF
JobQuest Navigator v3 - Test Environment Cleanup Summary
========================================================

Cleanup Date: $(date)
Project Root: ${PROJECT_ROOT}
Test Root: ${TEST_ROOT}

Actions Performed:
- Test containers stopped and removed
- Test processes terminated
- Test artifacts cleaned up
- Test database reset
- Network interfaces cleaned up
- Environment variables cleared

Artifacts Kept:
- Reports: $([ "$KEEP_REPORTS" = "true" ] && echo "Yes" || echo "No")
- Logs: $([ "$KEEP_LOGS" = "true" ] && echo "Yes" || echo "No")

Cleanup Status: SUCCESS
EOF
    
    log_success "Cleanup summary generated: $summary_file"
}

# Main cleanup function
main() {
    log_info "Starting test environment cleanup..."
    
    kill_test_processes
    stop_test_containers
    cleanup_test_artifacts
    cleanup_test_reports
    cleanup_test_logs
    cleanup_test_env_vars
    reset_test_database
    cleanup_test_network
    generate_cleanup_summary
    
    log_success "Test environment cleanup completed successfully!"
    
    # Display cleanup summary
    echo ""
    echo "Cleanup Summary:"
    echo "  Reports kept: $([ "$KEEP_REPORTS" = "true" ] && echo "Yes" || echo "No")"
    echo "  Logs kept: $([ "$KEEP_LOGS" = "true" ] && echo "Yes" || echo "No")"
    echo "  Cleanup completed at: $(date)"
    echo ""
    
    if [ "$KEEP_REPORTS" = "true" ] || [ "$KEEP_LOGS" = "true" ]; then
        echo "Note: Some artifacts were preserved as requested."
        echo "Use 'rm -rf ${TEST_ROOT}/{reports,logs}' to remove them manually."
        echo ""
    fi
}

# Run main function
main "$@"