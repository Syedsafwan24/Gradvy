"""
Serializers for user preferences and MongoDB data.
Converts between MongoDB documents and REST API JSON.
"""
from rest_framework import serializers
from typing import Dict, List, Any
from .models import UserPreference, BasicInfo, OnboardingStatus

# Import moved classes from their new domain apps
try:
    from apps.learning_content.models import ContentPreferences
    from apps.analytics.models import AIInsights, InteractionData
except ImportError:
    # Fallback for development - define minimal classes for compatibility
    class ContentPreferences:
        PLATFORM_CHOICES = ['udemy', 'coursera', 'youtube', 'edx', 'khan_academy', 'pluralsight', 'linkedin_learning']
        CONTENT_TYPES = ['video', 'article', 'interactive', 'quiz', 'project', 'book', 'podcast']
        DIFFICULTY_CHOICES = ['mixed', 'beginner', 'intermediate', 'advanced']
        DURATION_CHOICES = ['short', 'medium', 'long', 'mixed']

    class AIInsights:
        pass

    class InteractionData:
        INTERACTION_TYPES = ['course_click', 'quiz_attempt', 'video_watch', 'search', 'page_view', 'course_enroll', 'course_complete', 'bookmark', 'rating_given', 'review_written', 'course_abandoned', 'onboarding_started', 'onboarding_flow_completed']


class BasicInfoSerializer(serializers.Serializer):
    """Serializer for basic user learning preferences"""
    
    learning_goals = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    experience_level = serializers.ChoiceField(
        choices=BasicInfo.EXPERIENCE_CHOICES,
        required=False
    )
    preferred_pace = serializers.ChoiceField(
        choices=BasicInfo.PACE_CHOICES,
        required=False
    )
    time_availability = serializers.ChoiceField(
        choices=BasicInfo.TIME_CHOICES,
        required=False
    )
    learning_style = serializers.ListField(
        child=serializers.ChoiceField(choices=BasicInfo.STYLE_CHOICES),
        required=False,
        default=list
    )
    career_stage = serializers.ChoiceField(
        choices=BasicInfo.CAREER_CHOICES,
        required=False,
        allow_blank=True  # Allow empty strings
    )
    target_timeline = serializers.ChoiceField(
        choices=BasicInfo.TIMELINE_CHOICES,
        required=False,
        allow_blank=True  # Allow empty strings
    )

    def validate_career_stage(self, value):
        """Convert empty strings to None for proper MongoDB handling"""
        return None if value == '' else value

    def validate_target_timeline(self, value):
        """Convert empty strings to None for proper MongoDB handling"""
        return None if value == '' else value


class ContentPreferencesSerializer(serializers.Serializer):
    """Serializer for content filtering preferences"""
    
    preferred_platforms = serializers.ListField(
        child=serializers.ChoiceField(choices=ContentPreferences.PLATFORM_CHOICES),
        required=False,
        default=list
    )
    content_types = serializers.ListField(
        child=serializers.ChoiceField(choices=ContentPreferences.CONTENT_TYPES),
        required=False,
        default=list
    )
    difficulty_preference = serializers.ChoiceField(
        choices=ContentPreferences.DIFFICULTY_CHOICES,
        required=False,
        default='mixed'
    )
    duration_preference = serializers.ChoiceField(
        choices=ContentPreferences.DURATION_CHOICES,
        required=False,
        default='mixed'
    )
    language_preference = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=False,
        default=['english', 'hindi']
    )
    instructor_ratings_min = serializers.FloatField(
        min_value=0.0,
        max_value=5.0,
        required=False,
        default=3.0
    )

    def validate_preferred_platforms(self, value):
        """
        TEMPORARY FIX: Filter out platforms not supported by current MongoDB schema validation.

        This is a defensive measure to prevent MongoDB validation errors while the database
        schema is updated to match the full MongoEngine model choices.

        TODO: Remove this filtering once MongoDB schema is updated to include all platforms
        """
        import logging
        logger = logging.getLogger(__name__)

        # MongoDB schema currently only allows these platforms (discovered from error logs)
        mongodb_allowed_platforms = [
            'udemy', 'coursera', 'youtube', 'edx', 'khan_academy',
            'pluralsight', 'linkedin_learning'
        ]

        # Filter to only allowed platforms
        filtered_platforms = [p for p in value if p in mongodb_allowed_platforms]
        removed_platforms = [p for p in value if p not in mongodb_allowed_platforms]

        if removed_platforms:
            logger.warning(f"🔧 FILTERING unsupported platforms due to MongoDB schema restriction: {removed_platforms}")
            logger.warning(f"💡 Original platforms: {value}")
            logger.warning(f"✅ Filtered platforms: {filtered_platforms}")
            logger.warning(f"📋 TODO: Update MongoDB schema to include all {len(ContentPreferences.PLATFORM_CHOICES)} platforms from model")

        return filtered_platforms


class AIInsightsSerializer(serializers.Serializer):
    """Serializer for AI-generated user insights"""
    
    learning_patterns = serializers.DictField(required=False, default=dict)
    strength_areas = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )
    improvement_areas = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )
    recommended_paths = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    updated_at = serializers.DateTimeField(read_only=True)


class InteractionDataSerializer(serializers.Serializer):
    """Serializer for user interaction data"""
    
    type = serializers.ChoiceField(choices=InteractionData.INTERACTION_TYPES)
    data = serializers.DictField(default=dict)
    timestamp = serializers.DateTimeField(read_only=True)
    context = serializers.DictField(default=dict)


class UserPreferenceSerializer(serializers.Serializer):
    """Main serializer for user preferences"""
    
    user_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    basic_info = BasicInfoSerializer(required=False)
    content_preferences = ContentPreferencesSerializer(required=False)
    ai_insights = AIInsightsSerializer(read_only=True)
    interactions = InteractionDataSerializer(many=True, read_only=True)
    custom_preferences = serializers.DictField(required=False, default=dict)
    
    def create(self, validated_data):
        """Create a new user preference document"""
        user_id = self.context['request'].user.id

        # Extract nested data
        basic_info_data = validated_data.pop('basic_info', {})
        content_prefs_data = validated_data.pop('content_preferences', {})
        custom_prefs = validated_data.pop('custom_preferences', {})

        # Create main UserPreference document
        preference = UserPreference.create_for_user(user_id, basic_info_data)

        # Initialize domain models if they don't exist
        preference.initialize_domain_models()

        # Update content preferences in the appropriate domain model
        if content_prefs_data:
            try:
                from apps.learning_content.models import UserContentProfile, ContentPreferences
                content_profile = UserContentProfile.get_by_user_id(user_id)
                if not content_profile:
                    content_profile = UserContentProfile.create_for_user(user_id, content_prefs_data)
                else:
                    content_profile.content_preferences = ContentPreferences(**content_prefs_data)
                    content_profile.save()
            except ImportError:
                # Fallback - store in ui_preferences
                preference.ui_preferences['content_preferences'] = content_prefs_data

        # Store custom preferences
        preference.ui_preferences.update(custom_prefs)
        preference.save()

        return preference
    
    def update(self, instance, validated_data):
        """Update existing user preference document"""

        # Update basic info
        if 'basic_info' in validated_data:
            basic_info_data = validated_data.pop('basic_info')
            instance.update_basic_info(basic_info_data)

        # Update content preferences in the appropriate domain model
        if 'content_preferences' in validated_data:
            content_prefs_data = validated_data.pop('content_preferences')
            try:
                from apps.learning_content.models import UserContentProfile, ContentPreferences
                content_profile = UserContentProfile.get_by_user_id(instance.user_id)
                if not content_profile:
                    content_profile = UserContentProfile.create_for_user(instance.user_id, content_prefs_data)
                else:
                    if not content_profile.content_preferences:
                        content_profile.content_preferences = ContentPreferences()
                    for key, value in content_prefs_data.items():
                        setattr(content_profile.content_preferences, key, value)
                    content_profile.save()
            except ImportError:
                # Fallback - store in ui_preferences
                if 'content_preferences' not in instance.ui_preferences:
                    instance.ui_preferences['content_preferences'] = {}
                instance.ui_preferences['content_preferences'].update(content_prefs_data)

        # Update custom preferences
        if 'custom_preferences' in validated_data:
            custom_prefs = validated_data.pop('custom_preferences')
            instance.ui_preferences.update(custom_prefs)

        # Update other fields
        for key, value in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        instance.save()
        return instance
    
    def to_representation(self, instance):
        """Convert MongoDB document to JSON representation"""
        if instance is None:
            return None

        # Build the base data structure using our refactored model
        data = {
            'user_id': instance.user_id,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'custom_preferences': instance.ui_preferences or {},

            # Onboarding and profile completion fields
            'profile_completion_percentage': instance.profile_completeness or 0.0,
            'last_active': instance.last_active,
        }

        # Onboarding status from embedded document
        if instance.onboarding_status:
            data['onboarding_status'] = 'full_completed' if instance.onboarding_status.completed else 'not_started'
            data['onboarding_completed'] = instance.onboarding_status.completed
            data['quick_onboarding_completed'] = instance.onboarding_status.completed  # Legacy compatibility
            data['onboarding_completed_at'] = instance.onboarding_status.completed_at
        else:
            data['onboarding_status'] = 'not_started'
            data['onboarding_completed'] = False
            data['quick_onboarding_completed'] = False
            data['onboarding_completed_at'] = None

        # Basic info (still embedded in preferences)
        if instance.basic_info:
            data['basic_info'] = BasicInfoSerializer(instance.basic_info).data
        else:
            data['basic_info'] = None

        # Content preferences (from domain model via compatibility property)
        if instance.content_preferences:
            data['content_preferences'] = ContentPreferencesSerializer(instance.content_preferences).data
        else:
            data['content_preferences'] = None

        # AI insights (from analytics domain via compatibility property)
        if instance.ai_insights:
            data['ai_insights'] = AIInsightsSerializer(instance.ai_insights).data
        else:
            data['ai_insights'] = None

        # Recent interactions (from analytics domain via compatibility method)
        try:
            recent_interactions = instance.get_recent_interactions(days=30)[:50]
            data['interactions'] = InteractionDataSerializer(recent_interactions, many=True).data
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error serializing interactions for user {instance.user_id}: {str(e)}")
            data['interactions'] = []

        return data


class OnboardingSerializer(serializers.Serializer):
    """Serializer for onboarding data collection"""
    
    # Step 1: Goals and interests
    learning_goals = serializers.ListField(
        child=serializers.CharField(max_length=50),
        min_length=1,
        help_text="What do you want to learn?"
    )
    
    # Step 2: Experience level
    experience_level = serializers.ChoiceField(
        choices=BasicInfo.EXPERIENCE_CHOICES,
        help_text="Your current experience level"
    )
    
    # Step 3: Learning preferences
    preferred_pace = serializers.ChoiceField(
        choices=BasicInfo.PACE_CHOICES,
        help_text="How fast do you want to learn?"
    )
    
    time_availability = serializers.ChoiceField(
        choices=BasicInfo.TIME_CHOICES,
        help_text="How much time can you dedicate daily?"
    )
    
    learning_style = serializers.ListField(
        child=serializers.ChoiceField(choices=BasicInfo.STYLE_CHOICES),
        min_length=1,
        help_text="How do you prefer to learn?"
    )
    
    # Step 4: Career information
    career_stage = serializers.ChoiceField(
        choices=BasicInfo.CAREER_CHOICES,
        help_text="What's your career stage?"
    )
    
    target_timeline = serializers.ChoiceField(
        choices=BasicInfo.TIMELINE_CHOICES,
        help_text="When do you want to achieve your goals?"
    )
    
    # Step 5: Content preferences
    preferred_platforms = serializers.ListField(
        child=serializers.ChoiceField(choices=ContentPreferences.PLATFORM_CHOICES),
        required=False,
        default=list,
        help_text="Which platforms do you prefer?"
    )
    
    content_types = serializers.ListField(
        child=serializers.ChoiceField(choices=ContentPreferences.CONTENT_TYPES),
        required=False,
        default=list,
        help_text="What type of content do you prefer?"
    )
    
    language_preference = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=False,
        default=['english', 'hindi'],
        help_text="Preferred languages for content"
    )
    
    def create(self, validated_data):
        """Create user preferences from onboarding data"""
        import logging
        logger = logging.getLogger(__name__)

        user_id = self.context['request'].user.id
        logger.info(f"🚀 Starting onboarding creation for user {user_id}")

        # Split data into basic_info and content_preferences
        basic_info_fields = [
            'learning_goals', 'experience_level', 'preferred_pace',
            'time_availability', 'learning_style', 'career_stage', 'target_timeline'
        ]

        content_prefs_fields = [
            'preferred_platforms', 'content_types', 'language_preference'
        ]

        basic_info_data = {k: v for k, v in validated_data.items() if k in basic_info_fields}
        content_prefs_data = {k: v for k, v in validated_data.items() if k in content_prefs_fields}

        logger.debug(f"📝 Basic info fields count: {len([k for k, v in basic_info_data.items() if v])}")
        logger.debug(f"🎯 Content preferences fields count: {len([k for k, v in content_prefs_data.items() if v])}")

        # Get or create user preference (handle re-completion for incomplete records)
        existing_preference = UserPreference.get_by_user_id(user_id)

        if existing_preference and not existing_preference.is_onboarding_truly_complete():
            # Update existing incomplete record
            logger.info(f"🔄 Updating existing incomplete preferences for user {user_id}")
            preference = existing_preference

            # Update basic_info with new data
            if not preference.basic_info:
                preference.basic_info = BasicInfo()

            # Update basic_info fields
            for field, value in basic_info_data.items():
                if value:  # Only update non-empty values
                    setattr(preference.basic_info, field, value)

        else:
            # Create new preference (should not happen due to view logic, but safety net)
            logger.info(f"📝 Creating new preferences for user {user_id}")
            preference = UserPreference.create_for_user(user_id, basic_info_data)

        initial_completion = preference.calculate_profile_completion()
        logger.info(f"📊 Completion after updating basic info: {initial_completion:.1f}%")

        # Always create content preferences (required for complete onboarding)
        # If no content preferences data was provided, use defaults to ensure embedded document exists
        if not content_prefs_data:
            logger.info(f"📝 No content preferences provided, using defaults to ensure complete record")
            content_prefs_data = {
                'preferred_platforms': [],
                'content_types': [],
                'language_preference': ['english', 'hindi']
            }

        logger.debug(f"🎯 Creating content preferences with data: {content_prefs_data}")
        try:
            from apps.learning_content.models import ContentPreferences as DomainContentPreferences
            preference.content_preferences = DomainContentPreferences(**content_prefs_data)
        except ImportError:
            # Fallback - store in ui_preferences if domain model unavailable
            preference.ui_preferences['content_preferences'] = content_prefs_data
        content_completion = preference.calculate_profile_completion()
        logger.info(f"📈 Completion after content preferences: {content_completion:.1f}%")

        # Mark full onboarding as completed
        preference.mark_onboarding_completed('full')
        onboarding_completion = preference.calculate_profile_completion()
        logger.info(f"✅ Completion after marking onboarding complete: {onboarding_completion:.1f}%")

        # Log onboarding completion (using allowed interaction type)
        preference.add_interaction(
            'page_view',  # Use 'page_view' instead of 'onboarding_flow_completed' for MongoDB compatibility
            {'page': 'onboarding_complete', 'action': 'onboarding_flow_completed'},
            {'source': 'onboarding_flow'}
        )

        # Explicitly ensure completion percentage is recalculated with all onboarding data
        # This guarantees the completion percentage reflects the full onboarding state
        preference.update_completion_percentage(save_now=False)
        final_completion = preference.calculate_profile_completion()
        logger.info(f"🎯 Final completion percentage: {final_completion:.1f}%")

        # Final save to ensure all data (content preferences, interactions) is persisted
        preference.save()
        saved_completion = preference.profile_completion_percentage
        logger.info(f"💾 Saved completion percentage: {saved_completion:.1f}%")

        logger.info(f"🎉 Onboarding creation completed for user {user_id}")
        return preference


class InteractionLogSerializer(serializers.Serializer):
    """Serializer for logging user interactions"""
    
    type = serializers.ChoiceField(choices=InteractionData.INTERACTION_TYPES)
    data = serializers.DictField(default=dict)
    context = serializers.DictField(default=dict, required=False)
    
    def create(self, validated_data):
        """Log an interaction for the current user"""
        user_id = self.context['request'].user.id
        
        # Get or create user preferences
        preference = UserPreference.get_by_user_id(user_id)
        if not preference:
            preference = UserPreference.create_for_user(user_id)
        
        # Add interaction
        preference.add_interaction(
            validated_data['type'],
            validated_data['data'],
            validated_data.get('context', {})
        )
        
        # Get timestamp safely from the last interaction
        last_interaction_timestamp = None
        if preference.interactions:
            last_interaction_timestamp = UserPreference.safe_get_interaction_field(
                preference.interactions[-1], 'timestamp'
            )

        return {
            'success': True,
            'interaction_type': validated_data['type'],
            'timestamp': last_interaction_timestamp
        }


class RecommendationItemSerializer(serializers.Serializer):
    """Serializer for individual course recommendations"""
    
    course_id = serializers.CharField(max_length=200)
    platform = serializers.CharField(max_length=50)
    title = serializers.CharField(max_length=300)
    score = serializers.FloatField(min_value=0.0, max_value=1.0)
    reasoning = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list
    )
    metadata = serializers.DictField(default=dict)


class CourseRecommendationSerializer(serializers.Serializer):
    """Serializer for course recommendations"""
    
    user_id = serializers.IntegerField(read_only=True)
    generated_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    algorithm_version = serializers.CharField(read_only=True)
    recommendations = RecommendationItemSerializer(many=True, read_only=True)
    
    def to_representation(self, instance):
        """Convert MongoDB document to JSON"""
        if instance is None:
            return None
        
        return {
            'user_id': instance.user_id,
            'generated_at': instance.generated_at,
            'expires_at': instance.expires_at,
            'algorithm_version': instance.algorithm_version,
            'is_expired': instance.is_expired,
            'recommendations': RecommendationItemSerializer(
                instance.recommendations, many=True
            ).data
        }


class UserAnalyticsSerializer(serializers.Serializer):
    """Serializer for user analytics and insights"""
    
    total_interactions = serializers.IntegerField(read_only=True)
    recent_activity_count = serializers.IntegerField(read_only=True)
    learning_streak_days = serializers.IntegerField(read_only=True)
    preferred_learning_times = serializers.ListField(read_only=True)
    top_interests = serializers.ListField(read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    
    def to_representation(self, user_preference):
        """Generate analytics from user preference data"""
        if not user_preference:
            return {
                'total_interactions': 0,
                'recent_activity_count': 0,
                'learning_streak_days': 0,
                'preferred_learning_times': [],
                'top_interests': [],
                'completion_rate': 0.0
            }
        
        # Calculate analytics
        total_interactions = len(user_preference.interactions)
        recent_interactions = user_preference.get_recent_interactions(days=7)
        recent_activity_count = len(recent_interactions)
        
        # Extract learning goals as top interests
        top_interests = []
        if user_preference.basic_info and user_preference.basic_info.learning_goals:
            top_interests = user_preference.basic_info.learning_goals[:5]
        
        # Calculate completion rate from interactions (using safe access)
        completion_interactions = [
            i for i in user_preference.interactions
            if UserPreference.safe_get_interaction_field(i, 'type') == 'course_complete'
        ]
        enrolled_interactions = [
            i for i in user_preference.interactions
            if UserPreference.safe_get_interaction_field(i, 'type') == 'course_enroll'
        ]
        
        completion_rate = 0.0
        if enrolled_interactions:
            completion_rate = len(completion_interactions) / len(enrolled_interactions)
        
        return {
            'total_interactions': total_interactions,
            'recent_activity_count': recent_activity_count,
            'learning_streak_days': 0,  # TODO: Calculate actual streak
            'preferred_learning_times': [],  # TODO: Analyze interaction timestamps
            'top_interests': top_interests,
            'completion_rate': round(completion_rate, 2)
        }