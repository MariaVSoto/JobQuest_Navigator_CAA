#!/bin/bash

# JobQuest Navigator v2 - Development Environment Startup Script
# This script starts the development environment with all necessary services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="jobquest-navigator-v2"
COMPOSE_FILE="docker-compose.yml"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
    print_status "Docker is running"
}

# Function to check if ports are available
check_ports() {
    local ports=("3001" "8001" "5433" "6380")
    local occupied_ports=()
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            occupied_ports+=($port)
        fi
    done
    
    if [ ${#occupied_ports[@]} -ne 0 ]; then
        print_warning "The following ports are already in use: ${occupied_ports[*]}"
        print_warning "Please stop the processes using these ports or they will conflict"
        echo
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to create directories if they don't exist
create_directories() {
    local dirs=(
        "../../backend-fastapi-graphql/logs"
        "./logs"
        "./data/postgres"
        "./data/redis"
        "./data/minio"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Function to pull latest images
pull_images() {
    print_status "Pulling latest Docker images..."
    docker-compose pull
}

# Function to start services
start_services() {
    local profile="$1"
    
    print_header "Starting JobQuest Navigator v2 Development Environment"
    
    if [ -n "$profile" ]; then
        print_status "Starting with profile: $profile"
        docker-compose --profile "$profile" up -d
    else
        print_status "Starting core services (db, redis, backend, frontend)"
        docker-compose up -d db redis backend frontend
    fi
}

# Function to wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to become healthy..."
    
    local services=("db" "redis" "backend")
    local max_wait=120
    local wait_time=0
    
    for service in "${services[@]}"; do
        print_status "Checking $service..."
        while [ $wait_time -lt $max_wait ]; do
            if docker-compose ps $service | grep -q "healthy\|Up"; then
                print_status "$service is ready"
                break
            fi
            sleep 5
            wait_time=$((wait_time + 5))
        done
        
        if [ $wait_time -ge $max_wait ]; then
            print_warning "$service may not be fully ready, but continuing..."
        fi
    done
}

# Function to show service status
show_status() {
    print_header "Service Status"
    docker-compose ps
    
    echo
    print_header "Service URLs"
    echo -e "${GREEN}Frontend:${NC}     http://localhost:3001"
    echo -e "${GREEN}Backend API:${NC}  http://localhost:8001"
    echo -e "${GREEN}GraphQL:${NC}      http://localhost:8001/graphql"
    echo -e "${GREEN}Database:${NC}     localhost:5433 (postgres)"
    echo -e "${GREEN}Redis:${NC}        localhost:6380"
    
    # Show optional services if they're running
    if docker-compose ps mailhog | grep -q "Up"; then
        echo -e "${GREEN}MailHog:${NC}      http://localhost:8026"
    fi
    
    if docker-compose ps minio | grep -q "Up"; then
        echo -e "${GREEN}MinIO:${NC}        http://localhost:9002 (admin: minioadmin/minioadmin123)"
    fi
}

# Function to show logs
show_logs() {
    local service="$1"
    if [ -n "$service" ]; then
        print_status "Showing logs for $service (Ctrl+C to exit)"
        docker-compose logs -f "$service"
    else
        print_status "Showing logs for all services (Ctrl+C to exit)"
        docker-compose logs -f
    fi
}

# Main script logic
main() {
    local command="$1"
    local option="$2"
    
    case $command in
        "start")
            check_docker
            check_ports
            create_directories
            pull_images
            
            case $option in
                "--with-storage")
                    start_services "storage"
                    ;;
                "--with-mail")
                    start_services "development"
                    ;;
                "--minimal")
                    docker-compose up -d db redis backend
                    ;;
                *)
                    start_services
                    ;;
            esac
            
            wait_for_services
            show_status
            ;;
            
        "stop")
            print_status "Stopping all services..."
            docker-compose down
            ;;
            
        "restart")
            print_status "Restarting services..."
            docker-compose restart
            show_status
            ;;
            
        "logs")
            show_logs "$option"
            ;;
            
        "status")
            show_status
            ;;
            
        "clean")
            print_warning "This will remove all containers, volumes, and images for this project"
            read -p "Are you sure? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker-compose down -v --rmi all
                docker system prune -f
                print_status "Cleanup completed"
            fi
            ;;
            
        "help"|"--help"|"-h")
            echo "JobQuest Navigator v2 Development Environment"
            echo
            echo "Usage: $0 <command> [options]"
            echo
            echo "Commands:"
            echo "  start                Start development environment"
            echo "  start --with-storage Start with MinIO storage"
            echo "  start --with-mail    Start with MailHog"
            echo "  start --minimal      Start only essential services"
            echo "  stop                 Stop all services"
            echo "  restart              Restart all services"
            echo "  logs [service]       Show logs (all services or specific service)"
            echo "  status               Show service status and URLs"
            echo "  clean                Remove all containers and data"
            echo "  help                 Show this help message"
            echo
            ;;
            
        *)
            print_error "Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"