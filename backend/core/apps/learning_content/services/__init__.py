# File: backend/core/apps/learning_content/services/__init__.py
# Description: Services package for learning content - quiz generation, content scraping
# Why: Provides business logic layer for quiz orchestration and content extraction
# Relevant Files: content_scraper_service.py, quiz_orchestrator_service.py

from .content_scraper_service import ContentScraperService
from .quiz_orchestrator_service import QuizOrchestratorService

__all__ = [
    'ContentScraperService',
    'QuizOrchestratorService',
]
