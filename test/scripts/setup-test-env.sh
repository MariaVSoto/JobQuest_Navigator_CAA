#!/bin/bash

# JobQuest Navigator v3 - Test Environment Setup Script
# This script sets up the test environment for running tests

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
TEST_ENV=${TEST_ENV:-test}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
TEST_ROOT="${PROJECT_ROOT}/test"

# Create test directories if they don't exist
create_test_directories() {
    log_info "Creating test directories..."
    
    local dirs=(
        "${TEST_ROOT}/reports"
        "${TEST_ROOT}/reports/backend"
        "${TEST_ROOT}/reports/frontend"
        "${TEST_ROOT}/reports/e2e"
        "${TEST_ROOT}/reports/performance"
        "${TEST_ROOT}/reports/security"
        "${TEST_ROOT}/reports/coverage"
        "${TEST_ROOT}/logs"
        "${TEST_ROOT}/tmp"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done
    
    log_success "Test directories created successfully"
}

# Setup test database
setup_test_database() {
    log_info "Setting up test database..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if test containers are running
    if docker-compose -f "${PROJECT_ROOT}/JNv3/infrastructure/docker/docker-compose.yml" ps | grep -q "db"; then
        log_info "Test database container is already running"
    else
        log_info "Starting test database container..."
        cd "${PROJECT_ROOT}/JNv3/infrastructure/docker"
        docker-compose up -d db
        sleep 5  # Wait for database to be ready
    fi
    
    log_success "Test database setup completed"
}

# Install test dependencies
install_test_dependencies() {
    log_info "Installing test dependencies..."
    
    # Backend dependencies
    if [ -f "${PROJECT_ROOT}/JNv3/apps/backend-fastapi/requirements-test.txt" ]; then
        log_info "Installing backend test dependencies..."
        cd "${PROJECT_ROOT}/JNv3/apps/backend-fastapi"
        pip install -q -r requirements-test.txt
    else
        log_warning "Backend test requirements file not found"
    fi
    
    # Frontend dependencies
    if [ -f "${PROJECT_ROOT}/JNv3/apps/frontend-react/package.json" ]; then
        log_info "Installing frontend test dependencies..."
        cd "${PROJECT_ROOT}/JNv3/apps/frontend-react"
        npm install --silent
    else
        log_warning "Frontend package.json not found"
    fi
    
    # E2E test dependencies
    if [ -f "${TEST_ROOT}/e2e/package.json" ]; then
        log_info "Installing E2E test dependencies..."
        cd "${TEST_ROOT}/e2e"
        npm install --silent
        npx playwright install --with-deps chromium firefox webkit
    else
        log_warning "E2E test package.json not found"
    fi
    
    log_success "Test dependencies installed successfully"
}

# Setup test environment variables
setup_test_env_vars() {
    log_info "Setting up test environment variables..."
    
    # Export test environment variables
    export NODE_ENV=test
    export DJANGO_SETTINGS_MODULE=core.settings_test
    export TEST_DATABASE_URL=${TEST_DATABASE_URL:-"postgresql://postgres:password@localhost:5432/jobquest_test"}
    export COVERAGE_THRESHOLD=${COVERAGE_THRESHOLD:-80}
    export MAX_PARALLEL_JOBS=${MAX_PARALLEL_JOBS:-4}
    export TEST_TIMEOUT=${TEST_TIMEOUT:-300}
    
    # Create test environment file
    cat > "${TEST_ROOT}/.env.test" << EOF
# Test Environment Configuration
NODE_ENV=test
DJANGO_SETTINGS_MODULE=core.settings_test
TEST_DATABASE_URL=${TEST_DATABASE_URL}
COVERAGE_THRESHOLD=${COVERAGE_THRESHOLD}
MAX_PARALLEL_JOBS=${MAX_PARALLEL_JOBS}
TEST_TIMEOUT=${TEST_TIMEOUT}

# Test API Keys (mock values)
ADZUNA_API_ID=test_api_id
ADZUNA_API_KEY=test_api_key
OPENAI_API_KEY=test_openai_key
GOOGLE_MAPS_API_KEY=test_google_maps_key

# Test Database Configuration
DATABASE_URL=sqlite:///:memory:
REDIS_URL=redis://localhost:6379/1

# Test Storage Configuration
USE_MINIO=true
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET_NAME=jobquest-test

# Test Email Configuration
EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend

# Test Security Settings
SECRET_KEY=test-secret-key-for-testing-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Test GraphQL Settings
GRAPHQL_DEBUG=True
GRAPHQL_PLAYGROUND=True
EOF
    
    log_success "Test environment variables configured"
}

# Cleanup previous test artifacts
cleanup_previous_tests() {
    log_info "Cleaning up previous test artifacts..."
    
    # Remove old test reports
    rm -rf "${TEST_ROOT}/reports/"*
    rm -rf "${TEST_ROOT}/logs/"*
    rm -rf "${TEST_ROOT}/tmp/"*
    
    # Remove old coverage files
    find "${PROJECT_ROOT}" -name ".coverage" -type f -delete
    find "${PROJECT_ROOT}" -name "coverage.xml" -type f -delete
    find "${PROJECT_ROOT}" -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Remove Jest cache
    if [ -d "${PROJECT_ROOT}/frontend/node_modules/.cache" ]; then
        rm -rf "${PROJECT_ROOT}/frontend/node_modules/.cache"
    fi
    
    # Remove Playwright artifacts
    rm -rf "${TEST_ROOT}/e2e/test-results"
    rm -rf "${TEST_ROOT}/e2e/playwright-report"
    
    log_success "Previous test artifacts cleaned up"
}

# Validate test environment
validate_test_environment() {
    log_info "Validating test environment..."
    
    local errors=0
    
    # Check Python and pip
    if ! command -v python &> /dev/null; then
        log_error "Python is not installed or not in PATH"
        ((errors++))
    fi
    
    if ! command -v pip &> /dev/null; then
        log_error "pip is not installed or not in PATH"
        ((errors++))
    fi
    
    # Check Node.js and npm
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed or not in PATH"
        ((errors++))
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed or not in PATH"
        ((errors++))
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        ((errors++))
    fi
    
    if [ $errors -gt 0 ]; then
        log_error "Test environment validation failed with $errors errors"
        exit 1
    fi
    
    log_success "Test environment validation passed"
}

# Main setup function
main() {
    log_info "Starting test environment setup..."
    
    validate_test_environment
    cleanup_previous_tests
    create_test_directories
    setup_test_env_vars
    install_test_dependencies
    setup_test_database
    
    log_success "Test environment setup completed successfully!"
    
    # Display environment info
    echo ""
    echo "Test Environment Information:"
    echo "  Project Root: ${PROJECT_ROOT}"
    echo "  Test Root: ${TEST_ROOT}"
    echo "  Environment: ${TEST_ENV}"
    echo "  Database URL: ${TEST_DATABASE_URL}"
    echo "  Coverage Threshold: ${COVERAGE_THRESHOLD}%"
    echo "  Max Parallel Jobs: ${MAX_PARALLEL_JOBS}"
    echo "  Test Timeout: ${TEST_TIMEOUT}s"
    echo ""
}

# Run main function
main "$@"