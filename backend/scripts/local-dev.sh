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
    print_warning "Data services (PostgreSQL + Redis + MongoDB) are not running!"
    echo ""
    echo "📋 Required services:"
    echo "   • PostgreSQL database (localhost:5432)"
    echo "   • Redis cache (localhost:6380)"
    echo "   • MongoDB preferences (localhost:27017)"
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
source venv/scripts/activate

# Check if requirements are installed
if ! pip show django &> /dev/null; then
    print_error "Dependencies not installed! Run ./scripts/local-setup.sh first."
    exit 1
fi

# Navigate to Django project
cd core

# Check database connections
print_status "Testing database connections..."
if ! python manage.py check --database default; then
    print_error "PostgreSQL connection failed! Check if PostgreSQL container is running."
    exit 1
fi

# Test MongoDB connection
print_status "Testing MongoDB connection..."
mongodb_check=$(python -c "
try:
    import mongoengine
    from core.settings import MONGODB_SETTINGS
    mongoengine.connect(**MONGODB_SETTINGS)
    print('MongoDB: Connected successfully')
except Exception as e:
    print(f'MongoDB: Connection failed - {e}')
    exit(1)
" 2>/dev/null)

if echo "$mongodb_check" | grep -q "Connected successfully"; then
    print_success "MongoDB connection successful"
else
    print_error "MongoDB connection failed!"
    print_info "Check MongoDB status: ./scripts/mongodb-status.sh"
    print_info "Try starting services: ./scripts/data-start.sh"
    exit 1
fi

# Check Celery services
print_status "Checking Celery services..."
celery_worker_running=false
celery_beat_running=false

# Check if Celery worker is running
if pgrep -f "celery.*worker" > /dev/null 2>&1; then
    print_success "Celery worker is running"
    celery_worker_running=true
else
    print_warning "Celery worker is not running!"
    echo ""
    echo "📋 Celery Worker provides:"
    echo "   • Background task processing"
    echo "   • Email sending"
    echo "   • MFA cleanup tasks"
    echo ""
    
    if ask_yes_no "Would you like to start Celery worker now?"; then
        print_status "Starting Celery worker in background..."
        echo ""
        # Navigate back to backend root for celery script
        cd ..
        nohup ./scripts/local-celery.sh > celery-worker.log 2>&1 &
        CELERY_WORKER_PID=$!
        echo "Celery worker started (PID: $CELERY_WORKER_PID)"
        echo "Log file: celery-worker.log"
        celery_worker_running=true
        # Navigate back to core directory
        cd core
        sleep 2  # Give worker time to start
    else
        print_warning "Continuing without Celery worker. Background tasks won't be processed."
    fi
fi

# Check if Celery Beat is running
if pgrep -f "celery.*beat" > /dev/null 2>&1; then
    print_success "Celery Beat scheduler is running"
    celery_beat_running=true
else
    print_warning "Celery Beat scheduler is not running!"
    echo ""
    echo "📋 Celery Beat provides:"
    echo "   • Periodic task scheduling"
    echo "   • Automated MFA data cleanup"
    echo "   • Maintenance tasks"
    echo ""
    
    if ask_yes_no "Would you like to start Celery Beat scheduler now?"; then
        print_status "Starting Celery Beat scheduler in background..."
        echo ""
        # Navigate back to backend root for celery beat script
        cd ..
        nohup ./scripts/local-celery-beat.sh > celery-beat.log 2>&1 &
        CELERY_BEAT_PID=$!
        echo "Celery Beat scheduler started (PID: $CELERY_BEAT_PID)"
        echo "Log file: celery-beat.log"
        celery_beat_running=true
        # Navigate back to core directory
        cd core
        sleep 2  # Give scheduler time to start
    else
        print_warning "Continuing without Celery Beat. Scheduled tasks won't run automatically."
    fi
fi

echo ""

print_success "Starting Django development server..."
echo ""
echo "🔧 Configuration:"
echo "   • Database: PostgreSQL (Docker) -> localhost:5432"  
echo "   • Cache: Redis (Docker) -> localhost:6380"
echo "   • Preferences: MongoDB (Docker) -> localhost:27017"
echo "   • Django: Local development server"
if [ "$celery_worker_running" = true ]; then
    echo "   • Celery Worker: Running (background process)"
else
    echo "   • Celery Worker: Not running"
fi
if [ "$celery_beat_running" = true ]; then
    echo "   • Celery Beat: Running (background scheduler)"
else
    echo "   • Celery Beat: Not running"
fi
echo ""
echo "🌐 Access Points:"
echo "   • Django: http://localhost:8000/"
echo "   • Admin: http://localhost:8000/admin/"
echo "   • API Preferences: http://localhost:8000/api/preferences/"
echo ""
if [ "$celery_worker_running" = true ] || [ "$celery_beat_running" = true ]; then
    echo "📋 Celery Logs:"
    if [ "$celery_worker_running" = true ]; then
        echo "   • Worker: tail -f celery-worker.log"
    fi
    if [ "$celery_beat_running" = true ]; then
        echo "   • Beat: tail -f celery-beat.log"
    fi
    echo ""
fi
echo "⏹️  Press Ctrl+C to stop the Django server"
if [ "$celery_worker_running" = true ] || [ "$celery_beat_running" = true ]; then
    echo "   Celery services will continue running in background"
    echo "   To stop all: pkill -f celery"
fi
echo ""

# Start Django development server
python manage.py runserver