"""
MongoDB models for user preferences and personalization data.
Uses MongoEngine for document modeling with validation.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    StringField, IntField, DateTimeField, ListField, 
    DictField, FloatField, BooleanField, EmailField,
    ValidationError, DoesNotExist
)
from mongoengine.queryset.visitor import Q


class BasicInfo(EmbeddedDocument):
    """User's basic learning preferences from onboarding"""
    
    # Learning goals - what they want to learn
    learning_goals = ListField(StringField(max_length=50), default=list)
    
    # Experience level
    EXPERIENCE_CHOICES = ['complete_beginner', 'some_basics', 'intermediate', 'advanced']
    experience_level = StringField(choices=EXPERIENCE_CHOICES)
    
    # Learning pace preference
    PACE_CHOICES = ['slow', 'medium', 'fast']
    preferred_pace = StringField(choices=PACE_CHOICES)
    
    # Time availability
    TIME_CHOICES = ['1-2hrs', '3-5hrs', '5+hrs']
    time_availability = StringField(choices=TIME_CHOICES)
    
    # Learning style preferences
    STYLE_CHOICES = ['visual', 'hands_on', 'reading', 'videos', 'interactive']
    learning_style = ListField(StringField(choices=STYLE_CHOICES), default=list)
    
    # Career stage
    CAREER_CHOICES = ['student', 'career_change', 'skill_upgrade', 'professional']
    career_stage = StringField(choices=CAREER_CHOICES)
    
    # Target timeline
    TIMELINE_CHOICES = ['3months', '6months', '1year', 'flexible']
    target_timeline = StringField(choices=TIMELINE_CHOICES)


class InteractionData(EmbeddedDocument):
    """Individual user interaction record"""
    
    # Type of interaction
    INTERACTION_TYPES = [
        'course_click', 'quiz_attempt', 'video_watch', 'search',
        'page_view', 'course_enroll', 'course_complete', 'bookmark',
        'rating_given', 'review_written', 'course_abandoned'
    ]
    type = StringField(choices=INTERACTION_TYPES, required=True)
    
    # Interaction-specific data (flexible structure)
    data = DictField(default=dict)
    
    # Timestamp of interaction
    timestamp = DateTimeField(required=True, default=datetime.utcnow)
    
    # Context information
    context = DictField(default=dict)


class AIInsights(EmbeddedDocument):
    """AI-generated insights about the user"""
    
    # Learning patterns discovered by AI
    learning_patterns = DictField(default=dict)
    
    # Identified strength areas
    strength_areas = ListField(StringField(max_length=100), default=list)
    
    # Areas that need improvement
    improvement_areas = ListField(StringField(max_length=100), default=list)
    
    # AI-recommended learning paths
    recommended_paths = ListField(DictField(), default=list)
    
    # When these insights were last updated
    updated_at = DateTimeField(default=datetime.utcnow)


class ContentPreferences(EmbeddedDocument):
    """User's content filtering preferences"""
    
    # Preferred learning platforms
    PLATFORM_CHOICES = [
        'udemy', 'coursera', 'youtube', 'edx', 'khan_academy', 
        'pluralsight', 'linkedin_learning', 'codecademy', 'freecodecamp'
    ]
    preferred_platforms = ListField(StringField(choices=PLATFORM_CHOICES), default=list)
    
    # Content type preferences  
    CONTENT_TYPES = ['video', 'article', 'interactive', 'quiz', 'project', 'book', 'podcast']
    content_types = ListField(StringField(choices=CONTENT_TYPES), default=list)
    
    # Difficulty preference
    DIFFICULTY_CHOICES = ['mixed', 'beginner', 'intermediate', 'advanced']
    difficulty_preference = StringField(choices=DIFFICULTY_CHOICES, default='mixed')
    
    # Duration preference
    DURATION_CHOICES = ['short', 'medium', 'long', 'mixed']
    duration_preference = StringField(choices=DURATION_CHOICES, default='mixed')
    
    # Language preferences
    language_preference = ListField(StringField(max_length=20), default=['english'])
    
    # Minimum instructor rating
    instructor_ratings_min = FloatField(min_value=0.0, max_value=5.0, default=3.0)


class UserPreference(Document):
    """
    Main user preference document storing all personalization data.
    Links to Django User model via user_id.
    """
    
    # Link to Django User model
    user_id = IntField(required=True, unique=True)
    
    # Timestamps
    created_at = DateTimeField(required=True, default=datetime.utcnow)
    updated_at = DateTimeField(required=True, default=datetime.utcnow)
    
    # Embedded documents for structured data
    basic_info = EmbeddedDocumentField(BasicInfo)
    content_preferences = EmbeddedDocumentField(ContentPreferences)
    ai_insights = EmbeddedDocumentField(AIInsights)
    
    # User interactions array
    interactions = EmbeddedDocumentListField(InteractionData, default=list)
    
    # Additional flexible data
    custom_preferences = DictField(default=dict)
    
    # Onboarding and Profile Completion Tracking
    onboarding_completed = BooleanField(default=False)
    profile_completion_percentage = FloatField(min_value=0.0, max_value=100.0, default=0.0)
    onboarding_completed_at = DateTimeField()
    last_completion_prompt_shown = DateTimeField()
    completion_prompt_dismissed_count = IntField(default=0)
    
    # Quick onboarding for new users
    quick_onboarding_completed = BooleanField(default=False)
    quick_onboarding_data = DictField(default=dict)
    
    # Gamification elements
    achievement_badges = ListField(StringField(max_length=50), default=list)
    completion_milestones = DictField(default=dict)
    streak_data = DictField(default=dict)
    
    # Metadata
    meta = {
        'collection': 'user_preferences',
        'indexes': [
            'user_id',
            '-updated_at',
            'basic_info.learning_goals',
            'interactions.timestamp'
        ]
    }
    
    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def add_interaction(self, interaction_type: str, data: Dict[str, Any], context: Dict[str, Any] = None):
        """Add a new interaction to the user's history"""
        interaction = InteractionData(
            type=interaction_type,
            data=data,
            context=context or {},
            timestamp=datetime.utcnow()
        )
        self.interactions.append(interaction)
        self.save()
    
    def get_recent_interactions(self, days: int = 30, interaction_type: str = None) -> List[InteractionData]:
        """Get recent interactions, optionally filtered by type"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent = [
            interaction for interaction in self.interactions
            if interaction.timestamp > cutoff_date
        ]
        
        if interaction_type:
            recent = [i for i in recent if i.type == interaction_type]
        
        return sorted(recent, key=lambda x: x.timestamp, reverse=True)
    
    def update_ai_insights(self, insights: Dict[str, Any]):
        """Update AI-generated insights"""
        if not self.ai_insights:
            self.ai_insights = AIInsights()
        
        for key, value in insights.items():
            if hasattr(self.ai_insights, key):
                setattr(self.ai_insights, key, value)
        
        self.ai_insights.updated_at = datetime.utcnow()
        self.save()
    
    def calculate_profile_completion(self) -> float:
        """Calculate profile completion percentage based on filled fields"""
        completion_score = 0.0
        total_weight = 100.0
        
        # Basic Info (40% weight)
        if self.basic_info:
            basic_score = 0
            basic_fields = [
                'learning_goals', 'experience_level', 'preferred_pace', 
                'time_availability', 'learning_style', 'career_stage', 'target_timeline'
            ]
            for field in basic_fields:
                field_value = getattr(self.basic_info, field, None)
                if field_value and (not isinstance(field_value, list) or len(field_value) > 0):
                    basic_score += 1
            completion_score += (basic_score / len(basic_fields)) * 40
        
        # Content Preferences (35% weight)
        if self.content_preferences:
            content_score = 0
            content_fields = [
                'preferred_platforms', 'content_types', 'difficulty_preference',
                'duration_preference', 'language_preference'
            ]
            for field in content_fields:
                field_value = getattr(self.content_preferences, field, None)
                if field_value and (not isinstance(field_value, list) or len(field_value) > 0):
                    content_score += 1
            completion_score += (content_score / len(content_fields)) * 35
        
        # Quick Onboarding (15% weight)
        if self.quick_onboarding_completed:
            completion_score += 15
        
        # Profile activity (10% weight)
        if len(self.interactions) > 0:
            completion_score += 10
        
        return min(completion_score, 100.0)
    
    def update_completion_percentage(self):
        """Update the stored completion percentage"""
        self.profile_completion_percentage = self.calculate_profile_completion()
        self.save()
    
    def mark_onboarding_completed(self):
        """Mark onboarding as completed and update completion time"""
        self.onboarding_completed = True
        self.onboarding_completed_at = datetime.utcnow()
        self.update_completion_percentage()
    
    def add_achievement_badge(self, badge_name: str):
        """Add an achievement badge to user's collection"""
        if badge_name not in self.achievement_badges:
            self.achievement_badges.append(badge_name)
            self.save()
    
    def should_show_completion_prompt(self, hours_interval: int = 24) -> bool:
        """Check if we should show completion prompt based on time and dismissal count"""
        if self.profile_completion_percentage >= 80.0:
            return False
        
        if self.completion_prompt_dismissed_count >= 3:
            return False
        
        if not self.last_completion_prompt_shown:
            return True
        
        time_diff = datetime.utcnow() - self.last_completion_prompt_shown
        return time_diff.total_seconds() > (hours_interval * 3600)
    
    def dismiss_completion_prompt(self):
        """Record that user dismissed the completion prompt"""
        self.last_completion_prompt_shown = datetime.utcnow()
        self.completion_prompt_dismissed_count += 1
        self.save()
    
    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional['UserPreference']:
        """Get user preferences by Django user ID"""
        try:
            return cls.objects.get(user_id=user_id)
        except DoesNotExist:
            return None
    
    @classmethod
    def create_for_user(cls, user_id: int, basic_info: Dict[str, Any] = None) -> 'UserPreference':
        """Create new user preference record"""
        preference = cls(user_id=user_id)
        
        if basic_info:
            preference.basic_info = BasicInfo(**basic_info)
        
        preference.save()
        return preference
    
    def __str__(self):
        return f"UserPreference(user_id={self.user_id})"


class ActivityData(EmbeddedDocument):
    """Individual learning activity within a session"""
    
    ACTIVITY_TYPES = [
        'course_view', 'video_watch', 'quiz_attempt', 
        'coding_practice', 'reading', 'discussion_post'
    ]
    activity_type = StringField(choices=ACTIVITY_TYPES, required=True)
    
    # Content identifier (course ID, video ID, etc.)
    content_id = StringField(max_length=200)
    
    # Duration in seconds
    duration = IntField(min_value=0)
    
    # Completion rate (0.0 to 1.0)
    completion_rate = FloatField(min_value=0.0, max_value=1.0)
    
    # Activity timestamp
    timestamp = DateTimeField(required=True, default=datetime.utcnow)
    
    # Additional activity-specific data
    metadata = DictField(default=dict)


class DeviceInfo(EmbeddedDocument):
    """Device information for session tracking"""
    
    DEVICE_TYPES = ['desktop', 'mobile', 'tablet']
    type = StringField(choices=DEVICE_TYPES)
    
    os = StringField(max_length=100)
    browser = StringField(max_length=100)


class LearningSession(Document):
    """
    Detailed learning session tracking for analytics and AI insights.
    """
    
    # Link to Django User
    user_id = IntField(required=True)
    
    # Unique session identifier
    session_id = StringField(required=True, unique=True, max_length=100)
    
    # Session timing
    start_time = DateTimeField(required=True, default=datetime.utcnow)
    end_time = DateTimeField()
    duration = IntField()  # Duration in seconds
    
    # Activities during the session
    activities = EmbeddedDocumentListField(ActivityData, default=list)
    
    # Device information
    device_info = EmbeddedDocumentField(DeviceInfo)
    
    # Session metadata
    session_data = DictField(default=dict)
    
    meta = {
        'collection': 'learning_sessions',
        'indexes': [
            'user_id',
            'session_id',
            ('user_id', '-start_time')
        ]
    }
    
    def end_session(self):
        """Mark session as ended and calculate duration"""
        if not self.end_time:
            self.end_time = datetime.utcnow()
            self.duration = int((self.end_time - self.start_time).total_seconds())
            self.save()
    
    def add_activity(self, activity_type: str, content_id: str, duration: int = 0, 
                    completion_rate: float = 0.0, metadata: Dict[str, Any] = None):
        """Add an activity to the session"""
        activity = ActivityData(
            activity_type=activity_type,
            content_id=content_id,
            duration=duration,
            completion_rate=completion_rate,
            metadata=metadata or {}
        )
        self.activities.append(activity)
        self.save()
    
    @property
    def total_activity_time(self) -> int:
        """Calculate total time spent on activities"""
        return sum(activity.duration or 0 for activity in self.activities)
    
    def __str__(self):
        return f"LearningSession({self.session_id}, user={self.user_id})"


class RecommendationItem(EmbeddedDocument):
    """Individual course recommendation"""
    
    course_id = StringField(required=True, max_length=200)
    platform = StringField(required=True, max_length=50)
    title = StringField(required=True, max_length=300)
    
    # Recommendation score (0.0 to 1.0)
    score = FloatField(required=True, min_value=0.0, max_value=1.0)
    
    # Reasons for recommendation
    reasoning = ListField(StringField(max_length=100), default=list)
    
    # Course metadata
    metadata = DictField(default=dict)


class CourseRecommendation(Document):
    """
    Cached personalized course recommendations for users.
    Generated by AI and cached for performance.
    """
    
    # Link to Django User
    user_id = IntField(required=True)
    
    # Generation timestamps
    generated_at = DateTimeField(required=True, default=datetime.utcnow)
    expires_at = DateTimeField(required=True)
    
    # Recommendation list
    recommendations = EmbeddedDocumentListField(RecommendationItem, default=list)
    
    # Algorithm version for tracking
    algorithm_version = StringField(default='1.0.0')
    
    # Generation context
    generation_context = DictField(default=dict)
    
    meta = {
        'collection': 'course_recommendations',
        'indexes': [
            'user_id',
            'expires_at'
        ]
    }
    
    @property
    def is_expired(self) -> bool:
        """Check if recommendations are expired"""
        return datetime.utcnow() > self.expires_at
    
    def get_top_recommendations(self, limit: int = 10) -> List[RecommendationItem]:
        """Get top N recommendations by score"""
        return sorted(self.recommendations, key=lambda x: x.score, reverse=True)[:limit]
    
    @classmethod
    def get_valid_recommendations(cls, user_id: int) -> Optional['CourseRecommendation']:
        """Get non-expired recommendations for user"""
        try:
            return cls.objects.get(
                user_id=user_id,
                expires_at__gt=datetime.utcnow()
            )
        except DoesNotExist:
            return None
    
    def __str__(self):
        return f"CourseRecommendation(user={self.user_id}, count={len(self.recommendations)})"


class AITrainingData(Document):
    """
    Training data collection for improving AI personalization.
    Stores user feedback and behavior patterns.
    """
    
    # Link to Django User
    user_id = IntField(required=True)
    
    # Event type
    EVENT_TYPES = [
        'positive_feedback', 'negative_feedback', 'course_completion',
        'course_abandonment', 'rating_given', 'bookmark_added',
        'share_action', 'search_refinement'
    ]
    event_type = StringField(choices=EVENT_TYPES, required=True)
    
    # Event timestamp
    timestamp = DateTimeField(required=True, default=datetime.utcnow)
    
    # Event-specific data
    event_data = DictField(default=dict)
    
    # User context at time of event
    user_context = DictField(default=dict)
    
    # Labels for supervised learning
    labels = DictField(default=dict)
    
    meta = {
        'collection': 'ai_training_data',
        'indexes': [
            'user_id',
            'event_type',
            ('user_id', '-timestamp'),
            ('event_type', '-timestamp')
        ]
    }
    
    @classmethod
    def log_event(cls, user_id: int, event_type: str, event_data: Dict[str, Any],
                  user_context: Dict[str, Any] = None, labels: Dict[str, Any] = None):
        """Log a training event"""
        training_data = cls(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            user_context=user_context or {},
            labels=labels or {}
        )
        training_data.save()
        return training_data
    
    def __str__(self):
        return f"AITrainingData({self.event_type}, user={self.user_id})"
