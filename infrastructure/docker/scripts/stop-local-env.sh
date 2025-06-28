#!/bin/bash

# JobQuest Navigator - Stop Local Docker Environment Script

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
    echo "  JobQuest Navigator - Stop Environment"
    echo "=============================================="
    echo -e "${NC}"
}

# Check if Docker Compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        COMPOSE_COMMAND="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_COMMAND="docker compose"
    else
        print_error "Docker Compose is not available."
        exit 1
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --clean, -c      Stop and remove all containers, networks, and volumes"
    echo "  --soft, -s       Stop containers but keep data (default)"
    echo "  --reset, -r      Complete reset - remove everything including images"
    echo "  --help, -h       Show this help message"
}

# Stop services softly (keep data)
stop_soft() {
    print_status "Stopping services (keeping data)..."
    
    # Stop all running containers
    $COMPOSE_COMMAND -f ../docker-compose.yml -f ../docker-compose.dev.yml down
    
    print_success "Services stopped successfully"
    print_status "Data volumes are preserved"
}

# Stop and clean up
stop_clean() {
    print_status "Stopping services and cleaning up..."
    
    # Stop and remove containers, networks, and volumes
    $COMPOSE_COMMAND -f ../docker-compose.yml -f ../docker-compose.dev.yml down -v --remove-orphans
    
    # Remove unused networks
    docker network prune -f
    
    print_success "Services stopped and cleaned up"
    print_warning "All data has been removed"
}

# Complete reset
stop_reset() {
    print_warning "This will remove EVERYTHING including Docker images!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Reset cancelled"
        return
    fi
    
    print_status "Performing complete reset..."
    
    # Stop and remove everything
    $COMPOSE_COMMAND -f ../docker-compose.yml -f ../docker-compose.dev.yml down -v --remove-orphans --rmi all
    
    # Remove unused Docker resources
    docker system prune -a -f --volumes
    
    print_success "Complete reset performed"
    print_warning "All containers, images, volumes, and networks have been removed"
}

# Show current status
show_status() {
    print_status "Current container status:"
    echo ""
    
    if docker ps -a --filter "name=jobquest" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q jobquest; then
        docker ps -a --filter "name=jobquest" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        print_status "No JobQuest Navigator containers found"
    fi
    
    echo ""
    print_status "Current volumes:"
    if docker volume ls --filter "name=docker" --format "table {{.Name}}\t{{.Driver}}" | grep -q docker; then
        docker volume ls --filter "name=docker" --format "table {{.Name}}\t{{.Driver}}"
    else
        print_status "No JobQuest Navigator volumes found"
    fi
}

# Main execution
main() {
    print_header
    
    # Parse command line arguments
    MODE="soft"
    case $1 in
        --clean|-c)
            MODE="clean"
            ;;
        --soft|-s)
            MODE="soft"
            ;;
        --reset|-r)
            MODE="reset"
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        "")
            MODE="soft"
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    check_docker_compose
    
    # Change to docker directory
    cd "$(dirname "$0")/.."
    
    # Show current status before stopping
    show_status
    echo ""
    
    # Execute based on mode
    case $MODE in
        "clean")
            stop_clean
            ;;
        "reset")
            stop_reset
            ;;
        *)
            stop_soft
            ;;
    esac
    
    echo ""
    show_status
    
    print_success "Operation completed!"
}

# Run main function
main "$@"