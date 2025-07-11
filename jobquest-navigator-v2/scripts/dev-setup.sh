#!/bin/bash
# JobQuest Navigator v2 - Development Environment Setup Script

set -e

echo "🚀 JobQuest Navigator v2 - Development Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Check if Docker is installed and running
check_docker() {
    print_step "Checking Docker"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_status "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_step "Checking Docker Compose"
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    print_status "Docker Compose is available"
}

# Setup environment files
setup_env_files() {
    print_step "Setting up environment files"
    
    # Backend environment
    if [ ! -f "backend-fastapi-graphql/.env" ]; then
        print_status "Creating backend .env from template"
        cp backend-fastapi-graphql/.env.template backend-fastapi-graphql/.env
    else
        print_warning "Backend .env already exists"
    fi
    
    # Frontend environment
    if [ ! -f "frontend-react-minimal/.env" ]; then
        print_status "Creating frontend .env from template"
        cp frontend-react-minimal/.env.template frontend-react-minimal/.env
    else
        print_warning "Frontend .env already exists"
    fi
    
    # Docker environment
    if [ ! -f "infrastructure/docker/.env" ]; then
        print_status "Creating Docker .env from template"
        cp infrastructure/docker/.env.template infrastructure/docker/.env
    else
        print_warning "Docker .env already exists"
    fi
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies"
    
    # Backend Python dependencies
    print_status "Installing Python dependencies..."
    cd backend-fastapi-graphql
    if [ -f "requirements.txt" ]; then
        python -m pip install -r requirements.txt
    fi
    cd ..
    
    # Frontend Node dependencies
    print_status "Installing Node.js dependencies..."
    cd frontend-react-minimal
    if [ -f "package.json" ]; then
        npm install
    fi
    cd ..
    
    # Shared module dependencies
    print_status "Installing shared module dependencies..."
    cd shared
    if [ -f "package.json" ]; then
        npm install
    fi
    cd ..
}

# Build shared module
build_shared() {
    print_step "Building shared module"
    
    cd shared
    if [ -f "package.json" ]; then
        print_status "Building TypeScript shared module..."
        npm run build
    fi
    cd ..
}

# Initialize database
init_database() {
    print_step "Database initialization"
    
    print_status "Starting database services..."
    cd infrastructure/docker
    docker-compose up -d db redis
    
    print_status "Waiting for database to be ready..."
    sleep 10
    
    print_status "Running database migrations..."
    cd ../../backend-fastapi-graphql
    
    # Initialize Alembic if not already done
    if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions)" ]; then
        print_status "Creating initial migration..."
        alembic revision --autogenerate -m "Initial migration"
    fi
    
    # Run migrations
    alembic upgrade head
    
    cd ..
}

# Main setup function
main() {
    print_status "Starting development environment setup for JobQuest Navigator v2"
    
    # Change to project root directory
    cd "$(dirname "$0")/.."
    
    check_docker
    check_docker_compose
    setup_env_files
    
    # Ask user about dependency installation
    read -p "Install dependencies? This may take a few minutes. (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_dependencies
        build_shared
    fi
    
    # Ask user about database initialization
    read -p "Initialize database? This will start Docker services. (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        init_database
    fi
    
    print_step "Setup Complete!"
    print_status "Your development environment is ready!"
    echo
    echo "Next steps:"
    echo "1. Start the development environment:"
    echo "   cd infrastructure/docker && docker-compose up"
    echo
    echo "2. Or use the development script:"
    echo "   ./scripts/dev-start.sh"
    echo
    echo "3. Access the application:"
    echo "   - Frontend: http://localhost:3001"
    echo "   - Backend API: http://localhost:8001"
    echo "   - GraphQL Playground: http://localhost:8001/graphql"
}

# Run main function
main "$@"