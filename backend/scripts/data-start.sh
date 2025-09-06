#!/bin/bash
# Gradvy Hybrid Development - Data Services Startup
# Starts only PostgreSQL and Redis in Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[GRADVY DATA]${NC} $1"
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

# Navigate to backend directory
cd "$(dirname "$0")/.."

print_status "Starting Gradvy data services (PostgreSQL + Redis)..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose could not be found. Please install Docker Compose."
    exit 1
fi

# Start data services only
print_status "Starting PostgreSQL and Redis containers..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
sleep 10

# Check service status
print_status "Checking service health..."
docker-compose ps

# Check if services are healthy
if docker-compose ps | grep -q "healthy"; then
    print_success "Data services are running and healthy! 🎉"
    echo ""
    echo "📊 Service Status:"
    echo "   • PostgreSQL: localhost:5432"
    echo "   • Redis: localhost:6380"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Setup local environment: ./scripts/local-setup.sh"
    echo "   2. Run migrations: ./scripts/local-migrate.sh"
    echo "   3. Start Django: ./scripts/local-dev.sh"
    echo "   4. Start Celery: ./scripts/local-celery.sh"
else
    print_warning "Some services may still be starting up. Check logs with:"
    echo "   docker-compose logs"
fi