from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, UserProfile, BackupCode, PasswordResetToken, UserSession, AuthEvent
from .social_models import (
    SocialProvider, SocialAccount, SocialAuthEvent, SocialDataCollection,
    SocialProfileEnrichment, SocialWebhook
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'is_active', 'is_staff', 'mfa_enrolled', 
                   'is_locked', 'failed_login_attempts', 'date_joined', 'last_login']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'mfa_enrolled', 
                  'must_change_password', 'date_joined', 'last_login', 'last_password_change']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    filter_horizontal = ('groups', 'user_permissions')
    date_hierarchy = 'date_joined'
    list_per_page = 50
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                  'groups', 'user_permissions')}),
        ('Security & MFA', {'fields': ('must_change_password', 'mfa_enrolled', 
                                     'failed_login_attempts', 'locked_until')}),
        ('Important dates', {'fields': ('date_joined', 'last_login', 'last_password_change')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
        ('Security Settings', {
            'classes': ('wide',),
            'fields': ('is_active', 'must_change_password'),
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'unlock_users', 'reset_failed_attempts']
    
    def full_name(self, obj):
        """Display user's full name"""
        full_name = obj.get_full_name()
        return full_name if full_name else '-'
    full_name.short_description = 'Full Name'
    
    def is_locked(self, obj):
        if obj.is_locked:
            return format_html('<span style="color: red;">🔒 Locked</span>')
        return format_html('<span style="color: green;">✅ Active</span>')
    is_locked.short_description = 'Account Status'
    
    def activate_users(self, request, queryset):
        """Admin action to activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Admin action to deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were deactivated.')
    deactivate_users.short_description = "Deactivate selected users"
    
    def unlock_users(self, request, queryset):
        """Admin action to unlock users"""
        updated = queryset.update(locked_until=None, failed_login_attempts=0)
        self.message_user(request, f'{updated} users were unlocked.')
    unlock_users.short_description = "Unlock selected users"
    
    def reset_failed_attempts(self, request, queryset):
        """Admin action to reset failed login attempts"""
        updated = queryset.update(failed_login_attempts=0)
        self.message_user(request, f'Failed login attempts reset for {updated} users.')
    reset_failed_attempts.short_description = "Reset failed login attempts"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'totp_enabled', 'backup_codes_remaining', 
                   'language', 'timezone', 'created_at']
    list_filter = ['totp_enabled', 'language', 'timezone', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone_number']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'bio')
        }),
        ('MFA Settings', {
            'fields': ('totp_enabled', 'backup_codes_remaining')
        }),
        ('Preferences', {
            'fields': ('language', 'timezone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['reset_backup_codes']
    
    def reset_backup_codes(self, request, queryset):
        """Admin action to reset backup codes count"""
        updated = queryset.update(backup_codes_remaining=10)
        self.message_user(request, f'Backup codes reset for {updated} profiles.')
    reset_backup_codes.short_description = "Reset backup codes to 10"

# UserTOTPDevice admin removed - using standard django-otp TOTPDevice admin instead

@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code_display', 'status', 'used_at', 'created_at']
    list_filter = ['used', 'created_at', 'used_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    date_hierarchy = 'created_at'
    list_per_page = 100
    readonly_fields = ['code', 'used_at', 'created_at']
    
    fieldsets = (
        ('Code Information', {
            'fields': ('user', 'code', 'used')
        }),
        ('Usage Information', {
            'fields': ('used_at', 'created_at')
        }),
    )
    
    actions = ['mark_as_used', 'regenerate_codes']
    
    def code_display(self, obj):
        """Display truncated code for security"""
        return f"{obj.code[:4]}****"
    code_display.short_description = 'Code'
    
    def status(self, obj):
        """Display code status with colors"""
        if obj.used:
            return format_html('<span style="color: red;">✗ Used</span>')
        else:
            return format_html('<span style="color: green;">✓ Available</span>')
    status.short_description = 'Status'
    
    def mark_as_used(self, request, queryset):
        """Admin action to mark codes as used"""
        updated = 0
        for code in queryset.filter(used=False):
            code.mark_as_used()
            updated += 1
        self.message_user(request, f'{updated} backup codes marked as used.')
    mark_as_used.short_description = "Mark selected codes as used"


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_display', 'status', 'created_at', 'expires_at']
    list_filter = ['used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']
    date_hierarchy = 'created_at'
    
    def token_display(self, obj):
        """Display truncated token for security"""
        return f"{obj.token[:8]}...{obj.token[-4:]}"
    token_display.short_description = 'Token'
    
    def status(self, obj):
        """Display token status with colors"""
        if obj.used:
            return format_html('<span style="color: red;">Used</span>')
        elif obj.is_expired():
            return format_html('<span style="color: orange;">Expired</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')
    status.short_description = 'Status'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_display', 'ip_address', 'device_name', 
                   'status', 'created_at', 'last_activity']
    list_filter = ['is_active', 'is_current', 'created_at', 'last_activity']
    search_fields = ['user__email', 'ip_address', 'user_agent']
    readonly_fields = ['session_id', 'session_key', 'jwt_jti', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Session Info', {
            'fields': ('user', 'session_id', 'session_key', 'jwt_jti')
        }),
        ('Device Info', {
            'fields': ('ip_address', 'user_agent', 'device_info', 'location_info')
        }),
        ('Status', {
            'fields': ('is_active', 'is_current', 'revoked_at', 'revoked_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_activity', 'expires_at')
        }),
    )
    
    def session_display(self, obj):
        """Display truncated session ID"""
        return f"{obj.session_id[:12]}..."
    session_display.short_description = 'Session ID'
    
    def device_name(self, obj):
        """Display device name from parsed info"""
        return obj.get_device_name()
    device_name.short_description = 'Device'
    
    def status(self, obj):
        """Display session status with colors"""
        if not obj.is_active:
            return format_html('<span style="color: red;">Inactive</span>')
        elif obj.is_expired():
            return format_html('<span style="color: orange;">Expired</span>')
        elif obj.is_current:
            return format_html('<span style="color: green;">Current</span>')
        else:
            return format_html('<span style="color: blue;">Active</span>')
    status.short_description = 'Status'


@admin.register(AuthEvent)
class AuthEventAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'event_type', 'success_status', 'ip_address', 'created_at']
    list_filter = ['event_type', 'success', 'created_at']
    search_fields = ['user__email', 'ip_address', 'event_type']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Event Info', {
            'fields': ('user', 'event_type', 'success')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Additional Details', {
            'fields': ('details', 'created_at')
        }),
    )
    
    def user_display(self, obj):
        """Display user email or Anonymous"""
        return obj.user.email if obj.user else 'Anonymous'
    user_display.short_description = 'User'
    
    def success_status(self, obj):
        """Display success status with colors"""
        if obj.success:
            return format_html('<span style="color: green;">✅ Success</span>')
        else:
            return format_html('<span style="color: red;">❌ Failed</span>')
    success_status.short_description = 'Status'


# Social Authentication Admin


@admin.register(SocialProvider)
class SocialProviderAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'status', 'account_count', 'auto_register', 'created_at']
    list_filter = ['is_active', 'auto_register', 'require_email_verification', 'collect_extended_profile', 'created_at']
    search_fields = ['name', 'display_name', 'client_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'is_active')
        }),
        ('OAuth Configuration', {
            'fields': ('client_id', 'client_secret', 'authorize_url', 'token_url', 'user_info_url'),
            'classes': ('collapse',)
        }),
        ('Scopes & Data Collection', {
            'fields': ('default_scopes', 'optional_scopes', 'field_mappings'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('auto_register', 'require_email_verification', 'collect_extended_profile')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['activate_providers', 'deactivate_providers', 'enable_auto_register']
    
    def status(self, obj):
        """Display provider status with colors"""
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Active</span>')
        else:
            return format_html('<span style="color: red;">❌ Inactive</span>')
    status.short_description = 'Status'
    
    def account_count(self, obj):
        """Display number of connected accounts"""
        return obj.socialaccount_set.count()
    account_count.short_description = 'Connected Accounts'
    
    def activate_providers(self, request, queryset):
        """Admin action to activate providers"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} providers were activated.')
    activate_providers.short_description = "Activate selected providers"
    
    def deactivate_providers(self, request, queryset):
        """Admin action to deactivate providers"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} providers were deactivated.')
    deactivate_providers.short_description = "Deactivate selected providers"
    
    def enable_auto_register(self, request, queryset):
        """Admin action to enable auto registration"""
        updated = queryset.update(auto_register=True)
        self.message_user(request, f'Auto registration enabled for {updated} providers.')
    enable_auto_register.short_description = "Enable auto registration"


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'username', 'connection_status', 'last_sync', 'data_completeness', 'sync_frequency']
    list_filter = ['provider', 'is_active', 'connection_method', 'sync_frequency', 'data_collection_consent', 'created_at']
    search_fields = ['user__email', 'username', 'email', 'provider_user_id']
    readonly_fields = ['provider_user_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Account Info', {
            'fields': ('user', 'provider', 'provider_user_id', 'username', 'email')
        }),
        ('Connection Status', {
            'fields': ('is_active', 'connection_method', 'last_sync', 'sync_frequency')
        }),
        ('OAuth Tokens', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at', 'scopes_granted'),
            'classes': ('collapse',)
        }),
        ('Profile Data', {
            'fields': ('profile_data', 'raw_profile_data'),
            'classes': ('collapse',)
        }),
        ('Privacy Settings', {
            'fields': ('data_collection_consent', 'public_profile_allowed', 'analytics_consent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['sync_profile_data', 'revoke_access', 'enable_data_collection']
    
    def connection_status(self, obj):
        """Display connection status with colors"""
        if not obj.is_active:
            return format_html('<span style="color: red;">❌ Inactive</span>')
        elif obj.is_token_expired:
            return format_html('<span style="color: orange;">⚠️ Token Expired</span>')
        else:
            return format_html('<span style="color: green;">✅ Connected</span>')
    connection_status.short_description = 'Status'
    
    def data_completeness(self, obj):
        """Display data completeness percentage"""
        completeness = obj.profile_data.get('data_completeness', 0)
        if completeness >= 80:
            color = 'green'
        elif completeness >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html(f'<span style="color: {color};">{completeness}%</span>')
    data_completeness.short_description = 'Data Complete'
    
    def sync_profile_data(self, request, queryset):
        """Admin action to trigger profile data sync"""
        updated = 0
        for account in queryset.filter(is_active=True):
            # This would trigger a sync task in production
            account.last_sync = timezone.now()
            account.save()
            updated += 1
        self.message_user(request, f'Sync triggered for {updated} social accounts.')
    sync_profile_data.short_description = "Trigger profile data sync"
    
    def revoke_access(self, request, queryset):
        """Admin action to revoke social account access"""
        updated = queryset.update(is_active=False, data_collection_consent=False)
        self.message_user(request, f'Access revoked for {updated} social accounts.')
    revoke_access.short_description = "Revoke access for selected accounts"
    
    def enable_data_collection(self, request, queryset):
        """Admin action to enable data collection consent"""
        updated = queryset.update(data_collection_consent=True)
        self.message_user(request, f'Data collection enabled for {updated} accounts.')
    enable_data_collection.short_description = "Enable data collection consent"


@admin.register(SocialAuthEvent)
class SocialAuthEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'event_type', 'success_status', 'created_at']
    list_filter = ['provider', 'event_type', 'success', 'created_at']
    search_fields = ['user__email', 'error_message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Event Info', {
            'fields': ('user', 'social_account', 'provider', 'event_type', 'success')
        }),
        ('Event Details', {
            'fields': ('details', 'error_message')
        }),
        ('Request Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at')
        }),
    )
    
    def success_status(self, obj):
        """Display success status with colors"""
        if obj.success:
            return format_html('<span style="color: green;">✅ Success</span>')
        else:
            return format_html('<span style="color: red;">❌ Failed</span>')
    success_status.short_description = 'Status'


@admin.register(SocialDataCollection)
class SocialDataCollectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'collection_type', 'consent_status_display', 
                   'last_collection', 'data_points_collected']
    list_filter = ['provider', 'collection_type', 'consent_status', 'created_at']
    search_fields = ['user__email', 'purpose']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Collection Info', {
            'fields': ('user', 'provider', 'collection_type', 'purpose')
        }),
        ('Consent Management', {
            'fields': ('consent_status', 'consent_granted_at', 'consent_expires_at', 'consent_revoked_at')
        }),
        ('Data Collection Settings', {
            'fields': ('required_scopes', 'optional_scopes', 'data_retention_days')
        }),
        ('Collection Results', {
            'fields': ('last_collection', 'collection_count', 'data_points_collected')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def consent_status_display(self, obj):
        """Display consent status with colors"""
        status_colors = {
            'granted': 'green',
            'pending': 'orange',
            'denied': 'red',
            'revoked': 'red',
            'expired': 'gray'
        }
        color = status_colors.get(obj.consent_status, 'black')
        return format_html(f'<span style="color: {color};">{obj.get_consent_status_display()}</span>')
    consent_status_display.short_description = 'Consent Status'


@admin.register(SocialProfileEnrichment)
class SocialProfileEnrichmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'social_account', 'enrichment_type', 'confidence_display', 
                   'validation_status', 'created_at']
    list_filter = ['enrichment_type', 'is_validated', 'created_at']
    search_fields = ['user__email', 'extraction_method', 'validated_by']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Enrichment Info', {
            'fields': ('user', 'social_account', 'enrichment_type', 'confidence_score')
        }),
        ('Data', {
            'fields': ('enrichment_data', 'source_data'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('extraction_method', 'processing_version')
        }),
        ('Validation', {
            'fields': ('is_validated', 'validated_by', 'validation_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def confidence_display(self, obj):
        """Display confidence score with colors"""
        score = obj.confidence_score
        if score >= 0.8:
            color = 'green'
        elif score >= 0.5:
            color = 'orange'
        else:
            color = 'red'
        return format_html(f'<span style="color: {color};">{score:.2f}</span>')
    confidence_display.short_description = 'Confidence'
    
    def validation_status(self, obj):
        """Display validation status"""
        if obj.is_validated:
            return format_html('<span style="color: green;">✅ Validated</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    validation_status.short_description = 'Validated'


@admin.register(SocialWebhook)
class SocialWebhookAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'webhook_status', 'events_received', 'last_event_received']
    list_filter = ['provider', 'is_active', 'created_at']
    search_fields = ['user__email', 'webhook_url']
    readonly_fields = ['events_received', 'last_event_received', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Webhook Info', {
            'fields': ('provider', 'user', 'webhook_url', 'webhook_secret')
        }),
        ('Configuration', {
            'fields': ('subscribed_events', 'is_active', 'retry_attempts', 'timeout_seconds')
        }),
        ('Statistics', {
            'fields': ('events_received', 'last_event_received')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def webhook_status(self, obj):
        """Display webhook status with colors"""
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Active</span>')
        else:
            return format_html('<span style="color: red;">❌ Inactive</span>')
    webhook_status.short_description = 'Status'

