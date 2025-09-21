"""
backend/core/services/user_profile_service.py
Orchestrates user profile operations across multiple domain models
Handles complex workflows that span analytics, privacy, content, and social domains
RELEVANT FILES: preferences/models.py, analytics/models.py, privacy_compliance/models.py, learning_content/models.py
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserProfileService:
    """
    Service for managing user profiles across domain boundaries.
    Orchestrates operations between preferences, analytics, privacy, and content domains.
    """

    @staticmethod
    def initialize_user_profile(user_id: int, onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize a complete user profile across all domains.
        Creates records in preferences, analytics, privacy, and learning content domains.
        """
        from apps.preferences.models import UserPreference

        logger.info(f"🚀 Initializing complete user profile for user {user_id}")

        try:
            # Create or get main preferences record
            user_pref = UserPreference.get_by_user_id(user_id)
            if not user_pref:
                user_pref = UserPreference.create_for_user(user_id, onboarding_data.get('basic_info', {}))

            # Initialize domain models through compatibility layer
            user_pref.initialize_domain_models()

            # Extract domain-specific data
            basic_info_data = onboarding_data.get('basic_info', {})
            content_prefs_data = onboarding_data.get('content_preferences', {})
            privacy_prefs_data = onboarding_data.get('privacy_preferences', {})

            results = {
                'user_id': user_id,
                'preferences_created': True,
                'domain_models_initialized': {},
                'errors': []
            }

            # Initialize Analytics Domain
            try:
                analytics_result = UserProfileService._initialize_analytics_domain(user_id, basic_info_data)
                results['domain_models_initialized']['analytics'] = analytics_result
            except Exception as e:
                logger.error(f"Failed to initialize analytics domain for user {user_id}: {e}")
                results['errors'].append(f"Analytics: {str(e)}")

            # Initialize Learning Content Domain
            try:
                content_result = UserProfileService._initialize_content_domain(user_id, content_prefs_data)
                results['domain_models_initialized']['learning_content'] = content_result
            except Exception as e:
                logger.error(f"Failed to initialize content domain for user {user_id}: {e}")
                results['errors'].append(f"Learning Content: {str(e)}")

            # Initialize Privacy Compliance Domain
            try:
                privacy_result = UserProfileService._initialize_privacy_domain(user_id, privacy_prefs_data)
                results['domain_models_initialized']['privacy_compliance'] = privacy_result
            except Exception as e:
                logger.error(f"Failed to initialize privacy domain for user {user_id}: {e}")
                results['errors'].append(f"Privacy: {str(e)}")

            # Initialize Social Integration Domain (optional)
            try:
                social_result = UserProfileService._initialize_social_domain(user_id)
                results['domain_models_initialized']['social_integration'] = social_result
            except Exception as e:
                logger.error(f"Failed to initialize social domain for user {user_id}: {e}")
                results['errors'].append(f"Social: {str(e)}")

            user_pref.save()
            logger.info(f"✅ User profile initialization completed for user {user_id}")

            return results

        except Exception as e:
            logger.error(f"❌ Failed to initialize user profile for user {user_id}: {e}")
            raise

    @staticmethod
    def _initialize_analytics_domain(user_id: int, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize analytics domain models for user"""
        try:
            from apps.analytics.models import UserAnalytics, BehavioralPatterns

            # Create analytics record if it doesn't exist
            analytics = UserAnalytics.get_by_user_id(user_id)
            if not analytics:
                analytics = UserAnalytics.create_for_user(user_id)

                # Initialize behavioral patterns based on onboarding data
                if basic_info.get('learning_style'):
                    analytics.behavioral_patterns.preferred_learning_styles = basic_info['learning_style']

                if basic_info.get('time_availability'):
                    # Map time availability to optimal session length
                    time_mapping = {
                        '1-2hrs': 60,  # minutes
                        '3-5hrs': 120,
                        '5+hrs': 180
                    }
                    analytics.behavioral_patterns.optimal_session_length = time_mapping.get(
                        basic_info['time_availability'], 90
                    )

                analytics.save()

            return {'created': True, 'model': 'UserAnalytics', 'user_id': user_id}

        except ImportError:
            return {'created': False, 'reason': 'Analytics domain not available'}

    @staticmethod
    def _initialize_content_domain(user_id: int, content_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize learning content domain models for user"""
        try:
            from apps.learning_content.models import UserContentProfile, ContentPreferences

            # Create content profile if it doesn't exist
            content_profile = UserContentProfile.get_by_user_id(user_id)
            if not content_profile:
                content_profile = UserContentProfile.create_for_user(user_id, content_prefs)

            return {'created': True, 'model': 'UserContentProfile', 'user_id': user_id}

        except ImportError:
            return {'created': False, 'reason': 'Learning content domain not available'}

    @staticmethod
    def _initialize_privacy_domain(user_id: int, privacy_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize privacy compliance domain models for user"""
        try:
            from apps.privacy_compliance.models import UserPrivacy, PrivacySettings

            # Create privacy record if it doesn't exist
            privacy_record = UserPrivacy.get_by_user_id(user_id)
            if not privacy_record:
                privacy_record = UserPrivacy.create_for_user(user_id)

                # Set default privacy settings based on preferences
                if privacy_prefs:
                    privacy_record.privacy_settings.allow_analytics = privacy_prefs.get('analytics', False)
                    privacy_record.privacy_settings.allow_personalization = privacy_prefs.get('personalization', False)
                    privacy_record.privacy_settings.allow_marketing = privacy_prefs.get('marketing', False)
                    privacy_record.save()

            return {'created': True, 'model': 'UserPrivacy', 'user_id': user_id}

        except ImportError:
            return {'created': False, 'reason': 'Privacy compliance domain not available'}

    @staticmethod
    def _initialize_social_domain(user_id: int) -> Dict[str, Any]:
        """Initialize social integration domain models for user"""
        try:
            from apps.social_integration.models import SocialProfile

            # Create social profile placeholder
            social_profile = SocialProfile.get_by_user_id(user_id)
            if not social_profile:
                social_profile = SocialProfile.create_for_user(user_id)

            return {'created': True, 'model': 'SocialProfile', 'user_id': user_id}

        except ImportError:
            return {'created': False, 'reason': 'Social integration domain not available'}

    @staticmethod
    def get_comprehensive_user_data(user_id: int) -> Dict[str, Any]:
        """
        Retrieve comprehensive user data from all domains.
        Aggregates data from preferences, analytics, privacy, content, and social domains.
        """
        from apps.preferences.models import UserPreference

        logger.info(f"🔍 Retrieving comprehensive data for user {user_id}")

        user_pref = UserPreference.get_by_user_id(user_id)
        if not user_pref:
            return {'error': 'User preferences not found', 'user_id': user_id}

        comprehensive_data = {
            'user_id': user_id,
            'last_updated': datetime.utcnow().isoformat(),
            'preferences': {
                'basic_info': user_pref.basic_info.__dict__ if user_pref.basic_info else None,
                'onboarding_status': user_pref.onboarding_completed,
                'profile_completion': user_pref.profile_completion_percentage,
            },
            'analytics': {},
            'learning_content': {},
            'privacy_compliance': {},
            'social_integration': {},
            'cross_domain_insights': {}
        }

        # Gather analytics data
        try:
            analytics_data = UserProfileService._get_analytics_data(user_id)
            comprehensive_data['analytics'] = analytics_data
        except Exception as e:
            comprehensive_data['analytics'] = {'error': str(e)}

        # Gather learning content data
        try:
            content_data = UserProfileService._get_content_data(user_id)
            comprehensive_data['learning_content'] = content_data
        except Exception as e:
            comprehensive_data['learning_content'] = {'error': str(e)}

        # Gather privacy data
        try:
            privacy_data = UserProfileService._get_privacy_data(user_id)
            comprehensive_data['privacy_compliance'] = privacy_data
        except Exception as e:
            comprehensive_data['privacy_compliance'] = {'error': str(e)}

        # Gather social data
        try:
            social_data = UserProfileService._get_social_data(user_id)
            comprehensive_data['social_integration'] = social_data
        except Exception as e:
            comprehensive_data['social_integration'] = {'error': str(e)}

        # Generate cross-domain insights
        try:
            insights = UserProfileService._generate_cross_domain_insights(comprehensive_data)
            comprehensive_data['cross_domain_insights'] = insights
        except Exception as e:
            comprehensive_data['cross_domain_insights'] = {'error': str(e)}

        return comprehensive_data

    @staticmethod
    def _get_analytics_data(user_id: int) -> Dict[str, Any]:
        """Get analytics data from analytics domain"""
        try:
            from apps.analytics.models import UserAnalytics
            analytics = UserAnalytics.get_by_user_id(user_id)
            if analytics:
                return {
                    'total_interactions': analytics.total_interactions,
                    'engagement_score': analytics.behavioral_patterns.engagement_score if analytics.behavioral_patterns else 0,
                    'learning_velocity': analytics.behavioral_patterns.learning_velocity if analytics.behavioral_patterns else 0,
                    'recent_activity': len(analytics.get_recent_interactions(7)) if hasattr(analytics, 'get_recent_interactions') else 0
                }
            return {'available': False}
        except ImportError:
            return {'available': False, 'reason': 'Analytics domain not available'}

    @staticmethod
    def _get_content_data(user_id: int) -> Dict[str, Any]:
        """Get learning content data from content domain"""
        try:
            from apps.learning_content.models import UserContentProfile
            content_profile = UserContentProfile.get_by_user_id(user_id)
            if content_profile:
                return {
                    'preferred_platforms': content_profile.content_preferences.preferred_platforms if content_profile.content_preferences else [],
                    'content_types': content_profile.content_preferences.content_types if content_profile.content_preferences else [],
                    'difficulty_preference': content_profile.content_preferences.difficulty_preference if content_profile.content_preferences else None
                }
            return {'available': False}
        except ImportError:
            return {'available': False, 'reason': 'Learning content domain not available'}

    @staticmethod
    def _get_privacy_data(user_id: int) -> Dict[str, Any]:
        """Get privacy data from privacy domain"""
        try:
            from apps.privacy_compliance.models import UserPrivacy
            privacy_record = UserPrivacy.get_by_user_id(user_id)
            if privacy_record:
                return {
                    'allow_analytics': privacy_record.privacy_settings.allow_analytics if privacy_record.privacy_settings else False,
                    'allow_personalization': privacy_record.privacy_settings.allow_personalization if privacy_record.privacy_settings else False,
                    'consent_records_count': len(privacy_record.consent_records) if privacy_record.consent_records else 0
                }
            return {'available': False}
        except ImportError:
            return {'available': False, 'reason': 'Privacy compliance domain not available'}

    @staticmethod
    def _get_social_data(user_id: int) -> Dict[str, Any]:
        """Get social data from social domain"""
        try:
            from apps.social_integration.models import SocialProfile
            social_profile = SocialProfile.get_by_user_id(user_id)
            if social_profile:
                return {
                    'connected_platforms': len(social_profile.social_connections) if social_profile.social_connections else 0,
                    'profile_data_available': bool(social_profile.profile_data)
                }
            return {'available': False}
        except ImportError:
            return {'available': False, 'reason': 'Social integration domain not available'}

    @staticmethod
    def _generate_cross_domain_insights(comprehensive_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights that span multiple domains"""
        insights = {
            'profile_health_score': 0,
            'data_completeness': {},
            'engagement_factors': [],
            'privacy_compliance_level': 'unknown',
            'recommendations': []
        }

        # Calculate profile health score
        health_factors = []

        if comprehensive_data['preferences'].get('profile_completion', 0) > 80:
            health_factors.append(25)
        elif comprehensive_data['preferences'].get('profile_completion', 0) > 50:
            health_factors.append(15)

        if comprehensive_data['analytics'].get('engagement_score', 0) > 0.7:
            health_factors.append(25)
        elif comprehensive_data['analytics'].get('engagement_score', 0) > 0.4:
            health_factors.append(15)

        if comprehensive_data['learning_content'].get('available', False):
            health_factors.append(20)

        if comprehensive_data['privacy_compliance'].get('available', False):
            health_factors.append(15)

        if comprehensive_data['social_integration'].get('available', False):
            health_factors.append(15)

        insights['profile_health_score'] = sum(health_factors)

        # Generate recommendations based on cross-domain analysis
        recommendations = []

        if comprehensive_data['preferences'].get('profile_completion', 0) < 70:
            recommendations.append("Complete your profile to get better recommendations")

        if comprehensive_data['analytics'].get('engagement_score', 0) < 0.5:
            recommendations.append("Try engaging more with learning content to improve recommendations")

        if not comprehensive_data['learning_content'].get('available', False):
            recommendations.append("Set your learning preferences to get personalized content")

        insights['recommendations'] = recommendations

        return insights


class UserDataMigrationService:
    """
    Service for handling data migration between old monolithic structure and new domain structure.
    Helps migrate existing users to the new domain-driven architecture.
    """

    @staticmethod
    def migrate_user_to_domain_structure(user_id: int) -> Dict[str, Any]:
        """
        Migrate a user from old monolithic structure to new domain structure.
        Extracts data from old fields and creates proper domain models.
        """
        from apps.preferences.models import UserPreference

        logger.info(f"🔄 Migrating user {user_id} to domain structure")

        user_pref = UserPreference.get_by_user_id(user_id)
        if not user_pref:
            return {'error': 'User preferences not found', 'user_id': user_id}

        migration_results = {
            'user_id': user_id,
            'migration_started': datetime.utcnow().isoformat(),
            'domains_migrated': {},
            'errors': [],
            'warnings': []
        }

        # Migrate to analytics domain
        try:
            analytics_result = UserDataMigrationService._migrate_analytics_data(user_pref)
            migration_results['domains_migrated']['analytics'] = analytics_result
        except Exception as e:
            logger.error(f"Analytics migration failed for user {user_id}: {e}")
            migration_results['errors'].append(f"Analytics: {str(e)}")

        # Migrate to content domain
        try:
            content_result = UserDataMigrationService._migrate_content_data(user_pref)
            migration_results['domains_migrated']['learning_content'] = content_result
        except Exception as e:
            logger.error(f"Content migration failed for user {user_id}: {e}")
            migration_results['errors'].append(f"Learning Content: {str(e)}")

        # Migrate to privacy domain
        try:
            privacy_result = UserDataMigrationService._migrate_privacy_data(user_pref)
            migration_results['domains_migrated']['privacy_compliance'] = privacy_result
        except Exception as e:
            logger.error(f"Privacy migration failed for user {user_id}: {e}")
            migration_results['errors'].append(f"Privacy: {str(e)}")

        migration_results['migration_completed'] = datetime.utcnow().isoformat()
        logger.info(f"✅ Migration completed for user {user_id}")

        return migration_results

    @staticmethod
    def _migrate_analytics_data(user_pref) -> Dict[str, Any]:
        """Migrate analytics-related data to analytics domain"""
        try:
            from apps.analytics.models import UserAnalytics

            analytics = UserAnalytics.get_by_user_id(user_pref.user_id)
            if not analytics:
                analytics = UserAnalytics.create_for_user(user_pref.user_id)

            # Migrate interaction data if it exists in old structure
            if hasattr(user_pref, 'interactions') and user_pref.interactions:
                for interaction in user_pref.interactions:
                    analytics.add_interaction(
                        interaction.type,
                        interaction.data,
                        interaction.context if hasattr(interaction, 'context') else {}
                    )

            analytics.save()
            return {'migrated': True, 'interactions_count': len(user_pref.interactions) if user_pref.interactions else 0}

        except ImportError:
            return {'migrated': False, 'reason': 'Analytics domain not available'}

    @staticmethod
    def _migrate_content_data(user_pref) -> Dict[str, Any]:
        """Migrate content-related data to learning content domain"""
        try:
            from apps.learning_content.models import UserContentProfile, ContentPreferences

            content_profile = UserContentProfile.get_by_user_id(user_pref.user_id)
            if not content_profile:
                # Extract content preferences from old structure if available
                content_data = {}
                if hasattr(user_pref, 'content_preferences') and user_pref.content_preferences:
                    content_data = {
                        'preferred_platforms': user_pref.content_preferences.preferred_platforms,
                        'content_types': user_pref.content_preferences.content_types,
                        'difficulty_preference': user_pref.content_preferences.difficulty_preference,
                        'duration_preference': user_pref.content_preferences.duration_preference,
                        'language_preference': user_pref.content_preferences.language_preference,
                    }

                content_profile = UserContentProfile.create_for_user(user_pref.user_id, content_data)

            return {'migrated': True, 'preferences_migrated': bool(content_profile.content_preferences)}

        except ImportError:
            return {'migrated': False, 'reason': 'Learning content domain not available'}

    @staticmethod
    def _migrate_privacy_data(user_pref) -> Dict[str, Any]:
        """Migrate privacy-related data to privacy compliance domain"""
        try:
            from apps.privacy_compliance.models import UserPrivacy

            privacy_record = UserPrivacy.get_by_user_id(user_pref.user_id)
            if not privacy_record:
                privacy_record = UserPrivacy.create_for_user(user_pref.user_id)

                # Migrate privacy settings if they exist in old structure
                if hasattr(user_pref, 'privacy_settings') and user_pref.privacy_settings:
                    privacy_record.privacy_settings.allow_analytics = user_pref.privacy_settings.allow_analytics
                    privacy_record.privacy_settings.allow_personalization = user_pref.privacy_settings.allow_personalization
                    privacy_record.privacy_settings.allow_marketing = getattr(user_pref.privacy_settings, 'allow_marketing', False)

                privacy_record.save()

            return {'migrated': True, 'settings_migrated': bool(privacy_record.privacy_settings)}

        except ImportError:
            return {'migrated': False, 'reason': 'Privacy compliance domain not available'}