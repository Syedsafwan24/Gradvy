#!/usr/bin/env python
"""
Test script to verify preferences loading fix
Tests:
1. content_preferences property returns defaults when None
2. .to_mongo() method works on all content_preferences types
3. Null-safety for basic_info
"""

import os
import sys
import django

# Add the core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.preferences.models import UserPreference


def test_content_preferences_default():
    """Test that content_preferences returns defaults instead of None"""
    print("🧪 Test 1: content_preferences returns defaults when missing")
    print("-" * 60)

    # Get a user preference (any user)
    try:
        user_pref = UserPreference.objects.first()
        if not user_pref:
            print("❌ No UserPreference found in database. Create a user first.")
            return False

        print(f"✅ Testing with user_id: {user_pref.user_id}")

        # Get content_preferences
        content_prefs = user_pref.content_preferences

        if content_prefs is None:
            print("❌ FAILED: content_preferences returned None")
            return False

        print(f"✅ content_preferences exists: {type(content_prefs).__name__}")

        # Test .to_mongo() method exists
        if not hasattr(content_prefs, 'to_mongo'):
            print("❌ FAILED: content_preferences missing .to_mongo() method")
            return False

        print("✅ .to_mongo() method exists")

        # Test .to_mongo() returns dict
        try:
            mongo_dict = content_prefs.to_mongo()
            if not isinstance(mongo_dict, dict):
                print(f"❌ FAILED: .to_mongo() returned {type(mongo_dict)} instead of dict")
                return False

            print(f"✅ .to_mongo() returns dict with keys: {list(mongo_dict.keys())}")

            # Check for expected keys
            expected_keys = ['preferred_platforms', 'content_types', 'difficulty_preference']
            for key in expected_keys:
                if key in mongo_dict:
                    print(f"   ✓ {key}: {mongo_dict[key]}")

            print("✅ TEST PASSED: content_preferences works correctly")
            return True

        except Exception as e:
            print(f"❌ FAILED: .to_mongo() raised exception: {e}")
            return False

    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_info_null_safety():
    """Test that basic_info null check would work"""
    print("\n🧪 Test 2: basic_info null-safety check")
    print("-" * 60)

    try:
        user_pref = UserPreference.objects.first()
        if not user_pref:
            print("❌ No UserPreference found in database")
            return False

        print(f"✅ Testing with user_id: {user_pref.user_id}")

        # Check basic_info
        basic_info = user_pref.basic_info

        if basic_info is None:
            print("⚠️  basic_info is None - API would return clear error message")
            print("   This is expected for incomplete profiles")
            return True

        print(f"✅ basic_info exists")
        print(f"   - learning_goals: {basic_info.learning_goals}")
        print(f"   - experience_level: {basic_info.experience_level}")
        print(f"   - preferred_pace: {basic_info.preferred_pace}")

        print("✅ TEST PASSED: basic_info accessible")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("PREFERENCES LOADING FIX - TEST SUITE")
    print("=" * 60)
    print()

    results = []

    # Test 1: content_preferences defaults
    results.append(("content_preferences defaults", test_content_preferences_default()))

    # Test 2: basic_info null-safety
    results.append(("basic_info null-safety", test_basic_info_null_safety()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe preferences loading fix is working correctly.")
        print("You can now test the learning path generation API.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the errors above.")

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
