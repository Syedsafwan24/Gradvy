"""
API views for user preferences and personalization.
Handles CRUD operations for MongoDB-stored user data.
"""
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from utils.responses import (
    APISuccess, APIError, APIValidationError, PreferencesAPIResponse,
    StatusCodes, ErrorCodes, handle_exception
)
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
from .debug_utils import PreferencesDebugger
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
            # Enhanced debug logging for preferences retrieval
            logger.info(f"🔍 PREFERENCES GET - User {request.user.id} requesting preferences")
            logger.debug(f"👤 User details: ID={request.user.id}, email={request.user.email}")
            logger.debug(f"🔐 User authenticated: {request.user.is_authenticated}")

            preference = UserPreference.get_by_user_id(request.user.id)

            if not preference:
                logger.warning(f"❌ NO PREFERENCES FOUND - User {request.user.id} has no preferences record")
                return PreferencesAPIResponse.preferences_not_found()

            logger.info(f"✅ PREFERENCES FOUND - User {request.user.id} has preferences record")
            logger.debug(f"📊 Profile completion: {preference.profile_completion_percentage:.1f}%")
            logger.debug(f"🏷️  Onboarding status: {preference.onboarding_status}")

            # Verify data availability before serialization
            logger.debug(f"🔍 VERIFICATION - Basic info exists: {bool(preference.basic_info)}")
            logger.debug(f"🔍 VERIFICATION - Content prefs exists: {bool(preference.content_preferences)}")

            if preference.basic_info:
                logger.debug(f"📋 Basic info fields: {len([f for f in ['learning_goals', 'experience_level', 'preferred_pace'] if getattr(preference.basic_info, f, None)])}")

            if preference.content_preferences:
                logger.debug(f"🎯 Content pref fields: {len([f for f in ['preferred_platforms', 'content_types', 'language_preference'] if getattr(preference.content_preferences, f, None)])}")

            serializer = UserPreferenceSerializer(preference)
            serialized_data = serializer.data

            # Enhanced format verification for consistency with onboarding response
            logger.debug(f"🔍 GET RESPONSE FORMAT VERIFICATION:")
            logger.debug(f"   📊 Response has basic_info: {bool(serialized_data.get('basic_info'))}")
            logger.debug(f"   📊 Response has content_preferences: {bool(serialized_data.get('content_preferences'))}")
            logger.debug(f"   📊 Response profile_completion: {serialized_data.get('profile_completion_percentage')}")
            logger.debug(f"   📦 All response keys: {list(serialized_data.keys())}")

            # Check for missing critical data that would cause frontend issues
            critical_fields_missing = []
            if not serialized_data.get('basic_info'):
                critical_fields_missing.append('basic_info')
            if not serialized_data.get('content_preferences'):
                critical_fields_missing.append('content_preferences')

            if critical_fields_missing:
                logger.warning(f"⚠️  MISSING CRITICAL FIELDS: {critical_fields_missing}")
                logger.warning(f"   This may cause preferences page to show empty data")
                logger.warning(f"   User {request.user.id} has incomplete onboarding record")
                logger.warning(f"   📊 Onboarding status: {preference.onboarding_status}")
                logger.warning(f"   ✅ Truly complete: {preference.is_onboarding_truly_complete()}")

                # AUTO-MIGRATION: Fix missing content_preferences for existing users
                if 'content_preferences' in critical_fields_missing and preference.content_preferences is None:
                    logger.info(f"🔧 AUTO-MIGRATION: Creating missing content_preferences for user {request.user.id}")

                    # Import ContentPreferences model
                    from .models import ContentPreferences

                    # Create content_preferences with safe defaults
                    preference.content_preferences = ContentPreferences(
                        preferred_platforms=[],
                        content_types=[],
                        language_preference=['english', 'hindi']
                    )

                    # Save the migrated data
                    preference.save()
                    logger.info(f"✅ AUTO-MIGRATION SUCCESS: Content preferences created for user {request.user.id}")

                    # Re-serialize with the complete data
                    serializer = UserPreferenceSerializer(preference)
                    serialized_data = serializer.data

                    # Update critical_fields_missing since we fixed it
                    critical_fields_missing = []
                    if not serialized_data.get('basic_info'):
                        critical_fields_missing.append('basic_info')
                    if not serialized_data.get('content_preferences'):
                        critical_fields_missing.append('content_preferences')

                    logger.info(f"🎯 POST-MIGRATION: Critical fields still missing: {critical_fields_missing}")

            # Verify data structure matches what frontend components expect
            frontend_compatibility_check = {
                'has_basic_info_structure': bool(serialized_data.get('basic_info')),
                'has_content_prefs_structure': bool(serialized_data.get('content_preferences')),
                'has_completion_percentage': 'profile_completion_percentage' in serialized_data,
                'ready_for_preferences_page': len(critical_fields_missing) == 0
            }

            logger.debug(f"🔍 FRONTEND COMPATIBILITY CHECK: {frontend_compatibility_check}")
            logger.info(f"🎉 PREFERENCES SUCCESS - User {request.user.id} preferences retrieved successfully")

            return PreferencesAPIResponse.preferences_retrieved(
                preferences_data=serialized_data,
                message="Preferences retrieved successfully"
            )

        except Exception as e:
            # Enhanced error logging for debugging preferences retrieval failures
            logger.error(f"❌ PREFERENCES EXCEPTION - User {request.user.id}: {str(e)}")
            logger.error(f"🔍 Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"📍 Traceback: {traceback.format_exc()}")

            return handle_exception(
                exception=e,
                default_message='Failed to retrieve preferences'
            )
    
    def post(self, request):
        """Create initial preferences (usually from onboarding)"""
        try:
            # Check if user already has preferences
            existing = UserPreference.get_by_user_id(request.user.id)
            if existing:
                return APIError.conflict(
                    message='User preferences already exist. Use PUT to update.',
                    code=ErrorCodes.RESOURCE_CONFLICT,
                    details={'existing_data': UserPreferenceSerializer(existing).data}
                )
            
            serializer = UserPreferenceSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                preference = serializer.save()
                
                # Log preference creation
                logger.info(f"Created preferences for user {request.user.id}")
                
                return APISuccess.created(
                    data=UserPreferenceSerializer(preference).data,
                    message='Preferences created successfully'
                )
            
            return APIValidationError.create_from_serializer(serializer)
            
        except Exception as e:
            logger.error(f"Error creating preferences for user {request.user.id}: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to create preferences'
            )
    
    def put(self, request):
        """Update user preferences (full update)"""
        return self._update_preferences(request, partial=False)
    
    def patch(self, request):
        """Partially update user preferences"""
        return self._update_preferences(request, partial=True)
    
    def _update_preferences(self, request, partial=False):
        """Common logic for PUT/PATCH operations"""
        try:
            # Debug logging for manual save investigation
            logger.info(f"🔍 Preferences update request from user {request.user.id}")
            logger.info(f"📥 Request method: {request.method}")
            logger.info(f"📋 Partial update: {partial}")
            logger.info(f"📦 Request data: {request.data}")
            logger.info(f"📐 Data size: {len(str(request.data))} characters")

            preference = UserPreference.get_by_user_id(request.user.id)
            
            if not preference:
                return PreferencesAPIResponse.preferences_not_found()
            
            serializer = UserPreferenceSerializer(
                preference,
                data=request.data,
                partial=partial,
                context={'request': request}
            )
            
            if serializer.is_valid():
                updated_preference = serializer.save()

                # Ensure completion percentage is updated (safety net)
                updated_preference.update_completion_percentage()

                # Log preference update
                logger.info(f"✅ Updated preferences for user {request.user.id}")

                return PreferencesAPIResponse.preferences_updated(
                    preferences_data=UserPreferenceSerializer(updated_preference).data,
                    message='Preferences updated successfully'
                )

            # Debug: Log validation errors in detail
            logger.error(f"❌ Serializer validation failed for user {request.user.id}")
            logger.error(f"🔍 Validation errors: {serializer.errors}")
            logger.error(f"📋 Request data that failed validation: {request.data}")

            return APIValidationError.create_from_serializer(serializer)
            
        except Exception as e:
            # Enhanced error handling for MongoDB validation failures
            error_message = str(e)
            logger.error(f"Error updating preferences for user {request.user.id}: {error_message}")

            # Comprehensive logging for debugging
            logger.error(f"Request data: {request.data}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Full error details: {repr(e)}")

            # Check if this is a MongoDB validation error
            if 'Document failed validation' in error_message:
                # Parse MongoDB validation error for user-friendly message
                user_friendly_error = self._parse_mongodb_validation_error(error_message)
                return PreferencesAPIResponse.mongodb_validation_error(e)

            # Check for other common MongoDB errors
            elif 'Could not save document' in error_message:
                return APIError.bad_request(
                    message='Unable to save your preferences due to data validation issues.',
                    code=ErrorCodes.VALIDATION_ERROR,
                    details={'advice': 'Please check that all your selections are from the available options.'}
                )

            # Generic error fallback
            return handle_exception(
                exception=e,
                default_message='An unexpected error occurred while updating your preferences.'
            )

    def _parse_mongodb_validation_error(self, error_message):
        """
        Parse MongoDB validation error message to provide user-friendly feedback
        """
        try:
            import re

            # Extract invalid value from error message if present
            def extract_invalid_value():
                patterns = [
                    r"'consideredValue': '([^']+)'",
                    r'"consideredValue": "([^"]+)"',
                    r'value "([^"]+)" not in',
                    r"'([^']+)' is not valid"
                ]
                for pattern in patterns:
                    match = re.search(pattern, error_message)
                    if match:
                        return match.group(1)
                return None

            invalid_value = extract_invalid_value()

            # Field-specific validation errors
            if 'learning_goals' in error_message:
                return f"Invalid learning goal{f': {invalid_value}' if invalid_value else ''}. Please select from the available options."

            elif 'experience_level' in error_message:
                return f"Invalid experience level{f': {invalid_value}' if invalid_value else ''}. Please choose from: Complete Beginner, Some Basics, Intermediate, or Advanced."

            elif 'preferred_pace' in error_message:
                return f"Invalid learning pace{f': {invalid_value}' if invalid_value else ''}. Please choose from: Slow, Medium, or Fast."

            elif 'time_availability' in error_message:
                return f"Invalid time availability{f': {invalid_value}' if invalid_value else ''}. Please choose from: 1-2hrs, 3-5hrs, or 5+hrs per week."

            elif 'learning_style' in error_message:
                return f"Invalid learning style{f': {invalid_value}' if invalid_value else ''}. Please choose from: Visual, Hands-on, Reading, Videos, or Interactive."

            elif 'career_stage' in error_message:
                return f"Invalid career stage{f': {invalid_value}' if invalid_value else ''}. Please choose from: Student, Career Change, Skill Upgrade, or Professional."

            elif 'target_timeline' in error_message:
                return f"Invalid timeline{f': {invalid_value}' if invalid_value else ''}. Please choose from: 3 months, 6 months, 1 year, or Flexible."

            elif 'preferred_platforms' in error_message:
                if invalid_value:
                    # Provide specific messages for commonly selected unsupported platforms
                    platform_messages = {
                        'freecodecamp': "FreeCodeCamp is temporarily unavailable while we update our platform support. Please select from our currently available platforms: Udemy, Coursera, YouTube, edX, Khan Academy, Pluralsight, or LinkedIn Learning.",
                        'codecademy': "Codecademy is temporarily unavailable while we update our platform support. Please select from our currently available platforms.",
                        'skillshare': "Skillshare is temporarily unavailable while we update our platform support. Please select from our currently available platforms.",
                        'masterclass': "MasterClass is temporarily unavailable while we update our platform support. Please select from our currently available platforms.",
                        'brilliant': "Brilliant is temporarily unavailable while we update our platform support. Please select from our currently available platforms.",
                        'datacamp': "DataCamp is temporarily unavailable while we update our platform support. Please select from our currently available platforms.",
                        'udacity': "Udacity is temporarily unavailable while we update our platform support. Please select from our currently available platforms.",
                    }

                    if invalid_value.lower() in platform_messages:
                        return platform_messages[invalid_value.lower()]
                    else:
                        return f"The platform '{invalid_value}' is temporarily unavailable while we update our platform support. Please select from our currently available platforms: Udemy, Coursera, YouTube, edX, Khan Academy, Pluralsight, or LinkedIn Learning."
                return "Some selected learning platforms are temporarily unavailable. Please choose from our currently supported platforms: Udemy, Coursera, YouTube, edX, Khan Academy, Pluralsight, or LinkedIn Learning."

            elif 'content_types' in error_message:
                return f"Invalid content type{f': {invalid_value}' if invalid_value else ''}. Please choose from: Video, Article, Interactive, Quiz, Project, Book, or Podcast."

            elif 'difficulty_preference' in error_message:
                return f"Invalid difficulty level{f': {invalid_value}' if invalid_value else ''}. Please choose from: Beginner, Intermediate, Advanced, or Mixed."

            elif 'duration_preference' in error_message:
                return f"Invalid duration preference{f': {invalid_value}' if invalid_value else ''}. Please choose from: Short, Medium, Long, or Mixed."

            elif 'language_preference' in error_message:
                return f"Invalid language preference{f': {invalid_value}' if invalid_value else ''}. Please enter valid language codes."

            elif 'instructor_ratings_min' in error_message:
                return "Invalid instructor rating minimum. Please enter a value between 0.0 and 5.0."

            # MongoDB-specific error patterns
            elif 'ValidationError' in error_message or 'Document failed validation' in error_message:
                # Try to extract field name from validation error
                field_match = re.search(r"ValidationError \(([^)]+)\)", error_message)
                if field_match:
                    field_name = field_match.group(1)
                    return f"Validation error in field '{field_name}'. Please check your input and try again."
                return "Document validation failed. Please check all your inputs and try again."

            elif 'required' in error_message.lower():
                return "Some required fields are missing. Please fill in all required information."

            elif 'unique' in error_message.lower():
                return "This data conflicts with existing records. Please check your input."

            # Generic fallback with more helpful message
            return "Some of your selections contain invalid values. Please review your choices and ensure they match the available options."

        except Exception as e:
            logger.error(f"Error parsing MongoDB validation error: {str(e)}")
            return "Invalid data detected. Please check your selections and try again."


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
            # Enhanced debug logging for onboarding submission
            logger.info(f"🎯 ONBOARDING START - User {request.user.id} submitting onboarding data")
            logger.debug(f"📦 Request data keys: {list(request.data.keys())}")
            logger.debug(f"📋 Request data sample: {dict(list(request.data.items())[:5])}")
            logger.debug(f"🔐 User authenticated: {request.user.is_authenticated}")
            logger.debug(f"👤 User details: ID={request.user.id}, email={request.user.email}")

            # Check if user already completed onboarding with all required data
            existing = UserPreference.get_by_user_id(request.user.id)
            if existing:
                # Use the new method to check if onboarding is truly complete
                is_truly_complete = existing.is_onboarding_truly_complete()

                if is_truly_complete:
                    logger.warning(f"⚠️  User {request.user.id} has complete preferences - onboarding already finished")
                    return APISuccess.create(
                        data=UserPreferenceSerializer(existing).data,
                        message='Onboarding already completed'
                    )
                else:
                    # User has incomplete preferences - log details and allow re-completion
                    missing_fields = []
                    if existing.basic_info is None:
                        missing_fields.append('basic_info')
                    if existing.onboarding_status == 'full_completed' and existing.content_preferences is None:
                        missing_fields.append('content_preferences')

                    logger.info(f"🔄 User {request.user.id} has incomplete preferences - missing {missing_fields}")
                    logger.info(f"📊 Current status: {existing.onboarding_status}, allowing re-completion")
                    logger.info(f"🎯 Completion status: basic_info={existing.basic_info is not None}, content_preferences={existing.content_preferences is not None}")

                    # Continue with onboarding to fill in missing data
                    # The serializer will update the existing record
            
            serializer = OnboardingSerializer(
                data=request.data,
                context={'request': request}
            )

            logger.debug(f"🔍 Validating onboarding data for user {request.user.id}")
            if serializer.is_valid():
                logger.info(f"✅ Onboarding validation passed for user {request.user.id}")
                logger.debug(f"📋 Validated data fields: {list(serializer.validated_data.keys())}")

                # Log data distribution
                basic_info_fields = ['learning_goals', 'experience_level', 'preferred_pace', 'time_availability', 'learning_style', 'career_stage', 'target_timeline']
                content_fields = ['preferred_platforms', 'content_types', 'language_preference']

                basic_count = sum(1 for field in basic_info_fields if serializer.validated_data.get(field))
                content_count = sum(1 for field in content_fields if serializer.validated_data.get(field))
                logger.debug(f"📊 Data distribution - Basic info: {basic_count}/{len(basic_info_fields)}, Content: {content_count}/{len(content_fields)}")

                logger.info(f"💾 Starting preference creation for user {request.user.id}")
                preference = serializer.save()
                logger.info(f"✅ Preference created successfully for user {request.user.id}")

                logger.info(f"✅ Completed onboarding for user {request.user.id}")
                logger.debug(f"📊 Pre-refresh completion: {preference.profile_completion_percentage:.1f}%")

                # Refresh object from database to ensure latest state
                preference.reload()
                logger.debug(f"🔄 Post-refresh completion: {preference.profile_completion_percentage:.1f}%")

                # Use the standard serializer for consistent data format
                serialized_data = UserPreferenceSerializer(preference).data
                logger.debug(f"📤 Response completion: {serialized_data.get('profile_completion_percentage', 'N/A')}%")

                # Enhanced verification of data structure consistency
                logger.debug(f"🔍 RESPONSE FORMAT VERIFICATION:")
                logger.debug(f"   📊 Response has basic_info: {bool(serialized_data.get('basic_info'))}")
                logger.debug(f"   📊 Response has content_preferences: {bool(serialized_data.get('content_preferences'))}")
                logger.debug(f"   📊 Response profile_completion: {serialized_data.get('profile_completion_percentage')}")

                if serialized_data.get('basic_info'):
                    basic_info_keys = list(serialized_data['basic_info'].keys())
                    logger.debug(f"   📋 Basic info fields: {basic_info_keys}")
                    logger.debug(f"   🎯 Learning goals count: {len(serialized_data['basic_info'].get('learning_goals', []))}")

                if serialized_data.get('content_preferences'):
                    content_keys = list(serialized_data['content_preferences'].keys())
                    logger.debug(f"   🎯 Content pref fields: {content_keys}")

                # Verify data consistency with what frontend expects
                expected_format_valid = (
                    'basic_info' in serialized_data and
                    'content_preferences' in serialized_data and
                    'profile_completion_percentage' in serialized_data
                )
                logger.debug(f"🔍 FRONTEND COMPATIBILITY - Expected format valid: {expected_format_valid}")

                # Create response data
                response_data = {
                    'preferences': serialized_data,
                    'profile_completion_percentage': preference.profile_completion_percentage,
                    'onboarding_status': preference.onboarding_status,
                    # Add cache invalidation metadata for frontend
                    'cache_invalidation': {
                        'timestamp': preference.updated_at.isoformat(),
                        'user_id': request.user.id,
                        'requires_refresh': True
                    }
                }

                logger.info(f"🎉 ONBOARDING SUCCESS - User {request.user.id} onboarding completed with {preference.profile_completion_percentage:.1f}% completion")
                logger.debug(f"📤 Final response data keys: {list(response_data.keys())}")
                return PreferencesAPIResponse.onboarding_completed(
                    preferences_data=response_data,
                    completion_percentage=preference.profile_completion_percentage,
                    message='Onboarding completed successfully'
                )
            else:
                # Validation failed - detailed error logging
                logger.error(f"❌ ONBOARDING VALIDATION FAILED - User {request.user.id}")
                logger.error(f"🔍 Validation errors: {serializer.errors}")
                logger.error(f"📋 Failed fields: {list(serializer.errors.keys())}")

                return APIValidationError.create_from_serializer(serializer)
            
        except Exception as e:
            # Enhanced error logging for debugging onboarding failures
            logger.error(f"❌ ONBOARDING EXCEPTION - User {request.user.id}: {str(e)}")
            logger.error(f"🔍 Exception type: {type(e).__name__}")
            logger.error(f"📋 Exception args: {e.args}")
            import traceback
            logger.error(f"📍 Traceback: {traceback.format_exc()}")

            return handle_exception(
                exception=e,
                default_message='Failed to complete onboarding'
            )


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
            
            # Update quick onboarding fields using new unified status
            preference.quick_onboarding_data = quick_onboarding_data
            preference.mark_onboarding_completed('quick')
            
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

            # CRITICAL: Always create content_preferences for quick onboarding
            # This ensures preferences page works correctly for all users
            from .models import ContentPreferences
            if not preference.content_preferences:
                logger.info(f"🔧 Creating content_preferences for quick onboarding user {request.user.id}")
                preference.content_preferences = ContentPreferences(
                    preferred_platforms=[],
                    content_types=[],
                    language_preference=['english', 'hindi']
                )
                logger.info(f"✅ Content preferences created for quick onboarding user {request.user.id}")

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
            
            logger.info(f"✅ Completed quick onboarding for user {request.user.id}")
            logger.info(f"📊 Final completion status: truly_complete={preference.is_onboarding_truly_complete()}")
            logger.info(f"🎯 Data completeness: basic_info={preference.basic_info is not None}, content_preferences={preference.content_preferences is not None}")
            logger.info(f"📈 Profile completion: {preference.profile_completion_percentage}%")

            # Use the standard serializer for consistent data format
            serialized_data = UserPreferenceSerializer(preference).data

            return APISuccess.created(
                data={
                    'preferences': serialized_data,
                    'profile_completion_percentage': preference.profile_completion_percentage,
                    'onboarding_status': preference.onboarding_status
                },
                message='Quick onboarding completed successfully'
            )
            
        except Exception as e:
            logger.error(f"Error during quick onboarding for user {request.user.id}: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to complete quick onboarding'
            )


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
                return APISuccess.created(
                    data=result,
                    message='Interaction logged successfully'
                )

            return APIValidationError.create_from_serializer(serializer)
            
        except Exception as e:
            logger.error(f"Error logging interaction for user {request.user.id}: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to log interaction'
            )


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
            
            return APISuccess.create(
                data={
                    'analytics': serializer.data,
                    'generated_at': datetime.utcnow().isoformat()
                },
                message='Analytics retrieved successfully'
            )
            
        except Exception as e:
            logger.error(f"Error generating analytics for user {request.user.id}: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to generate analytics'
            )


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
            # Debug logging for 404 troubleshooting
            logger.info(f"🔍 RECOMMENDATIONS DEBUG: User {request.user.id} accessing recommendations")
            logger.info(f"🔍 Request path: {request.path}")
            logger.info(f"🔍 Request method: {request.method}")
            logger.info(f"🔍 User authenticated: {request.user.is_authenticated}")

            # Check for valid cached recommendations
            recommendations = CourseRecommendation.get_valid_recommendations(request.user.id)
            
            if recommendations:
                serializer = CourseRecommendationSerializer(recommendations)
                return APISuccess.create(
                    data={
                        'recommendations': serializer.data,
                        'source': 'cached'
                    },
                    message='Recommendations retrieved successfully'
                )
            
            # No valid recommendations found
            return APISuccess.create(
                data={
                    'recommendations': {
                        'user_id': request.user.id,
                        'recommendations': [],
                        'generated_at': None,
                        'expires_at': None
                    },
                    'source': 'none'
                },
                message='No recommendations available. Recommendations will be generated based on your preferences.'
            )
            
        except Exception as e:
            logger.error(f"Error retrieving recommendations for user {request.user.id}: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to retrieve recommendations'
            )
    
    def post(self, request):
        """Force regeneration of recommendations (for testing)"""
        try:
            # This would typically be called by an AI service
            # For now, we'll create a placeholder
            
            user_preference = UserPreference.get_by_user_id(request.user.id)
            if not user_preference:
                return PreferencesAPIResponse.preferences_not_found()
            
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
            return APISuccess.created(
                data={
                    'recommendations': serializer.data,
                    'source': 'generated'
                },
                message='Recommendations generated successfully'
            )
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {request.user.id}: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to generate recommendations'
            )


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
        
        return APISuccess.create(
            data=choices,
            message='Preference choices retrieved successfully'
        )


@method_decorator(csrf_exempt, name='dispatch')
class OnboardingProgressView(views.APIView):
    """
    Save incremental onboarding progress for the current user.
    Stores progress data under UserPreference.custom_preferences.onboarding_progress
    without requiring the full onboarding payload.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            pref = UserPreference.get_by_user_id(request.user.id)
            if not pref:
                pref = UserPreference.create_for_user(request.user.id)

            payload = request.data or {}
            step = payload.get('step')
            step_data = payload.get('data', {})

            # Initialize progress structure
            progress = pref.custom_preferences.get('onboarding_progress', {})
            steps_store = progress.get('steps', {})

            if step:
                steps_store[str(step)] = step_data
                progress['last_step'] = step
            else:
                # If no explicit step provided, still persist data
                progress['last_updated_payload'] = step_data

            progress['updated_at'] = datetime.utcnow().isoformat()
            progress['steps'] = steps_store

            # Persist back to custom preferences
            pref.custom_preferences['onboarding_progress'] = progress
            pref.save()

            return APISuccess.create(
                data={'onboarding_progress': progress},
                message='Progress saved successfully'
            )

        except Exception as e:
            logger.error(f"Error saving onboarding progress for user {request.user.id}: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to save onboarding progress'
            )


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
        return APISuccess.create(
            data={
                'privacy_summary': summary,
                'consent_records': records
            },
            message='Privacy consent summary retrieved successfully'
        )


@method_decorator(csrf_exempt, name='dispatch')
class PrivacyConsentUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, consent_id):
        """Update a specific consent (by record_id or consent_type)"""
        granted = request.data.get('granted', None)
        if granted is None:
            return APIError.bad_request(
                message='granted parameter is required',
                code=ErrorCodes.REQUIRED_FIELD_MISSING,
                field_errors={'granted': ['This field is required']}
            )

        pref = UserPreference.get_by_user_id(request.user.id)
        if not pref:
            return PreferencesAPIResponse.preferences_not_found()

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

        return APISuccess.create(
            data={
                'consent': {
                    'id': getattr(latest, 'record_id', None),
                    'consent_type': latest.consent_type,
                    'consent_types': latest.consent_types,
                    'granted': latest.granted,
                    'granted_at': latest.granted_at.isoformat() if latest.granted_at else None,
                    'updated_at': latest.updated_at.isoformat() if latest.updated_at else None,
                },
                'privacy_data': pref.get_privacy_summary()
            },
            message='Consent updated successfully'
        )


@method_decorator(csrf_exempt, name='dispatch')
class RevokeAllConsentsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        pref = UserPreference.get_by_user_id(request.user.id)
        if not pref:
            return PreferencesAPIResponse.preferences_not_found()

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

        return APISuccess.create(
            data={
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
            },
            message='All consents revoked successfully'
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def consent_history_download(request):
    """Download consent history as JSON attachment"""
    pref = UserPreference.get_by_user_id(request.user.id)
    if not pref:
        return APIError.not_found(
            message='User preferences not found',
            code=ErrorCodes.RESOURCE_NOT_FOUND
        )

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
    return APISuccess.create(
        data={
            'privacy_policy_version': privacy_version,
            'terms_version': terms_version,
            'cookie_policy_version': cookie_version,
            'last_updated': now().isoformat()
        },
        message='Privacy policy versions retrieved successfully'
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def privacy_accept(request):
    policy = request.data.get('policy')  # 'privacy' | 'terms' | 'cookie'
    version = request.data.get('version')
    if not policy or not version:
        return APIError.bad_request(
            message='Policy and version are required',
            code=ErrorCodes.REQUIRED_FIELD_MISSING,
            field_errors={'policy': ['This field is required'], 'version': ['This field is required']}
        )

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
        return APIError.bad_request(
            message='Invalid policy type. Must be privacy, terms, or cookie',
            code=ErrorCodes.INVALID_INPUT_FORMAT,
            field_errors={'policy': ['Must be one of: privacy, terms, cookie']}
        )

    pref.privacy_settings.last_updated = datetime.utcnow()
    pref.save()

    return APISuccess.create(
        data={
            'status': 'accepted',
            'privacy_settings': pref.get_privacy_summary()
        },
        message='Privacy policy accepted successfully'
    )


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
                return APIError.bad_request(
                    message='No events provided',
                    code=ErrorCodes.REQUIRED_FIELD_MISSING,
                    field_errors={'events': ['At least one event is required']}
                )
            
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
            
            return APISuccess.created(
                data={
                    'processed_events': len(processed_events),
                    'total_events': len(events),
                    'privacy_level': self._get_privacy_level(user_preference)
                },
                message='Analytics events processed successfully'
            )
            
        except Exception as e:
            logger.error(f"Failed to process analytics events: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to process analytics events'
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
                return APIError.bad_request(
                    message='No consent types provided',
                    code=ErrorCodes.REQUIRED_FIELD_MISSING,
                    field_errors={'consent_types': ['At least one consent type is required']}
                )
            
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
            
            return APISuccess.created(
                data={
                    'privacy_settings': user_preference.get_privacy_summary(),
                    'consent_recorded': consent_types
                },
                message='Privacy consent recorded successfully'
            )
            
        except Exception as e:
            logger.error(f"Failed to record privacy consent: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to record privacy consent'
            )
    
    def get(self, request):
        """Get current privacy settings"""
        try:
            user_preference = UserPreference.get_by_user_id(request.user.id)
            
            if not user_preference:
                return APISuccess.create(
                    data={
                        'privacy_configured': False,
                        'available_consent_types': [
                            'essential', 'analytics', 'personalization', 'marketing',
                            'social_integration', 'behavioral_analysis', 'external_enrichment'
                        ]
                    },
                    message='Privacy settings retrieved successfully'
                )
            
            return APISuccess.create(
                data=user_preference.get_privacy_summary(),
                message='Privacy settings retrieved successfully'
            )
            
        except Exception as e:
            logger.error(f"Failed to get privacy settings: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to get privacy settings'
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
                return PreferencesAPIResponse.preferences_not_found()
            
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
            
            return APISuccess.create(
                data=analytics_data,
                message='Enhanced analytics retrieved successfully'
            )
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {str(e)}")
            return handle_exception(
                exception=e,
                default_message='Failed to get enhanced analytics'
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
            return PreferencesAPIResponse.preferences_not_found()
        
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
        return handle_exception(
            exception=e,
            default_message='Internal server error occurred'
        )


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_consent(request, consent_id):
    """Update a specific consent (by record_id or consent_type)"""
    try:
        user_pref = UserPreference.get_by_user_id(request.user.id)
        if not user_pref:
            return PreferencesAPIResponse.preferences_not_found()

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
        return handle_exception(
            exception=e,
            default_message='Internal server error occurred'
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_all_consents(request):
    """Revoke all non-essential consents"""
    try:
        user_pref = UserPreference.get_by_user_id(request.user.id)
        if not user_pref:
            return PreferencesAPIResponse.preferences_not_found()

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
        return handle_exception(
            exception=e,
            default_message='Internal server error occurred'
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_consent_history(request):
    """Download user's consent history as JSON"""
    try:
        from django.http import HttpResponse
        import json

        user_pref = UserPreference.get_by_user_id(request.user.id)
        if not user_pref:
            return PreferencesAPIResponse.preferences_not_found()

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
        return handle_exception(
            exception=e,
            default_message='Internal server error occurred'
        )


# =============================================================================
# DEBUG API ENDPOINTS (development/troubleshooting)
# =============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class PreferencesDebugView(views.APIView):
    """
    Debug endpoint for troubleshooting preferences data flow issues.
    Used to diagnose why onboarding data doesn't appear in preferences page.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get comprehensive debug information for current user's preferences"""
        try:
            # Dump current user's state
            debug_data = PreferencesDebugger.dump_user_state(request.user.id)

            # Also run flow verification
            flow_verification = PreferencesDebugger.verify_onboarding_to_preferences_flow(request.user.id)

            response_data = {
                'user_id': request.user.id,
                'timestamp': datetime.utcnow().isoformat(),
                'debug_dump': debug_data,
                'flow_verification': flow_verification,
                'recommendations': _generate_debug_recommendations(debug_data, flow_verification)
            }

            logger.info(f"🔍 DEBUG ENDPOINT ACCESSED - User {request.user.id}")

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"❌ DEBUG ENDPOINT FAILED - User {request.user.id}: {str(e)}")
            return Response({
                'error': 'Debug endpoint failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _generate_debug_recommendations(debug_data: dict, flow_verification: dict) -> list:
    """Generate actionable recommendations based on debug findings"""
    recommendations = []

    # Check for common issues
    issues = debug_data.get('issues_detected', [])

    if 'No preferences record found in MongoDB' in issues:
        recommendations.append('User needs to complete onboarding to create preferences record')

    if 'Basic info is missing' in issues:
        recommendations.append('Re-run onboarding process to populate basic info')

    if 'Content preferences are missing' in issues:
        recommendations.append('Check onboarding serializer - content preferences not being saved')

    if any('serialization' in issue.lower() for issue in issues):
        recommendations.append('Check UserPreferenceSerializer for field mapping issues')

    if not flow_verification.get('flow_healthy', True):
        recommendations.append('Data flow from onboarding to preferences has issues - check bottlenecks')

    # Check cache issues
    if debug_data.get('database_state', {}).get('preferences_exist') and \
       not debug_data.get('serialization_state', {}).get('serialization_successful'):
        recommendations.append('Data exists in DB but serialization fails - check model-serializer mapping')

    if not recommendations:
        recommendations.append('No issues detected - preferences should display correctly')

    return recommendations
