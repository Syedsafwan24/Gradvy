"""
backend/ml_services/configs/service_configs.py
Configuration settings for ML services
Defines service-level configurations, caching, and operational parameters
RELEVANT FILES: base/service_interface.py, services/, model_configs.py
"""

import os
from typing import Dict, Any

# =================================================================
# GENERAL ML SERVICE SETTINGS
# =================================================================

ML_SERVICE_SETTINGS: Dict[str, Any] = {
    # Model loading and caching
    "model_loading": {
        "lazy_loading": True,  # Load models only when needed
        "preload_critical_models": False,  # Preload essential models on startup
        "model_timeout_minutes": 30,  # Unload unused models after 30 minutes
        "max_concurrent_loads": 2,  # Maximum models loading simultaneously
        "retry_attempts": 3,  # Retry model loading on failure
        "retry_delay_seconds": 5,  # Delay between retries
    },

    # Memory and resource management
    "resource_management": {
        "max_total_memory_gb": 32,  # Maximum total memory for all models
        "memory_buffer_gb": 4,  # Reserve memory buffer
        "auto_unload_on_memory_pressure": True,  # Auto-unload models when memory low
        "gpu_memory_fraction": 0.8,  # Use 80% of available GPU memory
        "cpu_threads": None,  # Auto-detect CPU threads
    },

    # Caching configuration
    "caching": {
        "enable_response_cache": True,
        "cache_backend": "memory",  # 'memory', 'redis', 'memcached'
        "cache_ttl_seconds": 3600,  # 1 hour default TTL
        "max_cache_size_mb": 512,  # Maximum cache size
        "cache_key_prefix": "gradvy_ml:",

        # Specific cache TTLs for different operations
        "ttl_by_operation": {
            "learning_path_generation": 3600,  # 1 hour
            "question_generation": 1800,  # 30 minutes
            "code_evaluation": 300,  # 5 minutes
            "embedding_similarity": 7200,  # 2 hours
        }
    },

    # Privacy and security
    "privacy": {
        "enable_data_sanitization": True,
        "log_user_data": False,  # Never log actual user data
        "anonymize_logs": True,  # Anonymize user IDs in logs
        "audit_trail": True,  # Keep audit trail of ML operations
        "consent_required_operations": [
            "learning_path_generation",
            "personalized_recommendations",
            "behavioral_analysis"
        ]
    },

    # Performance and monitoring
    "monitoring": {
        "enable_metrics": True,
        "metrics_backend": "prometheus",  # 'prometheus', 'statsd', 'cloudwatch'
        "log_inference_times": True,
        "log_resource_usage": True,
        "health_check_interval_seconds": 60,
        "performance_alert_thresholds": {
            "inference_time_ms": 5000,  # Alert if inference > 5s
            "memory_usage_percent": 90,  # Alert if memory > 90%
            "error_rate_percent": 5,  # Alert if error rate > 5%
        }
    },

    # Async processing
    "async_processing": {
        "enable_celery": True,
        "celery_broker": "redis://localhost:6379/1",
        "celery_backend": "redis://localhost:6379/1",
        "task_timeout_seconds": 300,  # 5 minute timeout for tasks
        "max_concurrent_tasks": 4,
        "priority_queue_enabled": True,
    },

    # Development and debugging
    "debug": {
        "enable_debug_mode": False,
        "verbose_logging": False,
        "save_model_inputs_outputs": False,  # For debugging only
        "profile_inference": False,  # Profile model performance
        "mock_models_for_testing": False,  # Use mock models in tests
    }
}

# =================================================================
# SERVICE-SPECIFIC CONFIGURATIONS
# =================================================================

LEARNING_PATH_SERVICE_CONFIG: Dict[str, Any] = {
    "service_name": "learning_path_service",
    "description": "Generates personalized learning paths using AI",

    # Model configuration
    "primary_model": "mistral-7b-instruct",
    "fallback_models": ["phi-3-mini"],
    "embedding_model": "all-minilm-l6-v2",

    # Generation parameters
    "generation": {
        "max_modules_per_path": 10,
        "max_lessons_per_module": 8,
        "min_path_duration_weeks": 2,
        "max_path_duration_weeks": 24,
        "difficulty_adaptation_enabled": True,
        "prerequisite_checking_enabled": True,
    },

    # Caching
    "cache_ttl_seconds": 3600,  # Cache paths for 1 hour
    "cache_per_user": True,

    # Privacy
    "require_consent": True,
    "sanitize_user_data": True,
    "log_generations": False,
}

QUESTION_GENERATOR_SERVICE_CONFIG: Dict[str, Any] = {
    "service_name": "question_generator_service",
    "description": "Generates dynamic questions and assessments",

    # Model configuration
    "primary_model": "flan-t5-xl",
    "fallback_models": ["mistral-7b-instruct"],

    # Generation parameters
    "generation": {
        "questions_per_topic": 5,
        "difficulty_levels": ["beginner", "intermediate", "advanced"],
        "question_types": ["multiple_choice", "true_false", "short_answer", "coding"],
        "max_question_length": 200,
        "max_options_per_question": 4,
        "include_explanations": True,
    },

    # Quality control
    "quality_control": {
        "min_confidence_score": 0.7,
        "duplicate_detection_enabled": True,
        "content_filtering_enabled": True,
        "human_review_threshold": 0.5,  # Questions below this need review
    },

    # Caching
    "cache_ttl_seconds": 1800,  # Cache for 30 minutes
    "cache_per_topic": True,
}

CODE_EVALUATOR_SERVICE_CONFIG: Dict[str, Any] = {
    "service_name": "code_evaluator_service",
    "description": "Evaluates and provides feedback on code submissions",

    # Model configuration
    "primary_model": "codellama-7b-instruct",
    "fallback_models": ["starcoder-7b"],

    # Evaluation parameters
    "evaluation": {
        "supported_languages": ["python", "javascript", "java", "cpp", "go"],
        "max_code_length": 5000,  # Maximum characters in code
        "timeout_seconds": 30,  # Code execution timeout
        "provide_suggestions": True,
        "check_best_practices": True,
        "security_scan_enabled": True,
    },

    # Sandbox configuration
    "sandbox": {
        "enable_code_execution": True,
        "execution_environment": "docker",
        "memory_limit_mb": 256,
        "cpu_limit_percent": 50,
        "network_disabled": True,
        "file_system_read_only": True,
    },

    # Caching
    "cache_ttl_seconds": 300,  # Cache for 5 minutes
    "cache_by_code_hash": True,
}

# Service registry mapping
SERVICE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "learning_path_service": LEARNING_PATH_SERVICE_CONFIG,
    "question_generator_service": QUESTION_GENERATOR_SERVICE_CONFIG,
    "code_evaluator_service": CODE_EVALUATOR_SERVICE_CONFIG,
}

# =================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# =================================================================

def get_environment_config() -> Dict[str, Any]:
    """
    Get environment-specific configuration overrides.

    Returns:
        Configuration dictionary with environment-specific settings
    """
    env = os.environ.get('DJANGO_ENVIRONMENT', 'development').lower()

    if env == 'production':
        return {
            "model_loading": {
                "preload_critical_models": True,
                "max_concurrent_loads": 1,  # Be conservative in production
            },
            "resource_management": {
                "max_total_memory_gb": 48,  # More memory in production
                "auto_unload_on_memory_pressure": True,
            },
            "caching": {
                "cache_backend": "redis",
                "max_cache_size_mb": 2048,  # Larger cache in production
            },
            "monitoring": {
                "enable_metrics": True,
                "health_check_interval_seconds": 30,  # More frequent checks
            },
            "debug": {
                "enable_debug_mode": False,
                "verbose_logging": False,
                "save_model_inputs_outputs": False,
            }
        }

    elif env == 'staging':
        return {
            "model_loading": {
                "preload_critical_models": True,
            },
            "resource_management": {
                "max_total_memory_gb": 24,
            },
            "caching": {
                "cache_backend": "redis",
            },
            "debug": {
                "enable_debug_mode": True,
                "verbose_logging": True,
            }
        }

    else:  # development
        return {
            "model_loading": {
                "lazy_loading": True,
                "model_timeout_minutes": 5,  # Faster unloading in dev
            },
            "resource_management": {
                "max_total_memory_gb": 16,
            },
            "caching": {
                "cache_backend": "memory",
                "cache_ttl_seconds": 300,  # Shorter cache in dev
            },
            "debug": {
                "enable_debug_mode": True,
                "verbose_logging": True,
                "save_model_inputs_outputs": True,
                "mock_models_for_testing": False,
            }
        }


def get_service_config(service_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific service with environment overrides.

    Args:
        service_name: Name of the service

    Returns:
        Service configuration dictionary

    Raises:
        KeyError: If service not found
    """
    if service_name not in SERVICE_CONFIGS:
        available_services = list(SERVICE_CONFIGS.keys())
        raise KeyError(
            f"Service '{service_name}' not found. "
            f"Available services: {', '.join(available_services)}"
        )

    # Start with base service config
    config = SERVICE_CONFIGS[service_name].copy()

    # Apply environment-specific overrides
    env_config = get_environment_config()

    # Merge configurations (environment overrides base)
    def merge_configs(base: dict, override: dict) -> dict:
        """Recursively merge configuration dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    # Apply global settings
    config.update(merge_configs(ML_SERVICE_SETTINGS, env_config))

    return config