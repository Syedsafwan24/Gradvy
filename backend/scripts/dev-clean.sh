#!/bin/bash
# Gradvy Development Clean Restart Script
# Stop all services, clean up, and restart fresh

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

print_warning "This will completely clean and restart the development environment."
print_warning "Data in volumes will be preserved, but containers will be rebuilt."
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Operation cancelled."
    exit 0
fi

print_status "Cleaning Gradvy development environment..."

# Stop and remove containers
print_status "Stopping and removing containers..."
docker-compose down || true

# Remove dangling images and containers
print_status "Cleaning up Docker resources..."
docker system prune -f

# Remove built images to force rebuild
print_status "Removing built images for clean rebuild..."
docker-compose down --rmi local || true

# Clear Python cache
print_status "Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

print_status "Rebuilding and starting services..."

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d

# Wait for services
print_status "Waiting for services to be ready..."
sleep 15

# Show status
print_status "Service Status:"
docker-compose ps

print_success "Clean restart completed! 🎉"
echo ""
echo "🎯 Next steps:"
echo "   1. Check logs: ./scripts/dev-logs.sh"
echo "   2. Run migrations: ./scripts/db-migrate.sh"
echo "   3. Create superuser: ./scripts/create-superuser.sh"
echo "   4. Start Django: cd core && python manage.py runserver"