#!/bin/bash
# Gradvy Preferences Data Reset
# Safely resets MongoDB preferences data for development

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
    echo -e "${CYAN}[PREFERENCES RESET]${NC} $1"
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

# Function to ask yes/no question
ask_yes_no() {
    local question="$1"
    local response
    while true; do
        echo -ne "${YELLOW}[QUESTION]${NC} $question (yes/no): "
        read -r response
        case $response in
            [Yy]es|[Yy]) return 0;;
            [Nn]o|[Nn]) return 1;;
            *) echo "Please answer yes or no.";;
        esac
    done
}

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

# MongoDB connection details
MONGO_HOST=${MONGO_HOST:-localhost}
MONGO_PORT=${MONGO_PORT:-27017}
MONGO_DB=${MONGO_DB:-gradvy_preferences}

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
echo "║                        🧹 Preferences Data Reset                                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
echo ""

print_warning "⚠️  This will DELETE ALL preferences data from MongoDB!"
echo ""
print_info "This includes:"
echo "   • All user preferences and settings"
echo "   • Learning sessions and activity history"
echo "   • Course recommendations"
echo "   • AI training data"
echo "   • User interaction logs"
echo ""
print_info "This will NOT affect:"
echo "   • Django user accounts (PostgreSQL)"
echo "   • Django app data"
echo "   • System configurations"
echo ""

# Safety check - only allow in development
if [ "${DJANGO_DEBUG:-False}" != "True" ] && [ "${NODE_ENV:-development}" = "production" ]; then
    print_error "🚫 SAFETY BLOCK: Cannot reset data in production environment!"
    print_info "This script only works in development mode."
    exit 1
fi

# Confirm action
if ! ask_yes_no "Are you sure you want to reset ALL preferences data?"; then
    print_info "Reset cancelled. No data was modified."
    exit 0
fi

echo ""
print_header "Environment Validation"

# Check if MongoDB is running
if ! docker ps --format "table {{.Names}}" | grep -q "gradvy-mongodb"; then
    print_error "MongoDB container is not running!"
    print_info "Start data services: ./scripts/data-start.sh"
    exit 1
fi

if ! docker exec gradvy-mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
    print_error "Cannot connect to MongoDB!"
    print_info "Check MongoDB status: ./scripts/mongodb-status.sh"
    exit 1
fi

print_success "MongoDB connection verified"

echo ""
print_header "Current Data Status"

# Show current data counts
collections=("user_preferences" "learning_sessions" "course_recommendations" "ai_training_data")

echo "📊 Current data counts:"
total_documents=0
for collection in "${collections[@]}"; do
    count=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "db.$collection.countDocuments({})" 2>/dev/null || echo "0")
    echo "   • $collection: $count documents"
    total_documents=$((total_documents + count))
done

echo "   📄 Total documents: $total_documents"

if [ "$total_documents" -eq 0 ]; then
    print_info "No data found to reset. Database is already clean."
    exit 0
fi

echo ""

# Final confirmation
print_warning "⚠️  FINAL CONFIRMATION"
echo "You are about to delete $total_documents documents from MongoDB."
echo ""

if ! ask_yes_no "Type 'yes' to proceed with data deletion"; then
    print_info "Reset cancelled. No data was modified."
    exit 0
fi

echo ""
print_header "Resetting Data"

# Create backup before deletion (optional)
backup_timestamp=$(date +"%Y%m%d_%H%M%S")
backup_file="preferences_backup_${backup_timestamp}.json"

print_info "Creating backup before deletion..."
if docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "
const collections = ['user_preferences', 'learning_sessions', 'course_recommendations', 'ai_training_data'];
const backup = {};
collections.forEach(col => {
    backup[col] = db[col].find({}).toArray();
});
print(JSON.stringify(backup, null, 2));
" > "$backup_file" 2>/dev/null; then
    print_success "Backup created: $backup_file"
else
    print_warning "Backup creation failed, but continuing with reset..."
fi

# Reset each collection
echo ""
print_info "Resetting collections..."

for collection in "${collections[@]}"; do
    print_info "Deleting $collection..."
    result=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "
        const result = db.$collection.deleteMany({});
        print('Deleted: ' + result.deletedCount + ' documents');
    " 2>/dev/null || echo "Error")
    
    if echo "$result" | grep -q "Deleted:"; then
        deleted_count=$(echo "$result" | grep "Deleted:" | cut -d' ' -f2)
        print_success "  ✓ $collection: $deleted_count documents deleted"
    else
        print_warning "  ⚠ $collection: Error during deletion"
    fi
done

echo ""
print_header "Verification"

# Verify deletion
echo "📊 Post-reset data counts:"
total_remaining=0
for collection in "${collections[@]}"; do
    count=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "db.$collection.countDocuments({})" 2>/dev/null || echo "0")
    echo "   • $collection: $count documents"
    total_remaining=$((total_remaining + count))
done

echo "   📄 Total remaining: $total_remaining documents"

if [ "$total_remaining" -eq 0 ]; then
    print_success "✅ All preferences data successfully reset!"
else
    print_warning "⚠️  Some data may still remain ($total_remaining documents)"
fi

echo ""
print_header "Next Steps"

echo "🚀 Recommended actions:"
echo "   1. Seed fresh data:    ./scripts/preferences-seed.sh"
echo "   2. Check status:       ./scripts/mongodb-status.sh"
echo "   3. Start Django:       ./scripts/local-dev.sh"
echo ""

if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
    echo "💾 Backup information:"
    echo "   • Backup file: $backup_file"
    echo "   • To restore: mongoimport or mongosh restore commands"
    echo "   • Auto-cleanup: backups older than 7 days will be cleaned"
    echo ""
    
    # Clean old backups (keep last 7 days)
    find . -name "preferences_backup_*.json" -mtime +7 -delete 2>/dev/null || true
fi

echo "✨ Reset completed successfully!"
echo ""