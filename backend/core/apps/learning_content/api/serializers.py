# File: backend/core/apps/learning_content/api/serializers.py
# Description: Serializers for learning path generation, progress tracking, and customization
# Why: Provides request/response DTOs for the learning path API endpoints
# Relevant Files: views.py, models.py, ml_services/services/learning_path_service.py

from rest_framework import serializers
from datetime import datetime


class ResourceSerializer(serializers.Serializer):
    """
    Serializer for additional learning resources
    Used for supplementary materials like exercises, articles, documentation
    """
    resource_id = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(
        choices=['exercise', 'article', 'documentation', 'video', 'quiz', 'project']
    )
    title = serializers.CharField(max_length=200)
    url = serializers.URLField()
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)


class LessonSerializer(serializers.Serializer):
    """
    Serializer for individual lessons within a module
    Each lesson represents a single learning activity (video, article, etc.)
    """
    lesson_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)
    type = serializers.ChoiceField(
        choices=['video', 'article', 'exercise', 'quiz', 'project', 'interactive']
    )
    duration_minutes = serializers.IntegerField(min_value=1)
    platform = serializers.CharField(max_length=100)  # youtube, udemy, coursera, etc.
    url = serializers.URLField()
    thumbnail = serializers.URLField(required=False, allow_blank=True)  # Course/video thumbnail
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    resources = ResourceSerializer(many=True, required=False)

    # Progress fields (added when enriching with user progress data)
    completed = serializers.BooleanField(required=False, default=False)
    progress_percentage = serializers.FloatField(required=False, default=0.0, min_value=0.0, max_value=100.0)
    time_spent_minutes = serializers.IntegerField(required=False, default=0, min_value=0)


class ModuleSerializer(serializers.Serializer):
    """
    Serializer for learning path modules
    Each module groups related lessons around a topic
    """
    module_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)
    order = serializers.IntegerField(min_value=1)
    lessons = LessonSerializer(many=True)
    estimated_hours = serializers.IntegerField(min_value=1)
    prerequisites = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )

    # Progress fields (added when enriching with user progress data)
    completed_lessons = serializers.IntegerField(required=False, default=0, min_value=0)
    total_lessons = serializers.IntegerField(required=False, min_value=1)
    progress_percentage = serializers.FloatField(required=False, default=0.0, min_value=0.0, max_value=100.0)


class LearningPathSerializer(serializers.Serializer):
    """
    Main serializer for learning paths
    Represents a complete personalized learning journey
    """
    path_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=2000)
    estimated_duration_hours = serializers.IntegerField(min_value=1)
    difficulty_level = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced']
    )
    modules = ModuleSerializer(many=True)
    prerequisites = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )
    created_at = serializers.DateTimeField(required=False)
    created_by = serializers.ChoiceField(
        choices=['ai', 'instructor', 'community', 'user'],
        default='ai'
    )

    # Status and progress fields
    status = serializers.ChoiceField(
        choices=['not_started', 'in_progress', 'completed'],
        required=False,
        default='not_started'
    )
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    completed_at = serializers.DateTimeField(required=False, allow_null=True)
    progress_percentage = serializers.FloatField(required=False, default=0.0, min_value=0.0, max_value=100.0)
    last_accessed = serializers.DateTimeField(required=False, allow_null=True)

    # Customization fields
    is_customized = serializers.BooleanField(required=False, default=False)
    customizations = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )

    # Phase 3: Career insights and enhanced learning outcomes
    career_insights = serializers.DictField(required=False, allow_null=True)
    skills_gained = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    project_milestones = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )


class LearningPathGenerationRequestSerializer(serializers.Serializer):
    """
    Serializer for learning path generation requests
    Used when user wants to generate a new personalized learning path
    """
    learning_goals = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1,
        help_text="List of learning goals (e.g., ['web_dev', 'ai_ml'])"
    )
    experience_level = serializers.ChoiceField(
        choices=['complete_beginner', 'some_basics', 'intermediate', 'advanced'],
        required=False,
        help_text="User's current skill level"
    )
    preferred_pace = serializers.ChoiceField(
        choices=['slow', 'medium', 'fast'],
        required=False,
        help_text="Preferred learning speed"
    )
    time_availability = serializers.ChoiceField(
        choices=['1-2hrs', '3-5hrs', '5+hrs'],
        required=False,
        help_text="Weekly time commitment"
    )
    learning_styles = serializers.ListField(
        child=serializers.ChoiceField(
            choices=['visual', 'hands_on', 'reading', 'videos', 'interactive']
        ),
        required=False,
        help_text="Preferred content formats"
    )
    target_timeline = serializers.ChoiceField(
        choices=['3months', '6months', '1year', 'flexible'],
        required=False,
        help_text="Goal achievement deadline"
    )
    preferred_platforms = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="Override default platform preferences"
    )
    force_regenerate = serializers.BooleanField(
        default=False,
        help_text="Ignore cache and generate new path"
    )

    # Optional overrides for dynamic calculation
    max_modules = serializers.IntegerField(
        required=False,
        min_value=6,
        max_value=15,
        help_text="Override calculated module count (6-15). If not provided, calculated based on time_availability, target_timeline, and roadmap complexity"
    )
    max_lessons_per_module = serializers.IntegerField(
        required=False,
        min_value=3,
        max_value=8,
        help_text="Override calculated lessons per module (3-8). If not provided, calculated based on preferred_pace and module position"
    )

    def validate_learning_goals(self, value):
        """Ensure at least one learning goal is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one learning goal is required")
        return value


class ProgressUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating progress on lessons
    Used to track user completion and time spent
    """
    path_id = serializers.CharField(max_length=100)
    module_id = serializers.CharField(max_length=100)
    lesson_id = serializers.CharField(max_length=100)
    progress_percentage = serializers.FloatField(min_value=0.0, max_value=100.0)
    completed = serializers.BooleanField(default=False)
    time_spent_minutes = serializers.IntegerField(min_value=0)

    def validate(self, data):
        """Ensure completed=True only when progress=100%"""
        if data.get('completed') and data.get('progress_percentage') < 100.0:
            raise serializers.ValidationError(
                "Cannot mark as completed when progress is less than 100%"
            )
        return data


class CustomizationSerializer(serializers.Serializer):
    """
    Serializer for learning path customizations
    Allows users to skip modules, adjust pace, or swap resources
    """
    path_id = serializers.CharField(max_length=100)
    customization_type = serializers.ChoiceField(
        choices=['skip_module', 'adjust_pace', 'swap_resource']
    )
    target_id = serializers.CharField(
        max_length=100,
        help_text="Module ID or Lesson ID being customized"
    )
    customization_data = serializers.DictField(
        help_text="Flexible data specific to customization type"
    )

    def validate_customization_data(self, value):
        """Validate customization_data based on type"""
        customization_type = self.initial_data.get('customization_type')

        if customization_type == 'skip_module':
            # For skip_module, no additional data needed
            pass
        elif customization_type == 'adjust_pace':
            # For adjust_pace, require pace_multiplier
            if 'pace_multiplier' not in value:
                raise serializers.ValidationError(
                    "adjust_pace requires 'pace_multiplier' in customization_data"
                )
            pace_multiplier = value['pace_multiplier']
            if not isinstance(pace_multiplier, (int, float)) or pace_multiplier <= 0:
                raise serializers.ValidationError(
                    "pace_multiplier must be a positive number"
                )
        elif customization_type == 'swap_resource':
            # For swap_resource, require new_url and new_platform
            required_fields = ['new_url', 'new_platform']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(
                        f"swap_resource requires '{field}' in customization_data"
                    )

        return value


class ProgressAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for learning path analytics response
    Provides insights on progress, velocity, and struggle areas
    """
    path_id = serializers.CharField(max_length=100)
    overall_progress = serializers.FloatField(min_value=0.0, max_value=100.0)
    completed_modules = serializers.IntegerField(min_value=0)
    total_modules = serializers.IntegerField(min_value=1)
    completed_lessons = serializers.IntegerField(min_value=0)
    total_lessons = serializers.IntegerField(min_value=1)

    # Time tracking
    total_time_spent_minutes = serializers.IntegerField(min_value=0)
    estimated_time_remaining_minutes = serializers.IntegerField(min_value=0)
    time_efficiency = serializers.DictField()  # {status: on_track/ahead/behind, percentage: float}

    # Learning velocity
    learning_velocity = serializers.FloatField(help_text="Lessons completed per week")
    estimated_completion_date = serializers.DateField(allow_null=True)

    # Struggle areas
    struggle_areas = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lessons/modules with low progress or excessive time"
    )

    # Recommendations
    recommendations = serializers.ListField(
        child=serializers.CharField(max_length=500),
        help_text="AI-generated recommendations based on progress"
    )


class DashboardSummarySerializer(serializers.Serializer):
    """
    Serializer for dashboard view of active learning paths
    Provides quick overview of user's learning journey
    """
    active_paths = LearningPathSerializer(many=True)
    next_lessons = serializers.ListField(
        child=serializers.DictField(),
        help_text="Next recommended lesson for each active path"
    )
    learning_streak_days = serializers.IntegerField(min_value=0)
    total_hours_learned = serializers.FloatField(min_value=0.0)
    modules_completed_this_week = serializers.IntegerField(min_value=0)
    current_learning_velocity = serializers.FloatField(help_text="Lessons/week across all paths")


# ============================================================================
# Quiz System Serializers
# ============================================================================
# Serializers for lesson quizzes, attempts, questions, and responses


class QuizQuestionSerializer(serializers.Serializer):
    """
    Serializer for individual quiz questions
    Used when displaying questions to users (without correct answer)
    """
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(min_value=0)
    question_text = serializers.CharField()
    question_type = serializers.ChoiceField(
        choices=['multiple_choice', 'true_false', 'short_answer', 'code', 'fill_blank', 'matching', 'ordering']
    )
    difficulty = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard'],
        required=False
    )
    points = serializers.IntegerField(min_value=1, default=1)

    # Options vary by question type (MC has list, T/F has bool, etc.)
    # For MC: {"options": ["A", "B", "C", "D"]}
    # For T/F: {"options": ["True", "False"]}
    # For others: may be empty or contain hints
    options = serializers.JSONField()

    # Note: correct_answer and explanation are excluded for security
    # These are only included in grading responses


class QuizQuestionDetailSerializer(QuizQuestionSerializer):
    """
    Serializer for quiz questions with answers (used for grading/review)
    Includes correct answer and explanation after submission
    """
    correct_answer = serializers.CharField()
    explanation = serializers.CharField(allow_blank=True)
    blooms_level = serializers.CharField(allow_blank=True, required=False)


class QuizSerializer(serializers.Serializer):
    """
    Serializer for quiz metadata and questions
    Used when fetching quiz for a lesson
    """
    id = serializers.IntegerField(read_only=True)
    path_id = serializers.CharField(max_length=100)
    lesson_id = serializers.CharField(max_length=200)
    lesson_title = serializers.CharField(max_length=300, required=False)
    lesson_platform = serializers.CharField(max_length=50, required=False)

    passing_score_percentage = serializers.IntegerField(min_value=0, max_value=100)
    num_questions = serializers.IntegerField(min_value=1)

    content_scraped = serializers.BooleanField()
    content_source = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)

    created_at = serializers.DateTimeField(read_only=True)
    cache_until = serializers.DateTimeField(read_only=True)

    # Questions (use QuizQuestionSerializer to hide answers)
    questions = QuizQuestionSerializer(many=True, read_only=True)


class QuestionResponseSerializer(serializers.Serializer):
    """
    Serializer for user's response to a single question
    Used when grading individual answers
    """
    id = serializers.IntegerField(read_only=True)
    question_id = serializers.IntegerField()
    user_answer = serializers.CharField(allow_blank=True)
    is_correct = serializers.BooleanField(read_only=True)
    points_earned = serializers.IntegerField(read_only=True)
    answered_at = serializers.DateTimeField(read_only=True)
    time_taken_seconds = serializers.IntegerField(required=False, allow_null=True)
    ai_feedback = serializers.CharField(allow_blank=True, read_only=True)


class QuizAttemptSerializer(serializers.Serializer):
    """
    Serializer for quiz attempt metadata and results
    Used for displaying attempt history and current attempt status
    """
    id = serializers.IntegerField(read_only=True)
    quiz_id = serializers.IntegerField()
    attempt_number = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(
        choices=['in_progress', 'completed', 'abandoned'],
        default='in_progress'
    )

    started_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    time_taken_seconds = serializers.IntegerField(read_only=True, allow_null=True)

    score_percentage = serializers.FloatField(min_value=0.0, max_value=100.0, read_only=True)
    total_points_earned = serializers.IntegerField(read_only=True)
    total_points_possible = serializers.IntegerField(read_only=True)
    passed = serializers.BooleanField(read_only=True)
    is_best_attempt = serializers.BooleanField(read_only=True)

    # Include responses when returning attempt results
    responses = QuestionResponseSerializer(many=True, read_only=True)


class StartQuizRequestSerializer(serializers.Serializer):
    """
    Serializer for starting a new quiz attempt
    Request body: path_id and lesson_id
    """
    path_id = serializers.CharField(max_length=100)
    lesson_id = serializers.CharField(max_length=200)

    def validate(self, data):
        """Ensure both path_id and lesson_id are provided"""
        if not data.get('path_id') or not data.get('lesson_id'):
            raise serializers.ValidationError("Both path_id and lesson_id are required")
        return data


class SubmitQuizAnswerSerializer(serializers.Serializer):
    """
    Serializer for submitting a single question answer
    Used during quiz attempt
    """
    question_id = serializers.IntegerField()
    user_answer = serializers.CharField(allow_blank=True)
    time_taken_seconds = serializers.IntegerField(required=False, allow_null=True, min_value=0)


class SubmitQuizRequestSerializer(serializers.Serializer):
    """
    Serializer for submitting complete quiz with all answers
    Request body: attempt_id and list of answers
    """
    attempt_id = serializers.IntegerField()
    answers = SubmitQuizAnswerSerializer(many=True)

    def validate_answers(self, value):
        """Ensure at least one answer is provided"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one answer is required")

        # Check for duplicate question IDs
        question_ids = [answer['question_id'] for answer in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError("Duplicate question IDs found in answers")

        return value


class QuizResultSerializer(serializers.Serializer):
    """
    Serializer for quiz results after submission
    Includes graded attempt, detailed feedback, and next steps
    """
    attempt = QuizAttemptSerializer()
    passed = serializers.BooleanField()
    score_percentage = serializers.FloatField(min_value=0.0, max_value=100.0)
    passing_score_percentage = serializers.IntegerField(min_value=0, max_value=100)

    # Question-by-question breakdown
    questions_breakdown = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of questions with user answer, correct answer, and explanation"
    )

    # Performance insights
    total_questions = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    incorrect_answers = serializers.IntegerField()
    time_taken_seconds = serializers.IntegerField()

    # Next steps
    can_retake = serializers.BooleanField()
    next_lesson_unlocked = serializers.BooleanField()
    best_score_percentage = serializers.FloatField(min_value=0.0, max_value=100.0)


class QuizStatsSerializer(serializers.Serializer):
    """
    Serializer for quiz statistics for a specific lesson
    Shows user's attempt history and best score
    """
    quiz_id = serializers.IntegerField()
    lesson_id = serializers.CharField(max_length=200)
    lesson_title = serializers.CharField(max_length=300)

    total_attempts = serializers.IntegerField(min_value=0)
    best_score_percentage = serializers.FloatField(min_value=0.0, max_value=100.0, allow_null=True)
    passed = serializers.BooleanField()
    passing_score_percentage = serializers.IntegerField(min_value=0, max_value=100)

    # Recent attempts
    attempts = QuizAttemptSerializer(many=True)


class LessonLockStateSerializer(serializers.Serializer):
    """
    Serializer for lesson lock state information
    Used to indicate if a lesson is locked and why
    """
    is_locked = serializers.BooleanField()
    lock_reason = serializers.CharField(
        allow_blank=True,
        help_text="Reason for lock (e.g., 'Complete previous lesson' or 'Pass previous quiz')"
    )

    # If locked, info about what needs to be completed
    requires_lesson_id = serializers.CharField(max_length=200, required=False, allow_null=True)
    requires_lesson_title = serializers.CharField(max_length=300, required=False, allow_null=True)
    requires_quiz_pass = serializers.BooleanField(required=False)

    # Quiz info for this lesson
    quiz_required = serializers.BooleanField()
    quiz_completed = serializers.BooleanField(required=False)
    quiz_passed = serializers.BooleanField(required=False)
    quiz_best_score = serializers.FloatField(min_value=0.0, max_value=100.0, required=False, allow_null=True)
