#!/bin/bash
# Gradvy Preferences Data Seeding
# Seeds MongoDB with realistic test data for development

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
    echo -e "${CYAN}[PREFERENCES SEED]${NC} $1"
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
echo "║                        🌱 Preferences Data Seeding                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists and MongoDB is running
print_header "Environment Validation"

if [ ! -d "venv" ]; then
    print_error "Virtual environment not found! Run ./scripts/local-setup.sh first."
    exit 1
fi

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

print_success "Environment validation passed!"

echo ""

# Check if Django models are accessible
print_header "Django Models Validation"

cd core
source ../venv/bin/activate

# Test Django setup
if ! python manage.py check --database default >/dev/null 2>&1; then
    print_error "Django configuration issues detected!"
    print_info "Run migrations: ./scripts/local-migrate.sh"
    cd ..
    exit 1
fi

print_success "Django models accessible!"

echo ""

# Create seeding script
print_header "Generating Sample Data"

python manage.py shell << 'EOF'
import os
import sys
from datetime import datetime, timedelta
from random import choice, randint, sample
from django.contrib.auth.models import User
from apps.preferences.models import (
    UserPreference, BasicInfo, ContentPreferences, AIInsights, 
    InteractionData, LearningSession, ActivityData, DeviceInfo,
    CourseRecommendation, RecommendationItem, AITrainingData
)

print("🌱 Starting preferences data seeding...")

# Sample data definitions
LEARNING_GOALS = [
    'web_dev', 'mobile_dev', 'ai_ml', 'data_science', 'devops', 
    'design', 'business', 'marketing', 'finance', 'languages'
]

EXPERIENCE_LEVELS = ['complete_beginner', 'some_basics', 'intermediate', 'advanced']
LEARNING_PACES = ['slow', 'medium', 'fast']
TIME_AVAILABILITIES = ['1-2hrs', '3-5hrs', '5+hrs']
LEARNING_STYLES = ['visual', 'hands_on', 'reading', 'videos', 'interactive']
CAREER_STAGES = ['student', 'career_change', 'skill_upgrade', 'professional']
TARGET_TIMELINES = ['3months', '6months', '1year', 'flexible']
PLATFORMS = ['udemy', 'coursera', 'youtube', 'edx', 'pluralsight', 'linkedin_learning']
CONTENT_TYPES = ['video', 'article', 'interactive', 'quiz', 'project', 'book']
LANGUAGES = ['english', 'spanish', 'french', 'german']

# Create sample users if they don't exist
sample_users = []
for i in range(1, 11):
    username = f'test_user_{i}'
    try:
        user = User.objects.get(username=username)
        sample_users.append(user)
        print(f"✓ Using existing user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=f'test{i}@gradvy.com',
            password='testpass123',
            first_name=f'Test',
            last_name=f'User{i}'
        )
        sample_users.append(user)
        print(f"✓ Created user: {username}")

print(f"✓ Created/verified {len(sample_users)} test users")

# Clear existing preferences for clean seeding
UserPreference.objects.filter(user_id__in=[u.id for u in sample_users]).delete()
LearningSession.objects.filter(user_id__in=[u.id for u in sample_users]).delete()
CourseRecommendation.objects.filter(user_id__in=[u.id for u in sample_users]).delete()
AITrainingData.objects.filter(user_id__in=[u.id for u in sample_users]).delete()
print("✓ Cleaned existing test data")

# Create diverse user preferences
for i, user in enumerate(sample_users):
    print(f"📋 Creating preferences for {user.username}...")
    
    # Create varied preference profiles
    basic_info = BasicInfo(
        learning_goals=sample(LEARNING_GOALS, randint(1, 4)),
        experience_level=choice(EXPERIENCE_LEVELS),
        preferred_pace=choice(LEARNING_PACES),
        time_availability=choice(TIME_AVAILABILITIES),
        learning_style=sample(LEARNING_STYLES, randint(1, 3)),
        career_stage=choice(CAREER_STAGES),
        target_timeline=choice(TARGET_TIMELINES)
    )
    
    content_preferences = ContentPreferences(
        preferred_platforms=sample(PLATFORMS, randint(2, 4)),
        content_types=sample(CONTENT_TYPES, randint(2, 4)),
        difficulty_preference='mixed',
        duration_preference='mixed',
        language_preference=sample(LANGUAGES, randint(1, 2)),
        instructor_ratings_min=choice([3.0, 3.5, 4.0, 4.5])
    )
    
    # Create user preference
    user_pref = UserPreference(
        user_id=user.id,
        basic_info=basic_info,
        content_preferences=content_preferences,
        created_at=datetime.utcnow() - timedelta(days=randint(1, 30))
    )
    user_pref.save()
    
    # Add some interactions
    interaction_types = ['course_click', 'video_watch', 'search', 'bookmark', 'course_enroll']
    for j in range(randint(5, 15)):
        interaction = InteractionData(
            type=choice(interaction_types),
            data={
                'course_id': f'course_{randint(1, 100)}',
                'duration': randint(300, 3600),
                'rating': randint(3, 5)
            },
            timestamp=datetime.utcnow() - timedelta(hours=randint(1, 720)),
            context={'source': 'web', 'page': 'dashboard'}
        )
        user_pref.interactions.append(interaction)
    
    user_pref.save()
    print(f"  ✓ Created {len(user_pref.interactions)} interactions")

print(f"✓ Created preferences for {len(sample_users)} users")

# Create sample learning sessions
session_count = 0
for user in sample_users:
    for session_num in range(randint(2, 8)):
        session_id = f"session_{user.id}_{session_num}_{randint(1000, 9999)}"
        
        start_time = datetime.utcnow() - timedelta(hours=randint(1, 168))
        duration = randint(600, 7200)  # 10 minutes to 2 hours
        
        session = LearningSession(
            user_id=user.id,
            session_id=session_id,
            start_time=start_time,
            end_time=start_time + timedelta(seconds=duration),
            duration=duration,
            device_info=DeviceInfo(
                type=choice(['desktop', 'mobile', 'tablet']),
                os=choice(['Windows', 'macOS', 'iOS', 'Android']),
                browser=choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
            )
        )
        
        # Add activities to session
        activity_types = ['course_view', 'video_watch', 'quiz_attempt', 'coding_practice']
        for activity_num in range(randint(1, 5)):
            activity = ActivityData(
                activity_type=choice(activity_types),
                content_id=f'content_{randint(1, 50)}',
                duration=randint(60, 1200),
                completion_rate=randint(50, 100) / 100.0,
                metadata={'difficulty': choice(['easy', 'medium', 'hard'])}
            )
            session.activities.append(activity)
        
        session.save()
        session_count += 1

print(f"✓ Created {session_count} learning sessions")

# Create sample course recommendations
recommendations_count = 0
for user in sample_users:
    # Create 1-2 recommendation sets per user
    for rec_set in range(randint(1, 2)):
        expires_at = datetime.utcnow() + timedelta(days=randint(1, 7))
        
        course_rec = CourseRecommendation(
            user_id=user.id,
            expires_at=expires_at,
            algorithm_version='1.0.0',
            generation_context={
                'user_goals': UserPreference.get_by_user_id(user.id).basic_info.learning_goals,
                'experience_level': UserPreference.get_by_user_id(user.id).basic_info.experience_level
            }
        )
        
        # Add recommendation items
        for rec_num in range(randint(5, 15)):
            platforms = ['udemy', 'coursera', 'youtube', 'edx']
            titles = [
                'Complete Python Bootcamp', 'React for Beginners', 'Data Science Fundamentals',
                'Machine Learning A-Z', 'JavaScript Masterclass', 'Web Development Complete',
                'AI and Deep Learning', 'Mobile App Development', 'Cloud Computing Basics'
            ]
            
            recommendation = RecommendationItem(
                course_id=f'course_{randint(1, 200)}',
                platform=choice(platforms),
                title=choice(titles),
                score=randint(70, 95) / 100.0,
                reasoning=[
                    choice(['matches_learning_goals', 'suitable_for_experience_level', 'popular_choice']),
                    choice(['high_rating', 'recent_content', 'comprehensive_curriculum'])
                ],
                metadata={
                    'duration': f'{randint(10, 50)} hours',
                    'rating': randint(40, 50) / 10.0,
                    'students': randint(1000, 50000)
                }
            )
            course_rec.recommendations.append(recommendation)
        
        course_rec.save()
        recommendations_count += 1

print(f"✓ Created {recommendations_count} recommendation sets")

# Create sample AI training data
training_data_count = 0
event_types = ['positive_feedback', 'negative_feedback', 'course_completion', 'course_abandonment']

for user in sample_users:
    for event_num in range(randint(3, 10)):
        training_data = AITrainingData(
            user_id=user.id,
            event_type=choice(event_types),
            timestamp=datetime.utcnow() - timedelta(hours=randint(1, 720)),
            event_data={
                'course_id': f'course_{randint(1, 100)}',
                'completion_rate': randint(0, 100),
                'rating': randint(1, 5)
            },
            user_context={
                'session_length': randint(600, 3600),
                'device_type': choice(['desktop', 'mobile']),
                'time_of_day': choice(['morning', 'afternoon', 'evening'])
            },
            labels={
                'satisfaction_score': randint(1, 5),
                'likelihood_to_continue': choice([True, False])
            }
        )
        training_data.save()
        training_data_count += 1

print(f"✓ Created {training_data_count} AI training data points")

# Summary
print("\n" + "="*60)
print("🎉 Data seeding completed successfully!")
print("="*60)
print(f"📊 Summary:")
print(f"   👥 Users: {len(sample_users)}")
print(f"   ⚙️  Preferences: {UserPreference.objects.filter(user_id__in=[u.id for u in sample_users]).count()}")
print(f"   📚 Learning Sessions: {session_count}")
print(f"   🎯 Recommendations: {recommendations_count}")
print(f"   🤖 AI Training Data: {training_data_count}")
print("="*60)

# Test data retrieval
print("\n🔍 Testing data retrieval...")
sample_user = sample_users[0]
user_pref = UserPreference.get_by_user_id(sample_user.id)
if user_pref:
    print(f"✓ Retrieved preferences for {sample_user.username}")
    print(f"  Goals: {user_pref.basic_info.learning_goals}")
    print(f"  Experience: {user_pref.basic_info.experience_level}")
    print(f"  Interactions: {len(user_pref.interactions)}")
else:
    print("✗ Failed to retrieve sample preferences")

print("\n🌟 Seeding completed! Use ./scripts/mongodb-status.sh to view data")

EOF

cd ..

if [ $? -eq 0 ]; then
    print_success "Data seeding completed successfully! 🎉"
    echo ""
    echo "📊 What was created:"
    echo "   • 10 test users with realistic preferences"
    echo "   • Diverse learning goals and experience levels"
    echo "   • Sample learning sessions and activities"
    echo "   • Course recommendations with scoring"
    echo "   • AI training data for personalization"
    echo ""
    echo "🔍 Next steps:"
    echo "   • Check data: ./scripts/mongodb-status.sh"
    echo "   • Start Django: ./scripts/local-dev.sh"
    echo "   • Test APIs via Django admin or API endpoints"
    echo ""
    echo "👥 Test Users (password: testpass123):"
    echo "   • test_user_1 through test_user_10"
    echo "   • Email format: test[N]@gradvy.com"
    echo ""
    echo "🚀 Ready for development and testing!"
else
    print_error "Data seeding failed!"
    print_info "Check Django setup and MongoDB connectivity"
    print_info "Debug with: ./scripts/mongodb-status.sh"
fi

echo ""