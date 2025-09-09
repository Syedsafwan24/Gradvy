"""
URL routing for social authentication endpoints
"""

from django.urls import path
from . import social_views

app_name = 'social_auth'

urlpatterns = [
    # OAuth flow endpoints
    path('initiate/', social_views.SocialAuthInitiateView.as_view(), name='initiate'),
    path('callback/', social_views.SocialAuthCallbackView.as_view(), name='callback'),
    
    # Social account management
    path('accounts/', social_views.SocialAccountsView.as_view(), name='accounts'),
    path('accounts/sync/', social_views.SocialDataSyncView.as_view(), name='sync'),
    path('accounts/batch-sync/', social_views.trigger_batch_sync, name='batch_sync'),
    
    # Privacy and data management
    path('privacy/', social_views.SocialPrivacySettingsView.as_view(), name='privacy'),
    path('enrichment/', social_views.SocialProfileEnrichmentView.as_view(), name='enrichment'),
    
    # Provider information
    path('providers/', social_views.social_providers_list, name='providers'),
]