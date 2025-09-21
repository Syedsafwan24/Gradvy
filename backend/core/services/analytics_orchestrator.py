"""
backend/core/services/analytics_orchestrator.py
Orchestrates analytics operations across multiple domains
Coordinates behavioral analysis, AI insights, and cross-domain analytics
RELEVANT FILES: analytics/models.py, preferences/models.py, learning_content/models.py
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AnalyticsOrchestrator:
    """
    Orchestrates analytics operations across domain boundaries.
    Handles complex analytics workflows that require data from multiple domains.
    """

    @staticmethod
    def process_user_interaction(user_id: int, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user interaction across all relevant domains.
        Updates analytics, behavioral patterns, and triggers cross-domain insights.
        """
        from apps.preferences.models import UserPreference

        logger.info(f"📊 Processing interaction for user {user_id}: {interaction_data.get('type', 'unknown')}")

        try:
            user_pref = UserPreference.get_by_user_id(user_id)
            if not user_pref:
                return {'error': 'User preferences not found', 'user_id': user_id}

            # Check privacy consent before processing
            if not user_pref.has_analytics_consent():
                return {'status': 'skipped', 'reason': 'no_analytics_consent', 'user_id': user_id}

            results = {
                'user_id': user_id,
                'interaction_type': interaction_data.get('type'),
                'processed_at': datetime.utcnow().isoformat(),
                'domains_updated': {},
                'insights_triggered': []
            }

            # Add interaction to preferences (compatibility layer)
            user_pref.add_interaction(
                interaction_data.get('type', 'page_view'),
                interaction_data.get('data', {}),
                interaction_data.get('context', {})
            )

            # Process in analytics domain
            try:
                analytics_result = AnalyticsOrchestrator._process_analytics_domain(user_id, interaction_data)
                results['domains_updated']['analytics'] = analytics_result
            except Exception as e:
                logger.error(f"Analytics domain processing failed: {e}")
                results['domains_updated']['analytics'] = {'error': str(e)}

            # Update behavioral patterns
            try:
                behavioral_result = AnalyticsOrchestrator._update_behavioral_patterns(user_id, interaction_data)
                results['domains_updated']['behavioral_patterns'] = behavioral_result
            except Exception as e:
                logger.error(f"Behavioral patterns update failed: {e}")
                results['domains_updated']['behavioral_patterns'] = {'error': str(e)}

            # Trigger insights if threshold reached
            try:
                insights_result = AnalyticsOrchestrator._check_insights_triggers(user_id, interaction_data)
                results['insights_triggered'] = insights_result
            except Exception as e:
                logger.error(f"Insights trigger check failed: {e}")
                results['insights_triggered'] = {'error': str(e)}

            return results

        except Exception as e:
            logger.error(f"❌ Failed to process interaction for user {user_id}: {e}")
            raise

    @staticmethod
    def _process_analytics_domain(user_id: int, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process interaction in analytics domain"""
        try:
            from apps.analytics.models import UserAnalytics

            analytics = UserAnalytics.get_by_user_id(user_id)
            if not analytics:
                analytics = UserAnalytics.create_for_user(user_id)

            # Add interaction to analytics record
            analytics.add_interaction(
                interaction_data.get('type', 'page_view'),
                interaction_data.get('data', {}),
                interaction_data.get('context', {})
            )

            # Update analytics metrics
            analytics.update_metrics()
            analytics.save()

            return {'processed': True, 'total_interactions': analytics.total_interactions}

        except ImportError:
            return {'processed': False, 'reason': 'Analytics domain not available'}

    @staticmethod
    def _update_behavioral_patterns(user_id: int, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update behavioral patterns based on interaction"""
        try:
            from apps.analytics.models import UserAnalytics

            analytics = UserAnalytics.get_by_user_id(user_id)
            if not analytics or not analytics.behavioral_patterns:
                return {'updated': False, 'reason': 'No behavioral patterns found'}

            interaction_type = interaction_data.get('type', '')
            updates = {}

            # Update engagement score based on interaction type
            if interaction_type in ['course_interaction', 'learning_activity', 'quiz_attempt']:
                current_score = analytics.behavioral_patterns.engagement_score or 0.0
                analytics.behavioral_patterns.engagement_score = min(1.0, current_score + 0.05)
                updates['engagement_score'] = analytics.behavioral_patterns.engagement_score

            # Update learning velocity for learning-related interactions
            if interaction_type in ['course_complete', 'quiz_complete', 'lesson_complete']:
                current_velocity = analytics.behavioral_patterns.learning_velocity or 0.0
                analytics.behavioral_patterns.learning_velocity = min(1.0, current_velocity + 0.1)
                updates['learning_velocity'] = analytics.behavioral_patterns.learning_velocity

            # Track content type preferences
            content_type = interaction_data.get('data', {}).get('content_type')
            if content_type and interaction_type in ['course_interaction', 'video_play', 'article_read']:
                current_types = analytics.behavioral_patterns.preferred_content_types or []
                if content_type not in current_types:
                    current_types.append(content_type)
                    analytics.behavioral_patterns.preferred_content_types = current_types
                    updates['preferred_content_types'] = current_types

            # Update peak activity hours
            current_hour = datetime.utcnow().hour
            peak_hours = analytics.behavioral_patterns.peak_activity_hours or []
            if current_hour not in peak_hours:
                peak_hours.append(current_hour)
                analytics.behavioral_patterns.peak_activity_hours = peak_hours[-5:]  # Keep last 5 hours
                updates['peak_activity_hours'] = analytics.behavioral_patterns.peak_activity_hours

            analytics.behavioral_patterns.last_analyzed = datetime.utcnow()
            analytics.save()

            return {'updated': True, 'changes': updates}

        except ImportError:
            return {'updated': False, 'reason': 'Analytics domain not available'}

    @staticmethod
    def _check_insights_triggers(user_id: int, interaction_data: Dict[str, Any]) -> List[str]:
        """Check if interaction should trigger AI insights generation"""
        try:
            from apps.analytics.models import UserAnalytics

            analytics = UserAnalytics.get_by_user_id(user_id)
            if not analytics:
                return []

            triggers = []

            # Check total interactions threshold
            if analytics.total_interactions % 50 == 0:  # Every 50 interactions
                triggers.append('interaction_milestone')

            # Check engagement level changes
            if analytics.behavioral_patterns and analytics.behavioral_patterns.engagement_score:
                if analytics.behavioral_patterns.engagement_score > 0.8:
                    triggers.append('high_engagement')
                elif analytics.behavioral_patterns.engagement_score < 0.3:
                    triggers.append('low_engagement_warning')

            # Check for learning pattern changes
            interaction_type = interaction_data.get('type', '')
            if interaction_type in ['course_complete', 'quiz_complete'] and len(triggers) == 0:
                triggers.append('learning_progress')

            # Schedule insights generation for triggered events
            for trigger in triggers:
                AnalyticsOrchestrator._schedule_insights_generation(user_id, trigger)

            return triggers

        except ImportError:
            return []

    @staticmethod
    def _schedule_insights_generation(user_id: int, trigger: str):
        """Schedule AI insights generation (placeholder for Celery task)"""
        logger.info(f"🧠 Scheduling insights generation for user {user_id}, trigger: {trigger}")
        # This would typically call a Celery task
        # generate_ai_insights.delay(user_id, trigger)

    @staticmethod
    def generate_comprehensive_analytics(user_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report for a user.
        Aggregates data from all domains to provide complete picture.
        """
        from apps.preferences.models import UserPreference

        logger.info(f"📈 Generating comprehensive analytics for user {user_id}")

        user_pref = UserPreference.get_by_user_id(user_id)
        if not user_pref:
            return {'error': 'User preferences not found', 'user_id': user_id}

        analytics_report = {
            'user_id': user_id,
            'generated_at': datetime.utcnow().isoformat(),
            'profile_overview': {},
            'engagement_metrics': {},
            'learning_analytics': {},
            'behavioral_insights': {},
            'privacy_compliance': {},
            'recommendations': []
        }

        # Profile overview
        analytics_report['profile_overview'] = {
            'completion_percentage': user_pref.profile_completion_percentage,
            'onboarding_completed': user_pref.onboarding_completed,
            'account_age_days': (datetime.utcnow() - user_pref.created_at).days if user_pref.created_at else 0,
            'last_active': user_pref.last_active.isoformat() if user_pref.last_active else None
        }

        # Engagement metrics from analytics domain
        try:
            engagement_data = AnalyticsOrchestrator._get_engagement_metrics(user_id)
            analytics_report['engagement_metrics'] = engagement_data
        except Exception as e:
            analytics_report['engagement_metrics'] = {'error': str(e)}

        # Learning analytics from content domain
        try:
            learning_data = AnalyticsOrchestrator._get_learning_analytics(user_id)
            analytics_report['learning_analytics'] = learning_data
        except Exception as e:
            analytics_report['learning_analytics'] = {'error': str(e)}

        # Behavioral insights
        try:
            behavioral_data = AnalyticsOrchestrator._get_behavioral_insights(user_id)
            analytics_report['behavioral_insights'] = behavioral_data
        except Exception as e:
            analytics_report['behavioral_insights'] = {'error': str(e)}

        # Privacy compliance status
        try:
            privacy_data = AnalyticsOrchestrator._get_privacy_compliance_status(user_id)
            analytics_report['privacy_compliance'] = privacy_data
        except Exception as e:
            analytics_report['privacy_compliance'] = {'error': str(e)}

        # Generate actionable recommendations
        try:
            recommendations = AnalyticsOrchestrator._generate_recommendations(analytics_report)
            analytics_report['recommendations'] = recommendations
        except Exception as e:
            analytics_report['recommendations'] = [{'error': str(e)}]

        return analytics_report

    @staticmethod
    def _get_engagement_metrics(user_id: int) -> Dict[str, Any]:
        """Get engagement metrics from analytics domain"""
        try:
            from apps.analytics.models import UserAnalytics

            analytics = UserAnalytics.get_by_user_id(user_id)
            if not analytics:
                return {'available': False}

            recent_interactions = analytics.get_recent_interactions(7) if hasattr(analytics, 'get_recent_interactions') else []

            return {
                'total_interactions': analytics.total_interactions,
                'recent_activity_7days': len(recent_interactions),
                'engagement_score': analytics.behavioral_patterns.engagement_score if analytics.behavioral_patterns else 0,
                'learning_velocity': analytics.behavioral_patterns.learning_velocity if analytics.behavioral_patterns else 0,
                'peak_activity_hours': analytics.behavioral_patterns.peak_activity_hours if analytics.behavioral_patterns else []
            }

        except ImportError:
            return {'available': False, 'reason': 'Analytics domain not available'}

    @staticmethod
    def _get_learning_analytics(user_id: int) -> Dict[str, Any]:
        """Get learning analytics from content domain"""
        try:
            from apps.learning_content.models import UserContentProfile

            content_profile = UserContentProfile.get_by_user_id(user_id)
            if not content_profile:
                return {'available': False}

            return {
                'preferred_platforms': content_profile.content_preferences.preferred_platforms if content_profile.content_preferences else [],
                'content_types': content_profile.content_preferences.content_types if content_profile.content_preferences else [],
                'difficulty_preference': content_profile.content_preferences.difficulty_preference if content_profile.content_preferences else None,
                'language_preferences': content_profile.content_preferences.language_preference if content_profile.content_preferences else []
            }

        except ImportError:
            return {'available': False, 'reason': 'Learning content domain not available'}

    @staticmethod
    def _get_behavioral_insights(user_id: int) -> Dict[str, Any]:
        """Get behavioral insights from analytics domain"""
        try:
            from apps.analytics.models import UserAnalytics

            analytics = UserAnalytics.get_by_user_id(user_id)
            if not analytics or not analytics.behavioral_patterns:
                return {'available': False}

            patterns = analytics.behavioral_patterns

            return {
                'engagement_trend': 'increasing' if patterns.engagement_score > 0.6 else 'needs_attention',
                'learning_pace': 'fast' if patterns.learning_velocity > 0.7 else 'moderate' if patterns.learning_velocity > 0.3 else 'slow',
                'preferred_content_types': patterns.preferred_content_types or [],
                'optimal_session_length': patterns.optimal_session_length or 60,
                'dropout_risk': patterns.dropout_risk_score or 0,
                'last_analyzed': patterns.last_analyzed.isoformat() if patterns.last_analyzed else None
            }

        except ImportError:
            return {'available': False, 'reason': 'Analytics domain not available'}

    @staticmethod
    def _get_privacy_compliance_status(user_id: int) -> Dict[str, Any]:
        """Get privacy compliance status from privacy domain"""
        try:
            from apps.privacy_compliance.models import UserPrivacy

            privacy_record = UserPrivacy.get_by_user_id(user_id)
            if not privacy_record:
                return {'available': False}

            return {
                'analytics_consent': privacy_record.privacy_settings.allow_analytics if privacy_record.privacy_settings else False,
                'personalization_consent': privacy_record.privacy_settings.allow_personalization if privacy_record.privacy_settings else False,
                'marketing_consent': privacy_record.privacy_settings.allow_marketing if privacy_record.privacy_settings else False,
                'consent_records_count': len(privacy_record.consent_records) if privacy_record.consent_records else 0,
                'gdpr_compliant': True  # Assume compliant if privacy record exists
            }

        except ImportError:
            return {'available': False, 'reason': 'Privacy compliance domain not available'}

    @staticmethod
    def _generate_recommendations(analytics_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analytics"""
        recommendations = []

        # Profile completion recommendations
        completion = analytics_report['profile_overview'].get('completion_percentage', 0)
        if completion < 70:
            recommendations.append({
                'type': 'profile_completion',
                'priority': 'high',
                'title': 'Complete Your Profile',
                'description': f'Your profile is {completion}% complete. Complete it to get better recommendations.',
                'action': 'Complete profile setup'
            })

        # Engagement recommendations
        engagement_score = analytics_report['engagement_metrics'].get('engagement_score', 0)
        if engagement_score < 0.4:
            recommendations.append({
                'type': 'engagement',
                'priority': 'medium',
                'title': 'Increase Learning Engagement',
                'description': 'Try exploring more interactive content to boost your learning engagement.',
                'action': 'Browse interactive courses'
            })

        # Learning pace recommendations
        learning_velocity = analytics_report['engagement_metrics'].get('learning_velocity', 0)
        if learning_velocity < 0.3:
            recommendations.append({
                'type': 'learning_pace',
                'priority': 'medium',
                'title': 'Set Learning Goals',
                'description': 'Consider setting daily learning goals to maintain consistent progress.',
                'action': 'Set learning schedule'
            })

        # Privacy recommendations
        if not analytics_report['privacy_compliance'].get('analytics_consent', False):
            recommendations.append({
                'type': 'privacy',
                'priority': 'low',
                'title': 'Enable Analytics',
                'description': 'Enable analytics to get personalized learning insights and recommendations.',
                'action': 'Review privacy settings'
            })

        return recommendations