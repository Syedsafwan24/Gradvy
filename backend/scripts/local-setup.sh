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
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing Python dependencies..."
pip install -r requirements.txt

print_success "Python dependencies installed!"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << 'EOF'
# Gradvy Hybrid Development Environment
# PostgreSQL and Redis in Docker, Django/Celery local

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

# Docker Services
POSTGRES_PASSWORD=gradvy_secure_2024

# Flower Monitoring
FLOWER_PASSWORD=flower_admin_2024
EOF
    print_success ".env file created with default values!"
else
    print_status ".env file already exists."
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x scripts/*.sh

print_success "Local environment setup complete! 🎉"
echo ""
echo "🔧 What was set up:"
echo "   ✅ Python virtual environment (venv/)"
echo "   ✅ Python dependencies installed"
echo "   ✅ Environment configuration (.env)"
echo "   ✅ Executable scripts"
echo ""
echo "🚀 Next steps:"
echo "   1. Start data services:    ./scripts/data-start.sh"
echo "   2. Run migrations:         ./scripts/local-migrate.sh"
echo "   3. Create superuser:       ./scripts/local-superuser.sh"
echo "   4. Start Django:           ./scripts/local-dev.sh"
echo "   5. Start Celery (optional): ./scripts/local-celery.sh"
echo "   6. Start Flower (optional): ./scripts/local-flower.sh"
echo ""
echo "📚 Documentation:"
echo "   • Check README.md for detailed instructions"
echo "   • Edit .env file to customize configuration"