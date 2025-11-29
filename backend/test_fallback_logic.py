#!/usr/bin/env python3
"""
Test script to verify intelligent fallback logic works correctly.

Tests the scenario from the user's logs:
- User selects "interactive" learning style
- Topics are mathematics (Statistics, Linear Algebra, etc.)
- Primary source (Exercism) returns 0 results
- Fallback should search articles + GitHub repos
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ml_services.integrations.course_search_service import CourseSearchService


def test_math_topic_interactive_style():
    """
    Test Case: Interactive style + Mathematics topic (from user's logs).

    Expected behavior:
    - Primary: Exercism returns 0 (no math track)
    - Fallback: Searches Dev.to, Hashnode, GitHub
    - Result: Should find articles and repos (NOT empty)
    """
    print("\n" + "="*80)
    print("TEST 1: Interactive Style + Mathematics Topic (User's Exact Scenario)")
    print("="*80)

    service = CourseSearchService()

    user_preferences = {
        'basic_info': {
            'learning_style': ['interactive'],  # User wants interactive
            'experience_level': 'intermediate'
        },
        'content_preferences': {
            'preferred_platforms': [],
            'duration_preference': 'mixed'
        }
    }

    # Test with mathematics topic (same as user's logs)
    topic = "Statistics"
    print(f"\nSearching for: '{topic}' with learning style: {user_preferences['basic_info']['learning_style']}")
    print("-" * 80)

    courses = service.search_courses(topic, user_preferences, max_results=10)

    print("\n📊 RESULTS:")
    print(f"  Total courses found: {len(courses)}")

    if len(courses) == 0:
        print("  ❌ FAIL - No courses found (same as before)")
        print("  Expected: Articles + GitHub repos via fallback")
        return False
    else:
        print("  ✅ SUCCESS - Found courses via fallback!")

        # Show breakdown by platform
        platforms = {}
        content_types = {}

        for scored_course in courses:
            course = scored_course.course
            platforms[course.platform] = platforms.get(course.platform, 0) + 1

            # Determine content type
            if course.platform in ['dev_to', 'hashnode', 'freecodecamp', 'medium']:
                content_type = 'article'
            elif course.platform == 'github':
                content_type = 'project/tutorial'
            elif course.platform == 'exercism':
                content_type = 'interactive'
            else:
                content_type = 'other'

            content_types[content_type] = content_types.get(content_type, 0) + 1

        print("\n  Platform breakdown:")
        for platform, count in platforms.items():
            print(f"    - {platform}: {count} courses")

        print("\n  Content type breakdown:")
        for ctype, count in content_types.items():
            print(f"    - {ctype}: {count} items")

        print("\n  Sample courses:")
        for i, scored_course in enumerate(courses[:3], 1):
            course = scored_course.course
            print(f"\n    {i}. {course.title[:60]}...")
            print(f"       Platform: {course.platform} | Type: article/tutorial | is_mock: {course.is_mock}")
            print(f"       URL: {course.url[:80]}")

        return True


def test_programming_topic_reading_style():
    """
    Test Case: Reading style + Programming topic.

    Expected behavior:
    - Primary: Dev.to, Hashnode, freeCodeCamp articles
    - Result: Should find articles (no fallback needed)
    """
    print("\n" + "="*80)
    print("TEST 2: Reading Style + Programming Topic (Should Work Without Fallback)")
    print("="*80)

    service = CourseSearchService()

    user_preferences = {
        'basic_info': {
            'learning_style': ['reading'],
            'experience_level': 'intermediate'
        },
        'content_preferences': {}
    }

    topic = "Python"
    print(f"\nSearching for: '{topic}' with learning style: {user_preferences['basic_info']['learning_style']}")
    print("-" * 80)

    courses = service.search_courses(topic, user_preferences, max_results=10)

    print("\n📊 RESULTS:")
    print(f"  Total courses found: {len(courses)}")

    if len(courses) >= 5:
        print("  ✅ SUCCESS - Found articles (primary sources worked)")

        article_platforms = [c.course.platform for c in courses if c.course.platform in ['dev_to', 'hashnode', 'freecodecamp', 'medium']]
        print(f"  Article platforms: {len(article_platforms)}/{len(courses)} courses")

        return True
    else:
        print("  ⚠️ WARNING - Expected more results from article platforms")
        return False


def test_topic_domain_classification():
    """
    Test Case: Topic domain classification.

    Verifies that _determine_topic_domain() correctly classifies topics.
    """
    print("\n" + "="*80)
    print("TEST 3: Topic Domain Classification")
    print("="*80)

    service = CourseSearchService()

    test_cases = [
        ("Python programming", "programming"),
        ("React Hooks", "programming"),
        ("Statistics", "mathematics"),
        ("Machine Learning", "machine_learning"),
        ("Data Science", "data_science"),
        ("Linear Algebra", "mathematics"),
        ("Gardening", "general"),
    ]

    all_passed = True

    for topic, expected_domain in test_cases:
        actual_domain = service._determine_topic_domain(topic)
        status = "✅" if actual_domain == expected_domain else "❌"
        print(f"  {status} '{topic}' → {actual_domain} (expected: {expected_domain})")

        if actual_domain != expected_domain:
            all_passed = False

    return all_passed


def main():
    """Run all tests."""
    print("\n" + "🧪"*40)
    print("TESTING INTELLIGENT FALLBACK LOGIC")
    print("🧪"*40)

    results = {
        'Math + Interactive (Fallback Test)': test_math_topic_interactive_style(),
        'Python + Reading (No Fallback)': test_programming_topic_reading_style(),
        'Topic Domain Classification': test_topic_domain_classification()
    }

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\n  Total: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Intelligent fallback is working correctly!")
        print("✅ Math + Interactive style now returns articles and GitHub repos!")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - Check the output above for details")
        return 1


if __name__ == '__main__':
    sys.exit(main())
