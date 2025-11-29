"""
backend/ml_services/models/api_text_generation_model.py
API-based text generation model using OpenAI-compatible APIs
Supports: OpenAI, Groq, Together AI, and other OpenAI-compatible endpoints
RELEVANT FILES: base/model_interface.py, base/exceptions.py, configs/model_configs.py
"""

import time
from datetime import datetime
from openai import OpenAI
from django.conf import settings

from ..base.model_interface import (
    BaseMLModel, InferenceRequest, InferenceResponse, ModelMetadata
)
from ..base.exceptions import ModelLoadError, InferenceError, ValidationError
from ..utils.external_api_logger import log_external_api_call


class APITextGenerationModel(BaseMLModel):
    """
    API-based text generation using OpenAI-compatible endpoints.

    This model class provides a unified interface for calling external ML APIs
    (OpenAI, Groq, Together AI) instead of loading models locally.

    Benefits:
    - No local model downloads
    - No GPU requirements
    - Faster initialization
    - Better model quality
    - Easy provider switching
    """

    def load(self) -> None:
        """
        Validate API configuration and initialize client.

        Raises:
            ModelLoadError: If API key or configuration is invalid
        """
        api_key = getattr(settings, 'ML_API_KEY', None)
        if not api_key:
            raise ModelLoadError("ML_API_KEY not configured in Django settings")

        api_base = getattr(settings, 'ML_API_BASE_URL', 'https://api.openai.com/v1')

        # Initialize OpenAI client (works with Groq, Together AI, etc.)
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self._is_loaded = True

        # Create metadata
        self._metadata = ModelMetadata(
            name=self.model_name,
            version="api-based",
            model_type="text_generation",
            size_mb=0.0,  # No local storage
            capabilities=["learning_path_generation", "text_generation"],
            loaded_at=datetime.now(),
            memory_usage_mb=0.1  # Minimal
        )

        self.logger.info(f"API model {self.model_name} initialized with {api_base}")

    def unload(self) -> None:
        """
        Unload the model. For API models, this just resets the loaded flag.
        """
        self._is_loaded = False
        self._metadata = None
        self.logger.info(f"API model {self.model_name} unloaded")

    @log_external_api_call(
        api_name="Groq LLM API",
        include_tokens=True,  # Track token usage for cost monitoring
        sanitize_auth=True,  # Sanitize API keys in logs
        truncate_response_at=2000  # Truncate long AI-generated responses
    )
    def generate(self, request: InferenceRequest) -> InferenceResponse:
        """
        Generate text using the external API.

        Args:
            request: InferenceRequest with prompt and generation parameters

        Returns:
            InferenceResponse with generated text and metadata

        Raises:
            InferenceError: If API call fails
        """
        self._ensure_loaded()
        start_time = time.time()

        try:
            # Get model name from config or settings
            api_model_name = self.model_config.get('api_model_name') or \
                            getattr(settings, 'ML_API_MODEL', 'gpt-3.5-turbo')

            # Call API with OpenAI-compatible format
            response = self.client.chat.completions.create(
                model=api_model_name,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_length or 1000,
                temperature=request.temperature or 0.7,
                top_p=request.top_p or 0.9
            )

            processing_time = (time.time() - start_time) * 1000
            generated_text = response.choices[0].message.content
            tokens_generated = response.usage.completion_tokens

            # Create inference response
            inference_response = InferenceResponse(
                generated_text=generated_text,
                confidence_score=0.9,  # APIs don't provide confidence scores
                processing_time_ms=processing_time,
                tokens_generated=tokens_generated,
                model_name=self.model_name,
                request_id=request.request_id,
                metadata={
                    'api_model': api_model_name,
                    'total_tokens': response.usage.total_tokens,
                    'prompt_tokens': response.usage.prompt_tokens
                }
            )

            # Log inference
            self._log_inference(request, inference_response)

            return inference_response

        except Exception as e:
            self.logger.error(f"API inference failed: {e}")
            raise InferenceError(f"API inference failed: {e}")

    def validate_input(self, request: InferenceRequest) -> None:
        """
        Validate input request.

        Args:
            request: Request to validate

        Raises:
            ValidationError: If input is invalid
        """
        if not request.prompt:
            raise ValidationError("prompt", request.prompt, "Prompt cannot be empty")

        if request.prompt and len(request.prompt) > 32000:
            raise ValidationError(
                "prompt",
                f"length={len(request.prompt)}",
                "Prompt too long (max 32000 chars)"
            )
