# File: backend/core/apps/learning_content/api/quiz_views.py
# Description: API views for quiz management - get quiz, start attempt, submit answers, view results
# Why: Exposes quiz functionality through REST API endpoints
# Relevant Files: views.py, serializers.py, services/quiz_orchestrator_service.py, models.py

import logging
from rest_framework import permissions
from rest_framework.views import APIView
from datetime import datetime
from typing import Dict, Any, List

from .serializers import (
    QuizSerializer,
    QuizQuestionSerializer,
    StartQuizRequestSerializer,
    SubmitQuizRequestSerializer,
    QuizAttemptSerializer,
    QuizResultSerializer,
    QuizStatsSerializer
)
from apps.learning_content.models import (
    LessonQuiz,
    QuizQuestion,
    QuizAttempt,
    QuestionResponse,
    CourseRecommendation
)
from apps.learning_content.services.quiz_orchestrator_service import QuizOrchestratorService
from utils.responses import APISuccess, APIError, StatusCodes, ErrorCodes

logger = logging.getLogger(__name__)


class GetOrCreateQuizView(APIView):
    """
    GET /api/quizzes/<path_id>/<lesson_id>/
    Get existing quiz or generate a new one for a lesson
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, path_id, lesson_id):
        """
        Get or create quiz for a lesson.

        If quiz doesn't exist, generates it using QuizOrchestratorService.
        Returns quiz with questions (but not correct answers).
        """
        try:
            # Try to get existing quiz first
            try:
                quiz = LessonQuiz.objects.get(path_id=path_id, lesson_id=lesson_id)

                # Check if expired
                if quiz.is_expired():
                    logger.info(f"Quiz expired for lesson {lesson_id}, regenerating")
                    quiz.delete()  # Will cascade delete questions
                    quiz = None
            except LessonQuiz.DoesNotExist:
                quiz = None

            # If no quiz exists, generate it
            if not quiz:
                # Get lesson details from CourseRecommendation
                try:
                    course_rec = CourseRecommendation.objects.get(user_id=request.user.id)
                    learning_path = next(
                        (path for path in course_rec.learning_paths if path.path_id == path_id),
                        None
                    )

                    if not learning_path:
                        return APIError.create(
                            message=f"Learning path '{path_id}' not found",
                            code="NOT_FOUND",
                            status_code=StatusCodes.NOT_FOUND
                        )

                    # Find the lesson
                    lesson = None
                    for module in learning_path.modules:
                        for l in module.get('lessons', []):
                            if l.get('lesson_id') == lesson_id:
                                lesson = l
                                break
                        if lesson:
                            break

                    if not lesson:
                        return APIError.create(
                            message=f"Lesson '{lesson_id}' not found in path",
                            code="NOT_FOUND",
                            status_code=StatusCodes.NOT_FOUND
                        )

                    # Generate quiz
                    logger.info(f"Generating quiz for lesson {lesson_id}")
                    quiz = QuizOrchestratorService.get_or_create_quiz(
                        path_id=path_id,
                        lesson_id=lesson_id,
                        lesson_title=lesson.get('title', 'Lesson'),
                        lesson_url=lesson.get('url', ''),
                        lesson_platform=lesson.get('platform', 'unknown'),
                        lesson_description=lesson.get('description', '')
                    )

                    if not quiz:
                        return APIError.create(
                            message="Failed to generate quiz",
                            code="QUIZ_GENERATION_FAILED",
                            status_code=StatusCodes.INTERNAL_SERVER_ERROR
                        )

                except CourseRecommendation.DoesNotExist:
                    return APIError.create(
                        message="No learning paths found for user",
                        code="NOT_FOUND",
                        status_code=StatusCodes.NOT_FOUND
                    )

            # Serialize quiz (without correct answers)
            quiz_data = {
                'id': quiz.id,
                'path_id': quiz.path_id,
                'lesson_id': quiz.lesson_id,
                'lesson_title': quiz.lesson_title,
                'lesson_platform': quiz.lesson_platform,
                'passing_score_percentage': quiz.passing_score_percentage,
                'num_questions': quiz.num_questions,
                'content_scraped': quiz.content_scraped,
                'content_source': quiz.content_source,
                'created_at': quiz.created_at,
                'cache_until': quiz.cache_until,
                'questions': [
                    {
                        'id': q.id,
                        'order': q.order,
                        'question_text': q.question_text,
                        'question_type': q.question_type,
                        'difficulty': q.difficulty,
                        'points': q.points,
                        'options': q.options
                        # Note: correct_answer and explanation excluded for security
                    }
                    for q in quiz.questions.all().order_by('order')
                ]
            }

            serializer = QuizSerializer(quiz_data)
            return APISuccess.create(
                data=serializer.data,
                message="Quiz retrieved successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            logger.error(f"Error getting quiz: {e}", exc_info=True)
            return APIError.create(
                message=f"Failed to get quiz: {str(e)}",
                code="QUIZ_RETRIEVAL_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class StartQuizAttemptView(APIView):
    """
    POST /api/quizzes/<quiz_id>/start/
    Start a new quiz attempt
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        """
        Start a new quiz attempt.

        Creates QuizAttempt record and returns attempt_id.
        """
        try:
            # Get quiz
            try:
                quiz = LessonQuiz.objects.get(id=quiz_id)
            except LessonQuiz.DoesNotExist:
                return APIError.create(
                    message=f"Quiz {quiz_id} not found",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Count existing attempts for this user/quiz
            attempt_count = QuizAttempt.objects.filter(
                quiz=quiz,
                user=request.user
            ).count()

            # Create new attempt
            attempt = QuizAttempt.objects.create(
                quiz=quiz,
                user=request.user,
                attempt_number=attempt_count + 1,
                status='in_progress',
                total_points_possible=sum(q.points for q in quiz.questions.all())
            )

            logger.info(f"Started quiz attempt {attempt.id} for user {request.user.id}")

            return APISuccess.create(
                data={
                    'attempt_id': attempt.id,
                    'quiz_id': quiz.id,
                    'attempt_number': attempt.attempt_number,
                    'started_at': attempt.started_at.isoformat(),
                    'status': attempt.status
                },
                message="Quiz attempt started successfully",
                status_code=StatusCodes.CREATED
            )

        except Exception as e:
            logger.error(f"Error starting quiz attempt: {e}", exc_info=True)
            return APIError.create(
                message=f"Failed to start quiz attempt: {str(e)}",
                code="ATTEMPT_START_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class SubmitQuizView(APIView):
    """
    POST /api/quizzes/attempts/<attempt_id>/submit/
    Submit quiz answers and get results
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, attempt_id):
        """
        Submit quiz answers for grading.

        Validates answers, grades them, calculates score,
        and returns detailed results with explanations.
        """
        # Validate request
        serializer = SubmitQuizRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return APIError.create(
                message="Invalid submission data",
                code="VALIDATION_ERROR",
                field_errors=serializer.errors,
                status_code=StatusCodes.BAD_REQUEST
            )

        validated_data = serializer.validated_data

        try:
            # Get attempt
            try:
                attempt = QuizAttempt.objects.select_related('quiz', 'user').get(id=attempt_id)
            except QuizAttempt.DoesNotExist:
                return APIError.create(
                    message=f"Quiz attempt {attempt_id} not found",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Verify ownership
            if attempt.user.id != request.user.id:
                return APIError.create(
                    message="You don't have permission to submit this quiz",
                    code="FORBIDDEN",
                    status_code=StatusCodes.FORBIDDEN
                )

            # Verify attempt is in progress
            if attempt.status != 'in_progress':
                return APIError.create(
                    message=f"Cannot submit quiz with status '{attempt.status}'",
                    code="INVALID_STATUS",
                    status_code=StatusCodes.BAD_REQUEST
                )

            # Grade the quiz (import grading logic)
            from .quiz_grader import QuizGrader

            grading_result = QuizGrader.grade_quiz_attempt(
                attempt=attempt,
                answers=validated_data['answers']
            )

            # Return results
            serializer = QuizResultSerializer(grading_result)
            return APISuccess.create(
                data=serializer.data,
                message="Quiz submitted and graded successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            logger.error(f"Error submitting quiz: {e}", exc_info=True)
            return APIError.create(
                message=f"Failed to submit quiz: {str(e)}",
                code="SUBMISSION_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class GetQuizAttemptView(APIView):
    """
    GET /api/quizzes/attempts/<attempt_id>/
    Get quiz attempt results
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, attempt_id):
        """
        Retrieve quiz attempt with results.

        Only returns full results if attempt is completed.
        """
        try:
            # Get attempt with related data
            try:
                attempt = QuizAttempt.objects.select_related('quiz', 'user').prefetch_related(
                    'responses__question'
                ).get(id=attempt_id)
            except QuizAttempt.DoesNotExist:
                return APIError.create(
                    message=f"Quiz attempt {attempt_id} not found",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Verify ownership
            if attempt.user.id != request.user.id:
                return APIError.create(
                    message="You don't have permission to view this attempt",
                    code="FORBIDDEN",
                    status_code=StatusCodes.FORBIDDEN
                )

            # Serialize attempt
            attempt_data = {
                'id': attempt.id,
                'quiz_id': attempt.quiz.id,
                'attempt_number': attempt.attempt_number,
                'status': attempt.status,
                'started_at': attempt.started_at,
                'completed_at': attempt.completed_at,
                'time_taken_seconds': attempt.time_taken_seconds,
                'score_percentage': attempt.score_percentage,
                'total_points_earned': attempt.total_points_earned,
                'total_points_possible': attempt.total_points_possible,
                'passed': attempt.passed,
                'is_best_attempt': attempt.is_best_attempt,
                'responses': [
                    {
                        'id': r.id,
                        'question_id': r.question.id,
                        'user_answer': r.user_answer,
                        'is_correct': r.is_correct,
                        'points_earned': r.points_earned,
                        'answered_at': r.answered_at,
                        'time_taken_seconds': r.time_taken_seconds,
                        'ai_feedback': r.ai_feedback
                    }
                    for r in attempt.responses.all()
                ] if attempt.status == 'completed' else []
            }

            serializer = QuizAttemptSerializer(attempt_data)
            return APISuccess.create(
                data=serializer.data,
                message="Quiz attempt retrieved successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            logger.error(f"Error retrieving quiz attempt: {e}", exc_info=True)
            return APIError.create(
                message=f"Failed to retrieve quiz attempt: {str(e)}",
                code="RETRIEVAL_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class GetQuizAttemptsView(APIView):
    """
    GET /api/quizzes/<path_id>/<lesson_id>/attempts/
    Get all quiz attempts for a lesson by current user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, path_id, lesson_id):
        """
        Get user's quiz attempt history for a lesson.

        Returns all attempts with statistics.
        """
        try:
            # Get quiz
            try:
                quiz = LessonQuiz.objects.get(path_id=path_id, lesson_id=lesson_id)
            except LessonQuiz.DoesNotExist:
                return APIError.create(
                    message=f"No quiz found for lesson {lesson_id}",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Get all attempts by this user
            attempts = QuizAttempt.objects.filter(
                quiz=quiz,
                user=request.user,
                status='completed'
            ).order_by('-started_at')

            # Calculate stats
            total_attempts = attempts.count()
            best_attempt = attempts.order_by('-score_percentage').first()
            best_score = best_attempt.score_percentage if best_attempt else None
            passed = best_attempt.passed if best_attempt else False

            # Serialize
            stats_data = {
                'quiz_id': quiz.id,
                'lesson_id': quiz.lesson_id,
                'lesson_title': quiz.lesson_title,
                'total_attempts': total_attempts,
                'best_score_percentage': best_score,
                'passed': passed,
                'passing_score_percentage': quiz.passing_score_percentage,
                'attempts': [
                    {
                        'id': a.id,
                        'quiz_id': a.quiz.id,
                        'attempt_number': a.attempt_number,
                        'status': a.status,
                        'started_at': a.started_at,
                        'completed_at': a.completed_at,
                        'time_taken_seconds': a.time_taken_seconds,
                        'score_percentage': a.score_percentage,
                        'total_points_earned': a.total_points_earned,
                        'total_points_possible': a.total_points_possible,
                        'passed': a.passed,
                        'is_best_attempt': a.is_best_attempt,
                        'responses': []  # Don't include detailed responses in list view
                    }
                    for a in attempts
                ]
            }

            serializer = QuizStatsSerializer(stats_data)
            return APISuccess.create(
                data=serializer.data,
                message="Quiz attempts retrieved successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            logger.error(f"Error retrieving quiz attempts: {e}", exc_info=True)
            return APIError.create(
                message=f"Failed to retrieve quiz attempts: {str(e)}",
                code="RETRIEVAL_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )
