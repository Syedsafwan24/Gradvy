from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager
from django_otp.plugins.otp_totp.models import TOTPDevice

class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    # Core fields
    email = models.EmailField(unique=True, verbose_name="Email Address")
    employee_id = models.CharField(max_length=32, unique=True, verbose_name="Employee ID")
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

    # Module Access
    modules = models.ManyToManyField('Module', blank=True, related_name='users')
    
    # Manager
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["employee_id"]
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "auth_user"
    
    def __str__(self):
        return f"{self.employee_id} - {self.email}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_locked(self):
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Contact
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    
    # MFA Settings
    totp_enabled = models.BooleanField(default=False)
    backup_codes_remaining = models.PositiveIntegerField(default=10)
    
    # Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "accounts_user_profile"
    
    def __str__(self):
        return f"Profile for {self.user.employee_id}"

class UserTOTPDevice(TOTPDevice):
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = "accounts_user_totp_device"
        verbose_name = "TOTP Device"
        verbose_name_plural = "TOTP Devices"
    
    def __str__(self):
        return f"TOTP Device for {self.user.employee_id}"

class BackupCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backup_codes')
    code = models.CharField(max_length=10, unique=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "accounts_backup_code"
    
    def __str__(self):
        return f"Backup code for {self.user.employee_id}"

class AuthAuditLog(models.Model):
    EVENT_TYPES = [
        ('login_success', 'Login Success'),
        ('login_failure', 'Login Failure'),
        ('logout', 'Logout'),
        ('mfa_enroll', 'MFA Enrollment'),
        ('mfa_verify', 'MFA Verification'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('account_lock', 'Account Locked'),
        ('account_unlock', 'Account Unlocked'),
        ('session_revoke', 'Session Revoked'),
        ('jwt_refresh', 'JWT Refresh'),
        ('jwt_blacklist', 'JWT Blacklisted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_info = models.JSONField(default=dict)
    location = models.CharField(max_length=100, blank=True)
    success = models.BooleanField(default=True)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "accounts_auth_audit_log"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} for {self.user.employee_id} at {self.created_at}"
