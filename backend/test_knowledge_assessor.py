"""
Test Knowledge Assessor service
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ml_services.services.knowledge_assessor import KnowledgeAssessor
from datetime import datetime, timedelta


def test_beginner_assessment():
    """Test assessment for complete beginner."""
    print("\n" + "="*80)
    print("TEST 1: Complete Beginner Assessment")
    print("="*80)

    assessor = KnowledgeAssessor()

    user_data = {
        'user_id': 1,
        'learning_goals': ['python'],
        'experience_level': 'complete_beginner',
        'completed_courses': [],
        'quiz_scores': {},
        'skills': [],
        'last_activity': datetime.now(),
    }

    score = assessor.assess_user_knowledge(
        user_id=1,
        topic='python',
        user_data=user_data
    )

    print(f"\nKnowledge Score: {score.score}/100")
    print(f"Confidence: {score.confidence:.2f}")
    print(f"Contributing Factors: {score.contributing_factors}")

    # Get difficulty recommendation
    preferences = {'preferred_pace': 'medium'}
    recommendation = assessor.recommend_module_difficulty(score, preferences)

    print(f"\nDifficulty Recommendation:")
    print(f"  Optimal Start: {recommendation.optimal_starting_difficulty}")
    print(f"  Range: {recommendation.min_difficulty}-{recommendation.max_difficulty}")
    print(f"  Progression: {recommendation.progression_rate}")

    assert score.score <= 20, "Beginner should have low score"
    assert recommendation.optimal_starting_difficulty < 30, "Should recommend easy content"


def test_intermediate_with_skills():
    """Test assessment for user with related skills."""
    print("\n" + "="*80)
    print("TEST 2: Intermediate User with Related Skills")
    print("="*80)

    assessor = KnowledgeAssessor()

    user_data = {
        'user_id': 2,
        'learning_goals': ['react'],
        'experience_level': 'some_basics',
        'completed_courses': [
            {'title': 'JavaScript Basics', 'completed': True},
            {'title': 'HTML & CSS', 'completed': True}
        ],
        'quiz_scores': {'javascript_fundamentals': 75},
        'skills': ['javascript', 'html', 'css'],
        'last_activity': datetime.now(),
    }

    score = assessor.assess_user_knowledge(
        user_id=2,
        topic='react',
        user_data=user_data
    )

    print(f"\nKnowledge Score: {score.score}/100")
    print(f"Confidence: {score.confidence:.2f}")
    print(f"Contributing Factors: {score.contributing_factors}")

    preferences = {'preferred_pace': 'medium'}
    recommendation = assessor.recommend_module_difficulty(score, preferences)

    print(f"\nDifficulty Recommendation:")
    print(f"  Optimal Start: {recommendation.optimal_starting_difficulty}")
    print(f"  Range: {recommendation.min_difficulty}-{recommendation.max_difficulty}")
    print(f"  Progression: {recommendation.progression_rate}")

    assert 30 <= score.score <= 70, "Should have moderate score with related skills"
    assert recommendation.optimal_starting_difficulty > 20, "Should start above beginner"


def test_advanced_with_courses():
    """Test assessment for advanced user with completed courses."""
    print("\n" + "="*80)
    print("TEST 3: Advanced User with Completed Courses")
    print("="*80)

    assessor = KnowledgeAssessor()

    user_data = {
        'user_id': 3,
        'learning_goals': ['python'],
        'experience_level': 'advanced',
        'completed_courses': [
            {'title': 'Python Fundamentals', 'completed': True},
            {'title': 'Advanced Python', 'completed': True},
            {'title': 'Python for Data Science', 'completed': True}
        ],
        'quiz_scores': {
            'python_basics': 90,
            'python_oop': 85,
            'python_advanced': 88
        },
        'skills': ['python', 'django', 'flask', 'numpy', 'pandas'],
        'last_activity': datetime.now(),
    }

    score = assessor.assess_user_knowledge(
        user_id=3,
        topic='python',
        user_data=user_data
    )

    print(f"\nKnowledge Score: {score.score}/100")
    print(f"Confidence: {score.confidence:.2f}")
    print(f"Contributing Factors: {score.contributing_factors}")

    preferences = {'preferred_pace': 'fast'}
    recommendation = assessor.recommend_module_difficulty(score, preferences)

    print(f"\nDifficulty Recommendation:")
    print(f"  Optimal Start: {recommendation.optimal_starting_difficulty}")
    print(f"  Range: {recommendation.min_difficulty}-{recommendation.max_difficulty}")
    print(f"  Progression: {recommendation.progression_rate}")

    assert score.score >= 60, "Should have high score with many courses and skills"
    assert score.confidence >= 0.8, "Should have high confidence with all data points"
    assert recommendation.progression_rate == 'fast', "Should recommend fast pace"


def test_time_decay():
    """Test knowledge decay over time."""
    print("\n" + "="*80)
    print("TEST 4: Knowledge Decay Over Time")
    print("="*80)

    assessor = KnowledgeAssessor()

    # Active user
    active_user_data = {
        'user_id': 4,
        'learning_goals': ['javascript'],
        'experience_level': 'intermediate',
        'completed_courses': [
            {'title': 'JavaScript Complete Course', 'completed': True}
        ],
        'quiz_scores': {'javascript': 80},
        'skills': ['javascript'],
        'last_activity': datetime.now(),  # Active today
    }

    active_score = assessor.assess_user_knowledge(
        user_id=4,
        topic='javascript',
        user_data=active_user_data
    )

    print(f"\nActive User (recent activity):")
    print(f"  Score: {active_score.score}/100")
    print(f"  Time Decay Applied: {active_score.contributing_factors.get('time_decay_applied')}")

    # Inactive user (6 months ago)
    inactive_user_data = active_user_data.copy()
    inactive_user_data['last_activity'] = datetime.now() - timedelta(days=180)

    inactive_score = assessor.assess_user_knowledge(
        user_id=4,
        topic='javascript',
        user_data=inactive_user_data
    )

    print(f"\nInactive User (6 months ago):")
    print(f"  Score: {inactive_score.score}/100")
    print(f"  Time Decay Applied: {inactive_score.contributing_factors.get('time_decay_applied')}")

    # Very inactive user (1 year ago)
    very_inactive_user_data = active_user_data.copy()
    very_inactive_user_data['last_activity'] = datetime.now() - timedelta(days=365)

    very_inactive_score = assessor.assess_user_knowledge(
        user_id=4,
        topic='javascript',
        user_data=very_inactive_user_data
    )

    print(f"\nVery Inactive User (1 year ago):")
    print(f"  Score: {very_inactive_score.score}/100")
    print(f"  Time Decay Applied: {very_inactive_score.contributing_factors.get('time_decay_applied')}")

    assert active_score.score > inactive_score.score, "Inactive users should have lower scores"
    # Note: Very inactive score may equal inactive score due to max decay limit (50%)
    assert inactive_score.score >= very_inactive_score.score, "Score shouldn't increase with inactivity"
    print("\n✅ Time decay working correctly (decay bottoms out at 50%)")


def test_pace_variations():
    """Test different learning pace recommendations."""
    print("\n" + "="*80)
    print("TEST 5: Learning Pace Variations")
    print("="*80)

    assessor = KnowledgeAssessor()

    user_data = {
        'user_id': 5,
        'learning_goals': ['react'],
        'experience_level': 'some_basics',
        'completed_courses': [],
        'quiz_scores': {},
        'skills': ['javascript'],
        'last_activity': datetime.now(),
    }

    score = assessor.assess_user_knowledge(
        user_id=5,
        topic='react',
        user_data=user_data
    )

    print(f"\nBase Knowledge Score: {score.score}/100")

    # Test slow pace
    slow_rec = assessor.recommend_module_difficulty(score, {'preferred_pace': 'slow'})
    print(f"\nSlow Pace:")
    print(f"  Optimal Start: {slow_rec.optimal_starting_difficulty}")
    print(f"  Range: {slow_rec.min_difficulty}-{slow_rec.max_difficulty}")

    # Test medium pace
    medium_rec = assessor.recommend_module_difficulty(score, {'preferred_pace': 'medium'})
    print(f"\nMedium Pace:")
    print(f"  Optimal Start: {medium_rec.optimal_starting_difficulty}")
    print(f"  Range: {medium_rec.min_difficulty}-{medium_rec.max_difficulty}")

    # Test fast pace
    fast_rec = assessor.recommend_module_difficulty(score, {'preferred_pace': 'fast'})
    print(f"\nFast Pace:")
    print(f"  Optimal Start: {fast_rec.optimal_starting_difficulty}")
    print(f"  Range: {fast_rec.min_difficulty}-{fast_rec.max_difficulty}")

    assert slow_rec.optimal_starting_difficulty < medium_rec.optimal_starting_difficulty, \
        "Slow pace should start easier"
    assert medium_rec.optimal_starting_difficulty < fast_rec.optimal_starting_difficulty, \
        "Fast pace should start harder"
    print("\n✅ Pace variations working correctly")


if __name__ == '__main__':
    print("\n🧪 Testing Knowledge Assessor")
    print("=" * 80)

    try:
        test_beginner_assessment()
        print("\n✅ Test 1 PASSED")
    except AssertionError as e:
        print(f"\n❌ Test 1 FAILED: {e}")

    try:
        test_intermediate_with_skills()
        print("\n✅ Test 2 PASSED")
    except AssertionError as e:
        print(f"\n❌ Test 2 FAILED: {e}")

    try:
        test_advanced_with_courses()
        print("\n✅ Test 3 PASSED")
    except AssertionError as e:
        print(f"\n❌ Test 3 FAILED: {e}")

    try:
        test_time_decay()
        print("\n✅ Test 4 PASSED")
    except AssertionError as e:
        print(f"\n❌ Test 4 FAILED: {e}")

    try:
        test_pace_variations()
        print("\n✅ Test 5 PASSED")
    except AssertionError as e:
        print(f"\n❌ Test 5 FAILED: {e}")

    print("\n" + "="*80)
    print("🎉 ALL KNOWLEDGE ASSESSOR TESTS COMPLETED!")
    print("="*80)
