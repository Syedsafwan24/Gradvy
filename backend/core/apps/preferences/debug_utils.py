#
# /backend/core/apps/preferences/debug_utils.py
# Debugging utilities for troubleshooting preferences data flow issues
# Used for diagnosing why onboarding data doesn't appear in preferences page
# RELEVANT FILES: views.py, models.py, serializers.py, frontend preferences pages

"""
Debugging utilities for preferences and onboarding data flow troubleshooting.
Used to diagnose issues where onboarding data doesn't appear in preferences page.
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from .models import UserPreference
from .serializers import UserPreferenceSerializer

logger = logging.getLogger(__name__)


class PreferencesDebugger:
    """Utility class for debugging preferences data flow issues"""

    @staticmethod
    def dump_user_state(user_id: int) -> Dict[str, Any]:
        """
        Comprehensive dump of user's preferences state for debugging.
        Returns detailed information about user's data in the system.
        """
        logger.info(f"🔍 DEBUG DUMP START - User {user_id}")

        debug_data = {
            'user_id': user_id,
            'timestamp': logger.info('📅 Timestamp'),
            'database_state': {},
            'serialization_state': {},
            'validation_state': {},
            'completion_analysis': {},
            'issues_detected': []
        }

        try:
            # 1. Check if user exists in Django
            try:
                django_user = User.objects.get(id=user_id)
                debug_data['django_user'] = {
                    'exists': True,
                    'username': django_user.username,
                    'is_active': django_user.is_active,
                    'date_joined': django_user.date_joined.isoformat()
                }
            except User.DoesNotExist:
                debug_data['django_user'] = {'exists': False}
                debug_data['issues_detected'].append('Django user does not exist')

            # 2. Check MongoDB preferences record
            preference = UserPreference.get_by_user_id(user_id)
            if preference:
                debug_data['database_state'] = {
                    'preferences_exist': True,
                    'created_at': preference.created_at.isoformat(),
                    'updated_at': preference.updated_at.isoformat(),
                    'profile_completion': preference.profile_completion_percentage,
                    'onboarding_status': preference.onboarding_status,
                    'basic_info_exists': bool(preference.basic_info),
                    'content_preferences_exists': bool(preference.content_preferences),
                    'interactions_count': len(preference.behavioral_patterns.interaction_history) if preference.behavioral_patterns else 0
                }

                # Basic info details
                if preference.basic_info:
                    debug_data['database_state']['basic_info_details'] = {
                        'learning_goals': preference.basic_info.learning_goals,
                        'experience_level': preference.basic_info.experience_level,
                        'preferred_pace': preference.basic_info.preferred_pace,
                        'time_availability': preference.basic_info.time_availability,
                        'learning_style': preference.basic_info.learning_style,
                        'career_stage': preference.basic_info.career_stage,
                        'target_timeline': preference.basic_info.target_timeline
                    }
                else:
                    debug_data['issues_detected'].append('Basic info is missing')

                # Content preferences details
                if preference.content_preferences:
                    debug_data['database_state']['content_prefs_details'] = {
                        'preferred_platforms': preference.content_preferences.preferred_platforms,
                        'content_types': preference.content_preferences.content_types,
                        'language_preference': preference.content_preferences.language_preference
                    }
                else:
                    debug_data['issues_detected'].append('Content preferences are missing')

                # 3. Test serialization
                try:
                    serializer = UserPreferenceSerializer(preference)
                    serialized_data = serializer.data
                    debug_data['serialization_state'] = {
                        'serialization_successful': True,
                        'serialized_keys': list(serialized_data.keys()),
                        'basic_info_serialized': bool(serialized_data.get('basic_info')),
                        'content_prefs_serialized': bool(serialized_data.get('content_preferences')),
                        'completion_serialized': serialized_data.get('profile_completion_percentage')
                    }

                    # Check for data loss in serialization
                    if preference.basic_info and not serialized_data.get('basic_info'):
                        debug_data['issues_detected'].append('Basic info exists in DB but not in serialized data')

                    if preference.content_preferences and not serialized_data.get('content_preferences'):
                        debug_data['issues_detected'].append('Content preferences exist in DB but not in serialized data')

                except Exception as e:
                    debug_data['serialization_state'] = {
                        'serialization_successful': False,
                        'error': str(e)
                    }
                    debug_data['issues_detected'].append(f'Serialization failed: {str(e)}')

                # 4. Completion percentage analysis
                expected_completion = preference.calculate_profile_completion()
                debug_data['completion_analysis'] = {
                    'stored_completion': preference.profile_completion_percentage,
                    'calculated_completion': expected_completion,
                    'completion_mismatch': abs(preference.profile_completion_percentage - expected_completion) > 1.0
                }

                if debug_data['completion_analysis']['completion_mismatch']:
                    debug_data['issues_detected'].append('Profile completion percentage mismatch')

            else:
                debug_data['database_state'] = {'preferences_exist': False}
                debug_data['issues_detected'].append('No preferences record found in MongoDB')

            # 5. Overall health assessment
            debug_data['health_assessment'] = {
                'has_critical_issues': len([issue for issue in debug_data['issues_detected']
                                          if any(keyword in issue.lower() for keyword in ['missing', 'failed', 'does not exist'])]) > 0,
                'data_completeness_score': _calculate_completeness_score(debug_data),
                'ready_for_preferences_page': _is_ready_for_preferences(debug_data)
            }

            logger.info(f"✅ DEBUG DUMP COMPLETE - User {user_id}, Issues: {len(debug_data['issues_detected'])}")

        except Exception as e:
            debug_data['dump_error'] = {
                'error': str(e),
                'error_type': type(e).__name__
            }
            debug_data['issues_detected'].append(f'Debug dump failed: {str(e)}')
            logger.error(f"❌ DEBUG DUMP FAILED - User {user_id}: {str(e)}")

        return debug_data

    @staticmethod
    def verify_onboarding_to_preferences_flow(user_id: int) -> Dict[str, Any]:
        """
        Specifically verify the data flow from onboarding completion to preferences display.
        """
        logger.info(f"🔄 FLOW VERIFICATION START - User {user_id}")

        verification = {
            'user_id': user_id,
            'flow_steps': {},
            'bottlenecks_detected': [],
            'recommendations': []
        }

        # Step 1: Check if onboarding was completed
        preference = UserPreference.get_by_user_id(user_id)
        if preference:
            verification['flow_steps']['onboarding_completed'] = {
                'status': preference.onboarding_status,
                'completion_percentage': preference.profile_completion_percentage,
                'has_basic_info': bool(preference.basic_info),
                'has_content_prefs': bool(preference.content_preferences)
            }

            # Step 2: Check data availability
            if not preference.basic_info:
                verification['bottlenecks_detected'].append('Basic info missing after onboarding')
                verification['recommendations'].append('Re-run onboarding to populate basic info')

            if not preference.content_preferences:
                verification['bottlenecks_detected'].append('Content preferences missing after onboarding')
                verification['recommendations'].append('Check onboarding serializer data mapping')

            # Step 3: Check serialization integrity
            try:
                serializer = UserPreferenceSerializer(preference)
                serialized = serializer.data
                verification['flow_steps']['serialization_check'] = {
                    'successful': True,
                    'basic_info_present': bool(serialized.get('basic_info')),
                    'content_prefs_present': bool(serialized.get('content_preferences'))
                }
            except Exception as e:
                verification['flow_steps']['serialization_check'] = {
                    'successful': False,
                    'error': str(e)
                }
                verification['bottlenecks_detected'].append(f'Serialization error: {str(e)}')

        else:
            verification['flow_steps']['onboarding_completed'] = {'status': 'no_preferences_record'}
            verification['bottlenecks_detected'].append('No preferences record found')
            verification['recommendations'].append('User needs to complete onboarding')

        verification['flow_healthy'] = len(verification['bottlenecks_detected']) == 0

        logger.info(f"✅ FLOW VERIFICATION COMPLETE - User {user_id}, Healthy: {verification['flow_healthy']}")
        return verification


def _calculate_completeness_score(debug_data: Dict[str, Any]) -> float:
    """Calculate a completeness score based on available data"""
    score = 0.0
    max_score = 100.0

    # Django user exists (10 points)
    if debug_data.get('django_user', {}).get('exists'):
        score += 10

    # MongoDB record exists (20 points)
    if debug_data.get('database_state', {}).get('preferences_exist'):
        score += 20

    # Basic info exists (30 points)
    if debug_data.get('database_state', {}).get('basic_info_exists'):
        score += 30

    # Content preferences exist (20 points)
    if debug_data.get('database_state', {}).get('content_preferences_exists'):
        score += 20

    # Serialization works (20 points)
    if debug_data.get('serialization_state', {}).get('serialization_successful'):
        score += 20

    return score


def _is_ready_for_preferences(debug_data: Dict[str, Any]) -> bool:
    """Determine if user data is ready to be displayed on preferences page"""
    required_conditions = [
        debug_data.get('django_user', {}).get('exists', False),
        debug_data.get('database_state', {}).get('preferences_exist', False),
        debug_data.get('serialization_state', {}).get('serialization_successful', False),
        len(debug_data.get('issues_detected', [])) == 0
    ]

    return all(required_conditions)