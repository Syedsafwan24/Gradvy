"""
Serializers for user preferences and MongoDB data.
Converts between MongoDB documents and REST API JSON.
"""
from rest_framework import serializers
from typing import Dict, List, Any
from .models import (
    UserPreference, BasicInfo, ContentPreferences, AIInsights,
    InteractionData, LearningSession, CourseRecommendation,
    AITrainingData, RecommendationItem
)


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
        required=False
    )
    target_timeline = serializers.ChoiceField(
        choices=BasicInfo.TIMELINE_CHOICES,
        required=False
    )


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
        default=['english']
    )
    instructor_ratings_min = serializers.FloatField(
        min_value=0.0,
        max_value=5.0,
        required=False,
        default=3.0
    )


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
        
        # Create MongoDB document
        preference = UserPreference(
            user_id=user_id,
            custom_preferences=custom_prefs
        )
        
        # Add nested objects if provided
        if basic_info_data:
            preference.basic_info = BasicInfo(**basic_info_data)
        
        if content_prefs_data:
            preference.content_preferences = ContentPreferences(**content_prefs_data)
        
        preference.save()
        return preference
    
    def update(self, instance, validated_data):
        """Update existing user preference document"""
        
        # Update basic info
        if 'basic_info' in validated_data:
            basic_info_data = validated_data.pop('basic_info')
            if not instance.basic_info:
                instance.basic_info = BasicInfo()
            
            for key, value in basic_info_data.items():
                setattr(instance.basic_info, key, value)
        
        # Update content preferences
        if 'content_preferences' in validated_data:
            content_prefs_data = validated_data.pop('content_preferences')
            if not instance.content_preferences:
                instance.content_preferences = ContentPreferences()
            
            for key, value in content_prefs_data.items():
                setattr(instance.content_preferences, key, value)
        
        # Update other fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """Convert MongoDB document to JSON representation"""
        if instance is None:
            return None
        
        data = {
            'user_id': instance.user_id,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'custom_preferences': instance.custom_preferences,
            
            # Onboarding and Profile Completion Fields (CRITICAL!)
            'onboarding_completed': instance.onboarding_completed,
            'profile_completion_percentage': instance.profile_completion_percentage,
            'onboarding_completed_at': instance.onboarding_completed_at,
            'last_completion_prompt_shown': instance.last_completion_prompt_shown,
            'completion_prompt_dismissed_count': instance.completion_prompt_dismissed_count,
            
            # Quick onboarding fields
            'quick_onboarding_completed': instance.quick_onboarding_completed,
            'quick_onboarding_data': instance.quick_onboarding_data,
            
            # Gamification fields
            'achievement_badges': instance.achievement_badges,
            'completion_milestones': instance.completion_milestones,
            'streak_data': instance.streak_data,
        }
        
        # Serialize nested objects
        if instance.basic_info:
            data['basic_info'] = BasicInfoSerializer(instance.basic_info).data
        
        if instance.content_preferences:
            data['content_preferences'] = ContentPreferencesSerializer(instance.content_preferences).data
        
        if instance.ai_insights:
            data['ai_insights'] = AIInsightsSerializer(instance.ai_insights).data
        
        # Recent interactions (limit to last 50 for performance)
        recent_interactions = instance.get_recent_interactions(days=30)[:50]
        data['interactions'] = InteractionDataSerializer(recent_interactions, many=True).data
        
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
        default=['english'],
        help_text="Preferred languages for content"
    )
    
    def create(self, validated_data):
        """Create user preferences from onboarding data"""
        user_id = self.context['request'].user.id
        
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
        
        # Create user preference
        preference = UserPreference.create_for_user(user_id, basic_info_data)
        
        # Add content preferences
        if content_prefs_data:
            preference.content_preferences = ContentPreferences(**content_prefs_data)
            preference.save()
        
        # Log onboarding completion
        preference.add_interaction(
            'page_view',
            {'page': 'onboarding_complete'},
            {'source': 'onboarding_flow'}
        )
        
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
        
        return {
            'success': True,
            'interaction_type': validated_data['type'],
            'timestamp': preference.interactions[-1].timestamp
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
        
        # Calculate completion rate from interactions
        completion_interactions = [
            i for i in user_preference.interactions 
            if i.type == 'course_complete'
        ]
        enrolled_interactions = [
            i for i in user_preference.interactions 
            if i.type == 'course_enroll'
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