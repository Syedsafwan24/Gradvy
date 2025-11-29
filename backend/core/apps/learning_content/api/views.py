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
    ML_SERVICES_AVAILABLE = True
except ImportError:
    ML_SERVICES_AVAILABLE = False
    print("Warning: ML services not available. Learning path generation will be disabled.")

# Initialize logger
logger = logging.getLogger(__name__)


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
        return defaults.get(platform.lower(), defaults['default'])

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
            'youtube': 'video',
            'udemy': 'video',  # Udemy is primarily video-based
            'coursera': 'video',
            'edx': 'video',
            'pluralsight': 'video',
            'linkedin': 'video',
            'medium': 'article',
            'dev_to': 'article',
            'freecodecamp': 'interactive',
            'codecademy': 'interactive',
            'leetcode': 'interactive',
            'preview': 'video'  # Preview/mock data defaults to video
        }

        # Get platform's default type
        default_type = platform_types.get(platform.lower(), 'article')

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
        elif 'reading' in learning_styles:
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
    def calculate_dynamic_module_count(
        user_preferences: Dict,
        roadmap,  # Full roadmap object for intelligent analysis
        request_override: Optional[int] = None
    ) -> int:
        """
        ML-driven dynamic module count calculation.

        Uses intelligent analysis of:
        1. Roadmap structure complexity (topic count, dependencies, skills, content depth)
        2. User learning capacity (time, experience, pace, timeline, goals)
        3. Configurable bounds from Django settings
        4. Optional user override

        This replaces the old hardcoded lookup tables (6/10/12) with a truly adaptive algorithm
        that considers roadmap complexity and user profile to generate varied, intelligent module counts.

        Returns:
            int: Optimal module count (typically 4-20, varies based on analysis)
        """
        import random

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

        # Step 6: Add small intelligent variance (±0-2) to avoid always same result for same inputs
        # Variance is proportional to capacity (higher capacity = more variance)
        max_variance = 2 if capacity_score > 1.0 else 1
        variance = random.randint(-max_variance, max_variance)
        final_count_with_variance = max(MIN_MODULES, min(final_count + variance, max_from_roadmap, MAX_MODULES))

        # Intelligent logging for transparency
        logger.info(f"""
        🧠 ML-Driven Module Count Calculation:
           Roadmap Analysis:
           • Total Topics: {total_topics}
           • Complexity Score: {complexity_score:.2f} (0=simple, 1=complex)

           User Profile:
           • Capacity Score: {capacity_score:.2f} (higher = can handle more)

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
        request_override: Optional[int] = None
    ) -> int:
        """
        Calculate dynamic lessons per module based on:
        1. Preferred pace (slow → 3, medium → 5, fast → 7)
        2. Module position (early modules +1 for foundation, late modules -1 for advanced)

        Range: 3-8 lessons per module

        Examples:
        - Slow pace, module 1/10 → 4 lessons (3 + 1 for early module)
        - Medium pace, module 5/10 → 5 lessons (middle module)
        - Fast pace, module 10/10 → 6 lessons (7 - 1 for late module)
        """
        # Get configurable bounds from Django settings
        MIN_LESSONS = settings.LEARNING_PATH_MIN_LESSONS
        MAX_LESSONS = settings.LEARNING_PATH_MAX_LESSONS

        # User override has highest priority
        if request_override and MIN_LESSONS <= request_override <= MAX_LESSONS:
            return request_override

        basic_info = user_preferences.get('basic_info', {})
        pace = basic_info.get('preferred_pace', 'medium')

        # Pace base: slow → 3 lessons, medium → 5, fast → 7
        pace_mapping = {'slow': 3, 'medium': 5, 'fast': 7}
        base_lessons = pace_mapping.get(pace, 5)

        # Module position adjustment
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

        # Bounds: Use configurable settings (default 2-10 lessons)
        return max(MIN_LESSONS, min(lessons, MAX_LESSONS))

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

            # Fetch roadmap for user's primary learning goal
            roadmap = roadmap_service.get_roadmap_for_preferences(user_preferences_dict)

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

            # Convert roadmap nodes to modules with real course resources
            modules_data = []
            total_duration = 0

            # Calculate dynamic module count using ML-driven intelligent analysis
            # Analyzes roadmap structure + user profile for truly adaptive module count
            dynamic_module_count = self.calculate_dynamic_module_count(
                user_preferences=user_preferences_dict,
                roadmap=filtered_roadmap,  # Pass full roadmap for intelligent analysis
                request_override=max_modules_override
            )

            # Iterate through dynamically calculated number of modules
            for idx, node in enumerate(filtered_roadmap.nodes[:dynamic_module_count], 1):
                # Calculate dynamic lesson count for this module based on pace and position
                dynamic_lesson_count = self.calculate_lessons_per_module(
                    user_preferences=user_preferences_dict,
                    module_index=idx - 1,  # 0-indexed for calculation
                    total_modules=dynamic_module_count,
                    request_override=max_lessons_override
                )

                # Enrich search query with user preferences (difficulty, learning style, duration, goal context)
                # This fixes generic queries like "Introduction" → "Introduction to Mobile Development beginner tutorial"
                enriched_query = course_search_service.enrich_search_query(
                    base_topic=node.title,
                    user_preferences=user_preferences_dict,
                    learning_goal=generation_request.learning_goals[0] if generation_request.learning_goals else None,
                    node_context={'difficulty': node.difficulty, 'category': node.category}
                )

                # Search for courses using enriched query and dynamic lesson count
                scored_courses = course_search_service.search_courses(
                    topic=enriched_query,  # Use enriched query instead of bare node.title
                    user_preferences=user_preferences_dict,
                    max_results=dynamic_lesson_count  # Use dynamic count instead of hardcoded 5
                )

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

                    lessons.append({
                        'lesson_id': f"{node.id}-lesson-{len(lessons) + 1}",
                        'title': course.title,
                        'description': course.description,
                        'type': lesson_type,  # Now respects user's content preferences!
                        'duration_minutes': int(course.duration_hours * 60),
                        'url': course.url,
                        'thumbnail': course.thumbnail_url or self._get_default_thumbnail(course.platform),
                        'platform': course.platform,
                        'instructor': course.instructor,
                        'rating': course.rating,
                        'difficulty': course.difficulty,
                        'price': course.price,
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
                modules_data.append(module)

            # Create learning path metadata
            # VALIDATION: Ensure minimum duration to pass MongoEngine validation (min_value=1)
            validated_duration = max(10, round(total_duration, 1)) if total_duration < 1 else round(total_duration, 1)

            if total_duration < 1:
                logger.warning(f"⚠️ Learning path has invalid duration {total_duration}, setting to 10 hours to prevent validation error")

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
                modules=modules_data,  # New module-based structure
                course_sequence=[],  # Legacy field
                prerequisites=learning_path_data.get('prerequisites', []),
                created_by='ai',
            )

            # Save to MongoDB with preference hash for smart cache invalidation
            try:
                course_recommendation = CourseRecommendation.objects.get(user_id=request.user.id)
                created = False
                # Clear old paths and update expiry
                course_recommendation.learning_paths = []
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
        """Add detailed progress data at module and lesson levels"""
        # TODO: Implement detailed progress calculation
        # For now, return basic structure
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
            'started_at': learning_path.started_at,
            'completed_at': learning_path.completed_at,
            'progress_percentage': learning_path.completion_rate * 100 if learning_path.completion_rate else 0.0,
            'status': 'completed' if learning_path.completed_at else ('in_progress' if learning_path.started_at else 'not_started'),
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
            # TODO: Implement full progress update logic
            # 1. Update UserContentProfile.in_progress_content
            # 2. Calculate completion percentages
            # 3. Move to completed_courses if 100%
            # 4. Update analytics
            # 5. Log interaction event

            return APISuccess.create(
                data=validated_data,
                message="Progress updated successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            return APIError.create(
                message=f"Failed to update progress: {str(e)}",
                code="UPDATE_FAILED",
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
            # TODO: Implement dashboard summary
            # 1. Get active paths (in_progress)
            # 2. Calculate next recommended lesson for each
            # 3. Get streak data
            # 4. Calculate stats

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
                message="Dashboard data retrieved successfully",
                status_code=StatusCodes.OK
            )

        except Exception as e:
            return APIError.create(
                message=f"Failed to retrieve dashboard data: {str(e)}",
                code="DASHBOARD_FAILED",
                status_code=StatusCodes.INTERNAL_SERVER_ERROR
            )
