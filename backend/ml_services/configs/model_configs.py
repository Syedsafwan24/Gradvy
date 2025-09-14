"""
backend/ml_services/configs/model_configs.py
Configuration registry for all supported ML models
Centralized model definitions with capabilities, requirements, and download info
RELEVANT FILES: base/model_interface.py, utils/model_loader.py, ML_Models/
"""

from typing import Dict, List, Any
import os

# Base directory for ML models
ML_MODELS_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'core', 'ML_Models'
)

# Model registry with comprehensive configuration
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # =================================================================
    # CODE GENERATION MODELS
    # =================================================================

    "codellama-7b-instruct": {
        "display_name": "CodeLlama 7B Instruct",
        "model_type": "code_generation",
        "huggingface_id": "codellama/CodeLlama-7b-Instruct-hf",
        "local_path": os.path.join(ML_MODELS_BASE_DIR, "models", "codellama-7b-instruct"),
        "size_gb": 13.0,
        "memory_requirement_gb": 16.0,  # Model + overhead
        "gpu_memory_gb": 14.0,  # GPU memory needed
        "capabilities": [
            "code_generation",
            "code_explanation",
            "code_debugging",
            "code_completion",
            "programming_questions",
            "algorithm_explanation"
        ],
        "supported_languages": [
            "python", "javascript", "java", "cpp", "c", "go",
            "rust", "php", "ruby", "swift", "kotlin", "typescript"
        ],
        "max_context_length": 4096,
        "quantization": {
            "enabled": True,
            "bits": 4,  # 4-bit quantization to reduce memory
            "method": "bnb"  # bitsandbytes
        },
        "download_config": {
            "use_auth_token": False,
            "revision": "main",
            "torch_dtype": "float16"
        },
        "generation_defaults": {
            "max_length": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "do_sample": True,
            "pad_token_id": 2  # EOS token
        }
    },

    "starcoder-7b": {
        "display_name": "StarCoder 7B",
        "model_type": "code_generation",
        "huggingface_id": "bigcode/starcoder",
        "local_path": os.path.join(ML_MODELS_BASE_DIR, "models", "starcoder-7b"),
        "size_gb": 13.0,
        "memory_requirement_gb": 16.0,
        "gpu_memory_gb": 14.0,
        "capabilities": [
            "code_generation",
            "code_completion",
            "code_translation",
            "documentation_generation"
        ],
        "supported_languages": [
            "python", "javascript", "java", "cpp", "c", "go",
            "typescript", "php", "ruby", "kotlin", "scala", "shell"
        ],
        "max_context_length": 8192,
        "quantization": {
            "enabled": True,
            "bits": 4,
            "method": "bnb"
        },
        "download_config": {
            "use_auth_token": False,
            "revision": "main",
            "torch_dtype": "float16"
        },
        "generation_defaults": {
            "max_length": 256,
            "temperature": 0.2,  # Lower for more deterministic code
            "top_p": 0.95,
            "do_sample": True
        }
    },

    # =================================================================
    # TEXT GENERATION MODELS
    # =================================================================

    "mistral-7b-instruct": {
        "display_name": "Mistral 7B Instruct",
        "model_type": "text_generation",
        "huggingface_id": "mistralai/Mistral-7B-Instruct-v0.2",
        "local_path": os.path.join(ML_MODELS_BASE_DIR, "models", "mistral-7b-instruct"),
        "size_gb": 13.0,
        "memory_requirement_gb": 16.0,
        "gpu_memory_gb": 14.0,
        "capabilities": [
            "text_generation",
            "instruction_following",
            "question_answering",
            "content_creation",
            "learning_path_generation",
            "educational_content"
        ],
        "max_context_length": 8192,
        "quantization": {
            "enabled": True,
            "bits": 4,
            "method": "bnb"
        },
        "download_config": {
            "use_auth_token": False,
            "revision": "main",
            "torch_dtype": "float16"
        },
        "generation_defaults": {
            "max_length": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "do_sample": True
        }
    },

    "phi-3-mini": {
        "display_name": "Phi-3 Mini 3.8B",
        "model_type": "text_generation",
        "huggingface_id": "microsoft/Phi-3-mini-4k-instruct",
        "local_path": os.path.join(ML_MODELS_BASE_DIR, "models", "phi-3-mini"),
        "size_gb": 7.0,  # Smaller model
        "memory_requirement_gb": 10.0,
        "gpu_memory_gb": 8.0,
        "capabilities": [
            "text_generation",
            "instruction_following",
            "question_generation",
            "educational_content",
            "quick_responses"
        ],
        "max_context_length": 4096,
        "quantization": {
            "enabled": True,
            "bits": 4,
            "method": "bnb"
        },
        "download_config": {
            "use_auth_token": False,
            "revision": "main",
            "torch_dtype": "float16"
        },
        "generation_defaults": {
            "max_length": 256,
            "temperature": 0.6,
            "top_p": 0.9,
            "do_sample": True
        }
    },

    # =================================================================
    # SPECIALIZED MODELS
    # =================================================================

    "flan-t5-xl": {
        "display_name": "FLAN-T5 XL",
        "model_type": "text_generation",
        "huggingface_id": "google/flan-t5-xl",
        "local_path": os.path.join(ML_MODELS_BASE_DIR, "models", "flan-t5-xl"),
        "size_gb": 11.0,
        "memory_requirement_gb": 14.0,
        "gpu_memory_gb": 12.0,
        "capabilities": [
            "question_generation",
            "structured_tasks",
            "educational_assessment",
            "quiz_creation",
            "content_summarization"
        ],
        "max_context_length": 512,
        "quantization": {
            "enabled": False,  # T5 doesn't work well with aggressive quantization
            "bits": 8,
            "method": "bnb"
        },
        "download_config": {
            "use_auth_token": False,
            "revision": "main",
            "torch_dtype": "float16"
        },
        "generation_defaults": {
            "max_length": 256,
            "temperature": 0.8,
            "top_p": 0.9,
            "do_sample": True
        }
    },

    # =================================================================
    # EMBEDDING MODELS
    # =================================================================

    "all-minilm-l6-v2": {
        "display_name": "All-MiniLM-L6-v2",
        "model_type": "embedding",
        "huggingface_id": "sentence-transformers/all-MiniLM-L6-v2",
        "local_path": os.path.join(ML_MODELS_BASE_DIR, "models", "all-minilm-l6-v2"),
        "size_gb": 0.4,  # Much smaller
        "memory_requirement_gb": 2.0,
        "gpu_memory_gb": 1.0,
        "capabilities": [
            "text_embedding",
            "semantic_similarity",
            "content_matching",
            "clustering",
            "search"
        ],
        "embedding_dimension": 384,
        "max_context_length": 512,
        "quantization": {
            "enabled": False  # Embeddings don't quantize well
        },
        "download_config": {
            "use_auth_token": False,
            "revision": "main"
        }
    },

    "codebert-base": {
        "display_name": "CodeBERT Base",
        "model_type": "embedding",
        "huggingface_id": "microsoft/codebert-base",
        "local_path": os.path.join(ML_MODELS_BASE_DIR, "models", "codebert-base"),
        "size_gb": 0.5,
        "memory_requirement_gb": 2.0,
        "gpu_memory_gb": 1.5,
        "capabilities": [
            "code_embedding",
            "code_similarity",
            "programming_search",
            "code_clustering"
        ],
        "embedding_dimension": 768,
        "max_context_length": 512,
        "quantization": {
            "enabled": False
        },
        "download_config": {
            "use_auth_token": False,
            "revision": "main"
        }
    }
}

# Model selection based on use case
MODEL_USE_CASES: Dict[str, List[str]] = {
    "learning_path_generation": ["mistral-7b-instruct", "phi-3-mini"],
    "question_generation": ["flan-t5-xl", "mistral-7b-instruct"],
    "code_evaluation": ["codellama-7b-instruct", "starcoder-7b"],
    "code_generation": ["codellama-7b-instruct", "starcoder-7b"],
    "content_similarity": ["all-minilm-l6-v2"],
    "code_similarity": ["codebert-base"],
    "quick_responses": ["phi-3-mini"],
    "comprehensive_responses": ["mistral-7b-instruct"]
}

# Resource requirements for different deployment scenarios
DEPLOYMENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "development": {
        "preferred_models": ["phi-3-mini", "all-minilm-l6-v2"],
        "max_memory_gb": 12,
        "allow_cpu_only": True,
        "quantization_aggressive": True
    },

    "production_small": {
        "preferred_models": ["mistral-7b-instruct", "codellama-7b-instruct", "all-minilm-l6-v2"],
        "max_memory_gb": 24,
        "allow_cpu_only": False,
        "quantization_aggressive": True
    },

    "production_large": {
        "preferred_models": MODEL_REGISTRY.keys(),
        "max_memory_gb": 64,
        "allow_cpu_only": False,
        "quantization_aggressive": False,
        "load_multiple_models": True
    }
}


def get_model_config(model_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific model.

    Args:
        model_name: Name of the model

    Returns:
        Model configuration dictionary

    Raises:
        KeyError: If model not found in registry
    """
    if model_name not in MODEL_REGISTRY:
        available_models = list(MODEL_REGISTRY.keys())
        raise KeyError(
            f"Model '{model_name}' not found in registry. "
            f"Available models: {', '.join(available_models)}"
        )

    return MODEL_REGISTRY[model_name].copy()


def get_models_by_type(model_type: str) -> List[str]:
    """
    Get all models of a specific type.

    Args:
        model_type: Type of models to retrieve

    Returns:
        List of model names
    """
    return [
        name for name, config in MODEL_REGISTRY.items()
        if config["model_type"] == model_type
    ]


def get_models_by_capability(capability: str) -> List[str]:
    """
    Get all models that support a specific capability.

    Args:
        capability: Capability to search for

    Returns:
        List of model names
    """
    return [
        name for name, config in MODEL_REGISTRY.items()
        if capability in config.get("capabilities", [])
    ]


def get_models_for_use_case(use_case: str) -> List[str]:
    """
    Get recommended models for a specific use case.

    Args:
        use_case: Use case to get models for

    Returns:
        List of model names ordered by preference
    """
    return MODEL_USE_CASES.get(use_case, [])


def get_deployment_profile(profile_name: str) -> Dict[str, Any]:
    """
    Get configuration for a deployment profile.

    Args:
        profile_name: Name of deployment profile

    Returns:
        Profile configuration
    """
    if profile_name not in DEPLOYMENT_PROFILES:
        available_profiles = list(DEPLOYMENT_PROFILES.keys())
        raise KeyError(
            f"Profile '{profile_name}' not found. "
            f"Available profiles: {', '.join(available_profiles)}"
        )

    return DEPLOYMENT_PROFILES[profile_name].copy()