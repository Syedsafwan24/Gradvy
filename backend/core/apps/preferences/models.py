"""
MongoDB models for user preferences and personalization data.
Uses MongoEngine for document modeling with validation.
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


class SocialData(EmbeddedDocument):
    """Social media and professional profile data"""
    
    # LinkedIn data
    linkedin_profile = DictField(default=dict)
    linkedin_connections = IntField(min_value=0, default=0)
    professional_headline = StringField(max_length=200)
    industry = StringField(max_length=100)
    experience_years = IntField(min_value=0, default=0)
    education = ListField(DictField(), default=list)
    skills = ListField(StringField(max_length=50), default=list)
    certifications = ListField(DictField(), default=list)
    
    # GitHub data
    github_profile = DictField(default=dict)
    github_repos = IntField(min_value=0, default=0)
    github_followers = IntField(min_value=0, default=0)
    programming_languages = ListField(StringField(max_length=30), default=list)
    github_contributions = IntField(min_value=0, default=0)
    
    # Google data
    google_profile = DictField(default=dict)
    google_interests = ListField(StringField(max_length=50), default=list)
    
    # Social engagement metrics
    social_learning_score = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    peer_connections = IntField(min_value=0, default=0)
    mentor_relationships = ListField(StringField(max_length=100), default=list)
    
    # Data freshness
    last_updated = DateTimeField(default=datetime.utcnow)
    data_quality_score = FloatField(min_value=0.0, max_value=1.0, default=0.5)


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


class ConsentRecord(EmbeddedDocument):
    """Individual consent tracking record"""

    CONSENT_TYPES = [
        'essential', 'analytics', 'personalization', 'marketing',
        'social_data', 'behavioral_analysis', 'location_data',
        'device_fingerprinting', 'third_party_sharing'
    ]

    # Unique identifier for the consent record (useful for UI updates)
    record_id = StringField(max_length=64, default=lambda: uuid.uuid4().hex)

    # Either a single type or multiple types recorded together
    consent_type = StringField(choices=CONSENT_TYPES)
    consent_types = ListField(StringField(choices=CONSENT_TYPES), default=list)

    granted = BooleanField(default=False)
    granted_at = DateTimeField()
    updated_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()  # Optional expiration

    # Consent source and method
    consent_method = StringField(max_length=50, default='explicit')  # explicit, implicit, updated
    ip_address = StringField(max_length=45)  # IPv4 or IPv6
    user_agent = StringField(max_length=500)

    # Legal basis under GDPR
    LEGAL_BASIS_CHOICES = ['consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests']
    legal_basis = StringField(choices=LEGAL_BASIS_CHOICES, default='consent')

    # Additional metadata
    consent_version = StringField(max_length=20, default='1.0')
    withdrawal_reason = StringField(max_length=200)


class PrivacySettings(EmbeddedDocument):
    """User privacy preferences and settings"""
    
    # Data collection consent levels
    consent_records = EmbeddedDocumentListField(ConsentRecord, default=list)
    
    # Global privacy level
    PRIVACY_LEVELS = ['minimal', 'balanced', 'full']
    privacy_level = StringField(choices=PRIVACY_LEVELS, default='balanced')
    
    # Specific data collection settings
    allow_analytics = BooleanField(default=True)
    allow_personalization = BooleanField(default=True)
    allow_marketing = BooleanField(default=False)
    allow_social_data_collection = BooleanField(default=False)
    allow_behavioral_analysis = BooleanField(default=True)
    allow_location_tracking = BooleanField(default=False)
    allow_device_fingerprinting = BooleanField(default=True)
    allow_third_party_sharing = BooleanField(default=False)
    
    # Data retention preferences
    data_retention_months = IntField(min_value=1, max_value=60, default=24)
    auto_delete_inactive = BooleanField(default=True)
    delete_after_months = IntField(min_value=6, max_value=84, default=36)
    
    # Communication preferences
    email_notifications = BooleanField(default=True)
    sms_notifications = BooleanField(default=False)
    push_notifications = BooleanField(default=True)
    marketing_emails = BooleanField(default=False)
    
    # Data export and portability
    last_data_export = DateTimeField()
    export_format_preference = StringField(max_length=20, default='json')
    
    # Privacy control metadata
    data_minimization = BooleanField(default=True)
    pseudonymization_enabled = BooleanField(default=True)
    encryption_required = BooleanField(default=True)
    
    # GDPR compliance tracking
    gdpr_consent_date = DateTimeField()
    privacy_policy_version = StringField(max_length=20, default='1.0')
    terms_accepted_version = StringField(max_length=20, default='1.0')
    
    # Settings metadata
    last_updated = DateTimeField(default=datetime.utcnow)
    updated_by_user = BooleanField(default=True)


class ExternalDataSource(EmbeddedDocument):
    """External platform integration data"""
    
    PLATFORM_TYPES = [
        'linkedin', 'github', 'google', 'facebook', 'twitter', 
        'stackoverflow', 'medium', 'youtube', 'coursera', 'udemy'
    ]
    
    platform = StringField(choices=PLATFORM_TYPES, required=True)
    platform_user_id = StringField(max_length=200)
    platform_username = StringField(max_length=100)
    
    # Connection status
    connected = BooleanField(default=False)
    connection_date = DateTimeField()
    last_sync = DateTimeField()
    
    # OAuth tokens (encrypted)
    access_token_hash = StringField(max_length=500)  # Hashed for security
    refresh_token_hash = StringField(max_length=500)
    token_expires_at = DateTimeField()
    
    # Data collection permissions
    permissions_granted = ListField(StringField(max_length=50), default=list)
    data_types_collected = ListField(StringField(max_length=50), default=list)
    
    # Sync status and metrics
    sync_frequency_hours = IntField(min_value=1, max_value=168, default=24)
    successful_syncs = IntField(min_value=0, default=0)
    failed_syncs = IntField(min_value=0, default=0)
    last_sync_status = StringField(max_length=50, default='pending')
    
    # Collected data summary
    data_points_collected = IntField(min_value=0, default=0)
    data_quality_score = FloatField(min_value=0.0, max_value=1.0, default=0.5)
    
    # Privacy and consent
    data_collection_consent = BooleanField(default=True)
    data_sharing_consent = BooleanField(default=False)
    retention_period_months = IntField(min_value=1, max_value=60, default=24)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


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


class LocationRecord(EmbeddedDocument):
    """Privacy-compliant location data for personalization"""
    
    # Coarse location (GDPR compliant)
    country_code = StringField(max_length=2)
    region_code = StringField(max_length=10)  # state/province
    city_name = StringField(max_length=100)
    timezone = StringField(max_length=50)
    
    # Coordinates (if explicitly consented, rounded for privacy)
    latitude_rounded = FloatField()  # Rounded to ~1km precision
    longitude_rounded = FloatField()  # Rounded to ~1km precision
    
    # Usage context
    location_type = StringField(max_length=20, default='home')  # home, work, travel, etc.
    usage_frequency = IntField(min_value=0, default=1)
    
    # Learning context
    preferred_content_languages = ListField(StringField(max_length=10), default=list)
    local_time_preferences = DictField(default=dict)  # preferred learning hours
    
    # Privacy controls
    precision_level = StringField(max_length=20, default='city')  # city, region, country
    sharing_consent = BooleanField(default=False)
    retention_days = IntField(min_value=1, max_value=365, default=90)
    
    # Collection metadata
    collected_at = DateTimeField(default=datetime.utcnow)
    collection_method = StringField(max_length=50)  # ip_geolocation, gps, manual
    accuracy_meters = FloatField(min_value=0.0)  # GPS accuracy if applicable
    
    # Compliance and consent
    gdpr_lawful_basis = StringField(max_length=50, default='consent')
    explicit_consent = BooleanField(default=False)
    consent_timestamp = DateTimeField()


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
    
    # Enhanced personalization data
    social_data = EmbeddedDocumentField(SocialData)
    behavioral_patterns = EmbeddedDocumentField(BehavioralPatterns)
    
    # Privacy and consent management
    privacy_settings = EmbeddedDocumentField(PrivacySettings)
    consent_history = EmbeddedDocumentListField(ConsentRecord, default=list)
    
    # External data integration
    external_data_sources = EmbeddedDocumentListField(ExternalDataSource, default=list)
    
    # Device and context tracking
    device_patterns = EmbeddedDocumentListField(DeviceUsagePattern, default=list)
    location_history = EmbeddedDocumentListField(LocationRecord, default=list)
    
    # Additional flexible data
    custom_preferences = DictField(default=dict)
    feature_flags = DictField(default=dict)  # For A/B testing and gradual rollouts
    
    # Onboarding Status Tracking (unified approach)
    ONBOARDING_STATUS_CHOICES = ['not_started', 'quick_completed', 'full_completed']
    onboarding_status = StringField(choices=ONBOARDING_STATUS_CHOICES, default='not_started')
    profile_completion_percentage = FloatField(min_value=0.0, max_value=100.0, default=0.0)
    onboarding_completed_at = DateTimeField()
    last_completion_prompt_shown = DateTimeField()
    completion_prompt_dismissed_count = IntField(default=0)
    
    # Quick onboarding data storage
    quick_onboarding_data = DictField(default=dict)
    
    # Gamification elements
    achievement_badges = ListField(StringField(max_length=50), default=list)
    completion_milestones = DictField(default=dict)
    streak_data = DictField(default=dict)
    
    # Metadata with comprehensive indexing strategy
    meta = {
        'collection': 'user_preferences',
        'indexes': [
            # Primary indexes
            'user_id',
            '-updated_at',
            
            # Basic info indexes
            'basic_info.learning_goals',
            'basic_info.experience_level',
            ('basic_info.experience_level', 'basic_info.learning_goals'),
            
            # Interaction indexes
            'interactions.timestamp',
            'interactions.type',
            ('user_id', '-interactions.timestamp'),
            
            # Behavioral pattern indexes
            'behavioral_patterns.engagement_score',
            'behavioral_patterns.dropout_risk_score',
            'behavioral_patterns.preferred_content_types',
            
            # Privacy and consent indexes
            'privacy_settings.allow_personalization',
            'privacy_settings.allow_behavioral_analysis',
            'consent_history.granted_at',
            
            # External data indexes
            'external_data_sources.platform',
            'external_data_sources.last_sync',
            
            # Device and location indexes
            'device_patterns.device_type',
            'location_history.country_code',
            
            # AI insights indexes
            'ai_insights.updated_at',
            
            # Compound indexes for complex queries
            ('basic_info.learning_goals', 'behavioral_patterns.engagement_score'),
            ('privacy_settings.allow_personalization', 'behavioral_patterns.dropout_risk_score'),
            
            # Text search index - requires proper setup
            # ('basic_info.learning_goals', 'text'),  # Commented out - needs proper text index setup
            
            # TTL indexes for data retention
            # ('interactions.timestamp', {'expireAfterSeconds': 31536000}),  # 1 year - commented out for now
            # ('external_data_sources.expires_at', 1, {'expireAfterSeconds': 0}),  # Commented out - no expires_at field
        ]
    }
    
    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def add_interaction(self, interaction_type: str, data: Dict[str, Any], context: Dict[str, Any] = None):
        """Add a new interaction to the user's history with enhanced privacy-aware tracking"""
        # Check privacy consent before storing detailed interaction data
        if not self.privacy_settings or not self.privacy_settings.allow_analytics:
            # Store minimal interaction data without detailed tracking
            data = {'type': interaction_type, 'timestamp': datetime.utcnow().isoformat()}
            context = {'consent_limited': True}
        
        interaction = InteractionData(
            type=interaction_type,
            data=data,
            context=context or {},
            timestamp=datetime.utcnow()
        )
        self.interactions.append(interaction)
        
        # Update behavioral patterns if consent given
        if self.privacy_settings and self.privacy_settings.allow_behavioral_analysis:
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
        """Update AI-generated insights with privacy checks"""
        # Check if user consented to AI insights
        if not self.privacy_settings or not self.privacy_settings.allow_personalization:
            return
        
        if not self.ai_insights:
            self.ai_insights = AIInsights()
        
        for key, value in insights.items():
            if hasattr(self.ai_insights, key):
                setattr(self.ai_insights, key, value)
        
        self.ai_insights.updated_at = datetime.utcnow()
        self.save()
    
    def calculate_profile_completion(self) -> float:
        """Calculate profile completion percentage based on filled fields and onboarding status"""
        completion_score = 0.0
        
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
        
        # Onboarding Status (15% weight)
        if self.onboarding_status == 'quick_completed':
            completion_score += 10  # Partial points for quick onboarding
        elif self.onboarding_status == 'full_completed':
            completion_score += 15  # Full points for complete onboarding
        
        # Profile activity (10% weight)
        if len(self.interactions) > 0:
            completion_score += 10
        
        return min(completion_score, 100.0)
    
    def update_completion_percentage(self):
        """Update the stored completion percentage"""
        self.profile_completion_percentage = self.calculate_profile_completion()
        self.save()
    
    def mark_onboarding_completed(self, onboarding_type='full'):
        """Mark onboarding as completed and update completion time"""
        if onboarding_type == 'quick':
            self.onboarding_status = 'quick_completed'
        else:
            self.onboarding_status = 'full_completed'
        self.onboarding_completed_at = datetime.utcnow()
        self.update_completion_percentage()
    
    def add_achievement_badge(self, badge_name: str):
        """Add an achievement badge to user's collection"""
        if badge_name not in self.achievement_badges:
            self.achievement_badges.append(badge_name)
            self.save()
    
    def should_show_completion_prompt(self, hours_interval: int = 24) -> bool:
        """Check if we should show completion prompt based on onboarding status and dismissal count"""
        # Don't show prompts if onboarding is fully completed
        if self.onboarding_status == 'full_completed':
            return False
        
        # Don't show prompts if profile is sufficiently complete
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
    
    def record_consent(self, consent_types: List[str], ip_address: str = None, user_agent: str = None):
        """Record user consent for GDPR compliance"""
        consent_record = ConsentRecord(
            consent_types=consent_types,
            granted=True,
            granted_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.consent_history.append(consent_record)
        
        # Update privacy settings based on consent
        if not self.privacy_settings:
            self.privacy_settings = PrivacySettings()
        
        # Map consent types to privacy settings
        consent_mapping = {
            'analytics': 'allow_analytics',
            'personalization': 'allow_personalization',
            'marketing': 'allow_marketing',
            'social_data': 'allow_social_data_collection',
            'behavioral_analysis': 'allow_behavioral_analysis',
            'third_party_sharing': 'allow_third_party_sharing',
            'location_data': 'allow_location_tracking',
            'device_fingerprinting': 'allow_device_fingerprinting',
        }
        
        for consent_type in consent_types:
            if consent_type in consent_mapping:
                setattr(self.privacy_settings, consent_mapping[consent_type], True)
        
        self.privacy_settings.last_updated = datetime.utcnow()
        self.save()

    def record_consent_change(self, consent_type: str, granted: bool, ip_address: str = None,
                              user_agent: str = None, consent_version: str = '1.0'):
        """Record a change for a single consent type and update flags"""
        change = ConsentRecord(
            consent_type=consent_type,
            consent_types=[consent_type],
            granted=granted,
            granted_at=datetime.utcnow() if granted else None,
            updated_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            consent_version=consent_version,
        )

        self.consent_history.append(change)

        # Ensure privacy settings exists
        if not self.privacy_settings:
            self.privacy_settings = PrivacySettings()

        # Map to setting field
        mapping = {
            'analytics': 'allow_analytics',
            'personalization': 'allow_personalization',
            'marketing': 'allow_marketing',
            'social_data': 'allow_social_data_collection',
            'behavioral_analysis': 'allow_behavioral_analysis',
            'third_party_sharing': 'allow_third_party_sharing',
            'location_data': 'allow_location_tracking',
            'device_fingerprinting': 'allow_device_fingerprinting',
        }
        if consent_type in mapping:
            setattr(self.privacy_settings, mapping[consent_type], granted)

        self.privacy_settings.last_updated = datetime.utcnow()
        self.save()
    
    def add_external_data(self, source_type: str, source_id: str, data_content: Dict[str, Any], 
                         confidence_score: float = 0.5, expires_in_days: int = 30):
        """Add external data source with privacy checks"""
        if not self.privacy_settings or not self.privacy_settings.allow_third_party_sharing:
            return False
        
        external_data = ExternalDataSource(
            platform=source_type,
            platform_user_id=source_id,
            data_quality_score=confidence_score,
            last_sync=datetime.utcnow(),
            data_collection_consent=True
        )
        
        # Remove existing data from same source
        self.external_data_sources = [
            source for source in self.external_data_sources 
            if not (source.platform == source_type and source.platform_user_id == source_id)
        ]
        
        self.external_data_sources.append(external_data)
        self.save()
        return True
    
    def update_device_pattern(self, device_info: Dict[str, Any]):
        """Update or create device usage pattern"""
        device_id = self._generate_device_id(device_info)
        
        # Find existing device pattern
        existing_pattern = None
        for pattern in self.device_patterns:
            if pattern.device_id == device_id:
                existing_pattern = pattern
                break
        
        if existing_pattern:
            existing_pattern.update_last_seen()
        else:
            new_pattern = DeviceUsagePattern(
                device_type=device_info.get('device_type'),
                device_id=device_id,
                operating_system=device_info.get('os'),
                browser=device_info.get('browser'),
                screen_resolution=device_info.get('screen_resolution')
            )
            self.device_patterns.append(new_pattern)
        
        self.save()
    
    def update_location(self, location_info: Dict[str, Any]):
        """Update location history with privacy checks"""
        if not self.privacy_settings or not self.privacy_settings.location_tracking:
            return
        
        ip_hash = self._hash_ip(location_info.get('ip_address', ''))
        
        # Check if this location already exists
        existing_location = None
        for location in self.location_history:
            if (location.country == location_info.get('country') and 
                location.city == location_info.get('city')):
                existing_location = location
                break
        
        if existing_location:
            existing_location.update_detection()
        else:
            new_location = LocationRecord(
                country=location_info.get('country'),
                city=location_info.get('city'),
                region=location_info.get('region'),
                timezone=location_info.get('timezone'),
                ip_address_hash=ip_hash,
                accuracy_level=location_info.get('accuracy_level', 'city')
            )
            self.location_history.append(new_location)
        
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
    
    def _generate_device_id(self, device_info: Dict[str, Any]) -> str:
        """Generate anonymous device identifier"""
        device_string = f"{device_info.get('os', '')}{device_info.get('browser', '')}{device_info.get('screen_resolution', '')}"
        return hashlib.sha256(device_string.encode()).hexdigest()[:16]
    
    def _hash_ip(self, ip_address: str) -> str:
        """Hash IP address for privacy"""
        if not ip_address:
            return ''
        return hashlib.sha256(f"{ip_address}privacy_salt".encode()).hexdigest()[:16]
    
    def get_valid_external_data(self, source_type: str = None) -> List[ExternalDataSource]:
        """Get valid external data sources"""
        valid_data = []
        for source in self.external_data_sources:
            if source.connected:  # Check if source is connected instead
                if source_type is None or source.platform == source_type:
                    valid_data.append(source)
        return valid_data
    
    def cleanup_expired_data(self):
        """Clean up expired external data and old interactions"""
        # Remove inactive external data sources
        self.external_data_sources = [
            source for source in self.external_data_sources 
            if source.connected
        ]
        
        # Apply retention policy to interactions based on privacy settings
        if self.privacy_settings:
            retention_days = {
                'minimal': 30,
                'standard': 365,
                'extended': 730
            }.get(self.privacy_settings.data_retention_months, 24)
            
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            self.interactions = [
                interaction for interaction in self.interactions 
                if interaction.timestamp > cutoff_date
            ]
        
        self.save()
    
    def get_privacy_summary(self) -> Dict[str, Any]:
        """Get summary of privacy settings and data usage"""
        if not self.privacy_settings:
            return {'privacy_configured': False}
        
        return {
            'privacy_configured': True,
            'consent_types': [record.consent_type for record in self.consent_history if record.granted],
            'data_retention_months': self.privacy_settings.data_retention_months,
            'social_integration_enabled': self.privacy_settings.allow_social_data_collection,
            'behavioral_analysis_enabled': self.privacy_settings.allow_behavioral_analysis,
            'external_enrichment_enabled': self.privacy_settings.allow_third_party_sharing,
            'location_tracking_enabled': self.privacy_settings.allow_location_tracking,
            'last_privacy_update': self.privacy_settings.last_updated
        }
    
    # Compatibility properties for legacy code that uses old boolean fields
    @property
    def onboarding_completed(self):
        """Compatibility property for legacy code"""
        return self.onboarding_status in ['quick_completed', 'full_completed']
    
    @property
    def quick_onboarding_completed(self):
        """Compatibility property for legacy code"""
        return self.onboarding_status in ['quick_completed', 'full_completed']
    
    @property
    def is_onboarding_complete(self):
        """Check if any onboarding has been completed"""
        return self.onboarding_status != 'not_started'
    
    @property
    def is_full_onboarding_complete(self):
        """Check if full onboarding has been completed"""
        return self.onboarding_status == 'full_completed'

    def __str__(self):
        privacy_status = "with privacy controls" if self.privacy_settings else "no privacy config"
        return f"UserPreference(user_id={self.user_id}, {privacy_status})"


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
