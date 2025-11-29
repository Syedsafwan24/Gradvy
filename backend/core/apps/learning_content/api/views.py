# File: backend/core/apps/learning_content/api/views.py
# Description: API views for learning path generation, retrieval, progress tracking, and customization
# Why: Exposes ML-powered learning path features through REST API endpoints
# Relevant Files: serializers.py, models.py, ml_services/services/learning_path_service.py, preferences/models.py

from rest_framework import permissions
from rest_framework.views import APIView
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.conf import settings
import uuid
import hashlib
import json
import logging

from .serializers import (
    LearningPathGenerationRequestSerializer,
    LearningPathSerializer,
    ProgressUpdateSerializer,
    CustomizationSerializer,
    ProgressAnalyticsSerializer,
    DashboardSummarySerializer
)
from apps.learning_content.models import CourseRecommendation, LearningPath, UserContentProfile
from apps.preferences.models import UserPreference
from utils.responses import APISuccess, APIError, APIValidationError, StatusCodes, ErrorCodes

# ML Service imports
try:
    from ml_services.services.learning_path_service import LearningPathService, LearningPathRequest
    from ml_services.integrations import RoadmapService, CourseSearchService
    from ml_services.services.career_insights_service import get_career_insights_service
    ML_SERVICES_AVAILABLE = True
except ImportError:
    ML_SERVICES_AVAILABLE = False
    print("Warning: ML services not available. Learning path generation will be disabled.")

# Initialize logger
logger = logging.getLogger(__name__)


# ============================================================================
# Quiz System Helper Functions
# ============================================================================
# Module-level helper functions for computing lesson lock states and quiz stats


def _is_lesson_completed(lesson_id: str, user) -> bool:
    """
    Check if a lesson is completed by the user.

    A lesson is completed if:
    - It exists in UserContentProfile.completed_courses, OR
    - It exists in UserContentProfile.in_progress_content with 100% progress

    Args:
        lesson_id: Lesson ID to check
        user: Django user instance

    Returns:
        True if lesson is completed, False otherwise
    """
    try:
        # Get user's content profile
        content_profile = UserContentProfile.get_by_user_id(user.id)
        if not content_profile:
            return False

        # Check completed_courses list
        for completed in content_profile.completed_courses:
            if completed.get('course_id') == lesson_id:
                return True

        # Check in_progress_content for 100% completion
        for in_progress in content_profile.in_progress_content:
            if (in_progress.get('content_id') == lesson_id and
                in_progress.get('progress_percentage', 0.0) >= 100.0):
                return True

        return False

    except Exception as e:
        logger.error(f"Error checking lesson completion for lesson_id={lesson_id}, user={user.id}: {e}")
        return False


def _get_quiz_stats(path_id: str, lesson_id: str, user) -> Dict[str, Any]:
    """
    Get quiz statistics for a specific lesson.

    Returns quiz metadata and user's attempt history including:
    - Whether quiz exists
    - Total attempts by user
    - Best score percentage
    - Whether user has passed (score >= passing_score_percentage)
    - Passing score requirement

    Args:
        path_id: Learning path ID
        lesson_id: Lesson ID within the path
        user: Django user instance

    Returns:
        Dictionary with quiz stats or None if quiz doesn't exist
    """
    from apps.learning_content.models import LessonQuiz, QuizAttempt

    try:
        # Try to get quiz for this lesson
        try:
            quiz = LessonQuiz.objects.get(path_id=path_id, lesson_id=lesson_id)
        except LessonQuiz.DoesNotExist:
            # No quiz exists for this lesson
            return {
                'quiz_exists': False,
                'quiz_required': False,
                'quiz_completed': False,
                'quiz_passed': False,
                'best_score': None,
                'total_attempts': 0,
                'passing_score_percentage': 70
            }

        # Get all completed attempts for this user
        attempts = QuizAttempt.objects.filter(
            quiz=quiz,
            user=user,
            status='completed'
        ).order_by('-score_percentage')

        total_attempts = attempts.count()
        best_attempt = attempts.first() if total_attempts > 0 else None

        best_score = best_attempt.score_percentage if best_attempt else None
        passed = best_attempt.passed if best_attempt else False

        return {
            'quiz_exists': True,
            'quiz_required': True,  # All lessons with quizzes require completion
            'quiz_completed': total_attempts > 0,
            'quiz_passed': passed,
            'best_score': best_score,
            'total_attempts': total_attempts,
            'passing_score_percentage': quiz.passing_score_percentage,
            'quiz_id': quiz.id
        }

    except Exception as e:
        logger.error(f"Error getting quiz stats for lesson_id={lesson_id}, user={user.id}: {e}")
        return {
            'quiz_exists': False,
            'quiz_required': False,
            'quiz_completed': False,
            'quiz_passed': False,
            'best_score': None,
            'total_attempts': 0,
            'passing_score_percentage': 70
        }


def _compute_lesson_lock_state(
    path_id: str,
    lesson_id: str,
    user,
    learning_path: Optional['LearningPath'] = None
) -> Dict[str, Any]:
    """
    Compute lock state for a lesson using strict sequential locking.

    Lock Rules (Strict Sequential):
    - First lesson in first module: ALWAYS UNLOCKED
    - Lesson N: LOCKED until lesson N-1 is both:
      1. Completed (100% progress)
      2. Quiz passed (if quiz exists for lesson N-1)

    Args:
        path_id: Learning path ID
        lesson_id: Lesson ID to check
        user: Django user instance
        learning_path: Optional LearningPath object (to avoid re-fetching)

    Returns:
        Dictionary with lock state information:
        {
            'is_locked': bool,
            'lock_reason': str,
            'requires_lesson_id': str or None,
            'requires_lesson_title': str or None,
            'requires_quiz_pass': bool,
            'quiz_required': bool,  # Does THIS lesson have a quiz?
            'quiz_stats': dict  # Quiz stats for THIS lesson
        }
    """
    try:
        # Find this lesson in the learning path
        if not learning_path:
            # Fetch learning path from CourseRecommendation
            try:
                from apps.learning_content.models import CourseRecommendation
                course_rec = CourseRecommendation.objects.get(user_id=user.id)
                learning_path = next(
                    (path for path in course_rec.learning_paths if path.path_id == path_id),
                    None
                )
                if not learning_path:
                    logger.warning(f"Learning path {path_id} not found for user {user.id}")
                    return {
                        'is_locked': True,
                        'lock_reason': 'Learning path not found',
                        'requires_lesson_id': None,
                        'requires_lesson_title': None,
                        'requires_quiz_pass': False,
                        'quiz_required': False,
                        'quiz_stats': {}
                    }
            except CourseRecommendation.DoesNotExist:
                logger.warning(f"CourseRecommendation not found for user {user.id}")
                return {
                    'is_locked': True,
                    'lock_reason': 'Course recommendation not found',
                    'requires_lesson_id': None,
                    'requires_lesson_title': None,
                    'requires_quiz_pass': False,
                    'quiz_required': False,
                    'quiz_stats': {}
                }

        # Find the current lesson and previous lesson
        all_lessons = []
        for module in learning_path.modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                all_lessons.append({
                    'lesson_id': lesson.get('lesson_id'),
                    'lesson_title': lesson.get('title'),
                    'module_id': module.get('module_id'),
                    'module_title': module.get('title')
                })

        # Find index of current lesson
        current_index = None
        for i, lesson in enumerate(all_lessons):
            if lesson['lesson_id'] == lesson_id:
                current_index = i
                break

        if current_index is None:
            logger.warning(f"Lesson {lesson_id} not found in path {path_id}")
            return {
                'is_locked': True,
                'lock_reason': 'Lesson not found in learning path',
                'requires_lesson_id': None,
                'requires_lesson_title': None,
                'requires_quiz_pass': False,
                'quiz_required': False,
                'quiz_stats': {}
            }

        # Get quiz stats for THIS lesson
        quiz_stats = _get_quiz_stats(path_id, lesson_id, user)

        # RULE: First lesson is always unlocked
        if current_index == 0:
            return {
                'is_locked': False,
                'lock_reason': '',
                'requires_lesson_id': None,
                'requires_lesson_title': None,
                'requires_quiz_pass': False,
                'quiz_required': quiz_stats['quiz_required'],
                'quiz_stats': quiz_stats
            }

        # RULE: Lesson N locked until lesson N-1 completed + quiz passed
        prev_lesson = all_lessons[current_index - 1]
        prev_lesson_id = prev_lesson['lesson_id']
        prev_lesson_title = prev_lesson['lesson_title']

        # Check if previous lesson is completed
        prev_completed = _is_lesson_completed(prev_lesson_id, user)

        # Check if previous lesson's quiz (if exists) is passed
        prev_quiz_stats = _get_quiz_stats(path_id, prev_lesson_id, user)
        prev_quiz_required = prev_quiz_stats['quiz_exists']
        prev_quiz_passed = prev_quiz_stats['quiz_passed']

        # Determine lock state
        if not prev_completed:
            # Previous lesson not completed
            return {
                'is_locked': True,
                'lock_reason': f'Complete "{prev_lesson_title}" to unlock this lesson',
                'requires_lesson_id': prev_lesson_id,
                'requires_lesson_title': prev_lesson_title,
                'requires_quiz_pass': False,
                'quiz_required': quiz_stats['quiz_required'],
                'quiz_stats': quiz_stats
            }
        elif prev_quiz_required and not prev_quiz_passed:
            # Previous lesson completed but quiz not passed
            return {
                'is_locked': True,
                'lock_reason': f'Pass the quiz for "{prev_lesson_title}" to unlock this lesson',
                'requires_lesson_id': prev_lesson_id,
                'requires_lesson_title': prev_lesson_title,
                'requires_quiz_pass': True,
                'quiz_required': quiz_stats['quiz_required'],
                'quiz_stats': quiz_stats
            }
        else:
            # Previous lesson completed and quiz passed (or no quiz) - UNLOCKED
            return {
                'is_locked': False,
                'lock_reason': '',
                'requires_lesson_id': None,
                'requires_lesson_title': None,
                'requires_quiz_pass': False,
                'quiz_required': quiz_stats['quiz_required'],
                'quiz_stats': quiz_stats
            }

    except Exception as e:
        logger.error(f"Error computing lock state for lesson_id={lesson_id}, user={user.id}: {e}", exc_info=True)
        # Default to locked on error for safety
        return {
            'is_locked': True,
            'lock_reason': 'Error determining lock state',
            'requires_lesson_id': None,
            'requires_lesson_title': None,
            'requires_quiz_pass': False,
            'quiz_required': False,
            'quiz_stats': {}
        }


class GenerateLearningPathView(APIView):
    """
    POST /api/learning-paths/generate/
    Generate a personalized learning path by:
    1. Fetching structured roadmap from roadmap.sh based on learning goals
    2. Searching real courses from YouTube and Udemy for each roadmap topic
    3. Ranking courses by user preferences (platform, rating, difficulty, duration)
    4. Creating a complete learning path with modules and lessons
    """
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def _get_default_thumbnail(platform: str) -> str:
        """
        Return default thumbnail based on platform when course thumbnail is not available

        Args:
            platform: Course platform (youtube, udemy, coursera, etc.)

        Returns:
            URL to default placeholder thumbnail for the platform
        """
        # Platform-specific placeholder thumbnails with brand colors
        defaults = {
            'youtube': 'https://via.placeholder.com/320x180/FF0000/FFFFFF?text=YouTube+Video',
            'udemy': 'https://via.placeholder.com/320x180/EC5252/FFFFFF?text=Udemy+Course',
            'coursera': 'https://via.placeholder.com/320x180/0056D2/FFFFFF?text=Coursera+Course',
            'edx': 'https://via.placeholder.com/320x180/02262B/FFFFFF?text=edX+Course',
            'pluralsight': 'https://via.placeholder.com/320x180/F15B2A/FFFFFF?text=Pluralsight',
            'linkedin': 'https://via.placeholder.com/320x180/0077B5/FFFFFF?text=LinkedIn+Learning',
            'default': 'https://via.placeholder.com/320x180/6B7280/FFFFFF?text=Course'
        }
        # Handle None platform gracefully
        platform_key = platform.lower() if platform else 'default'
        return defaults.get(platform_key, defaults['default'])

    @staticmethod
    def _determine_lesson_type(platform: str, learning_styles: List[str]) -> str:
        """
        Determine lesson type based on platform and user's learning style preferences.

        This ensures lesson types match the user's selected content type preferences:
        - If user selected 'videos' → lessons are marked as 'video'
        - If user selected 'reading' → lessons are marked as 'article'
        - If user selected 'hands_on' → lessons are marked as 'interactive'
        - If user selected 'interactive' → lessons are marked as 'interactive'

        Args:
            platform: Course platform (youtube, udemy, coursera, etc.)
            learning_styles: User's selected learning styles

        Returns:
            Lesson type string ('video', 'article', 'interactive', 'project', 'quiz')
        """
        # Map platforms to their primary content types
        platform_types = {
            # Video platforms
            'youtube': 'video',
            'udemy': 'video',  # Udemy is primarily video-based
            'coursera': 'video',
            'edx': 'video',
            'pluralsight': 'video',
            'linkedin': 'video',

            # Article platforms (reading content)
            'medium': 'article',
            'dev_to': 'article',  # Dev.to developer articles
            'hashnode': 'article',  # Hashnode developer blogs

            # Interactive/coding platforms
            'freecodecamp': 'interactive',  # freeCodeCamp interactive tutorials
            'codecademy': 'interactive',
            'leetcode': 'interactive',
            'exercism': 'interactive',  # Exercism coding exercises

            # Hands-on/project platforms
            'github': 'project',  # GitHub tutorial repositories

            # Legacy preview data (will be removed)
            'preview': 'video',
            'article_preview': 'article',
            'interactive_preview': 'interactive',
            'project_preview': 'project'
        }

        # Get platform's default type (handle None platform gracefully)
        platform_key = platform.lower() if platform else 'default'
        default_type = platform_types.get(platform_key, 'article')

        # Override based on user's learning style preferences
        # This ensures the type matches what the user actually wants
        if 'videos' in learning_styles or 'visual' in learning_styles:
            # User wants videos - keep video types
            if default_type == 'video':
                return 'video'
        elif 'hands_on' in learning_styles:
            # User wants hands-on - prefer interactive/project type
            if platform in ['udemy', 'coursera']:
                return 'project'  # These platforms offer project-based courses
            return 'interactive'
        elif 'reading' in learning_styles or 'articles' in learning_styles:  # Support both for backward compatibility
            # User wants reading material - prefer article type
            return 'article'
        elif 'interactive' in learning_styles:
            # User wants interactive content
            return 'interactive'

        # Fallback to platform default
        return default_type

    @staticmethod
    def analyze_roadmap_complexity(roadmap) -> float:
        """
        Analyze roadmap structure to determine complexity score (0.0 to 1.0).

        Considers:
        - Total topic count (more topics = more complex)
        - Dependency depth (interconnected topics = more complex)
        - Skill diversity (wide range of skills = more complex)
        - Content density (detailed descriptions = more complex)

        Returns:
            float: Complexity score between 0.0 (simple) and 1.0 (very complex)
        """
        nodes = roadmap.nodes if hasattr(roadmap, 'nodes') else []
        total_topics = len(nodes)

        if total_topics == 0:
            return 0.3  # Default moderate complexity

        # Factor 1: Total topic count (normalized to typical range 10-100)
        topic_score = min(total_topics / 80.0, 1.0)

        # Factor 2: Dependency depth (average prerequisites per node)
        total_prerequisites = sum(len(node.prerequisites) if hasattr(node, 'prerequisites') and node.prerequisites else 0 for node in nodes)
        avg_prerequisites = total_prerequisites / total_topics if total_topics > 0 else 0
        dependency_score = min(avg_prerequisites / 4.0, 1.0)  # Normalize to 0-4 prerequisites

        # Factor 3: Skill diversity (unique skills across roadmap)
        unique_skills = set()
        for node in nodes:
            if hasattr(node, 'skills') and node.skills:
                unique_skills.update(node.skills)
        skill_diversity_score = min(len(unique_skills) / 40.0, 1.0)  # Normalize to typical 40 skills

        # Factor 4: Content density (average description length)
        total_content_length = sum(len(node.description) if hasattr(node, 'description') and node.description else 0 for node in nodes)
        avg_content_length = total_content_length / total_topics if total_topics > 0 else 0
        content_score = min(avg_content_length / 400.0, 1.0)  # Normalize to typical 400 chars

        # Weighted combination: topic count is most important, then skills, dependencies, content
        complexity_score = (
            topic_score * 0.35 +           # 35% weight on topic count
            skill_diversity_score * 0.30 + # 30% weight on skill diversity
            dependency_score * 0.20 +      # 20% weight on dependencies
            content_score * 0.15           # 15% weight on content depth
        )

        logger.debug(f"Roadmap complexity analysis: topics={total_topics}, prereqs={avg_prerequisites:.1f}, skills={len(unique_skills)}, score={complexity_score:.2f}")
        return min(complexity_score, 1.0)

    @staticmethod
    def calculate_user_capacity_score(user_preferences: Dict) -> float:
        """
        Calculate user's learning capacity score based on preferences.

        Considers:
        - Time availability (weekly hours)
        - Experience level (impacts learning speed)
        - Learning pace preference
        - Target timeline (urgency factor)
        - Number of learning goals (breadth vs depth)

        Returns:
            float: Capacity score (typically 0.3 to 2.0, higher = can handle more modules)
        """
        basic_info = user_preferences.get('basic_info', {})

        # Factor 1: Time availability (convert to continuous scale)
        time_mapping = {
            '1-2hrs': 1.5,   # 1.5 hours/week average
            '3-5hrs': 4.0,   # 4 hours/week average
            '5+hrs': 7.0     # 7 hours/week average
        }
        weekly_hours = time_mapping.get(basic_info.get('time_availability', '3-5hrs'), 4.0)
        time_score = min(weekly_hours / 8.0, 1.0)  # Normalize to 0-1 (8hrs = max normal)

        # Factor 2: Experience level (affects learning efficiency)
        experience_multipliers = {
            'complete_beginner': 0.7,  # Needs more foundational work, fewer modules
            'some_basics': 0.85,
            'intermediate': 1.0,       # Baseline
            'advanced': 1.25           # Can handle more modules efficiently
        }
        exp_multiplier = experience_multipliers.get(basic_info.get('experience_level', 'intermediate'), 1.0)

        # Factor 3: Learning pace (self-assessed speed)
        pace_multipliers = {
            'slow': 0.75,     # Prefers depth over breadth
            'medium': 1.0,    # Balanced
            'fast': 1.3       # Can cover more ground
        }
        pace_multiplier = pace_multipliers.get(basic_info.get('preferred_pace', 'medium'), 1.0)

        # Factor 4: Timeline urgency
        timeline_factors = {
            '3months': 0.85,   # Tight deadline, focused scope
            '6months': 1.0,    # Normal
            '1year': 1.25,     # More time, can cover more
            'flexible': 1.15   # Slightly expanded scope
        }
        timeline_factor = timeline_factors.get(basic_info.get('target_timeline', '6months'), 1.0)

        # Factor 5: Learning goals breadth (more goals = more modules needed)
        learning_goals = basic_info.get('learning_goals', [])
        goals_count = len(learning_goals) if learning_goals else 1
        goals_factor = min(goals_count / 2.5, 1.3)  # Normalize: 1 goal=0.4, 3 goals=1.2, 5+ goals=1.3

        # Combined capacity score (multiplicative for compounding effects)
        capacity = time_score * exp_multiplier * pace_multiplier * timeline_factor * goals_factor

        logger.debug(f"User capacity: time={weekly_hours}hrs, exp={exp_multiplier}, pace={pace_multiplier}, timeline={timeline_factor}, goals={goals_count}, total={capacity:.2f}")
        return capacity

    @staticmethod
    def calculate_deterministic_variance(user_preferences: Dict) -> int:
        """
        Calculate module count adjustment based on user constraints (DETERMINISTIC).

        This replaces the random ±0-2 variance with a predictable calculation based on:
        - Time availability: Limited time = fewer modules
        - Timeline pressure: Urgent goals = fewer modules
        - Career urgency: Career change = more modules (comprehensive prep)

        Args:
            user_preferences: User preference dict with basic_info

        Returns:
            int: Variance adjustment (-2 to +2)
        """
        variance = 0
        basic_info = user_preferences.get('basic_info', {})

        # Time constraint adjustment
        # Less time available = reduce modules to avoid overwhelming
        time_map = {'1-2hrs': -1, '3-5hrs': 0, '5+hrs': +1}
        variance += time_map.get(basic_info.get('time_availability', '3-5hrs'), 0)

        # Timeline pressure adjustment
        # Shorter timeline = reduce modules to stay focused
        timeline_map = {'3months': -1, '6months': 0, '1year': +1, 'flexible': +1}
        variance += timeline_map.get(basic_info.get('target_timeline', '6months'), 0)

        # Career urgency adjustment
        # Career change = more modules (need comprehensive knowledge)
        # Professional = fewer modules (refining specific skills)
        career_map = {
            'student': 0,          # Baseline
            'career_change': +1,   # Need broad coverage
            'skill_upgrade': 0,    # Baseline
            'professional': -1     # Focus on specifics
        }
        variance += career_map.get(basic_info.get('career_stage', 'student'), 0)

        # Clamp to ±2
        return max(-2, min(variance, 2))

    @staticmethod
    def calculate_dynamic_module_count(
        user_preferences: Dict,
        roadmap,  # Full roadmap object for intelligent analysis
        request_override: Optional[int] = None,
        user_profile: Optional['UserContentProfile'] = None  # PHASE 3: Dropout risk adaptation
    ) -> int:
        """
        ML-driven dynamic module count calculation with dropout risk adaptation.

        Uses intelligent analysis of:
        1. Roadmap structure complexity (topic count, dependencies, skills, content depth)
        2. User learning capacity (time, experience, pace, timeline, goals)
        3. [PHASE 3] Dropout risk adaptation (high risk → -30%, medium risk → -15%)
        4. Configurable bounds from Django settings
        5. Optional user override

        This replaces the old hardcoded lookup tables (6/10/12) with a truly adaptive algorithm
        that considers roadmap complexity, user profile, and dropout risk to generate varied,
        intelligent module counts that maximize completion rates.

        Returns:
            int: Optimal module count (typically 4-20, varies based on analysis)
        """
        # Get configurable bounds from Django settings
        MIN_MODULES = settings.LEARNING_PATH_MIN_MODULES
        MAX_MODULES = settings.LEARNING_PATH_MAX_MODULES

        # User override has highest priority
        if request_override and MIN_MODULES <= request_override <= MAX_MODULES:
            logger.info(f"📌 Using user override: {request_override} modules")
            return request_override

        # Step 1: Analyze roadmap complexity (0.0 to 1.0)
        complexity_score = GenerateLearningPathView.analyze_roadmap_complexity(roadmap)

        # Step 2: Calculate user capacity score (typically 0.3 to 2.0)
        capacity_score = GenerateLearningPathView.calculate_user_capacity_score(user_preferences)

        # Step 3: ML-driven module count formula
        # Base formula: scale from MIN to MAX based on complexity and capacity
        range_size = MAX_MODULES - MIN_MODULES

        # Optimal modules = minimum + (range × complexity × capacity)
        # This ensures:
        # - Simple roadmap + beginner + low time = closer to MIN_MODULES
        # - Complex roadmap + advanced + high time = closer to MAX_MODULES
        optimal_modules = MIN_MODULES + (range_size * complexity_score * min(capacity_score, 1.5))

        # Step 4: Roadmap size constraint (can't exceed 80% of available topics)
        total_topics = len(roadmap.nodes) if hasattr(roadmap, 'nodes') else 10
        max_from_roadmap = int(total_topics * 0.8)

        # Step 5: Apply all constraints
        final_count = int(optimal_modules)
        final_count = max(MIN_MODULES, min(final_count, max_from_roadmap, MAX_MODULES))

        # Step 6: Add deterministic variance based on user constraints
        # This replaces random variance with predictable adjustment
        variance = GenerateLearningPathView.calculate_deterministic_variance(user_preferences)
        final_count_with_variance = max(MIN_MODULES, min(final_count + variance, max_from_roadmap, MAX_MODULES))

        # PHASE 3 - Step 7: Dropout risk adaptation
        # Users at high risk of dropping out get shorter, more achievable paths
        dropout_reduction = 0.0
        dropout_risk = 0.0
        if user_profile and hasattr(user_profile, 'dropout_risk_score') and user_profile.dropout_risk_score is not None:
            dropout_risk = user_profile.dropout_risk_score
            if dropout_risk >= 0.7:
                # High risk: reduce by 30% to create achievable, confidence-building path
                dropout_reduction = 0.30
                logger.warning(f"⚠️ High dropout risk ({dropout_risk:.2f}) detected → reducing modules by 30%")
            elif dropout_risk >= 0.5:
                # Medium risk: reduce by 15% to prevent overwhelm
                dropout_reduction = 0.15
                logger.info(f"⚡ Medium dropout risk ({dropout_risk:.2f}) → reducing modules by 15%")

        # Apply dropout risk reduction
        if dropout_reduction > 0:
            reduced_count = int(final_count_with_variance * (1 - dropout_reduction))
            final_count_with_variance = max(MIN_MODULES, reduced_count)
            logger.info(f"📉 Dropout adaptation applied: {final_count + variance} → {final_count_with_variance} modules")

        # Intelligent logging for transparency
        dropout_info = f"\n           • Dropout Risk: {dropout_risk:.2f} (reduction: {dropout_reduction*100:.0f}%)" if dropout_risk > 0 else ""
        logger.info(f"""
        🧠 ML-Driven Module Count Calculation:
           Roadmap Analysis:
           • Total Topics: {total_topics}
           • Complexity Score: {complexity_score:.2f} (0=simple, 1=complex)

           User Profile:
           • Capacity Score: {capacity_score:.2f} (higher = can handle more){dropout_info}

           Calculation:
           • Optimal Formula: {MIN_MODULES} + ({range_size} × {complexity_score:.2f} × {min(capacity_score, 1.5):.2f}) = {optimal_modules:.1f}
           • After Constraints: {final_count} modules
           • Variance Applied: {variance:+d}
           • FINAL: {final_count_with_variance} modules
        """)

        return final_count_with_variance

    @staticmethod
    def calculate_lessons_per_module(
        user_preferences: Dict,
        module_index: int,
        total_modules: int,
        request_override: Optional[int] = None,
        user_profile: Optional['UserContentProfile'] = None  # PHASE 3: Session duration optimization
    ) -> int:
        """
        PHASE 2 & 3: ADAPTIVE pacing - Calculate lessons per module dynamically.

        Considers:
        1. User's time availability (1-2hrs → fewer lessons, 5+hrs → more lessons)
        2. Skill level (beginners → fewer lessons to avoid overwhelm, advanced → more)
        3. Preferred pace as a multiplier
        4. Module position (early modules +1 for foundation, late modules -1 for focus)
        5. [PHASE 3] Session duration (< 20 min → -1 lesson, 60+ min → +1 lesson)
        6. [PHASE 3] Attention span (< 15 min → reduce lessons to avoid cognitive overload)

        Range: 2-10 lessons per module (configurable via settings)

        Examples:
        - Beginner, 1-2hrs, slow pace, module 1/10 → 3 lessons (2 base + 1 for early)
        - Intermediate, 3-5hrs, medium pace, module 5/10 → 5 lessons
        - Advanced, 5+hrs, fast pace, 60min sessions, module 10/10 → 9 lessons (9 - 1 late + 1 long session)
        - Beginner, 1-2hrs, 15min sessions, short attention → 2 lessons (minimum, bite-sized)
        """
        # Get configurable bounds from Django settings
        MIN_LESSONS = settings.LEARNING_PATH_MIN_LESSONS
        MAX_LESSONS = settings.LEARNING_PATH_MAX_LESSONS

        # User override has highest priority
        if request_override and MIN_LESSONS <= request_override <= MAX_LESSONS:
            return request_override

        basic_info = user_preferences.get('basic_info', {})

        # Factor 1: Time availability (base lesson count)
        # More time available = can handle more lessons per module
        time_availability = basic_info.get('time_availability', '3-5hrs')
        time_base_map = {
            '1-2hrs': 3,    # Limited time → fewer lessons
            '3-5hrs': 5,    # Moderate time → standard lessons
            '5+hrs': 7      # Lots of time → more lessons
        }
        time_base = time_base_map.get(time_availability, 5)

        # Factor 2: Skill level adjustment
        # Beginners need fewer lessons per module to avoid overwhelm
        # Advanced users can handle more lessons per module
        experience_level = basic_info.get('experience_level', 'some_basics')
        skill_adjustment = 0
        if experience_level == 'complete_beginner':
            skill_adjustment = -1  # Fewer lessons to start slow
        elif experience_level in ['advanced', 'expert']:
            skill_adjustment = +1  # More lessons for experienced users

        # Factor 3: Pace multiplier (affects speed, not quantity)
        # Slow pace = more review/practice, fast pace = skip basics
        pace = basic_info.get('preferred_pace', 'medium')
        pace_multiplier = {'slow': 0.9, 'medium': 1.0, 'fast': 1.1}.get(pace, 1.0)

        # Calculate base lessons with time and skill factors
        base_lessons = time_base + skill_adjustment
        base_lessons = int(base_lessons * pace_multiplier)

        # PHASE 3 - Factor 4.5: Session duration optimization
        # Users with short sessions need bite-sized lessons
        # Users with long sessions can handle deeper dives
        if user_profile and hasattr(user_profile, 'average_session_duration') and user_profile.average_session_duration:
            session_minutes = user_profile.average_session_duration
            if session_minutes < 20:
                base_lessons -= 1  # Short sessions (< 20 min) → fewer lessons for quick wins
                logger.debug(f"📱 Short session duration ({session_minutes} min) → reducing lessons by 1")
            elif session_minutes >= 60:
                base_lessons += 1  # Long sessions (60+ min) → more lessons for deep learning
                logger.debug(f"⏱️ Long session duration ({session_minutes} min) → adding 1 lesson")

        # PHASE 3 - Factor 4.6: Attention span consideration
        # Users with short attention spans need smaller chunks
        if user_profile and hasattr(user_profile, 'attention_span_minutes') and user_profile.attention_span_minutes:
            attention = user_profile.attention_span_minutes
            if attention < 15:
                base_lessons = max(2, base_lessons - 1)  # Very short attention → reduce lessons (min 2)
                logger.debug(f"🎯 Short attention span ({attention} min) → reducing to {base_lessons} lessons")

        # Factor 4: Module position adjustment
        # Early modules (first 33%) get +1 lesson (more foundational content)
        # Middle modules (33-67%) keep base count
        # Late modules (last 33%) get -1 lesson (more advanced, focused)
        position_ratio = (module_index + 1) / total_modules
        if position_ratio <= 0.33:  # First third - foundational
            lessons = base_lessons + 1
        elif position_ratio >= 0.67:  # Last third - advanced
            lessons = base_lessons - 1
        else:  # Middle third - normal
            lessons = base_lessons

        # Apply bounds: Use configurable settings (default 2-10 lessons)
        final_lessons = max(MIN_LESSONS, min(lessons, MAX_LESSONS))

        logger.debug(f"📊 Adaptive pacing: time={time_availability}({time_base}), skill={experience_level}({skill_adjustment:+d}), pace={pace}(×{pace_multiplier}), position={position_ratio:.2f} → {final_lessons} lessons")

        return final_lessons

    def _calculate_preference_hash(self, user_preferences_dict: Dict, generation_request) -> str:
        """
        Generate hash of preferences that affect learning path generation.
        Used for cache invalidation when preferences change.

        This creates a deterministic hash of all user preferences that influence
        the learning path generation algorithm. When preferences change, the hash
        will be different, triggering cache invalidation and regeneration.

        Args:
            user_preferences_dict: Full user preferences from MongoDB
            generation_request: LearningPathRequest with current request parameters

        Returns:
            First 16 characters of SHA256 hash for readability and uniqueness
        """
        # Create cache key data from all preferences that affect generation
        cache_key_data = {
            'learning_goals': sorted(generation_request.learning_goals),
            'experience_level': generation_request.experience_level,
            'preferred_pace': generation_request.preferred_pace,
            'time_availability': generation_request.time_availability,
            'learning_styles': sorted(generation_request.learning_styles),
            'target_timeline': generation_request.target_timeline,
            'content_preferences': user_preferences_dict.get('content_preferences', {}),
        }

        # Create deterministic JSON string (sorted keys for consistency)
        json_str = json.dumps(cache_key_data, sort_keys=True)

        # Return first 16 chars of hash for readability
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]

    def post(self, request):
        """
        Generate learning path based on user preferences

        Request body can override default preferences from user profile
        Returns: Serialized learning path
        """
        # Check if ML services are available
        if not ML_SERVICES_AVAILABLE:
            return APIError.create(
                message="ML services are not available. Please contact administrator.",
                code="ML_SERVICE_UNAVAILABLE",
                status_code=StatusCodes.SERVICE_UNAVAILABLE
            )

        # Validate request
        serializer = LearningPathGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return APIError.create(
                message="Invalid request data",
                code="VALIDATION_ERROR",
                field_errors=serializer.errors,
                status_code=StatusCodes.BAD_REQUEST
            )

        validated_data = serializer.validated_data
        force_regenerate = validated_data.get('force_regenerate', False)

        # Extract optional overrides for dynamic module/lesson calculation
        max_modules_override = validated_data.get('max_modules')
        max_lessons_override = validated_data.get('max_lessons_per_module')

        try:
            # Step 1: Get user preferences
            try:
                user_preference = UserPreference.objects.get(user_id=request.user.id)
                logger.info(f"📥 UserPreference fetched for user {request.user.id}")
                logger.debug(f"   Profile completion: {user_preference.profile_completion_percentage}%")
            except UserPreference.DoesNotExist:
                return APIError.create(
                    message="User preferences not found. Please complete onboarding first.",
                    code="PREFERENCES_NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Check if user has completed enough of profile
            if user_preference.profile_completion_percentage < 60:
                return APIError.create(
                    message="Profile is incomplete. Please complete at least 60% of your profile.",
                    code="INCOMPLETE_PROFILE",
                    status_code=StatusCodes.BAD_REQUEST
                )

            # Step 2: Build generation request from preferences (with optional overrides)
            logger.info(f"📋 Loading preferences for user {request.user.id}")

            # Safe access to basic_info with null-safety check
            basic_info = user_preference.basic_info
            if not basic_info:
                logger.error(f"❌ basic_info is None for user {request.user.id}")
                return APIError.create(
                    message="User profile basic information is missing. Please complete onboarding.",
                    code="BASIC_INFO_MISSING",
                    status_code=StatusCodes.BAD_REQUEST
                )

            logger.info(f"✅ basic_info loaded: goals={basic_info.learning_goals}, level={basic_info.experience_level}")

            # Generate unique request ID for tracking and logging
            request_id = str(uuid.uuid4())

            generation_request = LearningPathRequest(
                user_id=str(request.user.id),
                request_id=request_id,
                learning_goals=validated_data.get('learning_goals', basic_info.learning_goals),
                experience_level=validated_data.get('experience_level', basic_info.experience_level),
                preferred_pace=validated_data.get('preferred_pace', basic_info.preferred_pace),
                time_availability=validated_data.get('time_availability', basic_info.time_availability),
                learning_styles=validated_data.get('learning_styles', basic_info.learning_style),
                target_timeline=validated_data.get('target_timeline', basic_info.target_timeline),
            )

            # Build user preferences dictionary for services with safe content_preferences access
            logger.info(f"🔨 Building preferences dictionary...")

            # Safe access to content_preferences with detailed logging
            content_prefs = user_preference.content_preferences
            if content_prefs:
                try:
                    content_prefs_dict = content_prefs.to_mongo() if hasattr(content_prefs, 'to_mongo') else {}
                    logger.info(f"✅ content_preferences loaded from database: {list(content_prefs_dict.keys())}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to serialize content_preferences: {e}, using defaults")
                    content_prefs_dict = {
                        'preferred_platforms': ['youtube', 'udemy'],
                        'content_types': ['video', 'interactive'],
                        'difficulty_preference': 'mixed',
                        'duration_preference': 'mixed',
                        'language_preference': ['english'],
                        'instructor_ratings_min': 3.0
                    }
            else:
                logger.warning(f"⚠️ content_preferences is None for user {request.user.id}, using defaults")
                # Create minimal default content preferences
                content_prefs_dict = {
                    'preferred_platforms': ['youtube', 'udemy'],
                    'content_types': ['video', 'interactive'],
                    'difficulty_preference': 'mixed',
                    'duration_preference': 'mixed',
                    'language_preference': ['english'],
                    'instructor_ratings_min': 3.0
                }

            user_preferences_dict = {
                'basic_info': {
                    'learning_goals': generation_request.learning_goals,
                    'experience_level': generation_request.experience_level,
                    'preferred_pace': generation_request.preferred_pace,
                    'time_availability': generation_request.time_availability,
                    'learning_style': generation_request.learning_styles,
                    'target_timeline': generation_request.target_timeline,
                },
                'content_preferences': content_prefs_dict
            }

            logger.info(f"📦 Final preferences_dict built successfully")
            logger.debug(f"   Keys: {list(user_preferences_dict.keys())}")
            logger.debug(f"   content_preferences keys: {list(user_preferences_dict.get('content_preferences', {}).keys())}")

            # Step 3: Smart cache check with preference hash comparison (unless force_regenerate)
            # Only return cached path if preferences haven't changed
            if not force_regenerate:
                # Calculate current preference hash
                current_pref_hash = self._calculate_preference_hash(user_preferences_dict, generation_request)

                cached_recommendation = CourseRecommendation.get_valid_recommendations(request.user.id)
                if cached_recommendation and len(cached_recommendation.learning_paths) > 0:
                    # Check if preferences have changed since cache was created
                    cached_pref_hash = cached_recommendation.generation_context.get('preferences_hash', '')

                    if cached_pref_hash == current_pref_hash:
                        # Preferences unchanged - return cached path
                        logger.info(f"✅ Cache HIT: Preferences unchanged (hash: {current_pref_hash})")
                        learning_path = cached_recommendation.learning_paths[0]
                        serialized = LearningPathSerializer(self._learning_path_to_dict(learning_path))
                        return APISuccess.create(
                            data=serialized.data,
                            message="Learning path retrieved from cache (preferences unchanged)",
                            status_code=StatusCodes.OK
                        )
                    else:
                        # Preferences changed - invalidate cache and regenerate
                        logger.info(f"🔄 Cache MISS: Preferences changed (hash: {cached_pref_hash} → {current_pref_hash}), regenerating path")
                else:
                    logger.info(f"🔄 Cache MISS: No cached path found for user {request.user.id}")
            else:
                logger.info(f"🔄 Force regenerate requested, skipping cache")

            # Step 4: Fetch roadmap from roadmap.sh and search for real courses
            roadmap_service = RoadmapService()
            course_search_service = CourseSearchService()

            # PHASE 3: Fetch and merge roadmaps for all learning goals (multi-goal support)
            roadmap = roadmap_service.get_merged_roadmap_for_goals(
                generation_request.learning_goals,
                user_preferences_dict
            )

            if not roadmap:
                # Return error if no roadmap found
                return APIError.create(
                    message=f"No roadmap available for '{generation_request.learning_goals[0]}'. Supported goals: web_dev, ai_ml, data_science, devops, cybersecurity, blockchain, mobile_dev",
                    code="ROADMAP_NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Filter roadmap by user's experience level
            filtered_roadmap = roadmap_service.filter_roadmap_by_experience(
                roadmap,
                generation_request.experience_level
            )

            # PHASE 2: Skill gap analysis - filter by user's current skills
            # Get or create user content profile to access current_skills
            try:
                user_profile = UserContentProfile.objects.get(user_id=str(request.user.id))
                current_skills = user_profile.current_skills or []
                logger.info(f"🎯 User has {len(current_skills)} current skills: {current_skills[:3]}{'...' if len(current_skills) > 3 else ''}")
            except UserContentProfile.DoesNotExist:
                # No profile yet - user is complete beginner
                current_skills = []
                user_profile = None  # Initialize to None for new users without a profile
                logger.info(f"🎯 No content profile found - assuming beginner with no current skills")

            # Apply skill gap analysis if user has any skills
            if current_skills:
                # Step 1: Filter out nodes user already knows
                skill_filtered_roadmap = roadmap_service.filter_roadmap_by_skills(
                    filtered_roadmap,
                    current_skills,
                    similarity_threshold=0.7  # 70% similarity to consider skill "known"
                )

                # Step 2: Add back prerequisites for nodes user doesn't know
                filtered_roadmap = roadmap_service.add_prerequisite_nodes(
                    roadmap,
                    current_skills,
                    skill_filtered_roadmap
                )
                logger.info(f"✅ Skill gap analysis complete: {len(filtered_roadmap.nodes)} nodes in personalized roadmap")
            else:
                logger.info(f"⏭️  Skipping skill gap analysis (no current skills)")

            # Convert roadmap nodes to modules with real course resources
            modules_data = []
            total_duration = 0

            # Calculate dynamic module count using ML-driven intelligent analysis
            # Analyzes roadmap structure + user profile for truly adaptive module count
            # PHASE 3: Now includes dropout risk adaptation to maximize completion rates
            dynamic_module_count = self.calculate_dynamic_module_count(
                user_preferences=user_preferences_dict,
                roadmap=filtered_roadmap,  # Pass full roadmap for intelligent analysis
                request_override=max_modules_override,
                user_profile=user_profile  # PHASE 3: Pass profile for dropout risk adaptation
            )

            # PHASE 3: Priority-based module selection (not just first N modules)
            # Select optimal modules based on target_skills, goal alignment, career fit, etc.
            selected_modules = roadmap_service.select_optimal_modules(
                filtered_roadmap,
                user_preferences_dict,
                user_profile,  # UserContentProfile with target_skills, struggle_areas, etc.
                dynamic_module_count
            )

            logger.info(f"📊 Selected {len(selected_modules)} high-priority modules for learning path")

            # Iterate through intelligently selected modules
            for idx, node in enumerate(selected_modules, 1):
                # Calculate dynamic lesson count for this module based on pace and position
                # PHASE 3: Now includes session duration and attention span optimization
                dynamic_lesson_count = self.calculate_lessons_per_module(
                    user_preferences=user_preferences_dict,
                    module_index=idx - 1,  # 0-indexed for calculation
                    total_modules=dynamic_module_count,
                    request_override=max_lessons_override,
                    user_profile=user_profile  # PHASE 3: Pass profile for session duration/attention span
                )

                # Enrich search query with user preferences (difficulty, learning style, duration, goal context)
                # This fixes generic queries like "Introduction" → "Introduction to Mobile Development beginner tutorial"
                enriched_query = course_search_service.enrich_search_query(
                    base_topic=node.title,
                    user_preferences=user_preferences_dict,
                    learning_goal=generation_request.learning_goals[0] if generation_request.learning_goals else None,
                    node_context={'difficulty': node.difficulty, 'category': node.category}
                )

                # Search for courses using enriched query with progressive fallback
                # BUG FIX: Uses search_courses_with_fallback() to prevent empty modules
                scored_courses = course_search_service.search_courses_with_fallback(
                    topic=enriched_query,  # Use enriched query instead of bare node.title
                    user_preferences=user_preferences_dict,
                    max_results=dynamic_lesson_count  # Use dynamic count instead of hardcoded 5
                )

                # BUG FIX: Validate courses were found - skip module if empty
                if not scored_courses:
                    logger.warning(f"⚠️ No courses found for module '{node.title}' even after fallback - skipping module")
                    continue  # Skip to next module

                # Build lessons from dynamically calculated number of courses
                lessons = []
                for scored_course in scored_courses[:dynamic_lesson_count]:
                    course = scored_course.course

                    # NEW: Determine lesson type based on user's learning_styles + platform
                    # This respects user's content type preferences
                    lesson_type = self._determine_lesson_type(
                        course.platform,
                        generation_request.learning_styles
                    )

                    # Handle duration - GitHub repos and some platforms don't have duration_hours
                    duration_hours = getattr(course, 'duration_hours', None)
                    duration_minutes = int(duration_hours * 60) if duration_hours else 60  # Default to 1 hour for repos/articles

                    lessons.append({
                        'lesson_id': f"{node.id}-lesson-{len(lessons) + 1}",
                        'title': course.title,
                        'description': course.description,
                        'type': lesson_type,  # Now respects user's content preferences!
                        'duration_minutes': duration_minutes,
                        'url': course.url,
                        'thumbnail': course.thumbnail_url or self._get_default_thumbnail(course.platform),
                        'platform': course.platform,
                        'instructor': getattr(course, 'instructor', None),
                        'rating': getattr(course, 'rating', None),
                        'difficulty': getattr(course, 'difficulty', None),
                        'price': getattr(course, 'price', None),
                        'relevance_score': scored_course.relevance_score,
                        'is_completed': False,
                        'order': len(lessons) + 1
                    })

                # Calculate module duration from lessons (convert minutes back to hours)
                module_duration = sum(lesson['duration_minutes'] for lesson in lessons) / 60
                total_duration += module_duration

                # Create module with roadmap node data
                module = {
                    'module_id': f"module-{idx}",
                    'title': node.title,
                    'description': node.description,
                    'order': idx,
                    'estimated_hours': module_duration,
                    'difficulty': node.difficulty,
                    'skills_covered': node.skills,
                    'lessons': lessons,
                    'is_completed': False,
                    'prerequisites': node.prerequisites
                }

                # BUG FIX: Only add module if it has lessons (defense in depth)
                if lessons:
                    modules_data.append(module)
                else:
                    logger.warning(f"⚠️ Module '{node.title}' has no lessons - excluding from learning path")
                    # Adjust total_duration back since we're not adding this module
                    total_duration -= module_duration

            # Create learning path metadata
            # VALIDATION: Ensure minimum duration to pass MongoEngine validation (min_value=1)
            # If no content found (duration = 0), set to 1 hour minimum instead of arbitrary 10 hours
            if total_duration < 1:
                validated_duration = 1.0
                if total_duration == 0:
                    logger.warning("⚠️ Learning path has no content (0 lessons found). Duration set to 1 hour minimum.")
                else:
                    logger.warning(f"⚠️ Learning path has very short duration {total_duration}h, setting to 1 hour minimum to pass validation.")
            else:
                validated_duration = round(total_duration, 1)

            learning_path_data = {
                'path_id': f"lp-{request.user.id}-{int(datetime.utcnow().timestamp())}",
                'title': f"{filtered_roadmap.title} Learning Path",
                'description': filtered_roadmap.description,
                'estimated_duration_hours': validated_duration,
                'difficulty_level': generation_request.experience_level,
                'prerequisites': [],
            }

            # Add data quality indicator
            uses_preview_data = any(
                lesson.get('platform') == 'preview'
                for module in modules_data
                for lesson in module.get('lessons', [])
            )
            learning_path_data['data_quality'] = {
                'uses_preview_data': uses_preview_data,
                'message': 'Some courses are preview data. Configure YouTube/Udemy API keys for real courses.' if uses_preview_data else 'All courses are from real platforms.'
            }

            # Step 4.5: Phase 3 - Generate career insights and enhancements
            logger.info(f"🎯 Phase 3: Generating career insights and learning outcomes...")

            career_service = get_career_insights_service()

            # Generate career insights
            learning_goals_str = ', '.join(generation_request.learning_goals)
            # Location field may not exist in basic_info, use empty string as fallback
            user_location = getattr(basic_info, 'location', '')

            career_insights = career_service.generate_career_insights(
                learning_goals=learning_goals_str,
                modules=modules_data,
                user_location=user_location
            )

            # Extract skills gained from modules
            skills_gained = career_service.extract_skills_from_modules(modules_data)

            # Generate project milestones
            domain = career_service.map_learning_goals_to_career_domain(learning_goals_str)
            project_milestones = career_service.generate_project_milestones(
                modules=modules_data,
                domain=domain
            )

            # Add learning outcomes to each module using roadmap service
            roadmap_service = RoadmapService()
            for module in modules_data:
                learning_outcomes = roadmap_service.generate_module_learning_outcomes(
                    module_title=module.get('title', ''),
                    module_description=module.get('description', ''),
                    difficulty=module.get('difficulty', 'intermediate'),
                    lessons=module.get('lessons', [])
                )
                module['learning_outcomes'] = learning_outcomes

            logger.info(
                f"✅ Phase 3 complete: "
                f"{len(career_insights.career_roles)} roles, "
                f"{career_insights.total_job_openings} jobs, "
                f"{len(skills_gained)} skills, "
                f"{len(project_milestones)} milestones"
            )

            # Step 5: Save to MongoDB with smart caching using preference hash
            # Learning path is saved for persistence and retrieval
            # Cache invalidation happens automatically via preference hash comparison

            # Create learning path object
            learning_path = LearningPath(
                path_id=learning_path_data.get('path_id', f"lp-{request.user.id}-{int(datetime.utcnow().timestamp())}"),
                title=learning_path_data.get('title', f"Learning Path for {', '.join(generation_request.learning_goals)}"),
                description=learning_path_data.get('description', ''),
                estimated_duration_hours=learning_path_data.get('estimated_duration_hours', round(total_duration, 1) if total_duration > 0 else 40),
                difficulty_level=learning_path_data.get('difficulty_level', generation_request.experience_level),
                modules=modules_data,  # New module-based structure (now includes learning_outcomes)
                course_sequence=[],  # Legacy field
                prerequisites=learning_path_data.get('prerequisites', []),
                created_by='ai',
                status='active',  # Phase 2: Set initial status for new learning paths
                # Phase 3: Career insights and enhancements
                career_insights=career_insights,
                skills_gained=skills_gained,
                project_milestones=project_milestones,
            )

            # Save to MongoDB with preference hash for smart cache invalidation
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=request.user.id)
                created = False
                # BUG FIX: DON'T clear existing paths - preserve for multiple learning paths support
                # Just update expiry timestamp to extend cache
                course_recommendation.expires_at = datetime.utcnow() + timedelta(hours=24)  # Cache for 24 hours
            except CourseRecommendation.DoesNotExist:
                course_recommendation = CourseRecommendation(
                    user_id=request.user.id,
                    expires_at=datetime.utcnow() + timedelta(hours=24),
                    learning_paths=[]
                )
                created = True

            course_recommendation.learning_paths.append(learning_path)

            # Calculate preference hash for cache invalidation
            current_pref_hash = self._calculate_preference_hash(user_preferences_dict, generation_request)

            course_recommendation.generation_context = {
                'learning_goals': generation_request.learning_goals,
                'experience_level': generation_request.experience_level,
                'generated_at': datetime.utcnow().isoformat(),
                'roadmap_source': 'roadmap.sh',
                'roadmap_id': filtered_roadmap.roadmap_id,
                'total_nodes': len(filtered_roadmap.nodes),
                'filtered_nodes': len(modules_data),
                'course_sources': ['youtube', 'udemy'],
                'preferences_hash': current_pref_hash,  # NEW: For smart cache invalidation
                'dynamic_module_count': dynamic_module_count,  # NEW: For transparency
            }

            # NEW: Specific save with error handling for MongoDB save failures
            try:
                course_recommendation.save()
                logger.info(f"💾 MongoDB SAVE SUCCESS: Learning path saved (hash: {current_pref_hash}, modules: {dynamic_module_count})")
            except Exception as mongo_error:
                logger.error(f"❌ MongoDB SAVE FAILED: {str(mongo_error)}", exc_info=True)
                return APIError.create(
                    message=f"Learning path generated but failed to save: {str(mongo_error)}",
                    code="MONGODB_SAVE_FAILED",
                    status_code=StatusCodes.INTERNAL_SERVER_ERROR
                )

            # Step 6: Return serialized response with debug roadmap info
            serialized = LearningPathSerializer(self._learning_path_to_dict(learning_path))

            # Add debug roadmap information above the learning path
            response_data = {
                'debug_roadmap': {
                    'roadmap_id': filtered_roadmap.roadmap_id,
                    'title': filtered_roadmap.title,
                    'description': filtered_roadmap.description,
                    'category': filtered_roadmap.category,
                    'total_nodes': len(filtered_roadmap.nodes),
                    'selected_nodes': dynamic_module_count,
                    'experience_filter_applied': generation_request.experience_level,
                    'nodes': [
                        {
                            'id': node.id,
                            'title': node.title,
                            'description': node.description[:100] + '...' if len(node.description) > 100 else node.description,
                            'difficulty': node.difficulty,
                            'category': node.category,
                            'estimated_hours': node.estimated_hours,
                            'prerequisites': node.prerequisites,
                            'skills': node.skills,
                            'selected_for_path': idx < dynamic_module_count
                        }
                        for idx, node in enumerate(filtered_roadmap.nodes)
                    ]
                },
                'learning_path': serialized.data
            }

            return APISuccess.create(
                data=response_data,
                message="Learning path generated successfully",
                status_code=StatusCodes.CREATED
            )

        except Exception as e:
            return APIError.create(
                message=f"Failed to generate learning path: {str(e)}",
                code="GENERATION_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )

    def _learning_path_to_dict(self, learning_path: LearningPath) -> Dict[str, Any]:
        """Convert LearningPath EmbeddedDocument to dictionary for serialization"""
        return {
            'path_id': learning_path.path_id,
            'title': learning_path.title,
            'description': learning_path.description,
            'estimated_duration_hours': learning_path.estimated_duration_hours,
            'difficulty_level': learning_path.difficulty_level,
            'modules': learning_path.modules,
            'prerequisites': learning_path.prerequisites,
            'created_at': learning_path.started_at or datetime.utcnow(),
            'created_by': learning_path.created_by,
            'status': 'not_started',
            'progress_percentage': learning_path.completion_rate * 100 if learning_path.completion_rate else 0.0,
        }


class ListLearningPathsView(APIView):
    """
    GET /api/learning-paths/
    List all available learning paths for the authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retrieve all learning paths for user

        Returns: List of learning paths with status and progress
        """
        try:
            # Get user's course recommendations
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=request.user.id)
            except CourseRecommendation.DoesNotExist:
                return APISuccess.create(
                    data=[],
                    message="No learning paths found. Generate your first path!",
                    status_code=StatusCodes.OK
                )

            # Get user content profile for progress data
            try:
                content_profile = UserContentProfile.objects.get(user_id=request.user.id)
            except UserContentProfile.DoesNotExist:
                content_profile = None

            # Serialize learning paths with progress
            paths_data = []
            for learning_path in course_recommendation.learning_paths:
                path_dict = self._enrich_with_progress(learning_path, content_profile)
                paths_data.append(path_dict)

            serialized = LearningPathSerializer(paths_data, many=True)
            return APISuccess.create(
                data=serialized.data,
                message=f"Found {len(paths_data)} learning path(s)",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            return APIError.create(
                message=f"Failed to retrieve learning paths: {str(e)}",
                code="RETRIEVAL_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )

    def _enrich_with_progress(self, learning_path: LearningPath, content_profile: UserContentProfile) -> Dict[str, Any]:
        """Add progress data to learning path dict"""
        path_dict = {
            'path_id': learning_path.path_id,
            'title': learning_path.title,
            'description': learning_path.description,
            'estimated_duration_hours': learning_path.estimated_duration_hours,
            'difficulty_level': learning_path.difficulty_level,
            'modules': learning_path.modules,
            'prerequisites': learning_path.prerequisites,
            'created_at': learning_path.started_at or datetime.utcnow(),
            'created_by': learning_path.created_by,
            'started_at': learning_path.started_at,
            'completed_at': learning_path.completed_at,
            'progress_percentage': learning_path.completion_rate * 100 if learning_path.completion_rate else 0.0,
        }

        # Determine status
        if learning_path.completed_at:
            path_dict['status'] = 'completed'
        elif learning_path.started_at:
            path_dict['status'] = 'in_progress'
        else:
            path_dict['status'] = 'not_started'

        return path_dict


class LearningPathDetailView(APIView):
    """
    GET /api/learning-paths/<path_id>/
    Get detailed information about a specific learning path
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, path_id):
        """
        Retrieve single learning path with full details and progress

        Args:
            path_id: Unique identifier for the learning path

        Returns: Detailed learning path with module/lesson progress
        """
        try:
            # Get user's course recommendations
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=request.user.id)
            except CourseRecommendation.DoesNotExist:
                return APIError.create(
                    message="No learning paths found for this user",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Find specific learning path
            learning_path = None
            for path in course_recommendation.learning_paths:
                if path.path_id == path_id:
                    learning_path = path
                    break

            if not learning_path:
                return APIError.create(
                    message=f"Learning path '{path_id}' not found",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Get user content profile for progress
            try:
                content_profile = UserContentProfile.objects.get(user_id=request.user.id)
            except UserContentProfile.DoesNotExist:
                content_profile = None

            # Enrich with progress data
            path_dict = self._enrich_with_detailed_progress(learning_path, content_profile)

            serialized = LearningPathSerializer(path_dict)
            return APISuccess.create(
                data=serialized.data,
                message="Learning path retrieved successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            return APIError.create(
                message=f"Failed to retrieve learning path: {str(e)}",
                code="RETRIEVAL_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )

    def _enrich_with_detailed_progress(self, learning_path: LearningPath, content_profile: UserContentProfile) -> Dict[str, Any]:
        """
        Add detailed progress data and lock states at module and lesson levels.

        For each lesson, computes:
        - Completion status
        - Progress percentage
        - Lock state (is_locked, requires_lesson_id, etc.)
        - Quiz information (required, passed, best_score)
        """
        # Create a deep copy of modules to avoid modifying original
        enriched_modules = []

        for module in learning_path.modules:
            module_dict = dict(module)  # Convert to dict if EmbeddedDocument
            enriched_lessons = []

            lessons = module.get('lessons', [])
            for lesson in lessons:
                lesson_dict = dict(lesson)  # Convert to dict if needed
                lesson_id = lesson.get('lesson_id')

                # Get completion status
                is_completed = _is_lesson_completed(lesson_id, self.request.user) if content_profile else False

                # Get progress percentage from UserContentProfile
                progress_pct = 0.0
                if content_profile:
                    for in_prog in content_profile.in_progress_content:
                        if in_prog.get('content_id') == lesson_id:
                            progress_pct = in_prog.get('progress_percentage', 0.0)
                            break

                # Compute lock state for this lesson
                lock_state = _compute_lesson_lock_state(
                    path_id=learning_path.path_id,
                    lesson_id=lesson_id,
                    user=self.request.user,
                    learning_path=learning_path
                )

                # Add enrichment fields to lesson
                lesson_dict['completed'] = is_completed
                lesson_dict['progress_percentage'] = progress_pct
                lesson_dict['is_locked'] = lock_state['is_locked']
                lesson_dict['lock_reason'] = lock_state.get('lock_reason', '')
                lesson_dict['requires_lesson_id'] = lock_state.get('requires_lesson_id')
                lesson_dict['requires_lesson_title'] = lock_state.get('requires_lesson_title')
                lesson_dict['requires_quiz_pass'] = lock_state.get('requires_quiz_pass', False)

                # Add quiz information
                quiz_stats = lock_state.get('quiz_stats', {})
                lesson_dict['quiz_required'] = quiz_stats.get('quiz_required', False)
                lesson_dict['quiz_completed'] = quiz_stats.get('quiz_completed', False)
                lesson_dict['quiz_passed'] = quiz_stats.get('quiz_passed', False)
                lesson_dict['quiz_best_score'] = quiz_stats.get('best_score')
                lesson_dict['quiz_total_attempts'] = quiz_stats.get('total_attempts', 0)

                enriched_lessons.append(lesson_dict)

            # Calculate module-level progress
            total_lessons = len(enriched_lessons)
            completed_lessons = sum(1 for l in enriched_lessons if l.get('completed', False))
            module_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0

            module_dict['lessons'] = enriched_lessons
            module_dict['completed_lessons'] = completed_lessons
            module_dict['total_lessons'] = total_lessons
            module_dict['progress_percentage'] = module_progress

            enriched_modules.append(module_dict)

        # Calculate overall progress percentage
        total_lessons_all = sum(m.get('total_lessons', 0) for m in enriched_modules)
        completed_lessons_all = sum(m.get('completed_lessons', 0) for m in enriched_modules)
        overall_progress = (completed_lessons_all / total_lessons_all * 100) if total_lessons_all > 0 else 0.0

        # Phase 3: Convert career insights data to dict for JSON serialization
        career_insights_data = None
        if learning_path.career_insights:
            # Convert MongoEngine EmbeddedDocument to dict
            if hasattr(learning_path.career_insights, 'to_mongo'):
                career_insights_data = learning_path.career_insights.to_mongo().to_dict()
            else:
                career_insights_data = dict(learning_path.career_insights)

        skills_gained_data = []
        if learning_path.skills_gained:
            skills_gained_data = [
                skill.to_mongo().to_dict() if hasattr(skill, 'to_mongo') else dict(skill)
                for skill in learning_path.skills_gained
            ]

        project_milestones_data = []
        if learning_path.project_milestones:
            project_milestones_data = [
                milestone.to_mongo().to_dict() if hasattr(milestone, 'to_mongo') else dict(milestone)
                for milestone in learning_path.project_milestones
            ]

        # Return enriched path data
        return {
            'path_id': learning_path.path_id,
            'title': learning_path.title,
            'description': learning_path.description,
            'estimated_duration_hours': learning_path.estimated_duration_hours,
            'difficulty_level': learning_path.difficulty_level,
            'modules': enriched_modules,
            'prerequisites': learning_path.prerequisites,
            'created_at': learning_path.started_at or datetime.utcnow(),
            'created_by': learning_path.created_by,
            'started_at': learning_path.started_at,
            'completed_at': learning_path.completed_at,
            'progress_percentage': overall_progress,
            'status': 'completed' if learning_path.completed_at else ('in_progress' if learning_path.started_at else 'not_started'),
            'is_customized': learning_path.is_customized,
            'customizations': learning_path.customizations,
            # Phase 3: Career insights and enhanced learning outcomes
            'career_insights': career_insights_data,
            'skills_gained': skills_gained_data,
            'project_milestones': project_milestones_data,
        }


class StartLearningPathView(APIView):
    """
    POST /api/learning-paths/<path_id>/start/
    Mark a learning path as started
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, path_id):
        """
        Start a learning path

        Updates: started_at timestamp, creates progress tracking entry
        """
        try:
            # Get course recommendation
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=request.user.id)
            except CourseRecommendation.DoesNotExist:
                return APIError.create(
                    message="Learning path not found",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Find and update learning path
            learning_path = None
            for path in course_recommendation.learning_paths:
                if path.path_id == path_id:
                    learning_path = path
                    break

            if not learning_path:
                return APIError.create(
                    message=f"Learning path '{path_id}' not found",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Mark as started
            if not learning_path.started_at:
                learning_path.started_at = datetime.utcnow()
                course_recommendation.save()

            # TODO: Create entry in UserContentProfile.in_progress_content
            # TODO: Log interaction event in UserAnalytics

            return APISuccess.create(
                data={'path_id': path_id, 'started_at': learning_path.started_at.isoformat()},
                message="Learning path started successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            return APIError.create(
                message=f"Failed to start learning path: {str(e)}",
                code="START_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class UpdateProgressView(APIView):
    """
    PATCH /api/learning-paths/<path_id>/progress/
    Update progress on a lesson/module
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, path_id):
        """
        Update progress for a specific lesson

        Request body: ProgressUpdateSerializer data
        """
        # Validate request
        serializer = ProgressUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return APIError.create(
                message="Invalid progress data",
                code="VALIDATION_ERROR",
                field_errors=serializer.errors,
                status_code=StatusCodes.BAD_REQUEST
            )

        validated_data = serializer.validated_data

        try:
            # Step 1: Get or create UserContentProfile
            try:
                content_profile = UserContentProfile.objects.get(user_id=request.user.id)
            except UserContentProfile.DoesNotExist:
                content_profile = UserContentProfile(
                    user_id=request.user.id,
                    current_skills=[],
                    learning_goals=[],
                    in_progress_content=[],
                    completed_courses=[]
                )
                content_profile.save()
                logger.info(f"Created new UserContentProfile for user {request.user.id}")

            # Step 2: Determine if lesson is completed
            is_completed = validated_data.get('completed', False) or validated_data.get('progress_percentage', 0) >= 100

            # Step 2.5: QUIZ VALIDATION - Check if quiz must be passed before completion
            lesson_id = validated_data['lesson_id']
            if is_completed:
                # Get quiz stats for this lesson
                quiz_stats = _get_quiz_stats(
                    path_id=path_id,
                    lesson_id=lesson_id,
                    user=request.user
                )

                # If quiz exists and user hasn't passed it, prevent completion
                if quiz_stats['quiz_exists'] and not quiz_stats['quiz_passed']:
                    return APIError.create(
                        message="You must pass the quiz for this lesson before marking it as completed",
                        code="QUIZ_REQUIRED",
                        details={
                            'quiz_required': True,
                            'quiz_passed': False,
                            'quiz_completed': quiz_stats['quiz_completed'],
                            'best_score': quiz_stats['best_score'],
                            'passing_score_percentage': quiz_stats['passing_score_percentage'],
                            'total_attempts': quiz_stats['total_attempts'],
                            'lesson_id': lesson_id
                        },
                        status_code=StatusCodes.FORBIDDEN
                    )

            # Step 3: Update progress in UserContentProfile
            progress_pct = validated_data.get('progress_percentage', 0)

            # Check if content is already being tracked
            content_exists = any(
                p.get('content_id') == lesson_id
                for p in content_profile.in_progress_content
            ) or any(
                c.get('course_id') == lesson_id
                for c in content_profile.completed_courses
            )

            # If new content, start tracking it first
            if not content_exists and not is_completed:
                content_profile.start_content({
                    'content_id': lesson_id,
                    'platform': validated_data.get('platform', 'unknown'),
                    'title': validated_data.get('lesson_title', 'Lesson'),
                    'progress_percentage': progress_pct
                })
                logger.info(f"🆕 Started tracking lesson {lesson_id}")

            if is_completed:
                # Mark as completed - use dictionary format
                content_profile.add_completed_course({
                    'course_id': lesson_id,
                    'platform': validated_data.get('platform', 'unknown'),
                    'title': validated_data.get('lesson_title', 'Lesson'),
                    'completion_rate': 1.0,
                    'rating': None,
                    'duration_hours': validated_data.get('time_spent_minutes', 0) / 60.0 if validated_data.get('time_spent_minutes') else None
                })
                # Remove from in_progress if it exists there
                content_profile.in_progress_content = [
                    p for p in content_profile.in_progress_content
                    if p.get('content_id') != lesson_id
                ]
                logger.info(f"✅ Marked lesson {lesson_id} as completed")
            else:
                # Update in-progress (only takes content_id and progress_percentage)
                content_profile.update_content_progress(lesson_id, progress_pct)
                logger.info(f"📊 Updated progress: {progress_pct}%")

            content_profile.save()

            # Step 4: Update LearningPath in CourseRecommendation
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=request.user.id)

                # Find the learning path
                target_path = None
                for learning_path in course_recommendation.learning_paths:
                    if learning_path.path_id == path_id:
                        target_path = learning_path
                        break

                if target_path:
                    # Update last accessed
                    target_path.last_accessed = datetime.utcnow()

                    # Update lesson progress (modules and lessons are dicts, not objects)
                    for module in target_path.modules:
                        if module.get('module_id') == validated_data['module_id']:
                            lessons = module.get('lessons', [])
                            for lesson in lessons:
                                if lesson.get('lesson_id') == validated_data['lesson_id']:
                                    lesson['completed'] = is_completed
                                    lesson['progress_percentage'] = validated_data.get('progress_percentage', 0)
                                    break

                    # Recalculate overall progress
                    target_path.calculate_progress(content_profile)

                    # Mark as started if first interaction
                    if not target_path.started_at:
                        target_path.started_at = datetime.utcnow()

                    course_recommendation.save()
                    logger.info(f"💾 Updated learning path {path_id} in MongoDB")

            except CourseRecommendation.DoesNotExist:
                logger.warning(f"No course recommendations for user {request.user.id}")

            # Step 5: Return actual updated data
            response_data = {
                'lesson_id': validated_data['lesson_id'],
                'module_id': validated_data['module_id'],
                'progress_percentage': validated_data.get('progress_percentage', 0),
                'completed': is_completed,
                'time_spent_minutes': validated_data.get('time_spent_minutes', 0),
                'updated_at': datetime.utcnow().isoformat()
            }

            return APISuccess.create(
                data=response_data,
                message="Progress updated and saved successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            logger.error(f"❌ Error updating progress: {str(e)}", exc_info=True)
            return APIError.create(
                message=f"Failed to update progress: {str(e)}",
                code="PROGRESS_UPDATE_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class CustomizeLearningPathView(APIView):
    """
    POST /api/learning-paths/<path_id>/customize/
    Apply user customizations to learning path
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, path_id):
        """
        Customize learning path (skip module, adjust pace, swap resource)

        Request body: CustomizationSerializer data
        """
        # Validate request
        serializer = CustomizationSerializer(data=request.data)
        if not serializer.is_valid():
            return APIError.create(
                message="Invalid customization data",
                code="VALIDATION_ERROR",
                field_errors=serializer.errors,
                status_code=StatusCodes.BAD_REQUEST
            )

        validated_data = serializer.validated_data

        try:
            # TODO: Implement customization logic
            # 1. Validate customization type
            # 2. Apply changes to learning path structure
            # 3. Save customized version
            # 4. Mark as customized

            return APISuccess.create(
                data=validated_data,
                message="Learning path customized successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            return APIError.create(
                message=f"Failed to customize learning path: {str(e)}",
                code="CUSTOMIZATION_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class GetProgressAnalyticsView(APIView):
    """
    GET /api/learning-paths/<path_id>/analytics/
    Get analytics for a specific learning path
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, path_id):
        """
        Retrieve analytics for learning path

        Returns: Progress metrics, learning velocity, struggle areas
        """
        try:
            # TODO: Implement analytics calculation
            # 1. Calculate time spent vs estimated
            # 2. Identify struggle areas
            # 3. Calculate learning velocity
            # 4. Generate recommendations

            analytics_data = {
                'path_id': path_id,
                'overall_progress': 0.0,
                'completed_modules': 0,
                'total_modules': 1,
                'completed_lessons': 0,
                'total_lessons': 1,
                'total_time_spent_minutes': 0,
                'estimated_time_remaining_minutes': 0,
                'time_efficiency': {'status': 'on_track', 'percentage': 100.0},
                'learning_velocity': 0.0,
                'estimated_completion_date': None,
                'struggle_areas': [],
                'recommendations': []
            }

            serialized = ProgressAnalyticsSerializer(analytics_data)
            return APISuccess.create(
                data=serialized.data,
                message="Analytics retrieved successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            return APIError.create(
                message=f"Failed to retrieve analytics: {str(e)}",
                code="ANALYTICS_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class MyLearningPathsView(APIView):
    """
    GET /api/learning-paths/my/
    Dashboard view of user's active learning paths
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get dashboard summary of user's active paths

        Returns: Active paths, next lessons, streak, stats
        """
        try:
            # Query MongoDB for user's course recommendations
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=str(request.user.id))
            except CourseRecommendation.DoesNotExist:
                # User has no learning paths yet - return empty dashboard
                logger.info(f"No course recommendations found for user {request.user.id}")
                dashboard_data = {
                    'active_paths': [],
                    'next_lessons': [],
                    'learning_streak_days': 0,
                    'total_hours_learned': 0.0,
                    'modules_completed_this_week': 0,
                    'current_learning_velocity': 0.0
                }
                serialized = DashboardSummarySerializer(dashboard_data)
                return APISuccess.create(
                    data=serialized.data,
                    message="No learning paths found. Create your first path!",
                    status_code=StatusCodes.OK
                )

            # Get user content profile for progress tracking
            try:
                content_profile = UserContentProfile.objects.get(user_id=str(request.user.id))
            except UserContentProfile.DoesNotExist:
                content_profile = None
                logger.info(f"No content profile found for user {request.user.id}")

            # Build active_paths from real MongoDB data
            active_paths = []
            for learning_path in course_recommendation.learning_paths:
                # Enrich with progress data from content profile
                path_dict = self._enrich_with_progress(learning_path, content_profile)
                active_paths.append(path_dict)

            logger.info(f"✅ Fetched {len(active_paths)} learning paths for user {request.user.id}")

            # Build dashboard data with real learning paths
            # TODO: Implement next_lessons, streak, and stats calculations
            dashboard_data = {
                'active_paths': active_paths,
                'next_lessons': [],  # TODO: Implement next lesson recommendations
                'learning_streak_days': 0,  # TODO: Calculate from activity logs
                'total_hours_learned': 0.0,  # TODO: Sum from progress data
                'modules_completed_this_week': 0,  # TODO: Count weekly completions
                'current_learning_velocity': 0.0  # TODO: Calculate learning rate
            }

            serialized = DashboardSummarySerializer(dashboard_data)
            return APISuccess.create(
                data=serialized.data,
                message="Dashboard data retrieved successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            logger.error(f"❌ Error fetching dashboard: {str(e)}", exc_info=True)
            return APIError.create(
                message=f"Failed to retrieve dashboard data: {str(e)}",
                code="DASHBOARD_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )

    def _enrich_with_progress(self, learning_path: LearningPath, content_profile: UserContentProfile) -> Dict[str, Any]:
        """
        Enrich learning path with user progress data.

        Args:
            learning_path: LearningPath document from MongoDB
            content_profile: UserContentProfile with progress data (or None)

        Returns:
            dict: Learning path with progress information
        """
        path_dict = {
            'path_id': learning_path.path_id,
            'title': learning_path.title,
            'description': learning_path.description,
            'estimated_duration_hours': learning_path.estimated_duration_hours,
            'difficulty_level': learning_path.difficulty_level,
            'modules': learning_path.modules,
            'prerequisites': learning_path.prerequisites,
            'created_at': learning_path.started_at or datetime.utcnow(),
            'created_by': learning_path.created_by,
            'started_at': learning_path.started_at,
            'completed_at': learning_path.completed_at,
            'progress_percentage': learning_path.completion_rate * 100 if learning_path.completion_rate else 0.0,
        }

        # Determine status based on timestamps
        if learning_path.completed_at:
            path_dict['status'] = 'completed'
        elif learning_path.started_at:
            path_dict['status'] = 'in_progress'
        else:
            path_dict['status'] = 'not_started'

        return path_dict


class UpdatePathStatusView(APIView):
    """
    Phase 2: Update the status of a specific learning path.
    Supports status transitions: active → in_progress → completed/archived
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, path_id):
        """
        Update learning path status.

        Request body:
        {
            "status": "in_progress" | "completed" | "archived"
        }
        """
        try:
            # Get course recommendation for user
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=request.user.id)
            except CourseRecommendation.DoesNotExist:
                return APIError.create(
                    message="No learning paths found for this user",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Find the specific learning path
            learning_path = None
            path_index = None
            for idx, path in enumerate(course_recommendation.learning_paths):
                if path.path_id == path_id:
                    learning_path = path
                    path_index = idx
                    break

            if not learning_path:
                return APIError.create(
                    message=f"Learning path '{path_id}' not found",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Validate and update status
            new_status = request.data.get('status')
            if new_status not in ['active', 'in_progress', 'completed', 'archived']:
                return APIError.create(
                    message=f"Invalid status: {new_status}. Must be one of: active, in_progress, completed, archived",
                    code="INVALID_STATUS",
                    status_code=StatusCodes.BAD_REQUEST
                )

            # Update status and related timestamps
            old_status = learning_path.status
            learning_path.status = new_status

            # Update timestamps based on status transitions
            if new_status == 'in_progress' and not learning_path.started_at:
                learning_path.started_at = datetime.utcnow()
            elif new_status == 'completed':
                learning_path.completed_at = datetime.utcnow()
                if not learning_path.started_at:
                    learning_path.started_at = datetime.utcnow()
            elif new_status == 'archived':
                learning_path.archived_at = datetime.utcnow()

            # Save back to database
            course_recommendation.learning_paths[path_index] = learning_path
            course_recommendation.save()

            logger.info(f"✅ Updated learning path {path_id} status: {old_status} → {new_status}")

            return APISuccess.create(
                message=f"Learning path status updated from {old_status} to {new_status}",
                data={
                    'path_id': path_id,
                    'status': new_status,
                    'started_at': learning_path.started_at,
                    'completed_at': learning_path.completed_at,
                    'archived_at': learning_path.archived_at
                },
                status_code=StatusCodes.OK
            )

        except Exception as e:
            logger.error(f"❌ Error updating path status: {str(e)}")
            return APIError.create(
                message=f"Failed to update path status: {str(e)}",
                code="INTERNAL_ERROR",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )


class DeletePathView(APIView):
    """
    Phase 2: Delete a specific learning path by path_id.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, path_id):
        """
        Delete a learning path by path_id.
        """
        try:
            # Get course recommendation for user
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=request.user.id)
            except CourseRecommendation.DoesNotExist:
                return APIError.create(
                    message="No learning paths found for this user",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Find and remove the specific learning path
            initial_count = len(course_recommendation.learning_paths)
            course_recommendation.learning_paths = [
                path for path in course_recommendation.learning_paths
                if path.path_id != path_id
            ]
            final_count = len(course_recommendation.learning_paths)

            if initial_count == final_count:
                return APIError.create(
                    message=f"Learning path '{path_id}' not found",
                    code="NOT_FOUND",
                    status_code=StatusCodes.NOT_FOUND
                )

            # Save changes
            course_recommendation.save()

            logger.info(f"✅ Deleted learning path {path_id} for user {request.user.id}")

            return APISuccess.create(
                message=f"Learning path deleted successfully",
                data={
                    'path_id': path_id,
                    'remaining_paths': final_count
                },
                status_code=StatusCodes.OK
            )

        except Exception as e:
            logger.error(f"❌ Error deleting learning path: {str(e)}")
            return APIError.create(
                message=f"Failed to delete learning path: {str(e)}",
                code="INTERNAL_ERROR",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )
