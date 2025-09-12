#!/bin/bash
# Gradvy Hybrid Development - Local Environment Setup
# Complete setup for local development with Docker data services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[GRADVY SETUP]${NC} $1"
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

print_status "Setting up Gradvy hybrid development environment..."

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.13 or later."
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
print_status "Found Python $python_version"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

print_success "Prerequisites check passed!"

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created!"
else
    print_status "Virtual environment already exists."
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/scripts/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing Python dependencies..."
pip install -r requirements.txt

print_success "Python dependencies installed!"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file with MongoDB support..."
    cat > .env << 'EOF'
# Gradvy Hybrid Development Environment
# PostgreSQL, Redis, and MongoDB in Docker, Django/Celery local

# Django Configuration
DJANGO_SECRET_KEY=dev-secret-key-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (Docker PostgreSQL)
DB_NAME=gradvy_db
DB_USER=gradvy_user
DB_PASSWORD=gradvy_secure_2024
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration (Docker Redis)
CELERY_BROKER_URL=redis://localhost:6380/0

# MongoDB Configuration (Docker MongoDB)
MONGODB_URI=mongodb://gradvy_app:gradvy_app_secure_2024@localhost:27017/gradvy_preferences
MONGO_ROOT_USERNAME=gradvy_admin
MONGO_ROOT_PASSWORD=gradvy_mongo_secure_2024
MONGO_DB=gradvy_preferences
MONGO_PORT=27017

# Preferences App Settings
PREFERENCES_CACHE_TIMEOUT=3600
RECOMMENDATIONS_EXPIRY_DAYS=7
ANALYTICS_RETENTION_MONTHS=12
AI_INSIGHTS_UPDATE_INTERVAL=24

# Docker Services
POSTGRES_PASSWORD=gradvy_secure_2024

# Flower Monitoring
FLOWER_PASSWORD=flower_admin_2024
EOF
    print_success ".env file created with MongoDB configuration!"
else
    print_status ".env file already exists."
    
    # Check if MongoDB configuration exists
    if ! grep -q "MONGODB_URI" .env; then
        print_status "Adding MongoDB configuration to existing .env file..."
        cat >> .env << 'EOF'

# MongoDB Configuration (Docker MongoDB)
MONGODB_URI=mongodb://gradvy_app:gradvy_app_secure_2024@localhost:27017/gradvy_preferences
MONGO_ROOT_USERNAME=gradvy_admin
MONGO_ROOT_PASSWORD=gradvy_mongo_secure_2024
MONGO_DB=gradvy_preferences
MONGO_PORT=27017

# Preferences App Settings
PREFERENCES_CACHE_TIMEOUT=3600
RECOMMENDATIONS_EXPIRY_DAYS=7
ANALYTICS_RETENTION_MONTHS=12
AI_INSIGHTS_UPDATE_INTERVAL=24
EOF
        print_success "MongoDB configuration added to .env file!"
    else
        print_status "MongoDB configuration already exists in .env file."
    fi
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x scripts/*.sh

# Test MongoDB dependencies
print_status "Testing MongoDB dependencies..."
cd core
if python -c "import mongoengine, pymongo; print('MongoDB dependencies: OK')" 2>/dev/null; then
    print_success "MongoDB dependencies installed and working!"
else
    print_warning "MongoDB dependencies test failed. Installing additional packages..."
    cd ..
    source venv/scripts/activate
    pip install pymongo==4.6.0 mongoengine==0.27.0 dnspython==2.4.2
    cd core
    if python -c "import mongoengine, pymongo; print('MongoDB dependencies: OK')" 2>/dev/null; then
        print_success "MongoDB dependencies installed successfully!"
    else
        print_error "Failed to install MongoDB dependencies!"
    fi
fi
cd ..

print_success "Local environment setup complete! 🎉"
echo ""
echo "🔧 What was set up:"
echo "   ✅ Python virtual environment (venv/)"
echo "   ✅ Python dependencies installed"
echo "   ✅ MongoDB dependencies verified"
echo "   ✅ Environment configuration (.env) with MongoDB"
echo "   ✅ Executable scripts"
echo ""
echo "🚀 Next steps:"
echo "   1. Start data services:      ./scripts/data-start.sh"
echo "   2. Check MongoDB status:     ./scripts/mongodb-status.sh"
echo "   3. Run migrations:           ./scripts/local-migrate.sh"
echo "   4. Seed preferences data:    ./scripts/preferences-seed.sh"
echo "   5. Create superuser:         ./scripts/local-superuser.sh"
echo "   6. Start Django:             ./scripts/local-dev.sh"
echo "   7. Start Celery (optional):  ./scripts/local-celery.sh"
echo "   8. Start Flower (optional):  ./scripts/local-flower.sh"
echo ""
echo "📊 MongoDB Tools:"
echo "   • Status check:   ./scripts/mongodb-status.sh"
echo "   • Backup data:    ./scripts/mongodb-backup.sh (coming soon)"
echo "   • Reset data:     ./scripts/preferences-reset.sh (coming soon)"
echo ""
echo "📚 Documentation:"
echo "   • Check README.md for detailed instructions"
echo "   • Edit .env file to customize configuration"
echo "   • MongoDB runs on localhost:27017"