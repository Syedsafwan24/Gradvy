#!/bin/bash
# Gradvy Hybrid Development - Celery Beat Scheduler
# Starts Celery Beat scheduler locally connecting to Docker Redis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[GRADVY CELERY BEAT]${NC} $1"
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

# Check if Redis is running
print_status "Checking Redis connection..."
if ! docker-compose ps | grep gradvy-redis | grep -q "Up"; then
    print_error "Redis service not running! Start data services first:"
    echo "   ./scripts/data-start.sh"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Navigate to Django project
cd core

# Test Redis connection
print_status "Testing Redis connection..."
python -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6380, db=0)
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    exit(1)
"

print_success "Starting Celery Beat scheduler..."
echo ""
echo "🔧 Configuration:"
echo "   • Redis Broker: localhost:6380 (Docker)"
echo "   • Celery Beat: Local scheduler process"
echo "   • Schedule: Periodic task scheduling"
echo ""
echo "📋 Scheduled Tasks:"
echo "   • MFA Data Cleanup: Runs daily"
echo ""
echo "⏹️  Press Ctrl+C to stop the scheduler"
echo ""

# Start Celery Beat scheduler
celery -A core beat --loglevel=info