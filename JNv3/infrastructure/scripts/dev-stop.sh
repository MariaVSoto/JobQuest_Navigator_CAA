#!/bin/bash
# JobQuest Navigator v2 - Development Environment Stop Script

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

echo "🛑 Stopping JobQuest Navigator v2 Development Environment"
echo "========================================================"

# Parse command line arguments
CLEAN=""
VOLUMES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN="--clean"
            shift
            ;;
        --volumes)
            VOLUMES="--volumes"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --clean      Remove containers and networks"
            echo "  --volumes    Also remove volumes (WARNING: This will delete data!)"
            echo "  --help, -h   Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd infrastructure/docker

print_step "Stopping Services"

if [ -n "$CLEAN" ]; then
    print_status "Stopping and removing containers, networks..."
    
    if [ -n "$VOLUMES" ]; then
        print_warning "This will delete all data including database and uploaded files!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down --volumes --remove-orphans
            print_status "All services stopped and data volumes removed"
        else
            print_status "Cancelled volume removal"
            docker-compose down --remove-orphans
            print_status "Services stopped and containers removed"
        fi
    else
        docker-compose down --remove-orphans
        print_status "Services stopped and containers removed"
    fi
else
    print_status "Stopping services..."
    docker-compose stop
    print_status "All services stopped"
fi

# Show remaining containers if any
REMAINING=$(docker-compose ps --services --filter "status=running" 2>/dev/null || true)
if [ -n "$REMAINING" ]; then
    print_warning "Some services are still running:"
    docker-compose ps
else
    print_status "All services are stopped"
fi

print_step "Cleanup Complete"

if [ -z "$CLEAN" ]; then
    echo "Services are stopped but containers are preserved."
    echo "To restart: ./scripts/dev-start.sh"
    echo "To clean up: ./scripts/dev-stop.sh --clean"
else
    echo "Services and containers have been removed."
    echo "To restart: ./scripts/dev-start.sh"
fi