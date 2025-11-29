"""
backend/core/apps/learning_content/models.py
Learning content and course recommendation models
Handles course recommendations, content filtering, and learning paths
RELEVANT FILES: preferences/models.py, analytics/models.py, ml_services/
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Django ORM imports (PostgreSQL)
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# MongoEngine imports (MongoDB)
from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, EmbeddedDocumentListField,
    StringField, IntField, DateTimeField, ListField,
    DictField, FloatField, BooleanField, EmailField,
    ValidationError, DoesNotExist
)


class ContentPreferences(EmbeddedDocument):
    """User's content filtering preferences"""

    # Preferred learning platforms
    PLATFORM_CHOICES = [
        'udemy', 'coursera', 'youtube', 'edx', 'khan_academy',
        'pluralsight', 'linkedin_learning', 'codecademy', 'freecodecamp',
        'skillshare', 'masterclass', 'brilliant', 'datacamp', 'codewars',
        'hackerrank', 'leetcode', 'udacity', 'treehouse', 'laracasts',
        'egghead', 'frontend_masters', 'css_tricks', 'mdn_web_docs',
        'w3schools', 'stackoverflow', 'github', 'medium', 'dev_to'
    ]
    preferred_platforms = ListField(StringField(choices=PLATFORM_CHOICES), default=list)

    # Content type preferences
    CONTENT_TYPES = ['video', 'article', 'interactive', 'quiz', 'project', 'book', 'podcast']
    content_types = ListField(StringField(choices=CONTENT_TYPES), default=list)

    # Difficulty preference
    DIFFICULTY_CHOICES = ['mixed', 'beginner', 'intermediate', 'advanced']
    difficulty_preference = StringField(choices=DIFFICULTY_CHOICES, default='mixed')

    # Duration preference
    DURATION_CHOICES = ['short', 'medium', 'long', 'mixed']
    duration_preference = StringField(choices=DURATION_CHOICES, default='mixed')

    # Content structure preference (videos vs playlists)
    CONTENT_STRUCTURE_CHOICES = ['mixed', 'videos_only', 'playlists_preferred']
    content_structure = StringField(
        choices=CONTENT_STRUCTURE_CHOICES,
        default='mixed',
        help_text="Preferred content structure: mixed (60/40), videos_only, or playlists_preferred"
    )

    # Language preferences
    language_preference = ListField(StringField(max_length=20), default=['english', 'hindi'])

    # Minimum instructor rating
    instructor_ratings_min = FloatField(min_value=0.0, max_value=5.0, default=3.0)


class RecommendationItem(EmbeddedDocument):
    """Individual course recommendation"""

    course_id = StringField(required=True, max_length=200)
    platform = StringField(required=True, max_length=50)
    title = StringField(required=True, max_length=300)

    # Recommendation score (0.0 to 1.0)
    score = FloatField(required=True, min_value=0.0, max_value=1.0)

    # Reasons for recommendation
    reasoning = ListField(StringField(max_length=100), default=list)

    # Course metadata
    metadata = DictField(default=dict)


class CareerRole(EmbeddedDocument):
    """
    Career role achievable from learning path.

    Part of career insights system - shows what jobs users can get
    after completing a learning path.
    """
    role_title = StringField(required=True, max_length=100)
    role_description = StringField(max_length=500)

    # Salary data (in USD, can be converted to other currencies)
    salary_entry_min = IntField()  # e.g., 60000
    salary_entry_max = IntField()  # e.g., 80000
    salary_mid_min = IntField()    # e.g., 80000
    salary_mid_max = IntField()    # e.g., 120000
    salary_senior_min = IntField() # e.g., 120000
    salary_senior_max = IntField() # e.g., 180000

    # Required skills for this role (list of skill dictionaries)
    required_skills = ListField(DictField(), default=list)  # [{"skill": "React", "importance": 95}, ...]

    # Experience level required
    EXPERIENCE_CHOICES = ('entry', 'mid', 'senior')
    experience_level = StringField(choices=EXPERIENCE_CHOICES, default='entry')

    # Job market data (from API or static)
    job_openings_count = IntField(default=0)  # Current openings (updated periodically)

    MARKET_DEMAND_CHOICES = ('low', 'medium', 'high', 'very_high')
    market_demand = StringField(choices=MARKET_DEMAND_CHOICES, default='medium')

    # Career progression
    next_roles = ListField(StringField(max_length=100), default=list)  # e.g., ["Senior React Developer", "Tech Lead"]


class SkillOutcome(EmbeddedDocument):
    """
    Skill gained from a module/lesson.

    Tracks what specific skills users will learn from each module.
    """
    skill_name = StringField(required=True, max_length=100)
    skill_category = StringField(max_length=50)  # e.g., "frontend", "backend", "devops"

    PROFICIENCY_CHOICES = ('beginner', 'intermediate', 'advanced')
    proficiency_level = StringField(choices=PROFICIENCY_CHOICES, default='beginner')

    importance_score = IntField(min_value=0, max_value=100, default=50)  # How critical is this skill


class ProjectMilestone(EmbeddedDocument):
    """
    Hands-on project milestone in learning path.

    Provides practical, hands-on projects at key points in the learning journey.
    """
    milestone_id = StringField(required=True, max_length=100)
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    estimated_hours = IntField(min_value=1, default=5)

    # Skills practiced in this project
    skills_practiced = ListField(StringField(max_length=100), default=list)

    # Module index where this milestone appears (0-indexed)
    appears_after_module = IntField(default=0)

    # Project resources
    starter_code_url = StringField(max_length=500)
    instructions_url = StringField(max_length=500)
    example_solution_url = StringField(max_length=500)


class CareerInsights(EmbeddedDocument):
    """
    Career insights for a learning path.

    Comprehensive career information including roles, salaries, job openings,
    and career progression paths. Combines static data with real-time API data.
    """
    # Roles achievable after completing this path
    career_roles = EmbeddedDocumentListField(CareerRole, default=list)

    # Overall market demand for this path's skills
    market_demand_score = IntField(min_value=0, max_value=100, default=50)

    # Total job openings across all roles (aggregated)
    total_job_openings = IntField(default=0)

    # Career progression path (ordered list of role titles)
    career_progression = ListField(StringField(max_length=100), default=list)

    # Last updated timestamp (for cache invalidation)
    last_updated = DateTimeField(default=datetime.utcnow)


class LearningPath(EmbeddedDocument):
    """Structured learning path with multiple courses and modules"""

    path_id = StringField(max_length=100, required=True)
    title = StringField(max_length=200, required=True)
    description = StringField(max_length=2000)

    # Learning path metadata
    estimated_duration_hours = IntField(min_value=1, default=40)
    difficulty_level = StringField(max_length=20, default='intermediate')
    skill_level_required = StringField(max_length=20, default='beginner')

    # Path structure (new module-based structure)
    modules = ListField(DictField(), default=list)  # Structured module data with lessons
    course_sequence = ListField(DictField(), default=list)  # Legacy: Ordered list of courses
    milestones = ListField(DictField(), default=list)  # Achievement milestones
    prerequisites = ListField(StringField(max_length=100), default=list)

    # Phase 3: Career insights and enhanced learning outcomes
    career_insights = EmbeddedDocumentField(CareerInsights)  # Career opportunities, salaries, job market data
    skills_gained = EmbeddedDocumentListField(SkillOutcome, default=list)  # Aggregated skills from all modules
    project_milestones = EmbeddedDocumentListField(ProjectMilestone, default=list)  # Hands-on projects throughout the path

    # Path progress tracking
    completion_rate = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    progress_percentage = FloatField(min_value=0.0, max_value=100.0, default=0.0)  # Overall progress
    current_course_index = IntField(min_value=0, default=0)
    started_at = DateTimeField()
    completed_at = DateTimeField()
    last_accessed = DateTimeField()  # Track user engagement

    # Path lifecycle status (Phase 2: Multiple paths support)
    STATUS_CHOICES = ('active', 'in_progress', 'completed', 'archived')
    status = StringField(choices=STATUS_CHOICES, default='active', required=True)
    archived_at = DateTimeField()  # Timestamp when path was archived

    # Customization support
    is_customized = BooleanField(default=False)  # Flag for user-customized paths
    customizations = ListField(DictField(), default=list)  # History of user customizations

    # Path metadata
    created_by = StringField(max_length=20, default='ai')  # ai, instructor, community, user
    popularity_score = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    success_rate = FloatField(min_value=0.0, max_value=1.0, default=0.0)

    def calculate_progress(self, user_profile: 'UserContentProfile') -> float:
        """
        Calculate overall progress percentage based on UserContentProfile data.

        Args:
            user_profile: UserContentProfile instance for the user

        Returns:
            Progress percentage (0.0 to 100.0)
        """
        if not self.modules or len(self.modules) == 0:
            return 0.0

        total_lessons = 0
        completed_lessons = 0

        # Count total and completed lessons across all modules
        for module in self.modules:
            module_id = module.get('module_id')
            lessons = module.get('lessons', [])
            total_lessons += len(lessons)

            # Check completion status for each lesson
            for lesson in lessons:
                lesson_id = lesson.get('lesson_id')

                # Check if lesson is in completed_courses or in_progress with 100%
                for completed in user_profile.completed_courses:
                    if completed.get('course_id') == lesson_id:
                        completed_lessons += 1
                        break
                else:
                    # Check in_progress_content for 100% completion
                    for in_progress in user_profile.in_progress_content:
                        if (in_progress.get('content_id') == lesson_id and
                            in_progress.get('progress_percentage', 0.0) >= 100.0):
                            completed_lessons += 1
                            break

        if total_lessons == 0:
            return 0.0

        progress = (completed_lessons / total_lessons) * 100.0
        self.progress_percentage = progress
        return progress

    def get_next_lesson(self, user_profile: 'UserContentProfile') -> Optional[Dict[str, Any]]:
        """
        Get the next uncompleted lesson for the user to work on.

        Args:
            user_profile: UserContentProfile instance for the user

        Returns:
            Dictionary with next lesson details or None if all completed
        """
        if not self.modules:
            return None

        # Iterate through modules in order
        for module in sorted(self.modules, key=lambda m: m.get('order', 0)):
            module_id = module.get('module_id')
            lessons = module.get('lessons', [])

            # Check each lesson in the module
            for lesson in lessons:
                lesson_id = lesson.get('lesson_id')

                # Check if lesson is completed
                is_completed = False
                for completed in user_profile.completed_courses:
                    if completed.get('course_id') == lesson_id:
                        is_completed = True
                        break

                if not is_completed:
                    # Check if in progress with 100%
                    for in_progress in user_profile.in_progress_content:
                        if (in_progress.get('content_id') == lesson_id and
                            in_progress.get('progress_percentage', 0.0) >= 100.0):
                            is_completed = True
                            break

                # Return first uncompleted lesson
                if not is_completed:
                    return {
                        'module_id': module_id,
                        'module_title': module.get('title'),
                        'lesson_id': lesson_id,
                        'lesson_title': lesson.get('title'),
                        'lesson_type': lesson.get('type'),
                        'lesson_url': lesson.get('url'),
                        'duration_minutes': lesson.get('duration_minutes'),
                        'platform': lesson.get('platform')
                    }

        # All lessons completed
        return None

    def apply_customization(self, customization_type: str, target_id: str,
                          customization_data: Dict[str, Any]) -> bool:
        """
        Apply user customization to the learning path structure.

        Supports:
        - skip_module: Skip an entire module
        - adjust_pace: Adjust time estimates for a module
        - swap_resource: Replace a lesson with alternative content

        Args:
            customization_type: Type of customization (skip_module, adjust_pace, swap_resource)
            target_id: Module ID or Lesson ID being customized
            customization_data: Additional data specific to customization type

        Returns:
            True if customization was applied, False otherwise
        """
        customization_record = {
            'type': customization_type,
            'target_id': target_id,
            'data': customization_data,
            'applied_at': datetime.utcnow()
        }

        if customization_type == 'skip_module':
            # Mark module as skipped by removing it from active modules
            for i, module in enumerate(self.modules):
                if module.get('module_id') == target_id:
                    # Add skip flag to module instead of removing (for audit trail)
                    self.modules[i]['skipped'] = True
                    self.customizations.append(customization_record)
                    self.is_customized = True
                    return True
            return False

        elif customization_type == 'adjust_pace':
            # Adjust estimated hours based on pace multiplier
            pace_multiplier = customization_data.get('pace_multiplier', 1.0)
            for i, module in enumerate(self.modules):
                if module.get('module_id') == target_id:
                    original_hours = self.modules[i].get('estimated_hours', 10)
                    self.modules[i]['estimated_hours'] = int(original_hours * pace_multiplier)
                    self.customizations.append(customization_record)
                    self.is_customized = True
                    return True
            return False

        elif customization_type == 'swap_resource':
            # Replace lesson URL and platform with new resource
            new_url = customization_data.get('new_url')
            new_platform = customization_data.get('new_platform')

            if not new_url or not new_platform:
                return False

            # Find lesson across all modules
            for i, module in enumerate(self.modules):
                lessons = module.get('lessons', [])
                for j, lesson in enumerate(lessons):
                    if lesson.get('lesson_id') == target_id:
                        # Update lesson with new resource
                        self.modules[i]['lessons'][j]['url'] = new_url
                        self.modules[i]['lessons'][j]['platform'] = new_platform
                        self.modules[i]['lessons'][j]['customized'] = True
                        self.customizations.append(customization_record)
                        self.is_customized = True
                        return True
            return False

        # Unknown customization type
        return False


class CourseRecommendation(Document):
    """
    Cached personalized course recommendations for users.
    Generated by AI and cached for performance.
    """

    # Link to Django User
    user_id = IntField(required=True)

    # Generation timestamps
    generated_at = DateTimeField(required=True, default=datetime.utcnow)
    expires_at = DateTimeField(required=True)

    # Recommendation list
    recommendations = EmbeddedDocumentListField(RecommendationItem, default=list)

    # Learning paths
    learning_paths = EmbeddedDocumentListField(LearningPath, default=list)

    # Algorithm version for tracking
    algorithm_version = StringField(default='1.0.0')

    # Generation context
    generation_context = DictField(default=dict)

    # User feedback on recommendations
    user_feedback = DictField(default=dict)
    feedback_count = IntField(min_value=0, default=0)

    meta = {
        'collection': 'course_recommendations',
        'indexes': [
            'user_id',
            'expires_at',
            'generated_at',
            'algorithm_version'
        ]
    }

    @property
    def is_expired(self) -> bool:
        """Check if recommendations are expired"""
        return datetime.utcnow() > self.expires_at

    def get_top_recommendations(self, limit: int = 10) -> List[RecommendationItem]:
        """Get top N recommendations by score"""
        return sorted(self.recommendations, key=lambda x: x.score, reverse=True)[:limit]

    def get_recommendations_by_platform(self, platform: str, limit: int = 5) -> List[RecommendationItem]:
        """Get recommendations filtered by platform"""
        platform_recs = [r for r in self.recommendations if r.platform == platform]
        return sorted(platform_recs, key=lambda x: x.score, reverse=True)[:limit]

    def add_user_feedback(self, course_id: str, feedback_type: str, rating: float = None):
        """Add user feedback for a specific recommendation"""
        feedback_key = f"{course_id}_{feedback_type}"
        self.user_feedback[feedback_key] = {
            'type': feedback_type,
            'rating': rating,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.feedback_count += 1
        self.save()

    def get_learning_path_by_topic(self, topic: str) -> Optional[LearningPath]:
        """Get learning path for a specific topic"""
        for path in self.learning_paths:
            if topic.lower() in path.title.lower() or topic.lower() in path.description.lower():
                return path
        return None

    @classmethod
    def get_valid_recommendations(cls, user_id: int) -> Optional['CourseRecommendation']:
        """Get non-expired recommendations for user"""
        try:
            return cls.objects.get(
                user_id=user_id,
                expires_at__gt=datetime.utcnow()
            )
        except DoesNotExist:
            return None

    @classmethod
    def create_for_user(cls, user_id: int, recommendations: List[Dict[str, Any]],
                       learning_paths: List[Dict[str, Any]] = None,
                       expires_in_hours: int = 24) -> 'CourseRecommendation':
        """Create new recommendation set for user"""
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

        # Convert recommendations to RecommendationItem objects
        rec_items = []
        for rec in recommendations:
            rec_item = RecommendationItem(
                course_id=rec['course_id'],
                platform=rec['platform'],
                title=rec['title'],
                score=rec['score'],
                reasoning=rec.get('reasoning', []),
                metadata=rec.get('metadata', {})
            )
            rec_items.append(rec_item)

        # Convert learning paths to LearningPath objects
        path_items = []
        if learning_paths:
            for path in learning_paths:
                path_item = LearningPath(
                    path_id=path['path_id'],
                    title=path['title'],
                    description=path.get('description', ''),
                    estimated_duration_hours=path.get('estimated_duration_hours', 40),
                    difficulty_level=path.get('difficulty_level', 'intermediate'),
                    course_sequence=path.get('course_sequence', []),
                    milestones=path.get('milestones', []),
                    prerequisites=path.get('prerequisites', [])
                )
                path_items.append(path_item)

        recommendation = cls(
            user_id=user_id,
            expires_at=expires_at,
            recommendations=rec_items,
            learning_paths=path_items
        )
        recommendation.save()
        return recommendation

    def __str__(self):
        return f"CourseRecommendation(user={self.user_id}, count={len(self.recommendations)})"


class UserContentProfile(Document):
    """
    User's content preferences and learning content history.
    Links to Django User model.
    """

    # Link to Django User model
    user_id = IntField(required=True, unique=True)

    # Timestamps
    created_at = DateTimeField(required=True, default=datetime.utcnow)
    updated_at = DateTimeField(required=True, default=datetime.utcnow)

    # Content preferences
    content_preferences = EmbeddedDocumentField(ContentPreferences)

    # Learning goals and interests
    learning_goals = ListField(StringField(max_length=100), default=list)
    current_skills = ListField(StringField(max_length=100), default=list)
    target_skills = ListField(StringField(max_length=100), default=list)

    # Learning style preferences
    LEARNING_STYLES = ['visual', 'auditory', 'kinesthetic', 'reading_writing']
    preferred_learning_styles = ListField(StringField(choices=LEARNING_STYLES), default=list)

    # Content consumption patterns
    average_session_duration = IntField(min_value=5, default=60)  # minutes
    preferred_content_length = StringField(max_length=20, default='medium')
    best_learning_times = ListField(StringField(max_length=20), default=list)

    # Progress tracking
    completed_courses = ListField(DictField(), default=list)
    bookmarked_content = ListField(DictField(), default=list)
    in_progress_content = ListField(DictField(), default=list)

    # Personalization metadata
    last_recommendation_generation = DateTimeField()
    recommendation_effectiveness_score = FloatField(min_value=0.0, max_value=1.0, default=0.5)
    content_discovery_preferences = DictField(default=dict)

    meta = {
        'collection': 'user_content_profiles',
        'indexes': [
            'user_id',
            '-updated_at',
            'learning_goals',
            'content_preferences.preferred_platforms',
            'content_preferences.content_types',
            'last_recommendation_generation'
        ]
    }

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def add_completed_course(self, course_data: Dict[str, Any]):
        """Add a completed course to user's history"""
        completion_record = {
            'course_id': course_data['course_id'],
            'platform': course_data['platform'],
            'title': course_data['title'],
            'completed_at': datetime.utcnow(),
            'completion_rate': course_data.get('completion_rate', 1.0),
            'rating': course_data.get('rating'),
            'duration_hours': course_data.get('duration_hours'),
            'skills_gained': course_data.get('skills_gained', [])
        }

        self.completed_courses.append(completion_record)

        # Update current skills based on completed course
        new_skills = course_data.get('skills_gained', [])
        for skill in new_skills:
            if skill not in self.current_skills:
                self.current_skills.append(skill)

        self.save()

    def add_bookmark(self, content_data: Dict[str, Any]):
        """Bookmark content for later"""
        bookmark = {
            'content_id': content_data['content_id'],
            'platform': content_data['platform'],
            'title': content_data['title'],
            'url': content_data.get('url'),
            'bookmarked_at': datetime.utcnow(),
            'tags': content_data.get('tags', []),
            'notes': content_data.get('notes', '')
        }

        # Remove existing bookmark for same content
        self.bookmarked_content = [
            b for b in self.bookmarked_content
            if b['content_id'] != content_data['content_id']
        ]

        self.bookmarked_content.append(bookmark)
        self.save()

    def start_content(self, content_data: Dict[str, Any]):
        """Mark content as in progress"""
        progress_record = {
            'content_id': content_data['content_id'],
            'platform': content_data['platform'],
            'title': content_data['title'],
            'started_at': datetime.utcnow(),
            'last_accessed': datetime.utcnow(),
            'progress_percentage': content_data.get('progress_percentage', 0.0),
            'estimated_completion_time': content_data.get('estimated_completion_time')
        }

        # Remove existing progress record for same content
        self.in_progress_content = [
            p for p in self.in_progress_content
            if p['content_id'] != content_data['content_id']
        ]

        self.in_progress_content.append(progress_record)
        self.save()

    def update_content_progress(self, content_id: str, progress_percentage: float):
        """Update progress for content in progress"""
        for progress in self.in_progress_content:
            if progress['content_id'] == content_id:
                progress['progress_percentage'] = progress_percentage
                progress['last_accessed'] = datetime.utcnow()

                # Move to completed if 100%
                if progress_percentage >= 100.0:
                    self.add_completed_course({
                        'course_id': content_id,
                        'platform': progress['platform'],
                        'title': progress['title'],
                        'completion_rate': 1.0
                    })
                    # Remove from in progress
                    self.in_progress_content = [
                        p for p in self.in_progress_content
                        if p['content_id'] != content_id
                    ]
                break

        self.save()

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get user's learning statistics"""
        return {
            'completed_courses_count': len(self.completed_courses),
            'in_progress_count': len(self.in_progress_content),
            'bookmarked_count': len(self.bookmarked_content),
            'current_skills_count': len(self.current_skills),
            'target_skills_count': len(self.target_skills),
            'learning_goals_count': len(self.learning_goals),
            'average_session_duration': self.average_session_duration,
            'last_activity': max([
                p.get('last_accessed', datetime.min)
                for p in self.in_progress_content
            ] + [datetime.min]),
            'skills_gained_this_month': self._get_recent_skills_gained(30),
            'courses_completed_this_month': self._get_recent_completions(30)
        }

    def _get_recent_skills_gained(self, days: int) -> List[str]:
        """Get skills gained in recent days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_skills = []

        for course in self.completed_courses:
            if course.get('completed_at', datetime.min) > cutoff_date:
                recent_skills.extend(course.get('skills_gained', []))

        return list(set(recent_skills))

    def _get_recent_completions(self, days: int) -> int:
        """Get number of courses completed in recent days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        count = 0

        for course in self.completed_courses:
            if course.get('completed_at', datetime.min) > cutoff_date:
                count += 1

        return count

    def get_content_preferences_summary(self) -> Dict[str, Any]:
        """Get summary of content preferences"""
        if not self.content_preferences:
            return {}

        return {
            'preferred_platforms': self.content_preferences.preferred_platforms,
            'content_types': self.content_preferences.content_types,
            'difficulty_preference': self.content_preferences.difficulty_preference,
            'duration_preference': self.content_preferences.duration_preference,
            'language_preference': self.content_preferences.language_preference,
            'min_instructor_rating': self.content_preferences.instructor_ratings_min,
            'learning_styles': self.preferred_learning_styles,
            'average_session_duration': self.average_session_duration
        }

    @classmethod
    def get_by_user_id(cls, user_id: int) -> Optional['UserContentProfile']:
        """Get user content profile by Django user ID"""
        try:
            return cls.objects.get(user_id=user_id)
        except DoesNotExist:
            return None

    @classmethod
    def create_for_user(cls, user_id: int, initial_preferences: Dict[str, Any] = None) -> 'UserContentProfile':
        """Create new user content profile"""
        profile = cls(user_id=user_id)

        if initial_preferences:
            profile.content_preferences = ContentPreferences(**initial_preferences)

        profile.save()
        return profile

    def __str__(self):
        return f"UserContentProfile(user_id={self.user_id}, goals={len(self.learning_goals)})"


# ============================================================================
# PostgreSQL Django ORM Models - Quiz System
# ============================================================================
# These models use Django ORM (PostgreSQL) for ACID compliance and relational integrity
# Quiz data requires transactions, foreign keys, and strong consistency guarantees


class LessonQuiz(models.Model):
    """
    Quiz linked to a specific lesson in a learning path.

    Generated on-the-fly when user completes a lesson and wants to unlock the next one.
    Questions are generated from scraped lesson content or metadata.
    Cached for 30 days to avoid regenerating the same quiz.
    """

    # Link to learning path and lesson (stored as strings from MongoDB)
    path_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Learning path ID from MongoDB CourseRecommendation"
    )
    lesson_id = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Lesson ID within the learning path"
    )

    # Quiz configuration
    passing_score_percentage = models.IntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum score required to pass (default: 70%)"
    )
    num_questions = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Number of questions in this quiz"
    )

    # Content scraping metadata
    content_scraped = models.BooleanField(
        default=False,
        help_text="Whether actual lesson content was scraped for question generation"
    )
    content_source = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Source of scraped content (youtube_transcript, article, github, metadata)"
    )
    scraped_content_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Hash of scraped content to detect changes"
    )

    # Cache management
    created_at = models.DateTimeField(auto_now_add=True)
    cache_until = models.DateTimeField(
        help_text="When to regenerate this quiz (30 days from creation)"
    )

    # Metadata
    lesson_title = models.CharField(max_length=300, blank=True)
    lesson_platform = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'learning_content_lesson_quiz'
        verbose_name = 'Lesson Quiz'
        verbose_name_plural = 'Lesson Quizzes'
        indexes = [
            models.Index(fields=['path_id', 'lesson_id']),
            models.Index(fields=['cache_until']),
        ]
        # Ensure one quiz per lesson (can regenerate after expiry)
        constraints = [
            models.UniqueConstraint(
                fields=['path_id', 'lesson_id'],
                name='unique_quiz_per_lesson'
            )
        ]

    def save(self, *args, **kwargs):
        """Set cache_until to 30 days from now if not set"""
        if not self.cache_until:
            self.cache_until = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if quiz cache has expired"""
        return timezone.now() > self.cache_until

    def __str__(self):
        return f"Quiz for {self.lesson_title or self.lesson_id} ({self.num_questions} questions)"


class QuizQuestion(models.Model):
    """
    Individual question in a lesson quiz.

    Supports multiple question types: multiple choice, true/false, short answer, code.
    Generated by QuestionGeneratorService using AI.
    """

    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('code', 'Code Question'),
        ('fill_blank', 'Fill in the Blank'),
        ('matching', 'Matching'),
        ('ordering', 'Ordering'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    quiz = models.ForeignKey(
        LessonQuiz,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text="Quiz this question belongs to"
    )

    # Question order within quiz
    order = models.IntegerField(
        default=0,
        help_text="Display order (0-indexed)"
    )

    # Question content
    question_text = models.TextField(
        help_text="The question text"
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='multiple_choice'
    )

    # Answer options (JSON for flexibility)
    # For MC: {"options": ["A", "B", "C", "D"], "correct_index": 0}
    # For T/F: {"correct": true}
    # For short: {"keywords": ["key1", "key2"], "exact_match": false}
    # For code: {"test_cases": [...], "language": "python"}
    options = models.JSONField(
        default=dict,
        help_text="Question options and correct answer (structure varies by type)"
    )

    # Correct answer (for grading)
    correct_answer = models.TextField(
        help_text="Correct answer or grading criteria"
    )

    # Educational metadata
    explanation = models.TextField(
        blank=True,
        help_text="Explanation shown after answering (right or wrong)"
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )

    # Bloom's taxonomy level for question complexity
    blooms_level = models.CharField(
        max_length=20,
        blank=True,
        help_text="remember, understand, apply, analyze, evaluate, create"
    )

    # Points assigned to this question (for weighted scoring)
    points = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Points for this question (default: 1)"
    )

    class Meta:
        db_table = 'learning_content_quiz_question'
        verbose_name = 'Quiz Question'
        verbose_name_plural = 'Quiz Questions'
        ordering = ['order']
        indexes = [
            models.Index(fields=['quiz', 'order']),
        ]

    def __str__(self):
        return f"Q{self.order + 1}: {self.question_text[:50]}..."


class QuizAttempt(models.Model):
    """
    User's attempt at a quiz.

    Tracks each time a user takes a quiz, supports unlimited retakes.
    Best score is tracked across all attempts.
    """

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    quiz = models.ForeignKey(
        LessonQuiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        help_text="Quiz being attempted"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        help_text="User taking the quiz"
    )

    # Attempt metadata
    attempt_number = models.IntegerField(
        default=1,
        help_text="Which attempt is this (1, 2, 3...)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_taken_seconds = models.IntegerField(
        blank=True,
        null=True,
        help_text="Total time taken to complete (seconds)"
    )

    # Scoring
    score_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Score as percentage (0-100)"
    )
    total_points_earned = models.IntegerField(default=0)
    total_points_possible = models.IntegerField(default=0)
    passed = models.BooleanField(
        default=False,
        help_text="Whether user passed (score >= passing_score_percentage)"
    )

    # Best attempt tracking (denormalized for performance)
    is_best_attempt = models.BooleanField(
        default=False,
        help_text="Is this the user's best scoring attempt?"
    )

    class Meta:
        db_table = 'learning_content_quiz_attempt'
        verbose_name = 'Quiz Attempt'
        verbose_name_plural = 'Quiz Attempts'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'quiz']),
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['quiz', 'user', '-attempt_number']),
        ]

    def save(self, *args, **kwargs):
        """Auto-calculate time taken and passed status"""
        # Calculate time taken if completed
        if self.status == 'completed' and self.completed_at and not self.time_taken_seconds:
            self.time_taken_seconds = int((self.completed_at - self.started_at).total_seconds())

        # Determine if passed
        if self.status == 'completed':
            self.passed = self.score_percentage >= self.quiz.passing_score_percentage

        super().save(*args, **kwargs)

        # Update is_best_attempt flag for this user/quiz combination
        if self.status == 'completed':
            self._update_best_attempt()

    def _update_best_attempt(self):
        """Mark this as best attempt if it has the highest score"""
        # Get all completed attempts for this user/quiz
        all_attempts = QuizAttempt.objects.filter(
            user=self.user,
            quiz=self.quiz,
            status='completed'
        ).order_by('-score_percentage')

        # Clear all is_best_attempt flags
        all_attempts.update(is_best_attempt=False)

        # Set the highest scoring attempt as best
        if all_attempts.exists():
            best = all_attempts.first()
            best.is_best_attempt = True
            QuizAttempt.objects.filter(pk=best.pk).update(is_best_attempt=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.lesson_title} - Attempt {self.attempt_number} ({self.score_percentage:.1f}%)"


class QuestionResponse(models.Model):
    """
    User's response to a single question within a quiz attempt.

    Stores the answer, whether it was correct, and points earned.
    """

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Quiz attempt this response belongs to"
    )
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Question being answered"
    )

    # User's answer (format varies by question type)
    user_answer = models.TextField(
        blank=True,
        help_text="User's answer (text, index, JSON for complex answers)"
    )

    # Grading results
    is_correct = models.BooleanField(
        default=False,
        help_text="Whether the answer was correct"
    )
    points_earned = models.IntegerField(
        default=0,
        help_text="Points earned for this answer"
    )

    # Timing
    answered_at = models.DateTimeField(auto_now_add=True)
    time_taken_seconds = models.IntegerField(
        blank=True,
        null=True,
        help_text="Time taken to answer this question"
    )

    # AI grading feedback (for short answer/code questions)
    ai_feedback = models.TextField(
        blank=True,
        help_text="AI-generated feedback on the answer"
    )

    class Meta:
        db_table = 'learning_content_question_response'
        verbose_name = 'Question Response'
        verbose_name_plural = 'Question Responses'
        ordering = ['question__order']
        indexes = [
            models.Index(fields=['attempt', 'question']),
        ]
        # Each question can only be answered once per attempt
        constraints = [
            models.UniqueConstraint(
                fields=['attempt', 'question'],
                name='unique_response_per_attempt_question'
            )
        ]

    def __str__(self):
        return f"{self.attempt.user.username} - Q{self.question.order + 1} - {'✓' if self.is_correct else '✗'}"
