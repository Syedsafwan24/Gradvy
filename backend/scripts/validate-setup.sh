#!/bin/bash
# Gradvy Complete System Validation
# Comprehensive health check for all system components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}[SYSTEM VALIDATION]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

# Test counters
tests_passed=0
tests_failed=0
tests_warning=0

# Function to track test results
track_test() {
    local status=$1
    local message=$2
    
    case $status in
        "pass")
            print_success "$message"
            ((tests_passed++))
            ;;
        "fail")
            print_error "$message"
            ((tests_failed++))
            ;;
        "warn")
            print_warning "$message"
            ((tests_warning++))
            ;;
    esac
}

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
echo "║                        🔍 Complete System Validation                            ║"
echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Environment Setup Validation
print_header "Environment Setup"

# Check Python virtual environment
if [ -d "venv" ]; then
    track_test "pass" "Virtual environment exists"
    
    # Check if virtual environment has required packages
    if [ -f "venv/scripts/activate" ]; then
        source venv/scripts/activate
        
        # Test Django
        if python -c "import django; print(f'Django {django.get_version()}')" >/dev/null 2>&1; then
            django_version=$(python -c "import django; print(django.get_version())" 2>/dev/null)
            track_test "pass" "Django installed ($django_version)"
        else
            track_test "fail" "Django not installed or accessible"
        fi
        
        # Test MongoDB dependencies
        if python -c "import mongoengine, pymongo" >/dev/null 2>&1; then
            track_test "pass" "MongoDB dependencies installed"
        else
            track_test "fail" "MongoDB dependencies missing"
        fi
        
        # Test REST Framework
        if python -c "import rest_framework" >/dev/null 2>&1; then
            track_test "pass" "Django REST Framework installed"
        else
            track_test "fail" "Django REST Framework missing"
        fi
    else
        track_test "fail" "Virtual environment corrupted"
    fi
else
    track_test "fail" "Virtual environment not found"
fi

# Check .env file
if [ -f ".env" ]; then
    track_test "pass" ".env configuration file exists"
    
    # Check for required variables
    required_vars=("DJANGO_SECRET_KEY" "DB_NAME" "MONGODB_URI" "CELERY_BROKER_URL")
    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" .env; then
            track_test "pass" "$var configured in .env"
        else
            track_test "fail" "$var missing from .env"
        fi
    done
else
    track_test "fail" ".env configuration file missing"
fi

echo ""

# 2. Docker Services Validation
print_header "Docker Services"

# Check Docker
if command -v docker >/dev/null 2>&1; then
    track_test "pass" "Docker installed"
    
    if docker ps >/dev/null 2>&1; then
        track_test "pass" "Docker daemon running"
    else
        track_test "fail" "Docker daemon not running"
    fi
else
    track_test "fail" "Docker not installed"
fi

# Check Docker Compose
if command -v docker-compose >/dev/null 2>&1; then
    track_test "pass" "Docker Compose installed"
else
    track_test "fail" "Docker Compose not installed"
fi

# Check individual containers
services=("gradvy-postgres" "gradvy-redis" "gradvy-mongodb")
for service in "${services[@]}"; do
    if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
        track_test "pass" "$service container running"
    else
        track_test "fail" "$service container not running"
    fi
done

echo ""

# 3. Database Connectivity
print_header "Database Connectivity"

# PostgreSQL
if docker exec gradvy-postgres pg_isready -U gradvy_user -d gradvy_db >/dev/null 2>&1; then
    track_test "pass" "PostgreSQL connection successful"
else
    track_test "fail" "PostgreSQL connection failed"
fi

# Redis
if docker exec gradvy-redis redis-cli ping >/dev/null 2>&1; then
    track_test "pass" "Redis connection successful"
else
    track_test "fail" "Redis connection failed"
fi

# MongoDB
if docker exec gradvy-mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
    track_test "pass" "MongoDB connection successful"
    
    # Check MongoDB database
    if docker exec gradvy-mongodb mongosh gradvy_preferences --eval "db.stats()" >/dev/null 2>&1; then
        track_test "pass" "MongoDB database 'gradvy_preferences' accessible"
    else
        track_test "warn" "MongoDB database 'gradvy_preferences' not initialized"
    fi
    
    # Check MongoDB collections
    collections=("user_preferences" "learning_sessions" "course_recommendations" "ai_training_data")
    for collection in "${collections[@]}"; do
        if docker exec gradvy-mongodb mongosh gradvy_preferences --quiet --eval "db.$collection.countDocuments({})" >/dev/null 2>&1; then
            count=$(docker exec gradvy-mongodb mongosh gradvy_preferences --quiet --eval "db.$collection.countDocuments({})" 2>/dev/null || echo "0")
            track_test "pass" "MongoDB collection '$collection' accessible ($count documents)"
        else
            track_test "warn" "MongoDB collection '$collection' not found"
        fi
    done
else
    track_test "fail" "MongoDB connection failed"
fi

echo ""

# 4. Django Application Validation
print_header "Django Application"

if [ -d "venv" ] && [ -f "venv/scripts/activate" ]; then
    source venv/scripts/activate
    cd core
    
    # Django check
    if python manage.py check --database default >/dev/null 2>&1; then
        track_test "pass" "Django system check passed"
    else
        track_test "fail" "Django system check failed"
    fi
    
    # Database migrations
    migration_status=$(python manage.py showmigrations --plan 2>/dev/null | grep -c "[ ]" || echo "0")
    if [ "$migration_status" -eq 0 ]; then
        track_test "pass" "All Django migrations applied"
    else
        track_test "warn" "$migration_status pending migrations"
    fi
    
    # MongoDB connection from Django
    mongodb_django_check=$(python -c "
try:
    import mongoengine
    from core.settings import MONGODB_SETTINGS
    mongoengine.connect(**MONGODB_SETTINGS)
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>/dev/null)
    
    if echo "$mongodb_django_check" | grep -q "OK"; then
        track_test "pass" "Django MongoDB connection successful"
    else
        track_test "fail" "Django MongoDB connection failed"
    fi
    
    # Test preferences app
    if python -c "from apps.preferences.models import UserPreference" >/dev/null 2>&1; then
        track_test "pass" "Preferences app models accessible"
    else
        track_test "fail" "Preferences app models not accessible"
    fi
    
    cd ..
else
    track_test "fail" "Cannot validate Django (environment issues)"
fi

echo ""

# 5. API Endpoints Validation
print_header "API Endpoints"

# This would require Django to be running, so we'll just check URL configuration
if [ -f "core/core/urls.py" ]; then
    if grep -q "api/preferences/" core/core/urls.py; then
        track_test "pass" "Preferences API URLs configured"
    else
        track_test "fail" "Preferences API URLs not configured"
    fi
    
    if grep -q "api/auth/" core/core/urls.py; then
        track_test "pass" "Authentication API URLs configured"
    else
        track_test "fail" "Authentication API URLs not configured"
    fi
else
    track_test "fail" "Django URL configuration not found"
fi

echo ""

# 6. Script Validation
print_header "Scripts Validation"

scripts=(
    "mongodb-status.sh"
    "preferences-seed.sh" 
    "preferences-reset.sh"
    "local-setup.sh"
    "data-start.sh"
    "local-dev.sh"
    "local-migrate.sh"
    "local-superuser.sh"
)

for script in "${scripts[@]}"; do
    if [ -f "scripts/$script" ] && [ -x "scripts/$script" ]; then
        track_test "pass" "Script $script exists and executable"
    else
        track_test "fail" "Script $script missing or not executable"
    fi
done

echo ""

# 7. Network and Ports
print_header "Network and Ports"

ports=("5432:PostgreSQL" "6380:Redis" "27017:MongoDB")
for port_info in "${ports[@]}"; do
    port=$(echo "$port_info" | cut -d: -f1)
    service=$(echo "$port_info" | cut -d: -f2)
    
    if nc -z localhost "$port" 2>/dev/null; then
        track_test "pass" "$service port $port accessible"
    else
        track_test "fail" "$service port $port not accessible"
    fi
done

echo ""

# 8. File Structure Validation
print_header "File Structure"

required_files=(
    "docker-compose.yml"
    "requirements.txt"
    "core/manage.py"
    "core/core/settings.py"
    "core/apps/preferences/models.py"
    "core/apps/preferences/views.py"
    "scripts/mongodb-init/01-init-gradvy-db.js"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        track_test "pass" "Required file $file exists"
    else
        track_test "fail" "Required file $file missing"
    fi
done

echo ""

# Summary Report
print_header "Validation Summary"

total_tests=$((tests_passed + tests_failed + tests_warning))

echo "╔════════════════════════════════════════╗"
echo "║               📊 Results               ║"
echo "╠════════════════════════════════════════╣"
echo "║ ✅ Passed:   $(printf "%3d" $tests_passed) / $(printf "%-3d" $total_tests)                    ║"
echo "║ ❌ Failed:   $(printf "%3d" $tests_failed) / $(printf "%-3d" $total_tests)                    ║"
echo "║ ⚠️  Warnings: $(printf "%3d" $tests_warning) / $(printf "%-3d" $total_tests)                    ║"
echo "╚════════════════════════════════════════╝"

echo ""

# Overall status
if [ $tests_failed -eq 0 ]; then
    if [ $tests_warning -eq 0 ]; then
        print_success "🎉 All systems operational! Perfect setup!"
        echo ""
        echo "🚀 Ready for development:"
        echo "   • Start services: ./scripts/data-start.sh"
        echo "   • Seed data: ./scripts/preferences-seed.sh"
        echo "   • Start Django: ./scripts/local-dev.sh"
    else
        print_warning "⚠️  System mostly operational with minor issues"
        echo ""
        echo "💡 Consider addressing warnings for optimal experience"
    fi
else
    print_error "❌ System has critical issues that need to be resolved"
    echo ""
    echo "🔧 Recommended fixes:"
    
    if [ $tests_failed -gt 0 ]; then
        echo "   1. Review failed tests above"
        echo "   2. Run: ./scripts/local-setup.sh"
        echo "   3. Start services: ./scripts/data-start.sh"
        echo "   4. Re-run validation: ./scripts/validate-setup.sh"
    fi
fi

echo ""

# Exit with appropriate code
if [ $tests_failed -eq 0 ]; then
    exit 0
else
    exit 1
fi