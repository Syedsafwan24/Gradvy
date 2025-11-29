# File: backend/core/apps/learning_content/services/quiz_orchestrator_service.py
# Description: Orchestrator service for quiz generation, combining content scraping and AI question generation
# Why: Coordinates content extraction and quiz creation for lesson assessments
# Relevant Files: content_scraper_service.py, models.py, ml_services/services/question_generator_service.py

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction

from apps.learning_content.models import LessonQuiz, QuizQuestion
from .content_scraper_service import ContentScraperService

logger = logging.getLogger(__name__)


class QuizOrchestratorService:
    """
    Orchestrates quiz generation for lessons.

    Workflow:
    1. Check if quiz already exists (cached)
    2. Scrape lesson content via ContentScraperService
    3. Generate questions via QuestionGeneratorService
    4. Create LessonQuiz and QuizQuestion models
    5. Return quiz with questions

    Implements 30-day caching strategy.
    """

    # Default quiz configuration
    DEFAULT_NUM_QUESTIONS = 5
    DEFAULT_PASSING_SCORE = 70
    CACHE_DAYS = 30

    @classmethod
    def get_or_create_quiz(
        cls,
        path_id: str,
        lesson_id: str,
        lesson_title: str,
        lesson_url: str,
        lesson_platform: str,
        lesson_description: str = "",
        num_questions: int = None,
        force_regenerate: bool = False
    ) -> Optional[LessonQuiz]:
        """
        Get existing quiz or create new one for a lesson.

        Args:
            path_id: Learning path ID
            lesson_id: Lesson ID within the path
            lesson_title: Lesson title
            lesson_url: URL to scrape content from
            lesson_platform: Platform type (youtube, article, github)
            lesson_description: Lesson description (fallback content)
            num_questions: Number of questions to generate (default: 5)
            force_regenerate: Force regeneration even if cached quiz exists

        Returns:
            LessonQuiz instance with questions, or None if generation fails
        """
        num_questions = num_questions or cls.DEFAULT_NUM_QUESTIONS

        try:
            # Step 1: Check for existing quiz (unless force_regenerate)
            if not force_regenerate:
                try:
                    existing_quiz = LessonQuiz.objects.get(path_id=path_id, lesson_id=lesson_id)

                    # Check if cache is still valid
                    if not existing_quiz.is_expired():
                        logger.info(f"✅ Using cached quiz for lesson {lesson_id} (expires {existing_quiz.cache_until})")
                        return existing_quiz
                    else:
                        logger.info(f"⏰ Quiz cache expired for lesson {lesson_id}, regenerating")
                        # Delete old quiz and questions (cascade will handle questions)
                        existing_quiz.delete()

                except LessonQuiz.DoesNotExist:
                    logger.info(f"🆕 No existing quiz for lesson {lesson_id}, generating new one")

            # Step 2: Scrape lesson content
            logger.info(f"🔍 Scraping content from {lesson_url}")
            scraped_data = ContentScraperService.scrape_lesson_content(
                url=lesson_url,
                platform=lesson_platform,
                title=lesson_title,
                description=lesson_description
            )

            content = scraped_data['content']
            content_source = scraped_data['source']
            content_scraped = scraped_data['success']
            content_hash = scraped_data['content_hash']

            if not content or len(content) < 50:
                logger.error(f"Insufficient content scraped for lesson {lesson_id}")
                return None

            logger.info(f"✅ Scraped {scraped_data['word_count']} words from {content_source}")

            # Step 3: Generate questions using QuestionGeneratorService
            questions_data = cls._generate_questions_with_ai(
                content=content,
                lesson_title=lesson_title,
                lesson_platform=lesson_platform,
                num_questions=num_questions
            )

            if not questions_data or len(questions_data) == 0:
                logger.error(f"Question generation failed for lesson {lesson_id}")
                return None

            logger.info(f"✅ Generated {len(questions_data)} questions")

            # Step 4: Create LessonQuiz and QuizQuestion models in a transaction
            with transaction.atomic():
                # Create LessonQuiz
                quiz = LessonQuiz.objects.create(
                    path_id=path_id,
                    lesson_id=lesson_id,
                    lesson_title=lesson_title,
                    lesson_platform=lesson_platform,
                    passing_score_percentage=cls.DEFAULT_PASSING_SCORE,
                    num_questions=len(questions_data),
                    content_scraped=content_scraped,
                    content_source=content_source,
                    scraped_content_hash=content_hash,
                    cache_until=timezone.now() + timedelta(days=cls.CACHE_DAYS)
                )

                # Create QuizQuestion instances
                for idx, question_data in enumerate(questions_data):
                    QuizQuestion.objects.create(
                        quiz=quiz,
                        order=idx,
                        question_text=question_data['question_text'],
                        question_type=question_data['question_type'],
                        options=question_data.get('options', {}),
                        correct_answer=question_data['correct_answer'],
                        explanation=question_data.get('explanation', ''),
                        difficulty=question_data.get('difficulty', 'medium'),
                        blooms_level=question_data.get('blooms_level', ''),
                        points=question_data.get('points', 1)
                    )

                logger.info(f"💾 Created quiz {quiz.id} with {len(questions_data)} questions")

            return quiz

        except Exception as e:
            logger.error(f"Error in get_or_create_quiz for lesson {lesson_id}: {e}", exc_info=True)
            return None

    @classmethod
    def _generate_questions_with_ai(
        cls,
        content: str,
        lesson_title: str,
        lesson_platform: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate questions using QuestionGeneratorService.

        Args:
            content: Scraped lesson content
            lesson_title: Lesson title
            lesson_platform: Platform (for context)
            num_questions: Number of questions to generate

        Returns:
            List of question dictionaries ready for QuizQuestion creation
        """
        try:
            # Import QuestionGeneratorService
            from ml_services.services.question_generator_service import (
                QuestionGeneratorService,
                QuestionGenerationRequest,
                QuestionType,
                DifficultyLevel
            )

            # Initialize service (if not already initialized)
            question_service = QuestionGeneratorService()
            if not question_service._is_initialized:
                question_service.initialize()

            # Determine question types based on platform
            question_types = cls._determine_question_types(lesson_platform)

            # Create generation request
            request = QuestionGenerationRequest(
                topic=lesson_title,
                subtopics=[],
                learning_objectives=[],
                question_types=question_types,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                num_questions=num_questions,
                max_options_per_question=4,
                include_explanations=True,
                include_hints=False,
                assessment_purpose="practice"
            )

            # Add scraped content to request context
            # Note: QuestionGenerationRequest doesn't have a 'content' field by default
            # We'll need to pass it through the topic or subtopics
            # For now, we'll truncate content and add it to topic description
            content_preview = content[:500] if len(content) > 500 else content
            request.topic = f"{lesson_title}\n\nContent: {content_preview}"

            # Generate questions
            response = question_service.process(request)

            if not response.success or not response.questions:
                logger.error("Question generation failed or returned no questions")
                return []

            # Convert GeneratedQuestion objects to dictionaries for QuizQuestion creation
            questions_data = []
            for generated_q in response.questions:
                question_dict = {
                    'question_text': generated_q.question_text,
                    'question_type': generated_q.question_type.value,
                    'correct_answer': generated_q.correct_answer,
                    'explanation': generated_q.explanation or '',
                    'difficulty': cls._map_difficulty(generated_q.difficulty_level.value),
                    'blooms_level': cls._extract_blooms_level(generated_q),
                    'points': 1,
                    'options': {}
                }

                # Add options for multiple choice and true/false
                if generated_q.question_type == QuestionType.MULTIPLE_CHOICE:
                    question_dict['options'] = {
                        'options': generated_q.options or [],
                        'correct_index': cls._find_correct_option_index(
                            generated_q.options,
                            generated_q.correct_answer
                        ) if generated_q.options else 0
                    }
                elif generated_q.question_type == QuestionType.TRUE_FALSE:
                    question_dict['options'] = {
                        'options': ['True', 'False'],
                        'correct': generated_q.correct_answer.lower() in ['true', 't', 'yes']
                    }

                questions_data.append(question_dict)

            logger.info(f"✅ Converted {len(questions_data)} generated questions")
            return questions_data

        except ImportError as e:
            logger.error(f"QuestionGeneratorService not available: {e}")
            # Fallback to simple questions based on metadata
            return cls._generate_fallback_questions(lesson_title, content, num_questions)

        except Exception as e:
            logger.error(f"Error generating questions with AI: {e}", exc_info=True)
            # Fallback to simple questions
            return cls._generate_fallback_questions(lesson_title, content, num_questions)

    @staticmethod
    def _determine_question_types(platform: str) -> List:
        """
        Determine appropriate question types based on platform.

        YouTube/Videos: Multiple choice, True/False
        Articles: Short answer, Multiple choice
        Code/GitHub: Code questions, Multiple choice
        """
        from ml_services.services.question_generator_service import QuestionType

        platform_lower = platform.lower()

        if 'youtube' in platform_lower:
            return [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE]
        elif 'github' in platform_lower or 'code' in platform_lower:
            return [QuestionType.MULTIPLE_CHOICE, QuestionType.CODING_CHALLENGE]
        else:
            # Articles, general content
            return [QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER, QuestionType.TRUE_FALSE]

    @staticmethod
    def _map_difficulty(ai_difficulty: str) -> str:
        """Map AI difficulty levels to our schema (easy, medium, hard)"""
        mapping = {
            'beginner': 'easy',
            'intermediate': 'medium',
            'advanced': 'hard',
            'expert': 'hard'
        }
        return mapping.get(ai_difficulty.lower(), 'medium')

    @staticmethod
    def _extract_blooms_level(generated_q) -> str:
        """Extract Bloom's taxonomy level from generated question"""
        # The AI might include this in tags or learning objectives
        if hasattr(generated_q, 'tags') and generated_q.tags:
            for tag in generated_q.tags:
                if any(level in tag.lower() for level in ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']):
                    return tag.lower()
        return 'understand'

    @staticmethod
    def _find_correct_option_index(options: List[str], correct_answer: str) -> int:
        """Find the index of the correct answer in options list"""
        try:
            return options.index(correct_answer)
        except (ValueError, AttributeError):
            # If exact match not found, try case-insensitive
            for idx, option in enumerate(options):
                if option.lower().strip() == correct_answer.lower().strip():
                    return idx
            return 0  # Default to first option

    @classmethod
    def _generate_fallback_questions(
        cls,
        lesson_title: str,
        content: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate simple fallback questions when AI is unavailable.

        Creates basic multiple choice questions based on lesson title and content.
        """
        logger.warning("Using fallback question generation (AI unavailable)")

        fallback_questions = [
            {
                'question_text': f"What is the main topic of this lesson: '{lesson_title}'?",
                'question_type': 'multiple_choice',
                'correct_answer': lesson_title,
                'explanation': f"This lesson focuses on {lesson_title}.",
                'difficulty': 'easy',
                'blooms_level': 'remember',
                'points': 1,
                'options': {
                    'options': [lesson_title, 'Other topic A', 'Other topic B', 'Other topic C'],
                    'correct_index': 0
                }
            },
            {
                'question_text': f"True or False: This lesson covers {lesson_title}?",
                'question_type': 'true_false',
                'correct_answer': 'True',
                'explanation': f"Yes, this lesson is about {lesson_title}.",
                'difficulty': 'easy',
                'blooms_level': 'remember',
                'points': 1,
                'options': {
                    'options': ['True', 'False'],
                    'correct': True
                }
            }
        ]

        # Return limited number of fallback questions
        return fallback_questions[:min(num_questions, len(fallback_questions))]
