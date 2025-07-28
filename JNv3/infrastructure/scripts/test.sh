#!/bin/bash
# JobQuest Navigator v2 - Test Runner Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Change to project root
cd "$(dirname "$0")/.."

echo "🧪 JobQuest Navigator v2 - Test Suite"
echo "====================================="

# Parse command line arguments
BACKEND_ONLY=""
FRONTEND_ONLY=""
SHARED_ONLY=""
COVERAGE=""
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND_ONLY="true"
            shift
            ;;
        --frontend)
            FRONTEND_ONLY="true"
            shift
            ;;
        --shared)
            SHARED_ONLY="true"
            shift
            ;;
        --coverage)
            COVERAGE="true"
            shift
            ;;
        --verbose|-v)
            VERBOSE="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --backend     Run only backend tests"
            echo "  --frontend    Run only frontend tests"
            echo "  --shared      Run only shared module tests"
            echo "  --coverage    Generate coverage reports"
            echo "  --verbose, -v Verbose output"
            echo "  --help, -h    Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Test results tracking
BACKEND_RESULT=0
FRONTEND_RESULT=0
SHARED_RESULT=0

# Run backend tests
run_backend_tests() {
    print_step "Backend Tests (FastAPI + GraphQL)"
    
    cd backend-fastapi-graphql
    
    # Check if pytest is available
    if ! command -v pytest &> /dev/null; then
        print_warning "pytest not found. Installing test dependencies..."
        pip install pytest pytest-asyncio pytest-cov
    fi
    
    # Set test environment
    export TESTING=true
    export DATABASE_URL="sqlite+aiosqlite:///./test.db"
    
    print_status "Running backend tests..."
    
    if [ "$COVERAGE" = "true" ]; then
        if [ "$VERBOSE" = "true" ]; then
            pytest tests/ -v --cov=app --cov-report=html --cov-report=term
        else
            pytest tests/ --cov=app --cov-report=html --cov-report=term
        fi
    else
        if [ "$VERBOSE" = "true" ]; then
            pytest tests/ -v
        else
            pytest tests/
        fi
    fi
    
    BACKEND_RESULT=$?
    
    # Cleanup test database
    if [ -f "test.db" ]; then
        rm test.db
    fi
    
    cd ..
    
    if [ $BACKEND_RESULT -eq 0 ]; then
        print_status "Backend tests passed ✅"
    else
        print_error "Backend tests failed ❌"
    fi
}

# Run frontend tests
run_frontend_tests() {
    print_step "Frontend Tests (React + TypeScript)"
    
    cd frontend-react-minimal
    
    # Check if test script exists
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in frontend directory"
        cd ..
        return 1
    fi
    
    print_status "Running frontend tests..."
    
    if [ "$COVERAGE" = "true" ]; then
        if [ "$VERBOSE" = "true" ]; then
            npm test -- --coverage --verbose --watchAll=false
        else
            npm test -- --coverage --watchAll=false
        fi
    else
        if [ "$VERBOSE" = "true" ]; then
            npm test -- --verbose --watchAll=false
        else
            npm test -- --watchAll=false
        fi
    fi
    
    FRONTEND_RESULT=$?
    
    cd ..
    
    if [ $FRONTEND_RESULT -eq 0 ]; then
        print_status "Frontend tests passed ✅"
    else
        print_error "Frontend tests failed ❌"
    fi
}

# Run shared module tests
run_shared_tests() {
    print_step "Shared Module Tests (TypeScript)"
    
    cd shared
    
    # Check if test script exists
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in shared directory"
        cd ..
        return 1
    fi
    
    # Check if tests exist
    if [ ! -d "src/__tests__" ] && [ ! -d "tests" ]; then
        print_warning "No tests found in shared module"
        cd ..
        return 0
    fi
    
    print_status "Running shared module tests..."
    
    if [ "$COVERAGE" = "true" ]; then
        if [ "$VERBOSE" = "true" ]; then
            npm test -- --coverage --verbose
        else
            npm test -- --coverage
        fi
    else
        if [ "$VERBOSE" = "true" ]; then
            npm test -- --verbose
        else
            npm test
        fi
    fi
    
    SHARED_RESULT=$?
    
    cd ..
    
    if [ $SHARED_RESULT -eq 0 ]; then
        print_status "Shared module tests passed ✅"
    else
        print_error "Shared module tests failed ❌"
    fi
}

# Run linting
run_linting() {
    print_step "Code Quality Checks"
    
    # Backend linting
    print_status "Running backend linting..."
    cd backend-fastapi-graphql
    
    if command -v flake8 &> /dev/null; then
        flake8 app/ --max-line-length=100 || print_warning "Backend linting issues found"
    else
        print_warning "flake8 not found, skipping backend linting"
    fi
    
    if command -v black &> /dev/null; then
        black --check app/ || print_warning "Backend formatting issues found"
    else
        print_warning "black not found, skipping backend formatting check"
    fi
    
    cd ..
    
    # Frontend linting
    print_status "Running frontend linting..."
    cd frontend-react-minimal
    
    if [ -f "package.json" ]; then
        npm run lint --if-present || print_warning "Frontend linting issues found"
    fi
    
    cd ..
}

# Main execution
main() {
    if [ "$BACKEND_ONLY" = "true" ]; then
        run_backend_tests
    elif [ "$FRONTEND_ONLY" = "true" ]; then
        run_frontend_tests
    elif [ "$SHARED_ONLY" = "true" ]; then
        run_shared_tests
    else
        # Run all tests
        run_backend_tests
        run_frontend_tests
        run_shared_tests
        run_linting
    fi
    
    # Summary
    print_step "Test Summary"
    
    TOTAL_FAILURES=0
    
    if [ "$BACKEND_ONLY" != "true" ] && [ "$FRONTEND_ONLY" != "true" ] && [ "$SHARED_ONLY" != "true" ]; then
        echo "Backend Tests: $([ $BACKEND_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
        echo "Frontend Tests: $([ $FRONTEND_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
        echo "Shared Tests: $([ $SHARED_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
        
        TOTAL_FAILURES=$((BACKEND_RESULT + FRONTEND_RESULT + SHARED_RESULT))
    elif [ "$BACKEND_ONLY" = "true" ]; then
        echo "Backend Tests: $([ $BACKEND_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
        TOTAL_FAILURES=$BACKEND_RESULT
    elif [ "$FRONTEND_ONLY" = "true" ]; then
        echo "Frontend Tests: $([ $FRONTEND_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
        TOTAL_FAILURES=$FRONTEND_RESULT
    elif [ "$SHARED_ONLY" = "true" ]; then
        echo "Shared Tests: $([ $SHARED_RESULT -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
        TOTAL_FAILURES=$SHARED_RESULT
    fi
    
    if [ $TOTAL_FAILURES -eq 0 ]; then
        print_status "All tests passed! 🎉"
        exit 0
    else
        print_error "Some tests failed. Check the output above for details."
        exit 1
    fi
}

# Run main function
main "$@"