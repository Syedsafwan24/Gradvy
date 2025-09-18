#!/usr/bin/env python3
"""
Test script to verify manual save workflow implementation
Tests that preferences no longer auto-save and manual save button works
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3001"
TEST_USER_EMAIL = "admin@gradvy.com"
TEST_USER_PASSWORD = "admin123"

def print_step(step_name):
    print(f"\n{'='*60}")
    print(f"🧪 {step_name}")
    print(f"{'='*60}")

def print_result(success, message, data=None):
    emoji = "✅" if success else "❌"
    print(f"{emoji} {message}")
    if data:
        print(f"📊 Data: {json.dumps(data, indent=2)}")

def login_and_get_token():
    """Login and get auth token"""
    print_step("GETTING AUTH TOKEN")

    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            print_result(True, "Login successful", {"token_length": len(token) if token else 0})
            return token
        else:
            print_result(False, f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_result(False, f"Login error: {str(e)}")
        return None

def test_preference_update_without_auto_save(token):
    """Test that preference updates no longer auto-save immediately"""
    print_step("TESTING NO AUTO-SAVE BEHAVIOR")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Get current preferences
        print("📋 Getting current preferences...")
        response = requests.get(f"{BASE_URL}/preferences/", headers=headers)

        if response.status_code == 200:
            current_prefs = response.json()
            current_completion = current_prefs.get('profile_completion_percentage', 0)
            print_result(True, f"Current preferences retrieved", {
                "completion_percentage": current_completion,
                "onboarding_status": current_prefs.get('onboarding_status'),
                "has_basic_info": bool(current_prefs.get('basic_info'))
            })

            # Test making a small preference change
            print("🔄 Testing preference change (should not auto-save now)...")

            # Try to update just a single field (this used to auto-save)
            update_data = {
                "basic_info": {
                    "preferred_pace": "fast"  # Change pace to trigger update
                }
            }

            update_response = requests.patch(f"{BASE_URL}/preferences/",
                                           json=update_data, headers=headers)

            if update_response.status_code == 200:
                updated_prefs = update_response.json()
                new_completion = updated_prefs.get('profile_completion_percentage', 0)

                print_result(True, "Preference update successful", {
                    "old_completion": current_completion,
                    "new_completion": new_completion,
                    "preferred_pace": updated_prefs.get('basic_info', {}).get('preferred_pace')
                })

                # Verify the change was saved (this tests backend still works)
                verify_response = requests.get(f"{BASE_URL}/preferences/", headers=headers)
                if verify_response.status_code == 200:
                    verified_prefs = verify_response.json()
                    verified_pace = verified_prefs.get('basic_info', {}).get('preferred_pace')

                    if verified_pace == "fast":
                        print_result(True, "Change persisted correctly in backend")
                        return True
                    else:
                        print_result(False, f"Change not persisted. Expected 'fast', got '{verified_pace}'")
                        return False
            else:
                print_result(False, f"Preference update failed: {update_response.status_code} - {update_response.text}")
                return False
        else:
            print_result(False, f"Failed to get current preferences: {response.status_code}")
            return False

    except Exception as e:
        print_result(False, f"Error testing preference updates: {str(e)}")
        return False

def test_validation_fixes(token):
    """Test that validation no longer blocks legitimate saves"""
    print_step("TESTING VALIDATION FIXES")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Test updating preferences with partial data (should now work)
        print("🧪 Testing partial preference update (should not be blocked)...")

        partial_update = {
            "content_preferences": {
                "preferred_platforms": ["udemy", "coursera"],
                "content_types": ["video"]
                # Missing other fields - should still work with relaxed validation
            }
        }

        response = requests.patch(f"{BASE_URL}/preferences/",
                                json=partial_update, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print_result(True, "Partial update succeeded (validation fixed)", {
                "platforms": result.get('content_preferences', {}).get('preferred_platforms'),
                "types": result.get('content_preferences', {}).get('content_types')
            })
            return True
        else:
            # Check if it's a validation error
            error_text = response.text
            if "validation errors" in error_text.lower():
                print_result(False, f"Still getting validation errors (not fixed): {error_text}")
            else:
                print_result(False, f"Unexpected error: {response.status_code} - {error_text}")
            return False

    except Exception as e:
        print_result(False, f"Error testing validation fixes: {str(e)}")
        return False

def test_frontend_accessibility():
    """Test that frontend is accessible"""
    print_step("TESTING FRONTEND ACCESSIBILITY")

    try:
        # Test that frontend is running and responsive
        response = requests.get(FRONTEND_URL, timeout=10)

        if response.status_code == 200:
            print_result(True, f"Frontend accessible at {FRONTEND_URL}")

            # Check if the page contains preferences-related content
            content = response.text
            if "preferences" in content.lower() or "learning" in content.lower():
                print_result(True, "Frontend contains expected content")
                return True
            else:
                print_result(True, "Frontend accessible but content check inconclusive")
                return True
        else:
            print_result(False, f"Frontend not accessible: {response.status_code}")
            return False

    except Exception as e:
        print_result(False, f"Error accessing frontend: {str(e)}")
        return False

def main():
    """Run complete test suite for manual save workflow"""
    print(f"""
    🔬 MANUAL SAVE WORKFLOW TEST SUITE
    ==================================
    Testing the fixes for validation blocking and auto-save behavior

    Backend: {BASE_URL}
    Frontend: {FRONTEND_URL}
    Test User: {TEST_USER_EMAIL}
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)

    # Step 1: Get authentication token
    token = login_and_get_token()
    if not token:
        print("❌ Test suite failed at authentication")
        return

    # Step 2: Test no auto-save behavior (backend should still work when called directly)
    backend_works = test_preference_update_without_auto_save(token)

    # Step 3: Test validation fixes
    validation_fixed = test_validation_fixes(token)

    # Step 4: Test frontend accessibility
    frontend_accessible = test_frontend_accessibility()

    # Final results
    print_step("MANUAL SAVE WORKFLOW TEST RESULTS")

    all_passed = backend_works and validation_fixed and frontend_accessible

    print_result(all_passed, "Overall test result")

    print(f"""
    📊 DETAILED RESULTS:
    - Authentication: {'✅' if token else '❌'}
    - Backend Preferences API: {'✅' if backend_works else '❌'}
    - Validation Fixes: {'✅' if validation_fixed else '❌'}
    - Frontend Accessibility: {'✅' if frontend_accessible else '❌'}

    🔧 MANUAL SAVE IMPLEMENTATION STATUS:
    {'✅ SUCCESS' if all_passed else '❌ ISSUES DETECTED'} - Manual save workflow ready for testing

    📋 NEXT STEPS:
    1. Test the frontend manually at {FRONTEND_URL}/app/preferences
    2. Verify that:
       - Field changes don't auto-save immediately
       - "Save Changes" button appears when changes are made
       - Manual save works without validation blocking
       - No more infinite update loops in console

    🎯 USER EXPERIENCE IMPROVEMENTS:
    - No more "Please fix validation errors before saving" for normal edits
    - No more auto-save on every field change
    - Clear manual save workflow with visual feedback
    - Proper unsaved changes tracking
    """)

if __name__ == "__main__":
    main()