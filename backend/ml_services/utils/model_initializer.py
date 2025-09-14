"""
backend/ml_services/utils/model_initializer.py
Model initialization and registration system
Automatically registers all available models with the global registry
RELEVANT FILES: utils/model_registry.py, utils/model_loader.py, models/__init__.py
"""

import time
import logging
from typing import Dict, Any, List, Optional

from .model_registry import get_global_registry
from .model_loader import get_global_loader
from ..models import MODEL_CLASS_REGISTRY
from ..configs.model_configs import (
    MODEL_REGISTRY as CONFIG_REGISTRY,
    get_deployment_profile,
    get_models_for_use_case
)
from ..base.exceptions import ConfigurationError


class ModelInitializer:
    """
    Handles initialization and registration of ML models.

    This class:
    1. Registers model classes with the global registry
    2. Handles deployment-specific model loading
    3. Provides model discovery and health checking
    4. Manages model lifecycle during application startup
    """

    def __init__(self, deployment_profile: str = "development"):
        """
        Initialize the model initializer.

        Args:
            deployment_profile: Deployment profile to use
        """
        self.deployment_profile = deployment_profile
        self.profile_config = get_deployment_profile(deployment_profile)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # Get global instances
        self.registry = get_global_registry()
        self.loader = get_global_loader()

    def initialize_all_models(self) -> Dict[str, Any]:
        """
        Initialize all models according to deployment profile.

        Returns:
            Dictionary with initialization results
        """
        self.logger.info(f"Initializing models for deployment profile: {self.deployment_profile}")

        results = {
            'deployment_profile': self.deployment_profile,
            'registered_models': [],
            'preloaded_models': [],
            'failed_registrations': [],
            'initialization_time_ms': 0
        }

        start_time = time.time()

        try:
            # 1. Register all model classes
            registration_results = self._register_model_classes()
            results['registered_models'] = registration_results['success']
            results['failed_registrations'] = registration_results['failures']

            # 2. Preload models based on deployment profile
            if self._should_preload_models():
                preload_results = self._preload_priority_models()
                results['preloaded_models'] = preload_results

            results['initialization_time_ms'] = (time.time() - start_time) * 1000

            self.logger.info(
                f"Model initialization completed: "
                f"{len(results['registered_models'])} registered, "
                f"{len(results['preloaded_models'])} preloaded, "
                f"{len(results['failed_registrations'])} failures"
            )

            return results

        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
            raise ConfigurationError("model_initialization", str(e))

    def _register_model_classes(self) -> Dict[str, List[str]]:
        """Register all model classes with the registry."""
        results = {'success': [], 'failures': []}

        for model_name, model_class in MODEL_CLASS_REGISTRY.items():
            try:
                # Verify model has configuration
                if model_name not in CONFIG_REGISTRY:
                    self.logger.warning(f"No configuration found for model: {model_name}")
                    results['failures'].append(model_name)
                    continue

                # Register with the registry
                self.registry.register_model_class(model_name, model_class)
                results['success'].append(model_name)

                self.logger.debug(f"Registered model: {model_name}")

            except Exception as e:
                self.logger.error(f"Failed to register model {model_name}: {e}")
                results['failures'].append(model_name)

        return results

    def _should_preload_models(self) -> bool:
        """Check if models should be preloaded based on deployment profile."""
        return self.profile_config.get('preload_critical_models', False)

    def _preload_priority_models(self) -> List[str]:
        """Preload high-priority models for faster first access."""
        preferred_models = self.profile_config.get('preferred_models', [])
        preloaded = []

        if not preferred_models:
            self.logger.info("No preferred models specified for preloading")
            return preloaded

        self.logger.info(f"Preloading priority models: {preferred_models}")

        # Use the loader's preload functionality
        self.loader.preload_models(preferred_models)

        return preferred_models

    def get_available_models(self, filter_by_capability: str = None) -> List[Dict[str, Any]]:
        """
        Get list of available models with their status.

        Args:
            filter_by_capability: Optional capability to filter by

        Returns:
            List of model information dictionaries
        """
        models = []

        for model_name in self.registry._model_classes.keys():
            try:
                config = CONFIG_REGISTRY[model_name]
                status = self.registry.get_model_status(model_name)

                # Filter by capability if specified
                if filter_by_capability:
                    if filter_by_capability not in config.get('capabilities', []):
                        continue

                model_info = {
                    'name': model_name,
                    'display_name': config.get('display_name', model_name),
                    'type': config.get('model_type', 'unknown'),
                    'capabilities': config.get('capabilities', []),
                    'size_gb': config.get('size_gb', 0),
                    'is_loaded': status.is_loaded if status else False,
                    'health_status': status.health_status if status else 'unknown',
                    'usage_count': status.usage_count if status else 0,
                    'huggingface_id': config.get('huggingface_id', '')
                }

                models.append(model_info)

            except Exception as e:
                self.logger.warning(f"Error getting info for model {model_name}: {e}")

        return models

    def get_models_for_task(self, task_name: str) -> List[str]:
        """
        Get recommended models for a specific task.

        Args:
            task_name: Name of the task (e.g., 'learning_path_generation')

        Returns:
            List of model names ordered by preference
        """
        return get_models_for_use_case(task_name)

    def health_check_all_models(self) -> Dict[str, Any]:
        """
        Perform health check on all registered models.

        Returns:
            Health check results
        """
        self.logger.info("Performing health check on all models")

        results = {
            'healthy_models': [],
            'unhealthy_models': [],
            'unloaded_models': [],
            'total_models': len(self.registry._model_classes),
            'overall_health': 'unknown'
        }

        for model_name in self.registry._model_classes.keys():
            try:
                status = self.registry.get_model_status(model_name)

                if not status.is_loaded:
                    results['unloaded_models'].append({
                        'name': model_name,
                        'reason': 'not_loaded'
                    })
                    continue

                # Get model for health check
                model = self.registry.get_model(model_name, load_if_needed=False)
                health = model.health_check()

                if health['healthy']:
                    results['healthy_models'].append({
                        'name': model_name,
                        'status': health
                    })
                else:
                    results['unhealthy_models'].append({
                        'name': model_name,
                        'status': health
                    })

            except Exception as e:
                results['unhealthy_models'].append({
                    'name': model_name,
                    'error': str(e)
                })

        # Determine overall health
        total_loaded = len(results['healthy_models']) + len(results['unhealthy_models'])
        if total_loaded == 0:
            results['overall_health'] = 'no_models_loaded'
        elif len(results['unhealthy_models']) == 0:
            results['overall_health'] = 'healthy'
        elif len(results['healthy_models']) > len(results['unhealthy_models']):
            results['overall_health'] = 'mostly_healthy'
        else:
            results['overall_health'] = 'degraded'

        self.logger.info(
            f"Health check completed: {len(results['healthy_models'])} healthy, "
            f"{len(results['unhealthy_models'])} unhealthy, "
            f"{len(results['unloaded_models'])} unloaded"
        )

        return results

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            'deployment_profile': self.deployment_profile,
            'registry_stats': self.registry.get_stats() if hasattr(self.registry, 'get_stats') else {},
            'cache_stats': self.loader.get_cache_stats(),
            'available_models': len(self.registry._model_classes),
            'loaded_models': len(self.registry.get_loaded_models()),
            'resource_usage': self.registry.get_resource_usage().__dict__ if self.registry.get_resource_usage() else None
        }

    def cleanup_resources(self) -> None:
        """Clean up resources and shutdown gracefully."""
        self.logger.info("Cleaning up model resources")

        try:
            # Clean up old cache entries
            self.loader.cleanup_cache()

            # Shutdown registry
            self.registry.shutdown()

        except Exception as e:
            self.logger.error(f"Error during resource cleanup: {e}")


# Global initializer instance
_global_initializer: Optional[ModelInitializer] = None


def get_global_initializer(deployment_profile: str = "development") -> ModelInitializer:
    """Get the global model initializer instance."""
    global _global_initializer

    if _global_initializer is None or _global_initializer.deployment_profile != deployment_profile:
        _global_initializer = ModelInitializer(deployment_profile)

    return _global_initializer


def initialize_ml_system(deployment_profile: str = "development") -> Dict[str, Any]:
    """
    Initialize the entire ML system.

    This is the main entry point for setting up the ML infrastructure.
    Call this during application startup.

    Args:
        deployment_profile: Deployment profile to use

    Returns:
        Initialization results
    """
    import time

    logger = logging.getLogger("MLSystemInit")
    logger.info(f"Initializing ML system with profile: {deployment_profile}")

    try:
        initializer = get_global_initializer(deployment_profile)
        results = initializer.initialize_all_models()

        logger.info(
            f"ML system initialized successfully in {results['initialization_time_ms']:.0f}ms"
        )

        return results

    except Exception as e:
        logger.error(f"ML system initialization failed: {e}")
        raise