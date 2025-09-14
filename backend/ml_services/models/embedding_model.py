"""
backend/ml_services/models/embedding_model.py
Embedding model implementation for semantic similarity and content matching
Supports sentence-transformers and other embedding models
RELEVANT FILES: base/model_interface.py, configs/model_configs.py, utils/model_registry.py
"""

import os
import time
import torch
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sentence_transformers import SentenceTransformer
import gc

from ..base.model_interface import (
    BaseMLModel, ModelMetadata, InferenceRequest, InferenceResponse
)
from ..base.exceptions import ModelLoadError, InferenceError, ValidationError


class EmbeddingRequest(InferenceRequest):
    """Extended request for embedding operations."""

    def __init__(
        self,
        texts: Union[str, List[str]],
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        normalize_embeddings: bool = True,
        batch_size: int = 32
    ):
        # Convert single text to list for consistent handling
        if isinstance(texts, str):
            texts = [texts]

        super().__init__(
            prompt=texts[0] if texts else "",  # For compatibility with base class
            user_id=user_id,
            request_id=request_id
        )

        self.texts = texts
        self.normalize_embeddings = normalize_embeddings
        self.batch_size = batch_size


class EmbeddingResponse(InferenceResponse):
    """Extended response for embedding operations."""

    def __init__(
        self,
        embeddings: np.ndarray,
        processing_time_ms: float,
        model_name: str,
        request_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            generated_text="",  # Not applicable for embeddings
            confidence_score=1.0,  # Embeddings don't have confidence scores typically
            processing_time_ms=processing_time_ms,
            tokens_generated=0,  # Not applicable
            model_name=model_name,
            request_id=request_id,
            metadata=metadata or {}
        )

        self.embeddings = embeddings
        self.embedding_shape = embeddings.shape
        self.num_texts = embeddings.shape[0]


class EmbeddingModel(BaseMLModel):
    """
    Embedding model using sentence-transformers.

    Supports models like:
    - all-MiniLM-L6-v2 (general purpose)
    - CodeBERT (code similarity)
    - all-mpnet-base-v2 (high quality general purpose)

    Features:
    - Batch processing for efficiency
    - Automatic normalization
    - Similarity search capabilities
    - Memory-efficient processing
    """

    def __init__(self, model_name: str, model_config: Dict[str, Any] = None):
        super().__init__(model_name, model_config)

        # Embedding-specific attributes
        self._model = None
        self.embedding_dimension = self.model_config.get('embedding_dimension', 384)
        self.max_seq_length = self.model_config.get('max_context_length', 512)

        # Configuration
        self.huggingface_id = self.model_config.get('huggingface_id')
        self.local_path = self.model_config.get('local_path')

        # Device management
        self.device = None
        self.use_gpu = torch.cuda.is_available()

    def load(self) -> None:
        """Load the embedding model."""
        try:
            start_time = time.time()
            self.logger.info(f"Loading embedding model: {self.model_name}")

            # Determine device
            self.device = "cuda" if self.use_gpu else "cpu"
            self.logger.info(f"Using device: {self.device}")

            # Try local path first, fallback to HuggingFace
            model_path = self.local_path if os.path.exists(self.local_path) else self.huggingface_id

            self.logger.info(f"Loading model from: {model_path}")

            # Load the sentence transformer model
            self._model = SentenceTransformer(
                model_path,
                device=self.device,
                trust_remote_code=True
            )

            # Set max sequence length if specified
            if hasattr(self._model, 'max_seq_length'):
                self._model.max_seq_length = self.max_seq_length

            # Create metadata
            load_time_ms = (time.time() - start_time) * 1000
            self._load_time_ms = load_time_ms

            self._metadata = ModelMetadata(
                name=self.model_name,
                version="1.0.0",
                model_type="embedding",
                size_mb=self.model_config.get('size_gb', 0) * 1024,
                capabilities=self.model_config.get('capabilities', []),
                loaded_at=datetime.now(),
                memory_usage_mb=self._estimate_memory_usage()
            )

            self._is_loaded = True
            self.logger.info(
                f"Embedding model {self.model_name} loaded successfully in {load_time_ms:.0f}ms, "
                f"Device: {self.device}, Dimension: {self.embedding_dimension}"
            )

        except Exception as e:
            self.logger.error(f"Failed to load embedding model {self.model_name}: {e}")
            self._cleanup_on_failure()
            raise ModelLoadError(self.model_name, str(e))

    def unload(self) -> None:
        """Unload the model from memory."""
        try:
            self.logger.info(f"Unloading embedding model: {self.model_name}")

            # Delete model
            if self._model is not None:
                del self._model
                self._model = None

            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Force garbage collection
            gc.collect()

            self._is_loaded = False
            self._metadata = None

            self.logger.info(f"Embedding model {self.model_name} unloaded successfully")

        except Exception as e:
            self.logger.error(f"Error unloading embedding model {self.model_name}: {e}")

    def generate(self, request: InferenceRequest) -> InferenceResponse:
        """
        Generate embeddings for the given text(s).
        This overrides the base class method for embedding-specific processing.
        """
        # Convert standard InferenceRequest to EmbeddingRequest if needed
        if isinstance(request, EmbeddingRequest):
            embedding_request = request
        else:
            embedding_request = EmbeddingRequest(
                texts=[request.prompt],
                user_id=request.user_id,
                request_id=request.request_id
            )

        return self.encode(embedding_request)

    def encode(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Encode texts into embeddings.

        Args:
            request: Embedding request with texts to encode

        Returns:
            Embeddings response with numpy arrays
        """
        self._ensure_loaded()
        self.validate_embedding_input(request)

        try:
            start_time = time.time()

            # Encode texts
            embeddings = self._model.encode(
                request.texts,
                batch_size=request.batch_size,
                normalize_embeddings=request.normalize_embeddings,
                show_progress_bar=False,
                convert_to_numpy=True
            )

            # Ensure 2D array (batch_size, embedding_dim)
            if embeddings.ndim == 1:
                embeddings = embeddings.reshape(1, -1)

            processing_time_ms = (time.time() - start_time) * 1000

            response = EmbeddingResponse(
                embeddings=embeddings,
                processing_time_ms=processing_time_ms,
                model_name=self.model_name,
                request_id=request.request_id,
                metadata={
                    'num_texts': len(request.texts),
                    'embedding_dimension': embeddings.shape[1],
                    'normalized': request.normalize_embeddings,
                    'batch_size': request.batch_size,
                    'device': self.device
                }
            )

            # Log the inference
            self._log_embedding_inference(request, response)

            return response

        except Exception as e:
            self.logger.error(f"Embedding generation failed for {self.model_name}: {e}")
            raise InferenceError(self.model_name, str(request.texts[:2]), str(e))

    def similarity(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray,
        metric: str = "cosine"
    ) -> np.ndarray:
        """
        Calculate similarity between embeddings.

        Args:
            embeddings1: First set of embeddings
            embeddings2: Second set of embeddings
            metric: Similarity metric ('cosine', 'dot', 'euclidean')

        Returns:
            Similarity matrix
        """
        if metric == "cosine":
            # Normalize if not already normalized
            norm1 = np.linalg.norm(embeddings1, axis=1, keepdims=True)
            norm2 = np.linalg.norm(embeddings2, axis=1, keepdims=True)

            embeddings1_norm = embeddings1 / np.clip(norm1, 1e-8, None)
            embeddings2_norm = embeddings2 / np.clip(norm2, 1e-8, None)

            return np.dot(embeddings1_norm, embeddings2_norm.T)

        elif metric == "dot":
            return np.dot(embeddings1, embeddings2.T)

        elif metric == "euclidean":
            # Calculate pairwise euclidean distances
            distances = np.linalg.norm(
                embeddings1[:, np.newaxis] - embeddings2[np.newaxis, :],
                axis=2
            )
            # Convert distances to similarities (higher = more similar)
            return 1 / (1 + distances)

        else:
            raise ValueError(f"Unsupported similarity metric: {metric}")

    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: np.ndarray,
        top_k: int = 5,
        metric: str = "cosine"
    ) -> List[Dict[str, Any]]:
        """
        Find most similar embeddings to a query.

        Args:
            query_embedding: Query embedding (1D or 2D)
            candidate_embeddings: Candidate embeddings (2D)
            top_k: Number of top results to return
            metric: Similarity metric to use

        Returns:
            List of similarity results with indices and scores
        """
        # Ensure query is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Calculate similarities
        similarities = self.similarity(query_embedding, candidate_embeddings, metric)
        similarities = similarities.flatten()  # Flatten to 1D

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                'index': int(idx),
                'similarity_score': float(similarities[idx]),
                'metric': metric
            })

        return results

    def validate_input(self, request: InferenceRequest) -> None:
        """Validate standard inference request (for compatibility)."""
        if not request.prompt:
            raise ValidationError("prompt", request.prompt, "Text cannot be empty")

    def validate_embedding_input(self, request: EmbeddingRequest) -> None:
        """Validate embedding request."""
        if not request.texts or len(request.texts) == 0:
            raise ValidationError("texts", str(request.texts), "Text list cannot be empty")

        for i, text in enumerate(request.texts):
            if not text or not isinstance(text, str):
                raise ValidationError(
                    f"texts[{i}]",
                    str(text),
                    "Each text must be a non-empty string"
                )

        if len(request.texts) > 1000:  # Reasonable batch limit
            raise ValidationError(
                "texts",
                str(len(request.texts)),
                "Too many texts in batch (maximum 1000)"
            )

        if request.batch_size and (request.batch_size < 1 or request.batch_size > 128):
            raise ValidationError(
                "batch_size",
                str(request.batch_size),
                "Batch size must be between 1 and 128"
            )

    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        if self._model is None:
            return 0.0

        try:
            # Try to get model size from the sentence transformer
            total_params = 0
            for module in self._model.modules():
                if hasattr(module, 'parameters'):
                    for param in module.parameters():
                        total_params += param.numel()

            # Assume float32 (4 bytes per parameter)
            memory_mb = total_params * 4 / (1024 * 1024)
            return memory_mb

        except Exception:
            # Fallback to config size
            return self.model_config.get('size_gb', 0.5) * 1024

    def _log_embedding_inference(self, request: EmbeddingRequest, response: EmbeddingResponse) -> None:
        """Log embedding inference for monitoring."""
        self._total_inferences += 1
        self._total_inference_time_ms += response.processing_time_ms

        if self._metadata:
            self._metadata.inference_count = self._total_inferences
            self._metadata.last_inference = datetime.now()

        self.logger.info(
            f"Embedding inference completed - Model: {self.model_name}, "
            f"Texts: {response.num_texts}, "
            f"Dimension: {response.embedding_shape[1]}, "
            f"Time: {response.processing_time_ms:.2f}ms, "
            f"User: {request.user_id or 'anonymous'}"
        )

    def _cleanup_on_failure(self) -> None:
        """Clean up resources if loading fails."""
        try:
            if self._model is not None:
                del self._model
                self._model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
        except Exception:
            pass  # Ignore cleanup errors