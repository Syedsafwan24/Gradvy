#!/bin/bash
# Gradvy Superuser Creation Script
# Create Django superuser for admin access

set -e  # Exit on any error

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

print_status "Creating Django superuser..."

# Check if database services are running
if ! docker-compose ps | grep -q "gradvy-postgres.*Up"; then
    print_error "PostgreSQL service is not running. Please start services first:"
    echo "   ./scripts/dev-start.sh"
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_success "Virtual environment is active: $(basename $VIRTUAL_ENV)"
else
    print_warning "No virtual environment detected. Make sure you have activated the venv."
    echo "   source venv/bin/activate"
fi

# Navigate to Django core directory
cd core

print_status "Creating superuser account..."
echo ""
echo "🔐 Please provide superuser details:"

# Create superuser interactively
if python manage.py createsuperuser; then
    print_success "Superuser created successfully! 🎉"
    echo ""
    echo "🎯 Access admin interface:"
    echo "   🌐 URL: http://localhost:8000/admin/"
    echo "   👤 Use the credentials you just created"
    echo ""
    echo "🚀 Start Django server:"
    echo "   python manage.py runserver"
else
    print_error "Failed to create superuser"
    exit 1
fi