"""
backend/core/apps/learning_content/models.py
Learning content and course recommendation models
Handles course recommendations, content filtering, and learning paths
RELEVANT FILES: preferences/models.py, analytics/models.py, ml_services/
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
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

    # Path progress tracking
    completion_rate = FloatField(min_value=0.0, max_value=1.0, default=0.0)
    progress_percentage = FloatField(min_value=0.0, max_value=100.0, default=0.0)  # Overall progress
    current_course_index = IntField(min_value=0, default=0)
    started_at = DateTimeField()
    completed_at = DateTimeField()
    last_accessed = DateTimeField()  # Track user engagement

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
