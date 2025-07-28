#!/bin/bash
# JobQuest Navigator v2 - Development Environment Start Script

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

echo "🚀 Starting JobQuest Navigator v2 Development Environment"
echo "========================================================"

# Parse command line arguments
MODE="development"
WITH_STORAGE=""
DETACHED=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --production|--prod)
            MODE="production"
            shift
            ;;
        --with-storage)
            WITH_STORAGE="--profile storage"
            shift
            ;;
        --detached|-d)
            DETACHED="-d"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --production, --prod    Start in production mode"
            echo "  --with-storage          Include MinIO storage services"
            echo "  --detached, -d          Run in detached mode"
            echo "  --help, -h              Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_step "Environment Check"

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Check if environment files exist
if [ ! -f "infrastructure/docker/.env" ]; then
    print_warning "Docker .env file not found. Creating from template..."
    cp infrastructure/docker/.env.template infrastructure/docker/.env
fi

print_step "Starting Services ($MODE mode)"

cd infrastructure/docker

# Set environment variables for Docker Compose
export COMPOSE_PROJECT_NAME="jobquest_navigator_v2"

if [ "$MODE" = "production" ]; then
    export COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml"
    print_status "Using production configuration"
else
    export COMPOSE_FILE="docker-compose.yml:docker-compose.dev.yml"
    print_status "Using development configuration"
fi

# Build and start services
print_status "Building and starting services..."

if [ -n "$DETACHED" ]; then
    docker-compose up --build $DETACHED $WITH_STORAGE
    
    print_step "Services Started Successfully!"
    print_status "Running in detached mode. Use 'docker-compose logs -f' to view logs."
else
    # Start in foreground
    trap 'print_step "Shutting down services..."; docker-compose down; exit 0' INT TERM
    
    docker-compose up --build $WITH_STORAGE
fi

print_step "Service Information"
echo "Frontend: http://localhost:3001"
echo "Backend API: http://localhost:8001"
echo "GraphQL Playground: http://localhost:8001/graphql"
echo "Database: localhost:5433"
echo "Redis: localhost:6380"

if [[ "$WITH_STORAGE" == *"storage"* ]]; then
    echo "MinIO Console: http://localhost:9002 (minioadmin/minioadmin123)"
    echo "MinIO API: http://localhost:9001"
fi

print_status "Development environment is ready!"