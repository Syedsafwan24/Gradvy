"""
Authentication models for Gradvy project.

This module defines the custom User model and related profile models
for the authentication system with MFA support.
"""

from typing import Optional
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for Gradvy authentication system.
    
    This model extends Django's AbstractBaseUser and PermissionsMixin
    to provide a comprehensive user management system with MFA support.
    
    Attributes:
        email (str): User's email address (used as username)
        first_name (str): User's first name
        last_name (str): User's last name
        is_active (bool): Whether the user account is active
        is_staff (bool): Whether the user can access admin interface
        is_superuser (bool): Whether the user has all permissions
        must_change_password (bool): Whether user must change password on next login
        mfa_enrolled (bool): Whether user has enrolled in MFA
        last_password_change (datetime): When password was last changed
        failed_login_attempts (int): Number of consecutive failed login attempts
        locked_until (datetime): When account lock expires (if locked)
        date_joined (datetime): When the user account was created
        last_login (datetime): When user last logged in
    """
    # Core fields
    email = models.EmailField(unique=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Security fields
    must_change_password = models.BooleanField(default=True)
    mfa_enrolled = models.BooleanField(default=False)
    last_password_change = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    
    # Manager
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Only email is required now
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "auth_user"
    
    def __str__(self) -> str:
        """Return string representation of the user."""
        return self.email
    
    def get_full_name(self) -> str:
        """
        Return the user's full name.
        
        Returns:
            str: Full name combining first and last name, or empty string if both are empty.
        """
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self) -> str:
        """
        Return the user's short name (first name only).
        
        Returns:
            str: User's first name.
        """
        return self.first_name
    
    @property
    def is_locked(self) -> bool:
        """
        Check if the user account is currently locked.
        
        Returns:
            bool: True if account is locked and lock hasn't expired, False otherwise.
        """
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

class UserProfile(models.Model):
    """
    Extended user profile information.
    
    This model stores additional user information that is not part of the core
    authentication process but is useful for user management and preferences.
    
    Attributes:
        user (User): One-to-one relationship with User model
        phone_number (str): User's phone number for contact or SMS MFA
        bio (str): User's bio/about me section
        totp_enabled (bool): Legacy field for TOTP status (use User.mfa_enrolled instead)
        backup_codes_remaining (int): Number of unused backup codes remaining
        language (str): User's preferred language code
        timezone (str): User's preferred timezone
        created_at (datetime): When the profile was created
        updated_at (datetime): When the profile was last updated
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Contact information
    phone_number = models.CharField(max_length=20, blank=True, help_text="User's contact phone number")
    bio = models.TextField(max_length=500, blank=True, help_text="User's bio/about me section")
    
    # MFA Settings
    totp_enabled = models.BooleanField(default=False, help_text="Legacy TOTP status field")
    backup_codes_remaining = models.PositiveIntegerField(default=10, help_text="Number of unused backup codes")
    
    # User Preferences
    language = models.CharField(max_length=10, default='en', help_text="User's preferred language code")
    timezone = models.CharField(max_length=50, default='UTC', help_text="User's preferred timezone")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "accounts_user_profile"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self) -> str:
        """Return string representation of the user profile."""
        return f"Profile for {self.user.email}"

# Note: Using standard django-otp TOTPDevice model instead of custom model
# to avoid circular dependencies in migrations


class BackupCode(models.Model):
    """
    Backup codes for Multi-Factor Authentication.
    
    These codes can be used as a fallback when the primary MFA method
    (TOTP) is not available. Each code can only be used once.
    
    Attributes:
        user (User): Foreign key to the User who owns this backup code
        code (str): The backup code string (unique across all users)
        used (bool): Whether this backup code has been used
        used_at (datetime): When the backup code was used (if used)
        created_at (datetime): When the backup code was created
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backup_codes')
    code = models.CharField(max_length=10, unique=True, help_text="Unique backup code string")
    used = models.BooleanField(default=False, help_text="Whether this code has been used")
    used_at = models.DateTimeField(null=True, blank=True, help_text="When the code was used")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "accounts_backup_code"
        verbose_name = "Backup Code"
        verbose_name_plural = "Backup Codes"
        indexes = [
            models.Index(fields=['user', 'used']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self) -> str:
        """Return string representation of the backup code."""
        status = "used" if self.used else "unused"
        return f"Backup code for {self.user.email} ({status})"
    
    def mark_as_used(self) -> None:
        """
        Mark this backup code as used.
        
        Sets the used flag to True and records the current timestamp.
        """
        self.used = True
        self.used_at = timezone.now()
        self.save(update_fields=['used', 'used_at'])


class PasswordResetToken(models.Model):
    """
    Password reset tokens for secure password reset functionality.
    
    These tokens are generated when a user requests a password reset
    and are used to verify the reset request.
    
    Attributes:
        user (User): Foreign key to the User who requested the reset
        token (str): Unique token for password reset
        created_at (datetime): When the token was created
        expires_at (datetime): When the token expires
        used (bool): Whether this token has been used
        used_at (datetime): When the token was used (if used)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True, help_text="Unique password reset token")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When the token expires")
    used = models.BooleanField(default=False, help_text="Whether this token has been used")
    used_at = models.DateTimeField(null=True, blank=True, help_text="When the token was used")
    
    class Meta:
        db_table = "accounts_password_reset_token"
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self) -> str:
        """Return string representation of the password reset token."""
        status = "used" if self.used else ("expired" if self.is_expired() else "active")
        return f"Password reset token for {self.user.email} ({status})"
    
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the token is valid (not used and not expired)."""
        return not self.used and not self.is_expired()
    
    def mark_as_used(self) -> None:
        """
        Mark this token as used.
        
        Sets the used flag to True and records the current timestamp.
        """
        self.used = True
        self.used_at = timezone.now()
        self.save(update_fields=['used', 'used_at'])
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired tokens from the database."""
        cls.objects.filter(expires_at__lt=timezone.now()).delete()


class UserSession(models.Model):
    """
    Track user sessions for security and management purposes.
    
    This model tracks active user sessions to provide session management
    functionality and security monitoring.
    
    Attributes:
        user (User): Foreign key to the User who owns this session
        session_id (str): Unique session identifier
        session_key (str): Django session key (if applicable)
        jwt_jti (str): JWT token ID for tracking JWT tokens
        ip_address (str): IP address from which the session was created
        user_agent (str): User agent string from the browser
        device_info (dict): Parsed device information
        location_info (dict): Location information (if available)
        created_at (datetime): When the session was created
        last_activity (datetime): When the session was last active
        expires_at (datetime): When the session expires
        is_active (bool): Whether the session is currently active
        is_current (bool): Whether this is the current session
        revoked_at (datetime): When the session was revoked (if revoked)
        revoked_by (str): Who revoked the session ('user', 'admin', 'system')
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_id = models.CharField(max_length=255, unique=True, help_text="Unique session identifier")
    session_key = models.CharField(max_length=40, null=True, blank=True, help_text="Django session key")
    jwt_jti = models.CharField(max_length=255, null=True, blank=True, help_text="JWT token ID")
    
    # Session metadata
    ip_address = models.GenericIPAddressField(help_text="IP address from which session was created")
    user_agent = models.TextField(help_text="User agent string from browser")
    device_info = models.JSONField(default=dict, blank=True, help_text="Parsed device information")
    location_info = models.JSONField(default=dict, blank=True, help_text="Location information")
    
    # Session tracking
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="When the session expires")
    
    # Session status
    is_active = models.BooleanField(default=True, help_text="Whether the session is currently active")
    is_current = models.BooleanField(default=False, help_text="Whether this is the current session")
    revoked_at = models.DateTimeField(null=True, blank=True, help_text="When the session was revoked")
    revoked_by = models.CharField(max_length=50, null=True, blank=True, help_text="Who revoked the session")
    
    class Meta:
        db_table = "accounts_user_session"
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['jwt_jti']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self) -> str:
        """Return string representation of the user session."""
        return f"Session for {self.user.email} from {self.ip_address}"
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return timezone.now() > self.expires_at
    
    def revoke(self, revoked_by: str = 'user') -> None:
        """
        Revoke the session.
        
        Args:
            revoked_by: Who is revoking the session ('user', 'admin', 'system')
        """
        self.is_active = False
        self.revoked_at = timezone.now()
        self.revoked_by = revoked_by
        self.save(update_fields=['is_active', 'revoked_at', 'revoked_by'])
    
    def get_device_name(self) -> str:
        """Get a human-readable device name."""
        device_info = self.device_info
        if not device_info:
            return "Unknown Device"
        
        device_type = device_info.get('device_type', 'Unknown')
        browser = device_info.get('browser', 'Unknown Browser')
        os = device_info.get('os', 'Unknown OS')
        
        return f"{device_type} - {browser} on {os}"
    
    def get_location_name(self) -> str:
        """Get a human-readable location."""
        location = self.location_info
        if not location:
            return "Unknown Location"
        
        city = location.get('city', '')
        country = location.get('country', '')
        
        if city and country:
            return f"{city}, {country}"
        elif country:
            return country
        else:
            return "Unknown Location"
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    @classmethod
    def cleanup_expired_sessions(cls) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        from datetime import timedelta
        
        expired_sessions = cls.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
        count = expired_sessions.count()
        expired_sessions.update(
            is_active=False,
            revoked_at=timezone.now(),
            revoked_by='system'
        )
        return count


class AuthEvent(models.Model):
    """
    Track authentication events for security monitoring.
    
    This model logs various authentication-related events for security
    monitoring and audit purposes.
    
    Attributes:
        user (User): Foreign key to the User (if applicable)
        event_type (str): Type of authentication event
        success (bool): Whether the event was successful
        ip_address (str): IP address from which the event occurred
        user_agent (str): User agent string from the browser
        details (dict): Additional event details
        created_at (datetime): When the event occurred
    """
    EVENT_TYPES = (
        ('login_success', 'Login Success'),
        ('login_failed', 'Login Failed'),
        ('login_mfa_required', 'Login - MFA Required'),
        ('logout', 'Logout'),
        ('register', 'Registration'),
        ('password_change', 'Password Change'),
        ('password_reset_requested', 'Password Reset Requested'),
        ('password_reset_confirmed', 'Password Reset Confirmed'),
        ('mfa_enroll', 'MFA Enrolled'),
        ('mfa_verify', 'MFA Verification'),
        ('mfa_disable', 'MFA Disabled'),
        ('backup_codes_viewed', 'Backup Codes Viewed'),
        ('backup_codes_regenerated', 'Backup Codes Regenerated'),
        ('profile_updated', 'Profile Updated'),
        ('profile_update_failed', 'Profile Update Failed'),
        ('session_revoked', 'Session Revoked'),
        ('session_created', 'Session Created'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_events', 
                           null=True, blank=True, help_text="User associated with the event")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, help_text="Type of authentication event")
    success = models.BooleanField(help_text="Whether the event was successful")
    
    # Request metadata
    ip_address = models.GenericIPAddressField(help_text="IP address from which event occurred")
    user_agent = models.TextField(blank=True, help_text="User agent string from browser")
    
    # Additional event details
    details = models.JSONField(default=dict, blank=True, help_text="Additional event details")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "accounts_auth_event"
        verbose_name = "Authentication Event"
        verbose_name_plural = "Authentication Events"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['event_type', 'success']),
        ]
    
    def __str__(self) -> str:
        """Return string representation of the authentication event."""
        user_email = self.user.email if self.user else 'Anonymous'
        status = "Success" if self.success else "Failed"
        return f"{self.get_event_type_display()} - {user_email} ({status})"

