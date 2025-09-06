#!/bin/bash
# Gradvy Development Environment Startup Script
# Start all Docker services and prepare development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_status "Starting Gradvy development environment..."

# Navigate to the backend directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_status "Please review and update .env file with your configuration"
fi

# Create necessary directories
mkdir -p logs

# Pull latest images
print_status "Pulling latest Docker images..."
docker-compose pull

# Build services
print_status "Building Gradvy services..."
docker-compose build --no-cache

# Start services in detached mode
print_status "Starting services..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."

# Function to check service health
check_service_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep -q "$service.*healthy\|$service.*Up"; then
            print_success "$service is healthy"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "$service failed to become healthy"
            return 1
        fi
        
        print_status "Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    done
}

# Check health of critical services
check_service_health "gradvy-postgres"
check_service_health "gradvy-redis"

print_status "Services are starting up..."
sleep 10

# Show service status
print_status "Service Status:"
docker-compose ps

# Display useful information
echo ""
print_success "Gradvy development environment is ready!"
echo ""
echo "🎯 Services:"
echo "   📊 Flower (Celery monitoring): http://localhost:5555"
echo "   🗄️  PostgreSQL: localhost:5432"
echo "   🔄 Redis: localhost:6379"
echo ""
echo "🚀 Next steps:"
echo "   1. Run migrations: ./scripts/db-migrate.sh"
echo "   2. Create superuser: ./scripts/create-superuser.sh"
echo "   3. Start Django: cd core && python manage.py runserver"
echo ""
echo "📋 Useful commands:"
echo "   📊 View logs: ./scripts/dev-logs.sh"
echo "   🔄 Restart: ./scripts/dev-restart.sh"
echo "   🛑 Stop: ./scripts/dev-stop.sh"
echo "   🧹 Clean restart: ./scripts/dev-clean.sh"
echo ""
print_status "Development environment started successfully! 🎉"