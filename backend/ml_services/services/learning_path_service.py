"""
backend/ml_services/services/learning_path_service.py
AI-powered learning path generation service
Creates personalized learning curricula using local ML models and user data
RELEVANT FILES: base/service_interface.py, utils/model_registry.py, core/apps/preferences/models.py
"""

import json
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from django.conf import settings

from ..base.service_interface import BaseMLService, ServiceRequest, ServiceResponse
from ..base.model_interface import InferenceRequest
from ..base.exceptions import MLServiceError, ValidationError
from ..utils.model_registry import get_global_registry
from ..configs.service_configs import get_service_config


@dataclass
class LearningPathRequest(ServiceRequest):
    """Request for learning path generation."""

    # User learning preferences (required fields with default factory to resolve inheritance issue)
    learning_goals: List[str] = None
    experience_level: str = "intermediate"  # 'beginner', 'intermediate', 'advanced'
    time_availability: str = "3-5hrs"  # '1-2hrs', '3-5hrs', '5+hrs'
    preferred_pace: str = "medium"  # 'slow', 'medium', 'fast'
    learning_styles: List[str] = None  # ['visual', 'hands_on', 'reading', 'videos']
    target_timeline: str = "flexible"  # '3months', '6months', '1year', 'flexible'

    # Optional context
    career_stage: Optional[str] = None
    previous_experience: Optional[List[str]] = None
    preferred_platforms: Optional[List[str]] = None
    budget_constraint: Optional[str] = None
    specific_skills: Optional[List[str]] = None

    def __post_init__(self):
        super().__post_init__()
        if self.learning_goals is None:
            self.learning_goals = []
        if self.learning_styles is None:
            self.learning_styles = ['hands_on', 'reading']

    # Generation parameters
    max_modules: int = 8
    max_lessons_per_module: int = 6
    include_projects: bool = True
    include_assessments: bool = True


@dataclass
class LearningModule:
    """A module within a learning path."""
    id: str
    title: str
    description: str
    learning_objectives: List[str]
    estimated_hours: int
    difficulty_level: str
    prerequisites: List[str]
    lessons: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    assessment: Optional[Dict[str, Any]] = None
    projects: Optional[List[Dict[str, Any]]] = None


@dataclass
class LearningPathResponse(ServiceResponse):
    """Response containing generated learning path."""

    # Override the base response for type safety
    def __init__(
        self,
        learning_path: Dict[str, Any],
        modules: List[LearningModule],
        total_estimated_hours: int,
        confidence_score: float,
        processing_time_ms: float,
        request_id: Optional[str] = None
    ):
        super().__init__(
            success=True,
            data={
                'learning_path': learning_path,
                'modules': [self._module_to_dict(module) for module in modules],
                'total_estimated_hours': total_estimated_hours,
                'confidence_score': confidence_score
            },
            processing_time_ms=processing_time_ms,
            request_id=request_id
        )

        self.learning_path = learning_path
        self.modules = modules
        self.total_estimated_hours = total_estimated_hours
        self.confidence_score = confidence_score

    def _module_to_dict(self, module: LearningModule) -> Dict[str, Any]:
        """Convert module to dictionary."""
        return {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'learning_objectives': module.learning_objectives,
            'estimated_hours': module.estimated_hours,
            'difficulty_level': module.difficulty_level,
            'prerequisites': module.prerequisites,
            'lessons': module.lessons,
            'resources': module.resources,
            'assessment': module.assessment,
            'projects': module.projects
        }


class LearningPathService(BaseMLService):
    """
    AI-powered learning path generation service.

    This service creates personalized learning paths by:
    1. Analyzing user preferences and background
    2. Using AI to generate curriculum structure
    3. Mapping skills to appropriate learning resources
    4. Creating progressive difficulty curves
    5. Incorporating various learning modalities

    The service uses multiple models:
    - Primary: Text generation model for curriculum creation
    - Embedding: For content similarity and resource matching
    - Fallback: Alternative models if primary fails
    """

    def __init__(self):
        super().__init__(
            service_name="learning_path_service",
            required_models=["mistral-7b-instruct", "all-minilm-l6-v2"]
        )

        # Service configuration
        self.config = get_service_config("learning_path_service")
        self.primary_model = self.config["primary_model"]
        self.fallback_models = self.config["fallback_models"]
        self.embedding_model = self.config["embedding_model"]

        # Generation parameters
        self.generation_config = self.config["generation"]
        self.max_modules = self.generation_config["max_modules_per_path"]
        self.max_lessons = self.generation_config["max_lessons_per_module"]

        # Skill taxonomy and prerequisites mapping
        self.skill_taxonomy = self._load_skill_taxonomy()
        self.prerequisite_map = self._load_prerequisite_map()

    def initialize(self) -> None:
        """Initialize the learning path service."""
        try:
            self.logger.info("=" * 80)
            self.logger.info("INITIALIZING LEARNING PATH SERVICE")
            self.logger.info("=" * 80)

            # Check ML API provider configuration
            ml_api_provider = getattr(settings, 'ML_API_PROVIDER', 'mock')
            self.logger.warning(f"🔍 ML_API_PROVIDER: {ml_api_provider}")

            # Handle mock mode
            if ml_api_provider == 'mock':
                self.logger.warning("✅ MOCK MODE - Using mock learning path generation")
                self._is_initialized = True
                return

            # Initialize API-based model for external providers
            if ml_api_provider in ['openai', 'groq', 'together']:
                self.logger.info(f"✅ Initializing API-based model with {ml_api_provider}")
                from ..models.api_text_generation_model import APITextGenerationModel

                # Create and load API model
                api_model = APITextGenerationModel("api-text-generation", {
                    'api_model_name': getattr(settings, 'ML_API_MODEL', 'gpt-3.5-turbo')
                })
                api_model.load()
                self.add_model("api-text-generation", api_model)
                self._is_initialized = True
                self.logger.info(f"API-based model initialized successfully with {ml_api_provider}")
                return

            # Legacy: Try loading local models if provider not recognized
            self.logger.warning(f"Unknown ML_API_PROVIDER '{ml_api_provider}', attempting local model loading...")

            # Get model registry
            registry = get_global_registry()

            # Register required models
            for model_name in self.required_models:
                try:
                    model = registry.get_model(model_name, load_if_needed=False)
                    self.add_model(model_name, model)
                    self.logger.info(f"Added model {model_name} to learning path service")
                except Exception as e:
                    self.logger.warning(f"Could not add model {model_name}: {e}")

            # Verify we have at least the primary model
            if self.primary_model not in self._models:
                raise MLServiceError(
                    f"Primary model {self.primary_model} not available",
                    error_code="PRIMARY_MODEL_UNAVAILABLE"
                )

            self._is_initialized = True
            self.logger.info("Learning path service initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize learning path service: {e}")
            raise MLServiceError(f"Service initialization failed: {e}")

    def process(self, request: ServiceRequest) -> ServiceResponse:
        """
        Main processing method for learning path generation.

        Args:
            request: LearningPathRequest with user preferences

        Returns:
            LearningPathResponse with generated learning path
        """
        self._ensure_initialized()

        if not isinstance(request, LearningPathRequest):
            raise ValidationError("request", str(type(request)), "Expected LearningPathRequest")

        start_time = time.time()

        try:
            self.logger.info(f"Generating learning path for user {request.user_id}")

            # Validate the request
            self.validate_request(request)

            # Check which provider to use for generation
            ml_api_provider = getattr(settings, 'ML_API_PROVIDER', 'mock')
            self.logger.warning(f"🔍 process() ML_API_PROVIDER: {ml_api_provider}")
            self.logger.warning(f"🔍 process() _models available: {bool(self._models)}")

            # Use mock generation if in mock mode
            if ml_api_provider == 'mock' or not self._models:
                self.logger.warning("✅ MOCK MODE: Generating mock learning path")
                return self._generate_mock_learning_path(request)

            # Use API-based model if available
            if "api-text-generation" in self._models:
                self.logger.info("✅ Using API-based learning path generation")
                # Use API model for generation (will use _generate_learning_path with API model)
                # Continue to normal flow which will use the API model

            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = self._cache_get(cache_key)

            if cached_response and self._cache_is_valid(cache_key):
                self.logger.info("Returning cached learning path")
                cached_response.request_id = request.request_id
                return cached_response

            # Generate new learning path
            learning_path = self._generate_learning_path(request)

            processing_time_ms = (time.time() - start_time) * 1000

            # Create response
            response = LearningPathResponse(
                learning_path=learning_path['overview'],
                modules=learning_path['modules'],
                total_estimated_hours=learning_path['total_hours'],
                confidence_score=learning_path['confidence_score'],
                processing_time_ms=processing_time_ms,
                request_id=request.request_id
            )

            # Cache the response
            cache_ttl = self.config.get('cache_ttl_seconds', 3600)
            self._cache_set(cache_key, response, cache_ttl)

            # Log the request
            self._log_request(request, response)

            return response

        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Learning path generation failed: {e}")

            # Return error response
            error_response = ServiceResponse(
                success=False,
                error=str(e),
                processing_time_ms=processing_time_ms,
                request_id=request.request_id
            )

            self._log_request(request, error_response)
            return error_response

    def _generate_mock_learning_path(self, request: LearningPathRequest) -> "LearningPathResponse":
        """Generate a mock learning path for development/testing purposes."""
        self.logger.info("Generating mock learning path (ML_MOCK_MODE enabled)")

        # Create mock modules and lessons based on user goals
        goals = request.learning_goals if request.learning_goals else ["web_dev"]
        goal_name = goals[0].replace("_", " ").title()

        mock_modules = [
            {
                "module_number": 1,
                "title": f"Introduction to {goal_name}",
                "description": f"Learn the fundamentals and core concepts of {goal_name}",
                "estimated_hours": 10,
                "difficulty": "beginner",
                "lessons": [
                    {
                        "lesson_number": 1,
                        "title": f"What is {goal_name}?",
                        "type": "video",
                        "duration_minutes": 30,
                        "url": "https://example.com/lesson1",
                        "description": f"Introduction to {goal_name} concepts"
                    },
                    {
                        "lesson_number": 2,
                        "title": "Getting Started",
                        "type": "tutorial",
                        "duration_minutes": 45,
                        "url": "https://example.com/lesson2",
                        "description": "Set up your development environment"
                    }
                ]
            },
            {
                "module_number": 2,
                "title": f"Core {goal_name} Skills",
                "description": f"Build practical skills in {goal_name}",
                "estimated_hours": 15,
                "difficulty": request.experience_level or "intermediate",
                "lessons": [
                    {
                        "lesson_number": 1,
                        "title": "Hands-on Practice",
                        "type": "project",
                        "duration_minutes": 120,
                        "url": "https://example.com/project1",
                        "description": "Build a real project"
                    }
                ]
            }
        ]

        # Create mock response
        return LearningPathResponse(
            learning_path={
                "title": f"Personalized {goal_name} Learning Path",
                "description": f"A comprehensive path to master {goal_name} (Mock Data)",
                "difficulty": request.experience_level or "intermediate",
                "estimated_total_hours": 25
            },
            modules=mock_modules,
            total_estimated_hours=25,
            confidence_score=0.85,
            processing_time_ms=50.0,
            request_id=request.request_id
        )

    def _generate_learning_path(self, request: LearningPathRequest) -> Dict[str, Any]:
        """Generate the complete learning path using AI."""

        # 1. Analyze user requirements and create learning objectives
        learning_objectives = self._analyze_learning_requirements(request)

        # 2. Create curriculum structure using AI
        curriculum_structure = self._generate_curriculum_structure(request, learning_objectives)

        # 3. Generate detailed modules
        modules = self._generate_modules(request, curriculum_structure)

        # 4. Add resources and assessments
        modules = self._enhance_modules_with_resources(modules, request)

        # 5. Validate and optimize the path
        optimized_path = self._optimize_learning_path(modules, request)

        return optimized_path

    def _analyze_learning_requirements(self, request: LearningPathRequest) -> List[str]:
        """Analyze user requirements to create specific learning objectives."""

        # Create AI prompt for learning objective analysis
        prompt = self._create_objectives_prompt(request)

        # Get the primary model
        model = self.get_model(self.primary_model)

        # Generate learning objectives
        inference_request = InferenceRequest(
            prompt=prompt,
            max_length=300,
            temperature=0.7,
            user_id=request.user_id,
            request_id=request.request_id
        )

        response = model.generate(inference_request)

        # Parse objectives from AI response
        objectives = self._parse_learning_objectives(response.generated_text)

        self.logger.info(f"Generated {len(objectives)} learning objectives")
        return objectives

    def _create_objectives_prompt(self, request: LearningPathRequest) -> str:
        """Create AI prompt for learning objectives generation."""

        goals_text = ", ".join(request.learning_goals)
        styles_text = ", ".join(request.learning_styles)

        prompt = f"""As an AI learning path designer, create specific, measurable learning objectives for a student with these preferences:

Learning Goals: {goals_text}
Experience Level: {request.experience_level}
Time Availability: {request.time_availability} per week
Learning Pace: {request.preferred_pace}
Learning Styles: {styles_text}
Timeline: {request.target_timeline}
Career Stage: {request.career_stage or 'not specified'}

Create 5-8 specific learning objectives that are:
1. Measurable and achievable
2. Appropriate for the experience level
3. Aligned with career goals
4. Realistic for the given timeline

Format each objective as: "By the end of this learning path, the learner will be able to..."

Learning Objectives:"""

        return prompt

    def _parse_learning_objectives(self, ai_response: str) -> List[str]:
        """Parse learning objectives from AI response."""
        objectives = []
        lines = ai_response.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line and (
                line.startswith('- ') or
                line.startswith('• ') or
                'will be able to' in line.lower() or
                line[0].isdigit()
            ):
                # Clean up the objective
                objective = line.lstrip('- •0123456789. ')
                if objective:
                    objectives.append(objective)

        # If no objectives found, create default ones
        if not objectives:
            objectives = [
                "Understand fundamental concepts and principles",
                "Apply knowledge to practical scenarios",
                "Complete hands-on projects and exercises",
                "Demonstrate competency through assessments"
            ]

        return objectives[:8]  # Limit to 8 objectives

    def _generate_curriculum_structure(
        self,
        request: LearningPathRequest,
        objectives: List[str]
    ) -> Dict[str, Any]:
        """Generate high-level curriculum structure using AI."""

        # Create curriculum structure prompt
        prompt = self._create_curriculum_prompt(request, objectives)

        # Generate structure using AI
        model = self.get_model(self.primary_model)
        inference_request = InferenceRequest(
            prompt=prompt,
            max_length=800,
            temperature=0.6,
            user_id=request.user_id,
            request_id=request.request_id
        )

        response = model.generate(inference_request)

        # Parse and structure the response
        structure = self._parse_curriculum_structure(response.generated_text, request)

        return structure

    def _create_curriculum_prompt(
        self,
        request: LearningPathRequest,
        objectives: List[str]
    ) -> str:
        """Create AI prompt for curriculum structure generation."""

        objectives_text = "\n".join([f"- {obj}" for obj in objectives])
        goals_text = ", ".join(request.learning_goals)

        prompt = f"""Design a comprehensive learning curriculum for these objectives:

{objectives_text}

Student Profile:
- Learning Goals: {goals_text}
- Experience Level: {request.experience_level}
- Time Available: {request.time_availability} per week
- Learning Pace: {request.preferred_pace}
- Timeline: {request.target_timeline}

Create a curriculum with 4-8 modules that:
1. Progress logically from basics to advanced concepts
2. Build upon previous knowledge (prerequisites)
3. Include hands-on practice and projects
4. Fit within the specified timeline
5. Match the learner's pace and style

For each module, provide:
- Module Title
- Brief Description (1-2 sentences)
- Key Topics (3-5 topics)
- Estimated Hours
- Prerequisites (if any)

Format as:
Module 1: [Title]
Description: [Description]
Topics: [Topic1, Topic2, Topic3]
Hours: [Number]
Prerequisites: [None or list]

Curriculum:"""

        return prompt

    def _parse_curriculum_structure(
        self,
        ai_response: str,
        request: LearningPathRequest
    ) -> Dict[str, Any]:
        """Parse curriculum structure from AI response."""

        modules_data = []
        current_module = None

        lines = ai_response.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect module start
            if line.startswith('Module') and ':' in line:
                # Save previous module
                if current_module:
                    modules_data.append(current_module)

                # Start new module
                title = line.split(':', 1)[1].strip()
                current_module = {
                    'title': title,
                    'description': '',
                    'topics': [],
                    'estimated_hours': 10,  # default
                    'prerequisites': []
                }

            elif current_module:
                if line.startswith('Description:'):
                    current_module['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('Topics:'):
                    topics_text = line.split(':', 1)[1].strip()
                    topics = [t.strip() for t in topics_text.split(',')]
                    current_module['topics'] = topics
                elif line.startswith('Hours:'):
                    try:
                        hours = int(line.split(':')[1].strip())
                        current_module['estimated_hours'] = hours
                    except ValueError:
                        current_module['estimated_hours'] = 10
                elif line.startswith('Prerequisites:'):
                    prereq_text = line.split(':', 1)[1].strip()
                    if prereq_text.lower() not in ['none', 'n/a', '']:
                        prereqs = [p.strip() for p in prereq_text.split(',')]
                        current_module['prerequisites'] = prereqs

        # Add final module
        if current_module:
            modules_data.append(current_module)

        # If no modules parsed, create default structure
        if not modules_data:
            modules_data = self._create_default_curriculum(request)

        return {
            'modules': modules_data[:request.max_modules],  # Respect max modules limit
            'total_modules': len(modules_data),
            'estimated_total_hours': sum(m['estimated_hours'] for m in modules_data)
        }

    def _create_default_curriculum(self, request: LearningPathRequest) -> List[Dict[str, Any]]:
        """Create default curriculum structure if AI parsing fails."""

        main_goal = request.learning_goals[0] if request.learning_goals else "General Learning"

        return [
            {
                'title': f'Introduction to {main_goal}',
                'description': f'Fundamental concepts and overview of {main_goal}',
                'topics': ['Basic concepts', 'Key terminology', 'Overview'],
                'estimated_hours': 8,
                'prerequisites': []
            },
            {
                'title': f'Core {main_goal} Concepts',
                'description': f'Essential knowledge and principles in {main_goal}',
                'topics': ['Core principles', 'Key methodologies', 'Best practices'],
                'estimated_hours': 12,
                'prerequisites': [f'Introduction to {main_goal}']
            },
            {
                'title': f'Practical {main_goal} Applications',
                'description': f'Hands-on practice and real-world applications',
                'topics': ['Practical exercises', 'Case studies', 'Projects'],
                'estimated_hours': 16,
                'prerequisites': [f'Core {main_goal} Concepts']
            },
            {
                'title': f'Advanced {main_goal} Topics',
                'description': f'Advanced concepts and specialized knowledge',
                'topics': ['Advanced techniques', 'Specialized applications', 'Expert insights'],
                'estimated_hours': 14,
                'prerequisites': [f'Practical {main_goal} Applications']
            }
        ]

    def _generate_modules(
        self,
        request: LearningPathRequest,
        curriculum_structure: Dict[str, Any]
    ) -> List[LearningModule]:
        """Generate detailed modules from curriculum structure."""

        modules = []
        module_data_list = curriculum_structure['modules']

        for i, module_data in enumerate(module_data_list):
            module_id = f"module_{i+1:02d}"

            # Generate lessons for this module
            lessons = self._generate_lessons(module_data, request)

            # Generate resources
            resources = self._generate_resources(module_data, request)

            # Create assessment if requested
            assessment = None
            if request.include_assessments:
                assessment = self._generate_assessment(module_data)

            # Create projects if requested
            projects = None
            if request.include_projects and i > 0:  # Skip projects for first module
                projects = self._generate_projects(module_data)

            module = LearningModule(
                id=module_id,
                title=module_data['title'],
                description=module_data['description'],
                learning_objectives=self._create_module_objectives(module_data),
                estimated_hours=module_data['estimated_hours'],
                difficulty_level=self._determine_difficulty_level(i, len(module_data_list), request.experience_level),
                prerequisites=module_data['prerequisites'],
                lessons=lessons,
                resources=resources,
                assessment=assessment,
                projects=projects
            )

            modules.append(module)

        return modules

    def _generate_lessons(self, module_data: Dict[str, Any], request: LearningPathRequest) -> List[Dict[str, Any]]:
        """Generate lessons for a module."""

        lessons = []
        topics = module_data['topics']
        hours_per_lesson = max(1, module_data['estimated_hours'] // len(topics))

        for i, topic in enumerate(topics):
            lesson = {
                'id': f"lesson_{i+1:02d}",
                'title': topic,
                'description': f"Learn about {topic.lower()} in detail",
                'estimated_minutes': hours_per_lesson * 60,
                'content_type': self._suggest_content_type(topic, request.learning_styles),
                'learning_outcomes': [
                    f"Understand key concepts of {topic.lower()}",
                    f"Apply {topic.lower()} in practical scenarios"
                ]
            }
            lessons.append(lesson)

        return lessons

    def _suggest_content_type(self, topic: str, learning_styles: List[str]) -> str:
        """Suggest appropriate content type based on topic and learning styles."""

        # Map learning styles to content types
        style_mapping = {
            'visual': 'video',
            'hands_on': 'interactive',
            'reading': 'article',
            'videos': 'video',
            'interactive': 'interactive'
        }

        # Check if topic suggests specific content type
        if any(word in topic.lower() for word in ['code', 'programming', 'development']):
            return 'interactive'
        elif any(word in topic.lower() for word in ['theory', 'concept', 'principle']):
            return 'article'

        # Use preferred learning style
        for style in learning_styles:
            if style in style_mapping:
                return style_mapping[style]

        return 'video'  # default

    def _generate_resources(self, module_data: Dict[str, Any], request: LearningPathRequest) -> List[Dict[str, Any]]:
        """Generate learning resources for a module."""

        resources = []

        # Add primary learning resource
        resources.append({
            'type': 'course',
            'title': f"Complete Guide to {module_data['title']}",
            'description': module_data['description'],
            'platform': 'recommended',
            'estimated_hours': module_data['estimated_hours'],
            'difficulty': 'appropriate',
            'rating': 4.5
        })

        # Add supplementary resources
        for topic in module_data['topics'][:3]:  # Limit to 3 topics
            resources.append({
                'type': 'article',
                'title': f"Deep Dive: {topic}",
                'description': f"Comprehensive article on {topic.lower()}",
                'platform': 'blog',
                'estimated_hours': 0.5,
                'difficulty': 'appropriate',
                'rating': 4.0
            })

        return resources

    def _generate_assessment(self, module_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate assessment for a module."""

        return {
            'type': 'quiz',
            'title': f"{module_data['title']} Assessment",
            'description': f"Test your knowledge of {module_data['title'].lower()}",
            'questions': 10,
            'estimated_minutes': 20,
            'passing_score': 70,
            'attempts_allowed': 3
        }

    def _generate_projects(self, module_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate projects for a module."""

        return [{
            'type': 'hands_on_project',
            'title': f"Build a {module_data['title']} Project",
            'description': f"Apply your knowledge of {module_data['title'].lower()} in a practical project",
            'estimated_hours': max(4, module_data['estimated_hours'] // 2),
            'difficulty': 'challenging',
            'deliverables': [
                'Working implementation',
                'Documentation',
                'Reflection report'
            ]
        }]

    def _create_module_objectives(self, module_data: Dict[str, Any]) -> List[str]:
        """Create learning objectives for a module."""

        objectives = []
        for topic in module_data['topics']:
            objectives.append(f"Master the fundamentals of {topic.lower()}")

        return objectives

    def _determine_difficulty_level(self, module_index: int, total_modules: int, base_level: str) -> str:
        """Determine difficulty level for a module based on position and user level."""

        progress_ratio = (module_index + 1) / total_modules

        level_mapping = {
            'beginner': ['beginner', 'beginner', 'intermediate', 'intermediate'],
            'intermediate': ['intermediate', 'intermediate', 'advanced', 'advanced'],
            'advanced': ['advanced', 'advanced', 'expert', 'expert']
        }

        if progress_ratio <= 0.25:
            return level_mapping[base_level][0]
        elif progress_ratio <= 0.5:
            return level_mapping[base_level][1]
        elif progress_ratio <= 0.75:
            return level_mapping[base_level][2]
        else:
            return level_mapping[base_level][3]

    def _enhance_modules_with_resources(
        self,
        modules: List[LearningModule],
        request: LearningPathRequest
    ) -> List[LearningModule]:
        """Enhance modules with better resource recommendations."""

        # This is where we could use the embedding model to find similar content
        # For now, we'll enhance with platform-specific recommendations

        preferred_platforms = request.preferred_platforms or ['udemy', 'coursera', 'youtube']

        for module in modules:
            # Update resource platforms based on preferences
            for resource in module.resources:
                if resource['platform'] == 'recommended':
                    resource['platform'] = preferred_platforms[0]

        return modules

    def _optimize_learning_path(
        self,
        modules: List[LearningModule],
        request: LearningPathRequest
    ) -> Dict[str, Any]:
        """Optimize the complete learning path."""

        total_hours = sum(module.estimated_hours for module in modules)

        # VALIDATION: Ensure minimum duration to pass MongoEngine validation
        # LearningPath.estimated_duration_hours has min_value=1 (models.py:76)
        if total_hours < 1:
            self.logger.warning(f"⚠️ Total hours {total_hours} < 1, setting to minimum 10 hours to prevent validation error")
            total_hours = 10  # Set reasonable minimum

            # Distribute hours across modules if they're all 0
            if all(m.estimated_hours == 0 for m in modules):
                hours_per_module = max(1, total_hours // len(modules)) if modules else 10
                for module in modules:
                    module.estimated_hours = hours_per_module
                self.logger.info(f"✅ Distributed {total_hours} hours across {len(modules)} modules ({hours_per_module}h each)")

        # Calculate confidence score based on various factors
        confidence_factors = {
            'user_data_completeness': 0.8,  # How complete is user profile
            'content_coverage': 0.9,  # How well we cover the learning goals
            'resource_quality': 0.85,  # Quality of recommended resources
            'progression_logic': 0.9   # Logical flow of modules
        }

        confidence_score = sum(confidence_factors.values()) / len(confidence_factors)

        # Create overview
        overview = {
            'title': f"Personalized Learning Path: {', '.join(request.learning_goals[:2])}",
            'description': f"A comprehensive {request.target_timeline} learning journey tailored to your {request.experience_level} level",
            'total_modules': len(modules),
            'estimated_total_hours': total_hours,
            'target_timeline': request.target_timeline,
            'experience_level': request.experience_level,
            'created_at': datetime.now().isoformat(),
            'learning_goals': request.learning_goals,
            'key_features': [
                f"Designed for {request.experience_level} learners",
                f"Accommodates {request.time_availability} per week",
                f"Includes hands-on projects" if request.include_projects else "Theory-focused approach",
                f"Regular assessments" if request.include_assessments else "Self-paced learning",
                f"Optimized for {', '.join(request.learning_styles)} learning"
            ]
        }

        return {
            'overview': overview,
            'modules': modules,
            'total_hours': total_hours,
            'confidence_score': confidence_score,
            'generated_at': datetime.now().isoformat()
        }

    def validate_request(self, request: LearningPathRequest) -> None:
        """Validate the learning path request."""

        if not request.learning_goals:
            raise ValidationError("learning_goals", "", "At least one learning goal is required")

        valid_experience_levels = ['beginner', 'intermediate', 'advanced']
        if request.experience_level not in valid_experience_levels:
            raise ValidationError("experience_level", request.experience_level, f"Must be one of: {valid_experience_levels}")

        valid_timelines = ['3months', '6months', '1year', 'flexible']
        if request.target_timeline not in valid_timelines:
            raise ValidationError("target_timeline", request.target_timeline, f"Must be one of: {valid_timelines}")

        if request.max_modules < 1 or request.max_modules > 12:
            raise ValidationError("max_modules", str(request.max_modules), "Must be between 1 and 12")

    def _generate_cache_key(self, request: LearningPathRequest) -> str:
        """Generate cache key for request."""

        key_components = [
            "-".join(sorted(request.learning_goals)),
            request.experience_level,
            request.target_timeline,
            request.preferred_pace,
            "-".join(sorted(request.learning_styles)),
            str(request.max_modules),
            str(request.include_projects),
            str(request.include_assessments)
        ]

        return f"learning_path:{':'.join(key_components)}"

    def _load_skill_taxonomy(self) -> Dict[str, Any]:
        """Load skill taxonomy for learning path generation."""
        # This would typically load from a database or configuration file
        # For now, return a basic taxonomy
        return {
            'programming': {
                'fundamentals': ['variables', 'data_types', 'control_flow'],
                'intermediate': ['functions', 'objects', 'error_handling'],
                'advanced': ['design_patterns', 'algorithms', 'system_design']
            },
            'web_development': {
                'frontend': ['html', 'css', 'javascript'],
                'backend': ['server', 'database', 'api'],
                'fullstack': ['frontend', 'backend', 'deployment']
            }
        }

    def _load_prerequisite_map(self) -> Dict[str, List[str]]:
        """Load prerequisite mapping for skills."""
        return {
            'advanced_programming': ['programming_fundamentals', 'data_structures'],
            'web_backend': ['programming_fundamentals'],
            'machine_learning': ['programming_fundamentals', 'mathematics', 'statistics']
        }