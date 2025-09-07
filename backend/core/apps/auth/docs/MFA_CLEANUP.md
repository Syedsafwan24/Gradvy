# MFA Cleanup Background Task

## Overview

This implementation adds automatic cleanup of MFA-related data when a user disables Multi-Factor Authentication (MFA). The cleanup is performed in the background using Celery tasks.

## Components Added

### 1. Background Task (`cleanup_user_mfa_data`)
- **Location**: `backend/core/apps/auth/tasks/tasks.py`
- **Purpose**: Cleans up all MFA-related data for a specific user
- **What it cleans**:
  - All backup codes (used and unused) for the user
  - Unconfirmed TOTP devices for the user

### 2. Modified MFA Disable View
- **Location**: `backend/core/apps/auth/api/views.py` - `MFADisableView`
- **Enhancement**: Now triggers the cleanup task when MFA is disabled
- **Configurable**: Can run cleanup immediately or with a delay

### 3. Settings Configuration
- **Location**: `backend/core/settings/base.py`
- **New Setting**: `MFA_CLEANUP_ON_DISABLE_IMMEDIATE = True`
  - `True`: Cleanup runs immediately when MFA is disabled
  - `False`: Cleanup runs with a 5-minute delay (allows recovery time)

### 4. Management Command
- **Location**: `backend/core/apps/auth/management/commands/cleanup_mfa.py`
- **Usage**:
  ```bash
  # Clean up for specific user by ID
  python manage.py cleanup_mfa --user-id 123
  
  # Clean up for specific user by email
  python manage.py cleanup_mfa --user-email user@example.com
  
  # Run general cleanup (old devices and used backup codes)
  python manage.py cleanup_mfa --general
  ```

## Flow

1. User clicks "Disable MFA" in the frontend
2. Frontend calls the MFA disable API endpoint
3. Backend:
   - Deletes confirmed TOTP devices
   - Sets `mfa_enrolled = False`
   - Triggers background cleanup task
   - Returns success response
4. Background task (asynchronously):
   - Deletes all backup codes for the user
   - Deletes unconfirmed TOTP devices
   - Logs completion

## Benefits

1. **Non-blocking**: UI responds immediately, cleanup happens in background
2. **Complete cleanup**: Removes all MFA artifacts, not just active devices
3. **Configurable**: Can be immediate or delayed based on requirements
4. **Logged**: All cleanup actions are logged for audit purposes
5. **Minimal changes**: Leverages existing Celery infrastructure
6. **Testable**: Management command allows manual testing and maintenance

## Security Considerations

- Backup codes are permanently deleted (cannot be recovered)
- User will need to re-enable MFA from scratch if they change their mind
- Cleanup is logged for security audit purposes
- Delay option provides a grace period for accidental disables

## Existing Cleanup Task

The existing `clean_mfa_data()` task continues to work for routine maintenance:
- Cleans up old unconfirmed TOTP devices (24 hours old)
- Cleans up old used backup codes (90 days old)

This new task complements it by handling immediate cleanup when MFA is intentionally disabled.
