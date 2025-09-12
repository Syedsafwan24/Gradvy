#!/bin/bash
# Gradvy Hybrid Development - Create Superuser
# Create Django admin superuser

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[GRADVY SUPERUSER]${NC} $1"
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
source venv/scripts/activate

# Navigate to Django project
cd core

# Check if migrations are up to date
print_status "Checking database migrations..."
python manage.py showmigrations

print_status "Creating Django superuser..."
echo ""
echo "📝 Please provide superuser details:"

# Create superuser interactively
python manage.py createsuperuser

print_success "Superuser created successfully! 🎉"
echo ""
echo "🌐 Access Points:"
echo "   • Django Admin: http://localhost:8000/admin/"
echo "   • Main App: http://localhost:8000/"
echo ""
echo "🚀 Ready to start development:"
echo "   ./scripts/local-dev.sh"