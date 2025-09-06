"""
Authentication constants and configuration values.
"""

# MFA Configuration
MFA_TOKEN_EXPIRY_MINUTES = 5
TOTP_SECRET_LENGTH = 20  # bytes
BACKUP_CODE_LENGTH = 8
BACKUP_CODE_COUNT = 10

# Security Settings
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION_MINUTES = 15
PASSWORD_CHANGE_REQUIRED = True

# JWT Settings
ACCESS_TOKEN_LIFETIME_MINUTES = 60
REFRESH_TOKEN_LIFETIME_DAYS = 7

# Cleanup Settings
UNCONFIRMED_TOTP_RETENTION_HOURS = 24
USED_BACKUP_CODE_RETENTION_DAYS = 90

# Error Codes
class ErrorCodes:
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    PERMISSION_DENIED = 'PERMISSION_DENIED'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED'
    RATE_LIMITED = 'RATE_LIMITED'
    INTERNAL_ERROR = 'INTERNAL_ERROR'
    
    # Authentication specific
    INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
    MFA_REQUIRED = 'MFA_REQUIRED'
    MFA_INVALID_CODE = 'MFA_INVALID_CODE'
    MFA_EXPIRED_TOKEN = 'MFA_EXPIRED_TOKEN'
    MFA_DEVICE_NOT_FOUND = 'MFA_DEVICE_NOT_FOUND'
    MFA_ALREADY_ENROLLED = 'MFA_ALREADY_ENROLLED'
    MFA_NOT_ENROLLED = 'MFA_NOT_ENROLLED'

# Response Messages
class Messages:
    # Success messages
    LOGIN_SUCCESS = 'Login successful'
    LOGOUT_SUCCESS = 'Logout successful'
    MFA_ENROLLED = 'MFA enrolled successfully'
    MFA_DISABLED = 'MFA disabled successfully'
    PASSWORD_CHANGED = 'Password changed successfully'
    PROFILE_UPDATED = 'Profile updated successfully'
    
    # Error messages
    INVALID_CREDENTIALS = 'Invalid email or password'
    ACCOUNT_DISABLED = 'Account is disabled. Please contact support'
    ACCOUNT_LOCKED = 'Account temporarily locked due to too many failed attempts'
    MFA_REQUIRED = 'Multi-factor authentication required'
    MFA_INVALID_CODE = 'Invalid authentication code'
    MFA_EXPIRED_TOKEN = 'Authentication session expired. Please log in again'
    MFA_DEVICE_NOT_FOUND = 'MFA device not found'
    MFA_ALREADY_ENROLLED = 'Multi-factor authentication is already enabled'
    MFA_NOT_ENROLLED = 'Multi-factor authentication is not enabled'
    
    # General errors
    VALIDATION_ERROR = 'Please check your input and try again'
    PERMISSION_DENIED = 'You do not have permission to perform this action'
    RATE_LIMITED = 'Too many requests. Please wait before trying again'
    INTERNAL_ERROR = 'An internal error occurred. Please try again later'