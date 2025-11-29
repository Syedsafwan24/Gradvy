# File: backend/core/apps/learning_content/api/urls.py
# Description: URL routing for learning path API endpoints
# Why: Maps URLs to view handlers for learning path operations
# Relevant Files: views.py, quiz_views.py, core/urls.py

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
    UpdatePathStatusView,  # Phase 2: Status management
    DeletePathView,  # Phase 2: Path deletion
)
from .quiz_views import (
    GetOrCreateQuizView,
    StartQuizAttemptView,
    SubmitQuizView,
    GetQuizAttemptView,
    GetQuizAttemptsView,
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

    # Phase 2: Path management endpoints
    path('<str:path_id>/status/', UpdatePathStatusView.as_view(), name='update-path-status'),
    path('<str:path_id>/delete/', DeletePathView.as_view(), name='delete-path'),

    # Quiz endpoints
    path('quizzes/<str:path_id>/<str:lesson_id>/', GetOrCreateQuizView.as_view(), name='get-quiz'),
    path('quizzes/<int:quiz_id>/start/', StartQuizAttemptView.as_view(), name='start-quiz-attempt'),
    path('quizzes/attempts/<int:attempt_id>/submit/', SubmitQuizView.as_view(), name='submit-quiz'),
    path('quizzes/attempts/<int:attempt_id>/', GetQuizAttemptView.as_view(), name='get-quiz-attempt'),
    path('quizzes/<str:path_id>/<str:lesson_id>/attempts/', GetQuizAttemptsView.as_view(), name='get-quiz-attempts'),
]
