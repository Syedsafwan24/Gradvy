"""
backend/core/apps/preferences/models.py
Core user preferences and basic profile information
Handles onboarding data and basic user preferences, references other domain apps
RELEVANT FILES: analytics/models.py, social_integration/models.py, privacy_compliance/models.py, learning_content/models.py
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField,
    StringField, IntField, DateTimeField, ListField,
    DictField, BooleanField, ValidationError, DoesNotExist
)
from mongoengine.base import BaseField
import logging

logger = logging.getLogger(__name__)


class CompatibleOnboardingStatusField(EmbeddedDocumentField):
    """
    Custom field that handles both old string format and new embedded document format
    for onboarding_status. Provides automatic migration during document loading.
    """

    def __init__(self, document_type=None, **kwargs):
        # We'll set the document_type after OnboardingStatus is defined
        super().__init__(document_type or 'OnboardingStatus', **kwargs)

    def to_python(self, value):
        """Convert database value to Python object, handling both formats"""
        if value is None:
            return None

        # If it's already an OnboardingStatus object, return as-is
        if hasattr(value, '__class__') and value.__class__.__name__ == 'OnboardingStatus':
            return value

        # If it's a dictionary (standard MongoDB embedded document), let parent handle it
        if isinstance(value, dict):
            try:
                return super().to_python(value)
            except Exception as e:
                logger.warning(f"Failed to load OnboardingStatus from dict: {e}")
                # Fall through to create new object

        # Handle old string format - auto-migrate to new format
        if isinstance(value, str):
            logger.info(f"🔄 Auto-migrating onboarding_status from string '{value}' to embedded document")
            return self._migrate_string_to_embedded_document(value)

        # Unknown format - create default
        logger.warning(f"Unknown onboarding_status format: {type(value)} = {value}")
        return self._create_default_onboarding_status()

    def _migrate_string_to_embedded_document(self, string_value):
        """Convert old string values to new OnboardingStatus embedded document"""
        # Get OnboardingStatus class from the document_type
        OnboardingStatus = self.document_type

        # Map old string values to new structure
        if string_value in ['full_completed', 'completed', 'quick_completed']:
            return OnboardingStatus(
                completed=True,
                current_step='completed',
                completed_steps=['welcome', 'basic_info', 'preferences', 'completed'],
                started_at=datetime.utcnow() - timedelta(days=1),  # Estimate
                completed_at=datetime.utcnow() - timedelta(hours=1),  # Estimate
                total_steps=4,
                completion_percentage=100,
                source='web',
                is_onboarded=True,
                quick_onboarding_completed=True if string_value == 'quick_completed' else False
            )
        elif string_value in ['in_progress', 'partial']:
            return OnboardingStatus(
                completed=False,
                current_step='basic_info',
                completed_steps=['welcome'],
                started_at=datetime.utcnow() - timedelta(hours=2),  # Estimate
                total_steps=4,
                completion_percentage=25,
                source='web',
                is_onboarded=False,
                quick_onboarding_completed=False
            )
        else:  # 'not_started' or any other value
            return OnboardingStatus(
                completed=False,
                current_step='welcome',
                completed_steps=[],
                started_at=datetime.utcnow(),
                total_steps=4,
                completion_percentage=0,
                source='web',
                is_onboarded=False,
                quick_onboarding_completed=False
            )

    def _create_default_onboarding_status(self):
        """Create a default OnboardingStatus for unknown formats"""
        # Get OnboardingStatus class from the document_type
        OnboardingStatus = self.document_type

        return OnboardingStatus(
            completed=False,
            current_step='welcome',
            completed_steps=[],
            started_at=datetime.utcnow(),
            total_steps=4,
            completion_percentage=0,
            source='web',
            is_onboarded=False,
            quick_onboarding_completed=False
        )

    def to_mongo(self, value):
        """Convert Python object to MongoDB storage format"""
        if value is None:
            return None

        # If it's a string (old format), convert it first
        if isinstance(value, str):
            value = self._migrate_string_to_embedded_document(value)

        # Now convert to MongoDB format
        return super().to_mongo(value)


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


class OnboardingStatus(EmbeddedDocument):
    """Onboarding progress tracking"""

    # Onboarding completion status
    completed = BooleanField(default=False)
    current_step = StringField(max_length=50, default='welcome')
    completed_steps = ListField(StringField(max_length=50), default=list)

    # Onboarding flow metadata
    started_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    total_steps = IntField(default=5)
    completion_percentage = IntField(min_value=0, max_value=100, default=0)

    # Onboarding source tracking
    source = StringField(max_length=50, default='web')  # web, mobile, invite, etc.
    referrer = StringField(max_length=200)

    # Legacy support - remove after migration
    is_onboarded = BooleanField(default=False)
    quick_onboarding_completed = BooleanField(default=False)


class UserPreference(Document):
    """
    Simplified user preference document for core preferences only.
    Links to domain-specific models in other apps via user_id.

    Domain Model Relationships (via user_id):
    - UserAnalytics (analytics app) - behavioral tracking and insights
    - SocialProfile (social_integration app) - social media integrations
    - UserPrivacy (privacy_compliance app) - GDPR compliance and consent
    - UserContentProfile (learning_content app) - course recommendations and content
    """

    # Link to Django User model
    user_id = IntField(required=True, unique=True)

    # Timestamps
    created_at = DateTimeField(required=True, default=datetime.utcnow)
    updated_at = DateTimeField(required=True, default=datetime.utcnow)

    # Core preference data (kept in this app)
    basic_info = EmbeddedDocumentField(BasicInfo)
    onboarding_status = CompatibleOnboardingStatusField(OnboardingStatus)

    # User profile metadata
    profile_completeness = IntField(min_value=0, max_value=100, default=0)
    last_active = DateTimeField(default=datetime.utcnow)

    # Feature flags and configurations
    feature_flags = DictField(default=dict)
    ui_preferences = DictField(default=dict)  # theme, language, etc.

    # ========================================
    # LEGACY FIELDS FOR BACKWARD COMPATIBILITY
    # ========================================
    # These fields exist in old MongoDB documents but are now handled by domain models
    # or compatibility properties. Keeping them to prevent FieldDoesNotExist errors.

    # Legacy onboarding fields (now handled by onboarding_status embedded doc)
    onboarding_completed = BooleanField(default=False)  # Legacy - use onboarding_status.completed
    quick_onboarding_completed = BooleanField(default=False)  # Legacy
    onboarding_completed_at = DateTimeField()  # Legacy
    quick_onboarding_data = DictField(default=dict)  # Legacy
    completion_prompt_dismissed_count = IntField(default=0)  # Legacy
    completion_milestones = DictField(default=dict)  # Legacy
    profile_completion_percentage = IntField(min_value=0, max_value=100, default=0)  # Legacy - use profile_completeness

    # Legacy analytics fields (now handled by analytics domain)
    interactions = ListField(default=list)  # Legacy - now in UserAnalytics
    streak_data = DictField(default=dict)  # Legacy
    achievement_badges = ListField(default=list)  # Legacy

    # Legacy privacy fields (now handled by privacy_compliance domain)
    consent_history = ListField(default=list)  # Legacy - now in UserPrivacy

    # Legacy content fields (now handled by learning_content domain)
    _legacy_content_preferences = DictField(default=dict, db_field='content_preferences')  # Legacy - now in UserContentProfile

    # Legacy social fields (now handled by social_integration domain)
    external_data_sources = ListField(default=list)  # Legacy - now in SocialProfile

    # Legacy device/location fields (now handled by analytics domain)
    device_patterns = ListField(default=list)  # Legacy - now in UserAnalytics
    location_history = ListField(default=list)  # Legacy - now in UserAnalytics

    # Legacy custom preferences (now stored in ui_preferences)
    custom_preferences = DictField(default=dict)  # Legacy - merged into ui_preferences

    meta = {
        'collection': 'user_preferences',
        'indexes': [
            'user_id',
            '-updated_at',
            '-last_active',
            'onboarding_status.completed',
            'basic_info.experience_level',
            'basic_info.learning_goals',
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp and calculate completeness"""
        self.updated_at = datetime.utcnow()
        self._calculate_profile_completeness()
        return super().save(*args, **kwargs)

    def _calculate_profile_completeness(self):
        """Calculate profile completeness percentage"""
        completeness = 0

        # Basic info completeness (60% weight)
        if self.basic_info:
            basic_fields = [
                self.basic_info.learning_goals,
                self.basic_info.experience_level,
                self.basic_info.preferred_pace,
                self.basic_info.time_availability,
                self.basic_info.learning_style,
                self.basic_info.career_stage,
                self.basic_info.target_timeline
            ]
            filled_basic = sum(1 for field in basic_fields if field)
            completeness += (filled_basic / len(basic_fields)) * 60

        # Onboarding completion (40% weight)
        if self.onboarding_status and self.onboarding_status.completed:
            completeness += 40

        self.profile_completeness = int(completeness)

    def update_completion_percentage(self):
        """
        Public method to update profile completion percentage.
        This method is called by views after preference updates.
        """
        self._calculate_profile_completeness()

    def complete_onboarding_step(self, step_name: str):
        """Mark an onboarding step as completed"""
        if not self.onboarding_status:
            self.onboarding_status = OnboardingStatus()

        if step_name not in self.onboarding_status.completed_steps:
            self.onboarding_status.completed_steps.append(step_name)

        # Calculate completion percentage
        total_steps = self.onboarding_status.total_steps
        completed_count = len(self.onboarding_status.completed_steps)
        self.onboarding_status.completion_percentage = int((completed_count / total_steps) * 100)

        # Mark as completed if all steps done
        if completed_count >= total_steps:
            self.onboarding_status.completed = True
            self.onboarding_status.completed_at = datetime.utcnow()
            self.onboarding_status.is_onboarded = True  # Legacy support

        self.save()

    def update_basic_info(self, info_data: Dict[str, Any]):
        """Update basic info from onboarding or profile editing"""
        if not self.basic_info:
            self.basic_info = BasicInfo()

        # Update fields that are provided
        for field_name, value in info_data.items():
            if hasattr(self.basic_info, field_name):
                setattr(self.basic_info, field_name, value)

        self.save()

    def get_related_domain_data(self) -> Dict[str, bool]:
        """
        Check which domain models exist for this user.
        Returns dict of domain -> exists mapping.
        """
        from apps.analytics.models import UserAnalytics
        from apps.social_integration.models import SocialProfile
        from apps.privacy_compliance.models import UserPrivacy
        from apps.learning_content.models import UserContentProfile

        return {
            'analytics': UserAnalytics.get_by_user_id(self.user_id) is not None,
            'social': SocialProfile.get_by_user_id(self.user_id) is not None,
            'privacy': UserPrivacy.get_by_user_id(self.user_id) is not None,
            'content': UserContentProfile.get_by_user_id(self.user_id) is not None,
        }

    def initialize_domain_models(self):
        """
        Initialize related domain models if they don't exist.
        Called after user registration or onboarding completion.
        """
        from apps.analytics.models import UserAnalytics
        from apps.social_integration.models import SocialProfile
        from apps.privacy_compliance.models import UserPrivacy
        from apps.learning_content.models import UserContentProfile

        # Initialize analytics tracking
        if not UserAnalytics.get_by_user_id(self.user_id):
            UserAnalytics.create_for_user(self.user_id)

        # Initialize privacy settings with default consent
        if not UserPrivacy.get_by_user_id(self.user_id):
            UserPrivacy.create_for_user(
                self.user_id,
                initial_consents=['essential', 'analytics', 'personalization']
            )

        # Initialize content profile with basic preferences
        if not UserContentProfile.get_by_user_id(self.user_id):
            content_prefs = {}
            if self.basic_info:
                content_prefs = {
                    'difficulty_preference': self._map_experience_to_difficulty(),
                    'duration_preference': self._map_time_to_duration(),
                }
            UserContentProfile.create_for_user(self.user_id, content_prefs)

        # Social profile is created only when user connects external accounts
        # so we don't initialize it by default

    def _map_experience_to_difficulty(self) -> str:
        """Map experience level to content difficulty preference"""
        if not self.basic_info or not self.basic_info.experience_level:
            return 'mixed'

        mapping = {
            'complete_beginner': 'beginner',
            'some_basics': 'beginner',
            'intermediate': 'intermediate',
            'advanced': 'advanced'
        }
        return mapping.get(self.basic_info.experience_level, 'mixed')

    def _map_time_to_duration(self) -> str:
        """Map time availability to content duration preference"""
        if not self.basic_info or not self.basic_info.time_availability:
            return 'mixed'

        mapping = {
            '1-2hrs': 'short',
            '3-5hrs': 'medium',
            '5+hrs': 'long'
        }
        return mapping.get(self.basic_info.time_availability, 'mixed')

    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = datetime.utcnow()
        self.save()

    def set_feature_flag(self, flag_name: str, enabled: bool):
        """Set a feature flag for this user"""
        self.feature_flags[flag_name] = enabled
        self.save()

    def is_feature_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled for this user"""
        return self.feature_flags.get(flag_name, False)

    def get_profile_summary(self) -> Dict[str, Any]:
        """Get a summary of user's profile and preferences"""
        summary = {
            'user_id': self.user_id,
            'profile_completeness': self.profile_completeness,
            'onboarding_completed': self.onboarding_status.completed if self.onboarding_status else False,
            'last_active': self.last_active,
            'created_at': self.created_at,
        }

        if self.basic_info:
            summary.update({
                'learning_goals': self.basic_info.learning_goals,
                'experience_level': self.basic_info.experience_level,
                'preferred_pace': self.basic_info.preferred_pace,
                'career_stage': self.basic_info.career_stage,
                'target_timeline': self.basic_info.target_timeline,
            })

        # Add domain model status
        summary['domain_models'] = self.get_related_domain_data()

        return summary

    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional['UserPreference']:
        """Get user preferences by Django user ID"""
        try:
            return cls.objects.get(user_id=user_id)
        except DoesNotExist:
            return None

    @classmethod
    def create_for_user(cls, user_id: int, onboarding_data: Dict[str, Any] = None) -> 'UserPreference':
        """Create new user preferences record"""
        preferences = cls(user_id=user_id)

        # Initialize onboarding status
        preferences.onboarding_status = OnboardingStatus()

        # Add basic info if provided
        if onboarding_data:
            preferences.update_basic_info(onboarding_data)

        preferences.save()
        return preferences

    # =========================================================================
    # COMPATIBILITY METHODS - Delegate to Domain Models
    # These methods maintain backward compatibility with existing code
    # =========================================================================

    def has_analytics_consent(self) -> bool:
        """Check analytics consent - delegates to UserPrivacy model"""
        try:
            from apps.privacy_compliance.models import UserPrivacy
            privacy = UserPrivacy.get_by_user_id(self.user_id)
            return privacy.privacy_settings.allow_analytics if privacy and privacy.privacy_settings else True
        except Exception:
            return True  # Default to True for backward compatibility

    def has_behavioral_analysis_consent(self) -> bool:
        """Check behavioral analysis consent - delegates to UserPrivacy model"""
        try:
            from apps.privacy_compliance.models import UserPrivacy
            privacy = UserPrivacy.get_by_user_id(self.user_id)
            return privacy.privacy_settings.allow_behavioral_analysis if privacy and privacy.privacy_settings else True
        except Exception:
            return True

    def has_personalization_consent(self) -> bool:
        """Check personalization consent - delegates to UserPrivacy model"""
        try:
            from apps.privacy_compliance.models import UserPrivacy
            privacy = UserPrivacy.get_by_user_id(self.user_id)
            return privacy.privacy_settings.allow_personalization if privacy and privacy.privacy_settings else True
        except Exception:
            return True

    def update_behavioral_patterns(self, **kwargs):
        """Update behavioral patterns - delegates to UserAnalytics model"""
        try:
            from apps.analytics.models import UserAnalytics
            analytics = UserAnalytics.get_by_user_id(self.user_id)

            if not analytics:
                analytics = UserAnalytics.create_for_user(self.user_id)

            if not analytics.behavioral_patterns:
                from apps.analytics.models import BehavioralPatterns
                analytics.behavioral_patterns = BehavioralPatterns()

            # Update the behavioral patterns with provided kwargs
            for key, value in kwargs.items():
                if hasattr(analytics.behavioral_patterns, key):
                    setattr(analytics.behavioral_patterns, key, value)

            analytics.save()
        except Exception as e:
            # Log error but don't break the application
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating behavioral patterns for user {self.user_id}: {str(e)}")

    def update_ai_insights(self, insights: Dict[str, Any]):
        """Update AI insights - delegates to UserAnalytics model"""
        try:
            from apps.analytics.models import UserAnalytics
            analytics = UserAnalytics.get_by_user_id(self.user_id)

            if not analytics:
                analytics = UserAnalytics.create_for_user(self.user_id)

            analytics.update_ai_insights(insights)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating AI insights for user {self.user_id}: {str(e)}")

    def add_interaction(self, interaction_type: str, data: Dict[str, Any], context: Dict[str, Any] = None):
        """Add interaction - delegates to UserAnalytics model"""
        try:
            from apps.analytics.models import UserAnalytics
            analytics = UserAnalytics.get_by_user_id(self.user_id)

            if not analytics:
                analytics = UserAnalytics.create_for_user(self.user_id)

            analytics.add_interaction(interaction_type, data, context)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error adding interaction for user {self.user_id}: {str(e)}")

    @property
    def behavioral_patterns(self):
        """Access behavioral patterns - delegates to UserAnalytics model"""
        try:
            from apps.analytics.models import UserAnalytics
            analytics = UserAnalytics.get_by_user_id(self.user_id)
            return analytics.behavioral_patterns if analytics else None
        except Exception:
            return None

    @property
    def ai_insights(self):
        """Access AI insights - delegates to UserAnalytics model"""
        try:
            from apps.analytics.models import UserAnalytics
            analytics = UserAnalytics.get_by_user_id(self.user_id)
            return analytics.ai_insights if analytics else None
        except Exception:
            return None

    @property
    def privacy_settings(self):
        """Access privacy settings - delegates to UserPrivacy model"""
        try:
            from apps.privacy_compliance.models import UserPrivacy
            privacy = UserPrivacy.get_by_user_id(self.user_id)
            return privacy.privacy_settings if privacy else None
        except Exception:
            return None

    @property
    def social_data(self):
        """Access social data - delegates to SocialProfile model"""
        try:
            from apps.social_integration.models import SocialProfile
            social = SocialProfile.get_by_user_id(self.user_id)
            return social.social_data if social else None
        except Exception:
            return None

    @property
    def content_preferences(self):
        """Access content preferences - delegates to UserContentProfile model or creates defaults"""
        try:
            from apps.learning_content.models import UserContentProfile
            content = UserContentProfile.get_by_user_id(self.user_id)
            if content and content.content_preferences:
                return content.content_preferences
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Failed to load UserContentProfile for user {self.user_id}: {e}")

        # Fallback to legacy data
        if hasattr(self, '_legacy_content_preferences') and self._legacy_content_preferences:
            # Convert legacy dict to a simple object for compatibility
            class LegacyContentPrefs:
                def __init__(self, data):
                    for key, value in data.items():
                        setattr(self, key, value)

                def to_mongo(self):
                    """Convert to MongoDB dict format"""
                    return self.__dict__

            return LegacyContentPrefs(self._legacy_content_preferences)

        # NEW: Return default content preferences instead of None
        class DefaultContentPrefs:
            """Default content preferences when none exist"""
            def __init__(self):
                self.preferred_platforms = ['youtube', 'udemy']
                self.content_types = ['video', 'interactive']
                self.difficulty_preference = 'mixed'
                self.duration_preference = 'mixed'
                self.language_preference = ['english']
                self.instructor_ratings_min = 3.0

            def to_mongo(self):
                """Convert to MongoDB dict format"""
                return {
                    'preferred_platforms': self.preferred_platforms,
                    'content_types': self.content_types,
                    'difficulty_preference': self.difficulty_preference,
                    'duration_preference': self.duration_preference,
                    'language_preference': self.language_preference,
                    'instructor_ratings_min': self.instructor_ratings_min
                }

        return DefaultContentPrefs()

    # Legacy properties for backward compatibility
    @property
    def last_activity_date(self):
        """Backward compatibility - map to last_active"""
        return self.last_active

    def get_onboarding_completed(self):
        """Get onboarding completion status from embedded document"""
        onboard_status = object.__getattribute__(self, 'onboarding_status')
        return onboard_status.completed if onboard_status else False

    def is_onboarding_truly_complete(self) -> bool:
        """Check if onboarding is truly complete"""
        onboard_status = object.__getattribute__(self, 'onboarding_status')
        return onboard_status.completed if onboard_status else False

    # Additional helper methods for tasks
    def get_recent_interactions(self, days: int = 30, interaction_type: str = None):
        """Get recent interactions - delegates to UserAnalytics"""
        try:
            from apps.analytics.models import UserAnalytics
            analytics = UserAnalytics.get_by_user_id(self.user_id)
            return analytics.get_recent_interactions(days, interaction_type) if analytics else []
        except Exception:
            return []

    def calculate_user_segment(self) -> str:
        """Calculate user segment based on behavioral patterns"""
        try:
            patterns = self.behavioral_patterns
            if not patterns:
                return 'new_user'

            if patterns.engagement_score > 0.8 and patterns.dropout_risk_score < 0.2:
                return 'highly_engaged'
            elif patterns.dropout_risk_score > 0.6:
                return 'at_risk'
            elif patterns.learning_velocity > 0.1:
                return 'fast_learner'
            elif patterns.engagement_score < 0.3:
                return 'low_engagement'
            else:
                return 'regular'
        except Exception:
            return 'unknown'

    # ========================================
    # INTERACTION DATA COMPATIBILITY HELPERS
    # ========================================

    @staticmethod
    def safe_get_interaction_field(interaction, field_name, default=None):
        """
        Safely get a field from an interaction, handling both BaseDict and object formats.

        Args:
            interaction: Interaction data (BaseDict or object)
            field_name: Name of the field to retrieve
            default: Default value if field not found

        Returns:
            Field value or default
        """
        try:
            # Try dictionary access first (BaseDict format)
            if hasattr(interaction, 'get'):
                return interaction.get(field_name, default)
            elif hasattr(interaction, '__getitem__'):
                return interaction[field_name] if field_name in interaction else default
            # Try object attribute access (new format)
            elif hasattr(interaction, field_name):
                return getattr(interaction, field_name, default)
            else:
                return default
        except (KeyError, AttributeError, TypeError):
            return default

    def get_safe_interactions(self):
        """
        Get interactions with safe field access wrapper.
        Returns a list of interaction wrappers that work with both legacy and new formats.
        """
        if not self.interactions:
            return []

        class InteractionWrapper:
            """Wrapper to provide unified access to interaction data"""
            def __init__(self, raw_interaction):
                self._raw = raw_interaction

            @property
            def type(self):
                return UserPreference.safe_get_interaction_field(self._raw, 'type', 'unknown')

            @property
            def timestamp(self):
                return UserPreference.safe_get_interaction_field(self._raw, 'timestamp')

            @property
            def data(self):
                return UserPreference.safe_get_interaction_field(self._raw, 'data', {})

            @property
            def context(self):
                return UserPreference.safe_get_interaction_field(self._raw, 'context', {})

            def get(self, key, default=None):
                """Dictionary-like access"""
                return UserPreference.safe_get_interaction_field(self._raw, key, default)

            def __getitem__(self, key):
                """Dictionary-like access with KeyError"""
                value = UserPreference.safe_get_interaction_field(self._raw, key)
                if value is None:
                    raise KeyError(key)
                return value

        return [InteractionWrapper(interaction) for interaction in self.interactions]

    def __str__(self):
        completion = f"{self.profile_completeness}%"
        return f"UserPreference(user_id={self.user_id}, completion={completion})"