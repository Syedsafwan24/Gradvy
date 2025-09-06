#!/bin/bash
# Gradvy Development Environment Stop Script
# Gracefully stop all Docker services

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

# Navigate to the backend directory
cd "$(dirname "$0")/.."

print_status "Stopping Gradvy development environment..."

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    print_status "Gracefully stopping services..."
    docker-compose stop
    
    # Wait a moment for graceful shutdown
    sleep 3
    
    print_status "Removing containers..."
    docker-compose down
    
    print_success "All services stopped successfully"
else
    print_warning "No running services found"
fi

# Show final status
print_status "Final status:"
docker-compose ps

print_success "Gradvy development environment stopped! 🛑"
echo ""
echo "💡 To start again: ./scripts/dev-start.sh"
echo "🧹 For clean restart: ./scripts/dev-clean.sh"