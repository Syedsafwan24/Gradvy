"""
backend/ml_services/services/question_generator_service.py
AI-powered dynamic question and assessment generation service
Creates personalized quizzes, coding challenges, and evaluations based on learning progress
RELEVANT FILES: base/service_interface.py, utils/model_registry.py, services/learning_path_service.py
"""

import json
import time
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..base.service_interface import BaseMLService, ServiceRequest, ServiceResponse
from ..base.model_interface import InferenceRequest
from ..base.exceptions import MLServiceError, ValidationError
from ..utils.model_registry import get_global_registry
from ..configs.service_configs import get_service_config


class QuestionType(Enum):
    """Types of questions that can be generated"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    CODING_CHALLENGE = "coding_challenge"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    ESSAY = "essay"


class DifficultyLevel(Enum):
    """Question difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class QuestionGenerationRequest(ServiceRequest):
    """Request for question generation"""

    # Content specification (required field with default to resolve inheritance issue)
    topic: str = "General Programming"
    subtopics: List[str] = None
    learning_objectives: List[str] = None

    # Question parameters
    question_types: List[QuestionType] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    num_questions: int = 5
    max_options_per_question: int = 4

    def __post_init__(self):
        super().__post_init__()
        if self.subtopics is None:
            self.subtopics = []
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.question_types is None:
            self.question_types = [QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER]

    # Context from learning path
    previous_topics: Optional[List[str]] = None
    user_performance_history: Optional[Dict[str, float]] = None
    preferred_question_types: Optional[List[QuestionType]] = None

    # Special requirements
    include_explanations: bool = True
    include_hints: bool = False
    programming_language: Optional[str] = None  # For coding challenges
    assessment_purpose: str = "practice"  # 'practice', 'assessment', 'final_exam'


@dataclass
class GeneratedQuestion:
    """A single generated question with all its components"""

    question_id: str
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    topic: str

    # Core question content
    question_text: str
    options: Optional[List[str]] = None  # For multiple choice, matching
    correct_answer: str = ""

    # Additional content
    explanation: Optional[str] = None
    hint: Optional[str] = None
    code_template: Optional[str] = None  # For coding challenges
    test_cases: Optional[List[Dict[str, Any]]] = None  # For coding challenges

    # Metadata
    estimated_time_minutes: int = 5
    learning_objectives: List[str] = None
    tags: List[str] = None
    confidence_score: float = 0.8


@dataclass
class QuestionGenerationResponse(ServiceResponse):
    """Response containing generated questions"""

    def __init__(
        self,
        questions: List[GeneratedQuestion],
        topic_coverage: Dict[str, int],
        difficulty_distribution: Dict[str, int],
        generation_metadata: Dict[str, Any],
        processing_time_ms: float,
        request_id: Optional[str] = None
    ):
        super().__init__(
            success=True,
            data={
                'questions': [self._question_to_dict(q) for q in questions],
                'topic_coverage': topic_coverage,
                'difficulty_distribution': difficulty_distribution,
                'generation_metadata': generation_metadata
            },
            processing_time_ms=processing_time_ms,
            request_id=request_id
        )

        self.questions = questions
        self.topic_coverage = topic_coverage
        self.difficulty_distribution = difficulty_distribution
        self.generation_metadata = generation_metadata

    def _question_to_dict(self, question: GeneratedQuestion) -> Dict[str, Any]:
        """Convert question to dictionary for JSON serialization"""
        return {
            'question_id': question.question_id,
            'question_type': question.question_type.value,
            'difficulty_level': question.difficulty_level.value,
            'topic': question.topic,
            'question_text': question.question_text,
            'options': question.options,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'hint': question.hint,
            'code_template': question.code_template,
            'test_cases': question.test_cases,
            'estimated_time_minutes': question.estimated_time_minutes,
            'learning_objectives': question.learning_objectives or [],
            'tags': question.tags or [],
            'confidence_score': question.confidence_score
        }


class QuestionGeneratorService(BaseMLService):
    """
    AI-powered question generation service.

    This service creates high-quality educational questions by:
    1. Analyzing learning content and objectives
    2. Using AI to generate contextually relevant questions
    3. Creating diverse question types (multiple choice, coding, etc.)
    4. Adapting difficulty based on user performance
    5. Ensuring educational quality and validity
    6. Integrating with the playground for coding challenges

    The service uses multiple models:
    - Primary: FLAN-T5-XL for structured question generation
    - Fallback: Mistral-7B for general question creation
    - Code model: CodeLlama for programming questions
    """

    def __init__(self):
        super().__init__(
            service_name="question_generator_service",
            required_models=["flan-t5-xl", "mistral-7b-instruct", "codellama-7b-instruct"]
        )

        # Service configuration
        self.config = get_service_config("question_generator_service")
        self.primary_model = self.config["primary_model"]
        self.fallback_models = self.config["fallback_models"]

        # Generation parameters
        self.generation_config = self.config["generation"]
        self.quality_control = self.config["quality_control"]

        # Question templates and patterns
        self.question_templates = self._load_question_templates()
        self.bloom_taxonomy_levels = self._load_bloom_taxonomy()

    def initialize(self) -> None:
        """Initialize the question generator service"""
        try:
            self.logger.info("Initializing question generator service")

            # Get model registry
            registry = get_global_registry()

            # Register required models
            for model_name in self.required_models:
                try:
                    model = registry.get_model(model_name, load_if_needed=False)
                    self.add_model(model_name, model)
                    self.logger.info(f"Added model {model_name} to question generator")
                except Exception as e:
                    self.logger.warning(f"Could not add model {model_name}: {e}")

            # Verify we have at least the primary model
            if self.primary_model not in self._models:
                self.logger.warning(f"Primary model {self.primary_model} not available, using fallback")

            self._is_initialized = True
            self.logger.info("Question generator service initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize question generator: {e}")
            raise MLServiceError(f"Service initialization failed: {e}")

    def process(self, request: ServiceRequest) -> ServiceResponse:
        """
        Generate questions based on request parameters

        Args:
            request: QuestionGenerationRequest with generation parameters

        Returns:
            QuestionGenerationResponse with generated questions
        """
        self._ensure_initialized()

        if not isinstance(request, QuestionGenerationRequest):
            raise ValidationError("request", str(type(request)), "Expected QuestionGenerationRequest")

        start_time = time.time()

        try:
            self.logger.info(f"Generating {request.num_questions} questions for topic: {request.topic}")

            # Validate request
            self.validate_request(request)

            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = self._cache_get(cache_key)

            if cached_response and self._cache_is_valid(cache_key):
                self.logger.info("Returning cached questions")
                cached_response.request_id = request.request_id
                return cached_response

            # Generate new questions
            questions = self._generate_questions_batch(request)

            # Quality control and validation
            validated_questions = self._validate_and_filter_questions(questions, request)

            # Analyze generation results
            analysis = self._analyze_generated_questions(validated_questions, request)

            processing_time_ms = (time.time() - start_time) * 1000

            # Create response
            response = QuestionGenerationResponse(
                questions=validated_questions,
                topic_coverage=analysis['topic_coverage'],
                difficulty_distribution=analysis['difficulty_distribution'],
                generation_metadata=analysis['metadata'],
                processing_time_ms=processing_time_ms,
                request_id=request.request_id
            )

            # Cache the response
            cache_ttl = self.config.get('cache_ttl_seconds', 1800)  # 30 minutes
            self._cache_set(cache_key, response, cache_ttl)

            # Log the request
            self._log_request(request, response)

            return response

        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            self.logger.error(f"Question generation failed: {e}")

            error_response = ServiceResponse(
                success=False,
                error=str(e),
                processing_time_ms=processing_time_ms,
                request_id=request.request_id
            )

            self._log_request(request, error_response)
            return error_response

    def _generate_questions_batch(self, request: QuestionGenerationRequest) -> List[GeneratedQuestion]:
        """Generate a batch of questions using AI"""

        questions = []
        question_types = request.question_types or [QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER]

        # Distribute questions across types
        type_distribution = self._calculate_question_type_distribution(request.num_questions, question_types)

        for question_type, count in type_distribution.items():
            batch_questions = self._generate_questions_by_type(
                request, question_type, count
            )
            questions.extend(batch_questions)

        return questions

    def _calculate_question_type_distribution(
        self,
        total_questions: int,
        question_types: List[QuestionType]
    ) -> Dict[QuestionType, int]:
        """Calculate how many questions of each type to generate"""

        distribution = {}
        base_count = total_questions // len(question_types)
        remainder = total_questions % len(question_types)

        for i, question_type in enumerate(question_types):
            distribution[question_type] = base_count + (1 if i < remainder else 0)

        return distribution

    def _generate_questions_by_type(
        self,
        request: QuestionGenerationRequest,
        question_type: QuestionType,
        count: int
    ) -> List[GeneratedQuestion]:
        """Generate questions of a specific type"""

        questions = []

        for i in range(count):
            try:
                if question_type == QuestionType.CODING_CHALLENGE:
                    question = self._generate_coding_question(request)
                else:
                    question = self._generate_text_question(request, question_type)

                if question:
                    questions.append(question)

            except Exception as e:
                self.logger.warning(f"Failed to generate {question_type.value} question: {e}")

        return questions

    def _generate_text_question(
        self,
        request: QuestionGenerationRequest,
        question_type: QuestionType
    ) -> Optional[GeneratedQuestion]:
        """Generate text-based questions using AI"""

        # Create AI prompt based on question type
        prompt = self._create_question_prompt(request, question_type)

        # Choose appropriate model
        model_name = self.primary_model if self.primary_model in self._models else self.fallback_models[0]
        model = self.get_model(model_name)

        # Generate question
        inference_request = InferenceRequest(
            prompt=prompt,
            max_length=400,
            temperature=0.7,
            user_id=request.user_id,
            request_id=request.request_id
        )

        response = model.generate(inference_request)

        # Parse the AI response into structured question
        question = self._parse_question_response(
            response.generated_text,
            request,
            question_type
        )

        return question

    def _create_question_prompt(
        self,
        request: QuestionGenerationRequest,
        question_type: QuestionType
    ) -> str:
        """Create AI prompt for question generation"""

        subtopics_text = ", ".join(request.subtopics) if request.subtopics else "general concepts"
        objectives_text = "\n".join([f"- {obj}" for obj in (request.learning_objectives or [])])

        base_prompt = f"""Create a {question_type.value.replace('_', ' ')} question about {request.topic}.

Topic: {request.topic}
Subtopics: {subtopics_text}
Difficulty Level: {request.difficulty_level.value}
Purpose: {request.assessment_purpose}

Learning Objectives:
{objectives_text or "- Test understanding of core concepts"}

Requirements:
- Question should be clear and unambiguous
- Appropriate for {request.difficulty_level.value} level learners
- Educational and engaging
- Test practical understanding"""

        if question_type == QuestionType.MULTIPLE_CHOICE:
            prompt = base_prompt + f"""

Create a multiple choice question with {request.max_options_per_question} options.

Format your response as:
QUESTION: [Your question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
CORRECT: [Letter of correct answer]
EXPLANATION: [Why this is correct and others are wrong]

Question:"""

        elif question_type == QuestionType.TRUE_FALSE:
            prompt = base_prompt + """

Create a true/false question that tests understanding.

Format your response as:
QUESTION: [Your true/false statement]
CORRECT: [True or False]
EXPLANATION: [Explanation of why this is true/false]

Question:"""

        elif question_type == QuestionType.SHORT_ANSWER:
            prompt = base_prompt + """

Create a short answer question requiring 1-3 sentences.

Format your response as:
QUESTION: [Your question here]
ANSWER: [Expected answer]
EXPLANATION: [Additional context or explanation]

Question:"""

        elif question_type == QuestionType.FILL_IN_BLANK:
            prompt = base_prompt + """

Create a fill-in-the-blank question with one or more blanks.

Format your response as:
QUESTION: [Question with _____ blanks]
ANSWER: [Words/phrases to fill blanks]
EXPLANATION: [Why these are correct]

Question:"""

        else:
            prompt = base_prompt + "\n\nGenerate an appropriate question:"

        return prompt

    def _generate_coding_question(self, request: QuestionGenerationRequest) -> Optional[GeneratedQuestion]:
        """Generate coding challenge questions"""

        if "codellama-7b-instruct" not in self._models:
            self.logger.warning("CodeLlama not available for coding questions")
            return None

        # Create coding-specific prompt
        prompt = self._create_coding_prompt(request)

        model = self.get_model("codellama-7b-instruct")
        inference_request = InferenceRequest(
            prompt=prompt,
            max_length=600,
            temperature=0.6,
            user_id=request.user_id,
            request_id=request.request_id
        )

        response = model.generate(inference_request)

        # Parse coding question
        question = self._parse_coding_response(response.generated_text, request)

        return question

    def _create_coding_prompt(self, request: QuestionGenerationRequest) -> str:
        """Create prompt for coding question generation"""

        language = request.programming_language or "python"

        prompt = f"""Create a {language} programming challenge about {request.topic}.

Topic: {request.topic}
Difficulty: {request.difficulty_level.value}
Language: {language}

Requirements:
- Clear problem description
- Appropriate for {request.difficulty_level.value} programmers
- Include example input/output
- Provide starter code template
- Include test cases

Format your response as:
PROBLEM: [Clear problem description]
EXAMPLE: [Input/output example]
TEMPLATE: [Starter code with TODO comments]
TESTS: [Test cases in format: input -> expected_output]

Challenge:"""

        return prompt

    def _parse_question_response(
        self,
        ai_response: str,
        request: QuestionGenerationRequest,
        question_type: QuestionType
    ) -> Optional[GeneratedQuestion]:
        """Parse AI response into structured question"""

        try:
            question_id = self._generate_question_id(request.topic, question_type)

            if question_type == QuestionType.MULTIPLE_CHOICE:
                return self._parse_multiple_choice(ai_response, question_id, request)
            elif question_type == QuestionType.TRUE_FALSE:
                return self._parse_true_false(ai_response, question_id, request)
            elif question_type == QuestionType.SHORT_ANSWER:
                return self._parse_short_answer(ai_response, question_id, request)
            elif question_type == QuestionType.FILL_IN_BLANK:
                return self._parse_fill_blank(ai_response, question_id, request)
            else:
                return self._parse_generic_question(ai_response, question_id, request, question_type)

        except Exception as e:
            self.logger.error(f"Failed to parse question response: {e}")
            return None

    def _parse_multiple_choice(
        self,
        response: str,
        question_id: str,
        request: QuestionGenerationRequest
    ) -> GeneratedQuestion:
        """Parse multiple choice question from AI response"""

        lines = response.strip().split('\n')
        question_text = ""
        options = []
        correct_answer = ""
        explanation = ""

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('QUESTION:'):
                question_text = line[9:].strip()
                current_section = 'question'
            elif line.startswith('CORRECT:'):
                correct_answer = line[8:].strip()
                current_section = 'correct'
            elif line.startswith('EXPLANATION:'):
                explanation = line[12:].strip()
                current_section = 'explanation'
            elif re.match(r'^[A-D]\)', line):
                options.append(line[2:].strip())
            elif current_section == 'explanation':
                explanation += " " + line

        # Fallback parsing if structured format not found
        if not question_text or not options:
            question_text, options, correct_answer, explanation = self._fallback_parse_mc(response)

        return GeneratedQuestion(
            question_id=question_id,
            question_type=QuestionType.MULTIPLE_CHOICE,
            difficulty_level=request.difficulty_level,
            topic=request.topic,
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            explanation=explanation,
            estimated_time_minutes=3,
            learning_objectives=request.learning_objectives,
            confidence_score=0.8
        )

    def _parse_true_false(
        self,
        response: str,
        question_id: str,
        request: QuestionGenerationRequest
    ) -> GeneratedQuestion:
        """Parse true/false question"""

        question_text = ""
        correct_answer = ""
        explanation = ""

        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('QUESTION:'):
                question_text = line[9:].strip()
            elif line.startswith('CORRECT:'):
                correct_answer = line[8:].strip().lower()
            elif line.startswith('EXPLANATION:'):
                explanation = line[12:].strip()

        # Fallback parsing
        if not question_text:
            question_text = lines[0] if lines else "True or False question"

        return GeneratedQuestion(
            question_id=question_id,
            question_type=QuestionType.TRUE_FALSE,
            difficulty_level=request.difficulty_level,
            topic=request.topic,
            question_text=question_text,
            options=["True", "False"],
            correct_answer=correct_answer,
            explanation=explanation,
            estimated_time_minutes=2,
            learning_objectives=request.learning_objectives,
            confidence_score=0.8
        )

    def _parse_short_answer(
        self,
        response: str,
        question_id: str,
        request: QuestionGenerationRequest
    ) -> GeneratedQuestion:
        """Parse short answer question"""

        question_text = ""
        correct_answer = ""
        explanation = ""

        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('QUESTION:'):
                question_text = line[9:].strip()
            elif line.startswith('ANSWER:'):
                correct_answer = line[7:].strip()
            elif line.startswith('EXPLANATION:'):
                explanation = line[12:].strip()

        return GeneratedQuestion(
            question_id=question_id,
            question_type=QuestionType.SHORT_ANSWER,
            difficulty_level=request.difficulty_level,
            topic=request.topic,
            question_text=question_text,
            correct_answer=correct_answer,
            explanation=explanation,
            estimated_time_minutes=5,
            learning_objectives=request.learning_objectives,
            confidence_score=0.7
        )

    def _parse_coding_response(
        self,
        response: str,
        request: QuestionGenerationRequest
    ) -> Optional[GeneratedQuestion]:
        """Parse coding challenge from AI response"""

        question_id = self._generate_question_id(request.topic, QuestionType.CODING_CHALLENGE)

        problem = ""
        template = ""
        test_cases = []

        lines = response.strip().split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('PROBLEM:'):
                problem = line[8:].strip()
                current_section = 'problem'
            elif line.startswith('TEMPLATE:'):
                template = line[9:].strip()
                current_section = 'template'
            elif line.startswith('TESTS:'):
                current_section = 'tests'
            elif current_section == 'template' and line:
                template += "\n" + line
            elif current_section == 'tests' and '->' in line:
                test_cases.append(self._parse_test_case(line))

        return GeneratedQuestion(
            question_id=question_id,
            question_type=QuestionType.CODING_CHALLENGE,
            difficulty_level=request.difficulty_level,
            topic=request.topic,
            question_text=problem,
            code_template=template,
            test_cases=test_cases,
            estimated_time_minutes=15,
            learning_objectives=request.learning_objectives,
            confidence_score=0.7
        )

    def _parse_test_case(self, test_line: str) -> Dict[str, Any]:
        """Parse a test case line"""
        parts = test_line.split('->')
        if len(parts) == 2:
            return {
                'input': parts[0].strip(),
                'expected_output': parts[1].strip()
            }
        return {'input': '', 'expected_output': ''}

    def _fallback_parse_mc(self, response: str) -> Tuple[str, List[str], str, str]:
        """Fallback parser for multiple choice questions"""
        lines = [line.strip() for line in response.split('\n') if line.strip()]

        question_text = lines[0] if lines else "Multiple choice question"
        options = []
        correct_answer = "A"
        explanation = ""

        for line in lines[1:]:
            if re.match(r'^[A-D]\)', line):
                options.append(line[2:].strip())

        return question_text, options or ["Option 1", "Option 2", "Option 3", "Option 4"], correct_answer, explanation

    def _validate_and_filter_questions(
        self,
        questions: List[GeneratedQuestion],
        request: QuestionGenerationRequest
    ) -> List[GeneratedQuestion]:
        """Validate and filter generated questions for quality"""

        validated = []
        min_confidence = self.quality_control.get('min_confidence_score', 0.7)

        for question in questions:
            if self._is_question_valid(question, min_confidence):
                validated.append(question)

        # If we don't have enough valid questions, generate simple fallbacks
        if len(validated) < request.num_questions:
            needed = request.num_questions - len(validated)
            fallbacks = self._generate_fallback_questions(request, needed)
            validated.extend(fallbacks)

        return validated[:request.num_questions]

    def _is_question_valid(self, question: GeneratedQuestion, min_confidence: float) -> bool:
        """Check if a question meets quality standards"""

        # Basic validation
        if not question.question_text or len(question.question_text.strip()) < 10:
            return False

        if question.confidence_score < min_confidence:
            return False

        # Type-specific validation
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            if not question.options or len(question.options) < 2:
                return False
            if not question.correct_answer:
                return False

        return True

    def _generate_fallback_questions(
        self,
        request: QuestionGenerationRequest,
        count: int
    ) -> List[GeneratedQuestion]:
        """Generate simple fallback questions if AI generation fails"""

        fallbacks = []

        for i in range(count):
            question_id = self._generate_question_id(f"{request.topic}_fallback", QuestionType.MULTIPLE_CHOICE)

            question = GeneratedQuestion(
                question_id=question_id,
                question_type=QuestionType.MULTIPLE_CHOICE,
                difficulty_level=request.difficulty_level,
                topic=request.topic,
                question_text=f"Which of the following is an important concept in {request.topic}?",
                options=[
                    f"Core principles of {request.topic}",
                    f"Advanced techniques in {request.topic}",
                    f"Basic fundamentals of {request.topic}",
                    f"All of the above"
                ],
                correct_answer="D",
                explanation=f"All aspects are important when learning {request.topic}",
                estimated_time_minutes=3,
                confidence_score=0.6
            )

            fallbacks.append(question)

        return fallbacks

    def _analyze_generated_questions(
        self,
        questions: List[GeneratedQuestion],
        request: QuestionGenerationRequest
    ) -> Dict[str, Any]:
        """Analyze the generated question set"""

        topic_coverage = {}
        difficulty_distribution = {}
        type_distribution = {}

        for question in questions:
            # Topic coverage
            topic = question.topic
            topic_coverage[topic] = topic_coverage.get(topic, 0) + 1

            # Difficulty distribution
            difficulty = question.difficulty_level.value
            difficulty_distribution[difficulty] = difficulty_distribution.get(difficulty, 0) + 1

            # Type distribution
            q_type = question.question_type.value
            type_distribution[q_type] = type_distribution.get(q_type, 0) + 1

        avg_confidence = sum(q.confidence_score for q in questions) / len(questions) if questions else 0
        total_time = sum(q.estimated_time_minutes for q in questions)

        return {
            'topic_coverage': topic_coverage,
            'difficulty_distribution': difficulty_distribution,
            'metadata': {
                'type_distribution': type_distribution,
                'average_confidence': avg_confidence,
                'total_estimated_time_minutes': total_time,
                'questions_generated': len(questions),
                'generation_timestamp': datetime.now().isoformat()
            }
        }

    def validate_request(self, request: QuestionGenerationRequest) -> None:
        """Validate question generation request"""

        if not request.topic or len(request.topic.strip()) < 2:
            raise ValidationError("topic", request.topic, "Topic must be at least 2 characters")

        if request.num_questions < 1 or request.num_questions > 50:
            raise ValidationError("num_questions", str(request.num_questions), "Must be between 1 and 50")

        if request.max_options_per_question < 2 or request.max_options_per_question > 6:
            raise ValidationError("max_options_per_question", str(request.max_options_per_question), "Must be between 2 and 6")

    def _generate_cache_key(self, request: QuestionGenerationRequest) -> str:
        """Generate cache key for request"""

        key_components = [
            request.topic,
            request.difficulty_level.value,
            str(request.num_questions),
            str(sorted([qt.value for qt in (request.question_types or [])])),
            request.assessment_purpose,
            str(request.include_explanations),
            request.programming_language or ""
        ]

        key_string = ":".join(key_components)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]

        return f"questions:{key_hash}"

    def _generate_question_id(self, topic: str, question_type: QuestionType) -> str:
        """Generate unique question ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_hash = hashlib.md5(topic.encode()).hexdigest()[:8]
        return f"q_{question_type.value}_{topic_hash}_{timestamp}"

    def _load_question_templates(self) -> Dict[str, Any]:
        """Load question templates for different types"""
        return {
            'multiple_choice': {
                'format': 'QUESTION: {question}\nA) {option_a}\nB) {option_b}\nC) {option_c}\nD) {option_d}\nCORRECT: {correct}',
                'required_fields': ['question', 'options', 'correct_answer']
            },
            'true_false': {
                'format': 'QUESTION: {question}\nCORRECT: {correct}',
                'required_fields': ['question', 'correct_answer']
            }
        }

    def _load_bloom_taxonomy(self) -> Dict[str, List[str]]:
        """Load Bloom's taxonomy levels for educational alignment"""
        return {
            'remember': ['define', 'list', 'recall', 'identify', 'name'],
            'understand': ['explain', 'describe', 'summarize', 'classify', 'compare'],
            'apply': ['demonstrate', 'solve', 'use', 'implement', 'execute'],
            'analyze': ['examine', 'break down', 'differentiate', 'organize', 'deconstruct'],
            'evaluate': ['critique', 'judge', 'assess', 'validate', 'rate'],
            'create': ['design', 'build', 'develop', 'compose', 'generate']
        }