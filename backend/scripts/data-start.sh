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

print_status "Starting Gradvy data services (PostgreSQL + Redis + MongoDB)..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose could not be found. Please install Docker Compose."
    exit 1
fi

# Start data services only
print_status "Starting PostgreSQL, Redis, and MongoDB containers..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."
echo "⏳ Initializing containers..."
sleep 5

# Check PostgreSQL and Redis first (they start faster)
print_status "Checking PostgreSQL and Redis..."
sleep 5

# Wait longer for MongoDB (needs more time to initialize)
print_status "Waiting for MongoDB initialization..."
echo "⏳ MongoDB may take 30-60 seconds on first startup..."
sleep 15

# Check service status
print_status "Checking all service health..."
docker-compose ps

echo ""

# Individual service health checks
print_status "Testing individual service connectivity..."

# PostgreSQL check
if docker exec gradvy-postgres pg_isready -U gradvy_user -d gradvy_db >/dev/null 2>&1; then
    print_success "✅ PostgreSQL: Ready (localhost:5432)"
    postgres_ready=true
else
    print_warning "⚠️  PostgreSQL: Still starting up..."
    postgres_ready=false
fi

# Redis check
if docker exec gradvy-redis redis-cli ping >/dev/null 2>&1; then
    print_success "✅ Redis: Ready (localhost:6380)"
    redis_ready=true
else
    print_warning "⚠️  Redis: Still starting up..."
    redis_ready=false
fi

# MongoDB check
if docker exec gradvy-mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
    print_success "✅ MongoDB: Ready (localhost:27017)"
    mongodb_ready=true
    
    # Check if MongoDB is properly initialized
    if docker exec gradvy-mongodb mongosh gradvy_preferences --eval "db.stats()" >/dev/null 2>&1; then
        print_success "✅ MongoDB: Database 'gradvy_preferences' initialized"
    else
        print_warning "⚠️  MongoDB: Database initialization in progress..."
    fi
else
    print_warning "⚠️  MongoDB: Still starting up (this is normal for first startup)..."
    mongodb_ready=false
fi

echo ""

# Overall status summary
if [ "$postgres_ready" = true ] && [ "$redis_ready" = true ] && [ "$mongodb_ready" = true ]; then
    print_success "All data services are running and healthy! 🎉"
    echo ""
    echo "🗄️  Database Services:"
    echo "   ✅ PostgreSQL (Django): localhost:5432"
    echo "   ✅ Redis (Celery):      localhost:6380"
    echo "   ✅ MongoDB (Preferences): localhost:27017"
    echo ""
    echo "🔧 Management Tools:"
    echo "   • MongoDB status: ./scripts/mongodb-status.sh"
    echo "   • View all logs:  docker-compose logs"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Setup environment:   ./scripts/local-setup.sh"
    echo "   2. Check MongoDB:       ./scripts/mongodb-status.sh"
    echo "   3. Run migrations:      ./scripts/local-migrate.sh"
    echo "   4. Seed preferences:    ./scripts/preferences-seed.sh"
    echo "   5. Start Django:        ./scripts/local-dev.sh"
    echo "   6. Start Celery:        ./scripts/local-celery.sh"
else
    print_warning "Some services are still starting up..."
    echo ""
    echo "📋 Service Status:"
    if [ "$postgres_ready" = true ]; then
        echo "   ✅ PostgreSQL: Ready"
    else
        echo "   ⏳ PostgreSQL: Starting..."
    fi
    if [ "$redis_ready" = true ]; then
        echo "   ✅ Redis: Ready"
    else
        echo "   ⏳ Redis: Starting..."
    fi
    if [ "$mongodb_ready" = true ]; then
        echo "   ✅ MongoDB: Ready"
    else
        echo "   ⏳ MongoDB: Starting (can take 1-2 minutes)..."
    fi
    echo ""
    echo "💡 Troubleshooting:"
    echo "   • Check logs: docker-compose logs [service-name]"
    echo "   • MongoDB:    docker logs gradvy-mongodb"
    echo "   • Status:     ./scripts/mongodb-status.sh"
    echo ""
    echo "⏰ Wait 1-2 minutes and run this script again, or check:"
    echo "   ./scripts/mongodb-status.sh"
fi