"""
Social Authentication Models
Enhanced social authentication with rich profile data capture
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
import json
from typing import Dict, Any, Optional, List

User = get_user_model()


class SocialProvider(models.Model):
    """
    Social authentication providers configuration
    """
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('microsoft', 'Microsoft'),
        ('apple', 'Apple'),
        ('discord', 'Discord'),
        ('slack', 'Slack'),
    ]
    
    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    # OAuth Configuration
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    authorize_url = models.URLField()
    token_url = models.URLField()
    user_info_url = models.URLField()
    
    # Scope configuration for data collection
    default_scopes = models.JSONField(default=list, help_text="Default OAuth scopes to request")
    optional_scopes = models.JSONField(default=list, help_text="Optional scopes for rich data")
    
    # Data mapping configuration
    field_mappings = models.JSONField(default=dict, help_text="Map provider fields to our user fields")
    
    # Settings
    auto_register = models.BooleanField(default=True, help_text="Automatically register new users")
    require_email_verification = models.BooleanField(default=False)
    collect_extended_profile = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_social_provider'
        verbose_name = 'Social Provider'
        verbose_name_plural = 'Social Providers'
    
    def __str__(self):
        return f"{self.display_name} ({'Active' if self.is_active else 'Inactive'})"
    
    def get_authorize_url(self, state: str, redirect_uri: str, scopes: List[str] = None) -> str:
        """Generate OAuth authorization URL"""
        import urllib.parse
        
        if scopes is None:
            scopes = self.default_scopes
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': state,
        }
        
        return f"{self.authorize_url}?{urllib.parse.urlencode(params)}"


class SocialAccount(models.Model):
    """
    User's connected social media accounts with rich profile data
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE)
    
    # OAuth tokens
    access_token = models.TextField(help_text="OAuth access token")
    refresh_token = models.TextField(blank=True, help_text="OAuth refresh token")
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Provider-specific user identification
    provider_user_id = models.CharField(max_length=255, help_text="User ID on the provider's platform")
    username = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    
    # Profile Information
    profile_data = models.JSONField(default=dict, help_text="Complete profile data from provider")
    raw_profile_data = models.JSONField(default=dict, help_text="Raw unprocessed profile data")
    
    # Connection metadata
    scopes_granted = models.JSONField(default=list, help_text="OAuth scopes granted by user")
    connection_method = models.CharField(max_length=50, choices=[
        ('oauth', 'OAuth Authorization'),
        ('api_key', 'API Key'),
        ('webhook', 'Webhook'),
    ], default='oauth')
    
    # Status and tracking
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.CharField(max_length=20, choices=[
        ('real_time', 'Real Time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('manual', 'Manual Only'),
    ], default='daily')
    
    # Privacy settings
    data_collection_consent = models.BooleanField(default=True)
    public_profile_allowed = models.BooleanField(default=False)
    analytics_consent = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_social_account'
        verbose_name = 'Social Account'
        verbose_name_plural = 'Social Accounts'
        unique_together = ['provider', 'provider_user_id']
        indexes = [
            models.Index(fields=['user', 'provider']),
            models.Index(fields=['provider_user_id']),
            models.Index(fields=['last_sync']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.provider.display_name}"
    
    @property
    def is_token_expired(self) -> bool:
        """Check if access token has expired"""
        if not self.token_expires_at:
            return False
        return timezone.now() > self.token_expires_at
    
    def get_profile_field(self, field_name: str, default=None):
        """Get a field from profile data with fallback"""
        return self.profile_data.get(field_name, default)
    
    def update_profile_data(self, new_data: Dict[str, Any]) -> bool:
        """Update profile data and track changes"""
        if not self.data_collection_consent:
            return False
        
        # Store raw data
        self.raw_profile_data = new_data
        
        # Process and normalize data based on provider mappings
        processed_data = self._process_profile_data(new_data)
        
        # Update profile data
        self.profile_data.update(processed_data)
        self.last_sync = timezone.now()
        self.save()
        
        # Trigger downstream processing
        self._sync_with_user_preference()
        
        return True
    
    def _process_profile_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw profile data based on provider mappings"""
        processed = {}
        mappings = self.provider.field_mappings
        
        for our_field, provider_path in mappings.items():
            value = self._extract_nested_value(raw_data, provider_path)
            if value is not None:
                processed[our_field] = value
        
        # Add standard fields
        processed.update({
            'provider': self.provider.name,
            'provider_user_id': self.provider_user_id,
            'last_updated': timezone.now().isoformat(),
            'data_completeness': self._calculate_completeness(processed),
        })
        
        return processed
    
    def _extract_nested_value(self, data: Dict[str, Any], path: str):
        """Extract value from nested dictionary using dot notation"""
        try:
            keys = path.split('.')
            value = data
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
            return value
        except (KeyError, TypeError):
            return None
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate profile data completeness percentage"""
        expected_fields = [
            'name', 'email', 'avatar_url', 'location', 'bio',
            'company', 'website', 'followers_count', 'created_date'
        ]
        
        present_fields = sum(1 for field in expected_fields if data.get(field))
        return round((present_fields / len(expected_fields)) * 100, 2)
    
    def _sync_with_user_preference(self):
        """Sync social data with user preferences"""
        from apps.preferences.models import UserPreference
        
        try:
            user_pref = UserPreference.objects.get(user_id=str(self.user.id))
            
            # Update social data in preferences
            social_data = user_pref.social_data or []
            
            # Find existing entry or create new one
            existing_entry = None
            for entry in social_data:
                if (entry.get('platform') == self.provider.name and 
                    entry.get('user_id') == self.provider_user_id):
                    existing_entry = entry
                    break
            
            if existing_entry:
                existing_entry.update({
                    'profile_data': self.profile_data,
                    'last_sync': timezone.now().isoformat(),
                    'data_completeness': self.profile_data.get('data_completeness', 0),
                })
            else:
                social_data.append({
                    'platform': self.provider.name,
                    'user_id': self.provider_user_id,
                    'username': self.username,
                    'profile_data': self.profile_data,
                    'last_sync': timezone.now().isoformat(),
                    'data_completeness': self.profile_data.get('data_completeness', 0),
                })
            
            user_pref.social_data = social_data
            user_pref.save()
            
        except UserPreference.DoesNotExist:
            pass


class SocialAuthEvent(models.Model):
    """
    Track social authentication events and data collection
    """
    EVENT_TYPES = [
        ('connect', 'Account Connected'),
        ('disconnect', 'Account Disconnected'),
        ('sync', 'Profile Data Sync'),
        ('refresh_token', 'Token Refresh'),
        ('error', 'Authentication Error'),
        ('consent_granted', 'Data Consent Granted'),
        ('consent_revoked', 'Data Consent Revoked'),
        ('scope_updated', 'OAuth Scopes Updated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_auth_events')
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE)
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    success = models.BooleanField(default=True)
    
    # Event details
    details = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_social_event'
        verbose_name = 'Social Auth Event'
        verbose_name_plural = 'Social Auth Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['provider', 'created_at']),
            models.Index(fields=['success']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.get_event_type_display()} - {self.user.email} ({status})"


class SocialDataCollection(models.Model):
    """
    Track data collection requests and user consent for each social platform
    """
    COLLECTION_TYPES = [
        ('profile', 'Basic Profile'),
        ('contacts', 'Contacts/Friends'),
        ('posts', 'Posts/Tweets'),
        ('activity', 'Activity/Interactions'),
        ('preferences', 'User Preferences'),
        ('location', 'Location Data'),
        ('professional', 'Professional Information'),
        ('educational', 'Educational Background'),
        ('interests', 'Interests/Hobbies'),
        ('behavioral', 'Behavioral Patterns'),
    ]
    
    CONSENT_STATUS = [
        ('pending', 'Pending'),
        ('granted', 'Granted'),
        ('denied', 'Denied'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_data_collections')
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE)
    
    collection_type = models.CharField(max_length=50, choices=COLLECTION_TYPES)
    purpose = models.TextField(help_text="Purpose of data collection")
    
    consent_status = models.CharField(max_length=20, choices=CONSENT_STATUS, default='pending')
    consent_granted_at = models.DateTimeField(null=True, blank=True)
    consent_expires_at = models.DateTimeField(null=True, blank=True)
    consent_revoked_at = models.DateTimeField(null=True, blank=True)
    
    # Data collection details
    required_scopes = models.JSONField(default=list)
    optional_scopes = models.JSONField(default=list)
    data_retention_days = models.PositiveIntegerField(default=365)
    
    # Collection results
    last_collection = models.DateTimeField(null=True, blank=True)
    collection_count = models.PositiveIntegerField(default=0)
    data_points_collected = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_social_data_collection'
        verbose_name = 'Social Data Collection'
        verbose_name_plural = 'Social Data Collections'
        unique_together = ['user', 'provider', 'collection_type']
        indexes = [
            models.Index(fields=['consent_status']),
            models.Index(fields=['consent_expires_at']),
            models.Index(fields=['last_collection']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.provider.display_name} - {self.get_collection_type_display()}"
    
    def grant_consent(self, expires_in_days: int = 365):
        """Grant data collection consent"""
        self.consent_status = 'granted'
        self.consent_granted_at = timezone.now()
        if expires_in_days:
            self.consent_expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        self.save()
    
    def revoke_consent(self):
        """Revoke data collection consent"""
        self.consent_status = 'revoked'
        self.consent_revoked_at = timezone.now()
        self.save()
    
    @property
    def is_consent_valid(self) -> bool:
        """Check if consent is still valid"""
        if self.consent_status != 'granted':
            return False
        
        if self.consent_expires_at and timezone.now() > self.consent_expires_at:
            return False
        
        return True


class SocialProfileEnrichment(models.Model):
    """
    Track profile enrichment data from social platforms
    """
    ENRICHMENT_TYPES = [
        ('demographic', 'Demographic Information'),
        ('interests', 'Interests and Hobbies'),
        ('skills', 'Skills and Expertise'),
        ('education', 'Educational Background'),
        ('employment', 'Employment History'),
        ('location', 'Location History'),
        ('network', 'Social Network Analysis'),
        ('activity', 'Activity Patterns'),
        ('content', 'Content Preferences'),
        ('influence', 'Social Influence Metrics'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_enrichments')
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    
    enrichment_type = models.CharField(max_length=50, choices=ENRICHMENT_TYPES)
    confidence_score = models.FloatField(default=0.0, help_text="Confidence in data accuracy (0-1)")
    
    # Enrichment data
    enrichment_data = models.JSONField(default=dict)
    source_data = models.JSONField(default=dict, help_text="Original source data used for enrichment")
    
    # Metadata
    extraction_method = models.CharField(max_length=100, help_text="Method used to extract this data")
    processing_version = models.CharField(max_length=20, default='1.0')
    
    # Validation
    is_validated = models.BooleanField(default=False)
    validated_by = models.CharField(max_length=100, blank=True)
    validation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_social_profile_enrichment'
        verbose_name = 'Social Profile Enrichment'
        verbose_name_plural = 'Social Profile Enrichments'
        unique_together = ['social_account', 'enrichment_type']
        indexes = [
            models.Index(fields=['user', 'enrichment_type']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['is_validated']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_enrichment_type_display()} ({self.confidence_score:.2f})"
    
    def validate_data(self, validated_by: str, notes: str = ""):
        """Mark enrichment data as validated"""
        self.is_validated = True
        self.validated_by = validated_by
        self.validation_notes = notes
        self.save()


class SocialWebhook(models.Model):
    """
    Webhook configurations for real-time social media updates
    """
    provider = models.ForeignKey(SocialProvider, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_webhooks')
    
    webhook_url = models.URLField(help_text="URL endpoint for webhook")
    webhook_secret = models.CharField(max_length=255, help_text="Secret for webhook verification")
    
    # Event subscriptions
    subscribed_events = models.JSONField(default=list, help_text="List of events to subscribe to")
    
    # Configuration
    is_active = models.BooleanField(default=True)
    retry_attempts = models.PositiveIntegerField(default=3)
    timeout_seconds = models.PositiveIntegerField(default=30)
    
    # Statistics
    events_received = models.PositiveIntegerField(default=0)
    last_event_received = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_social_webhook'
        verbose_name = 'Social Webhook'
        verbose_name_plural = 'Social Webhooks'
        unique_together = ['provider', 'user']
    
    def __str__(self):
        return f"Webhook: {self.user.email} - {self.provider.display_name}"