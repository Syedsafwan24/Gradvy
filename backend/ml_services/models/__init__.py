"""
backend/ml_services/models/__init__.py
ML model wrapper classes for different model types
Provides unified interfaces for various open-source models
RELEVANT FILES: base/model_interface.py, services/, ML_Models/configs/
"""

# Import concrete model implementations (lazy loading to avoid torch dependency during startup)
def _get_text_generation_model():
    from .text_generation_model import TextGenerationModel
    return TextGenerationModel

def _get_code_generation_model():
    from .code_generation_model import CodeGenerationModel
    return CodeGenerationModel

def _get_embedding_model():
    from .embedding_model import EmbeddingModel, EmbeddingRequest, EmbeddingResponse
    return EmbeddingModel, EmbeddingRequest, EmbeddingResponse

# Model registry mapping model names to class getters (lazy loading)
MODEL_CLASS_REGISTRY = {
    # Text generation models
    "mistral-7b-instruct": _get_text_generation_model,
    "phi-3-mini": _get_text_generation_model,
    "flan-t5-xl": _get_text_generation_model,

    # Code generation models
    "codellama-7b-instruct": _get_code_generation_model,
    "starcoder-7b": _get_code_generation_model,

    # Embedding models (return EmbeddingModel only)
    "all-minilm-l6-v2": lambda: _get_embedding_model()[0],
    "codebert-base": lambda: _get_embedding_model()[0],
}

def get_model_class(model_name: str):
    """Get model class with lazy loading"""
    if model_name in MODEL_CLASS_REGISTRY:
        return MODEL_CLASS_REGISTRY[model_name]()
    raise ValueError(f"Unknown model: {model_name}")

__all__ = [
    '_get_text_generation_model',
    '_get_code_generation_model',
    '_get_embedding_model',
    'MODEL_CLASS_REGISTRY',
    'get_model_class'
]