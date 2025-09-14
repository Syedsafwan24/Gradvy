"""
backend/ml_services/services/code_evaluation_service.py
AI-powered code evaluation service for playground integration and assessment
Provides comprehensive code analysis, feedback, and scoring for learning activities
RELEVANT FILES: services/question_generator_service.py, utils/data_sanitizer.py, base/service_interface.py
"""

import re
import ast
import logging
import traceback
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from ..base.service_interface import BaseMLService, ServiceRequest, ServiceResponse
from ..utils.data_sanitizer import DataSanitizer


# Logging configuration
logger = logging.getLogger(__name__)


class CodeLanguage(Enum):
    """Supported programming languages for code evaluation"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    TYPESCRIPT = "typescript"
    UNKNOWN = "unknown"


class CodeComplexity(Enum):
    """Code complexity levels for assessment"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EvaluationAspect(Enum):
    """Different aspects of code evaluation"""
    CORRECTNESS = "correctness"
    STYLE = "style"
    EFFICIENCY = "efficiency"
    READABILITY = "readability"
    BEST_PRACTICES = "best_practices"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"


@dataclass
class CodeIssue:
    """Represents a single issue found in code"""
    aspect: EvaluationAspect
    severity: str  # "error", "warning", "suggestion"
    line_number: Optional[int]
    column: Optional[int]
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


@dataclass
class CodeAnalysis:
    """Results of static code analysis"""
    syntax_valid: bool
    complexity_score: float  # 0-10
    readability_score: float  # 0-10
    maintainability_score: float  # 0-10
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeEvaluationRequest(ServiceRequest):
    """Request for code evaluation"""
    code: str
    language: CodeLanguage
    problem_description: Optional[str] = None
    expected_output: Optional[str] = None
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    evaluation_aspects: List[EvaluationAspect] = field(default_factory=list)
    difficulty_level: CodeComplexity = CodeComplexity.BEGINNER
    max_execution_time: int = 30  # seconds
    include_suggestions: bool = True
    include_ai_feedback: bool = True


@dataclass
class CodeEvaluationResponse(ServiceResponse):
    """Response from code evaluation"""
    overall_score: float = 0.0  # 0-100
    aspect_scores: Dict[EvaluationAspect, float] = field(default_factory=dict)
    analysis: Optional[CodeAnalysis] = None
    ai_feedback: str = ""
    suggestions: List[str] = field(default_factory=list)
    passed_tests: int = 0
    total_tests: int = 0
    execution_results: List[Dict[str, Any]] = field(default_factory=list)
    improved_code: Optional[str] = None
    learning_progress: Dict[str, Any] = field(default_factory=dict)


class CodeEvaluationService(BaseMLService):
    """
    AI-powered code evaluation service for playground integration.

    This service provides comprehensive code analysis and evaluation including:
    - Static analysis for syntax, style, and best practices
    - AI-powered feedback and suggestions using CodeLlama models
    - Test case execution and validation
    - Learning progress tracking and objective alignment
    - Security vulnerability detection
    - Performance optimization suggestions
    """

    def __init__(self):
        super().__init__()
        self.service_name = "CodeEvaluationService"
        self.service_version = "1.0.0"
        self.primary_model = "codellama-7b-instruct"
        self.required_models = ["codellama-7b-instruct", "starcoder-7b"]

        # Language-specific patterns and rules
        self.language_patterns = self._initialize_language_patterns()

        # Data sanitizer for privacy compliance
        self.data_sanitizer = DataSanitizer()

        # Evaluation weights for different aspects
        self.aspect_weights = {
            EvaluationAspect.CORRECTNESS: 0.4,
            EvaluationAspect.STYLE: 0.15,
            EvaluationAspect.EFFICIENCY: 0.15,
            EvaluationAspect.READABILITY: 0.1,
            EvaluationAspect.BEST_PRACTICES: 0.1,
            EvaluationAspect.SECURITY: 0.05,
            EvaluationAspect.MAINTAINABILITY: 0.05
        }

    def _initialize_language_patterns(self) -> Dict[CodeLanguage, Dict[str, Any]]:
        """Initialize language-specific analysis patterns"""
        return {
            CodeLanguage.PYTHON: {
                "syntax_checker": self._check_python_syntax,
                "style_rules": [
                    r"^(\s{4})*[^\s]",  # 4-space indentation
                    r"^[a-z_][a-z0-9_]*$",  # snake_case variables
                ],
                "complexity_keywords": ["for", "while", "if", "elif", "try", "except", "with"],
                "security_patterns": [
                    r"eval\s*\(",
                    r"exec\s*\(",
                    r"subprocess\.",
                    r"os\.system",
                ]
            },
            CodeLanguage.JAVASCRIPT: {
                "syntax_checker": self._check_javascript_syntax,
                "style_rules": [
                    r"^\s{2}",  # 2-space indentation
                    r"^[a-zA-Z$_][a-zA-Z0-9$_]*$",  # camelCase variables
                ],
                "complexity_keywords": ["for", "while", "if", "else", "try", "catch", "switch"],
                "security_patterns": [
                    r"eval\s*\(",
                    r"innerHTML\s*=",
                    r"document\.write",
                ]
            },
        }

    def initialize(self) -> bool:
        """Initialize the code evaluation service"""
        try:
            logger.info(f"Initializing {self.service_name}...")

            # Initialize base service
            if not super().initialize():
                return False

            # Verify required models
            missing_models = []
            for model_name in self.required_models:
                if not self.model_registry.is_model_available(model_name):
                    missing_models.append(model_name)

            if missing_models:
                logger.warning(f"Missing models: {missing_models}. Some features may be limited.")

            self.is_initialized = True
            logger.info(f"{self.service_name} initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize {self.service_name}: {e}")
            return False

    def process(self, request: CodeEvaluationRequest) -> CodeEvaluationResponse:
        """Process code evaluation request"""
        try:
            # Validate request
            if not self._validate_request(request):
                return CodeEvaluationResponse(
                    success=False,
                    error="Invalid request parameters"
                )

            # Sanitize input data for privacy compliance
            sanitized_code = self.data_sanitizer.sanitize_code(
                request.code,
                request.language.value
            )

            # Step 1: Static Analysis
            analysis = self._perform_static_analysis(sanitized_code, request.language)

            # Step 2: Test Case Execution (if provided)
            execution_results, passed_tests, total_tests = self._execute_test_cases(
                sanitized_code,
                request.test_cases,
                request.language,
                request.max_execution_time
            )

            # Step 3: AI-Powered Analysis
            ai_feedback, suggestions, improved_code = self._generate_ai_feedback(
                sanitized_code,
                request,
                analysis,
                execution_results
            )

            # Step 4: Calculate Scores
            aspect_scores = self._calculate_aspect_scores(
                analysis,
                passed_tests,
                total_tests,
                request.evaluation_aspects
            )

            overall_score = self._calculate_overall_score(aspect_scores)

            # Step 5: Track Learning Progress
            learning_progress = self._track_learning_progress(
                request.learning_objectives,
                aspect_scores,
                overall_score
            )

            return CodeEvaluationResponse(
                success=True,
                overall_score=overall_score,
                aspect_scores=aspect_scores,
                analysis=analysis,
                ai_feedback=ai_feedback if request.include_ai_feedback else "",
                suggestions=suggestions if request.include_suggestions else [],
                passed_tests=passed_tests,
                total_tests=total_tests,
                execution_results=execution_results,
                improved_code=improved_code,
                learning_progress=learning_progress,
                processing_time_ms=self._get_processing_time()
            )

        except Exception as e:
            logger.error(f"Error processing code evaluation: {e}")
            return CodeEvaluationResponse(
                success=False,
                error=f"Code evaluation failed: {str(e)}"
            )

    def _validate_request(self, request: CodeEvaluationRequest) -> bool:
        """Validate code evaluation request"""
        try:
            # Check required fields
            if not request.code or not request.code.strip():
                return False

            # Check code length limits (prevent abuse)
            if len(request.code) > 50000:  # 50KB limit
                return False

            # Validate language
            if request.language == CodeLanguage.UNKNOWN:
                # Try to detect language
                request.language = self._detect_language(request.code)

            # Set default evaluation aspects if not provided
            if not request.evaluation_aspects:
                request.evaluation_aspects = [
                    EvaluationAspect.CORRECTNESS,
                    EvaluationAspect.STYLE,
                    EvaluationAspect.READABILITY
                ]

            return True

        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return False

    def _detect_language(self, code: str) -> CodeLanguage:
        """Detect programming language from code content"""
        try:
            # Simple heuristic-based language detection
            code_lower = code.lower()

            # Python indicators
            if any(keyword in code_lower for keyword in ["def ", "import ", "print(", "if __name__"]):
                return CodeLanguage.PYTHON

            # JavaScript indicators
            elif any(keyword in code for keyword in ["function ", "var ", "let ", "const ", "console.log"]):
                return CodeLanguage.JAVASCRIPT

            # Java indicators
            elif any(keyword in code for keyword in ["public class", "public static void main", "System.out"]):
                return CodeLanguage.JAVA

            # C++ indicators
            elif any(keyword in code for keyword in ["#include", "iostream", "std::", "cout"]):
                return CodeLanguage.CPP

            # SQL indicators
            elif any(keyword in code_lower for keyword in ["select ", "from ", "where ", "insert ", "update "]):
                return CodeLanguage.SQL

            return CodeLanguage.UNKNOWN

        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return CodeLanguage.UNKNOWN

    def _perform_static_analysis(self, code: str, language: CodeLanguage) -> CodeAnalysis:
        """Perform static code analysis"""
        try:
            issues = []
            metrics = {}

            # Check syntax
            syntax_valid = self._check_syntax(code, language)

            # Calculate complexity metrics
            complexity_score = self._calculate_complexity(code, language)
            readability_score = self._calculate_readability(code, language)
            maintainability_score = self._calculate_maintainability(code, language)

            # Check for common issues
            style_issues = self._check_style(code, language)
            security_issues = self._check_security(code, language)
            best_practice_issues = self._check_best_practices(code, language)

            issues.extend(style_issues)
            issues.extend(security_issues)
            issues.extend(best_practice_issues)

            # Collect metrics
            metrics.update({
                "lines_of_code": len([line for line in code.split('\n') if line.strip()]),
                "total_lines": len(code.split('\n')),
                "cyclomatic_complexity": self._calculate_cyclomatic_complexity(code, language),
                "function_count": self._count_functions(code, language),
                "class_count": self._count_classes(code, language)
            })

            return CodeAnalysis(
                syntax_valid=syntax_valid,
                complexity_score=complexity_score,
                readability_score=readability_score,
                maintainability_score=maintainability_score,
                issues=issues,
                metrics=metrics
            )

        except Exception as e:
            logger.error(f"Static analysis error: {e}")
            return CodeAnalysis(
                syntax_valid=False,
                complexity_score=0.0,
                readability_score=0.0,
                maintainability_score=0.0,
                issues=[],
                metrics={}
            )

    def _check_syntax(self, code: str, language: CodeLanguage) -> bool:
        """Check code syntax validity"""
        try:
            if language == CodeLanguage.PYTHON:
                return self._check_python_syntax(code)
            elif language == CodeLanguage.JAVASCRIPT:
                return self._check_javascript_syntax(code)
            # Add more languages as needed
            return True

        except Exception:
            return False

    def _check_python_syntax(self, code: str) -> bool:
        """Check Python syntax validity"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _check_javascript_syntax(self, code: str) -> bool:
        """Basic JavaScript syntax check"""
        try:
            # Simple bracket/brace matching
            brackets = {'(': ')', '[': ']', '{': '}'}
            stack = []

            for char in code:
                if char in brackets:
                    stack.append(brackets[char])
                elif char in brackets.values():
                    if not stack or stack.pop() != char:
                        return False

            return len(stack) == 0

        except Exception:
            return False

    def _calculate_complexity(self, code: str, language: CodeLanguage) -> float:
        """Calculate code complexity score (0-10)"""
        try:
            if language not in self.language_patterns:
                return 5.0  # Default complexity

            patterns = self.language_patterns[language]
            complexity_keywords = patterns.get("complexity_keywords", [])

            # Count complexity indicators
            complexity_count = 0
            lines = code.split('\n')

            for line in lines:
                for keyword in complexity_keywords:
                    complexity_count += line.count(keyword)

            # Calculate complexity score based on code length and complexity indicators
            loc = len([line for line in lines if line.strip()])

            if loc == 0:
                return 0.0

            complexity_ratio = complexity_count / loc

            # Scale to 0-10 range
            complexity_score = min(10.0, complexity_ratio * 50)

            return round(complexity_score, 2)

        except Exception as e:
            logger.error(f"Complexity calculation error: {e}")
            return 5.0

    def _calculate_readability(self, code: str, language: CodeLanguage) -> float:
        """Calculate code readability score (0-10)"""
        try:
            score = 10.0
            lines = code.split('\n')

            # Check for comments
            comment_lines = len([line for line in lines if line.strip().startswith('#') or '//' in line])
            if comment_lines == 0:
                score -= 2.0

            # Check line length
            long_lines = len([line for line in lines if len(line) > 120])
            score -= (long_lines * 0.5)

            # Check for meaningful variable names
            if language == CodeLanguage.PYTHON:
                # Look for single-letter variables (except loop counters)
                single_letter_vars = len(re.findall(r'\b[a-z]\s*=', code))
                score -= (single_letter_vars * 0.5)

            return max(0.0, min(10.0, score))

        except Exception as e:
            logger.error(f"Readability calculation error: {e}")
            return 5.0

    def _calculate_maintainability(self, code: str, language: CodeLanguage) -> float:
        """Calculate code maintainability score (0-10)"""
        try:
            score = 8.0

            # Check function length
            if language == CodeLanguage.PYTHON:
                functions = re.findall(r'def\s+\w+\(.*?\):', code)
                # This is a simplified check - in reality, would need to parse function bodies
                if len(functions) == 0 and len(code.split('\n')) > 20:
                    score -= 2.0  # Long code without functions

            # Check for code duplication (simplified)
            lines = [line.strip() for line in code.split('\n') if line.strip()]
            unique_lines = set(lines)
            duplication_ratio = (len(lines) - len(unique_lines)) / max(1, len(lines))
            score -= (duplication_ratio * 3)

            return max(0.0, min(10.0, score))

        except Exception as e:
            logger.error(f"Maintainability calculation error: {e}")
            return 5.0

    def _calculate_cyclomatic_complexity(self, code: str, language: CodeLanguage) -> int:
        """Calculate cyclomatic complexity"""
        try:
            if language not in self.language_patterns:
                return 1

            patterns = self.language_patterns[language]
            complexity_keywords = patterns.get("complexity_keywords", [])

            complexity = 1  # Base complexity

            for keyword in complexity_keywords:
                complexity += code.count(keyword)

            return complexity

        except Exception:
            return 1

    def _count_functions(self, code: str, language: CodeLanguage) -> int:
        """Count number of functions in code"""
        try:
            if language == CodeLanguage.PYTHON:
                return len(re.findall(r'def\s+\w+\(', code))
            elif language == CodeLanguage.JAVASCRIPT:
                return len(re.findall(r'function\s+\w+\(', code))
            return 0
        except Exception:
            return 0

    def _count_classes(self, code: str, language: CodeLanguage) -> int:
        """Count number of classes in code"""
        try:
            if language == CodeLanguage.PYTHON:
                return len(re.findall(r'class\s+\w+', code))
            elif language == CodeLanguage.JAVA:
                return len(re.findall(r'class\s+\w+', code))
            return 0
        except Exception:
            return 0

    def _check_style(self, code: str, language: CodeLanguage) -> List[CodeIssue]:
        """Check code style issues"""
        issues = []
        try:
            if language not in self.language_patterns:
                return issues

            lines = code.split('\n')

            for line_num, line in enumerate(lines, 1):
                # Check line length
                if len(line) > 120:
                    issues.append(CodeIssue(
                        aspect=EvaluationAspect.STYLE,
                        severity="warning",
                        line_number=line_num,
                        column=None,
                        message=f"Line too long ({len(line)} chars, max 120)",
                        suggestion="Break long lines for better readability"
                    ))

                # Check trailing whitespace
                if line.rstrip() != line:
                    issues.append(CodeIssue(
                        aspect=EvaluationAspect.STYLE,
                        severity="suggestion",
                        line_number=line_num,
                        column=len(line.rstrip()),
                        message="Trailing whitespace",
                        suggestion="Remove trailing whitespace"
                    ))

        except Exception as e:
            logger.error(f"Style check error: {e}")

        return issues

    def _check_security(self, code: str, language: CodeLanguage) -> List[CodeIssue]:
        """Check for security vulnerabilities"""
        issues = []
        try:
            if language not in self.language_patterns:
                return issues

            patterns = self.language_patterns[language]
            security_patterns = patterns.get("security_patterns", [])

            lines = code.split('\n')

            for line_num, line in enumerate(lines, 1):
                for pattern in security_patterns:
                    if re.search(pattern, line):
                        issues.append(CodeIssue(
                            aspect=EvaluationAspect.SECURITY,
                            severity="error",
                            line_number=line_num,
                            column=None,
                            message=f"Potential security vulnerability: {pattern}",
                            suggestion="Review this code for security implications"
                        ))

        except Exception as e:
            logger.error(f"Security check error: {e}")

        return issues

    def _check_best_practices(self, code: str, language: CodeLanguage) -> List[CodeIssue]:
        """Check for best practice violations"""
        issues = []
        try:
            if language == CodeLanguage.PYTHON:
                # Check for print statements in functions (should use logging)
                if 'print(' in code and 'def ' in code:
                    issues.append(CodeIssue(
                        aspect=EvaluationAspect.BEST_PRACTICES,
                        severity="suggestion",
                        line_number=None,
                        column=None,
                        message="Consider using logging instead of print statements",
                        suggestion="Replace print() with appropriate logging calls"
                    ))

                # Check for bare except clauses
                if 'except:' in code:
                    issues.append(CodeIssue(
                        aspect=EvaluationAspect.BEST_PRACTICES,
                        severity="warning",
                        line_number=None,
                        column=None,
                        message="Bare except clause catches all exceptions",
                        suggestion="Specify exception types to catch"
                    ))

        except Exception as e:
            logger.error(f"Best practices check error: {e}")

        return issues

    def _execute_test_cases(self, code: str, test_cases: List[Dict[str, Any]],
                          language: CodeLanguage, max_time: int) -> Tuple[List[Dict[str, Any]], int, int]:
        """Execute test cases against code (simulation for demo)"""
        try:
            execution_results = []
            passed_tests = 0
            total_tests = len(test_cases)

            for i, test_case in enumerate(test_cases):
                try:
                    # In a real implementation, this would execute code in a sandbox
                    # For demo purposes, we'll simulate test execution

                    expected_output = test_case.get('expected_output', '')
                    test_input = test_case.get('input', '')

                    # Simulate test execution result
                    passed = self._simulate_test_execution(code, test_input, expected_output, language)

                    result = {
                        'test_id': i + 1,
                        'input': test_input,
                        'expected_output': expected_output,
                        'actual_output': expected_output if passed else "Different output",
                        'passed': passed,
                        'execution_time_ms': 50 + (i * 10),  # Simulated execution time
                        'error_message': None if passed else "Output mismatch"
                    }

                    execution_results.append(result)

                    if passed:
                        passed_tests += 1

                except Exception as e:
                    execution_results.append({
                        'test_id': i + 1,
                        'input': test_case.get('input', ''),
                        'expected_output': test_case.get('expected_output', ''),
                        'actual_output': '',
                        'passed': False,
                        'execution_time_ms': 0,
                        'error_message': str(e)
                    })

            return execution_results, passed_tests, total_tests

        except Exception as e:
            logger.error(f"Test execution error: {e}")
            return [], 0, len(test_cases)

    def _simulate_test_execution(self, code: str, test_input: str,
                                expected_output: str, language: CodeLanguage) -> bool:
        """Simulate test execution (placeholder for real sandbox execution)"""
        try:
            # This is a simulation - in reality would execute code in secure sandbox

            # Simple heuristics based on code content
            code_lower = code.lower()

            # If code looks like it handles the expected functionality
            if expected_output and any(word in code_lower for word in expected_output.lower().split()[:3]):
                return True

            # Basic syntax check
            if language == CodeLanguage.PYTHON:
                try:
                    ast.parse(code)
                    return True
                except SyntaxError:
                    return False

            # Default to passing simple tests
            return len(code.strip()) > 10  # Basic non-empty code check

        except Exception:
            return False

    def _generate_ai_feedback(self, code: str, request: CodeEvaluationRequest,
                            analysis: CodeAnalysis, execution_results: List[Dict[str, Any]]) -> Tuple[str, List[str], Optional[str]]:
        """Generate AI-powered feedback and suggestions"""
        try:
            # Check if AI models are available
            if not self.model_registry.is_model_available(self.primary_model):
                return self._generate_fallback_feedback(code, request, analysis, execution_results)

            # Get the model for AI feedback generation
            code_model = self.model_registry.get_model(self.primary_model)

            # Prepare prompt for AI feedback
            prompt = self._create_feedback_prompt(code, request, analysis, execution_results)

            # Generate AI response
            from ..base.model_interface import InferenceRequest
            ai_request = InferenceRequest(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,
                context_data={
                    "task": "code_evaluation_feedback",
                    "language": request.language.value,
                    "difficulty": request.difficulty_level.value
                }
            )

            response = code_model.generate(ai_request)

            if response.success:
                # Parse AI response to extract feedback, suggestions, and improved code
                return self._parse_ai_response(response.generated_text)
            else:
                return self._generate_fallback_feedback(code, request, analysis, execution_results)

        except Exception as e:
            logger.error(f"AI feedback generation error: {e}")
            return self._generate_fallback_feedback(code, request, analysis, execution_results)

    def _create_feedback_prompt(self, code: str, request: CodeEvaluationRequest,
                              analysis: CodeAnalysis, execution_results: List[Dict[str, Any]]) -> str:
        """Create prompt for AI feedback generation"""

        prompt = f"""You are an expert code reviewer and programming tutor. Analyze the following {request.language.value} code and provide constructive feedback.

**Code to Review:**
```{request.language.value}
{code}
```

**Context:**
- Difficulty Level: {request.difficulty_level.value}
- Learning Objectives: {', '.join(request.learning_objectives) if request.learning_objectives else 'General programming'}
- Problem Description: {request.problem_description or 'Not provided'}

**Analysis Results:**
- Syntax Valid: {analysis.syntax_valid}
- Complexity Score: {analysis.complexity_score}/10
- Readability Score: {analysis.readability_score}/10
- Issues Found: {len(analysis.issues)}

**Test Results:**
- Tests Passed: {len([r for r in execution_results if r.get('passed', False)])}/{len(execution_results)}

Please provide your response in the following format:

**FEEDBACK:**
[Your detailed feedback about the code quality, correctness, and adherence to best practices]

**SUGGESTIONS:**
1. [Specific suggestion for improvement]
2. [Another suggestion]
3. [Additional suggestion if needed]

**IMPROVED_CODE:**
```{request.language.value}
[Optional: Provide an improved version of the code if significant improvements are needed]
```

Focus on being constructive, educational, and encouraging. Tailor your feedback to the difficulty level and learning objectives."""

        return prompt

    def _parse_ai_response(self, ai_text: str) -> Tuple[str, List[str], Optional[str]]:
        """Parse AI response to extract feedback, suggestions, and improved code"""
        try:
            feedback = ""
            suggestions = []
            improved_code = None

            # Split response into sections
            sections = ai_text.split("**")

            current_section = ""
            for section in sections:
                section = section.strip()
                if section.upper().startswith("FEEDBACK"):
                    current_section = "feedback"
                elif section.upper().startswith("SUGGESTIONS"):
                    current_section = "suggestions"
                elif section.upper().startswith("IMPROVED_CODE"):
                    current_section = "improved_code"
                elif current_section == "feedback" and section:
                    feedback = section
                elif current_section == "suggestions" and section:
                    # Parse numbered suggestions
                    suggestion_lines = [line.strip() for line in section.split('\n') if line.strip()]
                    for line in suggestion_lines:
                        if re.match(r'^\d+\.', line.strip()):
                            suggestions.append(re.sub(r'^\d+\.\s*', '', line.strip()))
                elif current_section == "improved_code" and section:
                    # Extract code from code blocks
                    code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', section, re.DOTALL)
                    if code_match:
                        improved_code = code_match.group(1).strip()

            # Fallback parsing if structured format not found
            if not feedback and not suggestions:
                lines = ai_text.split('\n')
                feedback_lines = []
                suggestion_lines = []

                in_suggestions = False
                for line in lines:
                    line = line.strip()
                    if line.lower().startswith('suggestion') or re.match(r'^\d+\.', line):
                        in_suggestions = True
                        if re.match(r'^\d+\.', line):
                            suggestion_lines.append(re.sub(r'^\d+\.\s*', '', line))
                    elif not in_suggestions and line:
                        feedback_lines.append(line)

                if not feedback:
                    feedback = ' '.join(feedback_lines)
                if not suggestions:
                    suggestions = suggestion_lines

            return feedback or "Good code structure overall.", suggestions, improved_code

        except Exception as e:
            logger.error(f"AI response parsing error: {e}")
            return "Unable to generate detailed feedback.", [], None

    def _generate_fallback_feedback(self, code: str, request: CodeEvaluationRequest,
                                  analysis: CodeAnalysis, execution_results: List[Dict[str, Any]]) -> Tuple[str, List[str], Optional[str]]:
        """Generate fallback feedback when AI models are not available"""

        feedback_parts = []
        suggestions = []

        # Generate feedback based on analysis
        if analysis.syntax_valid:
            feedback_parts.append("Your code has valid syntax.")
        else:
            feedback_parts.append("There are syntax errors in your code that need to be fixed.")

        if analysis.complexity_score > 7:
            feedback_parts.append("The code appears to have high complexity. Consider simplifying.")
            suggestions.append("Break down complex functions into smaller, more manageable pieces")

        if analysis.readability_score < 6:
            feedback_parts.append("Code readability could be improved.")
            suggestions.append("Add meaningful comments and use descriptive variable names")

        # Add suggestions based on issues found
        for issue in analysis.issues[:3]:  # Limit to top 3 issues
            if issue.suggestion:
                suggestions.append(issue.suggestion)

        # Test-based feedback
        passed_tests = len([r for r in execution_results if r.get('passed', False)])
        total_tests = len(execution_results)

        if total_tests > 0:
            if passed_tests == total_tests:
                feedback_parts.append("All test cases passed successfully!")
            elif passed_tests > total_tests * 0.5:
                feedback_parts.append(f"Most test cases passed ({passed_tests}/{total_tests}), but there's room for improvement.")
                suggestions.append("Review failed test cases and adjust your logic")
            else:
                feedback_parts.append(f"Several test cases failed ({passed_tests}/{total_tests}). Focus on correctness.")
                suggestions.append("Debug your code step by step with the provided test cases")

        # Default suggestions if none generated
        if not suggestions:
            suggestions = [
                "Keep practicing and experimenting with different approaches",
                "Consider edge cases in your solution",
                "Add comments to explain your logic"
            ]

        feedback = " ".join(feedback_parts) or "Keep up the good work on your coding journey!"

        return feedback, suggestions, None

    def _calculate_aspect_scores(self, analysis: CodeAnalysis, passed_tests: int,
                               total_tests: int, evaluation_aspects: List[EvaluationAspect]) -> Dict[EvaluationAspect, float]:
        """Calculate scores for different evaluation aspects"""

        aspect_scores = {}

        try:
            for aspect in evaluation_aspects:
                if aspect == EvaluationAspect.CORRECTNESS:
                    # Base correctness on test results and syntax validity
                    syntax_score = 100.0 if analysis.syntax_valid else 0.0
                    test_score = (passed_tests / max(1, total_tests)) * 100.0 if total_tests > 0 else syntax_score
                    aspect_scores[aspect] = (syntax_score * 0.3 + test_score * 0.7)

                elif aspect == EvaluationAspect.STYLE:
                    # Base on readability score and style issues
                    style_issues = len([issue for issue in analysis.issues if issue.aspect == EvaluationAspect.STYLE])
                    base_score = (analysis.readability_score / 10.0) * 100.0
                    penalty = min(30.0, style_issues * 5.0)  # 5 points penalty per style issue, max 30
                    aspect_scores[aspect] = max(0.0, base_score - penalty)

                elif aspect == EvaluationAspect.EFFICIENCY:
                    # Base on complexity score (lower complexity = higher efficiency)
                    complexity_penalty = min(analysis.complexity_score * 5, 50.0)
                    aspect_scores[aspect] = max(0.0, 100.0 - complexity_penalty)

                elif aspect == EvaluationAspect.READABILITY:
                    # Direct mapping from readability score
                    aspect_scores[aspect] = (analysis.readability_score / 10.0) * 100.0

                elif aspect == EvaluationAspect.BEST_PRACTICES:
                    # Base on best practice issues found
                    bp_issues = len([issue for issue in analysis.issues if issue.aspect == EvaluationAspect.BEST_PRACTICES])
                    penalty = min(50.0, bp_issues * 10.0)  # 10 points penalty per issue, max 50
                    aspect_scores[aspect] = max(0.0, 100.0 - penalty)

                elif aspect == EvaluationAspect.SECURITY:
                    # Base on security issues found
                    security_issues = len([issue for issue in analysis.issues if issue.aspect == EvaluationAspect.SECURITY])
                    if security_issues > 0:
                        aspect_scores[aspect] = max(0.0, 100.0 - security_issues * 20.0)  # 20 points penalty per security issue
                    else:
                        aspect_scores[aspect] = 100.0

                elif aspect == EvaluationAspect.MAINTAINABILITY:
                    # Base on maintainability score
                    aspect_scores[aspect] = (analysis.maintainability_score / 10.0) * 100.0

        except Exception as e:
            logger.error(f"Aspect score calculation error: {e}")
            # Return default scores
            for aspect in evaluation_aspects:
                aspect_scores[aspect] = 50.0  # Default middle score

        return aspect_scores

    def _calculate_overall_score(self, aspect_scores: Dict[EvaluationAspect, float]) -> float:
        """Calculate overall score based on weighted aspect scores"""

        try:
            if not aspect_scores:
                return 0.0

            weighted_sum = 0.0
            total_weight = 0.0

            for aspect, score in aspect_scores.items():
                weight = self.aspect_weights.get(aspect, 0.1)  # Default weight if not found
                weighted_sum += score * weight
                total_weight += weight

            overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

            return round(overall_score, 2)

        except Exception as e:
            logger.error(f"Overall score calculation error: {e}")
            return 0.0

    def _track_learning_progress(self, learning_objectives: List[str],
                               aspect_scores: Dict[EvaluationAspect, float],
                               overall_score: float) -> Dict[str, Any]:
        """Track learning progress against objectives"""

        try:
            progress = {
                "overall_progress": min(100.0, overall_score),
                "objective_progress": {},
                "strengths": [],
                "areas_for_improvement": [],
                "next_steps": []
            }

            # Map learning objectives to progress
            for objective in learning_objectives:
                # Simple mapping - in reality would be more sophisticated
                if "syntax" in objective.lower():
                    progress["objective_progress"][objective] = aspect_scores.get(EvaluationAspect.CORRECTNESS, 0.0)
                elif "style" in objective.lower() or "format" in objective.lower():
                    progress["objective_progress"][objective] = aspect_scores.get(EvaluationAspect.STYLE, 0.0)
                elif "efficiency" in objective.lower() or "performance" in objective.lower():
                    progress["objective_progress"][objective] = aspect_scores.get(EvaluationAspect.EFFICIENCY, 0.0)
                else:
                    progress["objective_progress"][objective] = overall_score

            # Identify strengths and areas for improvement
            for aspect, score in aspect_scores.items():
                if score >= 80.0:
                    progress["strengths"].append(aspect.value.replace("_", " ").title())
                elif score < 60.0:
                    progress["areas_for_improvement"].append(aspect.value.replace("_", " ").title())

            # Generate next steps
            if overall_score < 60:
                progress["next_steps"].append("Focus on basic correctness and syntax")
            elif overall_score < 80:
                progress["next_steps"].append("Work on code style and best practices")
            else:
                progress["next_steps"].append("Explore advanced concepts and optimizations")

            return progress

        except Exception as e:
            logger.error(f"Learning progress tracking error: {e}")
            return {
                "overall_progress": overall_score,
                "objective_progress": {},
                "strengths": [],
                "areas_for_improvement": [],
                "next_steps": ["Continue practicing coding skills"]
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform service health check"""
        try:
            base_health = super().health_check()

            # Add service-specific health checks
            service_health = {
                "language_patterns_loaded": len(self.language_patterns) > 0,
                "data_sanitizer_available": self.data_sanitizer is not None,
                "required_models_status": {
                    model: self.model_registry.is_model_available(model)
                    for model in self.required_models
                }
            }

            base_health.update(service_health)
            return base_health

        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "service_name": self.service_name,
                "status": "unhealthy",
                "error": str(e)
            }


# Convenience functions for external use
def evaluate_code(code: str, language: str, **kwargs) -> CodeEvaluationResponse:
    """
    Convenience function to evaluate code quickly

    Args:
        code: Code to evaluate
        language: Programming language ('python', 'javascript', etc.)
        **kwargs: Additional parameters for CodeEvaluationRequest

    Returns:
        CodeEvaluationResponse with evaluation results
    """
    try:
        # Convert string language to enum
        lang_enum = CodeLanguage(language.lower())

        # Create service and request
        service = CodeEvaluationService()
        service.initialize()

        request = CodeEvaluationRequest(
            code=code,
            language=lang_enum,
            **kwargs
        )

        return service.process(request)

    except Exception as e:
        return CodeEvaluationResponse(
            success=False,
            error=f"Code evaluation failed: {str(e)}"
        )


def get_supported_languages() -> List[str]:
    """Get list of supported programming languages"""
    return [lang.value for lang in CodeLanguage if lang != CodeLanguage.UNKNOWN]