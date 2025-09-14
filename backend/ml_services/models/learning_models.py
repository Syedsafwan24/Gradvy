"""
backend/ml_services/models/learning_models.py
MongoDB models for AI-generated learning paths and progress tracking
Integrates with existing UserPreference system for personalized learning experiences
RELEVANT FILES: core/apps/preferences/models.py, services/learning_path_service.py, services/question_generator_service.py, services/code_evaluation_service.py
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import uuid

from mongoengine import (
    Document, EmbeddedDocument, StringField, IntField, FloatField,
    BooleanField, DateTimeField, ListField, DictField, ReferenceField,
    EmbeddedDocumentField, UUIDField, EnumField, CASCADE, DENY
)

# Import UserPreference for integration
try:
    from core.apps.preferences.models import UserPreference
except ImportError:
    # Fallback for development/testing environments
    class UserPreference(Document):
        pass


class LearningStatus(Enum):
    """Status of learning items"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class DifficultyLevel(Enum):
    """Difficulty levels for learning content"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ContentType(Enum):
    """Types of learning content"""
    VIDEO = "video"
    ARTICLE = "article"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    PROJECT = "project"
    EXERCISE = "exercise"
    ASSESSMENT = "assessment"
    PLAYGROUND = "playground"


class QuestionType(Enum):
    """Types of assessment questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    CODING_CHALLENGE = "coding_challenge"
    ESSAY = "essay"
    FILL_IN_BLANK = "fill_in_blank"


class AssessmentResult(Enum):
    """Assessment completion results"""
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING = "pending"


# =============================================================================
# EMBEDDED DOCUMENTS (Sub-documents)
# =============================================================================

class LearningResource(EmbeddedDocument):
    """External learning resource reference"""
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=500)
    url = StringField(max_length=500)
    resource_type = EnumField(ContentType, required=True)
    platform = StringField(max_length=100)  # e.g., "youtube", "udemy", "coursera"
    duration_minutes = IntField(min_value=0)
    difficulty_level = EnumField(DifficultyLevel, default=DifficultyLevel.BEGINNER)
    is_free = BooleanField(default=True)
    language = StringField(max_length=10, default="en")
    tags = ListField(StringField(max_length=50), default=list)
    rating = FloatField(min_value=0, max_value=5)
    created_at = DateTimeField(default=datetime.utcnow)


class LearningObjective(EmbeddedDocument):
    """Specific learning objective or outcome"""
    objective_id = UUIDField(default=uuid.uuid4, unique=True)
    description = StringField(required=True, max_length=300)
    bloom_taxonomy_level = StringField(
        max_length=50,
        choices=[
            "remember", "understand", "apply", "analyze", "evaluate", "create"
        ]
    )
    skills_covered = ListField(StringField(max_length=100), default=list)
    is_completed = BooleanField(default=False)
    completion_criteria = StringField(max_length=200)
    weight = FloatField(min_value=0, max_value=1, default=1.0)  # Relative importance


class AssessmentQuestion(EmbeddedDocument):
    """Individual assessment question"""
    question_id = UUIDField(default=uuid.uuid4, unique=True)
    question_type = EnumField(QuestionType, required=True)
    question_text = StringField(required=True, max_length=1000)

    # Multiple choice / True-False options
    options = ListField(StringField(max_length=200), default=list)
    correct_answer = StringField(max_length=200)  # For objective questions

    # Coding challenge specifics
    programming_language = StringField(max_length=50)
    starter_code = StringField(max_length=5000)
    solution_code = StringField(max_length=5000)
    test_cases = ListField(DictField(), default=list)

    # Scoring and feedback
    points = IntField(min_value=0, default=1)
    explanation = StringField(max_length=1000)
    hints = ListField(StringField(max_length=200), default=list)

    # Metadata
    difficulty_level = EnumField(DifficultyLevel, default=DifficultyLevel.BEGINNER)
    estimated_time_minutes = IntField(min_value=1, default=5)
    tags = ListField(StringField(max_length=50), default=list)
    learning_objectives = ListField(StringField(max_length=100), default=list)


class StudentAnswer(EmbeddedDocument):
    """Student's answer to an assessment question"""
    question_id = UUIDField(required=True)
    answer = StringField(max_length=5000)  # Student's answer
    submitted_code = StringField(max_length=10000)  # For coding questions
    is_correct = BooleanField()
    score = FloatField(min_value=0)  # Points earned
    attempt_number = IntField(min_value=1, default=1)
    time_taken_seconds = IntField(min_value=0)
    ai_feedback = StringField(max_length=1000)  # AI-generated feedback
    submitted_at = DateTimeField(default=datetime.utcnow)


class LearningActivity(EmbeddedDocument):
    """Individual learning activity within a lesson"""
    activity_id = UUIDField(default=uuid.uuid4, unique=True)
    title = StringField(required=True, max_length=200)
    activity_type = EnumField(ContentType, required=True)
    description = StringField(max_length=500)

    # Content and resources
    content = StringField(max_length=10000)  # Main content/instructions
    resources = ListField(EmbeddedDocumentField(LearningResource), default=list)

    # Interactive elements
    is_interactive = BooleanField(default=False)
    playground_config = DictField()  # Configuration for code playground

    # Timing and requirements
    estimated_time_minutes = IntField(min_value=1, default=30)
    is_required = BooleanField(default=True)
    prerequisites = ListField(UUIDField(), default=list)  # Activity IDs

    # Learning objectives and assessment
    learning_objectives = ListField(EmbeddedDocumentField(LearningObjective), default=list)
    assessment_questions = ListField(EmbeddedDocumentField(AssessmentQuestion), default=list)

    # AI-generated content flags
    ai_generated = BooleanField(default=False)
    generation_model = StringField(max_length=100)
    generation_timestamp = DateTimeField()


class Lesson(EmbeddedDocument):
    """Individual lesson within a learning module"""
    lesson_id = UUIDField(default=uuid.uuid4, unique=True)
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    lesson_number = IntField(min_value=1, required=True)

    # Content organization
    activities = ListField(EmbeddedDocumentField(LearningActivity), default=list)

    # Timing and requirements
    estimated_time_minutes = IntField(min_value=1, default=60)
    difficulty_level = EnumField(DifficultyLevel, default=DifficultyLevel.BEGINNER)
    prerequisites = ListField(UUIDField(), default=list)  # Lesson IDs

    # Learning outcomes
    learning_objectives = ListField(EmbeddedDocumentField(LearningObjective), default=list)
    skills_taught = ListField(StringField(max_length=100), default=list)

    # Assessment
    has_assessment = BooleanField(default=False)
    assessment_questions = ListField(EmbeddedDocumentField(AssessmentQuestion), default=list)
    passing_score_percentage = IntField(min_value=0, max_value=100, default=70)

    # AI generation metadata
    ai_generated = BooleanField(default=False)
    generation_model = StringField(max_length=100)
    generated_at = DateTimeField()


class ProjectSpecification(EmbeddedDocument):
    """Specifications for a hands-on project"""
    project_id = UUIDField(default=uuid.uuid4, unique=True)
    title = StringField(required=True, max_length=200)
    description = StringField(required=True, max_length=2000)

    # Project details
    difficulty_level = EnumField(DifficultyLevel, required=True)
    estimated_hours = IntField(min_value=1, required=True)
    programming_languages = ListField(StringField(max_length=50), default=list)

    # Requirements and deliverables
    requirements = ListField(StringField(max_length=300), default=list)
    deliverables = ListField(StringField(max_length=200), default=list)

    # Resources and support
    starter_files = DictField()  # filename: content mapping
    resources = ListField(EmbeddedDocumentField(LearningResource), default=list)

    # Assessment criteria
    grading_criteria = ListField(DictField(), default=list)  # {criterion, weight, description}
    peer_review_enabled = BooleanField(default=False)

    # AI assistance
    ai_mentor_enabled = BooleanField(default=True)
    ai_feedback_prompts = ListField(StringField(max_length=300), default=list)


# =============================================================================
# MAIN DOCUMENTS (Top-level collections)
# =============================================================================

class LearningPath(Document):
    """
    AI-generated personalized learning path

    This represents a complete learning curriculum generated by the ML services
    based on user preferences and goals.
    """

    # Identification
    path_id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    version = StringField(max_length=20, default="1.0")

    # User association
    user = ReferenceField(UserPreference, required=True, reverse_delete_rule=CASCADE)

    # Path characteristics
    difficulty_level = EnumField(DifficultyLevel, required=True)
    estimated_total_hours = IntField(min_value=1, required=True)
    target_timeline_weeks = IntField(min_value=1)

    # Learning goals and outcomes
    primary_goals = ListField(StringField(max_length=100), required=True)
    secondary_goals = ListField(StringField(max_length=100), default=list)
    target_skills = ListField(StringField(max_length=100), default=list)
    career_relevance = StringField(max_length=200)

    # Path structure
    total_modules = IntField(min_value=1, required=True)
    total_lessons = IntField(min_value=1, default=0)
    total_activities = IntField(min_value=1, default=0)

    # Learning methodology
    learning_approaches = ListField(StringField(max_length=50), default=list)  # "hands_on", "theory", "visual"
    includes_projects = BooleanField(default=True)
    includes_assessments = BooleanField(default=True)
    adaptive_difficulty = BooleanField(default=True)

    # AI generation metadata
    ai_generated = BooleanField(default=True)
    generation_model = StringField(max_length=100, required=True)
    generation_parameters = DictField()  # Parameters used for generation
    generated_at = DateTimeField(default=datetime.utcnow, required=True)

    # Status and updates
    status = EnumField(LearningStatus, default=LearningStatus.NOT_STARTED)
    is_active = BooleanField(default=True)
    is_published = BooleanField(default=False)
    last_updated = DateTimeField(default=datetime.utcnow)

    # Personalization data
    personalization_factors = DictField()  # Factors that influenced generation
    user_feedback_incorporated = BooleanField(default=False)
    adaptation_count = IntField(default=0)  # Number of times path was adapted

    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    tags = ListField(StringField(max_length=50), default=list)
    language = StringField(max_length=10, default="en")

    meta = {
        'collection': 'learning_paths',
        'indexes': [
            'user',
            'status',
            'difficulty_level',
            'primary_goals',
            'generated_at',
            'is_active'
        ],
        'ordering': ['-created_at']
    }

    def __str__(self):
        return f"LearningPath: {self.title} (User: {self.user.id if self.user else 'Unknown'})"


class LearningModule(Document):
    """
    Individual module within a learning path

    Represents a cohesive unit of learning covering specific topics or skills.
    """

    # Identification
    module_id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    title = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    module_number = IntField(min_value=1, required=True)

    # Path association
    learning_path = ReferenceField(LearningPath, required=True, reverse_delete_rule=CASCADE)

    # Module content
    lessons = ListField(EmbeddedDocumentField(Lesson), default=list)

    # Module characteristics
    difficulty_level = EnumField(DifficultyLevel, required=True)
    estimated_hours = IntField(min_value=1, required=True)
    prerequisites = ListField(StringField(max_length=100), default=list)

    # Learning outcomes
    learning_objectives = ListField(EmbeddedDocumentField(LearningObjective), default=list)
    skills_covered = ListField(StringField(max_length=100), default=list)
    key_concepts = ListField(StringField(max_length=100), default=list)

    # Projects and assessments
    projects = ListField(EmbeddedDocumentField(ProjectSpecification), default=list)
    has_final_assessment = BooleanField(default=True)
    final_assessment_questions = ListField(EmbeddedDocumentField(AssessmentQuestion), default=list)
    passing_score_percentage = IntField(min_value=0, max_value=100, default=70)

    # AI generation metadata
    ai_generated = BooleanField(default=True)
    generation_model = StringField(max_length=100)
    generation_prompt = StringField(max_length=2000)  # Prompt used for generation
    generated_at = DateTimeField(default=datetime.utcnow)

    # Module status
    status = EnumField(LearningStatus, default=LearningStatus.NOT_STARTED)
    is_published = BooleanField(default=False)

    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    last_updated = DateTimeField(default=datetime.utcnow)
    tags = ListField(StringField(max_length=50), default=list)

    meta = {
        'collection': 'learning_modules',
        'indexes': [
            'learning_path',
            'module_number',
            'status',
            'difficulty_level',
            'generated_at'
        ],
        'ordering': ['module_number']
    }

    def __str__(self):
        return f"Module {self.module_number}: {self.title}"


class LearningProgress(Document):
    """
    Tracks individual user progress through learning paths and modules

    This document tracks detailed progress, performance, and analytics
    for personalized learning experiences.
    """

    # Identification
    progress_id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)

    # Associations
    user = ReferenceField(UserPreference, required=True, reverse_delete_rule=CASCADE)
    learning_path = ReferenceField(LearningPath, required=True, reverse_delete_rule=CASCADE)
    current_module = ReferenceField(LearningModule, reverse_delete_rule=DENY)

    # Overall progress
    overall_progress_percentage = FloatField(min_value=0, max_value=100, default=0)
    modules_completed = IntField(min_value=0, default=0)
    lessons_completed = IntField(min_value=0, default=0)
    activities_completed = IntField(min_value=0, default=0)

    # Module-specific progress
    module_progress = DictField()  # module_id: progress_data mapping
    lesson_progress = DictField()  # lesson_id: progress_data mapping
    activity_progress = DictField()  # activity_id: progress_data mapping

    # Time tracking
    total_time_spent_minutes = IntField(min_value=0, default=0)
    session_count = IntField(min_value=0, default=0)
    average_session_time_minutes = FloatField(min_value=0, default=0)
    last_activity_at = DateTimeField(default=datetime.utcnow)

    # Performance metrics
    overall_score_percentage = FloatField(min_value=0, max_value=100, default=0)
    assessments_completed = IntField(min_value=0, default=0)
    assessments_passed = IntField(min_value=0, default=0)
    projects_completed = IntField(min_value=0, default=0)

    # Skill development tracking
    skills_mastered = ListField(StringField(max_length=100), default=list)
    skills_in_progress = ListField(StringField(max_length=100), default=list)
    competency_scores = DictField()  # skill: score mapping (0-100)

    # Learning behavior analytics
    preferred_learning_times = ListField(IntField(), default=list)  # Hours of day (0-23)
    learning_streak_days = IntField(min_value=0, default=0)
    longest_streak_days = IntField(min_value=0, default=0)
    consistency_score = FloatField(min_value=0, max_value=100, default=0)

    # Adaptive learning data
    difficulty_adjustments = ListField(DictField(), default=list)  # History of adjustments
    personalized_recommendations = ListField(DictField(), default=list)
    learning_velocity = FloatField(default=1.0)  # Relative learning speed

    # Engagement metrics
    completion_rate = FloatField(min_value=0, max_value=100, default=0)
    engagement_score = FloatField(min_value=0, max_value=100, default=0)
    satisfaction_ratings = ListField(IntField(min_value=1, max_value=5), default=list)

    # Status and milestones
    status = EnumField(LearningStatus, default=LearningStatus.NOT_STARTED)
    milestones_achieved = ListField(DictField(), default=list)
    certificates_earned = ListField(StringField(max_length=100), default=list)

    # AI interaction history
    ai_interactions = ListField(DictField(), default=list)  # AI assistance requests
    ai_feedback_received = IntField(min_value=0, default=0)
    ai_suggestions_followed = IntField(min_value=0, default=0)

    # Metadata
    started_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    last_updated = DateTimeField(default=datetime.utcnow)

    # Data for ML model improvements
    feedback_data = DictField()  # Data for improving AI recommendations

    meta = {
        'collection': 'learning_progress',
        'indexes': [
            'user',
            'learning_path',
            'status',
            'overall_progress_percentage',
            'last_activity_at',
            ('user', 'learning_path')  # Compound index for user's paths
        ],
        'ordering': ['-last_activity_at']
    }

    def __str__(self):
        return f"Progress: {self.user.id if self.user else 'Unknown'} - {self.learning_path.title if self.learning_path else 'Unknown'} ({self.overall_progress_percentage:.1f}%)"


class AssessmentSession(Document):
    """
    Individual assessment attempt and results

    Tracks detailed information about assessment attempts for analytics
    and adaptive learning improvements.
    """

    # Identification
    session_id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)

    # Associations
    user = ReferenceField(UserPreference, required=True, reverse_delete_rule=CASCADE)
    learning_path = ReferenceField(LearningPath, reverse_delete_rule=CASCADE)
    module = ReferenceField(LearningModule, reverse_delete_rule=CASCADE)

    # Assessment details
    assessment_type = StringField(
        max_length=50,
        choices=["lesson", "module", "project", "final", "diagnostic", "practice"],
        required=True
    )
    assessment_title = StringField(max_length=200, required=True)

    # Session metadata
    started_at = DateTimeField(default=datetime.utcnow, required=True)
    completed_at = DateTimeField()
    time_taken_minutes = IntField(min_value=0)
    attempt_number = IntField(min_value=1, default=1)

    # Questions and answers
    questions = ListField(EmbeddedDocumentField(AssessmentQuestion), default=list)
    answers = ListField(EmbeddedDocumentField(StudentAnswer), default=list)

    # Results
    total_questions = IntField(min_value=0, default=0)
    correct_answers = IntField(min_value=0, default=0)
    score_percentage = FloatField(min_value=0, max_value=100, default=0)
    points_earned = FloatField(min_value=0, default=0)
    max_points = FloatField(min_value=0, default=0)

    # Performance analysis
    result = EnumField(AssessmentResult, default=AssessmentResult.PENDING)
    passing_score_required = IntField(min_value=0, max_value=100, default=70)
    difficulty_level = EnumField(DifficultyLevel, required=True)

    # Question-type performance breakdown
    performance_by_type = DictField()  # question_type: {correct, total, percentage}
    performance_by_skill = DictField()  # skill: {correct, total, percentage}

    # AI-powered insights
    ai_feedback = StringField(max_length=2000)
    strengths_identified = ListField(StringField(max_length=100), default=list)
    areas_for_improvement = ListField(StringField(max_length=100), default=list)
    personalized_recommendations = ListField(StringField(max_length=200), default=list)

    # Learning analytics
    time_per_question_seconds = ListField(IntField(min_value=0), default=list)
    question_difficulty_matched = BooleanField()  # Whether difficulty matched user level
    confidence_scores = ListField(IntField(min_value=1, max_value=5), default=list)  # User's confidence per question

    # Adaptive learning triggers
    triggered_difficulty_adjustment = BooleanField(default=False)
    suggested_review_topics = ListField(StringField(max_length=100), default=list)
    next_recommended_activities = ListField(DictField(), default=list)

    # Session context
    device_type = StringField(max_length=50)  # mobile, tablet, desktop
    location_context = StringField(max_length=100)  # home, school, work, etc.
    session_interruptions = IntField(min_value=0, default=0)

    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'assessment_sessions',
        'indexes': [
            'user',
            'learning_path',
            'module',
            'assessment_type',
            'result',
            'started_at',
            ('user', 'assessment_type'),  # User's performance by assessment type
            ('user', 'learning_path')     # User's assessments for a path
        ],
        'ordering': ['-started_at']
    }

    def __str__(self):
        return f"Assessment: {self.assessment_title} - {self.user.id if self.user else 'Unknown'} ({self.score_percentage:.1f}%)"


class CodeSubmission(Document):
    """
    Code submissions from playground and coding challenges

    Stores code submissions for evaluation, feedback, and progress tracking.
    """

    # Identification
    submission_id = UUIDField(default=uuid.uuid4, unique=True, primary_key=True)

    # Associations
    user = ReferenceField(UserPreference, required=True, reverse_delete_rule=CASCADE)
    learning_path = ReferenceField(LearningPath, reverse_delete_rule=CASCADE)
    module = ReferenceField(LearningModule, reverse_delete_rule=CASCADE)
    assessment_session = ReferenceField(AssessmentSession, reverse_delete_rule=CASCADE)

    # Code details
    programming_language = StringField(max_length=50, required=True)
    code = StringField(max_length=50000, required=True)  # The submitted code
    problem_description = StringField(max_length=2000)

    # Submission context
    submission_type = StringField(
        max_length=50,
        choices=["exercise", "project", "assessment", "practice", "exploration"],
        required=True
    )
    attempt_number = IntField(min_value=1, default=1)

    # Evaluation results
    overall_score = FloatField(min_value=0, max_value=100, default=0)
    correctness_score = FloatField(min_value=0, max_value=100, default=0)
    style_score = FloatField(min_value=0, max_value=100, default=0)
    efficiency_score = FloatField(min_value=0, max_value=100, default=0)

    # Test results
    test_cases_passed = IntField(min_value=0, default=0)
    total_test_cases = IntField(min_value=0, default=0)
    test_results = ListField(DictField(), default=list)

    # Code analysis
    syntax_errors = ListField(DictField(), default=list)
    runtime_errors = ListField(DictField(), default=list)
    style_issues = ListField(DictField(), default=list)
    security_issues = ListField(DictField(), default=list)

    # AI feedback
    ai_feedback = StringField(max_length=3000)
    ai_suggestions = ListField(StringField(max_length=300), default=list)
    improved_code_suggestion = StringField(max_length=50000)

    # Performance metrics
    execution_time_ms = IntField(min_value=0)
    memory_usage_kb = IntField(min_value=0)
    code_complexity_score = FloatField(min_value=0, max_value=10)
    lines_of_code = IntField(min_value=0)

    # Learning progress impact
    skills_demonstrated = ListField(StringField(max_length=100), default=list)
    concepts_applied = ListField(StringField(max_length=100), default=list)
    learning_objectives_met = ListField(StringField(max_length=100), default=list)

    # Timestamps
    submitted_at = DateTimeField(default=datetime.utcnow, required=True)
    evaluated_at = DateTimeField()

    # Metadata
    evaluation_model = StringField(max_length=100)  # AI model used for evaluation
    evaluation_version = StringField(max_length=50)

    meta = {
        'collection': 'code_submissions',
        'indexes': [
            'user',
            'learning_path',
            'programming_language',
            'submission_type',
            'submitted_at',
            ('user', 'programming_language'),  # User's submissions by language
            ('user', 'learning_path'),        # User's submissions for a path
            ('overall_score', '-submitted_at') # High scores, recent first
        ],
        'ordering': ['-submitted_at']
    }

    def __str__(self):
        return f"Code Submission: {self.programming_language} - {self.user.id if self.user else 'Unknown'} ({self.overall_score:.1f}%)"


# =============================================================================
# UTILITY FUNCTIONS AND MANAGERS
# =============================================================================

class LearningPathManager:
    """Manager class for learning path operations"""

    @staticmethod
    def create_learning_path_from_ai_response(user: UserPreference, ai_response: Dict[str, Any]) -> LearningPath:
        """Create a LearningPath document from AI service response"""
        try:
            path_data = ai_response.get('learning_path', {})
            modules_data = ai_response.get('modules', [])

            # Create the learning path
            learning_path = LearningPath(
                title=path_data.get('title', 'Personalized Learning Path'),
                description=path_data.get('description', ''),
                user=user,
                difficulty_level=DifficultyLevel(path_data.get('experience_level', 'beginner')),
                estimated_total_hours=path_data.get('estimated_total_hours', 60),
                target_timeline_weeks=path_data.get('target_timeline_weeks', 12),
                primary_goals=path_data.get('primary_goals', []),
                secondary_goals=path_data.get('secondary_goals', []),
                target_skills=path_data.get('target_skills', []),
                total_modules=len(modules_data),
                learning_approaches=path_data.get('learning_approaches', []),
                generation_model=ai_response.get('model_used', 'unknown'),
                generation_parameters=ai_response.get('generation_parameters', {}),
                personalization_factors=ai_response.get('personalization_factors', {}),
                tags=path_data.get('tags', [])
            )

            learning_path.save()

            # Create associated modules
            for i, module_data in enumerate(modules_data, 1):
                learning_module = LearningModuleManager.create_module_from_ai_data(
                    learning_path, module_data, i
                )
                learning_module.save()

            # Create initial progress tracking
            progress = LearningProgress(
                user=user,
                learning_path=learning_path,
                status=LearningStatus.NOT_STARTED
            )
            progress.save()

            return learning_path

        except Exception as e:
            raise ValueError(f"Failed to create learning path from AI response: {str(e)}")

    @staticmethod
    def get_user_active_paths(user: UserPreference) -> List[LearningPath]:
        """Get all active learning paths for a user"""
        return LearningPath.objects(
            user=user,
            is_active=True,
            status__in=[LearningStatus.NOT_STARTED, LearningStatus.IN_PROGRESS, LearningStatus.PAUSED]
        ).order_by('-created_at')

    @staticmethod
    def get_recommended_next_activity(user: UserPreference, learning_path: LearningPath) -> Optional[Dict[str, Any]]:
        """Get the next recommended activity for a user in a learning path"""
        try:
            progress = LearningProgress.objects(user=user, learning_path=learning_path).first()
            if not progress:
                return None

            # Simple logic - return first incomplete activity
            # In practice, this would be more sophisticated
            modules = LearningModule.objects(learning_path=learning_path).order_by('module_number')

            for module in modules:
                module_progress = progress.module_progress.get(str(module.module_id), {})
                if module_progress.get('status') != 'completed':
                    return {
                        'type': 'module',
                        'module_id': str(module.module_id),
                        'title': module.title,
                        'description': module.description,
                        'estimated_hours': module.estimated_hours
                    }

            return None

        except Exception:
            return None


class LearningModuleManager:
    """Manager class for learning module operations"""

    @staticmethod
    def create_module_from_ai_data(learning_path: LearningPath, module_data: Dict[str, Any], module_number: int) -> LearningModule:
        """Create a LearningModule from AI-generated data"""
        try:
            # Create learning objectives
            objectives = []
            for obj_text in module_data.get('learning_objectives', []):
                objective = LearningObjective(
                    description=obj_text,
                    bloom_taxonomy_level="understand"  # Default level
                )
                objectives.append(objective)

            # Create lessons
            lessons = []
            for i, lesson_data in enumerate(module_data.get('lessons', []), 1):
                lesson = Lesson(
                    title=lesson_data.get('title', f'Lesson {i}'),
                    description=lesson_data.get('description', ''),
                    lesson_number=i,
                    estimated_time_minutes=lesson_data.get('estimated_minutes', 60),
                    ai_generated=True,
                    generated_at=datetime.utcnow()
                )
                lessons.append(lesson)

            # Create the module
            module = LearningModule(
                title=module_data.get('title', f'Module {module_number}'),
                description=module_data.get('description', ''),
                module_number=module_number,
                learning_path=learning_path,
                difficulty_level=DifficultyLevel(module_data.get('difficulty_level', 'beginner')),
                estimated_hours=module_data.get('estimated_hours', 10),
                learning_objectives=objectives,
                skills_covered=module_data.get('skills_covered', []),
                lessons=lessons,
                ai_generated=True,
                generation_model=module_data.get('generation_model', 'unknown'),
                generated_at=datetime.utcnow()
            )

            return module

        except Exception as e:
            raise ValueError(f"Failed to create module from AI data: {str(e)}")


class ProgressTracker:
    """Utility class for tracking and updating learning progress"""

    @staticmethod
    def update_progress(user: UserPreference, learning_path: LearningPath,
                       activity_type: str, activity_id: str, completion_data: Dict[str, Any]):
        """Update progress for a specific activity"""
        try:
            progress = LearningProgress.objects(user=user, learning_path=learning_path).first()
            if not progress:
                progress = LearningProgress(user=user, learning_path=learning_path)

            # Update activity progress
            if activity_type == 'lesson':
                progress.lesson_progress[activity_id] = completion_data
                progress.lessons_completed += 1
            elif activity_type == 'activity':
                progress.activity_progress[activity_id] = completion_data
                progress.activities_completed += 1
            elif activity_type == 'module':
                progress.module_progress[activity_id] = completion_data
                progress.modules_completed += 1

            # Update overall progress
            progress.overall_progress_percentage = ProgressTracker._calculate_overall_progress(progress)
            progress.last_activity_at = datetime.utcnow()
            progress.last_updated = datetime.utcnow()

            # Update status
            if progress.overall_progress_percentage >= 100:
                progress.status = LearningStatus.COMPLETED
                progress.completed_at = datetime.utcnow()
            elif progress.overall_progress_percentage > 0:
                progress.status = LearningStatus.IN_PROGRESS

            progress.save()
            return progress

        except Exception as e:
            raise ValueError(f"Failed to update progress: {str(e)}")

    @staticmethod
    def _calculate_overall_progress(progress: LearningProgress) -> float:
        """Calculate overall progress percentage"""
        try:
            total_activities = progress.learning_path.total_activities or 1
            completed_activities = progress.activities_completed
            return min(100.0, (completed_activities / total_activities) * 100.0)
        except:
            return 0.0


# Export key classes for easy importing
__all__ = [
    'LearningPath', 'LearningModule', 'LearningProgress',
    'AssessmentSession', 'CodeSubmission',
    'LearningPathManager', 'LearningModuleManager', 'ProgressTracker',
    'LearningStatus', 'DifficultyLevel', 'ContentType', 'QuestionType'
]