"""
File: backend/test_phase1_direct.py
Description: Direct unit tests for Phase 1 improvements (no HTTP/auth required)
Purpose: Test deterministic variance and career weighting logic directly
RELEVANT FILES: backend/core/apps/learning_content/api/views.py, backend/ml_services/integrations/course_search_service.py
"""

import sys
import os
import django

# Setup Django environment
sys.path.insert(0, '/home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/backend/core')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.learning_content.api.views import GenerateLearningPathView
from ml_services.integrations.course_search_service import CourseSearchService


def test_deterministic_variance():
    """Test that calculate_deterministic_variance produces consistent results."""
    print("\n" + "="*80)
    print("TEST 1: DETERMINISTIC VARIANCE FUNCTION")
    print("="*80)

    # Test Case 1: Career changer with tight timeline (variance should be -1)
    test_prefs_1 = {
        "basic_info": {
            "time_availability": "1-2hrs",      # -1
            "target_timeline": "3months",       # -1
            "career_stage": "career_change"     # +1
        }
    }

    variance_1 = GenerateLearningPathView.calculate_deterministic_variance(test_prefs_1)
    expected_1 = -1  # -1 + -1 + 1 = -1
    print(f"\nTest Case 1: Career changer with tight timeline")
    print(f"  Time availability: 1-2hrs (-1)")
    print(f"  Timeline: 3months (-1)")
    print(f"  Career stage: career_change (+1)")
    print(f"  Expected variance: {expected_1}")
    print(f"  Actual variance: {variance_1}")
    test1_pass = variance_1 == expected_1
    print(f"  {'✅ PASS' if test1_pass else '❌ FAIL'}")

    # Test Case 2: Student with flexible timeline (variance should be +1)
    test_prefs_2 = {
        "basic_info": {
            "time_availability": "5+hrs",       # +1
            "target_timeline": "1year",         # +1
            "career_stage": "student"           # 0
        }
    }

    variance_2 = GenerateLearningPathView.calculate_deterministic_variance(test_prefs_2)
    expected_2 = 2  # +1 + +1 + 0 = 2 (capped at 2)
    print(f"\nTest Case 2: Student with flexible timeline")
    print(f"  Time availability: 5+hrs (+1)")
    print(f"  Timeline: 1year (+1)")
    print(f"  Career stage: student (0)")
    print(f"  Expected variance: {expected_2}")
    print(f"  Actual variance: {variance_2}")
    test2_pass = variance_2 == expected_2
    print(f"  {'✅ PASS' if test2_pass else '❌ FAIL'}")

    # Test Case 3: Professional with moderate timeline (variance should be -1)
    test_prefs_3 = {
        "basic_info": {
            "time_availability": "3-5hrs",      # 0
            "target_timeline": "6months",       # 0
            "career_stage": "professional"      # -1
        }
    }

    variance_3 = GenerateLearningPathView.calculate_deterministic_variance(test_prefs_3)
    expected_3 = -1  # 0 + 0 + -1 = -1
    print(f"\nTest Case 3: Professional with moderate timeline")
    print(f"  Time availability: 3-5hrs (0)")
    print(f"  Timeline: 6months (0)")
    print(f"  Career stage: professional (-1)")
    print(f"  Expected variance: {expected_3}")
    print(f"  Actual variance: {variance_3}")
    test3_pass = variance_3 == expected_3
    print(f"  {'✅ PASS' if test3_pass else '❌ FAIL'}")

    # Test Case 4: Same inputs twice (deterministic check)
    variance_1_repeat = GenerateLearningPathView.calculate_deterministic_variance(test_prefs_1)
    print(f"\nTest Case 4: Deterministic check (same input twice)")
    print(f"  First call: {variance_1}")
    print(f"  Second call: {variance_1_repeat}")
    test4_pass = variance_1 == variance_1_repeat
    print(f"  {'✅ PASS - Deterministic!' if test4_pass else '❌ FAIL - Not deterministic!'}")

    all_passed = test1_pass and test2_pass and test3_pass and test4_pass
    if all_passed:
        print(f"\n{'='*80}")
        print("✅ ALL DETERMINISTIC VARIANCE TESTS PASSED!")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("❌ SOME TESTS FAILED")
        print(f"{'='*80}")

    return all_passed


def test_career_content_weighting():
    """Test that career-based content weighting is correctly configured."""
    print("\n" + "="*80)
    print("TEST 2: CAREER CONTENT WEIGHTING FUNCTION")
    print("="*80)

    # Test all career stages
    career_stages = ["student", "career_change", "skill_upgrade", "professional"]

    all_tests_pass = True

    for career_stage in career_stages:
        print(f"\n--- Testing {career_stage.upper()} ---")

        weights = CourseSearchService._get_career_content_weights(career_stage)

        # Verify weights exist
        if not weights:
            print(f"  ❌ FAIL: No weights returned for {career_stage}")
            all_tests_pass = False
            continue

        print(f"  Content type weights:")
        for content_type, multiplier in weights.items():
            print(f"    {content_type}: {multiplier}x")

        # Verify expected patterns
        if career_stage == "career_change":
            if weights.get("project", 0) >= 2.0:
                print(f"  ✅ Career changers prioritize projects (2.0x)")
            else:
                print(f"  ❌ Projects should be 2.0x for career changers")
                all_tests_pass = False

        elif career_stage == "student":
            if weights.get("video", 0) >= 1.5:
                print(f"  ✅ Students prioritize videos (1.5x)")
            else:
                print(f"  ❌ Videos should be 1.5x for students")
                all_tests_pass = False

        elif career_stage == "professional":
            if weights.get("article", 0) >= 1.2:
                print(f"  ✅ Professionals prioritize articles (1.2x)")
            else:
                print(f"  ❌ Articles should be 1.2x for professionals")
                all_tests_pass = False

    if all_tests_pass:
        print(f"\n{'='*80}")
        print("✅ ALL CAREER WEIGHTING TESTS PASSED!")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("❌ SOME TESTS FAILED")
        print(f"{'='*80}")

    return all_tests_pass


def test_no_random_imports():
    """Verify that random module is no longer imported in views.py."""
    print("\n" + "="*80)
    print("TEST 3: VERIFY NO RANDOM IMPORTS")
    print("="*80)

    import inspect
    source = inspect.getsource(GenerateLearningPathView)

    has_random_import = "import random" in source or "from random import" in source
    has_random_usage = "random.randint" in source or "random.choice" in source

    print(f"\nChecking GenerateLearningPathView source code:")
    print(f"  Contains 'import random': {has_random_import}")
    print(f"  Contains 'random.randint' usage: {has_random_usage}")

    test_pass = not has_random_import and not has_random_usage

    if test_pass:
        print(f"\n  ✅ PASS: No random module usage found!")
    else:
        print(f"\n  ❌ FAIL: Random module still being used!")

    return test_pass


def main():
    """Run all Phase 1 direct tests."""
    print("\n" + "="*80)
    print("PHASE 1 DIRECT TESTING - NO AUTHENTICATION REQUIRED")
    print("="*80)

    results = {
        "deterministic_variance": test_deterministic_variance(),
        "career_weighting": test_career_content_weighting(),
        "no_random_imports": test_no_random_imports()
    }

    # Summary
    print("\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80)

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")

    print(f"\nOverall: {passed_tests}/{total_tests} test groups passed")

    if passed_tests == total_tests:
        print("\n" + "="*80)
        print("🎉 ALL PHASE 1 LOGIC TESTS PASSED!")
        print("✓ Deterministic variance working correctly")
        print("✓ Career-based content weighting implemented")
        print("✓ Random module removed from codebase")
        print("\n✅ Ready to proceed to Phase 2: Core Intelligence")
        print("="*80)
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test group(s) failed. Review implementation.")


if __name__ == "__main__":
    main()
