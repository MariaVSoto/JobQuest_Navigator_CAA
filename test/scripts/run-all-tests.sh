#!/bin/bash

#
# JobQuest Navigator v3 - Comprehensive Test Runner
# Executes all test suites with proper setup and cleanup
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TEST_DIR="${PROJECT_ROOT}/test"

# Default options
RUN_BACKEND=true
RUN_FRONTEND=true
RUN_E2E=true
RUN_PERFORMANCE=false
RUN_SECURITY=false
GENERATE_COVERAGE=true
PARALLEL_EXECUTION=true
VERBOSE=false
WATCH_MODE=false
TEST_ENV="test"
CLEANUP_AFTER=true

# Test results tracking
BACKEND_EXIT_CODE=0
FRONTEND_EXIT_CODE=0
E2E_EXIT_CODE=0
PERFORMANCE_EXIT_CODE=0
SECURITY_EXIT_CODE=0

# Function to display help
show_help() {
    cat << EOF
JobQuest Navigator v3 - Test Runner

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -b, --backend-only      Run only backend tests
    -f, --frontend-only     Run only frontend tests
    -e, --e2e-only          Run only end-to-end tests
    -p, --performance       Include performance tests
    -s, --security          Include security tests
    --no-coverage           Skip coverage reporting
    --no-parallel           Run tests sequentially
    -v, --verbose           Enable verbose output
    -w, --watch             Run tests in watch mode
    --env ENV               Set test environment (default: test)
    --no-cleanup            Skip cleanup after tests
    --quick                 Run quick test suite (unit tests only)
    --ci                    CI mode (optimized for CI/CD)

EXAMPLES:
    $0                      # Run all tests with coverage
    $0 --backend-only       # Run only backend tests
    $0 --quick              # Run quick test suite
    $0 --performance        # Include performance tests
    $0 --ci                 # CI mode
    $0 --watch --frontend-only  # Watch frontend tests

ENVIRONMENT VARIABLES:
    TEST_DATABASE_URL       Test database connection string
    COVERAGE_THRESHOLD      Minimum coverage threshold (default: 80)
    MAX_PARALLEL_JOBS       Maximum parallel test jobs (default: 4)
    TEST_TIMEOUT           Global test timeout in seconds (default: 300)

EOF
}

# Function to log with colors
log() {
    local level=$1
    shift
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")  echo -e "${CYAN}[INFO]${NC} ${timestamp} - $*" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} ${timestamp} - $*" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${timestamp} - $*" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - $*" ;;
        "DEBUG") [[ $VERBOSE == true ]] && echo -e "${PURPLE}[DEBUG]${NC} ${timestamp} - $*" ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "${PROJECT_ROOT}/test/README.md" ]]; then
        log "ERROR" "Test directory not found. Please run from project root."
        exit 1
    fi
    
    # Check required tools
    local missing_tools=()
    
    if [[ $RUN_BACKEND == true ]]; then
        command -v python3 >/dev/null 2>&1 || missing_tools+=("python3")
        command -v pytest >/dev/null 2>&1 || missing_tools+=("pytest")
    fi
    
    if [[ $RUN_FRONTEND == true ]]; then
        command -v node >/dev/null 2>&1 || missing_tools+=("node")
        command -v npm >/dev/null 2>&1 || missing_tools+=("npm")
    fi
    
    if [[ $RUN_E2E == true ]]; then
        command -v npx >/dev/null 2>&1 || missing_tools+=("npx")
    fi
    
    if [[ $GENERATE_COVERAGE == true ]]; then
        command -v coverage >/dev/null 2>&1 || log "WARN" "Coverage tool not found, installing..."
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log "ERROR" "Missing required tools: ${missing_tools[*]}"
        log "INFO" "Please install missing tools and try again."
        exit 1
    fi
    
    log "SUCCESS" "Prerequisites check passed"
}

# Function to setup test environment
setup_test_environment() {
    log "INFO" "Setting up test environment..."
    
    # Create necessary directories
    mkdir -p "${TEST_DIR}/reports/coverage"
    mkdir -p "${TEST_DIR}/reports/backend"
    mkdir -p "${TEST_DIR}/reports/frontend"
    mkdir -p "${TEST_DIR}/reports/e2e"
    mkdir -p "${TEST_DIR}/reports/performance"
    mkdir -p "${TEST_DIR}/reports/security"
    
    # Set environment variables
    export NODE_ENV=$TEST_ENV
    export PYTHONPATH="${PROJECT_ROOT}/JNv3/apps/backend-fastapi:${PYTHONPATH}"
    export TEST_DATABASE_URL="${TEST_DATABASE_URL:-postgresql://test:test@localhost:5433/test_jobquest}"
    export COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-80}"
    export MAX_PARALLEL_JOBS="${MAX_PARALLEL_JOBS:-4}"
    export TEST_TIMEOUT="${TEST_TIMEOUT:-300}"
    
    # Setup test database if needed
    if [[ $RUN_BACKEND == true ]]; then
        log "INFO" "Setting up test database..."
        "${SCRIPT_DIR}/setup-test-env.sh" --database-only
    fi
    
    log "SUCCESS" "Test environment setup completed"
}

# Function to run backend tests
run_backend_tests() {
    if [[ $RUN_BACKEND != true ]]; then
        return 0
    fi
    
    log "INFO" "Running backend tests..."
    
    local pytest_args=(
        "--config-file=${TEST_DIR}/config/pytest.ini"
        "--rootdir=${PROJECT_ROOT}"
        "--tb=short"
    )
    
    if [[ $GENERATE_COVERAGE == true ]]; then
        pytest_args+=(
            "--cov=app"
            "--cov-report=html:${TEST_DIR}/reports/coverage/backend/html"
            "--cov-report=xml:${TEST_DIR}/reports/coverage/backend/coverage.xml"
            "--cov-report=term-missing"
            "--cov-fail-under=${COVERAGE_THRESHOLD}"
        )
    fi
    
    if [[ $PARALLEL_EXECUTION == true ]]; then
        pytest_args+=("-n" "$MAX_PARALLEL_JOBS")
    fi
    
    if [[ $VERBOSE == true ]]; then
        pytest_args+=("-v")
    fi
    
    if [[ $WATCH_MODE == true ]]; then
        pytest_args+=("-f")
    fi
    
    # Add test paths
    pytest_args+=(
        "${TEST_DIR}/backend/unit"
        "${TEST_DIR}/backend/integration"
        "${TEST_DIR}/backend/graphql"
    )
    
    # Run tests
    cd "${PROJECT_ROOT}/JNv3/apps/backend-fastapi"
    
    if python -m pytest "${pytest_args[@]}"; then
        log "SUCCESS" "Backend tests passed"
        BACKEND_EXIT_CODE=0
    else
        log "ERROR" "Backend tests failed"
        BACKEND_EXIT_CODE=1
    fi
    
    cd "${PROJECT_ROOT}"
}

# Function to run frontend tests
run_frontend_tests() {
    if [[ $RUN_FRONTEND != true ]]; then
        return 0
    fi
    
    log "INFO" "Running frontend tests..."
    
    cd "${PROJECT_ROOT}/JNv3/apps/frontend-react"
    
    local npm_args=()
    
    if [[ $GENERATE_COVERAGE == true ]]; then
        npm_args+=("--coverage" "--watchAll=false")
    fi
    
    if [[ $WATCH_MODE == true ]]; then
        npm_args+=("--watchAll")
    fi
    
    if [[ $VERBOSE == true ]]; then
        npm_args+=("--verbose")
    fi
    
    # Set test configuration
    export JEST_CONFIG="${TEST_DIR}/config/jest.config.js"
    
    # Run tests
    if [[ $WATCH_MODE == true ]]; then
        npm test -- "${npm_args[@]}"
        FRONTEND_EXIT_CODE=$?
    else
        npm run test:ci -- "${npm_args[@]}"
        FRONTEND_EXIT_CODE=$?
    fi
    
    if [[ $FRONTEND_EXIT_CODE -eq 0 ]]; then
        log "SUCCESS" "Frontend tests passed"
    else
        log "ERROR" "Frontend tests failed"
    fi
    
    cd "${PROJECT_ROOT}"
}

# Function to run E2E tests
run_e2e_tests() {
    if [[ $RUN_E2E != true ]]; then
        return 0
    fi
    
    log "INFO" "Running end-to-end tests..."
    
    # Start test services if not running
    log "INFO" "Starting test services..."
    "${SCRIPT_DIR}/setup-test-env.sh" --services-only
    
    # Wait for services to be ready
    log "INFO" "Waiting for services to be ready..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health >/dev/null 2>&1; do sleep 2; done'
    timeout 60 bash -c 'until curl -f http://localhost:3000 >/dev/null 2>&1; do sleep 2; done'
    
    # Run Playwright tests
    cd "${PROJECT_ROOT}"
    
    local playwright_args=(
        "--config=${TEST_DIR}/config/playwright.config.js"
    )
    
    if [[ $PARALLEL_EXECUTION == true ]]; then
        playwright_args+=("--workers=$MAX_PARALLEL_JOBS")
    fi
    
    if [[ $VERBOSE == true ]]; then
        playwright_args+=("--reporter=line")
    fi
    
    if npx playwright test "${playwright_args[@]}"; then
        log "SUCCESS" "E2E tests passed"
        E2E_EXIT_CODE=0
    else
        log "ERROR" "E2E tests failed"
        E2E_EXIT_CODE=1
    fi
}

# Function to run performance tests
run_performance_tests() {
    if [[ $RUN_PERFORMANCE != true ]]; then
        return 0
    fi
    
    log "INFO" "Running performance tests..."
    
    cd "${PROJECT_ROOT}"
    
    # Run backend performance tests
    if python -m pytest "${TEST_DIR}/backend/performance" -v --tb=short; then
        log "SUCCESS" "Backend performance tests passed"
    else
        log "ERROR" "Backend performance tests failed"
        PERFORMANCE_EXIT_CODE=1
    fi
    
    # Run frontend performance tests
    if npm run test:performance --prefix "${PROJECT_ROOT}/JNv3/apps/frontend-react"; then
        log "SUCCESS" "Frontend performance tests passed"
    else
        log "ERROR" "Frontend performance tests failed"
        PERFORMANCE_EXIT_CODE=1
    fi
}

# Function to run security tests
run_security_tests() {
    if [[ $RUN_SECURITY != true ]]; then
        return 0
    fi
    
    log "INFO" "Running security tests..."
    
    cd "${PROJECT_ROOT}"
    
    # Run backend security tests
    if python -m pytest "${TEST_DIR}/backend/security" -v --tb=short; then
        log "SUCCESS" "Backend security tests passed"
    else
        log "ERROR" "Backend security tests failed"
        SECURITY_EXIT_CODE=1
    fi
    
    # Run security scans
    if [[ -x "${SCRIPT_DIR}/run-security-tests.sh" ]]; then
        "${SCRIPT_DIR}/run-security-tests.sh" --quick
        SECURITY_EXIT_CODE=$?
    fi
}

# Function to generate test reports
generate_reports() {
    if [[ $GENERATE_COVERAGE != true ]]; then
        return 0
    fi
    
    log "INFO" "Generating test reports..."
    
    # Merge coverage reports
    if [[ -f "${TEST_DIR}/reports/coverage/backend/coverage.xml" ]] && [[ -f "${TEST_DIR}/reports/coverage/frontend/coverage-final.json" ]]; then
        log "INFO" "Merging coverage reports..."
        # Custom script to merge different coverage formats
        python "${SCRIPT_DIR}/../shared/utils/merge-coverage.py" \
            --backend "${TEST_DIR}/reports/coverage/backend/coverage.xml" \
            --frontend "${TEST_DIR}/reports/coverage/frontend/coverage-final.json" \
            --output "${TEST_DIR}/reports/coverage/merged-coverage.json"
    fi
    
    # Generate HTML report
    if command -v coverage >/dev/null 2>&1; then
        coverage html -d "${TEST_DIR}/reports/coverage/html"
    fi
    
    # Generate test summary
    cat > "${TEST_DIR}/reports/test-summary.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "results": {
    "backend": {
      "exitCode": $BACKEND_EXIT_CODE,
      "passed": $([ $BACKEND_EXIT_CODE -eq 0 ] && echo "true" || echo "false")
    },
    "frontend": {
      "exitCode": $FRONTEND_EXIT_CODE,
      "passed": $([ $FRONTEND_EXIT_CODE -eq 0 ] && echo "true" || echo "false")
    },
    "e2e": {
      "exitCode": $E2E_EXIT_CODE,
      "passed": $([ $E2E_EXIT_CODE -eq 0 ] && echo "true" || echo "false")
    },
    "performance": {
      "exitCode": $PERFORMANCE_EXIT_CODE,
      "passed": $([ $PERFORMANCE_EXIT_CODE -eq 0 ] && echo "true" || echo "false")
    },
    "security": {
      "exitCode": $SECURITY_EXIT_CODE,
      "passed": $([ $SECURITY_EXIT_CODE -eq 0 ] && echo "true" || echo "false")
    }
  },
  "coverage": {
    "backend": "$(grep -o 'TOTAL.*[0-9]*%' "${TEST_DIR}/reports/coverage/backend/coverage.xml" 2>/dev/null || echo 'N/A')",
    "frontend": "$(grep -o '"total".*"pct":[0-9.]*' "${TEST_DIR}/reports/coverage/frontend/coverage-final.json" 2>/dev/null || echo 'N/A')"
  }
}
EOF
    
    log "SUCCESS" "Test reports generated"
}

# Function to cleanup test environment
cleanup_test_environment() {
    if [[ $CLEANUP_AFTER != true ]]; then
        return 0
    fi
    
    log "INFO" "Cleaning up test environment..."
    
    # Stop test services
    "${SCRIPT_DIR}/cleanup-test-env.sh" --quiet
    
    # Clean temporary files
    find "${TEST_DIR}" -name "*.pyc" -delete 2>/dev/null || true
    find "${TEST_DIR}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "${TEST_DIR}" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log "SUCCESS" "Cleanup completed"
}

# Function to display test summary
display_summary() {
    echo
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}       TEST EXECUTION SUMMARY        ${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo
    
    # Backend results
    if [[ $RUN_BACKEND == true ]]; then
        if [[ $BACKEND_EXIT_CODE -eq 0 ]]; then
            echo -e "Backend Tests:    ${GREEN}✓ PASSED${NC}"
        else
            echo -e "Backend Tests:    ${RED}✗ FAILED${NC}"
        fi
    fi
    
    # Frontend results
    if [[ $RUN_FRONTEND == true ]]; then
        if [[ $FRONTEND_EXIT_CODE -eq 0 ]]; then
            echo -e "Frontend Tests:   ${GREEN}✓ PASSED${NC}"
        else
            echo -e "Frontend Tests:   ${RED}✗ FAILED${NC}"
        fi
    fi
    
    # E2E results
    if [[ $RUN_E2E == true ]]; then
        if [[ $E2E_EXIT_CODE -eq 0 ]]; then
            echo -e "E2E Tests:        ${GREEN}✓ PASSED${NC}"
        else
            echo -e "E2E Tests:        ${RED}✗ FAILED${NC}"
        fi
    fi
    
    # Performance results
    if [[ $RUN_PERFORMANCE == true ]]; then
        if [[ $PERFORMANCE_EXIT_CODE -eq 0 ]]; then
            echo -e "Performance:      ${GREEN}✓ PASSED${NC}"
        else
            echo -e "Performance:      ${RED}✗ FAILED${NC}"
        fi
    fi
    
    # Security results
    if [[ $RUN_SECURITY == true ]]; then
        if [[ $SECURITY_EXIT_CODE -eq 0 ]]; then
            echo -e "Security:         ${GREEN}✓ PASSED${NC}"
        else
            echo -e "Security:         ${RED}✗ FAILED${NC}"
        fi
    fi
    
    echo
    
    # Coverage information
    if [[ $GENERATE_COVERAGE == true ]]; then
        echo -e "${CYAN}Coverage Reports:${NC}"
        echo "  Backend:  ${TEST_DIR}/reports/coverage/backend/html/index.html"
        echo "  Frontend: ${TEST_DIR}/reports/coverage/frontend/lcov-report/index.html"
        echo "  Merged:   ${TEST_DIR}/reports/coverage/html/index.html"
        echo
    fi
    
    # Overall result
    local overall_exit_code=$((BACKEND_EXIT_CODE + FRONTEND_EXIT_CODE + E2E_EXIT_CODE + PERFORMANCE_EXIT_CODE + SECURITY_EXIT_CODE))
    
    if [[ $overall_exit_code -eq 0 ]]; then
        echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
        echo
        return 0
    else
        echo -e "${RED}❌ SOME TESTS FAILED ❌${NC}"
        echo
        return 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -b|--backend-only)
            RUN_BACKEND=true
            RUN_FRONTEND=false
            RUN_E2E=false
            shift
            ;;
        -f|--frontend-only)
            RUN_BACKEND=false
            RUN_FRONTEND=true
            RUN_E2E=false
            shift
            ;;
        -e|--e2e-only)
            RUN_BACKEND=false
            RUN_FRONTEND=false
            RUN_E2E=true
            shift
            ;;
        -p|--performance)
            RUN_PERFORMANCE=true
            shift
            ;;
        -s|--security)
            RUN_SECURITY=true
            shift
            ;;
        --no-coverage)
            GENERATE_COVERAGE=false
            shift
            ;;
        --no-parallel)
            PARALLEL_EXECUTION=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -w|--watch)
            WATCH_MODE=true
            shift
            ;;
        --env)
            TEST_ENV="$2"
            shift 2
            ;;
        --no-cleanup)
            CLEANUP_AFTER=false
            shift
            ;;
        --quick)
            RUN_E2E=false
            RUN_PERFORMANCE=false
            RUN_SECURITY=false
            shift
            ;;
        --ci)
            PARALLEL_EXECUTION=true
            VERBOSE=false
            WATCH_MODE=false
            CLEANUP_AFTER=true
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   JobQuest Navigator v3 Test Runner   ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
    
    # Setup trap for cleanup
    trap cleanup_test_environment EXIT
    
    # Execute test pipeline
    check_prerequisites
    setup_test_environment
    
    # Run tests based on configuration
    run_backend_tests
    run_frontend_tests
    run_e2e_tests
    run_performance_tests
    run_security_tests
    
    # Generate reports
    generate_reports
    
    # Display summary and exit with appropriate code
    if display_summary; then
        exit 0
    else
        exit 1
    fi
}

# Execute main function
main "$@"