"""
Test script for AI Goal Analyzer
Tests hybrid roadmap.sh + AI generation approach
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ml_services.services.ai_goal_analyzer import AIGoalAnalyzer


def test_roadmap_hybrid():
    """Test hybrid approach with roadmap.sh (mobile_dev)."""
    print("\n" + "="*80)
    print("TEST 1: Hybrid Approach - Mobile Development (should use roadmap.sh)")
    print("="*80)

    analyzer = AIGoalAnalyzer()

    user_background = {
        'skills': ['python', 'javascript'],
        'career_stage': 'student',
        'experience_level': 'some_basics'
    }

    preferences = {
        'experience_level': 'some_basics',
        'time_availability': '5-10hrs',
        'learning_styles': ['hands_on', 'videos'],
        'target_timeline': '6months'
    }

    try:
        path = analyzer.analyze_learning_goal(
            learning_goal='mobile_dev',
            user_background=user_background,
            preferences=preferences,
            force_ai=False
        )

        print(f"\n✅ Generated Learning Path:")
        print(f"   Title: {path.title}")
        print(f"   Description: {path.description}")
        print(f"   Learning Goal: {path.learning_goal}")
        print(f"   Total Modules: {len(path.modules)}")
        print(f"   Total Hours: {path.total_estimated_hours}")
        print(f"   Generation Method: {path.metadata.get('generation_method')}")
        print(f"   Source: {path.metadata.get('source')}")

        print(f"\n📚 First 3 Modules:")
        for module in path.modules[:3]:
            print(f"\n   Module {module.recommended_sequence}: {module.title}")
            print(f"      Difficulty: {module.difficulty_score}/100")
            print(f"      Hours: {module.estimated_hours}")
            print(f"      Skills: {', '.join(module.skills_to_master[:3])}")
            print(f"      Prerequisites: {module.prerequisites}")

        print(f"\n📈 Difficulty Progression: {path.difficulty_progression[:5]}...")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_semantic_matching():
    """Test semantic matching with variations."""
    print("\n" + "="*80)
    print("TEST 2: Semantic Matching - 'app development' → 'mobile_dev'")
    print("="*80)

    analyzer = AIGoalAnalyzer()

    user_background = {
        'skills': ['html', 'css'],
        'career_stage': 'career_switcher'
    }

    preferences = {
        'experience_level': 'complete_beginner',
        'time_availability': '3-5hrs',
        'learning_styles': ['videos'],
        'target_timeline': '1year'
    }

    try:
        path = analyzer.analyze_learning_goal(
            learning_goal='app development',  # Should match to mobile_dev
            user_background=user_background,
            preferences=preferences,
            force_ai=False
        )

        print(f"\n✅ Semantic Match Successful:")
        print(f"   Input: 'app development'")
        print(f"   Matched To: {path.metadata.get('source')}")
        print(f"   Title: {path.title}")
        print(f"   Modules: {len(path.modules)}")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pure_ai_generation():
    """Test pure AI generation with custom goal."""
    print("\n" + "="*80)
    print("TEST 3: Pure AI Generation - Custom Goal 'quantum computing'")
    print("="*80)

    analyzer = AIGoalAnalyzer()

    user_background = {
        'skills': ['python', 'linear algebra', 'physics'],
        'career_stage': 'researcher'
    }

    preferences = {
        'experience_level': 'intermediate',
        'time_availability': '10+hrs',
        'learning_styles': ['reading', 'hands_on'],
        'target_timeline': '1year'
    }

    try:
        path = analyzer.analyze_learning_goal(
            learning_goal='quantum computing',  # No roadmap.sh match - should use AI
            user_background=user_background,
            preferences=preferences,
            force_ai=False  # Let it try roadmap.sh first, then fall back
        )

        print(f"\n✅ AI-Generated Learning Path:")
        print(f"   Title: {path.title}")
        print(f"   Description: {path.description}")
        print(f"   Learning Goal: {path.learning_goal}")
        print(f"   Total Modules: {len(path.modules)}")
        print(f"   Total Hours: {path.total_estimated_hours}")
        print(f"   Generation Method: {path.metadata.get('generation_method')}")
        print(f"   AI Model: {path.metadata.get('ai_model')}")

        print(f"\n📚 All Modules:")
        for module in path.modules:
            print(f"\n   {module.recommended_sequence}. {module.title}")
            print(f"      Difficulty: {module.difficulty_score}/100")
            print(f"      Hours: {module.estimated_hours}")
            print(f"      Objectives: {module.learning_objectives[:2]}")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_force_ai():
    """Test forcing AI generation (skip roadmap.sh)."""
    print("\n" + "="*80)
    print("TEST 4: Force AI Mode - 'web development' with force_ai=True")
    print("="*80)

    analyzer = AIGoalAnalyzer()

    user_background = {
        'skills': [],
        'career_stage': 'student'
    }

    preferences = {
        'experience_level': 'complete_beginner',
        'time_availability': '3-5hrs',
        'learning_styles': ['videos', 'hands_on'],
        'target_timeline': 'flexible'
    }

    try:
        path = analyzer.analyze_learning_goal(
            learning_goal='web development',
            user_background=user_background,
            preferences=preferences,
            force_ai=True  # Force AI, skip roadmap.sh
        )

        print(f"\n✅ Forced AI Generation:")
        print(f"   Title: {path.title}")
        print(f"   Generation Method: {path.metadata.get('generation_method')}")
        print(f"   Should be: pure_ai")
        print(f"   Modules: {len(path.modules)}")

        assert path.metadata.get('generation_method') == 'pure_ai', \
            "Force AI should use pure_ai generation method"

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🧪 Testing AI Goal Analyzer")
    print("=" * 80)

    results = []

    # Run all tests
    results.append(("Hybrid Roadmap.sh", test_roadmap_hybrid()))
    results.append(("Semantic Matching", test_semantic_matching()))
    results.append(("Pure AI Generation", test_pure_ai_generation()))
    results.append(("Force AI Mode", test_force_ai()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)
    print("\n" + ("="*80))
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*80)
