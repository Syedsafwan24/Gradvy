"""
API views for user preferences and personalization.
Handles CRUD operations for MongoDB-stored user data.
"""
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
import logging

from .models import (
    UserPreference, LearningSession, CourseRecommendation,
    AITrainingData, RecommendationItem
)
from .serializers import (
    UserPreferenceSerializer, OnboardingSerializer,
    InteractionLogSerializer, CourseRecommendationSerializer,
    UserAnalyticsSerializer
)
from django.conf import settings
from django.http import JsonResponse
from django.utils.timezone import now

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class UserPreferenceView(views.APIView):
    """
    Main endpoint for user preferences CRUD operations.
    GET: Retrieve user preferences
    POST: Create initial preferences (onboarding)
    PUT/PATCH: Update existing preferences
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user's preferences"""
        try:
            preference = UserPreference.get_by_user_id(request.user.id)
            
            if not preference:
                return Response({
                    'message': 'No preferences found. Please complete onboarding.',
                    'onboarding_required': True
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = UserPreferenceSerializer(preference)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error retrieving preferences for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to retrieve preferences'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create initial preferences (usually from onboarding)"""
        try:
            # Check if user already has preferences
            existing = UserPreference.get_by_user_id(request.user.id)
            if existing:
                return Response({
                    'error': 'User preferences already exist. Use PUT to update.',
                    'existing_data': UserPreferenceSerializer(existing).data
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserPreferenceSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                preference = serializer.save()
                
                # Log preference creation
                logger.info(f"Created preferences for user {request.user.id}")
                
                return Response(
                    UserPreferenceSerializer(preference).data,
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating preferences for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to create preferences'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update user preferences (full update)"""
        return self._update_preferences(request, partial=False)
    
    def patch(self, request):
        """Partially update user preferences"""
        return self._update_preferences(request, partial=True)
    
    def _update_preferences(self, request, partial=False):
        """Common logic for PUT/PATCH operations"""
        try:
            preference = UserPreference.get_by_user_id(request.user.id)
            
            if not preference:
                return Response({
                    'error': 'No preferences found. Use POST to create initial preferences.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = UserPreferenceSerializer(
                preference,
                data=request.data,
                partial=partial,
                context={'request': request}
            )
            
            if serializer.is_valid():
                updated_preference = serializer.save()
                
                # Log preference update
                logger.info(f"Updated preferences for user {request.user.id}")
                
                return Response(UserPreferenceSerializer(updated_preference).data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to update preferences'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class OnboardingView(views.APIView):
    """
    Dedicated endpoint for user onboarding flow.
    Handles the complete onboarding data collection and preference creation.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Complete onboarding and create user preferences"""
        try:
            # Check if user already completed onboarding
            existing = UserPreference.get_by_user_id(request.user.id)
            if existing:
                return Response({
                    'message': 'Onboarding already completed',
                    'preferences': UserPreferenceSerializer(existing).data
                }, status=status.HTTP_200_OK)
            
            serializer = OnboardingSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                preference = serializer.save()
                
                logger.info(f"Completed onboarding for user {request.user.id}")
                
                return Response({
                    'message': 'Onboarding completed successfully',
                    'preferences': UserPreferenceSerializer(preference).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'message': 'Onboarding data validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error during onboarding for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to complete onboarding'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class QuickOnboardingView(views.APIView):
    """
    Dedicated endpoint for quick onboarding flow.
    Handles minimal essential preference collection immediately after registration.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Complete quick onboarding and create/update user preferences"""
        try:
            # Get or create user preference
            preference = UserPreference.get_by_user_id(request.user.id)
            
            if not preference:
                # Create new preference record
                preference = UserPreference(user_id=request.user.id)
            
            # Extract quick onboarding data from request
            quick_onboarding_data = request.data.get('quick_onboarding_data', {})
            basic_info_data = request.data.get('basic_info', {})
            
            # Update quick onboarding fields
            preference.quick_onboarding_completed = True
            preference.quick_onboarding_data = quick_onboarding_data
            
            # Create or update basic info with quick onboarding data
            from .models import BasicInfo
            if not preference.basic_info:
                preference.basic_info = BasicInfo()
            
            # Update basic info fields with provided data
            if basic_info_data.get('learning_goals'):
                preference.basic_info.learning_goals = basic_info_data['learning_goals']
            if basic_info_data.get('experience_level'):
                preference.basic_info.experience_level = basic_info_data['experience_level']
            if basic_info_data.get('time_availability'):
                preference.basic_info.time_availability = basic_info_data['time_availability']
            if basic_info_data.get('learning_style'):
                preference.basic_info.learning_style = basic_info_data['learning_style']
            if basic_info_data.get('preferred_pace'):
                preference.basic_info.preferred_pace = basic_info_data['preferred_pace']
            
            # Update profile completion percentage
            preference.update_completion_percentage()
            
            # Save the preference
            preference.save()
            
            # Log interaction using a valid interaction type
            preference.add_interaction(
                'page_view',
                {
                    'completion_time': datetime.utcnow().isoformat(),
                    'preferences_set': len([k for k, v in quick_onboarding_data.items() if v]),
                    'profile_completion': preference.profile_completion_percentage,
                    'page': 'quick_onboarding_completion'
                },
                {
                    'source': 'quick_onboarding_flow',
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
            
            logger.info(f"Completed quick onboarding for user {request.user.id}")
            
            return Response({
                'message': 'Quick onboarding completed successfully',
                'profile_completion_percentage': preference.profile_completion_percentage,
                'quick_onboarding_completed': preference.quick_onboarding_completed,
                'onboarding_completed': preference.onboarding_completed,
                'user_id': preference.user_id,
                'basic_info': {
                    'learning_goals': preference.basic_info.learning_goals if preference.basic_info else [],
                    'experience_level': preference.basic_info.experience_level if preference.basic_info else '',
                    'time_availability': preference.basic_info.time_availability if preference.basic_info else '',
                    'learning_style': preference.basic_info.learning_style if preference.basic_info else [],
                    'preferred_pace': preference.basic_info.preferred_pace if preference.basic_info else ''
                },
                'quick_onboarding_data': preference.quick_onboarding_data,
                'created_at': preference.created_at.isoformat() if preference.created_at else None,
                'updated_at': preference.updated_at.isoformat() if preference.updated_at else None
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error during quick onboarding for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to complete quick onboarding',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class InteractionLogView(views.APIView):
    """
    Endpoint for logging user interactions.
    Used to track user behavior for personalization.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Log a user interaction"""
        try:
            serializer = InteractionLogSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                result = serializer.save()
                return Response(result, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error logging interaction for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to log interaction'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class UserAnalyticsView(views.APIView):
    """
    Endpoint for user analytics and learning insights.
    Provides analytics data based on user interactions and preferences.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user analytics and learning insights"""
        try:
            preference = UserPreference.get_by_user_id(request.user.id)
            
            serializer = UserAnalyticsSerializer(preference)
            
            return Response({
                'analytics': serializer.data,
                'generated_at': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error generating analytics for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to generate analytics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class PersonalizedRecommendationsView(views.APIView):
    """
    Endpoint for personalized course recommendations.
    Returns cached recommendations or generates new ones.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get personalized course recommendations"""
        try:
            # Check for valid cached recommendations
            recommendations = CourseRecommendation.get_valid_recommendations(request.user.id)
            
            if recommendations:
                serializer = CourseRecommendationSerializer(recommendations)
                return Response({
                    'recommendations': serializer.data,
                    'source': 'cached'
                })
            
            # No valid recommendations found
            return Response({
                'message': 'No recommendations available. Recommendations will be generated based on your preferences.',
                'recommendations': {
                    'user_id': request.user.id,
                    'recommendations': [],
                    'generated_at': None,
                    'expires_at': None
                },
                'source': 'none'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving recommendations for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to retrieve recommendations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Force regeneration of recommendations (for testing)"""
        try:
            # This would typically be called by an AI service
            # For now, we'll create a placeholder
            
            user_preference = UserPreference.get_by_user_id(request.user.id)
            if not user_preference:
                return Response({
                    'error': 'User preferences not found. Complete onboarding first.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Create mock recommendations for testing
            mock_recommendations = [
                RecommendationItem(
                    course_id="test_course_1",
                    platform="udemy",
                    title="Mock Course 1",
                    score=0.95,
                    reasoning=["matches_learning_goal", "appropriate_difficulty"],
                    metadata={"duration": "10 hours", "rating": 4.5}
                ),
                RecommendationItem(
                    course_id="test_course_2",
                    platform="coursera",
                    title="Mock Course 2", 
                    score=0.87,
                    reasoning=["popular_choice", "high_rating"],
                    metadata={"duration": "6 hours", "rating": 4.7}
                )
            ]
            
            # Create recommendation document
            recommendation = CourseRecommendation(
                user_id=request.user.id,
                expires_at=datetime.utcnow() + timedelta(hours=24),
                recommendations=mock_recommendations,
                algorithm_version="1.0.0-mock"
            )
            recommendation.save()
            
            serializer = CourseRecommendationSerializer(recommendation)
            return Response({
                'message': 'Recommendations generated successfully',
                'recommendations': serializer.data,
                'source': 'generated'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {request.user.id}: {str(e)}")
            return Response({
                'error': 'Failed to generate recommendations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class PreferenceChoicesView(views.APIView):
    """
    Endpoint to get available choices for preference fields.
    Useful for frontend form generation.
    """
    permission_classes = [permissions.AllowAny]  # Public endpoint
    
    def get(self, request):
        """Get all available choices for preference fields"""
        from .models import BasicInfo, ContentPreferences, InteractionData
        
        choices = {
            'learning_goals': [
                'web_dev', 'mobile_dev', 'ai_ml', 'data_science', 'devops',
                'design', 'business', 'marketing', 'finance', 'languages'
            ],
            'experience_levels': BasicInfo.EXPERIENCE_CHOICES,
            'pace_options': BasicInfo.PACE_CHOICES,
            'time_availability': BasicInfo.TIME_CHOICES,
            'learning_styles': BasicInfo.STYLE_CHOICES,
            'career_stages': BasicInfo.CAREER_CHOICES,
            'timelines': BasicInfo.TIMELINE_CHOICES,
            'platforms': ContentPreferences.PLATFORM_CHOICES,
            'content_types': ContentPreferences.CONTENT_TYPES,
            'difficulty_levels': ContentPreferences.DIFFICULTY_CHOICES,
            'duration_preferences': ContentPreferences.DURATION_CHOICES,
            'interaction_types': InteractionData.INTERACTION_TYPES
        }
        
        return Response(choices)


# =============================================================================
# PRIVACY & CONSENT API ENDPOINTS (alignment with frontend component)
# =============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class PrivacyConsentSummaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Return privacy summary and consent records for the current user"""
        pref = UserPreference.get_by_user_id(request.user.id)
        if not pref:
            pref = UserPreference.create_for_user(request.user.id)

        privacy = pref.privacy_settings
        records = []
        for rec in (pref.consent_history or []):
            records.append({
                'id': getattr(rec, 'record_id', None) or rec.consent_type or (rec.consent_types[0] if rec.consent_types else None),
                'consent_type': rec.consent_type,
                'consent_types': rec.consent_types,
                'granted': rec.granted,
                'granted_at': rec.granted_at.isoformat() if rec.granted_at else None,
                'updated_at': rec.updated_at.isoformat() if rec.updated_at else None,
                'expires_at': rec.expires_at.isoformat() if rec.expires_at else None,
                'consent_version': rec.consent_version,
            })

        summary = pref.get_privacy_summary()
        return Response({
            'privacy_summary': summary,
            'consent_records': records,
        })


@method_decorator(csrf_exempt, name='dispatch')
class PrivacyConsentUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, consent_id):
        """Update a specific consent (by record_id or consent_type)"""
        granted = request.data.get('granted', None)
        if granted is None:
            return Response({'error': 'granted is required'}, status=status.HTTP_400_BAD_REQUEST)

        pref = UserPreference.get_by_user_id(request.user.id)
        if not pref:
            return Response({'error': 'User preferences not found'}, status=status.HTTP_404_NOT_FOUND)

        # Resolve consent type
        ctype = None
        # Match by record_id
        for rec in (pref.consent_history or []):
            if getattr(rec, 'record_id', None) == consent_id:
                ctype = rec.consent_type or (rec.consent_types[0] if rec.consent_types else None)
                break
        # Fallback to treating consent_id as type
        if not ctype:
            ctype = consent_id

        pref.record_consent_change(
            consent_type=ctype,
            granted=bool(granted),
            ip_address=request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Return updated record snapshot
        latest = None
        for rec in reversed(pref.consent_history):
            rtype = rec.consent_type or (rec.consent_types[0] if rec.consent_types else None)
            if rtype == ctype:
                latest = rec
                break

        return Response({
            'consent': {
                'id': getattr(latest, 'record_id', None),
                'consent_type': latest.consent_type,
                'consent_types': latest.consent_types,
                'granted': latest.granted,
                'granted_at': latest.granted_at.isoformat() if latest.granted_at else None,
                'updated_at': latest.updated_at.isoformat() if latest.updated_at else None,
            },
            'privacy_data': pref.get_privacy_summary()
        })


@method_decorator(csrf_exempt, name='dispatch')
class RevokeAllConsentsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        pref = UserPreference.get_by_user_id(request.user.id)
        if not pref:
            return Response({'error': 'User preferences not found'}, status=status.HTTP_404_NOT_FOUND)

        # Revoke all non-essential consents
        revoke_types = [
            'analytics', 'personalization', 'marketing', 'social_data',
            'behavioral_analysis', 'third_party_sharing', 'location_data', 'device_fingerprinting'
        ]
        for t in revoke_types:
            pref.record_consent_change(
                consent_type=t,
                granted=False,
                ip_address=request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        return Response({
            'status': 'success',
            'privacy_data': pref.get_privacy_summary(),
            'consent_records': [
                {
                    'id': rec.record_id,
                    'consent_type': rec.consent_type,
                    'consent_types': rec.consent_types,
                    'granted': rec.granted,
                    'updated_at': rec.updated_at.isoformat() if rec.updated_at else None,
                } for rec in pref.consent_history
            ]
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def consent_history_download(request):
    """Download consent history as JSON attachment"""
    pref = UserPreference.get_by_user_id(request.user.id)
    if not pref:
        return Response({'error': 'User preferences not found'}, status=404)

    payload = [
        {
            'id': rec.record_id,
            'consent_type': rec.consent_type,
            'consent_types': rec.consent_types,
            'granted': rec.granted,
            'granted_at': rec.granted_at.isoformat() if rec.granted_at else None,
            'updated_at': rec.updated_at.isoformat() if rec.updated_at else None,
            'consent_version': rec.consent_version,
        }
        for rec in pref.consent_history
    ]
    response = JsonResponse(payload, safe=False)
    response['Content-Disposition'] = 'attachment; filename="consent-history.json"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def privacy_versions(request):
    privacy_version = getattr(settings, 'PRIVACY_POLICY_VERSION', '1.0')
    terms_version = getattr(settings, 'TERMS_VERSION', '1.0')
    cookie_version = getattr(settings, 'COOKIE_POLICY_VERSION', '1.0')
    return Response({
        'privacy_policy_version': privacy_version,
        'terms_version': terms_version,
        'cookie_policy_version': cookie_version,
        'last_updated': now().isoformat()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def privacy_accept(request):
    policy = request.data.get('policy')  # 'privacy' | 'terms' | 'cookie'
    version = request.data.get('version')
    if not policy or not version:
        return Response({'error': 'policy and version are required'}, status=400)

    pref = UserPreference.get_by_user_id(request.user.id)
    if not pref:
        pref = UserPreference.create_for_user(request.user.id)

    if not pref.privacy_settings:
        from .models import PrivacySettings
        pref.privacy_settings = PrivacySettings()

    if policy == 'privacy':
        pref.privacy_settings.privacy_policy_version = version
        pref.privacy_settings.gdpr_consent_date = datetime.utcnow()
    elif policy == 'terms':
        pref.privacy_settings.terms_accepted_version = version
    elif policy == 'cookie':
        # Track via consent record for transparency
        pref.record_consent_change('analytics', True)
    else:
        return Response({'error': 'invalid policy'}, status=400)

    pref.privacy_settings.last_updated = datetime.utcnow()
    pref.save()

    return Response({'status': 'accepted', 'privacy_settings': pref.get_privacy_summary()})


@method_decorator(csrf_exempt, name='dispatch')
class AnalyticsEventAPIView(views.APIView):
    """
    API endpoint for receiving and processing frontend analytics events.
    Handles batch event processing with privacy compliance.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Process batch of analytics events from frontend"""
        try:
            data = request.data
            events = data.get('events', [])
            
            if not events:
                return Response({'error': 'No events provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create user preference record
            user_preference, created = self._get_or_create_user_preference(request.user)
            
            # Process events with privacy compliance
            processed_events = []
            for event in events:
                processed_event = self._process_analytics_event(event, user_preference, request)
                if processed_event:
                    processed_events.append(processed_event)
            
            # Update behavioral patterns if consent given
            if (user_preference.privacy_settings and 
                user_preference.privacy_settings.allow_behavioral_analysis):
                self._update_behavioral_patterns(user_preference, processed_events)
            
            # Trigger AI insights update if significant activity
            if len(processed_events) >= 10:  # Threshold for insights update
                # Schedule AI insights update task
                logger.info(f"Scheduling AI insights update for user {request.user.id}")
            
            logger.info(f"Processed {len(processed_events)} events for user {request.user.id}")
            
            return Response({
                'processed_events': len(processed_events),
                'total_events': len(events),
                'privacy_level': self._get_privacy_level(user_preference),
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Failed to process analytics events: {str(e)}")
            return Response(
                {'error': 'Failed to process events', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_or_create_user_preference(self, user):
        """Get or create user preference record"""
        user_preference = UserPreference.get_by_user_id(user.id)
        
        if not user_preference:
            user_preference = UserPreference.create_for_user(user.id)
            
            # Set default privacy settings for new users
        from .models import PrivacySettings
        user_preference.privacy_settings = PrivacySettings(
            allow_analytics=False,
            allow_personalization=False,
        )
        user_preference.save()
        
        return user_preference, user_preference.created_at == user_preference.updated_at
    
    def _process_analytics_event(self, event, user_preference, request):
        """Process individual analytics event with privacy checks"""
        
        event_type = event.get('event_type')
        if not event_type:
            return None
        
        # Check privacy consent for event type
        if not self._has_consent_for_event(event_type, user_preference):
            # Store minimal event without detailed data
            return self._create_minimal_event(event_type, user_preference)
        
        # Extract and sanitize event data
        processed_event = {
            'event_id': event.get('event_id'),
            'event_type': event_type,
            'timestamp': self._parse_timestamp(event.get('timestamp')),
            'session_id': event.get('session_id'),
            'properties': self._sanitize_properties(event.get('properties', {})),
            'context': self._extract_context(event, request),
            'privacy_level': self._get_privacy_level(user_preference),
        }
        
        # Add event to user interactions using existing method
        user_preference.add_interaction(
            interaction_type=event_type,
            data=processed_event['properties'],
            context=processed_event['context']
        )
        
        # Log for AI training if consent given
        if (user_preference.privacy_settings and 
            user_preference.privacy_settings.allow_personalization):
            AITrainingData.log_event(
                user_id=request.user.id,
                event_type=event_type,
                event_data=processed_event['properties'],
                user_context=processed_event['context']
            )
        
        return processed_event
    
    def _has_consent_for_event(self, event_type, user_preference):
        """Check if user has given consent for this event type"""
        if not user_preference.privacy_settings:
            return False  # No consent given

        # Essential events are always allowed
        essential_events = ['session_start', 'session_end', 'error_event', 'form_submit']
        if event_type in essential_events:
            return True

        # Map event types to required consent
        consent_mapping = {
            'page_view': 'allow_analytics',
            'route_change': 'allow_analytics',
            'button_click': 'allow_analytics',
            'link_click': 'allow_analytics',
            'input_focus': 'allow_behavioral_analysis',
            'input_blur': 'allow_behavioral_analysis',
            'card_view': 'allow_analytics',
            'card_click': 'allow_analytics',
            'course_interaction': 'allow_personalization',
            'learning_activity': 'allow_personalization',
            'learning_session': 'allow_personalization',
            'quiz_attempt': 'allow_personalization',
            'search': 'allow_analytics',
            'video_play': 'allow_personalization',
            'video_pause': 'allow_personalization',
            'video_complete': 'allow_personalization',
            'user_engagement': 'allow_behavioral_analysis',
            'personalization_event': 'allow_personalization',
            'goal_progress': 'allow_personalization',
            'performance_metric': 'allow_analytics',
        }

        required_consent = consent_mapping.get(event_type, 'allow_analytics')
        return getattr(user_preference.privacy_settings, required_consent, False)
    
    def _create_minimal_event(self, event_type, user_preference):
        """Create minimal event record for privacy compliance"""
        minimal_event = {
            'event_type': event_type,
            'timestamp': datetime.utcnow(),
            'privacy_limited': True,
            'user_id': user_preference.user_id,
        }
        
        # Add minimal interaction
        user_preference.add_interaction(
            interaction_type=event_type,
            data={'privacy_limited': True, 'timestamp': datetime.utcnow().isoformat()},
            context={'consent_limited': True}
        )
        
        return minimal_event
    
    def _sanitize_properties(self, properties):
        """Sanitize event properties to remove sensitive data"""
        sanitized = {}
        
        sensitive_keys = ['password', 'token', 'secret', 'key', 'credential']
        
        for key, value in properties.items():
            # Remove sensitive keys
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                sanitized[key] = '[REDACTED]'
                continue
            
            # Limit string length
            if isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + '...'
                continue
            
            # Recursively sanitize nested objects
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_properties(value)
                continue
            
            sanitized[key] = value
        
        return sanitized
    
    def _extract_context(self, event, request):
        """Extract context information from event and request"""
        context = {
            'page_url': event.get('page_url'),
            'referrer': event.get('referrer'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'ip_address': self._get_client_ip(request),
            'session_id': event.get('session_id'),
            'device_fingerprint': event.get('device_fingerprint'),
            'viewport': event.get('viewport'),
            'timestamp': event.get('timestamp'),
        }
        
        # Add device info if available
        if 'device_info' in event:
            context['device_info'] = event['device_info']
        
        return context
    
    def _get_client_ip(self, request):
        """Get client IP address with proxy support"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _parse_timestamp(self, timestamp_str):
        """Parse ISO timestamp string"""
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return datetime.utcnow()
    
    def _get_privacy_level(self, user_preference):
        """Get user's privacy level"""
        if not user_preference.privacy_settings:
            return 'unknown'

        privacy = user_preference.privacy_settings
        if privacy.allow_behavioral_analysis and privacy.allow_personalization:
            return 'full'
        elif privacy.allow_analytics:
            return 'analytics'
        else:
            return 'minimal'
    
    def _update_behavioral_patterns(self, user_preference, events):
        """Update behavioral patterns based on processed events"""
        if not user_preference.behavioral_patterns:
            from .models import BehavioralPatterns
            user_preference.behavioral_patterns = BehavioralPatterns()
        
        # Calculate engagement metrics from events
        engagement_events = [e for e in events if e['event_type'] in [
            'course_interaction', 'learning_activity', 'video_play', 'quiz_attempt'
        ]]
        
        if engagement_events:
            # Update engagement score
            current_score = user_preference.behavioral_patterns.engagement_score or 0.0
            new_score = min(len(engagement_events) / 10.0, 1.0)  # Normalize to 0-1
            
            # Exponential moving average
            alpha = 0.2
            user_preference.behavioral_patterns.engagement_score = (
                alpha * new_score + (1 - alpha) * current_score
            )
            
            # Update activity times
            current_hour = datetime.utcnow().hour
            if current_hour not in user_preference.behavioral_patterns.peak_activity_hours:
                user_preference.behavioral_patterns.peak_activity_hours.append(current_hour)
            
            # Update last analysis time
            user_preference.behavioral_patterns.last_analyzed = datetime.utcnow()
            user_preference.save()


@method_decorator(csrf_exempt, name='dispatch')
class PrivacyConsentAPIView(views.APIView):
    """
    API endpoint for managing user privacy consent.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Record user privacy consent"""
        try:
            consent_types = request.data.get('consent_types', [])
            
            if not consent_types:
                return Response({'error': 'No consent types provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user preference
            user_preference = UserPreference.get_by_user_id(request.user.id)
            if not user_preference:
                user_preference = UserPreference.create_for_user(request.user.id)
            
            # Record consent
            user_preference.record_consent(
                consent_types=consent_types,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response({
                'status': 'success',
                'privacy_settings': user_preference.get_privacy_summary(),
                'consent_recorded': consent_types,
            })
            
        except Exception as e:
            logger.error(f"Failed to record privacy consent: {str(e)}")
            return Response(
                {'error': 'Failed to record consent', 'details': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get current privacy settings"""
        try:
            user_preference = UserPreference.get_by_user_id(request.user.id)
            
            if not user_preference:
                return Response({
                    'privacy_configured': False,
                    'available_consent_types': [
                        'essential', 'analytics', 'personalization', 'marketing',
                        'social_integration', 'behavioral_analysis', 'external_enrichment'
                    ]
                })
            
            return Response(user_preference.get_privacy_summary())
            
        except Exception as e:
            logger.error(f"Failed to get privacy settings: {str(e)}")
            return Response(
                {'error': 'Failed to get privacy settings'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class EnhancedUserAnalyticsView(views.APIView):
    """
    Enhanced API endpoint for comprehensive user analytics dashboard data.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive user analytics and insights"""
        try:
            user_preference = UserPreference.get_by_user_id(request.user.id)
            
            if not user_preference:
                return Response({'error': 'User preferences not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get analytics data
            analytics_data = {
                'profile_completion': user_preference.profile_completion_percentage,
                'total_interactions': len(user_preference.interactions),
                'recent_activity': self._get_recent_activity_summary(user_preference),
                'learning_insights': self._get_learning_insights(user_preference),
                'engagement_metrics': self._get_engagement_metrics(user_preference),
                'privacy_summary': user_preference.get_privacy_summary(),
                'device_patterns': self._get_device_patterns(user_preference),
                'location_insights': self._get_location_insights(user_preference),
            }
            
            # Add AI insights if available and consent given
            if (user_preference.ai_insights and 
                user_preference.privacy_settings and 
                user_preference.privacy_settings.allow_personalization):
                analytics_data['ai_insights'] = {
                    'learning_patterns': user_preference.ai_insights.learning_patterns,
                    'strength_areas': user_preference.ai_insights.strength_areas,
                    'improvement_areas': user_preference.ai_insights.improvement_areas,
                    'career_fit_score': user_preference.ai_insights.career_fit_score,
                    'last_updated': user_preference.ai_insights.updated_at,
                }
            
            return Response(analytics_data)
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {str(e)}")
            return Response(
                {'error': 'Failed to get analytics data'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_recent_activity_summary(self, user_preference):
        """Get summary of recent user activity"""
        recent_interactions = user_preference.get_recent_interactions(days=7)
        
        activity_types = {}
        for interaction in recent_interactions:
            activity_type = interaction.type
            if activity_type not in activity_types:
                activity_types[activity_type] = 0
            activity_types[activity_type] += 1
        
        return {
            'total_interactions_7days': len(recent_interactions),
            'activity_breakdown': activity_types,
            'most_active_day': self._get_most_active_day(recent_interactions),
            'last_activity': recent_interactions[0].timestamp if recent_interactions else None,
        }
    
    def _get_learning_insights(self, user_preference):
        """Get learning-specific insights"""
        learning_interactions = [
            interaction for interaction in user_preference.get_recent_interactions(days=30)
            if interaction.type in ['course_interaction', 'learning_activity', 'quiz_attempt', 'video_play']
        ]
        
        insights = {
            'total_learning_sessions': len(learning_interactions),
            'courses_viewed': len(set([
                interaction.data.get('course_id') for interaction in learning_interactions 
                if interaction.data.get('course_id')
            ])),
            'average_session_length': 0,
            'completion_rate': 0,
        }
        
        # Calculate more detailed insights if we have enough data
        if learning_interactions:
            insights['learning_streak'] = self._calculate_learning_streak(learning_interactions)
            insights['preferred_content_types'] = self._get_preferred_content_types(learning_interactions)
        
        return insights
    
    def _get_engagement_metrics(self, user_preference):
        """Get user engagement metrics"""
        if not user_preference.behavioral_patterns:
            return {'engagement_score': 0, 'no_data': True}
        
        patterns = user_preference.behavioral_patterns
        return {
            'engagement_score': patterns.engagement_score or 0,
            'learning_velocity': patterns.learning_velocity or 0,
            'average_session_length': patterns.optimal_session_length or 0,
            'peak_activity_hours': patterns.peak_activity_hours or [],
            'course_completion_rate': patterns.course_completion_rate or 0,
            'last_analyzed': patterns.last_analyzed,
        }
    
    def _get_device_patterns(self, user_preference):
        """Get device usage patterns"""
        if not user_preference.device_patterns:
            return {'no_data': True}
        
        devices = []
        for pattern in user_preference.device_patterns:
            devices.append({
                'device_type': pattern.device_type,
                'operating_system': pattern.operating_system,
                'browser': pattern.browser,
                'usage_frequency': pattern.usage_frequency,
                'last_seen': pattern.last_seen,
            })
        
        return {
            'devices': devices,
            'total_devices': len(devices),
            'primary_device': devices[0] if devices else None,
        }
    
    def _get_location_insights(self, user_preference):
        """Get location-based insights"""
        if not user_preference.location_history:
            return {'no_data': True}
        
        locations = []
        for location in user_preference.location_history:
            locations.append({
                'country': location.country,
                'city': location.city,
                'session_count': location.session_count,
                'last_detected': location.last_detected,
            })
        
        return {
            'locations': locations,
            'primary_location': locations[0] if locations else None,
            'countries_count': len(set([loc.country for loc in user_preference.location_history])),
        }
    
    def _get_most_active_day(self, interactions):
        """Get the most active day from interactions"""
        if not interactions:
            return None
        
        day_counts = {}
        for interaction in interactions:
            day = interaction.timestamp.strftime('%A')
            day_counts[day] = day_counts.get(day, 0) + 1
        
        return max(day_counts, key=day_counts.get) if day_counts else None
    
    def _calculate_learning_streak(self, interactions):
        """Calculate current learning streak"""
        if not interactions:
            return 0
        
        dates = set([interaction.timestamp.date() for interaction in interactions])
        if not dates:
            return 0
        
        sorted_dates = sorted(dates, reverse=True)
        streak = 0
        expected_date = sorted_dates[0]
        
        for date in sorted_dates:
            if date == expected_date:
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            else:
                break
        
        return streak
    
    def _get_preferred_content_types(self, interactions):
        """Get preferred content types from interactions"""
        content_types = {}
        for interaction in interactions:
            content_type = interaction.data.get('content_type') or interaction.data.get('activity_type')
            if content_type:
                content_types[content_type] = content_types.get(content_type, 0) + 1
        
        return sorted(content_types.keys(), key=lambda x: content_types[x], reverse=True)[:3]

# =============================================================================
# PRIVACY CONTROL API ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def privacy_overview(request):
    """
    Get comprehensive privacy overview for user
    """
    try:
        user_pref = UserPreference.get_by_user_id(request.user.id)
        if not user_pref:
            return Response({'error': 'User preferences not found'}, status=404)
        
        # Calculate privacy score
        privacy_score = calculate_privacy_score(user_pref)
        
        # Get consent status
        privacy = user_pref.privacy_settings
        consent_status = {
            'allow_analytics': getattr(privacy, 'allow_analytics', False),
            'allow_behavioral_analysis': getattr(privacy, 'allow_behavioral_analysis', False),
            'allow_personalization': getattr(privacy, 'allow_personalization', False),
            'allow_marketing': getattr(privacy, 'allow_marketing', False),
        }
        
        # Data collection summary
        data_collection = {
            'profile_data_points': len(user_pref.preferences_data.keys()) if user_pref.preferences_data else 0,
            'learning_interactions': user_pref.analytics_data.get('total_interactions', 0) if user_pref.analytics_data else 0,
            'social_connections': len(user_pref.social_data) if user_pref.social_data else 0,
            'analytics_events': user_pref.analytics_data.get('total_events', 0) if user_pref.analytics_data else 0,
        }
        
        # Recent privacy activity
        recent_activity = get_recent_privacy_activity(user_pref)
        
        # Privacy recommendations
        recommendations = generate_privacy_recommendations(user_pref, privacy_score)
        
        return Response({
            'privacy_score': privacy_score,
            'overall_privacy_level': get_privacy_level_name(privacy_score),
            'consent_status': consent_status,
            'data_collection': data_collection,
            'recent_activity': recent_activity,
            'recommendations': recommendations,
            'last_updated': user_pref.updated_at.isoformat() if user_pref.updated_at else None,
        })
        
    except Exception as e:
        logger.error(f"Error getting privacy overview: {str(e)}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def privacy_quick_toggle(request):
    """
    Quick toggle for common privacy settings
    """
    try:
        setting = request.data.get('setting')
        value = request.data.get('value')
        
        if not setting:
            return Response({'error': 'Setting parameter required'}, status=400)
        
        user_pref = UserPreference.get_by_user_id(request.user.id)
        if not user_pref:
            return Response({'error': 'User preferences not found'}, status=404)
        
        # Update the specific setting
        mapping = {
            'analytics': 'allow_analytics',
            'behavioral_analysis': 'allow_behavioral_analysis',
            'personalization': 'allow_personalization',
            'marketing': 'allow_marketing',
        }
        if setting not in mapping:
            return Response({'error': 'Invalid setting'}, status=400)

        # Record consent change (and update privacy settings)
        user_pref.record_consent_change(
            consent_type=setting,
            granted=bool(value),
            ip_address=request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Get updated privacy data
        privacy_score = calculate_privacy_score(user_pref)
        
        return Response({
            'success': True,
            'privacy_data': {
                'privacy_score': privacy_score,
                'overall_privacy_level': get_privacy_level_name(privacy_score),
                'consent_status': {
                    'allow_analytics': user_pref.privacy_settings.allow_analytics,
                    'allow_behavioral_analysis': user_pref.privacy_settings.allow_behavioral_analysis,
                    'allow_personalization': user_pref.privacy_settings.allow_personalization,
                    'allow_marketing': user_pref.privacy_settings.allow_marketing,
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error toggling privacy setting: {str(e)}")
        return Response({'error': str(e)}, status=500)

# =============================================================================
# PRIVACY HELPER FUNCTIONS
# =============================================================================

def calculate_privacy_score(user_pref: UserPreference) -> int:
    """Calculate overall privacy protection score"""
    score = 0
    privacy_settings = user_pref.privacy_settings
    
    # Base score for having privacy settings
    if privacy_settings:
        score += 20
    
    # Consent granularity bonus
    consent_count = len(privacy_settings.consent_records) if privacy_settings.consent_records else 0
    score += min(20, consent_count * 5)
    
    # Data retention settings
    if hasattr(user_pref, 'data_collection_settings') and user_pref.data_collection_settings:
        retention_settings = user_pref.data_collection_settings.get('retention', {})
        if retention_settings:
            score += 15
    
    # Privacy-conscious choices (lower collection = higher score)
    if not getattr(privacy_settings, 'allow_behavioral_analysis', False):
        score += 10
    if not getattr(privacy_settings, 'allow_marketing', False):
        score += 10
    if getattr(privacy_settings, 'data_minimization', False):
        score += 10
    
    return min(score, 100)

def get_privacy_level_name(score: int) -> str:
    """Get privacy level name from score"""
    if score >= 80:
        return 'High'
    elif score >= 60:
        return 'Medium'
    elif score >= 40:
        return 'Basic'
    else:
        return 'Low'

def get_recent_privacy_activity(user_pref: UserPreference) -> list:
    """Get recent privacy-related activities"""
    activities = []
    
    # Get recent privacy events from consent history
    if user_pref.consent_history:
        for record in user_pref.consent_history[-5:]:  # Last 5 records
            activities.append({
                'action': f'Consent {"granted" if record.granted else "withdrawn"}',
                'description': f'{(record.consent_type or ", ".join(record.consent_types))} consent updated',
                'timestamp': record.updated_at.isoformat() if record.updated_at else datetime.now().isoformat(),
            })
    
    return activities

def generate_privacy_recommendations(user_pref: UserPreference, privacy_score: int) -> list:
    """Generate privacy improvement recommendations"""
    recommendations = []
    
    if privacy_score < 60:
        recommendations.append({
            'title': 'Review Your Consent Settings',
            'description': 'Consider reviewing which data collection activities you consent to.',
            'action_text': 'Review Consents',
        })
    
    if not user_pref.privacy_settings.data_minimization:
        recommendations.append({
            'title': 'Enable Data Minimization',
            'description': 'Reduce the amount of data we collect about you.',
            'action_text': 'Enable Now',
        })
    
    return recommendations


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def data_collection_settings(request):
    """Update user's data collection settings"""
    try:
        user_pref = UserPreference.objects(user_id=str(request.user.id)).first()
        if not user_pref:
            return Response({'error': 'User preferences not found'}, status=status.HTTP_404_NOT_FOUND)
        
        settings = request.data.get('settings', {})
        
        # Update collection settings in privacy_settings
        if not hasattr(user_pref.privacy_settings, 'collection_settings'):
            user_pref.privacy_settings.collection_settings = {}
        
        user_pref.privacy_settings.collection_settings.update(settings)
        user_pref.save()
        
        return Response({
            'message': 'Data collection settings updated successfully',
            'settings': user_pref.privacy_settings.collection_settings
        })
        
    except Exception as e:
        logger.error(f"Error updating data collection settings for user {request.user.id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_consent(request, consent_id):
    """Update a specific consent (by record_id or consent_type)"""
    try:
        user_pref = UserPreference.get_by_user_id(request.user.id)
        if not user_pref:
            return Response({'error': 'User preferences not found'}, status=status.HTTP_404_NOT_FOUND)

        granted = bool(request.data.get('granted', False))

        # Resolve consent type
        consent_type = None
        for rec in (user_pref.consent_history or []):
            if getattr(rec, 'record_id', None) == consent_id:
                consent_type = rec.consent_type or (rec.consent_types[0] if rec.consent_types else None)
                break
        if not consent_type:
            consent_type = consent_id

        # Record the change and update flags
        user_pref.record_consent_change(
            consent_type=consent_type,
            granted=granted,
            ip_address=request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Prepare response with latest consent entry for this type
        latest = None
        for rec in reversed(user_pref.consent_history):
            rtype = rec.consent_type or (rec.consent_types[0] if rec.consent_types else None)
            if rtype == consent_type:
                latest = rec
                break

        privacy_score = calculate_privacy_score(user_pref)
        return Response({
            'consent': {
                'id': getattr(latest, 'record_id', None),
                'consent_type': consent_type,
                'granted': granted,
                'granted_at': latest.granted_at.isoformat() if latest and latest.granted_at else None,
                'updated_at': latest.updated_at.isoformat() if latest and latest.updated_at else None
            },
            'privacy_data': {
                'privacy_score': privacy_score,
                'privacy_summary': user_pref.get_privacy_summary()
            }
        })

    except Exception as e:
        logger.error(f"Error updating consent {consent_id} for user {request.user.id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_all_consents(request):
    """Revoke all non-essential consents"""
    try:
        user_pref = UserPreference.get_by_user_id(request.user.id)
        if not user_pref:
            return Response({'error': 'User preferences not found'}, status=status.HTTP_404_NOT_FOUND)

        revoke_types = [
            'analytics', 'personalization', 'marketing', 'social_data',
            'behavioral_analysis', 'third_party_sharing', 'location_data', 'device_fingerprinting'
        ]
        for t in revoke_types:
            user_pref.record_consent_change(
                consent_type=t,
                granted=False,
                ip_address=request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        privacy_score = calculate_privacy_score(user_pref)
        return Response({
            'message': 'All non-essential consents have been revoked',
            'consent_records': [
                {
                    'id': rec.record_id,
                    'consent_type': rec.consent_type,
                    'consent_types': rec.consent_types,
                    'granted': rec.granted,
                    'updated_at': rec.updated_at.isoformat() if rec.updated_at else None,
                } for rec in user_pref.consent_history
            ],
            'privacy_data': {
                'privacy_score': privacy_score,
                'privacy_summary': user_pref.get_privacy_summary()
            }
        })

    except Exception as e:
        logger.error(f"Error revoking all consents for user {request.user.id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_consent_history(request):
    """Download user's consent history as JSON"""
    try:
        from django.http import HttpResponse
        import json

        user_pref = UserPreference.get_by_user_id(request.user.id)
        if not user_pref:
            return Response({'error': 'User preferences not found'}, status=status.HTTP_404_NOT_FOUND)

        consent_history = {
            'user_id': request.user.id,
            'generated_at': datetime.utcnow().isoformat(),
            'consent_records': []
        }

        for record in (user_pref.consent_history or []):
            consent_history['consent_records'].append({
                'id': getattr(record, 'record_id', None),
                'consent_type': record.consent_type,
                'consent_types': record.consent_types,
                'granted': record.granted,
                'granted_at': record.granted_at.isoformat() if record.granted_at else None,
                'updated_at': record.updated_at.isoformat() if record.updated_at else None,
                'expires_at': record.expires_at.isoformat() if record.expires_at else None,
            })

        response = HttpResponse(
            json.dumps(consent_history, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="consent-history.json"'
        return response

    except Exception as e:
        logger.error(f"Error generating consent history for user {request.user.id}: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
