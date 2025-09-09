"""
URL patterns for user preferences and personalization API endpoints.
"""
from django.urls import path
from . import views

app_name = 'preferences'

urlpatterns = [
    # Main preferences CRUD
    path('', views.UserPreferenceView.as_view(), name='user_preferences'),
    
    # Onboarding flow
    path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
    path('quick-onboarding/', views.QuickOnboardingView.as_view(), name='quick_onboarding'),
    
    # Interaction tracking
    path('interactions/', views.InteractionLogView.as_view(), name='log_interaction'),
    
    # Analytics and insights
    path('analytics/', views.UserAnalyticsView.as_view(), name='user_analytics'),
    
    # Personalized recommendations
    path('recommendations/', views.PersonalizedRecommendationsView.as_view(), name='recommendations'),
    
    # Utility endpoints
    path('choices/', views.PreferenceChoicesView.as_view(), name='preference_choices'),
    
    # Privacy and data management
    path('privacy-overview/', views.privacy_overview, name='privacy_overview'),
    path('privacy-quick-toggle/', views.privacy_quick_toggle, name='privacy_quick_toggle'),
    path('data-collection-settings/', views.data_collection_settings, name='data_collection_settings'),
    path('consent/<str:consent_id>/', views.update_consent, name='update_consent'),
    path('consent/revoke-all/', views.revoke_all_consents, name='revoke_all_consents'),
    path('consent-history/download/', views.download_consent_history, name='download_consent_history'),
]