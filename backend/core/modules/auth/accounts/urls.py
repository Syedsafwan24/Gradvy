from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('mfa/verify/', views.MFAVerifyView.as_view(), name='mfa_verify'),
    path('mfa/enroll/', views.MFAEnrollmentView.as_view(), name='mfa_enroll'),
    path('mfa/disable/', views.MFADisableView.as_view(), name='mfa_disable'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management
    path('me/', views.UserProfileView.as_view(), name='profile'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
