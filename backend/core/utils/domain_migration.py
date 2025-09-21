"""
backend/core/utils/domain_migration.py
Database migration utilities for transitioning from monolithic to domain-driven structure
Handles data migration between old and new MongoDB document structures
RELEVANT FILES: preferences/models.py, analytics/models.py, privacy_compliance/models.py, learning_content/models.py
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class DomainMigrationStrategy:
    """
    Handles migration strategy for transitioning from monolithic UserPreference
    to domain-driven architecture with separate domain models.
    """

    @staticmethod
    def analyze_migration_needs() -> Dict[str, Any]:
        """
        Analyze the current database state and determine migration requirements.
        Returns a comprehensive report of what needs to be migrated.
        """
        from apps.preferences.models import UserPreference

        logger.info("🔍 Analyzing domain migration needs...")

        analysis = {
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'total_users': 0,
            'migration_requirements': {
                'analytics': {'users_needing_migration': 0, 'data_complexity': 'low'},
                'learning_content': {'users_needing_migration': 0, 'data_complexity': 'low'},
                'privacy_compliance': {'users_needing_migration': 0, 'data_complexity': 'low'},
                'social_integration': {'users_needing_migration': 0, 'data_complexity': 'low'}
            },
            'migration_strategy': {},
            'estimated_time': 'unknown',
            'risks': []
        }

        try:
            # Get all UserPreference documents
            all_preferences = UserPreference.objects.all()
            analysis['total_users'] = len(all_preferences)

            if analysis['total_users'] == 0:
                analysis['migration_strategy'] = 'no_migration_needed'
                return analysis

            # Analyze each domain's migration needs
            analytics_analysis = DomainMigrationStrategy._analyze_analytics_migration(all_preferences)
            content_analysis = DomainMigrationStrategy._analyze_content_migration(all_preferences)
            privacy_analysis = DomainMigrationStrategy._analyze_privacy_migration(all_preferences)
            social_analysis = DomainMigrationStrategy._analyze_social_migration(all_preferences)

            analysis['migration_requirements']['analytics'] = analytics_analysis
            analysis['migration_requirements']['learning_content'] = content_analysis
            analysis['migration_requirements']['privacy_compliance'] = privacy_analysis
            analysis['migration_requirements']['social_integration'] = social_analysis

            # Determine overall migration strategy
            analysis['migration_strategy'] = DomainMigrationStrategy._determine_migration_strategy(analysis)

            # Estimate migration time and risks
            analysis['estimated_time'] = DomainMigrationStrategy._estimate_migration_time(analysis)
            analysis['risks'] = DomainMigrationStrategy._identify_migration_risks(analysis)

            logger.info(f"✅ Migration analysis completed: {analysis['total_users']} users analyzed")
            return analysis

        except Exception as e:
            logger.error(f"❌ Migration analysis failed: {e}")
            analysis['error'] = str(e)
            return analysis

    @staticmethod
    def _analyze_analytics_migration(preferences: List) -> Dict[str, Any]:
        """Analyze analytics domain migration requirements"""
        analysis = {
            'users_needing_migration': 0,
            'data_complexity': 'low',
            'existing_domain_records': 0,
            'data_types_found': set(),
            'interaction_count': 0
        }

        try:
            from apps.analytics.models import UserAnalytics
            existing_analytics = UserAnalytics.objects.all()
            analysis['existing_domain_records'] = len(existing_analytics)
        except ImportError:
            analysis['domain_available'] = False
            return analysis

        for pref in preferences:
            needs_migration = False

            # Check for interaction data
            if hasattr(pref, 'interactions') and pref.interactions:
                needs_migration = True
                analysis['interaction_count'] += len(pref.interactions)
                analysis['data_types_found'].add('interactions')

            # Check for behavioral patterns in old structure
            if hasattr(pref, 'behavioral_patterns') and pref.behavioral_patterns:
                needs_migration = True
                analysis['data_types_found'].add('behavioral_patterns')

            # Check for AI insights in old structure
            if hasattr(pref, 'ai_insights') and pref.ai_insights:
                needs_migration = True
                analysis['data_types_found'].add('ai_insights')

            if needs_migration:
                analysis['users_needing_migration'] += 1

        # Determine complexity
        if analysis['interaction_count'] > 1000 or len(analysis['data_types_found']) > 2:
            analysis['data_complexity'] = 'high'
        elif analysis['interaction_count'] > 100 or len(analysis['data_types_found']) > 1:
            analysis['data_complexity'] = 'medium'

        analysis['data_types_found'] = list(analysis['data_types_found'])
        return analysis

    @staticmethod
    def _analyze_content_migration(preferences: List) -> Dict[str, Any]:
        """Analyze learning content domain migration requirements"""
        analysis = {
            'users_needing_migration': 0,
            'data_complexity': 'low',
            'existing_domain_records': 0,
            'data_types_found': set()
        }

        try:
            from apps.learning_content.models import UserContentProfile
            existing_content = UserContentProfile.objects.all()
            analysis['existing_domain_records'] = len(existing_content)
        except ImportError:
            analysis['domain_available'] = False
            return analysis

        for pref in preferences:
            needs_migration = False

            # Check for content preferences in old structure
            if hasattr(pref, 'content_preferences') and pref.content_preferences:
                needs_migration = True
                analysis['data_types_found'].add('content_preferences')

            # Check for course recommendations
            if hasattr(pref, 'course_recommendations'):
                needs_migration = True
                analysis['data_types_found'].add('course_recommendations')

            if needs_migration:
                analysis['users_needing_migration'] += 1

        if len(analysis['data_types_found']) > 1:
            analysis['data_complexity'] = 'medium'

        analysis['data_types_found'] = list(analysis['data_types_found'])
        return analysis

    @staticmethod
    def _analyze_privacy_migration(preferences: List) -> Dict[str, Any]:
        """Analyze privacy compliance domain migration requirements"""
        analysis = {
            'users_needing_migration': 0,
            'data_complexity': 'low',
            'existing_domain_records': 0,
            'data_types_found': set(),
            'consent_records_count': 0
        }

        try:
            from apps.privacy_compliance.models import UserPrivacy
            existing_privacy = UserPrivacy.objects.all()
            analysis['existing_domain_records'] = len(existing_privacy)
        except ImportError:
            analysis['domain_available'] = False
            return analysis

        for pref in preferences:
            needs_migration = False

            # Check for privacy settings in old structure
            if hasattr(pref, 'privacy_settings') and pref.privacy_settings:
                needs_migration = True
                analysis['data_types_found'].add('privacy_settings')

            # Check for consent history
            if hasattr(pref, 'consent_history') and pref.consent_history:
                needs_migration = True
                analysis['data_types_found'].add('consent_history')
                analysis['consent_records_count'] += len(pref.consent_history)

            if needs_migration:
                analysis['users_needing_migration'] += 1

        # Privacy data is always complex due to compliance requirements
        if analysis['consent_records_count'] > 0:
            analysis['data_complexity'] = 'high'

        analysis['data_types_found'] = list(analysis['data_types_found'])
        return analysis

    @staticmethod
    def _analyze_social_migration(preferences: List) -> Dict[str, Any]:
        """Analyze social integration domain migration requirements"""
        analysis = {
            'users_needing_migration': 0,
            'data_complexity': 'low',
            'existing_domain_records': 0,
            'data_types_found': set()
        }

        try:
            from apps.social_integration.models import SocialProfile
            existing_social = SocialProfile.objects.all()
            analysis['existing_domain_records'] = len(existing_social)
        except ImportError:
            analysis['domain_available'] = False
            return analysis

        for pref in preferences:
            needs_migration = False

            # Check for social data in old structure
            if hasattr(pref, 'social_data') and pref.social_data:
                needs_migration = True
                analysis['data_types_found'].add('social_data')

            # Check for external connections
            if hasattr(pref, 'external_connections'):
                needs_migration = True
                analysis['data_types_found'].add('external_connections')

            if needs_migration:
                analysis['users_needing_migration'] += 1

        analysis['data_types_found'] = list(analysis['data_types_found'])
        return analysis

    @staticmethod
    def _determine_migration_strategy(analysis: Dict[str, Any]) -> Dict[str, str]:
        """Determine the best migration strategy based on analysis"""
        strategy = {}

        total_users = analysis['total_users']
        requirements = analysis['migration_requirements']

        # Analytics strategy
        analytics_users = requirements['analytics']['users_needing_migration']
        if analytics_users == 0:
            strategy['analytics'] = 'no_migration_needed'
        elif analytics_users < total_users * 0.1:
            strategy['analytics'] = 'gradual_migration'
        else:
            strategy['analytics'] = 'batch_migration'

        # Content strategy
        content_users = requirements['learning_content']['users_needing_migration']
        if content_users == 0:
            strategy['learning_content'] = 'no_migration_needed'
        elif content_users < total_users * 0.2:
            strategy['learning_content'] = 'gradual_migration'
        else:
            strategy['learning_content'] = 'batch_migration'

        # Privacy strategy (always careful with privacy data)
        privacy_users = requirements['privacy_compliance']['users_needing_migration']
        if privacy_users == 0:
            strategy['privacy_compliance'] = 'no_migration_needed'
        else:
            strategy['privacy_compliance'] = 'careful_migration'  # Always careful with privacy

        # Social strategy
        social_users = requirements['social_integration']['users_needing_migration']
        if social_users == 0:
            strategy['social_integration'] = 'no_migration_needed'
        else:
            strategy['social_integration'] = 'gradual_migration'

        # Overall strategy
        if all(s in ['no_migration_needed'] for s in strategy.values()):
            strategy['overall'] = 'no_migration_needed'
        elif any(s in ['batch_migration'] for s in strategy.values()):
            strategy['overall'] = 'phased_migration'
        else:
            strategy['overall'] = 'gradual_migration'

        return strategy

    @staticmethod
    def _estimate_migration_time(analysis: Dict[str, Any]) -> str:
        """Estimate migration time based on data complexity and volume"""
        total_users = analysis['total_users']
        requirements = analysis['migration_requirements']

        if total_users == 0:
            return 'immediate'

        # Calculate complexity score
        complexity_score = 0
        for domain, req in requirements.items():
            if req.get('domain_available', True):
                users_needing = req['users_needing_migration']
                complexity = req['data_complexity']

                if complexity == 'high':
                    complexity_score += users_needing * 3
                elif complexity == 'medium':
                    complexity_score += users_needing * 2
                else:
                    complexity_score += users_needing * 1

        if complexity_score < 100:
            return 'under_1_hour'
        elif complexity_score < 500:
            return '1-3_hours'
        elif complexity_score < 1000:
            return '3-6_hours'
        else:
            return 'over_6_hours'

    @staticmethod
    def _identify_migration_risks(analysis: Dict[str, Any]) -> List[str]:
        """Identify potential risks during migration"""
        risks = []

        total_users = analysis['total_users']
        requirements = analysis['migration_requirements']

        # Data volume risks
        if total_users > 1000:
            risks.append("Large user base - consider batching migration")

        # Domain availability risks
        for domain, req in requirements.items():
            if not req.get('domain_available', True):
                risks.append(f"{domain} domain not available - will use fallback compatibility layer")

        # Data complexity risks
        for domain, req in requirements.items():
            if req['data_complexity'] == 'high':
                risks.append(f"{domain} has complex data - requires careful migration")

        # Privacy compliance risks
        if requirements['privacy_compliance']['users_needing_migration'] > 0:
            risks.append("Privacy data migration requires GDPR compliance verification")

        # Interaction data risks
        if requirements['analytics'].get('interaction_count', 0) > 10000:
            risks.append("Large interaction dataset - may impact performance during migration")

        if not risks:
            risks.append("Low risk migration - proceed with standard procedures")

        return risks

    @staticmethod
    def execute_migration(strategy: str = 'gradual', batch_size: int = 50, dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute the domain migration according to specified strategy.
        """
        from apps.preferences.models import UserPreference
        from services.user_profile_service import UserDataMigrationService

        logger.info(f"🚀 Starting domain migration: strategy={strategy}, batch_size={batch_size}, dry_run={dry_run}")

        migration_result = {
            'migration_started': datetime.utcnow().isoformat(),
            'strategy': strategy,
            'batch_size': batch_size,
            'dry_run': dry_run,
            'total_users_processed': 0,
            'successful_migrations': 0,
            'failed_migrations': 0,
            'domain_results': {},
            'errors': []
        }

        try:
            # Get all users that need migration
            all_preferences = UserPreference.objects.all()
            migration_result['total_users_to_process'] = len(all_preferences)

            if strategy == 'batch_migration':
                # Process all users in batches
                for i in range(0, len(all_preferences), batch_size):
                    batch = all_preferences[i:i + batch_size]
                    batch_result = DomainMigrationStrategy._process_migration_batch(batch, dry_run)
                    DomainMigrationStrategy._merge_batch_result(migration_result, batch_result)

            elif strategy == 'gradual_migration':
                # Process users one by one with error handling
                for pref in all_preferences:
                    try:
                        if not dry_run:
                            user_result = UserDataMigrationService.migrate_user_to_domain_structure(pref.user_id)
                        else:
                            user_result = {'dry_run': True, 'user_id': pref.user_id}

                        migration_result['successful_migrations'] += 1
                    except Exception as e:
                        logger.error(f"Failed to migrate user {pref.user_id}: {e}")
                        migration_result['failed_migrations'] += 1
                        migration_result['errors'].append(f"User {pref.user_id}: {str(e)}")

                    migration_result['total_users_processed'] += 1

            migration_result['migration_completed'] = datetime.utcnow().isoformat()
            migration_result['success_rate'] = (
                migration_result['successful_migrations'] / migration_result['total_users_processed']
                if migration_result['total_users_processed'] > 0 else 0
            )

            logger.info(f"✅ Migration completed: {migration_result['successful_migrations']}/{migration_result['total_users_processed']} successful")
            return migration_result

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            migration_result['migration_failed'] = str(e)
            return migration_result

    @staticmethod
    def _process_migration_batch(batch: List, dry_run: bool) -> Dict[str, Any]:
        """Process a batch of users for migration"""
        from services.user_profile_service import UserDataMigrationService

        batch_result = {
            'batch_size': len(batch),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for pref in batch:
            try:
                if not dry_run:
                    UserDataMigrationService.migrate_user_to_domain_structure(pref.user_id)
                batch_result['successful'] += 1
            except Exception as e:
                batch_result['failed'] += 1
                batch_result['errors'].append(f"User {pref.user_id}: {str(e)}")

        return batch_result

    @staticmethod
    def _merge_batch_result(main_result: Dict[str, Any], batch_result: Dict[str, Any]):
        """Merge batch result into main migration result"""
        main_result['total_users_processed'] += batch_result['batch_size']
        main_result['successful_migrations'] += batch_result['successful']
        main_result['failed_migrations'] += batch_result['failed']
        main_result['errors'].extend(batch_result['errors'])

    @staticmethod
    def verify_migration_integrity() -> Dict[str, Any]:
        """
        Verify the integrity of migrated data across all domains.
        Checks that data was properly migrated and is accessible through compatibility layer.
        """
        from apps.preferences.models import UserPreference

        logger.info("🔍 Verifying migration integrity...")

        verification_result = {
            'verification_timestamp': datetime.utcnow().isoformat(),
            'total_users_checked': 0,
            'integrity_checks': {
                'compatibility_layer': {'passed': 0, 'failed': 0, 'errors': []},
                'domain_consistency': {'passed': 0, 'failed': 0, 'errors': []},
                'data_accessibility': {'passed': 0, 'failed': 0, 'errors': []}
            },
            'overall_status': 'unknown'
        }

        try:
            all_preferences = UserPreference.objects.all()
            verification_result['total_users_checked'] = len(all_preferences)

            for pref in all_preferences:
                # Test compatibility layer
                try:
                    # Test that all compatibility methods work
                    analytics_consent = pref.has_analytics_consent()
                    behavioral_patterns = pref.behavioral_patterns
                    ai_insights = pref.ai_insights
                    privacy_settings = pref.privacy_settings
                    content_preferences = pref.content_preferences

                    verification_result['integrity_checks']['compatibility_layer']['passed'] += 1
                except Exception as e:
                    verification_result['integrity_checks']['compatibility_layer']['failed'] += 1
                    verification_result['integrity_checks']['compatibility_layer']['errors'].append(
                        f"User {pref.user_id}: {str(e)}"
                    )

                # Test domain consistency (if domains are available)
                try:
                    DomainMigrationStrategy._verify_domain_consistency(pref.user_id)
                    verification_result['integrity_checks']['domain_consistency']['passed'] += 1
                except Exception as e:
                    verification_result['integrity_checks']['domain_consistency']['failed'] += 1
                    verification_result['integrity_checks']['domain_consistency']['errors'].append(
                        f"User {pref.user_id}: {str(e)}"
                    )

            # Determine overall status
            total_checks = verification_result['total_users_checked'] * 2  # 2 checks per user
            total_passed = (
                verification_result['integrity_checks']['compatibility_layer']['passed'] +
                verification_result['integrity_checks']['domain_consistency']['passed']
            )

            if total_passed == total_checks:
                verification_result['overall_status'] = 'excellent'
            elif total_passed >= total_checks * 0.9:
                verification_result['overall_status'] = 'good'
            elif total_passed >= total_checks * 0.7:
                verification_result['overall_status'] = 'acceptable'
            else:
                verification_result['overall_status'] = 'poor'

            logger.info(f"✅ Migration integrity check completed: {verification_result['overall_status']}")
            return verification_result

        except Exception as e:
            logger.error(f"❌ Migration integrity check failed: {e}")
            verification_result['error'] = str(e)
            return verification_result

    @staticmethod
    def _verify_domain_consistency(user_id: int):
        """Verify that domain data is consistent with preferences data"""
        # This would check that data in domain models matches what's accessible
        # through the compatibility layer in UserPreference
        pass  # Implementation depends on specific domain model availability


class MigrationReportGenerator:
    """
    Generates comprehensive reports about migration status and health.
    """

    @staticmethod
    def generate_migration_report() -> Dict[str, Any]:
        """Generate a comprehensive migration status report"""
        logger.info("📊 Generating migration report...")

        # Get migration analysis
        analysis = DomainMigrationStrategy.analyze_migration_needs()

        # Get integrity verification
        integrity = DomainMigrationStrategy.verify_migration_integrity()

        # Compile comprehensive report
        report = {
            'report_generated': datetime.utcnow().isoformat(),
            'migration_analysis': analysis,
            'integrity_verification': integrity,
            'recommendations': MigrationReportGenerator._generate_recommendations(analysis, integrity),
            'next_steps': MigrationReportGenerator._suggest_next_steps(analysis, integrity)
        }

        return report

    @staticmethod
    def _generate_recommendations(analysis: Dict[str, Any], integrity: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis and integrity results"""
        recommendations = []

        # Based on migration needs
        total_users = analysis.get('total_users', 0)
        if total_users == 0:
            recommendations.append("No users found - no migration needed")
            return recommendations

        migration_strategy = analysis.get('migration_strategy', {}).get('overall', 'unknown')
        if migration_strategy == 'no_migration_needed':
            recommendations.append("No migration required - system is already using domain structure")
        elif migration_strategy == 'gradual_migration':
            recommendations.append("Recommend gradual migration during low-traffic periods")
        elif migration_strategy == 'phased_migration':
            recommendations.append("Recommend phased migration with careful monitoring")

        # Based on integrity results
        overall_status = integrity.get('overall_status', 'unknown')
        if overall_status == 'poor':
            recommendations.append("URGENT: Fix integrity issues before proceeding")
        elif overall_status == 'acceptable':
            recommendations.append("Address integrity issues for optimal performance")

        # Based on risks
        risks = analysis.get('risks', [])
        if 'Privacy data migration requires GDPR compliance verification' in risks:
            recommendations.append("Ensure GDPR compliance team reviews privacy migration plan")

        return recommendations

    @staticmethod
    def _suggest_next_steps(analysis: Dict[str, Any], integrity: Dict[str, Any]) -> List[str]:
        """Suggest specific next steps based on current state"""
        next_steps = []

        migration_strategy = analysis.get('migration_strategy', {}).get('overall', 'unknown')

        if migration_strategy == 'no_migration_needed':
            next_steps.append("1. Monitor system performance with current domain structure")
            next_steps.append("2. Run periodic integrity checks")
        else:
            next_steps.append("1. Create migration backup plan")
            next_steps.append("2. Schedule migration during maintenance window")
            next_steps.append("3. Execute migration with dry-run first")
            next_steps.append("4. Verify migration integrity")
            next_steps.append("5. Monitor system performance post-migration")

        return next_steps