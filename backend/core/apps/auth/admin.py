from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, BackupCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 
                   'is_active', 'is_staff', 'mfa_enrolled', 'is_locked']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'mfa_enrolled', 
                  'date_joined', 'last_login']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    filter_horizontal = ('groups', 'user_permissions')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                  'groups', 'user_permissions')}),
        ('Security', {'fields': ('must_change_password', 'mfa_enrolled', 
                               'failed_login_attempts', 'locked_until')}),
        ('Important dates', {'fields': ()}),
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
    )
    
    def is_locked(self, obj):
        if obj.is_locked:
            return format_html('<span style="color: red;">🔒 Locked</span>')
        return format_html('<span style="color: green;">✅ Active</span>')
    is_locked.short_description = 'Status'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
    search_fields = ['user__email']

# UserTOTPDevice admin removed - using standard django-otp TOTPDevice admin instead

@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'used', 'used_at', 'created_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__email', 'code']

