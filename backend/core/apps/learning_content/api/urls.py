# File: backend/core/apps/learning_content/api/urls.py
# Description: URL routing for learning path API endpoints
# Why: Maps URLs to view handlers for learning path operations
# Relevant Files: views.py, core/urls.py

from django.urls import path
from .views import (
    GenerateLearningPathView,
    ListLearningPathsView,
    LearningPathDetailView,
    StartLearningPathView,
    UpdateProgressView,
    CustomizeLearningPathView,
    GetProgressAnalyticsView,
    MyLearningPathsView,
)

app_name = 'learning_content'

urlpatterns = [
    # Generation
    path('generate/', GenerateLearningPathView.as_view(), name='generate-learning-path'),

    # Dashboard view (must come before <path_id> to avoid conflicts)
    path('my/', MyLearningPathsView.as_view(), name='my-learning-paths'),

    # Listing and detail
    path('', ListLearningPathsView.as_view(), name='list-learning-paths'),
    path('<str:path_id>/', LearningPathDetailView.as_view(), name='learning-path-detail'),

    # Actions on specific paths
    path('<str:path_id>/start/', StartLearningPathView.as_view(), name='start-learning-path'),
    path('<str:path_id>/progress/', UpdateProgressView.as_view(), name='update-progress'),
    path('<str:path_id>/customize/', CustomizeLearningPathView.as_view(), name='customize-path'),
    path('<str:path_id>/analytics/', GetProgressAnalyticsView.as_view(), name='path-analytics'),
]
