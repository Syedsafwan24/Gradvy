"""
backend/ml_services/tasks.py
Celery background tasks for ML services processing
Handles asynchronous AI operations like learning path generation and code evaluation
RELEVANT FILES: services/learning_path_service.py, services/code_evaluation_service.py, services/question_generator_service.py, models/learning_models.py
"""

import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from celery import shared_task, group, chain
from celery.exceptions import Retry, MaxRetriesExceededError
from django.core.cache import cache
from django.conf import settings

# Import ML services
try:
    from .services.learning_path_service import LearningPathService, LearningPathRequest
    from .services.question_generator_service import QuestionGeneratorService, QuestionGenerationRequest
    from .services.code_evaluation_service import CodeEvaluationService, CodeEvaluationRequest, CodeLanguage
    from .utils.data_sanitizer import DataSanitizer, sanitize_for_ml
    from .models.learning_models import (
        LearningPath, LearningModule, LearningProgress, AssessmentSession,
        CodeSubmission, LearningPathManager, ProgressTracker
    )
    from .utils.model_initializer import get_global_initializer, initialize_ml_system
except ImportError as e:
    logging.warning(f"ML services not available: {e}")

# Import user models
try:
    from core.apps.preferences.models import UserPreference
except ImportError:
    logging.warning("UserPreference model not available")

# Logging configuration
logger = logging.getLogger(__name__)

# Task configuration
TASK_RETRY_DELAY = 60  # 1 minute
TASK_MAX_RETRIES = 3
TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
TASK_TIME_LIMIT = 600  # 10 minutes


# =============================================================================
# LEARNING PATH GENERATION TASKS
# =============================================================================

@shared_task(
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    soft_time_limit=TASK_SOFT_TIME_LIMIT,
    time_limit=TASK_TIME_LIMIT
)
def generate_learning_path_task(self, user_preference_id: str, generation_params: Dict[str, Any]):
    """
    Generate personalized learning path using AI models

    Args:
        user_preference_id: MongoDB ObjectId of UserPreference
        generation_params: Parameters for path generation

    Returns:
        Dict with learning path ID and generation status
    """
    task_id = self.request.id
    logger.info(f"Task {task_id}: Starting learning path generation for user {user_preference_id}")

    try:
        # Set task status in cache
        cache.set(f"task_{task_id}_status", "initializing", timeout=3600)

        # Get user preferences
        try:
            user_preference = UserPreference.objects.get(id=user_preference_id)
        except UserPreference.DoesNotExist:
            logger.error(f"Task {task_id}: User preference not found: {user_preference_id}")
            return {"success": False, "error": "User preference not found"}

        cache.set(f"task_{task_id}_status", "sanitizing_data", timeout=3600)

        # Sanitize user data for AI processing
        sanitizer = DataSanitizer()
        sanitized_prefs = sanitizer.sanitize_user_preferences(user_preference.to_mongo().to_dict())

        if not sanitized_prefs.sanitized_data:
            logger.error(f"Task {task_id}: Data sanitization failed")
            return {"success": False, "error": "Data sanitization failed"}

        cache.set(f"task_{task_id}_status", "initializing_ai_service", timeout=3600)

        # Initialize learning path service
        learning_service = LearningPathService()
        if not learning_service.initialize():
            logger.warning(f"Task {task_id}: AI service initialization failed, using fallback")

        # Create learning path request
        request = LearningPathRequest(
            user_id=str(user_preference.id),
            request_id=f"task_{task_id}",
            learning_goals=sanitized_prefs.sanitized_data.get('learning_goals', []),
            experience_level=sanitized_prefs.sanitized_data.get('experience_level', 'beginner'),
            time_availability=sanitized_prefs.sanitized_data.get('time_availability', '3-5hrs'),
            preferred_pace=sanitized_prefs.sanitized_data.get('preferred_pace', 'medium'),
            learning_styles=sanitized_prefs.sanitized_data.get('learning_styles', []),
            target_timeline=sanitized_prefs.sanitized_data.get('target_timeline', '6months'),
            career_stage=sanitized_prefs.sanitized_data.get('career_stage', 'student'),
            previous_experience=sanitized_prefs.sanitized_data.get('previous_experience', []),
            preferred_platforms=sanitized_prefs.sanitized_data.get('preferred_platforms', []),
            **generation_params
        )

        cache.set(f"task_{task_id}_status", "generating_learning_path", timeout=3600)

        # Generate learning path
        response = learning_service.process(request)

        if response.success:
            cache.set(f"task_{task_id}_status", "saving_to_database", timeout=3600)

            # Save to MongoDB using the manager
            learning_path = LearningPathManager.create_learning_path_from_ai_response(
                user_preference, response.data
            )

            cache.set(f"task_{task_id}_status", "completed", timeout=3600)

            logger.info(f"Task {task_id}: Learning path generated successfully: {learning_path.path_id}")

            # Schedule follow-up tasks
            generate_initial_assessments_task.delay(str(learning_path.path_id))

            return {
                "success": True,
                "learning_path_id": str(learning_path.path_id),
                "title": learning_path.title,
                "total_modules": learning_path.total_modules,
                "estimated_hours": learning_path.estimated_total_hours,
                "generation_time_ms": response.processing_time_ms
            }
        else:
            logger.error(f"Task {task_id}: Learning path generation failed: {response.error}")
            return {"success": False, "error": response.error}

    except Exception as e:
        logger.error(f"Task {task_id}: Unexpected error: {e}")
        logger.error(traceback.format_exc())

        # Retry with exponential backoff
        if self.request.retries < TASK_MAX_RETRIES:
            retry_delay = TASK_RETRY_DELAY * (2 ** self.request.retries)
            cache.set(f"task_{task_id}_status", f"retrying_in_{retry_delay}s", timeout=3600)
            raise self.retry(countdown=retry_delay, exc=e)

        cache.set(f"task_{task_id}_status", "failed", timeout=3600)
        return {"success": False, "error": str(e)}


@shared_task(
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    soft_time_limit=180,
    time_limit=300
)
def generate_initial_assessments_task(self, learning_path_id: str):
    """
    Generate initial assessment questions for a learning path

    Args:
        learning_path_id: Learning path UUID

    Returns:
        Dict with assessment generation results
    """
    task_id = self.request.id
    logger.info(f"Task {task_id}: Generating assessments for learning path {learning_path_id}")

    try:
        # Get learning path
        try:
            learning_path = LearningPath.objects.get(path_id=learning_path_id)
            modules = LearningModule.objects(learning_path=learning_path).order_by('module_number')
        except (LearningPath.DoesNotExist, Exception) as e:
            logger.error(f"Task {task_id}: Learning path not found: {e}")
            return {"success": False, "error": "Learning path not found"}

        # Initialize question generation service
        question_service = QuestionGeneratorService()
        if not question_service.initialize():
            logger.warning(f"Task {task_id}: Question service initialization failed")

        generated_assessments = 0

        # Generate questions for each module
        for module in modules:
            try:
                # Create question generation request
                request = QuestionGenerationRequest(
                    user_id=str(learning_path.user.id) if learning_path.user else "anonymous",
                    request_id=f"assessment_{module.module_id}",
                    topic=module.title,
                    subtopics=[obj.description for obj in module.learning_objectives[:3]],
                    difficulty_level=module.difficulty_level.value,
                    question_count=5,  # 5 questions per module
                    question_types=['multiple_choice', 'short_answer'],
                    learning_objectives=[obj.description for obj in module.learning_objectives]
                )

                # Generate questions
                response = question_service.process(request)

                if response.success and response.data.get('questions'):
                    # Convert questions to assessment format and save to module
                    questions_data = response.data['questions']
                    # This would be saved to the module's assessment_questions
                    # Implementation details would depend on the final schema
                    generated_assessments += len(questions_data)

            except Exception as e:
                logger.warning(f"Task {task_id}: Failed to generate questions for module {module.module_id}: {e}")

        logger.info(f"Task {task_id}: Generated {generated_assessments} assessment questions")

        return {
            "success": True,
            "learning_path_id": learning_path_id,
            "assessments_generated": generated_assessments,
            "modules_processed": len(modules)
        }

    except Exception as e:
        logger.error(f"Task {task_id}: Assessment generation failed: {e}")
        if self.request.retries < TASK_MAX_RETRIES:
            raise self.retry(countdown=TASK_RETRY_DELAY * (2 ** self.request.retries), exc=e)
        return {"success": False, "error": str(e)}


# =============================================================================
# CODE EVALUATION TASKS
# =============================================================================

@shared_task(
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    soft_time_limit=120,
    time_limit=180
)
def evaluate_code_submission_task(self, submission_data: Dict[str, Any]):
    """
    Evaluate code submission using AI models

    Args:
        submission_data: Code submission data

    Returns:
        Dict with evaluation results
    """
    task_id = self.request.id
    logger.info(f"Task {task_id}: Evaluating code submission")

    try:
        # Sanitize code for AI processing
        sanitized_data = sanitize_for_ml(submission_data, "code")

        # Initialize code evaluation service
        evaluation_service = CodeEvaluationService()
        if not evaluation_service.initialize():
            logger.warning(f"Task {task_id}: Code evaluation service initialization failed")

        # Create evaluation request
        try:
            language = CodeLanguage(submission_data.get('language', 'python').lower())
        except ValueError:
            language = CodeLanguage.PYTHON  # Default

        request = CodeEvaluationRequest(
            code=sanitized_data.get('code', ''),
            language=language,
            problem_description=submission_data.get('problem_description'),
            expected_output=submission_data.get('expected_output'),
            test_cases=submission_data.get('test_cases', []),
            learning_objectives=submission_data.get('learning_objectives', []),
            difficulty_level=submission_data.get('difficulty_level', 'beginner'),
            include_ai_feedback=True,
            include_suggestions=True
        )

        # Perform evaluation
        response = evaluation_service.process(request)

        if response.success:
            # Save evaluation results to database if submission_id provided
            if 'submission_id' in submission_data:
                try:
                    submission = CodeSubmission.objects.get(submission_id=submission_data['submission_id'])
                    submission.overall_score = response.overall_score
                    submission.correctness_score = response.aspect_scores.get('correctness', 0)
                    submission.style_score = response.aspect_scores.get('style', 0)
                    submission.efficiency_score = response.aspect_scores.get('efficiency', 0)
                    submission.test_cases_passed = response.passed_tests
                    submission.total_test_cases = response.total_tests
                    submission.ai_feedback = response.ai_feedback
                    submission.ai_suggestions = response.suggestions
                    submission.evaluated_at = datetime.utcnow()
                    submission.save()
                except Exception as e:
                    logger.warning(f"Task {task_id}: Failed to update submission: {e}")

            logger.info(f"Task {task_id}: Code evaluation completed with score {response.overall_score}")

            return {
                "success": True,
                "overall_score": response.overall_score,
                "aspect_scores": {k.value: v for k, v in response.aspect_scores.items()},
                "ai_feedback": response.ai_feedback,
                "suggestions": response.suggestions,
                "passed_tests": response.passed_tests,
                "total_tests": response.total_tests,
                "processing_time_ms": response.processing_time_ms
            }
        else:
            logger.error(f"Task {task_id}: Code evaluation failed: {response.error}")
            return {"success": False, "error": response.error}

    except Exception as e:
        logger.error(f"Task {task_id}: Code evaluation task failed: {e}")
        if self.request.retries < TASK_MAX_RETRIES:
            raise self.retry(countdown=TASK_RETRY_DELAY * (2 ** self.request.retries), exc=e)
        return {"success": False, "error": str(e)}


# =============================================================================
# PROGRESS TRACKING TASKS
# =============================================================================

@shared_task
def update_learning_progress_task(user_id: str, learning_path_id: str,
                                activity_data: Dict[str, Any]):
    """
    Update user learning progress after activity completion

    Args:
        user_id: User preference ID
        learning_path_id: Learning path UUID
        activity_data: Completed activity information

    Returns:
        Updated progress information
    """
    logger.info(f"Updating progress for user {user_id} in path {learning_path_id}")

    try:
        # Get user and learning path
        user_preference = UserPreference.objects.get(id=user_id)
        learning_path = LearningPath.objects.get(path_id=learning_path_id)

        # Update progress using the tracker
        progress = ProgressTracker.update_progress(
            user_preference,
            learning_path,
            activity_data.get('activity_type', 'activity'),
            activity_data.get('activity_id', ''),
            activity_data
        )

        # Trigger adaptive recommendations if needed
        if progress.overall_progress_percentage % 20 == 0:  # Every 20% completion
            generate_adaptive_recommendations_task.delay(user_id, learning_path_id)

        return {
            "success": True,
            "overall_progress": progress.overall_progress_percentage,
            "modules_completed": progress.modules_completed,
            "status": progress.status.value
        }

    except Exception as e:
        logger.error(f"Progress update failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def generate_adaptive_recommendations_task(user_id: str, learning_path_id: str):
    """
    Generate adaptive learning recommendations based on progress

    Args:
        user_id: User preference ID
        learning_path_id: Learning path UUID

    Returns:
        Generated recommendations
    """
    logger.info(f"Generating adaptive recommendations for user {user_id}")

    try:
        # Get user progress data
        user_preference = UserPreference.objects.get(id=user_id)
        learning_path = LearningPath.objects.get(path_id=learning_path_id)
        progress = LearningProgress.objects(
            user=user_preference,
            learning_path=learning_path
        ).first()

        if not progress:
            return {"success": False, "error": "Progress not found"}

        # Simple adaptive logic - in practice this would be more sophisticated
        recommendations = []

        # Check if user is struggling
        if progress.overall_score_percentage < 70:
            recommendations.append({
                "type": "review",
                "message": "Consider reviewing previous modules",
                "priority": "high"
            })

        # Check if user is progressing too fast
        if progress.learning_velocity > 1.5:
            recommendations.append({
                "type": "challenge",
                "message": "Try advanced exercises for better understanding",
                "priority": "medium"
            })

        # Check consistency
        if progress.consistency_score < 50:
            recommendations.append({
                "type": "schedule",
                "message": "Set up a regular learning schedule",
                "priority": "medium"
            })

        # Save recommendations to progress
        progress.personalized_recommendations = recommendations
        progress.save()

        return {
            "success": True,
            "recommendations": recommendations,
            "user_id": user_id,
            "learning_path_id": learning_path_id
        }

    except Exception as e:
        logger.error(f"Adaptive recommendations failed: {e}")
        return {"success": False, "error": str(e)}


# =============================================================================
# BATCH PROCESSING TASKS
# =============================================================================

@shared_task
def batch_generate_questions_task(question_requests: List[Dict[str, Any]]):
    """
    Generate questions in batch for efficiency

    Args:
        question_requests: List of question generation requests

    Returns:
        Batch processing results
    """
    logger.info(f"Batch generating {len(question_requests)} question sets")

    try:
        question_service = QuestionGeneratorService()
        if not question_service.initialize():
            logger.warning("Question service initialization failed")

        results = []
        for i, request_data in enumerate(question_requests):
            try:
                request = QuestionGenerationRequest(**request_data)
                response = question_service.process(request)
                results.append({
                    "request_index": i,
                    "success": response.success,
                    "questions_generated": len(response.data.get('questions', [])) if response.success else 0,
                    "error": response.error if not response.success else None
                })
            except Exception as e:
                results.append({
                    "request_index": i,
                    "success": False,
                    "questions_generated": 0,
                    "error": str(e)
                })

        successful = sum(1 for r in results if r['success'])
        total_questions = sum(r['questions_generated'] for r in results)

        return {
            "success": True,
            "batch_size": len(question_requests),
            "successful_requests": successful,
            "total_questions_generated": total_questions,
            "results": results
        }

    except Exception as e:
        logger.error(f"Batch question generation failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def batch_evaluate_submissions_task(submission_ids: List[str]):
    """
    Evaluate multiple code submissions in batch

    Args:
        submission_ids: List of submission IDs to evaluate

    Returns:
        Batch evaluation results
    """
    logger.info(f"Batch evaluating {len(submission_ids)} code submissions")

    try:
        evaluation_service = CodeEvaluationService()
        if not evaluation_service.initialize():
            logger.warning("Code evaluation service initialization failed")

        results = []
        for submission_id in submission_ids:
            try:
                submission = CodeSubmission.objects.get(submission_id=submission_id)

                request = CodeEvaluationRequest(
                    code=submission.code,
                    language=CodeLanguage(submission.programming_language),
                    include_ai_feedback=True
                )

                response = evaluation_service.process(request)

                if response.success:
                    # Update submission with results
                    submission.overall_score = response.overall_score
                    submission.ai_feedback = response.ai_feedback
                    submission.evaluated_at = datetime.utcnow()
                    submission.save()

                results.append({
                    "submission_id": submission_id,
                    "success": response.success,
                    "score": response.overall_score if response.success else 0,
                    "error": response.error if not response.success else None
                })

            except Exception as e:
                results.append({
                    "submission_id": submission_id,
                    "success": False,
                    "score": 0,
                    "error": str(e)
                })

        successful = sum(1 for r in results if r['success'])
        average_score = sum(r['score'] for r in results if r['success']) / max(1, successful)

        return {
            "success": True,
            "batch_size": len(submission_ids),
            "successful_evaluations": successful,
            "average_score": round(average_score, 2),
            "results": results
        }

    except Exception as e:
        logger.error(f"Batch evaluation failed: {e}")
        return {"success": False, "error": str(e)}


# =============================================================================
# SYSTEM MAINTENANCE TASKS
# =============================================================================

@shared_task
def cleanup_old_cache_task():
    """Clean up old cache entries and temporary data"""
    logger.info("Starting cache cleanup")

    try:
        # This would implement cache cleanup logic
        # For now, just a placeholder
        cleanup_count = 0

        # Clean up old task status entries
        for key in cache.keys("task_*_status"):
            cache.delete(key)
            cleanup_count += 1

        logger.info(f"Cleaned up {cleanup_count} cache entries")
        return {"success": True, "cleaned_entries": cleanup_count}

    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def model_health_check_task():
    """Periodic health check for ML models"""
    logger.info("Performing model health check")

    try:
        # Get global model initializer
        initializer = get_global_initializer()

        if not initializer:
            return {"success": False, "error": "Model initializer not available"}

        # Get system stats
        stats = initializer.get_system_stats()

        # Check model availability
        unhealthy_models = []
        healthy_models = []

        for model_name in stats.get('available_models', []):
            try:
                model = initializer.model_registry.get_model(model_name, load_if_needed=False)
                if model and hasattr(model, 'health_check'):
                    health = model.health_check()
                    if health.get('status') == 'healthy':
                        healthy_models.append(model_name)
                    else:
                        unhealthy_models.append(model_name)
                else:
                    healthy_models.append(model_name)  # Assume healthy if no health check
            except Exception as e:
                unhealthy_models.append(f"{model_name}: {str(e)}")

        # Log results
        if unhealthy_models:
            logger.warning(f"Unhealthy models detected: {unhealthy_models}")
        else:
            logger.info(f"All models healthy: {healthy_models}")

        return {
            "success": True,
            "healthy_models": healthy_models,
            "unhealthy_models": unhealthy_models,
            "system_stats": stats
        }

    except Exception as e:
        logger.error(f"Model health check failed: {e}")
        return {"success": False, "error": str(e)}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the current status of a task"""
    try:
        # Check cache for custom status
        custom_status = cache.get(f"task_{task_id}_status")

        # This would also check Celery's task status
        # For now, return basic info
        return {
            "task_id": task_id,
            "status": custom_status or "unknown",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return {"task_id": task_id, "status": "error", "error": str(e)}


def schedule_learning_path_generation(user_id: str, generation_params: Optional[Dict[str, Any]] = None):
    """
    Convenience function to schedule learning path generation

    Args:
        user_id: User preference ID
        generation_params: Optional parameters for generation

    Returns:
        Task ID for tracking
    """
    params = generation_params or {}
    task = generate_learning_path_task.delay(user_id, params)
    return task.id


def schedule_code_evaluation(submission_data: Dict[str, Any]):
    """
    Convenience function to schedule code evaluation

    Args:
        submission_data: Code submission data

    Returns:
        Task ID for tracking
    """
    task = evaluate_code_submission_task.delay(submission_data)
    return task.id


# Export key functions and tasks
__all__ = [
    'generate_learning_path_task',
    'generate_initial_assessments_task',
    'evaluate_code_submission_task',
    'update_learning_progress_task',
    'generate_adaptive_recommendations_task',
    'batch_generate_questions_task',
    'batch_evaluate_submissions_task',
    'cleanup_old_cache_task',
    'model_health_check_task',
    'get_task_status',
    'schedule_learning_path_generation',
    'schedule_code_evaluation'
]