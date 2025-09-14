# Location: backend/core/apps/preferences/management/commands/check_schema_validation.py
# Description: Django management command to check MongoDB schema validation issues
# Purpose: Identify users affected by enum validation problems and fix them
# Relevant Files: models.py, views.py

"""
Django management command to check and fix MongoDB schema validation issues
Usage: python manage.py check_schema_validation --fix
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from datetime import datetime
import json
from ...models import UserPreference, ContentPreferences
from pymongo import MongoClient
import logging

# Setup logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check and fix MongoDB schema validation issues for user preferences'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix identified validation issues',
        )
        parser.add_argument(
            '--user_id',
            type=int,
            help='Check specific user ID only',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        fix_issues = options['fix']
        user_id = options.get('user_id')
        verbose = options['verbose']

        self.stdout.write("🔍 CHECKING MONGODB SCHEMA VALIDATION ISSUES")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Timestamp: {datetime.utcnow().isoformat()}")
        self.stdout.write(f"Fix Mode: {'ON' if fix_issues else 'OFF'}")
        self.stdout.write(f"User Filter: {user_id if user_id else 'ALL USERS'}")

        try:
            # Step 1: Check MongoDB connection and get raw collection access
            self.stdout.write("\n📊 MONGODB CONNECTION & SCHEMA INFO")

            # Get MongoDB collection directly
            from mongoengine import connection
            db = connection.get_db()
            collection = db.user_preferences

            total_docs = collection.count_documents({})
            self.stdout.write(f"✅ Connected - Total documents: {total_docs}")

            # Step 2: Check for documents that would fail current validation
            self.stdout.write(f"\n🔍 SCANNING DOCUMENTS FOR VALIDATION ISSUES")

            # Define current valid enums from the model
            valid_platforms = ContentPreferences.PLATFORM_CHOICES
            valid_content_types = ContentPreferences.CONTENT_TYPES
            valid_difficulty_choices = ContentPreferences.DIFFICULTY_CHOICES
            valid_duration_choices = ContentPreferences.DURATION_CHOICES

            if verbose:
                self.stdout.write(f"Valid platforms: {valid_platforms}")
                self.stdout.write(f"Valid content types: {valid_content_types}")

            # Query for documents with potential issues
            query = {}
            if user_id:
                query['user_id'] = user_id

            problematic_docs = []
            validation_issues = {
                'invalid_platforms': [],
                'invalid_content_types': [],
                'invalid_difficulty': [],
                'invalid_duration': [],
                'missing_content_preferences': []
            }

            # Scan documents
            for doc in collection.find(query):
                doc_user_id = doc.get('user_id')
                issues_found = []

                # Check content_preferences
                content_prefs = doc.get('content_preferences')
                if content_prefs:
                    # Check preferred_platforms
                    platforms = content_prefs.get('preferred_platforms', [])
                    invalid_platforms = [p for p in platforms if p not in valid_platforms]
                    if invalid_platforms:
                        issues_found.append(f"Invalid platforms: {invalid_platforms}")
                        validation_issues['invalid_platforms'].append({
                            'user_id': doc_user_id,
                            'invalid_values': invalid_platforms,
                            'current_platforms': platforms
                        })

                    # Check content_types
                    content_types = content_prefs.get('content_types', [])
                    invalid_content_types = [ct for ct in content_types if ct not in valid_content_types]
                    if invalid_content_types:
                        issues_found.append(f"Invalid content types: {invalid_content_types}")
                        validation_issues['invalid_content_types'].append({
                            'user_id': doc_user_id,
                            'invalid_values': invalid_content_types
                        })

                    # Check difficulty_preference
                    difficulty = content_prefs.get('difficulty_preference')
                    if difficulty and difficulty not in valid_difficulty_choices:
                        issues_found.append(f"Invalid difficulty: {difficulty}")
                        validation_issues['invalid_difficulty'].append({
                            'user_id': doc_user_id,
                            'invalid_value': difficulty
                        })

                    # Check duration_preference
                    duration = content_prefs.get('duration_preference')
                    if duration and duration not in valid_duration_choices:
                        issues_found.append(f"Invalid duration: {duration}")
                        validation_issues['invalid_duration'].append({
                            'user_id': doc_user_id,
                            'invalid_value': duration
                        })

                else:
                    # Missing content_preferences entirely
                    validation_issues['missing_content_preferences'].append(doc_user_id)
                    issues_found.append("Missing content_preferences")

                if issues_found:
                    problematic_docs.append({
                        'user_id': doc_user_id,
                        'issues': issues_found
                    })
                    if verbose:
                        self.stdout.write(f"   User {doc_user_id}: {', '.join(issues_found)}")

            # Step 3: Report findings
            self.stdout.write(f"\n📋 VALIDATION ISSUES SUMMARY")
            self.stdout.write("-" * 40)

            total_issues = sum(len(issues) for issues in validation_issues.values())
            self.stdout.write(f"Documents with issues: {len(problematic_docs)}")
            self.stdout.write(f"Total validation issues: {total_issues}")

            for issue_type, issues in validation_issues.items():
                if issues:
                    self.stdout.write(f"  {issue_type.replace('_', ' ').title()}: {len(issues)}")
                    if verbose and issue_type == 'invalid_platforms':
                        for issue in issues[:3]:  # Show first 3 examples
                            self.stdout.write(f"    User {issue['user_id']}: {issue['invalid_values']}")

            # Step 4: Fix issues if requested
            if fix_issues and problematic_docs:
                self.stdout.write(f"\n🔧 APPLYING FIXES")

                fixed_count = 0
                for doc_info in problematic_docs:
                    doc_user_id = doc_info['user_id']

                    try:
                        # Load the document using MongoEngine
                        user_pref = UserPreference.get_by_user_id(doc_user_id)
                        if not user_pref:
                            continue

                        changes_made = []

                        # Fix content preferences
                        if user_pref.content_preferences:
                            cp = user_pref.content_preferences

                            # Fix invalid platforms - remove invalid ones
                            if hasattr(cp, 'preferred_platforms') and cp.preferred_platforms:
                                original_platforms = cp.preferred_platforms.copy()
                                cp.preferred_platforms = [p for p in cp.preferred_platforms if p in valid_platforms]
                                if original_platforms != cp.preferred_platforms:
                                    removed = set(original_platforms) - set(cp.preferred_platforms)
                                    changes_made.append(f"Removed invalid platforms: {list(removed)}")

                            # Fix invalid content types - remove invalid ones
                            if hasattr(cp, 'content_types') and cp.content_types:
                                original_types = cp.content_types.copy()
                                cp.content_types = [ct for ct in cp.content_types if ct in valid_content_types]
                                if original_types != cp.content_types:
                                    removed = set(original_types) - set(cp.content_types)
                                    changes_made.append(f"Removed invalid content types: {list(removed)}")

                            # Fix invalid difficulty - set to default
                            if hasattr(cp, 'difficulty_preference') and cp.difficulty_preference not in valid_difficulty_choices:
                                old_difficulty = cp.difficulty_preference
                                cp.difficulty_preference = 'mixed'
                                changes_made.append(f"Changed difficulty '{old_difficulty}' to 'mixed'")

                            # Fix invalid duration - set to default
                            if hasattr(cp, 'duration_preference') and cp.duration_preference not in valid_duration_choices:
                                old_duration = cp.duration_preference
                                cp.duration_preference = 'mixed'
                                changes_made.append(f"Changed duration '{old_duration}' to 'mixed'")

                        else:
                            # Create default content preferences
                            user_pref.content_preferences = ContentPreferences()
                            changes_made.append("Created default content preferences")

                        if changes_made:
                            user_pref.save()
                            fixed_count += 1
                            self.stdout.write(f"  ✅ Fixed user {doc_user_id}: {'; '.join(changes_made)}")

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  ❌ Failed to fix user {doc_user_id}: {str(e)}"))

                self.stdout.write(self.style.SUCCESS(f"\n🎉 Fixed {fixed_count} user documents"))

            elif fix_issues and not problematic_docs:
                self.stdout.write(f"\n✅ No issues found that need fixing")

            elif not fix_issues and problematic_docs:
                self.stdout.write(f"\n💡 Run with --fix to repair {len(problematic_docs)} problematic documents")

            self.stdout.write(f"\n✅ Schema validation check complete!")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Critical error during schema check: {str(e)}"))
            import traceback
            if verbose:
                self.stdout.write(traceback.format_exc())
            raise CommandError(f'Schema validation check failed: {e}')