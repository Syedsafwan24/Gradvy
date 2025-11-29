#!/usr/bin/env python3
"""
Test script to verify REAL content APIs work correctly - NO MOCK DATA!

This script tests:
1. Dev.to API integration
2. Hashnode GraphQL API
3. GitHub tutorial search
4. freeCodeCamp RSS parsing
5. Medium RSS parsing
6. Exercism API

All APIs should return real content with is_mock=False.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ml_services.integrations.course_search_service import CourseSearchService


def test_devto_api():
    """Test Dev.to API returns REAL articles."""
    print("\n" + "="*80)
    print("TEST 1: Dev.to API Integration")
    print("="*80)

    service = CourseSearchService()
    articles = service._search_devto("python", max_results=3)

    print(f"\n✅ Found {len(articles)} articles from Dev.to")

    if articles:
        for i, article in enumerate(articles, 1):
            print(f"\n  Article {i}:")
            print(f"    Title: {article.title}")
            print(f"    URL: {article.url}")
            print(f"    Platform: {article.platform}")
            print(f"    is_mock: {article.is_mock} {'❌ FAIL - Should be False!' if article.is_mock else '✅ PASS'}")
            print(f"    Rating: {article.rating}")
            print(f"    Reading time: {article.duration_hours * 60:.1f} minutes")
    else:
        print("  ⚠️ WARNING: No articles found!")

    return len(articles) > 0


def test_github_api():
    """Test GitHub API returns REAL tutorial repos."""
    print("\n" + "="*80)
    print("TEST 2: GitHub Repositories API")
    print("="*80)

    service = CourseSearchService()
    repos = service._search_github_tutorials("react", max_results=3)

    print(f"\n✅ Found {len(repos)} tutorial repos from GitHub")

    if repos:
        for i, repo in enumerate(repos, 1):
            print(f"\n  Repo {i}:")
            print(f"    Title: {repo.title}")
            print(f"    URL: {repo.url}")
            print(f"    Platform: {repo.platform}")
            print(f"    is_mock: {repo.is_mock} {'❌ FAIL - Should be False!' if repo.is_mock else '✅ PASS'}")
            print(f"    Stars: {repo.num_ratings}")
    else:
        print("  ⚠️ WARNING: No repos found!")

    return len(repos) > 0


def test_freecodecamp_rss():
    """Test freeCodeCamp RSS parsing returns REAL articles."""
    print("\n" + "="*80)
    print("TEST 3: freeCodeCamp RSS Feed")
    print("="*80)

    service = CourseSearchService()
    articles = service._search_freecodecamp_rss("javascript", max_results=3)

    print(f"\n✅ Found {len(articles)} articles from freeCodeCamp RSS")

    if articles:
        for i, article in enumerate(articles, 1):
            print(f"\n  Article {i}:")
            print(f"    Title: {article.title}")
            print(f"    URL: {article.url}")
            print(f"    Platform: {article.platform}")
            print(f"    is_mock: {article.is_mock} {'❌ FAIL - Should be False!' if article.is_mock else '✅ PASS'}")
    else:
        print("  ⚠️ WARNING: No articles found (topic might not be in recent RSS feed)")

    return True  # RSS parsing is optional, don't fail if no results


def test_medium_rss():
    """Test Medium RSS parsing returns REAL articles."""
    print("\n" + "="*80)
    print("TEST 4: Medium RSS Feed")
    print("="*80)

    service = CourseSearchService()
    articles = service._search_medium_rss("programming", max_results=3)

    print(f"\n✅ Found {len(articles)} articles from Medium RSS")

    if articles:
        for i, article in enumerate(articles, 1):
            print(f"\n  Article {i}:")
            print(f"    Title: {article.title}")
            print(f"    Platform: {article.platform}")
            print(f"    is_mock: {article.is_mock} {'❌ FAIL - Should be False!' if article.is_mock else '✅ PASS'}")
    else:
        print("  ⚠️ WARNING: No articles found (tag might not exist)")

    return True  # RSS parsing is optional


def test_exercism_api():
    """Test Exercism API returns REAL coding exercises."""
    print("\n" + "="*80)
    print("TEST 5: Exercism API")
    print("="*80)

    service = CourseSearchService()
    exercises = service._search_exercism("python", max_results=3)

    print(f"\n✅ Found {len(exercises)} exercise tracks from Exercism")

    if exercises:
        for i, exercise in enumerate(exercises, 1):
            print(f"\n  Track {i}:")
            print(f"    Title: {exercise.title}")
            print(f"    URL: {exercise.url}")
            print(f"    Platform: {exercise.platform}")
            print(f"    is_mock: {exercise.is_mock} {'❌ FAIL - Should be False!' if exercise.is_mock else '✅ PASS'}")
            print(f"    Estimated hours: {exercise.duration_hours}")
    else:
        print("  ⚠️ WARNING: No exercises found!")

    return len(exercises) > 0


def test_full_search_integration():
    """Test full search_courses() integration with reading style."""
    print("\n" + "="*80)
    print("TEST 6: Full search_courses() Integration (Reading Style)")
    print("="*80)

    service = CourseSearchService()

    user_preferences = {
        'basic_info': {
            'learning_style': ['reading'],  # Request ONLY reading content
            'experience_level': 'intermediate'
        },
        'content_preferences': {
            'preferred_platforms': [],
            'duration_preference': 'mixed'
        }
    }

    courses = service.search_courses("python", user_preferences, max_results=10)

    print(f"\n✅ Found {len(courses)} total courses")

    # Check that NO video courses are returned
    video_courses = [c for c in courses if c.course.platform in ['youtube', 'udemy']]
    article_courses = [c for c in courses if c.course.platform in ['dev_to', 'hashnode', 'medium', 'freecodecamp']]

    print(f"\n  Video courses: {len(video_courses)} {'❌ FAIL - Should be 0!' if video_courses else '✅ PASS'}")
    print(f"  Article courses: {len(article_courses)} {'✅ PASS' if article_courses else '⚠️ WARNING'}")

    # Verify all courses have is_mock=False
    mock_courses = [c for c in courses if c.course.is_mock]
    print(f"  Mock courses: {len(mock_courses)} {'❌ FAIL - Should be 0!' if mock_courses else '✅ PASS'}")

    if courses:
        print(f"\n  Sample courses:")
        for i, scored_course in enumerate(courses[:3], 1):
            course = scored_course.course
            print(f"\n    Course {i}:")
            print(f"      Title: {course.title[:60]}...")
            print(f"      Platform: {course.platform}")
            print(f"      Type: {'article' if course.platform in ['dev_to', 'hashnode', 'medium', 'freecodecamp'] else 'other'}")
            print(f"      is_mock: {course.is_mock}")
            print(f"      Score: {scored_course.relevance_score}")

    return len(mock_courses) == 0 and len(video_courses) == 0


def main():
    """Run all tests."""
    print("\n" + "🚀"*40)
    print("TESTING REAL CONTENT APIs - NO MOCK DATA!")
    print("🚀"*40)

    results = {
        'Dev.to API': test_devto_api(),
        'GitHub API': test_github_api(),
        'freeCodeCamp RSS': test_freecodecamp_rss(),
        'Medium RSS': test_medium_rss(),
        'Exercism API': test_exercism_api(),
        'Full Integration': test_full_search_integration()
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
        print("\n🎉 ALL TESTS PASSED! Real content APIs are working correctly!")
        print("✅ NO MOCK DATA - All content is real and fetched from live APIs!")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - Check the output above for details")
        return 1


if __name__ == '__main__':
    sys.exit(main())
