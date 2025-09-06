#!/bin/bash
# Gradvy Development Logs Viewer
# View logs from all services or specific service

set -e  # Exit on any error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[GRADVY]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Navigate to the backend directory
cd "$(dirname "$0")/.."

# Check if specific service is requested
SERVICE=$1
LINES=${2:-100}

if [ -z "$SERVICE" ]; then
    print_status "Showing logs for all services (last $LINES lines)..."
    echo ""
    echo "🎯 Available services:"
    echo "   - gradvy-postgres"
    echo "   - gradvy-redis"
    echo "   - gradvy-celery-worker"
    echo "   - gradvy-celery-beat"
    echo "   - gradvy-flower"
    echo ""
    echo "💡 Usage: $0 [service-name] [lines]"
    echo "   Example: $0 gradvy-celery-worker 50"
    echo ""
    print_status "Showing combined logs..."
    docker-compose logs --tail=$LINES -f
else
    print_status "Showing logs for $SERVICE (last $LINES lines)..."
    docker-compose logs --tail=$LINES -f "$SERVICE"
fi