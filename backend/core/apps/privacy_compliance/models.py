"""
backend/core/apps/privacy_compliance/models.py
Privacy compliance and GDPR consent management models
Handles user consent, privacy settings, location data, and compliance tracking
RELEVANT FILES: preferences/models.py, auth/models.py, analytics/models.py
"""

from datetime import datetime, timedelta
import uuid
import hashlib
from typing import Dict, List, Any, Optional
from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    StringField, IntField, DateTimeField, ListField,
    DictField, FloatField, BooleanField, EmailField,
    ValidationError, DoesNotExist
)


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


class UserPrivacy(Document):
    """
    Main privacy compliance document linking to Django User model.
    Contains all privacy settings, consent records, and compliance data.
    """

    # Link to Django User model
    user_id = IntField(required=True, unique=True)

    # Timestamps
    created_at = DateTimeField(required=True, default=datetime.utcnow)
    updated_at = DateTimeField(required=True, default=datetime.utcnow)

    # Privacy and consent management
    privacy_settings = EmbeddedDocumentField(PrivacySettings)
    consent_history = EmbeddedDocumentListField(ConsentRecord, default=list)

    # Location data with privacy controls
    location_history = EmbeddedDocumentListField(LocationRecord, default=list)

    # Data subject rights tracking
    data_export_requests = ListField(DictField(), default=list)
    data_deletion_requests = ListField(DictField(), default=list)
    data_rectification_requests = ListField(DictField(), default=list)

    # Privacy compliance status
    gdpr_compliance_status = StringField(max_length=20, default='compliant')
    last_compliance_check = DateTimeField(default=datetime.utcnow)
    privacy_officer_notes = ListField(DictField(), default=list)

    meta = {
        'collection': 'user_privacy',
        'indexes': [
            'user_id',
            '-updated_at',
            'privacy_settings.allow_personalization',
            'privacy_settings.allow_behavioral_analysis',
            'consent_history.granted_at',
            'gdpr_compliance_status',
            'location_history.country_code',
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp and check compliance"""
        self.updated_at = datetime.utcnow()
        self._check_compliance()
        return super().save(*args, **kwargs)

    def record_consent(self, consent_types: List[str], ip_address: str = None,
                      user_agent: str = None, consent_method: str = 'explicit'):
        """Record user consent for GDPR compliance"""
        consent_record = ConsentRecord(
            consent_types=consent_types,
            granted=True,
            granted_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            consent_method=consent_method
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

    def withdraw_consent(self, consent_type: str, reason: str = None):
        """Withdraw consent for a specific type"""
        self.record_consent_change(consent_type, False)

        # Add withdrawal reason to the latest record
        if self.consent_history:
            self.consent_history[-1].withdrawal_reason = reason

        self.save()

    def update_location(self, location_info: Dict[str, Any]):
        """Update location history with privacy checks"""
        if not self.privacy_settings or not self.privacy_settings.allow_location_tracking:
            return

        # Create privacy-safe location record
        location_record = LocationRecord(
            country_code=location_info.get('country_code'),
            region_code=location_info.get('region_code'),
            city_name=location_info.get('city_name'),
            timezone=location_info.get('timezone'),
            collection_method=location_info.get('collection_method', 'ip_geolocation'),
            precision_level=location_info.get('precision_level', 'city'),
            explicit_consent=location_info.get('explicit_consent', False),
            consent_timestamp=datetime.utcnow()
        )

        # Round coordinates for privacy if provided
        if location_info.get('latitude') and location_info.get('longitude'):
            # Round to ~1km precision (3 decimal places)
            location_record.latitude_rounded = round(location_info['latitude'], 3)
            location_record.longitude_rounded = round(location_info['longitude'], 3)

        # Clean up old location records based on retention
        retention_days = location_record.retention_days
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        self.location_history = [
            loc for loc in self.location_history
            if loc.collected_at > cutoff_date
        ]

        self.location_history.append(location_record)
        self.save()

    def request_data_export(self, export_format: str = 'json') -> str:
        """Request data export (GDPR Article 20)"""
        export_request = {
            'request_id': uuid.uuid4().hex,
            'requested_at': datetime.utcnow(),
            'format': export_format,
            'status': 'pending',
            'completed_at': None
        }

        self.data_export_requests.append(export_request)

        if self.privacy_settings:
            self.privacy_settings.last_data_export = datetime.utcnow()
            self.privacy_settings.export_format_preference = export_format

        self.save()
        return export_request['request_id']

    def request_data_deletion(self, reason: str = None) -> str:
        """Request data deletion (GDPR Article 17)"""
        deletion_request = {
            'request_id': uuid.uuid4().hex,
            'requested_at': datetime.utcnow(),
            'reason': reason,
            'status': 'pending',
            'completed_at': None
        }

        self.data_deletion_requests.append(deletion_request)
        self.save()
        return deletion_request['request_id']

    def request_data_rectification(self, fields_to_correct: List[str], reason: str = None) -> str:
        """Request data rectification (GDPR Article 16)"""
        rectification_request = {
            'request_id': uuid.uuid4().hex,
            'requested_at': datetime.utcnow(),
            'fields_to_correct': fields_to_correct,
            'reason': reason,
            'status': 'pending',
            'completed_at': None
        }

        self.data_rectification_requests.append(rectification_request)
        self.save()
        return rectification_request['request_id']

    def get_consent_status(self, consent_type: str) -> Dict[str, Any]:
        """Get current consent status for a specific type"""
        # Find the most recent consent record for this type
        relevant_records = [
            record for record in self.consent_history
            if consent_type in (record.consent_types or [record.consent_type])
        ]

        if not relevant_records:
            return {'granted': False, 'never_asked': True}

        latest_record = sorted(relevant_records, key=lambda r: r.updated_at)[-1]

        return {
            'granted': latest_record.granted,
            'granted_at': latest_record.granted_at,
            'updated_at': latest_record.updated_at,
            'consent_method': latest_record.consent_method,
            'legal_basis': latest_record.legal_basis,
            'never_asked': False
        }

    def get_privacy_summary(self) -> Dict[str, Any]:
        """Get summary of privacy settings and data usage"""
        if not self.privacy_settings:
            return {'privacy_configured': False}

        return {
            'privacy_configured': True,
            'privacy_level': self.privacy_settings.privacy_level,
            'consent_types': [
                record.consent_type for record in self.consent_history
                if record.granted
            ],
            'data_retention_months': self.privacy_settings.data_retention_months,
            'location_tracking_enabled': self.privacy_settings.allow_location_tracking,
            'social_data_collection_enabled': self.privacy_settings.allow_social_data_collection,
            'behavioral_analysis_enabled': self.privacy_settings.allow_behavioral_analysis,
            'third_party_sharing_enabled': self.privacy_settings.allow_third_party_sharing,
            'last_privacy_update': self.privacy_settings.last_updated,
            'gdpr_compliance_status': self.gdpr_compliance_status,
            'location_records_count': len(self.location_history),
            'export_requests_count': len(self.data_export_requests),
            'deletion_requests_count': len(self.data_deletion_requests)
        }

    def cleanup_expired_data(self):
        """Clean up expired location data and old consent records"""
        current_time = datetime.utcnow()

        # Clean up expired location records
        self.location_history = [
            loc for loc in self.location_history
            if (current_time - loc.collected_at).days <= loc.retention_days
        ]

        # Clean up very old consent records (keep for legal purposes but limit)
        # Keep records for 7 years for legal compliance
        seven_years_ago = current_time - timedelta(days=7*365)
        self.consent_history = [
            record for record in self.consent_history
            if record.updated_at > seven_years_ago
        ]

        self.save()

    def _check_compliance(self):
        """Check GDPR compliance status"""
        # Basic compliance checks
        issues = []

        if not self.privacy_settings:
            issues.append('No privacy settings configured')

        if not self.consent_history:
            issues.append('No consent records found')

        # Check if essential consent is granted
        essential_consent = self.get_consent_status('essential')
        if not essential_consent['granted']:
            issues.append('Essential consent not granted')

        # Check for expired location data
        if self.location_history:
            expired_locations = [
                loc for loc in self.location_history
                if (datetime.utcnow() - loc.collected_at).days > loc.retention_days
            ]
            if expired_locations:
                issues.append(f'{len(expired_locations)} expired location records')

        # Update compliance status
        self.gdpr_compliance_status = 'non_compliant' if issues else 'compliant'
        self.last_compliance_check = datetime.utcnow()

        return issues

    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional['UserPrivacy']:
        """Get user privacy by Django user ID"""
        try:
            return cls.objects.get(user_id=user_id)
        except DoesNotExist:
            return None

    @classmethod
    def create_for_user(cls, user_id: int, initial_consents: List[str] = None) -> 'UserPrivacy':
        """Create new user privacy record"""
        privacy = cls(user_id=user_id)

        # Record initial consents if provided
        if initial_consents:
            privacy.save()  # Save first to get an ID
            privacy.record_consent(initial_consents)
        else:
            privacy.save()

        return privacy

    def __str__(self):
        compliance_status = self.gdpr_compliance_status
        return f"UserPrivacy(user_id={self.user_id}, status={compliance_status})"
