from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, UserTOTPDevice, BackupCode, AuthAuditLog, Module

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'employee_id', 'first_name', 'last_name', 
                   'is_active', 'is_staff', 'mfa_enrolled', 'is_locked']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'mfa_enrolled', 
                  'date_joined', 'last_login', 'modules']
    search_fields = ['email', 'employee_id', 'first_name', 'last_name']
    ordering = ['-date_joined']
    filter_horizontal = ('groups', 'user_permissions', 'modules')
    
    fieldsets = (
        (None, {'fields': ('email', 'employee_id', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                  'groups', 'user_permissions')}),
        ('Module Access', {'fields': ('modules',)}),
        ('Security', {'fields': ('must_change_password', 'mfa_enrolled', 
                               'failed_login_attempts', 'locked_until')}),
        ('Important dates', {'fields': ()}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'employee_id', 'password', 'password2'),
        }),
    )
    
    def is_locked(self, obj):
        if obj.is_locked:
            return format_html('<span style="color: red;">🔒 Locked</span>')
        return format_html('<span style="color: green;">✅ Active</span>')
    is_locked.short_description = 'Status'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'position', 'phone_number']
    list_filter = ['department', 'position']
    search_fields = ['user__email', 'user__employee_id', 'department', 'position']

@admin.register(UserTOTPDevice)
class UserTOTPDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'confirmed', 'last_used']
    list_filter = ['confirmed']
    search_fields = ['user__email', 'user__employee_id', 'name']

@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'used', 'used_at', 'created_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__email', 'user__employee_id', 'code']

@admin.register(AuthAuditLog)
class AuthAuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'event_type', 'ip_address', 'success', 'created_at']
    list_filter = ['event_type', 'success', 'created_at']
    search_fields = ['user__email', 'user__employee_id', 'ip_address']
    readonly_fields = ['user', 'event_type', 'ip_address', 'user_agent', 
                      'device_info', 'location', 'success', 'details', 'created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
