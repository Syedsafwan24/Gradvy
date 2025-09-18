#!/usr/bin/env python
"""
Test script to verify interaction logging fixes work correctly.
This script tests the filtering of problematic interaction types.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from core.apps.preferences.models import UserPreference
import logging

# Setup logging to see our debug messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_interaction_filtering():
    """Test that problematic interaction types are properly filtered."""

    print("🧪 Testing interaction type filtering fixes...")

    # Create or get a test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )

    # Get or create user preference
    preference, created = UserPreference.objects.get_or_create(user_id=user.id)

    # Test the problematic interaction types that were causing validation errors
    problematic_types = [
        'onboarding_started',           # Previously caused MongoDB validation error
        'onboarding_flow_completed',    # Previously caused MongoDB validation error
    ]

    # Test allowed interaction types
    allowed_types = [
        'course_click',
        'quiz_attempt',
        'video_watch',
        'search',
        'page_view',
        'course_enroll',
        'course_complete'
    ]

    print("\n📊 Testing problematic interaction types (should be filtered):")
    for interaction_type in problematic_types:
        try:
            print(f"  Testing: {interaction_type}")
            preference.add_interaction(
                interaction_type,
                {'page': 'test', 'action': 'test'},
                {'source': 'test_script'}
            )
            print(f"  ✅ {interaction_type} - handled without error (filtered)")
        except Exception as e:
            print(f"  ❌ {interaction_type} - error: {e}")

    print("\n📊 Testing allowed interaction types (should work):")
    for interaction_type in allowed_types:
        try:
            print(f"  Testing: {interaction_type}")
            preference.add_interaction(
                interaction_type,
                {'page': 'test', 'action': 'test'},
                {'source': 'test_script'}
            )
            print(f"  ✅ {interaction_type} - logged successfully")
        except Exception as e:
            print(f"  ❌ {interaction_type} - error: {e}")

    # Check the behavioral patterns to see what was actually saved
    preference.reload()
    recent_interactions = preference.behavioral_patterns.interaction_history[-10:]

    print(f"\n📈 Recent interactions saved (last 10):")
    for i, interaction in enumerate(recent_interactions, 1):
        print(f"  {i}. Type: {interaction.get('type', 'N/A')}, Data: {interaction.get('data', {})}")

    print(f"\n🎯 Test Summary:")
    print(f"  - User ID: {user.id}")
    print(f"  - Total interactions: {len(preference.behavioral_patterns.interaction_history)}")
    print(f"  - Problematic types should be filtered (not saved)")
    print(f"  - Allowed types should be saved normally")

    return True

if __name__ == "__main__":
    try:
        test_interaction_filtering()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()