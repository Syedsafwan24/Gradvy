#!/bin/bash
# Gradvy Hybrid Development - Database Migrations
# Run Django migrations against Docker PostgreSQL

set -e

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
    echo -e "${BLUE}[GRADVY MIGRATE]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found! Run ./scripts/local-setup.sh first."
    exit 1
fi

# Check if PostgreSQL is running
print_status "Checking PostgreSQL connection..."
if ! docker-compose ps | grep gradvy-postgres | grep -q "Up"; then
    print_error "PostgreSQL service not running! Start data services first:"
    echo "   ./scripts/data-start.sh"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
activate_venv

# Navigate to Django project
cd core

# Test database connection
print_status "Testing database connection..."
if ! python manage.py check --database default; then
    print_error "Database connection failed!"
    exit 1
fi

# Create migrations if needed
print_status "Creating migrations..."
python manage.py makemigrations

# Run migrations
print_status "Running database migrations..."
python manage.py migrate

print_success "Database migrations completed! 🎉"
echo ""
echo "📊 Database Status:"
echo "   • PostgreSQL: Running in Docker (localhost:5432)"
echo "   • Database: gradvy_db"
echo "   • User: gradvy_user"
echo ""
echo "🚀 Next Steps:"
echo "   • Create superuser: ./scripts/local-superuser.sh"
echo "   • Start Django: ./scripts/local-dev.sh"