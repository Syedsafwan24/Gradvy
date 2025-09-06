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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to ask yes/no question with default yes
ask_yes_no() {
    local question="$1"
    local response
    while true; do
        echo -ne "${YELLOW}[QUESTION]${NC} $question (Y/n): "
        read -r response
        # Default to yes if empty response
        response=${response:-y}
        case $response in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes (y) or no (n). Press Enter for default (yes).";;
        esac
    done
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
    print_warning "Data services (PostgreSQL + Redis) are not running!"
    echo ""
    echo "📋 Required services:"
    echo "   • PostgreSQL database (localhost:5432)"
    echo "   • Redis cache (localhost:6380)"
    echo ""
    
    if ask_yes_no "Would you like to start the data services now?"; then
        print_status "Starting data services..."
        echo ""
        if ./scripts/data-start.sh; then
            print_success "Data services started successfully! 🎉"
            echo ""
        else
            print_error "Failed to start data services!"
            echo "Please run './scripts/data-start.sh' manually and try again."
            exit 1
        fi
    else
        print_error "Data services are required for Django to run."
        echo ""
        echo "💡 To start data services manually:"
        echo "   ./scripts/data-start.sh"
        echo ""
        echo "Then run this script again: ./scripts/local-dev.sh"
        exit 1
    fi
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