# Location: backend/core/apps/preferences/management/commands/diagnose_user_preferences.py
# Description: Django management command to diagnose UserPreference document issues
# Purpose: Identify and fix MongoDB schema mismatch problems for specific users
# Relevant Files: models.py, serializers.py, views.py

"""
Django management command to diagnose UserPreference MongoDB document issues
Usage: python manage.py diagnose_user_preferences --user_id 6
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from datetime import datetime
import json
from ...models import UserPreference
from ...serializers import UserPreferenceSerializer
import logging

# Setup logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Diagnose UserPreference MongoDB document issues for specific users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user_id',
            type=int,
            default=6,
            help='User ID to diagnose (default: 6)',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix identified issues',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        fix_issues = options['fix']
        verbose = options['verbose']

        self.stdout.write("🔍 DIAGNOSING USER PREFERENCES DOCUMENT")
        self.stdout.write("=" * 60)
        self.stdout.write(f"User ID: {user_id}")
        self.stdout.write(f"Timestamp: {datetime.utcnow().isoformat()}")
        self.stdout.write(f"Fix Mode: {'ON' if fix_issues else 'OFF'}")

        try:
            # Step 1: Test MongoDB connection
            self.stdout.write("\n📊 MONGODB CONNECTION TEST")
            total_docs = UserPreference.objects.count()
            self.stdout.write(f"✅ MongoDB connected - Total UserPreference documents: {total_docs}")

            # Step 2: Retrieve user document
            self.stdout.write(f"\n🔍 RETRIEVING USER {user_id} DOCUMENT")
            user_preference = UserPreference.get_by_user_id(user_id)

            if not user_preference:
                self.stdout.write(self.style.ERROR(f"❌ No UserPreference document found for user {user_id}"))
                if fix_issues:
                    self.stdout.write("🔧 Creating default document...")
                    user_preference = UserPreference.create_for_user(user_id)
                    self.stdout.write(self.style.SUCCESS(f"✅ Created default document for user {user_id}"))
                else:
                    self.stdout.write("💡 Run with --fix to create a default document")
                    return

            self.stdout.write(self.style.SUCCESS(f"✅ Found UserPreference document for user {user_id}"))
            self.stdout.write(f"   - Created: {user_preference.created_at}")
            self.stdout.write(f"   - Updated: {user_preference.updated_at}")

            # Step 3: Test critical fields
            self.stdout.write(f"\n📋 TESTING CRITICAL FIELDS")

            critical_fields = [
                'user_id', 'created_at', 'updated_at', 'onboarding_status',
                'profile_completion_percentage', 'onboarding_completed_at',
                'quick_onboarding_data', 'basic_info', 'custom_preferences'
            ]

            field_issues = []

            for field in critical_fields:
                try:
                    value = getattr(user_preference, field, None)
                    if value is not None:
                        if verbose:
                            self.stdout.write(f"   ✅ {field}: {type(value).__name__} = {repr(str(value)[:50])}")
                    else:
                        field_issues.append(field)
                        self.stdout.write(self.style.WARNING(f"   ⚠️  {field}: None/Missing"))
                except Exception as e:
                    field_issues.append(field)
                    self.stdout.write(self.style.ERROR(f"   ❌ {field}: Error - {str(e)}"))

            # Step 4: Test problematic properties
            self.stdout.write(f"\n🎯 TESTING PROBLEMATIC PROPERTIES")

            properties_to_test = ['onboarding_completed', 'quick_onboarding_completed']
            property_issues = []

            for prop_name in properties_to_test:
                try:
                    # Test direct property access
                    prop_value = getattr(user_preference, prop_name)
                    self.stdout.write(self.style.SUCCESS(f"   ✅ {prop_name}: {prop_value}"))
                except Exception as e:
                    property_issues.append(prop_name)
                    self.stdout.write(self.style.ERROR(f"   ❌ {prop_name}: Failed - {str(e)}"))

                    # Try manual computation
                    try:
                        onboarding_status = getattr(user_preference, 'onboarding_status', 'not_started')
                        manual_value = onboarding_status in ['quick_completed', 'full_completed']
                        self.stdout.write(f"      💡 Manual computation: {manual_value} (onboarding_status='{onboarding_status}')")
                    except Exception as manual_e:
                        self.stdout.write(self.style.ERROR(f"      ❌ Manual computation failed: {str(manual_e)}"))

            # Step 5: Test serialization
            self.stdout.write(f"\n📤 TESTING SERIALIZATION")

            serialization_failed = False
            try:
                serializer = UserPreferenceSerializer(user_preference)
                serialized_data = serializer.data
                self.stdout.write(self.style.SUCCESS("   ✅ Serialization successful"))
                if verbose:
                    self.stdout.write(f"   - onboarding_completed: {serialized_data.get('onboarding_completed')}")
                    self.stdout.write(f"   - quick_onboarding_completed: {serialized_data.get('quick_onboarding_completed')}")
                    self.stdout.write(f"   - onboarding_status: {serialized_data.get('onboarding_status')}")
            except Exception as e:
                serialization_failed = True
                self.stdout.write(self.style.ERROR(f"   ❌ Serialization failed: {str(e)}"))

            # Step 6: Fix issues if requested
            if fix_issues and (field_issues or property_issues or serialization_failed):
                self.stdout.write(f"\n🔧 APPLYING FIXES")

                fixed_count = 0

                # Fix missing onboarding_status
                if not hasattr(user_preference, 'onboarding_status') or user_preference.onboarding_status is None:
                    user_preference.onboarding_status = 'not_started'
                    fixed_count += 1
                    self.stdout.write("   ✅ Set onboarding_status = 'not_started'")

                # Fix missing profile_completion_percentage
                if not hasattr(user_preference, 'profile_completion_percentage') or user_preference.profile_completion_percentage is None:
                    user_preference.profile_completion_percentage = 0.0
                    fixed_count += 1
                    self.stdout.write("   ✅ Set profile_completion_percentage = 0.0")

                # Fix missing quick_onboarding_data
                if not hasattr(user_preference, 'quick_onboarding_data') or user_preference.quick_onboarding_data is None:
                    user_preference.quick_onboarding_data = {}
                    fixed_count += 1
                    self.stdout.write("   ✅ Set quick_onboarding_data = {}")

                # Fix missing custom_preferences
                if not hasattr(user_preference, 'custom_preferences') or user_preference.custom_preferences is None:
                    user_preference.custom_preferences = {}
                    fixed_count += 1
                    self.stdout.write("   ✅ Set custom_preferences = {}")

                if fixed_count > 0:
                    user_preference.save()
                    self.stdout.write(self.style.SUCCESS(f"   💾 Saved {fixed_count} fixes to database"))
                else:
                    self.stdout.write("   ℹ️  No fixes needed to be applied")

            # Step 7: Final test
            if fix_issues:
                self.stdout.write(f"\n🧪 FINAL VERIFICATION TEST")
                try:
                    # Re-fetch the document
                    user_preference = UserPreference.get_by_user_id(user_id)
                    serializer = UserPreferenceSerializer(user_preference)
                    serialized_data = serializer.data
                    self.stdout.write(self.style.SUCCESS("   ✅ Final serialization test passed"))
                    self.stdout.write(f"   - onboarding_completed: {serialized_data.get('onboarding_completed')}")
                    self.stdout.write(f"   - quick_onboarding_completed: {serialized_data.get('quick_onboarding_completed')}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"   ❌ Final test failed: {str(e)}"))

            # Step 8: Summary
            self.stdout.write(f"\n📊 DIAGNOSIS SUMMARY")
            self.stdout.write("-" * 40)
            self.stdout.write(f"Field Issues Found: {len(field_issues)}")
            self.stdout.write(f"Property Issues Found: {len(property_issues)}")
            self.stdout.write(f"Serialization Issues: {'Yes' if serialization_failed else 'No'}")

            if field_issues:
                self.stdout.write(f"Problematic Fields: {', '.join(field_issues)}")
            if property_issues:
                self.stdout.write(f"Problematic Properties: {', '.join(property_issues)}")

            self.stdout.write(f"\n✅ Diagnosis complete for user {user_id}!")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Critical error during diagnosis: {str(e)}"))
            import traceback
            if verbose:
                self.stdout.write(traceback.format_exc())
            raise CommandError(f'Diagnosis failed: {e}')