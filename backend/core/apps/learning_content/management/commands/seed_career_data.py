# File: backend/core/apps/learning_content/management/commands/seed_career_data.py
# Description: Django management command to seed learning paths with career insights data
# Why: Useful for testing and populating existing paths with career data
# Relevant Files: career_insights_service.py, career_data.py, models.py

"""
Seed Career Data Management Command

This command enriches existing learning paths with career insights.

Usage:
    python manage.py seed_career_data                    # Process all paths
    python manage.py seed_career_data --user-id 123      # Process paths for specific user
    python manage.py seed_career_data --path-id abc123   # Process specific path
    python manage.py seed_career_data --dry-run          # Preview changes without saving

Features:
- Adds career_insights to learning paths that don't have them
- Extracts skills_gained from modules
- Generates project_milestones
- Optionally refreshes data for paths that already have career insights
"""

from django.core.management.base import BaseCommand, CommandError
from apps.learning_content.models import CourseRecommendation, LearningPath
from ml_services.services.career_insights_service import get_career_insights_service
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Seed learning paths with career insights data'

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--user-id',
            type=int,
            help='Process paths for specific user ID only'
        )
        parser.add_argument(
            '--path-id',
            type=str,
            help='Process specific path ID only'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving to database'
        )
        parser.add_argument(
            '--refresh',
            action='store_true',
            help='Refresh career data even for paths that already have it'
        )
        parser.add_argument(
            '--location',
            type=str,
            default='',
            help='User location for job market data (e.g., "San Francisco")'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        user_id = options.get('user_id')
        path_id = options.get('path_id')
        dry_run = options.get('dry_run', False)
        refresh = options.get('refresh', False)
        location = options.get('location', '')

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('SEED CAREER DATA COMMAND'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN MODE - No changes will be saved\n'))

        # Get career insights service
        career_service = get_career_insights_service()

        # Build query filters
        query_filters = {}
        if user_id:
            query_filters['user_id'] = user_id
            self.stdout.write(f"📌 Filtering by user ID: {user_id}")

        # Get all course recommendations
        try:
            recommendations = CourseRecommendation.objects.filter(**query_filters)
            total_recs = len(recommendations)

            if total_recs == 0:
                self.stdout.write(self.style.WARNING('⚠️  No course recommendations found'))
                return

            self.stdout.write(f"✅ Found {total_recs} course recommendation(s)\n")

        except Exception as e:
            raise CommandError(f'Error fetching recommendations: {str(e)}')

        # Process each recommendation
        total_paths_processed = 0
        total_paths_updated = 0
        total_paths_skipped = 0

        for rec in recommendations:
            user = User.objects.filter(id=rec.user_id).first()
            username = user.email if user else f"User {rec.user_id}"

            self.stdout.write(f"\n📊 Processing recommendation for: {username}")
            self.stdout.write(f"   Total paths: {len(rec.learning_paths)}")

            # Process each learning path
            for idx, path in enumerate(rec.learning_paths):
                total_paths_processed += 1

                # Apply path_id filter if specified
                if path_id and path.path_id != path_id:
                    continue

                self.stdout.write(f"\n   Path {idx + 1}: {path.title}")
                self.stdout.write(f"      Path ID: {path.path_id}")
                self.stdout.write(f"      Modules: {len(path.modules)}")

                # Check if already has career insights
                if path.career_insights and not refresh:
                    self.stdout.write(self.style.WARNING(
                        f"      ⏭️  Skipping (already has career insights). Use --refresh to update."
                    ))
                    total_paths_skipped += 1
                    continue

                # Generate career insights
                try:
                    # Use path description as learning goals (fallback)
                    learning_goals = path.description or path.title

                    self.stdout.write(f"      🔄 Generating career insights...")

                    # Generate career insights
                    career_insights = career_service.generate_career_insights(
                        learning_goals=learning_goals,
                        modules=path.modules,
                        user_location=location
                    )

                    # Extract skills
                    skills_gained = career_service.extract_skills_from_modules(path.modules)

                    # Generate project milestones
                    # Determine domain first
                    domain = career_service.map_learning_goals_to_career_domain(learning_goals)
                    project_milestones = career_service.generate_project_milestones(
                        path.modules,
                        domain
                    )

                    # Preview results
                    self.stdout.write(self.style.SUCCESS(f"      ✅ Career insights generated:"))
                    self.stdout.write(f"         - Roles: {len(career_insights.career_roles)}")
                    self.stdout.write(f"         - Total job openings: {career_insights.total_job_openings}")
                    self.stdout.write(f"         - Market demand score: {career_insights.market_demand_score}")
                    self.stdout.write(f"         - Skills extracted: {len(skills_gained)}")
                    self.stdout.write(f"         - Project milestones: {len(project_milestones)}")

                    # Show roles
                    for role in career_insights.career_roles:
                        salary_range = f"${role.salary_entry_min:,} - ${role.salary_entry_max:,}"
                        self.stdout.write(
                            f"           • {role.role_title} ({role.experience_level}): "
                            f"{salary_range}, {role.job_openings_count} openings"
                        )

                    # Update path (if not dry run)
                    if not dry_run:
                        path.career_insights = career_insights
                        path.skills_gained = skills_gained
                        path.project_milestones = project_milestones
                        total_paths_updated += 1
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"      🔍 Dry run - not saving changes"
                        ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"      ❌ Error generating career insights: {str(e)}"
                    ))
                    logger.error(f"Error processing path {path.path_id}: {str(e)}", exc_info=True)
                    continue

            # Save recommendation (if not dry run)
            if not dry_run and total_paths_updated > 0:
                try:
                    rec.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"\n✅ Saved recommendation for {username}"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"\n❌ Error saving recommendation: {str(e)}"
                    ))

        # Final summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(f"   Total paths processed: {total_paths_processed}")
        self.stdout.write(f"   Paths updated: {total_paths_updated}")
        self.stdout.write(f"   Paths skipped: {total_paths_skipped}")

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\n🔍 This was a DRY RUN. Run without --dry-run to save changes.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Successfully updated {total_paths_updated} learning path(s)!'
            ))

        self.stdout.write('')
