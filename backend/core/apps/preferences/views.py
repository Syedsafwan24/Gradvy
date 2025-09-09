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
