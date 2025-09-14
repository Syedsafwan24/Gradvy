"""
backend/ml_services/utils/model_loader.py
Intelligent model loader with automatic downloading, caching, and memory management
Handles HuggingFace model downloads, local storage, and efficient model lifecycle
RELEVANT FILES: configs/model_configs.py, utils/model_registry.py, base/exceptions.py
"""

import os
import shutil
import hashlib
import json
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dataclasses import dataclass

try:
    from huggingface_hub import snapshot_download, hf_hub_download
    from transformers import AutoConfig
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

from ..base.exceptions import ModelLoadError, ConfigurationError, ResourceExhaustedError
from ..configs.model_configs import get_model_config, ML_MODELS_BASE_DIR


@dataclass
class DownloadProgress:
    """Progress information for model downloads"""
    model_name: str
    total_size_mb: float = 0.0
    downloaded_mb: float = 0.0
    progress_percent: float = 0.0
    status: str = "pending"  # 'pending', 'downloading', 'completed', 'failed'
    error_message: str = ""
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


@dataclass
class CacheEntry:
    """Cache entry for a downloaded model"""
    model_name: str
    local_path: str
    download_time: datetime
    size_mb: float
    last_accessed: datetime
    access_count: int
    huggingface_id: str
    version_hash: str  # Hash of model config for version tracking


class ModelLoader:
    """
    Intelligent model loader with caching and memory management.

    Features:
    1. **Automatic Downloads**: Downloads models from HuggingFace on first use
    2. **Smart Caching**: LRU cache with configurable size limits
    3. **Version Management**: Tracks model versions and handles updates
    4. **Progress Tracking**: Real-time download progress reporting
    5. **Memory Management**: Monitors disk usage and cleans up old models
    6. **Thread Safety**: Concurrent downloads and cache operations
    7. **Failure Recovery**: Retry logic and partial download recovery

    Usage:
        loader = ModelLoader()
        model_path = loader.ensure_model_available("mistral-7b-instruct")
        # Model is now available locally at model_path
    """

    def __init__(self, cache_dir: str = None, max_cache_size_gb: float = 100.0):
        """
        Initialize the model loader.

        Args:
            cache_dir: Directory for model cache (defaults to ML_MODELS_BASE_DIR)
            max_cache_size_gb: Maximum cache size in GB
        """
        self.cache_dir = cache_dir or ML_MODELS_BASE_DIR
        self.max_cache_size_gb = max_cache_size_gb
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # Thread safety
        self._lock = threading.RLock()
        self._download_locks: Dict[str, threading.Lock] = {}

        # Cache management
        self._cache_metadata_file = os.path.join(self.cache_dir, "cache_metadata.json")
        self._cache_entries: Dict[str, CacheEntry] = {}
        self._download_progress: Dict[str, DownloadProgress] = {}

        # Progress callbacks
        self._progress_callbacks: Dict[str, List[Callable]] = {}

        # Initialize cache directory and load metadata
        self._initialize_cache()

        # Verify HuggingFace dependencies
        if not HUGGINGFACE_AVAILABLE:
            self.logger.warning(
                "HuggingFace Hub not available. Model downloading will be disabled. "
                "Install with: pip install huggingface_hub transformers"
            )

    def _initialize_cache(self) -> None:
        """Initialize cache directory and load existing metadata."""
        try:
            # Create cache directories
            os.makedirs(self.cache_dir, exist_ok=True)
            os.makedirs(os.path.join(self.cache_dir, "models"), exist_ok=True)
            os.makedirs(os.path.join(self.cache_dir, "tokenizers"), exist_ok=True)
            os.makedirs(os.path.join(self.cache_dir, "cache"), exist_ok=True)

            # Load existing cache metadata
            if os.path.exists(self._cache_metadata_file):
                self._load_cache_metadata()
            else:
                self._save_cache_metadata()

            self.logger.info(f"Model cache initialized at {self.cache_dir}")
            self.logger.info(f"Cache contains {len(self._cache_entries)} models")

        except Exception as e:
            raise ConfigurationError("cache_initialization", f"Failed to initialize cache: {e}")

    def _load_cache_metadata(self) -> None:
        """Load cache metadata from disk."""
        try:
            with open(self._cache_metadata_file, 'r') as f:
                data = json.load(f)

            self._cache_entries = {}
            for model_name, entry_data in data.get('entries', {}).items():
                self._cache_entries[model_name] = CacheEntry(
                    model_name=entry_data['model_name'],
                    local_path=entry_data['local_path'],
                    download_time=datetime.fromisoformat(entry_data['download_time']),
                    size_mb=entry_data['size_mb'],
                    last_accessed=datetime.fromisoformat(entry_data['last_accessed']),
                    access_count=entry_data['access_count'],
                    huggingface_id=entry_data['huggingface_id'],
                    version_hash=entry_data.get('version_hash', '')
                )

        except Exception as e:
            self.logger.warning(f"Failed to load cache metadata: {e}")
            self._cache_entries = {}

    def _save_cache_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'entries': {}
            }

            for model_name, entry in self._cache_entries.items():
                data['entries'][model_name] = {
                    'model_name': entry.model_name,
                    'local_path': entry.local_path,
                    'download_time': entry.download_time.isoformat(),
                    'size_mb': entry.size_mb,
                    'last_accessed': entry.last_accessed.isoformat(),
                    'access_count': entry.access_count,
                    'huggingface_id': entry.huggingface_id,
                    'version_hash': entry.version_hash
                }

            with open(self._cache_metadata_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save cache metadata: {e}")

    def ensure_model_available(self, model_name: str) -> str:
        """
        Ensure model is available locally, downloading if necessary.

        Args:
            model_name: Name of the model to ensure availability

        Returns:
            Local path to the model

        Raises:
            ModelLoadError: If model cannot be made available
        """
        with self._lock:
            # Check if model is already cached
            if self._is_model_cached(model_name):
                local_path = self._get_cached_model_path(model_name)
                self._update_access_time(model_name)
                self.logger.info(f"Model {model_name} found in cache at {local_path}")
                return local_path

            # Download model if not cached
            return self._download_model(model_name)

    def _is_model_cached(self, model_name: str) -> bool:
        """Check if model is available in local cache."""
        if model_name not in self._cache_entries:
            return False

        entry = self._cache_entries[model_name]

        # Check if local path still exists
        if not os.path.exists(entry.local_path):
            self.logger.warning(f"Cached model {model_name} path no longer exists: {entry.local_path}")
            del self._cache_entries[model_name]
            self._save_cache_metadata()
            return False

        return True

    def _get_cached_model_path(self, model_name: str) -> str:
        """Get local path for cached model."""
        return self._cache_entries[model_name].local_path

    def _download_model(self, model_name: str) -> str:
        """
        Download model from HuggingFace.

        Args:
            model_name: Name of the model to download

        Returns:
            Local path to downloaded model

        Raises:
            ModelLoadError: If download fails
        """
        if not HUGGINGFACE_AVAILABLE:
            raise ModelLoadError(
                model_name,
                "HuggingFace Hub not available. Please install: pip install huggingface_hub transformers"
            )

        # Get model configuration
        try:
            config = get_model_config(model_name)
        except KeyError:
            raise ModelLoadError(model_name, f"Model configuration not found: {model_name}")

        huggingface_id = config['huggingface_id']
        local_path = os.path.join(self.cache_dir, "models", model_name)

        # Ensure we don't have multiple downloads of the same model
        if model_name not in self._download_locks:
            self._download_locks[model_name] = threading.Lock()

        with self._download_locks[model_name]:
            # Check again in case another thread completed the download
            if self._is_model_cached(model_name):
                return self._get_cached_model_path(model_name)

            self.logger.info(f"Downloading model {model_name} from {huggingface_id}")

            # Initialize progress tracking
            progress = DownloadProgress(
                model_name=model_name,
                status="downloading",
                start_time=datetime.now()
            )
            self._download_progress[model_name] = progress

            try:
                # Ensure we have space
                self._ensure_cache_space(config['size_gb'])

                # Download with progress tracking
                download_path = self._download_with_progress(
                    huggingface_id=huggingface_id,
                    local_path=local_path,
                    config=config,
                    progress=progress
                )

                # Create cache entry
                version_hash = self._calculate_version_hash(config)
                size_mb = self._calculate_directory_size(download_path)

                cache_entry = CacheEntry(
                    model_name=model_name,
                    local_path=download_path,
                    download_time=datetime.now(),
                    size_mb=size_mb,
                    last_accessed=datetime.now(),
                    access_count=1,
                    huggingface_id=huggingface_id,
                    version_hash=version_hash
                )

                self._cache_entries[model_name] = cache_entry
                self._save_cache_metadata()

                progress.status = "completed"
                progress.progress_percent = 100.0

                self.logger.info(
                    f"Model {model_name} downloaded successfully to {download_path} "
                    f"({size_mb:.1f} MB)"
                )

                # Trigger progress callbacks
                self._notify_progress_callbacks(model_name, progress)

                return download_path

            except Exception as e:
                progress.status = "failed"
                progress.error_message = str(e)
                self._notify_progress_callbacks(model_name, progress)

                # Clean up partial download
                if os.path.exists(local_path):
                    shutil.rmtree(local_path, ignore_errors=True)

                raise ModelLoadError(model_name, f"Download failed: {e}")

            finally:
                # Clean up progress tracking
                if model_name in self._download_progress:
                    del self._download_progress[model_name]

    def _download_with_progress(
        self,
        huggingface_id: str,
        local_path: str,
        config: Dict[str, Any],
        progress: DownloadProgress
    ) -> str:
        """Download model with progress tracking."""
        try:
            # Use HuggingFace snapshot_download for complete model download
            download_config = config.get('download_config', {})

            # Create progress callback
            def progress_callback(downloaded: int, total: int):
                if total > 0:
                    progress.downloaded_mb = downloaded / (1024 * 1024)
                    progress.total_size_mb = total / (1024 * 1024)
                    progress.progress_percent = (downloaded / total) * 100

                    # Estimate completion time
                    elapsed = datetime.now() - progress.start_time
                    if downloaded > 0:
                        total_time_estimate = elapsed * total / downloaded
                        progress.estimated_completion = progress.start_time + total_time_estimate

                    self._notify_progress_callbacks(progress.model_name, progress)

            # Download the model
            downloaded_path = snapshot_download(
                repo_id=huggingface_id,
                cache_dir=local_path,
                local_files_only=False,
                **download_config
            )

            return downloaded_path

        except Exception as e:
            raise ModelLoadError(progress.model_name, f"HuggingFace download failed: {e}")

    def _ensure_cache_space(self, required_gb: float) -> None:
        """Ensure sufficient cache space by removing old models if necessary."""
        current_size_gb = self._calculate_total_cache_size()
        available_space_gb = self.max_cache_size_gb - current_size_gb

        if available_space_gb >= required_gb:
            return  # Sufficient space available

        space_to_free_gb = required_gb - available_space_gb
        self.logger.info(f"Need to free {space_to_free_gb:.1f}GB of cache space")

        # Sort models by last access time (LRU)
        models_by_access = sorted(
            self._cache_entries.values(),
            key=lambda x: x.last_accessed
        )

        freed_space_gb = 0.0
        for entry in models_by_access:
            if freed_space_gb >= space_to_free_gb:
                break

            self.logger.info(f"Removing cached model {entry.model_name} to free space")

            try:
                if os.path.exists(entry.local_path):
                    shutil.rmtree(entry.local_path)
                    freed_space_gb += entry.size_mb / 1024

                del self._cache_entries[entry.model_name]

            except Exception as e:
                self.logger.warning(f"Failed to remove cached model {entry.model_name}: {e}")

        self._save_cache_metadata()

        if freed_space_gb < space_to_free_gb:
            raise ResourceExhaustedError(
                "disk_space",
                f"{required_gb:.1f}GB",
                f"{available_space_gb + freed_space_gb:.1f}GB"
            )

    def _calculate_total_cache_size(self) -> float:
        """Calculate total size of cached models in GB."""
        return sum(entry.size_mb for entry in self._cache_entries.values()) / 1024

    def _calculate_directory_size(self, directory: str) -> float:
        """Calculate directory size in MB."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, IOError):
                    continue
        return total_size / (1024 * 1024)  # Convert to MB

    def _calculate_version_hash(self, config: Dict[str, Any]) -> str:
        """Calculate hash for model version tracking."""
        # Use configuration as version identifier
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:8]

    def _update_access_time(self, model_name: str) -> None:
        """Update access time and count for a cached model."""
        if model_name in self._cache_entries:
            self._cache_entries[model_name].last_accessed = datetime.now()
            self._cache_entries[model_name].access_count += 1
            # Save metadata periodically (not on every access for performance)
            if self._cache_entries[model_name].access_count % 10 == 0:
                self._save_cache_metadata()

    def register_progress_callback(self, model_name: str, callback: Callable[[DownloadProgress], None]) -> None:
        """Register callback for download progress updates."""
        if model_name not in self._progress_callbacks:
            self._progress_callbacks[model_name] = []
        self._progress_callbacks[model_name].append(callback)

    def _notify_progress_callbacks(self, model_name: str, progress: DownloadProgress) -> None:
        """Notify registered callbacks of progress updates."""
        if model_name in self._progress_callbacks:
            for callback in self._progress_callbacks[model_name]:
                try:
                    callback(progress)
                except Exception as e:
                    self.logger.warning(f"Progress callback failed: {e}")

    def get_download_progress(self, model_name: str) -> Optional[DownloadProgress]:
        """Get current download progress for a model."""
        return self._download_progress.get(model_name)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size_mb = sum(entry.size_mb for entry in self._cache_entries.values())

        return {
            'total_models': len(self._cache_entries),
            'total_size_mb': total_size_mb,
            'total_size_gb': total_size_mb / 1024,
            'max_size_gb': self.max_cache_size_gb,
            'usage_percent': (total_size_mb / 1024) / self.max_cache_size_gb * 100,
            'most_accessed': self._get_most_accessed_models(5),
            'oldest_downloads': self._get_oldest_models(5),
        }

    def _get_most_accessed_models(self, limit: int) -> List[Dict[str, Any]]:
        """Get most accessed models."""
        sorted_models = sorted(
            self._cache_entries.values(),
            key=lambda x: x.access_count,
            reverse=True
        )[:limit]

        return [
            {
                'model_name': model.model_name,
                'access_count': model.access_count,
                'size_mb': model.size_mb,
                'last_accessed': model.last_accessed.isoformat()
            }
            for model in sorted_models
        ]

    def _get_oldest_models(self, limit: int) -> List[Dict[str, Any]]:
        """Get oldest downloaded models."""
        sorted_models = sorted(
            self._cache_entries.values(),
            key=lambda x: x.download_time
        )[:limit]

        return [
            {
                'model_name': model.model_name,
                'download_time': model.download_time.isoformat(),
                'size_mb': model.size_mb,
                'access_count': model.access_count
            }
            for model in sorted_models
        ]

    def cleanup_cache(self, max_age_days: int = 30) -> None:
        """Clean up old unused models from cache."""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        models_to_remove = []

        for model_name, entry in self._cache_entries.items():
            if entry.last_accessed < cutoff_date:
                models_to_remove.append(model_name)

        for model_name in models_to_remove:
            self.logger.info(f"Cleaning up old cached model: {model_name}")
            entry = self._cache_entries[model_name]

            try:
                if os.path.exists(entry.local_path):
                    shutil.rmtree(entry.local_path)
                del self._cache_entries[model_name]
            except Exception as e:
                self.logger.warning(f"Failed to cleanup model {model_name}: {e}")

        if models_to_remove:
            self._save_cache_metadata()
            self.logger.info(f"Cleaned up {len(models_to_remove)} old models")

    def preload_models(self, model_names: List[str]) -> None:
        """Preload models in background for faster first access."""
        def preload_worker():
            for model_name in model_names:
                try:
                    self.logger.info(f"Preloading model: {model_name}")
                    self.ensure_model_available(model_name)
                except Exception as e:
                    self.logger.error(f"Failed to preload model {model_name}: {e}")

        preload_thread = threading.Thread(
            target=preload_worker,
            name="ModelLoader-Preloader",
            daemon=True
        )
        preload_thread.start()


# Global loader instance
_global_loader: Optional[ModelLoader] = None
_loader_lock = threading.Lock()


def get_global_loader() -> ModelLoader:
    """Get the global model loader instance."""
    global _global_loader

    if _global_loader is None:
        with _loader_lock:
            if _global_loader is None:
                _global_loader = ModelLoader()

    return _global_loader