#!/bin/bash
# Gradvy MongoDB Status and Health Monitoring
# Comprehensive MongoDB health check and status reporting

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
    echo -e "${CYAN}[MONGODB STATUS]${NC} $1"
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

# Load environment variables
cd "$(dirname "$0")/.."
if [ -f ".env" ]; then
    source .env
fi

# MongoDB connection details
MONGO_HOST=${MONGO_HOST:-localhost}
MONGO_PORT=${MONGO_PORT:-27017}
MONGO_DB=${MONGO_DB:-gradvy_preferences}
MONGO_ROOT_USERNAME=${MONGO_ROOT_USERNAME:-gradvy_admin}
MONGO_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD:-gradvy_mongo_secure_2024}
MONGO_APP_USER=${MONGO_APP_USER:-gradvy_app}

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════════╗"
echo "║                           🍃 MongoDB Health Status Report                       ║"
echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if MongoDB container is running
print_header "Container Status Check"
if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "gradvy-mongodb"; then
    container_status=$(docker ps --format "{{.Status}}" --filter "name=gradvy-mongodb")
    print_success "MongoDB container is running: $container_status"
    
    # Check container health
    health_status=$(docker inspect --format='{{.State.Health.Status}}' gradvy-mongodb 2>/dev/null || echo "no-health-check")
    if [ "$health_status" = "healthy" ]; then
        print_success "Container health check: $health_status"
    elif [ "$health_status" = "no-health-check" ]; then
        print_warning "No health check configured for container"
    else
        print_error "Container health check: $health_status"
    fi
else
    print_error "MongoDB container is not running!"
    echo ""
    print_info "To start MongoDB: ./scripts/data-start.sh"
    exit 1
fi

echo ""

# Check MongoDB connectivity
print_header "Database Connectivity"
if docker exec gradvy-mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
    print_success "MongoDB server is responding"
    
    # Get MongoDB version
    mongo_version=$(docker exec gradvy-mongodb mongosh --quiet --eval "db.version()" 2>/dev/null)
    print_info "MongoDB version: $mongo_version"
else
    print_error "Cannot connect to MongoDB server!"
    exit 1
fi

echo ""

# Check database and collections
print_header "Database Structure"
if docker exec gradvy-mongodb mongosh $MONGO_DB --eval "db.stats()" >/dev/null 2>&1; then
    print_success "Database '$MONGO_DB' is accessible"
    
    # Get database stats
    db_size=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "db.stats().dataSize" 2>/dev/null)
    db_size_mb=$((db_size / 1024 / 1024))
    print_info "Database size: ${db_size_mb}MB"
    
    # Check collections
    echo ""
    print_info "Collections status:"
    
    collections=("user_preferences" "learning_sessions" "course_recommendations" "ai_training_data")
    for collection in "${collections[@]}"; do
        if docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "db.$collection.countDocuments({})" >/dev/null 2>&1; then
            count=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "db.$collection.countDocuments({})" 2>/dev/null)
            indexes=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "db.$collection.getIndexes().length" 2>/dev/null)
            print_success "  📄 $collection: $count documents, $indexes indexes"
        else
            print_warning "  📄 $collection: Collection not found or inaccessible"
        fi
    done
else
    print_error "Cannot access database '$MONGO_DB'!"
fi

echo ""

# Check user permissions
print_header "User Permissions"
if docker exec gradvy-mongodb mongosh $MONGO_DB -u $MONGO_APP_USER -p gradvy_app_secure_2024 --eval "db.user_preferences.findOne()" >/dev/null 2>&1; then
    print_success "Application user '$MONGO_APP_USER' has proper access"
else
    print_error "Application user '$MONGO_APP_USER' access issues!"
    print_info "Check user configuration in MongoDB init scripts"
fi

echo ""

# Performance metrics
print_header "Performance Metrics"
current_connections=$(docker exec gradvy-mongodb mongosh --quiet --eval "db.serverStatus().connections.current" 2>/dev/null || echo "N/A")
available_connections=$(docker exec gradvy-mongodb mongosh --quiet --eval "db.serverStatus().connections.available" 2>/dev/null || echo "N/A")
total_connections=$(docker exec gradvy-mongodb mongosh --quiet --eval "db.serverStatus().connections.totalCreated" 2>/dev/null || echo "N/A")

print_info "Connections - Current: $current_connections, Available: $available_connections"
print_info "Total connections created: $total_connections"

# Memory usage
opcounters_insert=$(docker exec gradvy-mongodb mongosh --quiet --eval "db.serverStatus().opcounters.insert" 2>/dev/null || echo "N/A")
opcounters_query=$(docker exec gradvy-mongodb mongosh --quiet --eval "db.serverStatus().opcounters.query" 2>/dev/null || echo "N/A")
opcounters_update=$(docker exec gradvy-mongodb mongosh --quiet --eval "db.serverStatus().opcounters.update" 2>/dev/null || echo "N/A")

print_info "Operations - Inserts: $opcounters_insert, Queries: $opcounters_query, Updates: $opcounters_update"

echo ""

# Recent activity check
print_header "Recent Activity"
echo ""
print_info "Recent user preferences (last 5):"
recent_prefs=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "
db.user_preferences.find({}, {user_id: 1, created_at: 1, updated_at: 1})
.sort({updated_at: -1})
.limit(5)
.forEach(function(doc) {
    print('  User ID: ' + doc.user_id + ', Updated: ' + doc.updated_at);
})
" 2>/dev/null || echo "  No data available")

if [ -n "$recent_prefs" ] && [ "$recent_prefs" != "  No data available" ]; then
    echo "$recent_prefs"
else
    print_warning "  No recent user preferences found"
fi

echo ""
print_info "Recent learning sessions (last 5):"
recent_sessions=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "
db.learning_sessions.find({}, {user_id: 1, start_time: 1, duration: 1})
.sort({start_time: -1})
.limit(5)
.forEach(function(doc) {
    print('  User ID: ' + doc.user_id + ', Duration: ' + (doc.duration || 0) + 's, Started: ' + doc.start_time);
})
" 2>/dev/null || echo "  No data available")

if [ -n "$recent_sessions" ] && [ "$recent_sessions" != "  No data available" ]; then
    echo "$recent_sessions"
else
    print_warning "  No recent learning sessions found"
fi

echo ""

# Index performance
print_header "Index Status"
print_info "Checking index usage on critical collections..."

for collection in "user_preferences" "learning_sessions"; do
    index_stats=$(docker exec gradvy-mongodb mongosh $MONGO_DB --quiet --eval "
    db.$collection.getIndexes().forEach(function(index) {
        print('  $collection.' + index.name + ': ' + JSON.stringify(index.key));
    })
    " 2>/dev/null || echo "  No indexes found")
    
    if [ -n "$index_stats" ] && [ "$index_stats" != "  No indexes found" ]; then
        echo "$index_stats"
    else
        print_warning "  No indexes found for $collection"
    fi
done

echo ""

# Network and ports
print_header "Network Configuration"
container_ip=$(docker inspect gradvy-mongodb --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null || echo "N/A")
port_mapping=$(docker port gradvy-mongodb 2>/dev/null || echo "No port mapping")

print_info "Container IP: $container_ip"
print_info "Port mapping: $port_mapping"

# Test external connectivity
if nc -z $MONGO_HOST $MONGO_PORT 2>/dev/null; then
    print_success "External connectivity test passed ($MONGO_HOST:$MONGO_PORT)"
else
    print_warning "External connectivity test failed ($MONGO_HOST:$MONGO_PORT)"
    print_info "This may be normal if accessing from outside Docker network"
fi

echo ""

# Storage information
print_header "Storage Information"
container_volumes=$(docker inspect gradvy-mongodb --format='{{range .Mounts}}{{.Source}} -> {{.Destination}} ({{.Type}}){{"\n"}}{{end}}' 2>/dev/null || echo "No volume info")
print_info "Volume mounts:"
echo "$container_volumes"

# Check available disk space
available_space=$(df -h $(docker inspect gradvy-mongodb --format='{{range .Mounts}}{{.Source}}{{end}}' 2>/dev/null | head -1) 2>/dev/null | tail -1 | awk '{print $4}' || echo "N/A")
print_info "Available disk space: $available_space"

echo ""

# Quick recommendations
print_header "Recommendations"
if [ "$current_connections" != "N/A" ] && [ "$current_connections" -gt 50 ]; then
    print_warning "High connection count ($current_connections). Consider connection pooling."
fi

if [ "$db_size_mb" -gt 100 ]; then
    print_info "Database size is ${db_size_mb}MB. Consider implementing data archiving strategy."
fi

echo ""

# Summary
print_header "Summary"
echo "╔════════════════════════════════════════╗"
echo "║             🚀 Quick Actions           ║"
echo "╠════════════════════════════════════════╣"
echo "║ 📊 Full logs: docker logs gradvy-mongodb"
echo "║ 🔄 Restart:   docker restart gradvy-mongodb"
echo "║ 💾 Backup:    ./scripts/mongodb-backup.sh"
echo "║ 🧹 Cleanup:   ./scripts/mongodb-cleanup.sh"
echo "║ 🌱 Seed data: ./scripts/preferences-seed.sh"
echo "╚════════════════════════════════════════╝"

echo ""
print_success "MongoDB status check completed! 🎉"
echo ""