"""
backend/core/apps/preferences/management/commands/migrate_onboarding_status.py
Django management command to permanently migrate onboarding_status from string to embedded document
Handles the schema migration for all existing UserPreference documents
RELEVANT FILES: preferences/models.py, utils/domain_migration.py
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.preferences.models import UserPreference, OnboardingStatus
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate onboarding_status from string format to OnboardingStatus embedded document'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of documents to process per batch (default: 100)'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Migrate only a specific user ID (for testing)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        user_id = options.get('user_id')

        self.stdout.write(self.style.SUCCESS('🔄 Starting onboarding_status migration...'))

        if dry_run:
            self.stdout.write(self.style.WARNING('📋 DRY RUN MODE - No changes will be made'))

        try:
            # Get all documents that need migration
            if user_id:
                documents = [UserPreference.get_by_user_id(user_id)]
                documents = [doc for doc in documents if doc]  # Filter out None
            else:
                documents = list(UserPreference.objects.all())

            if not documents:
                self.stdout.write(self.style.WARNING('ℹ️  No documents found to migrate'))
                return

            self.stdout.write(f'📊 Found {len(documents)} total documents')

            # Analyze migration needs
            migration_stats = self._analyze_migration_needs(documents)
            self._display_analysis(migration_stats)

            if migration_stats['needs_migration'] == 0:
                self.stdout.write(self.style.SUCCESS('✅ No migration needed - all documents already use embedded format'))
                return

            if not dry_run:
                confirm = input(f'\n🔄 Proceed with migrating {migration_stats["needs_migration"]} documents? (y/N): ')
                if confirm.lower() != 'y':
                    self.stdout.write(self.style.WARNING('❌ Migration cancelled by user'))
                    return

            # Perform migration
            migration_results = self._perform_migration(documents, batch_size, dry_run)
            self._display_results(migration_results)

        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            raise CommandError(f'Migration failed: {e}')

    def _analyze_migration_needs(self, documents):
        """Analyze which documents need migration"""
        stats = {
            'total': len(documents),
            'needs_migration': 0,
            'already_migrated': 0,
            'null_status': 0,
            'string_formats': {},
            'problematic': []
        }

        for doc in documents:
            try:
                # Access the raw onboarding_status field
                raw_status = doc._data.get('onboarding_status')

                if raw_status is None:
                    stats['null_status'] += 1
                elif isinstance(raw_status, str):
                    stats['needs_migration'] += 1
                    stats['string_formats'][raw_status] = stats['string_formats'].get(raw_status, 0) + 1
                elif isinstance(raw_status, dict) or hasattr(raw_status, 'completed'):
                    stats['already_migrated'] += 1
                else:
                    stats['problematic'].append((doc.user_id, type(raw_status), str(raw_status)))

            except Exception as e:
                stats['problematic'].append((doc.user_id, 'error', str(e)))

        return stats

    def _display_analysis(self, stats):
        """Display migration analysis results"""
        self.stdout.write('\n📊 Migration Analysis:')
        self.stdout.write(f'   📄 Total documents: {stats["total"]}')
        self.stdout.write(f'   🔄 Need migration: {stats["needs_migration"]}')
        self.stdout.write(f'   ✅ Already migrated: {stats["already_migrated"]}')
        self.stdout.write(f'   ⚪ Null status: {stats["null_status"]}')

        if stats['problematic']:
            self.stdout.write(f'   ⚠️  Problematic: {len(stats["problematic"])}')

        if stats['string_formats']:
            self.stdout.write('\n📋 String formats found:')
            for format_str, count in stats['string_formats'].items():
                self.stdout.write(f'   • "{format_str}": {count} documents')

        if stats['problematic']:
            self.stdout.write('\n⚠️  Problematic documents:')
            for user_id, type_info, value in stats['problematic'][:5]:  # Show first 5
                self.stdout.write(f'   • User {user_id}: {type_info} = {value}')
            if len(stats['problematic']) > 5:
                self.stdout.write(f'   ... and {len(stats["problematic"]) - 5} more')

    def _perform_migration(self, documents, batch_size, dry_run):
        """Perform the actual migration"""
        results = {
            'total_processed': 0,
            'successfully_migrated': 0,
            'already_migrated': 0,
            'failed': 0,
            'errors': []
        }

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            self.stdout.write(f'\n📦 Processing batch {i//batch_size + 1} ({len(batch)} documents)...')

            batch_results = self._migrate_batch(batch, dry_run)

            # Update totals
            results['total_processed'] += batch_results['processed']
            results['successfully_migrated'] += batch_results['migrated']
            results['already_migrated'] += batch_results['skipped']
            results['failed'] += batch_results['failed']
            results['errors'].extend(batch_results['errors'])

            self.stdout.write(f'   ✅ Batch complete: {batch_results["migrated"]} migrated, {batch_results["skipped"]} skipped, {batch_results["failed"]} failed')

        return results

    def _migrate_batch(self, documents, dry_run):
        """Migrate a batch of documents"""
        batch_results = {
            'processed': 0,
            'migrated': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }

        for doc in documents:
            batch_results['processed'] += 1

            try:
                # Check if migration is needed
                raw_status = doc._data.get('onboarding_status')

                if not isinstance(raw_status, str):
                    batch_results['skipped'] += 1
                    continue

                # Perform migration
                if not dry_run:
                    # The CompatibleOnboardingStatusField will auto-migrate when we access it
                    migrated_status = doc.onboarding_status  # This triggers auto-migration

                    # Force save to persist the migrated data
                    doc.save()

                    # Verify migration worked
                    if hasattr(migrated_status, 'completed'):
                        batch_results['migrated'] += 1
                        self.stdout.write(f'   🔄 Migrated user {doc.user_id}: "{raw_status}" → OnboardingStatus(completed={migrated_status.completed})')
                    else:
                        batch_results['failed'] += 1
                        batch_results['errors'].append(f'User {doc.user_id}: Migration result is not an OnboardingStatus object')
                else:
                    # Dry run - just show what would happen
                    batch_results['migrated'] += 1
                    self.stdout.write(f'   🔄 [DRY RUN] Would migrate user {doc.user_id}: "{raw_status}" → OnboardingStatus')

            except Exception as e:
                batch_results['failed'] += 1
                error_msg = f'User {doc.user_id}: {str(e)}'
                batch_results['errors'].append(error_msg)
                logger.error(f"Failed to migrate user {doc.user_id}: {e}", exc_info=True)

        return batch_results

    def _display_results(self, results):
        """Display migration results"""
        self.stdout.write('\n📊 Migration Results:')
        self.stdout.write(f'   📄 Total processed: {results["total_processed"]}')
        self.stdout.write(f'   ✅ Successfully migrated: {results["successfully_migrated"]}')
        self.stdout.write(f'   ⏭️  Already migrated: {results["already_migrated"]}')
        self.stdout.write(f'   ❌ Failed: {results["failed"]}')

        if results['errors']:
            self.stdout.write(f'\n❌ Errors ({len(results["errors"])}):')
            for error in results['errors'][:10]:  # Show first 10 errors
                self.stdout.write(f'   • {error}')
            if len(results['errors']) > 10:
                self.stdout.write(f'   ... and {len(results["errors"]) - 10} more errors')

        # Calculate success rate
        if results['total_processed'] > 0:
            success_rate = (results['successfully_migrated'] / results['total_processed']) * 100
            self.stdout.write(f'\n📈 Success rate: {success_rate:.1f}%')

        if results['failed'] == 0:
            self.stdout.write(self.style.SUCCESS('\n🎉 Migration completed successfully!'))
        elif results['successfully_migrated'] > 0:
            self.stdout.write(self.style.WARNING('\n⚠️  Migration completed with some errors'))
        else:
            self.stdout.write(self.style.ERROR('\n❌ Migration failed - no documents were migrated'))

        # Next steps
        if results['successfully_migrated'] > 0:
            self.stdout.write('\n📋 Next Steps:')
            self.stdout.write('   1. Verify data integrity with: python manage.py verify_onboarding_migration')
            self.stdout.write('   2. Test API endpoints to ensure functionality')
            self.stdout.write('   3. Monitor application logs for any issues')
            if results['failed'] > 0:
                self.stdout.write('   4. Review and fix failed migrations')