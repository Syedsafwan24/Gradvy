"""
backend/test_ml_setup.py
Verification script for ML dependencies installation
Tests all ML components and provides comprehensive diagnostics
RELEVANT FILES: requirements-ml-base.txt, requirements-ml-gpu.txt, ml_services/
"""

import sys
import os

# Colors for terminal output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_header(text):
    """Print a colored header"""
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'=' * 60}{NC}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{NC}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}○ {text}{NC}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{NC}")


def test_pytorch():
    """Test PyTorch installation"""
    print_header("PyTorch Installation")

    try:
        import torch
        print_success(f"PyTorch version: {torch.__version__}")

        # Check CUDA availability
        if torch.cuda.is_available():
            print_success(f"CUDA available: Yes")
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  GPU count: {torch.cuda.device_count()}")

            for i in range(torch.cuda.device_count()):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print(f"  GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")

            return 'gpu'
        else:
            print_warning("CUDA available: No (CPU mode)")
            print("  Note: This is normal for CPU-only installations")
            return 'cpu'

    except ImportError as e:
        print_error(f"PyTorch not installed: {e}")
        return None


def test_transformers():
    """Test Transformers library"""
    print_header("HuggingFace Transformers")

    try:
        import transformers
        print_success(f"Transformers version: {transformers.__version__}")

        # Test core imports
        from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
        print_success("Core imports: OK")

        return True
    except ImportError as e:
        print_error(f"Transformers not installed: {e}")
        return False


def test_sentence_transformers():
    """Test Sentence Transformers"""
    print_header("Sentence Transformers")

    try:
        import sentence_transformers
        print_success(f"Sentence-Transformers version: {sentence_transformers.__version__}")
        return True
    except ImportError as e:
        print_error(f"Sentence-Transformers not installed: {e}")
        return False


def test_quantization(device_type):
    """Test quantization support"""
    print_header("Quantization Support (bitsandbytes)")

    if device_type == 'cpu':
        print_warning("Quantization skipped on CPU-only systems")
        print("  Note: Models will run in float16 without quantization")
        return 'cpu_skipped'

    try:
        import bitsandbytes as bnb
        print_success(f"bitsandbytes installed")

        # Test BitsAndBytesConfig import
        from transformers import BitsAndBytesConfig
        print_success("BitsAndBytesConfig available")

        return True
    except ImportError:
        print_warning("bitsandbytes not installed")
        print("  Install with: pip install -r requirements-ml-gpu.txt")
        return False


def test_model_registry():
    """Test model registry initialization"""
    print_header("Model Registry Initialization")

    try:
        # Add ml_services to path
        sys.path.insert(0, os.path.dirname(__file__))

        from ml_services.utils.model_registry import ModelRegistry
        from ml_services.configs.model_configs import MODEL_REGISTRY, DEPLOYMENT_PROFILES

        print_success(f"Model registry imported")
        print_success(f"Registered models: {len(MODEL_REGISTRY)}")

        # List available models
        print("\n  Available models:")
        for model_name, config in MODEL_REGISTRY.items():
            size = config.get('size_gb', 0)
            model_type = config.get('model_type', 'unknown')
            print(f"    - {model_name} ({model_type}, {size:.1f} GB)")

        # Test registry initialization
        registry = ModelRegistry(deployment_profile='development')
        print_success("Model registry initialized (development profile)")

        # Check deployment profile settings
        dev_profile = DEPLOYMENT_PROFILES['development']
        print(f"\n  Development profile settings:")
        print(f"    Max memory: {dev_profile['max_memory_gb']} GB")
        print(f"    Allow CPU: {dev_profile['allow_cpu_only']}")
        print(f"    Aggressive quantization: {dev_profile['quantization_aggressive']}")
        print(f"    Preferred models: {', '.join(dev_profile['preferred_models'])}")

        return True

    except ImportError as e:
        print_error(f"Failed to import model registry: {e}")
        return False
    except Exception as e:
        print_error(f"Failed to initialize model registry: {e}")
        return False


def test_system_resources():
    """Test system resources"""
    print_header("System Resources")

    try:
        import psutil

        # Memory
        memory = psutil.virtual_memory()
        print(f"  RAM: {memory.total / 1024**3:.1f} GB total")
        print(f"  RAM available: {memory.available / 1024**3:.1f} GB ({memory.percent}% used)")

        # Disk space
        disk = psutil.disk_usage(os.path.dirname(__file__))
        print(f"  Disk: {disk.total / 1024**3:.1f} GB total")
        print(f"  Disk available: {disk.free / 1024**3:.1f} GB ({disk.percent}% used)")

        # CPU
        print(f"  CPU cores: {psutil.cpu_count()}")
        print(f"  CPU usage: {psutil.cpu_percent()}%")

        # Recommendations
        if memory.available / 1024**3 < 8:
            print_warning("Low RAM: Less than 8GB available. May struggle with large models.")
        else:
            print_success(f"RAM sufficient for ML operations")

        if disk.free / 1024**3 < 50:
            print_warning("Low disk space: Less than 50GB free. May not fit all models.")
        else:
            print_success("Disk space sufficient for model storage")

        return True

    except ImportError:
        print_warning("psutil not available, skipping resource check")
        return None


def main():
    """Run all verification tests"""
    print(f"\n{BLUE}Gradvy ML Setup Verification{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")

    # Track results
    results = {}

    # Test PyTorch
    device_type = test_pytorch()
    results['pytorch'] = device_type is not None

    if device_type is None:
        print_error("\nCritical: PyTorch not installed. Cannot continue.")
        print("Install with: pip install -r requirements-ml-base.txt")
        sys.exit(1)

    # Test Transformers
    results['transformers'] = test_transformers()

    # Test Sentence Transformers
    results['sentence_transformers'] = test_sentence_transformers()

    # Test Quantization
    quant_result = test_quantization(device_type)
    results['quantization'] = quant_result

    # Test Model Registry
    results['model_registry'] = test_model_registry()

    # Test System Resources
    results['resources'] = test_system_resources()

    # Final summary
    print_header("Verification Summary")

    passed = sum(1 for v in results.values() if v is True)
    total = len([v for v in results.values() if v is not None and v != 'cpu_skipped'])

    print(f"  Tests passed: {passed}/{total}")
    print(f"  Device type: {device_type.upper()}")

    if device_type == 'cpu':
        print(f"  Mode: CPU-only (quantization disabled)")
    elif results['quantization'] is True:
        print(f"  Mode: GPU with quantization")
    else:
        print(f"  Mode: GPU without quantization")

    print("")

    if all(v for v in results.values() if v is not None and v != 'cpu_skipped'):
        print_success("All tests passed! ML setup is ready.")
        print("")
        print("Next steps:")
        print("  1. Models will auto-download on first use")
        print("  2. See: docs/ML_SETUP.md for usage guide")
        print("  3. Start development server: ./scripts/local-dev.sh")
        return 0
    else:
        print_warning("Some tests failed. Check errors above.")
        print("")
        print("Troubleshooting:")
        print("  1. Reinstall: ./scripts/ml-install.sh")
        print("  2. See: docs/ML_SETUP.md")
        print("  3. Check: docs/TROUBLESHOOTING.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
