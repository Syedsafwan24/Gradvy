"""
backend/core/apps/analytics/models.py
User analytics and behavioral tracking models
Handles learning behavior analysis, interaction tracking, and AI insights
RELEVANT FILES: preferences/models.py, auth/models.py, ml_services/
"""

from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Any, Optional
from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    StringField, IntField, DateTimeField, ListField,
    DictField, FloatField, BooleanField, EmailField,
    ValidationError, DoesNotExist
)
from mongoengine.queryset.visitor import Q


class InteractionData(EmbeddedDocument):
    """Individual user interaction record"""

    # Type of interaction
    INTERACTION_TYPES = [
        'course_click', 'quiz_attempt', 'video_watch', 'search',
        'page_view', 'course_enroll', 'course_complete', 'bookmark',
        'rating_given', 'review_written', 'course_abandoned',
        'onboarding_started', 'onboarding_flow_completed'
    ]
    type = StringField(choices=INTERACTION_TYPES, required=True)

    # Interaction-specific data (flexible structure)
    data = DictField(default=dict)

    # Timestamp of interaction
    timestamp = DateTimeField(required=True, default=datetime.utcnow)

    # Context information
    context = DictField(default=dict)


class BehavioralPatterns(EmbeddedDocument):
    """Learning behavior analysis and patterns"""

    # Learning velocity metrics
    learning_velocity = FloatField(default=0.0)  # concepts per hour
    average_session_length = FloatField(default=0.0)  # minutes
    daily_consistency_score = FloatField(min_value=0.0, max_value=1.0, default=0.0)

    # Engagement patterns
    engagement_score = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    attention_span_minutes = FloatField(min_value=0.0, default=30.0)
    peak_activity_hours = ListField(IntField(min_value=0, max_value=23), default=list)
    preferred_session_duration = IntField(min_value=5, max_value=480, default=60)  # minutes

    # Content interaction patterns
    preferred_content_types = ListField(StringField(max_length=50), default=list)
    content_completion_rate = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    quiz_performance_trend = ListField(FloatField(), default=list)
    video_watch_patterns = DictField(default=dict)  # playback speed, skip patterns, etc.

    # Learning difficulties and strengths
    struggle_areas = ListField(StringField(max_length=100), default=list)
    strength_areas = ListField(StringField(max_length=100), default=list)
    help_seeking_frequency = FloatField(min_value=0.0, default=0.0)

    # Dropout risk analysis
    dropout_risk_score = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    warning_signals = ListField(StringField(max_length=100), default=list)
    intervention_history = ListField(DictField(), default=list)

    # Motivation and goal tracking
    goal_completion_rate = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    motivation_trend = ListField(FloatField(min_value=0.0, max_value=1.0), default=list)
    achievement_unlock_rate = FloatField(min_value=0.0, default=0.0)

    # Analysis metadata
    pattern_confidence = FloatField(min_value=0.0, max_value=1.0, default=0.5)
    last_analyzed = DateTimeField(default=datetime.utcnow)
    data_points_count = IntField(min_value=0, default=0)


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


class DeviceUsagePattern(EmbeddedDocument):
    """Device fingerprinting and usage pattern tracking"""

    # Device identification
    device_fingerprint = StringField(max_length=200)  # Hashed fingerprint
    device_type = StringField(max_length=20)  # desktop, mobile, tablet

    # Browser and OS information
    browser = StringField(max_length=50)
    browser_version = StringField(max_length=20)
    operating_system = StringField(max_length=50)
    os_version = StringField(max_length=20)

    # Screen and hardware info
    screen_resolution = StringField(max_length=20)  # e.g., "1920x1080"
    color_depth = IntField(min_value=1, max_value=64, default=24)
    timezone_offset = IntField(min_value=-12, max_value=14, default=0)

    # Usage patterns
    session_count = IntField(min_value=0, default=0)
    total_time_minutes = FloatField(min_value=0.0, default=0.0)
    average_session_length = FloatField(min_value=0.0, default=0.0)

    # Interaction patterns
    click_patterns = DictField(default=dict)  # click frequency, locations, etc.
    scroll_patterns = DictField(default=dict)  # scroll speed, distance, etc.
    keyboard_patterns = DictField(default=dict)  # typing speed, patterns

    # Performance metrics
    page_load_times = ListField(FloatField(), default=list)
    interaction_delays = ListField(FloatField(), default=list)
    error_frequency = FloatField(min_value=0.0, default=0.0)

    # Security and fraud detection
    suspicious_activity_score = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    bot_probability = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    proxy_detection = BooleanField(default=False)

    # Location approximation (privacy-safe)
    country_code = StringField(max_length=2)
    city_hash = StringField(max_length=200)  # Hashed for privacy
    isp_hash = StringField(max_length=200)  # Hashed ISP info

    # Tracking metadata
    first_seen = DateTimeField(default=datetime.utcnow)
    last_seen = DateTimeField(default=datetime.utcnow)
    data_collection_consent = BooleanField(default=True)


class UserAnalytics(Document):
    """
    Main analytics document linking to Django User model.
    Contains all user behavioral patterns and analytics data.
    """

    # Link to Django User model
    user_id = IntField(required=True, unique=True)

    # Timestamps
    created_at = DateTimeField(required=True, default=datetime.utcnow)
    updated_at = DateTimeField(required=True, default=datetime.utcnow)

    # Embedded analytics data
    behavioral_patterns = EmbeddedDocumentField(BehavioralPatterns)
    ai_insights = EmbeddedDocumentField(AIInsights)

    # User interactions array
    interactions = EmbeddedDocumentListField(InteractionData, default=list)

    # Device and context tracking
    device_patterns = EmbeddedDocumentListField(DeviceUsagePattern, default=list)

    # Analytics configuration
    analytics_enabled = BooleanField(default=True)
    data_collection_consent = BooleanField(default=True)

    meta = {
        'collection': 'user_analytics',
        'indexes': [
            'user_id',
            '-updated_at',
            'interactions.timestamp',
            'interactions.type',
            ('user_id', '-interactions.timestamp'),
            'behavioral_patterns.engagement_score',
            'behavioral_patterns.dropout_risk_score',
            'device_patterns.device_type',
            'ai_insights.updated_at',
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def add_interaction(self, interaction_type: str, data: Dict[str, Any], context: Dict[str, Any] = None):
        """Add a new interaction to the user's history"""
        if not self.data_collection_consent:
            return

        interaction = InteractionData(
            type=interaction_type,
            data=data,
            context=context or {},
            timestamp=datetime.utcnow()
        )
        self.interactions.append(interaction)

        # Update behavioral patterns if enabled
        if self.analytics_enabled:
            self._update_behavioral_patterns_from_interaction(interaction)

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

    def _update_behavioral_patterns_from_interaction(self, interaction: InteractionData):
        """Update behavioral patterns based on new interaction"""
        if not self.behavioral_patterns:
            self.behavioral_patterns = BehavioralPatterns()

        # Update engagement score based on interaction type
        engagement_weights = {
            'course_complete': 1.0,
            'quiz_attempt': 0.8,
            'video_watch': 0.6,
            'course_click': 0.4,
            'page_view': 0.2
        }

        weight = engagement_weights.get(interaction.type, 0.1)
        current_score = self.behavioral_patterns.engagement_score or 0.0

        # Exponential moving average
        alpha = 0.1
        self.behavioral_patterns.engagement_score = (alpha * weight) + ((1 - alpha) * current_score)
        self.behavioral_patterns.last_analyzed = datetime.utcnow()

    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional['UserAnalytics']:
        """Get user analytics by Django user ID"""
        try:
            return cls.objects.get(user_id=user_id)
        except DoesNotExist:
            return None

    @classmethod
    def create_for_user(cls, user_id: int) -> 'UserAnalytics':
        """Create new user analytics record"""
        analytics = cls(user_id=user_id)
        analytics.save()
        return analytics

    def __str__(self):
        return f"UserAnalytics(user_id={self.user_id})"
