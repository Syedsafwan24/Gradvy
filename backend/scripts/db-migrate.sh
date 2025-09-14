#!/bin/bash
# Gradvy Database Migration Script
# Run Django migrations safely

set -e  # Exit on any error

# Set cross-platform virtual environment activation commands
VENV_ACTIVATE_LINUX="source venv/bin/activate"
VENV_ACTIVATE_WINDOWS="source venv/Scripts/activate"
VENV_ACTIVATE_WINDOWS_CMD="venv\\Scripts\\activate.bat"
VENV_ACTIVATE_DEFAULT="source venv/bin/activate"

# Cross-platform virtual environment activation function
activate_venv() {
    # Detect operating system
    case "$(uname -s)" in
        Linux*)
            VENV_CMD="${VENV_ACTIVATE_LINUX:-source venv/bin/activate}"
            ;;
        Darwin*)
            VENV_CMD="${VENV_ACTIVATE_LINUX:-source venv/bin/activate}"
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            VENV_CMD="${VENV_ACTIVATE_WINDOWS:-source venv/Scripts/activate}"
            ;;
        *)
            VENV_CMD="${VENV_ACTIVATE_DEFAULT:-source venv/bin/activate}"
            ;;
    esac

    # Execute the activation command
    eval "$VENV_CMD"
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[GRADVY]${NC} $1"
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

# Navigate to the backend directory
cd "$(dirname "$0")/.."

print_status "Running Django migrations..."

# Check if database services are running
if ! docker-compose ps | grep -q "gradvy-postgres.*Up"; then
    print_error "PostgreSQL service is not running. Please start services first:"
    echo "   ./scripts/dev-start.sh"
    exit 1
fi

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 5

# Function to run Django commands safely
run_django_command() {
    local command=$1
    print_status "Running: python manage.py $command"
    
    if cd core && python manage.py $command; then
        print_success "Command completed: $command"
        return 0
    else
        print_error "Command failed: $command"
        return 1
    fi
}

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_success "Virtual environment is active: $(basename $VIRTUAL_ENV)"
else
    print_warning "No virtual environment detected. Make sure you have activated the venv."
    echo "   Run: activate_venv (cross-platform activation)"
fi

# Create migrations for auth app
print_status "Creating migrations for auth app..."
run_django_command "makemigrations auth"

# Create migrations for all apps
print_status "Creating migrations for all apps..."
run_django_command "makemigrations"

# Apply migrations
print_status "Applying migrations..."
run_django_command "migrate"

# Collect static files (if needed)
print_status "Collecting static files..."
run_django_command "collectstatic --noinput"

print_success "Database migrations completed successfully! 🎉"
echo ""
echo "🎯 Next steps:"
echo "   1. Create superuser: ./scripts/create-superuser.sh"
echo "   2. Start Django server: cd core && python manage.py runserver"
echo "   3. Access admin: http://localhost:8000/admin/"