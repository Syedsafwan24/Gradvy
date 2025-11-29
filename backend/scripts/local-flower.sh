#!/bin/bash
# Gradvy Hybrid Development - Flower Monitoring
# Starts Flower monitoring locally connecting to Docker Redis

set -e

# Set cross-platform virtual environment activation commands
VENV_ACTIVATE_LINUX="source venv/bin/activate"
VENV_ACTIVATE_WINDOWS="source venv/Scripts/activate"
VENV_ACTIVATE_WINDOWS_CMD="venv\\Scripts\\activate.bat"
VENV_ACTIVATE_DEFAULT="source venv/bin/activate"

# Cross-platform virtual environment activation function
activate_venv() {
    # Detect operating system
    case "$(uname -s)" in
        Linux*)
            VENV_CMD="${VENV_ACTIVATE_LINUX:-source venv/bin/activate}"
            ;;
        Darwin*)
            VENV_CMD="${VENV_ACTIVATE_LINUX:-source venv/bin/activate}"
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            VENV_CMD="${VENV_ACTIVATE_WINDOWS:-source venv/Scripts/activate}"
            ;;
        *)
            VENV_CMD="${VENV_ACTIVATE_DEFAULT:-source venv/bin/activate}"
            ;;
    esac

    # Execute the activation command
    eval "$VENV_CMD"
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[GRADVY FLOWER]${NC} $1"
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
activate_venv

# Navigate to Django project
cd core

print_success "Starting Flower monitoring interface..."
echo ""
echo "🔧 Configuration:"
echo "   • Redis Broker: localhost:6380 (Docker)"
echo "   • Flower UI: Local web interface"
echo ""
echo "🌐 Access Point:"
echo "   • Flower: http://localhost:5555/"
echo "   • Username: admin"
echo "   • Password: flower_admin_2024"
echo ""
echo "⏹️  Press Ctrl+C to stop Flower"
echo ""

# Start Flower with authentication and explicit Redis broker configuration
# Export environment variables for consistency with worker/beat scripts
CELERY_BROKER_URL=redis://localhost:6380/0 \
CELERY_RESULT_BACKEND=redis://localhost:6380/0 \
celery -A core flower --port=5555 --basic_auth=admin:flower_admin_2024