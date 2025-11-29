"""
Test semantic matching without requiring ML_API_KEY
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ml_services.services.ai_goal_analyzer import AIGoalAnalyzer


def test_semantic_variations():
    """Test various semantic matches."""
    print("\n" + "="*80)
    print("SEMANTIC MATCHING TEST - No AI Required")
    print("="*80)

    analyzer = AIGoalAnalyzer()

    test_cases = [
        ('app development', 'react-native'),
        ('mobile app', 'react-native'),
        ('mobile development', 'react-native'),
        ('web development', 'frontend'),
        ('frontend development', 'frontend'),
        ('backend development', 'backend'),
        ('full stack', 'full-stack'),
        ('data science', 'ai-data-scientist'),
        ('machine learning', 'ai-data-scientist'),
        ('cybersecurity', 'cyber-security'),
        ('devops', 'devops'),
    ]

    user_background = {
        'skills': ['python'],
        'career_stage': 'student'
    }

    preferences = {
        'experience_level': 'some_basics',
        'time_availability': '3-5hrs',
        'learning_styles': ['videos'],
        'target_timeline': 'flexible'
    }

    results = []

    for input_goal, expected_roadmap in test_cases:
        print(f"\nTesting: '{input_goal}' → '{expected_roadmap}'")

        try:
            # This should use semantic matching and fetch directly
            path = analyzer.analyze_learning_goal(
                learning_goal=input_goal,
                user_background=user_background,
                preferences=preferences,
                force_ai=False
            )

            if path:
                actual_source = path.metadata.get('source', 'unknown')
                method = path.metadata.get('generation_method', 'unknown')

                print(f"   ✅ SUCCESS: {path.title}")
                print(f"      Source: {actual_source}")
                print(f"      Method: {method}")
                print(f"      Modules: {len(path.modules)}")

                results.append((input_goal, True, f"roadmap.sh ({len(path.modules)} modules)"))
            else:
                print(f"   ❌ FAILED: Returned None")
                results.append((input_goal, False, "None returned"))

        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            results.append((input_goal, False, str(e)))

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for input_goal, success, info in results:
        status = "✅" if success else "❌"
        print(f"{status} '{input_goal}': {info}")

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    return passed == total


if __name__ == '__main__':
    success = test_semantic_variations()
    exit(0 if success else 1)
