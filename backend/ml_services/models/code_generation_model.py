"""
backend/ml_services/models/code_generation_model.py
Code generation model implementation optimized for programming tasks
Supports CodeLlama, StarCoder, and other code-focused models
RELEVANT FILES: base/model_interface.py, text_generation_model.py, configs/model_configs.py
"""

import re
from typing import Dict, Any, List
from .text_generation_model import TextGenerationModel
from ..base.model_interface import InferenceRequest, InferenceResponse
from ..base.exceptions import ValidationError


class CodeGenerationModel(TextGenerationModel):
    """
    Specialized text generation model for code generation tasks.

    Extends TextGenerationModel with code-specific features:
    - Code-optimized prompting
    - Language-specific formatting
    - Code quality validation
    - Programming context awareness
    """

    def __init__(self, model_name: str, model_config: Dict[str, Any] = None):
        super().__init__(model_name, model_config)

        # Code-specific configuration
        self.supported_languages = self.model_config.get('supported_languages', [])
        self.code_capabilities = [
            cap for cap in self.model_config.get('capabilities', [])
            if 'code' in cap or 'programming' in cap
        ]

    def generate(self, request: InferenceRequest) -> InferenceResponse:
        """
        Generate code with specialized handling.

        Args:
            request: Inference request with code generation context

        Returns:
            Generated code response with enhanced metadata
        """
        # Enhanced validation for code tasks
        self.validate_code_request(request)

        # Enhance the request for code generation
        enhanced_request = self._enhance_code_request(request)

        # Generate using parent class
        response = super().generate(enhanced_request)

        # Post-process code output
        response.generated_text = self._post_process_code(
            response.generated_text,
            enhanced_request
        )

        # Add code-specific metadata
        response.metadata.update(self._analyze_generated_code(response.generated_text))

        return response

    def validate_code_request(self, request: InferenceRequest) -> None:
        """Validate code generation request."""
        # Call parent validation
        super().validate_input(request)

        # Code-specific validation
        if hasattr(request, 'language') and request.language:
            if request.language not in self.supported_languages:
                raise ValidationError(
                    "language",
                    request.language,
                    f"Language not supported. Available: {', '.join(self.supported_languages)}"
                )

    def _enhance_code_request(self, request: InferenceRequest) -> InferenceRequest:
        """Enhance the request with code-specific prompting."""
        enhanced_prompt = self._create_code_prompt(request)

        # Create enhanced request
        enhanced_request = InferenceRequest(
            prompt=enhanced_prompt,
            max_length=request.max_length or 256,  # Shorter for code
            temperature=request.temperature or 0.2,  # Lower for more deterministic code
            top_p=request.top_p or 0.95,
            top_k=request.top_k,
            stop_sequences=request.stop_sequences or self._get_code_stop_sequences(),
            context_length=request.context_length,
            user_id=request.user_id,
            request_id=request.request_id
        )

        return enhanced_request

    def _create_code_prompt(self, request: InferenceRequest) -> str:
        """Create optimized prompt for code generation."""
        prompt = request.prompt

        # Detect if it's already a well-formatted code prompt
        if self._is_code_prompt_formatted(prompt):
            return prompt

        # Extract language hint from context or prompt
        language = self._detect_language(prompt)

        # Create structured code prompt
        if language:
            # Language-specific prompting
            if language == "python":
                prompt = f"# Python code\n# Task: {prompt}\n\n```python\n"
            elif language == "javascript":
                prompt = f"// JavaScript code\n// Task: {prompt}\n\n```javascript\n"
            elif language in ["java", "cpp", "c"]:
                prompt = f"// {language.upper()} code\n// Task: {prompt}\n\n```{language}\n"
            else:
                prompt = f"# {language} code\n# Task: {prompt}\n\n```{language}\n"
        else:
            # Generic code prompt
            prompt = f"# Code to solve the following task:\n# {prompt}\n\n```\n"

        return prompt

    def _detect_language(self, prompt: str) -> str:
        """Detect programming language from the prompt."""
        prompt_lower = prompt.lower()

        # Language keywords mapping
        language_keywords = {
            "python": ["python", "def ", "import ", "class ", ".py", "pip", "django", "flask"],
            "javascript": ["javascript", "js", "function", "const ", "let ", "var ", "node", "react"],
            "java": ["java", "class ", "public static", "import java", ".java", "spring"],
            "cpp": ["c++", "cpp", "#include", "std::", "iostream", "vector"],
            "c": ["c language", "#include <", "int main", "printf", "scanf"],
            "go": ["golang", "go", "func ", "package ", "import ", ".go"],
            "rust": ["rust", "fn ", "let mut", "cargo", ".rs", "struct"],
            "php": ["php", "<?php", "$", "echo ", "class ", ".php"],
            "ruby": ["ruby", "def ", "class ", "end", ".rb", "rails"],
            "swift": ["swift", "func ", "var ", "let ", ".swift", "ios"],
            "kotlin": ["kotlin", "fun ", "class ", "val ", ".kt", "android"],
            "typescript": ["typescript", "ts", "interface ", "type ", ".ts", "angular"],
        }

        # Count matches for each language
        language_scores = {}
        for language, keywords in language_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                language_scores[language] = score

        # Return the language with the highest score
        if language_scores:
            return max(language_scores.keys(), key=language_scores.get)

        return None

    def _is_code_prompt_formatted(self, prompt: str) -> bool:
        """Check if the prompt is already formatted for code generation."""
        code_indicators = [
            "```", "def ", "function", "class ", "import ", "#include",
            "public class", "fn ", "func ", "let ", "const ", "var "
        ]
        return any(indicator in prompt for indicator in code_indicators)

    def _get_code_stop_sequences(self) -> List[str]:
        """Get stop sequences appropriate for code generation."""
        return [
            "```",
            "\n\n\n",  # Multiple newlines
            "# End",
            "// End",
            "/*",
            "*/",
            "<|endoftext|>",
            "Human:",
            "Assistant:",
        ]

    def _post_process_code(self, code: str, request: InferenceRequest) -> str:
        """Post-process generated code for quality and formatting."""
        # Remove markdown code block markers
        code = re.sub(r'^```\w*\n', '', code)
        code = re.sub(r'\n```$', '', code)
        code = code.strip()

        # Remove common prompt artifacts
        artifacts = [
            "# Code to solve the following task:",
            "// Code to solve the following task:",
            "# Task:",
            "// Task:",
        ]
        for artifact in artifacts:
            code = code.replace(artifact, "").strip()

        # Clean up excessive newlines
        code = re.sub(r'\n{3,}', '\n\n', code)

        # Basic syntax cleanup
        code = self._basic_syntax_cleanup(code)

        return code

    def _basic_syntax_cleanup(self, code: str) -> str:
        """Perform basic syntax cleanup on generated code."""
        lines = code.split('\n')
        cleaned_lines = []

        for line in lines:
            # Remove excessive spaces
            line = re.sub(r'  +', '  ', line)  # Replace multiple spaces with double space

            # Remove trailing whitespace
            line = line.rstrip()

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _analyze_generated_code(self, code: str) -> Dict[str, Any]:
        """Analyze the generated code and provide metadata."""
        analysis = {
            'code_lines': len([line for line in code.split('\n') if line.strip()]),
            'total_lines': len(code.split('\n')),
            'estimated_language': self._detect_language_from_code(code),
            'has_functions': self._has_functions(code),
            'has_classes': self._has_classes(code),
            'has_imports': self._has_imports(code),
            'complexity_estimate': self._estimate_complexity(code),
        }

        return analysis

    def _detect_language_from_code(self, code: str) -> str:
        """Detect programming language from generated code."""
        # Language-specific syntax patterns
        patterns = {
            "python": [r'def\s+\w+\(', r'import\s+\w+', r'class\s+\w+:', r'if\s+__name__\s*=='],
            "javascript": [r'function\s+\w+\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'=>\s*{'],
            "java": [r'public\s+class\s+\w+', r'public\s+static\s+void\s+main', r'import\s+java\.'],
            "cpp": [r'#include\s*<', r'std::', r'int\s+main\s*\(', r'cout\s*<<'],
            "c": [r'#include\s*<.*\.h>', r'int\s+main\s*\(', r'printf\s*\(', r'scanf\s*\('],
            "go": [r'package\s+\w+', r'func\s+\w+\(', r'import\s*\(', r'fmt\.Print'],
            "rust": [r'fn\s+\w+\(', r'let\s+mut\s+', r'use\s+std::', r'println!'],
        }

        for language, lang_patterns in patterns.items():
            matches = sum(1 for pattern in lang_patterns if re.search(pattern, code))
            if matches >= 2:  # Require at least 2 pattern matches
                return language

        return "unknown"

    def _has_functions(self, code: str) -> bool:
        """Check if code contains function definitions."""
        function_patterns = [
            r'def\s+\w+\(',      # Python
            r'function\s+\w+\(', # JavaScript
            r'func\s+\w+\(',     # Go
            r'fn\s+\w+\(',       # Rust
            r'\w+\s+\w+\s*\(',   # C/C++/Java methods
        ]
        return any(re.search(pattern, code) for pattern in function_patterns)

    def _has_classes(self, code: str) -> bool:
        """Check if code contains class definitions."""
        class_patterns = [
            r'class\s+\w+',        # Python, Java, C++
            r'interface\s+\w+',    # Java, TypeScript
            r'struct\s+\w+',       # C, C++, Go, Rust
        ]
        return any(re.search(pattern, code) for pattern in class_patterns)

    def _has_imports(self, code: str) -> bool:
        """Check if code contains import statements."""
        import_patterns = [
            r'import\s+',          # Python, Java, JavaScript
            r'from\s+\w+\s+import', # Python
            r'#include\s*<',       # C/C++
            r'use\s+',             # Rust
            r'require\s*\(',       # JavaScript/Node.js
        ]
        return any(re.search(pattern, code) for pattern in import_patterns)

    def _estimate_complexity(self, code: str) -> str:
        """Estimate code complexity based on various factors."""
        lines = len([line for line in code.split('\n') if line.strip()])

        # Count complexity indicators
        complexity_indicators = [
            r'if\s+',              # Conditional statements
            r'for\s+',             # Loops
            r'while\s+',           # Loops
            r'try\s*:',            # Exception handling
            r'except\s*:',         # Exception handling
            r'catch\s*\(',         # Exception handling
            r'switch\s*\(',        # Switch statements
            r'class\s+',           # Class definitions
            r'function\s+',        # Function definitions
            r'def\s+',             # Function definitions
        ]

        complexity_count = sum(
            len(re.findall(pattern, code))
            for pattern in complexity_indicators
        )

        # Simple complexity estimation
        if lines < 10 and complexity_count < 3:
            return "low"
        elif lines < 50 and complexity_count < 10:
            return "medium"
        else:
            return "high"

    def get_capabilities(self) -> List[str]:
        """Get code-specific capabilities."""
        return self.code_capabilities + super().get_capabilities()