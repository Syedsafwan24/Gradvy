"""
backend/ml_services/base/model_interface.py
Abstract base class defining the interface for all ML models
Ensures consistent behavior across different model implementations
RELEVANT FILES: base/exceptions.py, models/, services/
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime
from dataclasses import dataclass

from .exceptions import ModelLoadError, InferenceError, ValidationError


@dataclass
class ModelMetadata:
    """Metadata about a loaded model"""
    name: str
    version: str
    model_type: str  # 'text_generation', 'code_generation', 'embedding', etc.
    size_mb: float
    capabilities: List[str]
    loaded_at: datetime
    memory_usage_mb: float = 0.0
    inference_count: int = 0
    last_inference: Optional[datetime] = None


@dataclass
class InferenceRequest:
    """Structured request for model inference"""
    prompt: str
    max_length: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    context_length: Optional[int] = None
    user_id: Optional[str] = None  # For privacy tracking
    request_id: Optional[str] = None  # For request tracking


@dataclass
class InferenceResponse:
    """Structured response from model inference"""
    generated_text: str
    confidence_score: float
    processing_time_ms: float
    tokens_generated: int
    model_name: str
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseMLModel(ABC):
    """
    Abstract base class for all ML models in the Gradvy platform.

    This class defines the interface that all ML models must implement,
    ensuring consistency across different model types and implementations.

    Key Design Principles:
    1. **Lazy Loading**: Models are loaded only when first needed
    2. **Resource Management**: Automatic memory and GPU resource tracking
    3. **Error Handling**: Comprehensive error handling with detailed context
    4. **Privacy**: Built-in data sanitization and audit logging
    5. **Monitoring**: Performance metrics and health checks

    Usage Example:
        model = CodeGenerationModel("codellama-7b")
        response = model.generate(InferenceRequest(
            prompt="Write a Python function to calculate fibonacci",
            max_length=200
        ))
    """

    def __init__(self, model_name: str, model_config: Dict[str, Any] = None):
        """
        Initialize the ML model with configuration

        Args:
            model_name: Name of the model to load
            model_config: Optional configuration overrides
        """
        self.model_name = model_name
        self.model_config = model_config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{model_name}")

        # Model state
        self._model = None
        self._tokenizer = None
        self._is_loaded = False
        self._metadata: Optional[ModelMetadata] = None

        # Performance tracking
        self._load_time_ms = 0.0
        self._total_inferences = 0
        self._total_inference_time_ms = 0.0

    @property
    def is_loaded(self) -> bool:
        """Check if the model is currently loaded in memory"""
        return self._is_loaded

    @property
    def metadata(self) -> Optional[ModelMetadata]:
        """Get model metadata"""
        return self._metadata

    @abstractmethod
    def load(self) -> None:
        """
        Load the model into memory.

        This method should:
        1. Download model files if not present
        2. Load model and tokenizer
        3. Initialize any required components
        4. Update metadata
        5. Set _is_loaded = True

        Raises:
            ModelLoadError: If model loading fails
        """
        pass

    @abstractmethod
    def unload(self) -> None:
        """
        Unload the model from memory to free resources.

        This method should:
        1. Clear model from memory
        2. Clear tokenizer from memory
        3. Free any GPU memory
        4. Set _is_loaded = False
        """
        pass

    @abstractmethod
    def generate(self, request: InferenceRequest) -> InferenceResponse:
        """
        Generate text using the model.

        Args:
            request: Structured inference request

        Returns:
            InferenceResponse with generated text and metadata

        Raises:
            InferenceError: If generation fails
            ValidationError: If input validation fails
        """
        pass

    @abstractmethod
    def validate_input(self, request: InferenceRequest) -> None:
        """
        Validate input request before processing.

        Args:
            request: Request to validate

        Raises:
            ValidationError: If validation fails
        """
        pass

    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities supported by this model.

        Returns:
            List of capability strings
        """
        if self._metadata:
            return self._metadata.capabilities
        return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Get performance and usage statistics.

        Returns:
            Dictionary with model statistics
        """
        avg_inference_time = 0.0
        if self._total_inferences > 0:
            avg_inference_time = self._total_inference_time_ms / self._total_inferences

        return {
            'model_name': self.model_name,
            'is_loaded': self.is_loaded,
            'total_inferences': self._total_inferences,
            'avg_inference_time_ms': avg_inference_time,
            'load_time_ms': self._load_time_ms,
            'memory_usage_mb': self._metadata.memory_usage_mb if self._metadata else 0.0,
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the model.

        Returns:
            Dictionary with health status
        """
        try:
            # Basic health check with simple inference
            if not self.is_loaded:
                return {
                    'status': 'unloaded',
                    'healthy': False,
                    'message': 'Model not loaded'
                }

            # Try a simple inference to check if model is working
            test_request = InferenceRequest(
                prompt="Test",
                max_length=5,
                temperature=0.1
            )

            start_time = datetime.now()
            response = self.generate(test_request)
            health_check_time = (datetime.now() - start_time).total_seconds() * 1000

            return {
                'status': 'healthy',
                'healthy': True,
                'response_time_ms': health_check_time,
                'last_check': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'healthy': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

    def _ensure_loaded(self) -> None:
        """Ensure model is loaded, load if necessary"""
        if not self.is_loaded:
            self.logger.info(f"Loading model {self.model_name}")
            self.load()

    def _log_inference(self, request: InferenceRequest, response: InferenceResponse) -> None:
        """Log inference for monitoring and privacy compliance"""
        self._total_inferences += 1
        self._total_inference_time_ms += response.processing_time_ms

        if self._metadata:
            self._metadata.inference_count = self._total_inferences
            self._metadata.last_inference = datetime.now()

        # Log inference (be careful with privacy)
        self.logger.info(
            f"Inference completed - Model: {self.model_name}, "
            f"Tokens: {response.tokens_generated}, "
            f"Time: {response.processing_time_ms:.2f}ms, "
            f"User: {request.user_id or 'anonymous'}"
        )

    def __str__(self) -> str:
        status = "loaded" if self.is_loaded else "unloaded"
        return f"{self.__class__.__name__}({self.model_name}, {status})"

    def __repr__(self) -> str:
        return self.__str__()