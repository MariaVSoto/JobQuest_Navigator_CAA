#!/bin/bash

# JobQuest Navigator - Django Management Script for Docker

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

# Check if backend container is running
check_backend_running() {
    if ! $COMPOSE_COMMAND ps backend | grep -q "Up\|running"; then
        print_error "Backend container is not running. Please start the environment first."
        print_status "Run: ./start-local-env.sh"
        exit 1
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Django Management Commands:"
    echo "  migrate              Run database migrations"
    echo "  makemigrations       Create new migrations"
    echo "  createsuperuser      Create Django superuser"
    echo "  collectstatic        Collect static files"
    echo "  shell                Open Django shell"
    echo "  dbshell              Open database shell"
    echo "  test                 Run tests"
    echo "  loaddata [fixture]   Load fixture data"
    echo "  dumpdata [app]       Dump data from app"
    echo ""
    echo "Custom Commands:"
    echo "  logs                 Show backend logs"
    echo "  restart              Restart backend container"
    echo "  bash                 Open bash shell in backend container"
    echo "  pip [command]        Run pip command in backend container"
    echo "  requirements         Install requirements.txt"
    echo ""
    echo "Database Commands:"
    echo "  db-reset             Reset database (WARNING: destroys all data)"
    echo "  db-backup            Backup database"
    echo "  db-restore [file]    Restore database from backup"
    echo ""
    echo "Examples:"
    echo "  $0 migrate"
    echo "  $0 createsuperuser"
    echo "  $0 test jobs.tests"
    echo "  $0 pip install django-extensions"
}

# Execute Django management command
run_django_command() {
    local cmd=$1
    shift
    print_status "Running Django command: $cmd $@"
    $COMPOSE_COMMAND exec backend python manage.py $cmd "$@"
}

# Execute custom commands
run_custom_command() {
    local cmd=$1
    shift
    
    case $cmd in
        "logs")
            print_status "Showing backend logs (Ctrl+C to exit)..."
            $COMPOSE_COMMAND logs -f backend
            ;;
        "restart")
            print_status "Restarting backend container..."
            $COMPOSE_COMMAND restart backend
            print_success "Backend restarted"
            ;;
        "bash")
            print_status "Opening bash shell in backend container..."
            $COMPOSE_COMMAND exec backend bash
            ;;
        "pip")
            print_status "Running pip command: $@"
            $COMPOSE_COMMAND exec backend pip "$@"
            ;;
        "requirements")
            print_status "Installing requirements.txt..."
            $COMPOSE_COMMAND exec backend pip install -r requirements.txt
            print_success "Requirements installed"
            ;;
        "db-reset")
            print_warning "This will DESTROY ALL DATA in the database!"
            read -p "Are you sure you want to continue? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_status "Resetting database..."
                $COMPOSE_COMMAND exec backend python manage.py flush --noinput
                $COMPOSE_COMMAND exec backend python manage.py migrate
                print_success "Database reset completed"
            else
                print_status "Database reset cancelled"
            fi
            ;;
        "db-backup")
            local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
            print_status "Creating database backup: $backup_file"
            $COMPOSE_COMMAND exec database pg_dump -U jobquest_user jobquest_navigator > "backups/$backup_file"
            print_success "Database backup created: backups/$backup_file"
            ;;
        "db-restore")
            if [ -z "$1" ]; then
                print_error "Please specify backup file to restore"
                exit 1
            fi
            local backup_file=$1
            if [ ! -f "backups/$backup_file" ]; then
                print_error "Backup file not found: backups/$backup_file"
                exit 1
            fi
            print_warning "This will OVERWRITE ALL DATA in the database!"
            read -p "Are you sure you want to continue? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_status "Restoring database from: $backup_file"
                $COMPOSE_COMMAND exec -T database psql -U jobquest_user jobquest_navigator < "backups/$backup_file"
                print_success "Database restored successfully"
            else
                print_status "Database restore cancelled"
            fi
            ;;
        *)
            print_error "Unknown custom command: $cmd"
            show_usage
            exit 1
            ;;
    esac
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi
    
    check_docker_compose
    
    # Change to docker directory
    cd "$(dirname "$0")/.."
    
    # Create backups directory if it doesn't exist
    mkdir -p backups
    
    local command=$1
    shift
    
    # Check if backend is running for most commands
    case $command in
        "logs"|"restart")
            # These commands don't require backend to be running
            ;;
        *)
            check_backend_running
            ;;
    esac
    
    # Execute based on command type
    case $command in
        # Django management commands
        "migrate"|"makemigrations"|"createsuperuser"|"collectstatic"|"shell"|"dbshell"|"test"|"loaddata"|"dumpdata")
            run_django_command $command "$@"
            ;;
        # Custom commands
        "logs"|"restart"|"bash"|"pip"|"requirements"|"db-reset"|"db-backup"|"db-restore")
            run_custom_command $command "$@"
            ;;
        # Help
        "--help"|"-h"|"help")
            show_usage
            ;;
        *)
            # Try to run as Django command first
            print_status "Attempting to run as Django command: $command"
            run_django_command $command "$@"
            ;;
    esac
}

# Run main function
main "$@"