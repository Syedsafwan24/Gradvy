#!/bin/bash

# Gradvy Backend - Automated Developer Setup Script
# This script sets up the complete development environment for new developers

set -e  # Exit on any error

echo "🚀 Welcome to Gradvy Backend Setup!"
echo "===================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Check if running on Windows (Git Bash/WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    WINDOWS=true
    print_status "Detected Windows environment"
else
    WINDOWS=false
    print_status "Detected Unix-like environment"
fi

# Step 1: Check Prerequisites
print_status "Step 1: Checking prerequisites..."

# Check Git
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi
print_success "Git is installed"

# Check Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    print_error "Python is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    if [[ "$PYTHON_VERSION" == 3.* ]]; then
        PYTHON_CMD="python"
    fi
fi

print_success "Python is installed: $(${PYTHON_CMD} --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker Desktop first."
    exit 1
fi
print_success "Docker is installed: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is available"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL client (psql) not found. You might need to install it."
    print_warning "The setup will continue, but database commands might not work."
else
    print_success "PostgreSQL client is installed"
fi

echo ""

# Step 2: Clone Repository (if needed)
print_status "Step 2: Setting up project directory..."

if [[ ! -f "manage.py" && ! -f "core/manage.py" ]]; then
    print_status "It looks like you're not in the project directory."
    print_status "Please run this script from the core-backend project root directory."
    exit 1
fi

print_success "Project directory confirmed"

# Step 3: Create Virtual Environment
print_status "Step 3: Setting up Python virtual environment..."

if [[ ! -d "venv" ]]; then
    print_status "Creating virtual environment..."
    ${PYTHON_CMD} -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
if [[ "$WINDOWS" == true ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
print_success "Virtual environment activated"

# Step 4: Install Python Dependencies
print_status "Step 4: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Step 5: Environment Configuration
print_status "Step 5: Setting up environment configuration..."

if [[ ! -f "core/.env" ]]; then
    print_status "Creating environment configuration file..."
    cp .env.example core/.env 2>/dev/null || cat > core/.env << 'EOF'
# Database Configuration
POSTGRES_DB=gradvy_db
POSTGRES_USER=gradvy_user
POSTGRES_PASSWORD=gradvy_pass123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
USE_TLS=False
EOF
    print_success "Environment file created: core/.env"
else
    print_success "Environment file already exists"
fi

# Step 6: Database Setup
print_status "Step 6: Setting up PostgreSQL database..."

print_status "Creating database and user..."
if command -v psql &> /dev/null; then
    # Try to create database
    createdb gradvy_db 2>/dev/null || print_warning "Database might already exist"
    
    # Create user and grant permissions
    psql -d gradvy_db -c "
    DO \$\$
    BEGIN
        CREATE USER gradvy_user WITH PASSWORD 'gradvy_pass123';
        EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'User already exists';
    END
    \$\$;
    
    GRANT ALL PRIVILEGES ON DATABASE gradvy_db TO gradvy_user;
    GRANT ALL ON SCHEMA public TO gradvy_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gradvy_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gradvy_user;
    ALTER USER gradvy_user CREATEDB;
    " 2>/dev/null || print_warning "Database setup encountered issues. You may need to set it up manually."
    
    print_success "Database setup completed"
else
    print_warning "PostgreSQL client not available. Please set up the database manually:"
    echo "  1. Create database: gradvy_db"
    echo "  2. Create user: gradvy_user with password: gradvy_pass123"
    echo "  3. Grant all privileges to gradvy_user on gradvy_db"
fi

# Step 7: Django Setup
print_status "Step 7: Setting up Django application..."

cd core

# Run migrations
print_status "Running database migrations..."
${PYTHON_CMD} manage.py makemigrations
${PYTHON_CMD} manage.py migrate
print_success "Database migrations completed"

# Create superuser (optional)
print_status "Would you like to create a Django superuser? (y/n)"
read -r create_superuser
if [[ "$create_superuser" == "y" || "$create_superuser" == "Y" ]]; then
    print_status "Creating Django superuser..."
    ${PYTHON_CMD} manage.py createsuperuser
    print_success "Superuser created"
fi

cd ..

# Step 8: Docker Setup
print_status "Step 8: Setting up Docker containers for Celery and Redis..."

print_status "Building and starting Docker containers..."
docker-compose down 2>/dev/null || true
docker-compose up --build -d

# Wait for containers to start
print_status "Waiting for containers to start..."
sleep 10

# Check container status
REDIS_STATUS=$(docker ps --filter "name=gradvy-redis" --format "table {{.Status}}" | tail -n +2)
WORKER_STATUS=$(docker ps --filter "name=gradvy-celery-worker" --format "table {{.Status}}" | tail -n +2)

if [[ "$REDIS_STATUS" == *"Up"* ]]; then
    print_success "Redis container is running"
else
    print_warning "Redis container might have issues"
fi

if [[ "$WORKER_STATUS" == *"Up"* ]]; then
    print_success "Celery worker container is running"
else
    print_warning "Celery worker container might have issues"
fi

# Step 9: Test Setup
print_status "Step 9: Testing the setup..."

# Test Django
print_status "Testing Django setup..."
cd core
${PYTHON_CMD} manage.py check
if [[ $? -eq 0 ]]; then
    print_success "Django setup is working"
else
    print_error "Django setup has issues"
fi

# Test Redis connection
print_status "Testing Redis connection..."
docker exec gradvy-redis redis-cli ping > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    print_success "Redis is working"
else
    print_error "Redis connection failed"
fi

# Test Celery task
print_status "Testing Celery task execution..."
TASK_RESULT=$(${PYTHON_CMD} manage.py shell -c "
from apps.accounts.tasks import send_welcome_email
result = send_welcome_email.delay('test@setup.com')
print(f'Task ID: {result.task_id}')
" 2>/dev/null)

if [[ "$TASK_RESULT" == *"Task ID:"* ]]; then
    print_success "Celery task execution working"
else
    print_warning "Celery task execution might have issues"
fi

cd ..

# Step 10: Final Instructions
echo ""
print_success "🎉 Setup completed successfully!"
echo "=============================="
echo ""
echo "Your Gradvy Backend development environment is ready!"
echo ""
echo "📋 Next Steps:"
echo "  1. Start the Django development server:"
echo "     cd core && python manage.py runserver"
echo ""
echo "  2. Access the application:"
echo "     • Django API: http://localhost:8000"
echo "     • Django Admin: http://localhost:8000/admin"
echo "     • Flower (Celery Monitor): http://localhost:5555"
echo ""
echo "  3. Useful commands:"
echo "     • Start Docker services: docker-compose up -d"
echo "     • Stop Docker services: docker-compose down"
echo "     • View logs: docker-compose logs -f"
echo "     • Run tests: python manage.py test"
echo ""
echo "📚 Documentation:"
echo "  • See docs/ folder for detailed guides"
echo "  • API documentation will be available at /api/docs/"
echo ""
echo "🛠️  Development workflow:"
echo "  1. Always activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "  2. Make sure Docker containers are running before testing Celery tasks"
echo "  3. Run migrations after model changes: python manage.py makemigrations && python manage.py migrate"
echo ""
print_success "Happy coding! 🚀"
