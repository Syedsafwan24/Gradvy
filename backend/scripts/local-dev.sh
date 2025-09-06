#!/bin/bash
# Gradvy Hybrid Development - Django Development Server
# Starts Django development server locally connecting to Docker data services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[GRADVY DEV]${NC} $1"
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

# Check if data services are running
print_status "Checking data services..."
if ! docker-compose ps | grep -q "Up"; then
    print_error "Data services not running! Start them first:"
    echo "   ./scripts/data-start.sh"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! pip show django &> /dev/null; then
    print_error "Dependencies not installed! Run ./scripts/local-setup.sh first."
    exit 1
fi

# Navigate to Django project
cd core

# Check database connection
print_status "Testing database connection..."
if ! python manage.py check --database default; then
    print_error "Database connection failed! Check if PostgreSQL container is running."
    exit 1
fi

print_success "Starting Django development server..."
echo ""
echo "🔧 Configuration:"
echo "   • Database: PostgreSQL (Docker) -> localhost:5432"  
echo "   • Redis: Redis (Docker) -> localhost:6380"
echo "   • Django: Local development server"
echo ""
echo "🌐 Access Points:"
echo "   • Django: http://localhost:8000/"
echo "   • Admin: http://localhost:8000/admin/"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start Django development server
python manage.py runserver