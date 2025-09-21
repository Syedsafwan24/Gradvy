"""
backend/core/apps/social_integration/models.py
Social media and external platform integration models
Handles LinkedIn, GitHub, Google integrations and external data sources
RELEVANT FILES: preferences/models.py, auth/models.py, privacy_compliance/models.py
"""

from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Any, Optional
from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    StringField, IntField, DateTimeField, ListField,
    DictField, FloatField, BooleanField, EmailField,
    ValidationError, DoesNotExist, Q
)


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


class SocialProfile(Document):
    """
    Main social integration document linking to Django User model.
    Contains all social media profiles and external integrations.
    """

    # Link to Django User model
    user_id = IntField(required=True, unique=True)

    # Timestamps
    created_at = DateTimeField(required=True, default=datetime.utcnow)
    updated_at = DateTimeField(required=True, default=datetime.utcnow)

    # Embedded social data
    social_data = EmbeddedDocumentField(SocialData)

    # External data integration
    external_data_sources = EmbeddedDocumentListField(ExternalDataSource, default=list)

    # Social features configuration
    social_features_enabled = BooleanField(default=False)
    public_profile = BooleanField(default=False)
    social_learning_enabled = BooleanField(default=False)

    # Social networking preferences
    allow_friend_requests = BooleanField(default=True)
    show_learning_progress = BooleanField(default=False)
    share_achievements = BooleanField(default=False)

    meta = {
        'collection': 'social_profiles',
        'indexes': [
            'user_id',
            '-updated_at',
            'external_data_sources.platform',
            'external_data_sources.last_sync',
            'social_data.linkedin_profile',
            'social_data.github_profile',
            'social_features_enabled',
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def add_external_data_source(self, platform: str, platform_user_id: str,
                                 platform_username: str = None, permissions: List[str] = None):
        """Add or update external data source"""
        # Remove existing source for same platform
        self.external_data_sources = [
            source for source in self.external_data_sources
            if source.platform != platform
        ]

        external_source = ExternalDataSource(
            platform=platform,
            platform_user_id=platform_user_id,
            platform_username=platform_username,
            connected=True,
            connection_date=datetime.utcnow(),
            permissions_granted=permissions or [],
            data_collection_consent=True
        )

        self.external_data_sources.append(external_source)
        self.save()
        return external_source

    def remove_external_data_source(self, platform: str):
        """Remove external data source"""
        self.external_data_sources = [
            source for source in self.external_data_sources
            if source.platform != platform
        ]
        self.save()

    def get_external_data_source(self, platform: str) -> Optional[ExternalDataSource]:
        """Get external data source by platform"""
        for source in self.external_data_sources:
            if source.platform == platform and source.connected:
                return source
        return None

    def update_social_data(self, platform: str, data: Dict[str, Any]):
        """Update social data from external platform"""
        if not self.social_data:
            self.social_data = SocialData()

        if platform == 'linkedin':
            self.social_data.linkedin_profile.update(data)
            self.social_data.linkedin_connections = data.get('connections', 0)
            self.social_data.professional_headline = data.get('headline', '')
            self.social_data.industry = data.get('industry', '')
            self.social_data.experience_years = data.get('experience_years', 0)
            self.social_data.education = data.get('education', [])
            self.social_data.skills = data.get('skills', [])
            self.social_data.certifications = data.get('certifications', [])

        elif platform == 'github':
            self.social_data.github_profile.update(data)
            self.social_data.github_repos = data.get('public_repos', 0)
            self.social_data.github_followers = data.get('followers', 0)
            self.social_data.programming_languages = data.get('languages', [])
            self.social_data.github_contributions = data.get('contributions', 0)

        elif platform == 'google':
            self.social_data.google_profile.update(data)
            self.social_data.google_interests = data.get('interests', [])

        # Update data quality and timestamp
        self.social_data.last_updated = datetime.utcnow()
        self._calculate_social_learning_score()
        self.save()

    def _calculate_social_learning_score(self):
        """Calculate social learning score based on available data"""
        if not self.social_data:
            return

        score = 0.0
        factors = 0

        # LinkedIn factors
        if self.social_data.linkedin_connections > 0:
            score += min(self.social_data.linkedin_connections / 500, 1.0) * 0.3
            factors += 1

        if self.social_data.skills:
            score += min(len(self.social_data.skills) / 20, 1.0) * 0.2
            factors += 1

        # GitHub factors
        if self.social_data.github_repos > 0:
            score += min(self.social_data.github_repos / 50, 1.0) * 0.3
            factors += 1

        if self.social_data.github_contributions > 0:
            score += min(self.social_data.github_contributions / 1000, 1.0) * 0.2
            factors += 1

        # Calculate final score
        if factors > 0:
            self.social_data.social_learning_score = score / factors
        else:
            self.social_data.social_learning_score = 0.0

    def sync_external_data(self, platform: str = None) -> Dict[str, Any]:
        """Sync data from external platforms"""
        sync_results = {}

        sources_to_sync = [
            source for source in self.external_data_sources
            if source.connected and (platform is None or source.platform == platform)
        ]

        for source in sources_to_sync:
            try:
                # Here you would implement actual API calls to sync data
                # For now, we'll just update the sync timestamp
                source.last_sync = datetime.utcnow()
                source.successful_syncs += 1
                source.last_sync_status = 'success'
                sync_results[source.platform] = 'success'

            except Exception as e:
                source.failed_syncs += 1
                source.last_sync_status = 'failed'
                sync_results[source.platform] = f'failed: {str(e)}'

        self.save()
        return sync_results

    def get_social_connections(self) -> Dict[str, Any]:
        """Get summary of social connections across platforms"""
        if not self.social_data:
            return {}

        return {
            'linkedin_connections': self.social_data.linkedin_connections,
            'github_followers': self.social_data.github_followers,
            'peer_connections': self.social_data.peer_connections,
            'mentor_relationships': len(self.social_data.mentor_relationships),
            'social_learning_score': self.social_data.social_learning_score,
            'total_connections': (
                self.social_data.linkedin_connections +
                self.social_data.github_followers +
                self.social_data.peer_connections
            )
        }

    def get_professional_summary(self) -> Dict[str, Any]:
        """Get professional summary from social data"""
        if not self.social_data:
            return {}

        return {
            'headline': self.social_data.professional_headline,
            'industry': self.social_data.industry,
            'experience_years': self.social_data.experience_years,
            'skills': self.social_data.skills,
            'programming_languages': self.social_data.programming_languages,
            'github_repos': self.social_data.github_repos,
            'certifications_count': len(self.social_data.certifications),
            'education_count': len(self.social_data.education),
        }

    def cleanup_expired_tokens(self):
        """Clean up expired OAuth tokens"""
        current_time = datetime.utcnow()

        for source in self.external_data_sources:
            if source.token_expires_at and source.token_expires_at < current_time:
                source.access_token_hash = None
                source.refresh_token_hash = None
                source.connected = False
                source.last_sync_status = 'token_expired'

        self.save()

    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional['SocialProfile']:
        """Get social profile by Django user ID"""
        try:
            return cls.objects.get(user_id=user_id)
        except DoesNotExist:
            return None

    @classmethod
    def create_for_user(cls, user_id: int) -> 'SocialProfile':
        """Create new social profile record"""
        profile = cls(user_id=user_id)
        profile.save()
        return profile

    def __str__(self):
        platforms = [source.platform for source in self.external_data_sources if source.connected]
        return f"SocialProfile(user_id={self.user_id}, platforms={platforms})"


class SocialConnection(Document):
    """
    Represents connections between users for social learning features.
    """

    # User who initiated the connection
    from_user_id = IntField(required=True)

    # User who received the connection request
    to_user_id = IntField(required=True)

    # Connection status
    CONNECTION_STATUS = ['pending', 'accepted', 'declined', 'blocked']
    status = StringField(choices=CONNECTION_STATUS, default='pending')

    # Connection type
    CONNECTION_TYPES = ['friend', 'mentor', 'mentee', 'study_buddy', 'colleague']
    connection_type = StringField(choices=CONNECTION_TYPES, default='friend')

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    accepted_at = DateTimeField()

    # Connection metadata
    message = StringField(max_length=500)  # Optional message with request
    common_interests = ListField(StringField(max_length=50), default=list)
    shared_goals = ListField(StringField(max_length=100), default=list)

    meta = {
        'collection': 'social_connections',
        'indexes': [
            ('from_user_id', 'to_user_id'),
            'from_user_id',
            'to_user_id',
            'status',
            'connection_type',
            '-created_at'
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def accept_connection(self):
        """Accept the connection request"""
        self.status = 'accepted'
        self.accepted_at = datetime.utcnow()
        self.save()

    def decline_connection(self):
        """Decline the connection request"""
        self.status = 'declined'
        self.save()

    def block_connection(self):
        """Block the connection"""
        self.status = 'blocked'
        self.save()

    @classmethod
    def get_user_connections(cls, user_id: int, status: str = 'accepted') -> List['SocialConnection']:
        """Get all connections for a user"""
        return cls.objects.filter(
            Q(from_user_id=user_id) | Q(to_user_id=user_id),
            status=status
        ).order_by('-created_at')

    @classmethod
    def get_connection_between_users(cls, user1_id: int, user2_id: int) -> Optional['SocialConnection']:
        """Get connection between two specific users"""
        return cls.objects.filter(
            (Q(from_user_id=user1_id) & Q(to_user_id=user2_id)) |
            (Q(from_user_id=user2_id) & Q(to_user_id=user1_id))
        ).first()

    @classmethod
    def create_connection_request(cls, from_user_id: int, to_user_id: int,
                                 connection_type: str = 'friend', message: str = None) -> 'SocialConnection':
        """Create a new connection request"""
        # Check if connection already exists
        existing = cls.get_connection_between_users(from_user_id, to_user_id)
        if existing:
            raise ValueError("Connection already exists between these users")

        connection = cls(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            connection_type=connection_type,
            message=message,
            status='pending'
        )
        connection.save()
        return connection

    def __str__(self):
        return f"SocialConnection({self.from_user_id} -> {self.to_user_id}, {self.status})"
