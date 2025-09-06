from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password management
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # MFA
    path('mfa/verify/', views.MFAVerifyView.as_view(), name='mfa_verify'),
    path('mfa/enroll/', views.MFAEnrollmentView.as_view(), name='mfa_enroll'),
    path('mfa/disable/', views.MFADisableView.as_view(), name='mfa_disable'),
    
    # User management
    path('me/', views.UserProfileView.as_view(), name='profile'),
]
