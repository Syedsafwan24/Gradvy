from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.CookieTokenRefreshView.as_view(), name='token_refresh'),
    
    # Password management
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # MFA
    path('mfa/verify/', views.MFAVerifyView.as_view(), name='mfa_verify'),
    path('mfa/enroll/', views.MFAEnrollmentView.as_view(), name='mfa_enroll'),
    path('mfa/disable/', views.MFADisableView.as_view(), name='mfa_disable'),
    path('mfa/status/', views.MFAStatusView.as_view(), name='mfa_status'),
    path('mfa/backup-codes/', views.MFABackupCodesView.as_view(), name='mfa_backup_codes'),
    
    # User management
    path('me/', views.UserProfileView.as_view(), name='profile'),
    
    # CSRF token
    path('csrf-token/', views.CSRFTokenView.as_view(), name='csrf_token'),
    
    # Session management
    path('sessions/', views.UserSessionsView.as_view(), name='user_sessions'),
    path('sessions/revoke/', views.RevokeSessionView.as_view(), name='revoke_session'),
    path('sessions/revoke-all/', views.RevokeAllSessionsView.as_view(), name='revoke_all_sessions'),
    path('sessions/activity/', views.SessionActivityView.as_view(), name='session_activity'),
]
