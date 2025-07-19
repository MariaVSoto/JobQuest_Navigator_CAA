#!/bin/bash

# JobQuest Navigator - Local Docker Environment Startup Script

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

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  JobQuest Navigator - Local Environment"
    echo "=============================================="
    echo -e "${NC}"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    print_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if command -v docker-compose &> /dev/null; then
        COMPOSE_COMMAND="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_COMMAND="docker compose"
    else
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    print_success "Docker Compose is available: $COMPOSE_COMMAND"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p ../../backend/logs
    mkdir -p ../../backend/media
    mkdir -p ../../backend/staticfiles
    print_success "Directories created"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://jobquest_user:jobquest_password@database:5432/jobquest_navigator
POSTGRES_DB=jobquest_navigator
POSTGRES_USER=jobquest_user
POSTGRES_PASSWORD=jobquest_password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Django Configuration
SECRET_KEY=django-insecure-local-development-key-change-in-production
DEBUG=1
DJANGO_SETTINGS_MODULE=core.settings_docker
ALLOWED_HOSTS=localhost,127.0.0.1,backend,0.0.0.0

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80

# React Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# Email Configuration (using MailHog)
USE_MAILHOG=1

# MinIO Configuration (S3-compatible storage)
USE_MINIO=1
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET_NAME=jobquest-resumes

# AI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here
EOF
        print_success ".env file created"
    else
        print_warning ".env file already exists"
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTION] [--with-storage] [--with-email] [--with-monitoring]"
    echo ""
    echo "Options:"
    echo "  --dev, -d        Start development environment with hot reload"
    echo "  --prod, -p       Start production-like environment"
    echo "  --full, -f       Start full environment with all services"
    echo "  --minimal, -m    Start minimal environment (database, backend, frontend only)"
    echo "  --with-storage   Add MinIO S3-compatible storage service"
    echo "  --with-localstack Add LocalStack AWS services emulation"
    echo "  --with-email     Add MailHog email testing service"
    echo "  --with-monitoring Add Prometheus and Grafana monitoring"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --dev --with-storage      Start dev environment with MinIO"
    echo "  $0 --dev --with-localstack   Start dev environment with LocalStack AWS"
    echo "  $0 --prod --with-email       Start prod environment with email testing"
    echo "  $0 --full                    Start all services"
    echo ""
    echo "Available profiles:"
    echo "  default          Core services (database, redis, backend, frontend)"
    echo "  proxy            Add nginx proxy"
    echo "  email            Add mailhog for email testing"
    echo "  storage          Add MinIO for S3-compatible storage"
    echo "  localstack       Add LocalStack for AWS services emulation"
    echo "  search           Add Elasticsearch for search functionality"
    echo "  monitoring       Add Prometheus and Grafana for monitoring"
    echo "  devtools         Add development tools container"
}

# Start services based on mode
start_services() {
    local mode=$1
    shift  # Remove first argument (mode)
    local extra_profiles=""
    
    # Parse additional flags
    while [[ $# -gt 0 ]]; do
        case $1 in
            --with-storage)
                extra_profiles="$extra_profiles --profile storage"
                print_status "Including MinIO storage service"
                ;;
            --with-localstack)
                extra_profiles="$extra_profiles --profile localstack"
                print_status "Including LocalStack AWS services emulation"
                ;;
            --with-email)
                extra_profiles="$extra_profiles --profile email"
                print_status "Including MailHog email service"
                ;;
            --with-monitoring)
                extra_profiles="$extra_profiles --profile monitoring"
                print_status "Including monitoring services"
                ;;
        esac
        shift
    done
    
    print_status "Starting JobQuest Navigator in $mode mode..."
    
    case $mode in
        "dev")
            print_status "Starting development environment with hot reload..."
            if [ -f docker-compose.dev.yml ]; then
                $COMPOSE_COMMAND -f docker-compose.yml -f docker-compose.dev.yml $extra_profiles up --build -d
            else
                $COMPOSE_COMMAND -f docker-compose.yml $extra_profiles up --build -d
            fi
            ;;
        "prod")
            print_status "Starting production-like environment..."
            $COMPOSE_COMMAND -f docker-compose.yml --profile proxy $extra_profiles up --build -d
            ;;
        "full")
            print_status "Starting full environment with all services..."
            $COMPOSE_COMMAND -f docker-compose.yml --profile proxy --profile email --profile storage --profile localstack --profile monitoring up --build -d
            ;;
        "minimal")
            print_status "Starting minimal environment..."
            $COMPOSE_COMMAND -f docker-compose.yml up database redis backend frontend --build -d
            ;;
        *)
            print_status "Starting default environment..."
            $COMPOSE_COMMAND -f docker-compose.yml $extra_profiles up --build -d
            ;;
    esac
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_services_health
}

# Check if services are healthy
check_services_health() {
    print_status "Checking service health..."
    
    # Check database
    if $COMPOSE_COMMAND ps database | grep -q "healthy\|Up"; then
        print_success "Database is running"
    else
        print_warning "Database may not be ready yet"
    fi
    
    # Check backend
    if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
        print_success "Backend API is responding"
    else
        print_warning "Backend API is not responding yet (this is normal for first startup)"
    fi
    
    # Check frontend - adjust port based on mode
    local frontend_port="3000"
    if [[ -f docker-compose.dev.yml ]] && [[ "$MODE" == "dev" ]]; then
        frontend_port="3002"
    fi
    
    if curl -s http://localhost:${frontend_port}/ > /dev/null 2>&1; then
        print_success "Frontend is responding"
    else
        print_warning "Frontend is not responding yet"
    fi
}

# Show service URLs
show_services() {
    print_success "JobQuest Navigator is starting up!"
    echo ""
    echo "Service URLs:"
    echo "─────────────"
    
    # Determine frontend port based on mode
    local frontend_port="3000"
    if [[ -f docker-compose.dev.yml ]] && [[ "$MODE" == "dev" ]]; then
        frontend_port="3002"
    fi
    
    echo "🌐 Frontend:           http://localhost:${frontend_port}"
    echo "🔗 API:                http://localhost:8000"
    echo "🔧 Django Admin:       http://localhost:8000/admin/"
    echo "📊 API Documentation:  http://localhost:8000/api/docs/"
    echo "🗄️  Database:          localhost:5432"
    echo "🚀 Redis:              localhost:6379"
    echo ""
    echo "Optional Services (if enabled):"
    echo "📧 MailHog:            http://localhost:8025"
    echo "🗃️  MinIO:             http://localhost:9001"
    echo "☁️  LocalStack:        http://localhost:4566 (AWS services)"
    echo "🔍 Elasticsearch:      http://localhost:9200"
    echo "📈 Prometheus:         http://localhost:9090"
    echo "📊 Grafana:            http://localhost:3001 (admin/admin123)"
    echo ""
    echo "Useful Commands:"
    echo "─────────────────"
    echo "📋 View logs:          $COMPOSE_COMMAND logs -f [service_name]"
    echo "🔧 Run management:     $COMPOSE_COMMAND exec backend python manage.py [command]"
    echo "🛠️  Access shell:       $COMPOSE_COMMAND exec backend bash"
    echo "🛑 Stop services:      $COMPOSE_COMMAND down"
    echo "🗑️  Clean up:          $COMPOSE_COMMAND down -v --remove-orphans"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    $COMPOSE_COMMAND exec backend python manage.py migrate
    print_success "Migrations completed"
}

# Create superuser
create_superuser() {
    print_status "Creating Django superuser..."
    echo "Please create a superuser account for Django admin:"
    $COMPOSE_COMMAND exec backend python manage.py createsuperuser
}

# Main execution
main() {
    print_header
    
    # Parse command line arguments
    MODE="default"
    EXTRA_ARGS=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev|-d)
                MODE="dev"
                ;;
            --prod|-p)
                MODE="prod"
                ;;
            --full|-f)
                MODE="full"
                ;;
            --minimal|-m)
                MODE="minimal"
                ;;
            --with-storage|--with-localstack|--with-email|--with-monitoring)
                EXTRA_ARGS+=("$1")
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            "")
                MODE="default"
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
        shift
    done
    
    # Pre-flight checks
    check_docker
    check_docker_compose
    create_directories
    setup_env
    
    # Change to docker directory
    cd "$(dirname "$0")/.."
    
    # Start services
    start_services $MODE "${EXTRA_ARGS[@]}"
    
    # Post-startup tasks
    show_services
    
    # Ask if user wants to run migrations
    echo ""
    read -p "Do you want to run database migrations now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_migrations
        
        echo ""
        read -p "Do you want to create a superuser account? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_superuser
        fi
        
        # If storage is enabled, offer to setup MinIO test data
        if [[ " ${EXTRA_ARGS[@]} " =~ " --with-storage " ]] || [[ "$MODE" == "full" ]]; then
            echo ""
            read -p "Do you want to setup MinIO test data? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_status "Setting up MinIO test data..."
                $COMPOSE_COMMAND exec backend python manage.py setup_minio_test_data --create-bucket
                print_success "MinIO test data setup completed"
                print_status "MinIO Web UI: http://localhost:9001 (minioadmin/minioadmin123)"
            fi
        fi
        
        # If LocalStack is enabled, offer to setup LocalStack test data
        if [[ " ${EXTRA_ARGS[@]} " =~ " --with-localstack " ]] || [[ "$MODE" == "full" ]]; then
            echo ""
            read -p "Do you want to setup LocalStack AWS test data? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_status "Setting up LocalStack test data..."
                $COMPOSE_COMMAND exec backend python manage.py setup_localstack_test_data --create-bucket
                print_success "LocalStack test data setup completed"
                print_status "LocalStack Web UI: http://localhost:4566/_localstack/health"
                print_status "S3 Console: http://localhost:4566/_localstack/s3"
            fi
        fi
    fi
    
    print_success "JobQuest Navigator local environment is ready!"
    print_status "Use 'docker-compose logs -f' to view logs"
    print_status "Use 'docker-compose down' to stop all services"
}

# Run main function
main "$@"