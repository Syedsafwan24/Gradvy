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
]