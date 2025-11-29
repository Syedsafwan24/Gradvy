"""
backend/ml_services/models/text_generation_model.py
Text generation model implementation using HuggingFace transformers
Supports models like Mistral-7B, Phi-3, and other instruction-following models
RELEVANT FILES: base/model_interface.py, configs/model_configs.py, utils/model_registry.py
"""

import os
import time
import torch
from typing import Dict, Any, Optional
from datetime import datetime
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    GenerationConfig
)

# Conditional import for GPU-only quantization support
# bitsandbytes requires NVIDIA GPU and won't work on CPU-only systems
try:
    from transformers import BitsAndBytesConfig
    QUANTIZATION_AVAILABLE = True
except ImportError:
    # bitsandbytes not installed (CPU-only setup)
    # Quantization will be disabled, models will run in float16
    BitsAndBytesConfig = None
    QUANTIZATION_AVAILABLE = False
import gc

from ..base.model_interface import (
    BaseMLModel, ModelMetadata, InferenceRequest, InferenceResponse
)
from ..base.exceptions import ModelLoadError, InferenceError, ValidationError


class TextGenerationModel(BaseMLModel):
    """
    Text generation model using HuggingFace transformers.

    Supports instruction-following models like:
    - Mistral-7B-Instruct
    - Phi-3-Mini
    - Any compatible HuggingFace model

    Features:
    - Automatic quantization for memory efficiency
    - GPU/CPU fallback
    - Optimized generation parameters
    - Privacy-safe inference logging
    """

    def __init__(self, model_name: str, model_config: Dict[str, Any] = None):
        super().__init__(model_name, model_config)

        # Model-specific attributes
        self._model = None
        self._tokenizer = None
        self._generation_config = None

        # Configuration
        self.huggingface_id = self.model_config.get('huggingface_id')
        self.local_path = self.model_config.get('local_path')
        self.max_context_length = self.model_config.get('max_context_length', 4096)

        # Quantization config
        self.quantization_config = self.model_config.get('quantization', {})
        self.use_quantization = self.quantization_config.get('enabled', False)

        # Generation defaults
        self.generation_defaults = self.model_config.get('generation_defaults', {})

        # Device management
        self.device = None
        self.use_gpu = torch.cuda.is_available()

    def load(self) -> None:
        """Load the model and tokenizer from HuggingFace or local storage."""
        try:
            start_time = time.time()
            self.logger.info(f"Loading text generation model: {self.model_name}")

            # Determine device
            self.device = "cuda" if self.use_gpu else "cpu"
            self.logger.info(f"Using device: {self.device}")

            # Load tokenizer first (lighter weight)
            self._load_tokenizer()

            # Load model with appropriate configuration
            self._load_model()

            # Create generation configuration
            self._setup_generation_config()

            # Create metadata
            load_time_ms = (time.time() - start_time) * 1000
            self._load_time_ms = load_time_ms

            self._metadata = ModelMetadata(
                name=self.model_name,
                version="1.0.0",
                model_type="text_generation",
                size_mb=self.model_config.get('size_gb', 0) * 1024,
                capabilities=self.model_config.get('capabilities', []),
                loaded_at=datetime.now(),
                memory_usage_mb=self._estimate_memory_usage()
            )

            self._is_loaded = True
            self.logger.info(
                f"Model {self.model_name} loaded successfully in {load_time_ms:.0f}ms, "
                f"Device: {self.device}, Memory: {self._metadata.memory_usage_mb:.0f}MB"
            )

        except Exception as e:
            self.logger.error(f"Failed to load model {self.model_name}: {e}")
            self._cleanup_on_failure()
            raise ModelLoadError(self.model_name, str(e))

    def _load_tokenizer(self) -> None:
        """Load the tokenizer."""
        try:
            # Try local path first, fallback to HuggingFace
            model_path = self.local_path if os.path.exists(self.local_path) else self.huggingface_id

            self.logger.info(f"Loading tokenizer from: {model_path}")

            self._tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                **self.model_config.get('download_config', {})
            )

            # Ensure we have a pad token
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token

        except Exception as e:
            raise ModelLoadError(self.model_name, f"Failed to load tokenizer: {e}")

    def _load_model(self) -> None:
        """Load the main model."""
        try:
            # Try local path first, fallback to HuggingFace
            model_path = self.local_path if os.path.exists(self.local_path) else self.huggingface_id

            self.logger.info(f"Loading model from: {model_path}")

            # Setup quantization if enabled, GPU available, AND bitsandbytes installed
            quantization_config = None
            if self.use_quantization and self.use_gpu and QUANTIZATION_AVAILABLE:
                quantization_config = self._create_quantization_config()
                self.logger.info(f"Using {self.quantization_config.get('bits', 4)}-bit quantization")
            elif self.use_quantization and self.use_gpu and not QUANTIZATION_AVAILABLE:
                self.logger.warning(
                    "Quantization requested but bitsandbytes not available. "
                    "Install GPU dependencies: pip install -r requirements-ml-gpu.txt"
                )
            elif self.use_quantization and not self.use_gpu:
                self.logger.info("Quantization disabled on CPU (running in float16)")

            # Load model
            download_config = self.model_config.get('download_config', {})

            self._model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=quantization_config,
                torch_dtype=getattr(torch, download_config.get('torch_dtype', 'float16')),
                device_map="auto" if self.use_gpu else None,
                trust_remote_code=True,
                **{k: v for k, v in download_config.items() if k != 'torch_dtype'}
            )

            # Move to device if not using device_map
            if not self.use_gpu or quantization_config is None:
                self._model = self._model.to(self.device)

        except Exception as e:
            raise ModelLoadError(self.model_name, f"Failed to load model: {e}")

    def _create_quantization_config(self) -> Optional[BitsAndBytesConfig]:
        """
        Create quantization configuration for memory efficiency.

        Returns None if bitsandbytes not available (CPU-only setup).
        """
        if not QUANTIZATION_AVAILABLE:
            return None
        bits = self.quantization_config.get('bits', 4)

        if bits == 4:
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            )
        elif bits == 8:
            return BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_enable_fp32_cpu_offload=True
            )
        else:
            raise ValueError(f"Unsupported quantization bits: {bits}")

    def _setup_generation_config(self) -> None:
        """Setup generation configuration with model-specific defaults."""
        config_dict = {
            'max_length': self.generation_defaults.get('max_length', 512),
            'temperature': self.generation_defaults.get('temperature', 0.7),
            'top_p': self.generation_defaults.get('top_p', 0.9),
            'top_k': self.generation_defaults.get('top_k', 50),
            'do_sample': self.generation_defaults.get('do_sample', True),
            'pad_token_id': self._tokenizer.pad_token_id,
            'eos_token_id': self._tokenizer.eos_token_id,
            'repetition_penalty': 1.1,
            'length_penalty': 1.0,
        }

        # Add model-specific tokens if available
        if hasattr(self._tokenizer, 'pad_token_id') and self._tokenizer.pad_token_id is not None:
            config_dict['pad_token_id'] = self._tokenizer.pad_token_id

        self._generation_config = GenerationConfig(**config_dict)

    def unload(self) -> None:
        """Unload the model from memory."""
        try:
            self.logger.info(f"Unloading model: {self.model_name}")

            # Delete model and tokenizer
            if self._model is not None:
                del self._model
                self._model = None

            if self._tokenizer is not None:
                del self._tokenizer
                self._tokenizer = None

            if self._generation_config is not None:
                del self._generation_config
                self._generation_config = None

            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Force garbage collection
            gc.collect()

            self._is_loaded = False
            self._metadata = None

            self.logger.info(f"Model {self.model_name} unloaded successfully")

        except Exception as e:
            self.logger.error(f"Error unloading model {self.model_name}: {e}")

    def generate(self, request: InferenceRequest) -> InferenceResponse:
        """
        Generate text using the model.

        Args:
            request: Inference request with prompt and parameters

        Returns:
            Generated text response
        """
        self._ensure_loaded()
        self.validate_input(request)

        try:
            start_time = time.time()

            # Prepare input
            prompt = self._prepare_prompt(request.prompt)
            inputs = self._tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_context_length - (request.max_length or 512)
            ).to(self.device)

            # Override generation config with request parameters
            generation_config = GenerationConfig(
                **{**self._generation_config.to_dict(),
                   **self._extract_generation_params(request)}
            )

            # Generate
            with torch.no_grad():
                output = self._model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    generation_config=generation_config,
                    pad_token_id=self._tokenizer.pad_token_id
                )

            # Decode output
            generated_ids = output[0][len(inputs.input_ids[0]):]  # Remove input tokens
            generated_text = self._tokenizer.decode(generated_ids, skip_special_tokens=True)

            # Clean up the output
            generated_text = self._post_process_output(generated_text)

            # Calculate metrics
            processing_time_ms = (time.time() - start_time) * 1000
            tokens_generated = len(generated_ids)

            response = InferenceResponse(
                generated_text=generated_text,
                confidence_score=0.8,  # Placeholder - could implement actual confidence
                processing_time_ms=processing_time_ms,
                tokens_generated=tokens_generated,
                model_name=self.model_name,
                request_id=request.request_id,
                metadata={
                    'prompt_tokens': len(inputs.input_ids[0]),
                    'device': self.device,
                    'quantized': self.use_quantization
                }
            )

            # Log the inference
            self._log_inference(request, response)

            return response

        except Exception as e:
            self.logger.error(f"Generation failed for {self.model_name}: {e}")
            raise InferenceError(self.model_name, request.prompt[:100], str(e))

    def validate_input(self, request: InferenceRequest) -> None:
        """Validate the inference request."""
        if not request.prompt:
            raise ValidationError("prompt", request.prompt, "Prompt cannot be empty")

        if len(request.prompt) > self.max_context_length * 4:  # Rough character estimate
            raise ValidationError(
                "prompt",
                request.prompt,
                f"Prompt too long for model context ({self.max_context_length} tokens)"
            )

        if request.max_length and request.max_length > 2048:
            raise ValidationError(
                "max_length",
                str(request.max_length),
                "max_length too large (maximum 2048)"
            )

    def _prepare_prompt(self, prompt: str) -> str:
        """
        Prepare the prompt for the specific model.
        Different models may need different prompt formats.
        """
        # For instruction-following models, we might need special formatting
        if "instruct" in self.model_name.lower():
            # Check if it's already formatted
            if not prompt.startswith("<|im_start|>") and not prompt.startswith("[INST]"):
                # Use a generic instruction format
                prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        return prompt

    def _extract_generation_params(self, request: InferenceRequest) -> Dict[str, Any]:
        """Extract generation parameters from the request."""
        params = {}

        if request.max_length is not None:
            params['max_new_tokens'] = request.max_length
        if request.temperature is not None:
            params['temperature'] = request.temperature
        if request.top_p is not None:
            params['top_p'] = request.top_p
        if request.top_k is not None:
            params['top_k'] = request.top_k
        if request.stop_sequences:
            params['stopping_criteria'] = self._create_stopping_criteria(request.stop_sequences)

        return params

    def _create_stopping_criteria(self, stop_sequences: list) -> Any:
        """Create stopping criteria for generation."""
        # This would need to be implemented based on transformers version
        # For now, we'll rely on post-processing
        return None

    def _post_process_output(self, text: str) -> str:
        """Post-process the generated text."""
        # Remove common artifacts
        text = text.strip()

        # Remove incomplete sentences at the end
        sentences = text.split('.')
        if len(sentences) > 1 and not text.endswith('.'):
            text = '.'.join(sentences[:-1]) + '.'

        return text

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        if self._model is None:
            return 0.0

        # Get model parameters count
        total_params = sum(p.numel() for p in self._model.parameters())

        # Estimate memory based on dtype and quantization
        if self.use_quantization:
            bits = self.quantization_config.get('bits', 4)
            memory_mb = total_params * bits / 8 / (1024 * 1024)  # Convert to MB
        else:
            # Assume float16 (2 bytes per parameter)
            memory_mb = total_params * 2 / (1024 * 1024)

        return memory_mb

    def _cleanup_on_failure(self) -> None:
        """Clean up resources if loading fails."""
        try:
            if self._model is not None:
                del self._model
                self._model = None
            if self._tokenizer is not None:
                del self._tokenizer
                self._tokenizer = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
        except Exception:
            pass  # Ignore cleanup errors