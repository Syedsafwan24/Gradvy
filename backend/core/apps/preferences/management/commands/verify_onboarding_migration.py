"""
backend/core/apps/preferences/management/commands/verify_onboarding_migration.py
Django management command to verify the integrity of onboarding_status migration
Ensures all documents have properly formatted OnboardingStatus embedded documents
RELEVANT FILES: preferences/models.py, migrate_onboarding_status.py
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.preferences.models import UserPreference, OnboardingStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verify the integrity of onboarding_status migration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix any issues found'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Verify only a specific user ID'
        )

    def handle(self, *args, **options):
        fix_issues = options['fix']
        user_id = options.get('user_id')

        self.stdout.write(self.style.SUCCESS('🔍 Starting onboarding_status migration verification...'))

        if fix_issues:
            self.stdout.write(self.style.WARNING('🔧 Auto-fix mode enabled'))

        try:
            # Get documents to verify
            if user_id:
                documents = [UserPreference.get_by_user_id(user_id)]
                documents = [doc for doc in documents if doc]  # Filter out None
            else:
                documents = list(UserPreference.objects.all())

            if not documents:
                self.stdout.write(self.style.WARNING('ℹ️  No documents found to verify'))
                return

            self.stdout.write(f'📊 Verifying {len(documents)} documents...')

            # Perform verification
            verification_results = self._verify_documents(documents, fix_issues)
            self._display_verification_results(verification_results)

        except Exception as e:
            logger.error(f"Verification failed: {e}", exc_info=True)
            raise CommandError(f'Verification failed: {e}')

    def _verify_documents(self, documents, fix_issues):
        """Verify all documents and optionally fix issues"""
        results = {
            'total': len(documents),
            'valid_embedded': 0,
            'legacy_strings': 0,
            'null_status': 0,
            'invalid_format': 0,
            'fixed': 0,
            'issues': [],
            'fixes_applied': []
        }

        for doc in documents:
            try:
                verification = self._verify_single_document(doc, fix_issues)

                # Update counters
                results[verification['status']] += 1

                # Track issues and fixes
                if verification['issue']:
                    results['issues'].append(verification['issue'])

                if verification['fixed']:
                    results['fixed'] += 1
                    results['fixes_applied'].append(verification['fix_description'])

            except Exception as e:
                results['invalid_format'] += 1
                error_msg = f'User {doc.user_id}: Verification error - {str(e)}'
                results['issues'].append(error_msg)
                logger.error(f"Failed to verify user {doc.user_id}: {e}", exc_info=True)

        return results

    def _verify_single_document(self, doc, fix_issues):
        """Verify a single document"""
        verification = {
            'status': 'unknown',
            'issue': None,
            'fixed': False,
            'fix_description': None
        }

        # Check the raw data first
        raw_status = doc._data.get('onboarding_status')

        if raw_status is None:
            verification['status'] = 'null_status'
            verification['issue'] = f'User {doc.user_id}: onboarding_status is null'

            if fix_issues:
                # Create default OnboardingStatus
                doc.onboarding_status = OnboardingStatus()
                doc.save()
                verification['fixed'] = True
                verification['fix_description'] = f'User {doc.user_id}: Created default OnboardingStatus'
                verification['status'] = 'valid_embedded'  # After fix

        elif isinstance(raw_status, str):
            verification['status'] = 'legacy_strings'
            verification['issue'] = f'User {doc.user_id}: Still has string format "{raw_status}"'

            if fix_issues:
                # Trigger auto-migration by accessing the field
                migrated_status = doc.onboarding_status
                doc.save()
                verification['fixed'] = True
                verification['fix_description'] = f'User {doc.user_id}: Auto-migrated "{raw_status}" to embedded document'
                verification['status'] = 'valid_embedded'  # After fix

        else:
            # Should be an embedded document - verify its structure
            try:
                onboarding_status = doc.onboarding_status

                # Check that it's an OnboardingStatus object
                if not isinstance(onboarding_status, OnboardingStatus):
                    verification['status'] = 'invalid_format'
                    verification['issue'] = f'User {doc.user_id}: onboarding_status is not an OnboardingStatus object (type: {type(onboarding_status)})'
                else:
                    # Verify required fields
                    required_fields = ['completed', 'current_step', 'started_at']
                    missing_fields = []

                    for field in required_fields:
                        if not hasattr(onboarding_status, field) or getattr(onboarding_status, field) is None:
                            missing_fields.append(field)

                    if missing_fields:
                        verification['status'] = 'invalid_format'
                        verification['issue'] = f'User {doc.user_id}: Missing required fields: {missing_fields}'

                        if fix_issues:
                            # Fix missing fields
                            self._fix_missing_fields(onboarding_status, missing_fields)
                            doc.save()
                            verification['fixed'] = True
                            verification['fix_description'] = f'User {doc.user_id}: Fixed missing fields {missing_fields}'
                            verification['status'] = 'valid_embedded'  # After fix
                    else:
                        verification['status'] = 'valid_embedded'

            except Exception as e:
                verification['status'] = 'invalid_format'
                verification['issue'] = f'User {doc.user_id}: Error accessing onboarding_status - {str(e)}'

        return verification

    def _fix_missing_fields(self, onboarding_status, missing_fields):
        """Fix missing fields in OnboardingStatus"""
        defaults = {
            'completed': False,
            'current_step': 'welcome',
            'started_at': datetime.utcnow(),
            'completed_steps': [],
            'total_steps': 4,
            'completion_percentage': 0,
            'source': 'web',
            'is_onboarded': False,
            'quick_onboarding_completed': False
        }

        for field in missing_fields:
            if field in defaults:
                setattr(onboarding_status, field, defaults[field])

    def _display_verification_results(self, results):
        """Display verification results"""
        self.stdout.write('\n📊 Verification Results:')
        self.stdout.write(f'   📄 Total documents: {results["total"]}')
        self.stdout.write(f'   ✅ Valid embedded documents: {results["valid_embedded"]}')
        self.stdout.write(f'   🔄 Legacy string format: {results["legacy_strings"]}')
        self.stdout.write(f'   ⚪ Null status: {results["null_status"]}')
        self.stdout.write(f'   ❌ Invalid format: {results["invalid_format"]}')

        if results['fixed'] > 0:
            self.stdout.write(f'   🔧 Issues fixed: {results["fixed"]}')

        # Calculate health score
        healthy = results['valid_embedded']
        total = results['total']
        health_percentage = (healthy / total * 100) if total > 0 else 0

        self.stdout.write(f'\n📈 Migration Health Score: {health_percentage:.1f}%')

        if health_percentage == 100:
            self.stdout.write(self.style.SUCCESS('🎉 Perfect! All documents have valid embedded documents'))
        elif health_percentage >= 90:
            self.stdout.write(self.style.SUCCESS('✅ Excellent! Migration is largely successful'))
        elif health_percentage >= 70:
            self.stdout.write(self.style.WARNING('⚠️  Good! Most documents migrated, some issues remain'))
        else:
            self.stdout.write(self.style.ERROR('❌ Poor! Significant issues found - migration needs attention'))

        # Show issues
        if results['issues']:
            self.stdout.write(f'\n⚠️  Issues Found ({len(results["issues"])}):')
            for issue in results['issues'][:10]:  # Show first 10
                self.stdout.write(f'   • {issue}')
            if len(results['issues']) > 10:
                self.stdout.write(f'   ... and {len(results["issues"]) - 10} more issues')

        # Show fixes applied
        if results['fixes_applied']:
            self.stdout.write(f'\n🔧 Fixes Applied ({len(results["fixes_applied"])}):')
            for fix in results['fixes_applied'][:10]:  # Show first 10
                self.stdout.write(f'   • {fix}')
            if len(results['fixes_applied']) > 10:
                self.stdout.write(f'   ... and {len(results["fixes_applied"]) - 10} more fixes')

        # Recommendations
        self.stdout.write('\n📋 Recommendations:')

        if results['legacy_strings'] > 0:
            self.stdout.write('   🔄 Run migration command to convert remaining string formats:')
            self.stdout.write('      python manage.py migrate_onboarding_status')

        if results['null_status'] > 0:
            self.stdout.write('   ⚪ Fix null status documents:')
            self.stdout.write('      python manage.py verify_onboarding_migration --fix')

        if results['invalid_format'] > 0:
            self.stdout.write('   ❌ Investigate invalid format documents manually')

        if health_percentage == 100:
            self.stdout.write('   🎉 No action needed - migration is complete!')

        # API testing recommendation
        self.stdout.write('   🧪 Test API endpoints to ensure functionality:')
        self.stdout.write('      curl -H "Authorization: Bearer <token>" http://localhost:8000/api/preferences/')

        return results