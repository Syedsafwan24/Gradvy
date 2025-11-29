# ML Setup Guide - Gradvy AI-Powered Learning Platform

Complete guide for installing and configuring ML dependencies for Gradvy's AI-powered learning path features.

## Table of Contents

1. [Overview](#overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Quick Installation](#quick-installation)
4. [CPU Installation Guide](#cpu-installation-guide)
5. [GPU Installation Guide](#gpu-installation-guide)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Model Storage](#model-storage)
9. [Development Mode](#development-mode)
10. [Performance Tips](#performance-tips)

---

## Overview

Gradvy uses local ML models for:
- **Learning Path Generation**: Personalized course recommendations
- **Question Generation**: AI-powered quiz creation
- **Code Evaluation**: Automated code review and feedback

### Supported Models

| Model | Type | Size | Purpose |
|-------|------|------|---------|
| Mistral-7B-Instruct | Text Generation | 13 GB | Learning paths, content generation |
| Phi-3-Mini | Text Generation | 7 GB | Quick responses, Q&A |
| CodeLlama-7B | Code Generation | 13 GB | Code explanation, debugging |
| StarCoder-7B | Code Generation | 13 GB | Code completion |
| FLAN-T5-XL | Question Generation | 11 GB | Quiz creation, assessments |
| All-MiniLM-L6-v2 | Embeddings | 0.4 GB | Content matching |
| CodeBERT | Embeddings | 0.5 GB | Code similarity |

**Total Storage**: ~40 GB for full suite, ~10 GB for minimal setup

---

## Hardware Requirements

### CPU-Only Systems

**Minimum**:
- 8 GB RAM
- 20 GB disk space
- Any modern CPU (Intel/AMD)

**Recommended**:
- 16 GB RAM
- 50 GB disk space
- Multi-core CPU

**Performance**: Slower inference (5-30 seconds per request), but fully functional

### GPU Systems

**Minimum**:
- NVIDIA GPU with 8 GB VRAM
- 16 GB RAM
- 50 GB disk space
- CUDA 11.8 or 12.1

**Recommended**:
- NVIDIA GPU with 16+ GB VRAM (RTX 3090, RTX 4090, A100)
- 32 GB RAM
- 100 GB disk space

**Supported GPUs**:
- RTX 20/30/40 series
- Tesla T4, V100, A100
- GTX 1080 Ti and newer (with enough VRAM)

**Performance**: Fast inference (1-5 seconds per request) with quantization

---

## Quick Installation

### Option 1: Auto-Detect (Recommended)

```bash
cd backend
./scripts/ml-install.sh
```

This script:
1. Detects your hardware (CPU/GPU)
2. Installs appropriate dependencies
3. Verifies installation
4. Provides next steps

### Option 2: Manual CPU Installation

```bash
cd backend
pip install -r requirements-ml-base.txt
python test_ml_setup.py
```

### Option 3: Manual GPU Installation

```bash
cd backend
./scripts/ml-install-gpu.sh
python test_ml_setup.py
```

---

## CPU Installation Guide

### Step-by-Step

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install CPU dependencies**:
   ```bash
   pip install -r requirements-ml-cpu.txt
   ```

   Or use the script:
   ```bash
   ./scripts/ml-install-cpu.sh
   ```

3. **Verify installation**:
   ```bash
   python test_ml_setup.py
   ```

### What Gets Installed

- PyTorch (CPU version) - ~500 MB
- Transformers - ~50 MB
- Sentence-Transformers - ~30 MB
- HuggingFace Hub - ~20 MB
- Supporting libraries

**Total download**: ~1-2 GB
**Installation time**: 5-10 minutes

### Performance Expectations

- **Inference time**: 5-30 seconds per request
- **Memory usage**: 4-8 GB RAM per model
- **Quantization**: Disabled (models run in float16)
- **Use case**: Development, testing, small-scale deployments

---

## GPU Installation Guide

### Prerequisites

1. **NVIDIA GPU** with 8+ GB VRAM
2. **NVIDIA Drivers** installed
   ```bash
   nvidia-smi  # Should show GPU info
   ```
3. **CUDA Toolkit** (optional, PyTorch includes necessary CUDA libs)

### Step-by-Step

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Run GPU installation script**:
   ```bash
   ./scripts/ml-install-gpu.sh
   ```

3. **Select CUDA version**:
   - **CUDA 11.8** (recommended) - RTX 20/30/40, Tesla, most GPUs
   - **CUDA 12.1** - Newer RTX 40 series with latest drivers

4. **Verify installation**:
   ```bash
   python test_ml_setup.py
   ```

   Should show:
   ```
   ✓ CUDA available: True
   ✓ Quantization: Available
   ```

### What Gets Installed

**Base dependencies** (from requirements-ml-base.txt):
- PyTorch (CPU version initially) - ~500 MB

**GPU add-ons** (from requirements-ml-gpu.txt):
- PyTorch (GPU version with CUDA) - ~2-3 GB
- bitsandbytes (quantization) - ~10 MB

**Total download**: ~3-4 GB
**Installation time**: 15-25 minutes

### Performance Expectations

- **Inference time**: 1-5 seconds per request
- **Memory usage**: 2-4 GB VRAM per model (with 4-bit quantization)
- **Quantization**: Enabled (4-bit/8-bit compression)
- **Use case**: Production, high-volume, real-time inference

---

## Verification

### Run Test Script

```bash
python test_ml_setup.py
```

### Expected Output

**CPU Installation**:
```
✓ PyTorch version: 2.x.x
○ CUDA available: No (CPU mode)
✓ Transformers version: 4.x.x
✓ Sentence-Transformers version: 2.x.x
○ Quantization skipped on CPU-only systems
✓ Model registry initialized
✓ RAM sufficient for ML operations
✓ All tests passed! ML setup is ready.
```

**GPU Installation**:
```
✓ PyTorch version: 2.x.x
✓ CUDA available: Yes
  CUDA version: 11.8
  GPU: NVIDIA RTX 3090 (24.0 GB)
✓ Transformers version: 4.x.x
✓ Sentence-Transformers version: 2.x.x
✓ bitsandbytes installed
✓ BitsAndBytesConfig available
✓ Model registry initialized
✓ All tests passed! ML setup is ready.
```

### Manual Verification

```python
# Test PyTorch and CUDA
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Test quantization
python -c "import bitsandbytes; print('Quantization: OK')"

# Test model registry
python -c "from ml_services.utils.model_registry import ModelRegistry; registry = ModelRegistry(); print('Registry: OK')"
```

---

## Troubleshooting

### Network Errors During Installation

**Problem**: `ConnectionResetError` or timeout during pip install

**Solutions**:
1. **Retry with increased timeout**:
   ```bash
   pip install -r requirements-ml-base.txt --timeout=1000 --retries=10
   ```

2. **Use PyTorch CDN** (more reliable):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Install incrementally**:
   ```bash
   pip install torch
   pip install transformers
   pip install sentence-transformers
   # ... etc
   ```

### CUDA Not Available After GPU Installation

**Problem**: `torch.cuda.is_available()` returns `False`

**Diagnosis**:
```bash
# Check NVIDIA driver
nvidia-smi

# Check PyTorch version
python -c "import torch; print(torch.__version__)"
```

**Solutions**:
1. **Verify CUDA version matches**:
   ```bash
   # Check driver CUDA version
   nvidia-smi | grep "CUDA Version"

   # Should match PyTorch installation
   ```

2. **Reinstall GPU PyTorch**:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Try different CUDA version**:
   ```bash
   # For CUDA 12.1
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### bitsandbytes Import Error

**Problem**: `ImportError: cannot import name 'BitsAndBytesConfig'`

**Cause**: bitsandbytes not installed (CPU setup) or incompatible version

**Solution**:
```bash
# For GPU systems
pip install bitsandbytes>=0.39.0

# For CPU systems - this is normal, quantization disabled
# No action needed
```

### Out of Memory (OOM) Errors

**Problem**: `RuntimeError: CUDA out of memory` or system freeze

**Solutions**:

1. **Enable aggressive quantization** (reduces memory by 4x):
   ```python
   # Models automatically use 4-bit quantization on GPU
   # Already configured in model_configs.py
   ```

2. **Use smaller models**:
   ```python
   # In development profile:
   # - phi-3-mini (7 GB) instead of mistral-7b (13 GB)
   # - all-minilm-l6-v2 (0.4 GB) for embeddings
   ```

3. **Increase system swap** (Linux):
   ```bash
   sudo fallocate -l 16G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Model Download Failures

**Problem**: HuggingFace download timeout or incomplete

**Solutions**:
1. **Check connection**:
   ```bash
   curl -I https://huggingface.co
   ```

2. **Manual download**:
   ```bash
   # Models auto-download on first use
   # Or pre-download:
   python -c "from transformers import AutoModel; AutoModel.from_pretrained('microsoft/Phi-3-mini-4k-instruct')"
   ```

3. **Use HuggingFace token** (for gated models):
   ```bash
   export HF_TOKEN="your_token_here"
   ```

---

## Model Storage

### Storage Locations

**Models directory**: `backend/core/ML_Models/`

**Structure**:
```
ML_Models/
├── models/              # Model weights
│   ├── mistral-7b-instruct/
│   ├── phi-3-mini/
│   ├── codellama-7b-instruct/
│   └── ...
├── tokenizers/          # Tokenizer files
├── cache/               # HuggingFace cache
└── configs/             # Model configs
```

### Disk Space Management

**Check storage**:
```bash
du -sh ML_Models/
```

**Clear cache**:
```bash
rm -rf ML_Models/cache/*
```

**Remove specific model**:
```bash
rm -rf ML_Models/models/model-name/
```

### Model Download Behavior

- **Lazy loading**: Models download on first use
- **Caching**: Downloaded models are cached
- **LRU eviction**: Least recently used models unloaded automatically
- **Max storage**: Configurable in `model_configs.py`

---

## Development Mode

### Running Without Models

For development/testing without downloading 40+ GB models:

1. **Install dependencies only**:
   ```bash
   pip install -r requirements-ml-base.txt
   ```

2. **Skip model initialization**:
   ```python
   # Models don't load until first use
   # Services gracefully handle missing models
   ```

3. **Mock ML responses** (optional):
   ```python
   # In settings.py
   ML_MOCK_MODE = True  # Returns placeholder responses
   ```

### Development Profile

The `development` deployment profile:
- Uses smaller models (Phi-3, MiniLM)
- Allows CPU-only operation
- Aggressive quantization
- 12 GB memory limit
- Auto-unloads unused models

**Activate**:
```python
from ml_services.utils.model_registry import ModelRegistry
registry = ModelRegistry(deployment_profile='development')
```

---

## Performance Tips

### For CPU Users

1. **Use smaller models**:
   - Phi-3-Mini (7 GB) instead of Mistral (13 GB)
   - All-MiniLM-L6-v2 for embeddings

2. **Reduce batch size**:
   ```python
   # Generate one item at a time
   ```

3. **Use caching**:
   - Cache frequent queries
   - Store embeddings in MongoDB

4. **Consider GPU cloud** (production):
   - AWS SageMaker
   - Google Vertex AI
   - RunPod, Lambda Labs (cheap GPU rentals)

### For GPU Users

1. **Enable quantization** (already default):
   - 4-bit: 75% memory savings, minimal quality loss
   - 8-bit: 50% memory savings, no quality loss

2. **Use mixed precision**:
   ```python
   # Already configured in model configs
   torch_dtype="float16"
   ```

3. **Batch requests**:
   - Process multiple requests together
   - Better GPU utilization

4. **Monitor VRAM**:
   ```python
   import torch
   print(torch.cuda.memory_summary())
   ```

### For Production

1. **Use deployment profiles**:
   - `production_small`: 24 GB RAM, curated models
   - `production_large`: 64 GB RAM, all models

2. **Scale horizontally**:
   - Multiple instances with load balancer
   - Dedicated ML service containers

3. **Use model caching**:
   - Keep hot models loaded
   - Pre-warm at startup

4. **Monitor performance**:
   - Track inference times
   - Memory usage per model
   - Request queue depth

---

## Next Steps

After successful installation:

1. **Start development server**:
   ```bash
   ./scripts/local-dev.sh
   ```

2. **Test ML endpoints**:
   ```bash
   # Learning path generation
   curl -X POST http://localhost:8000/api/ml/learning-path \
     -H "Content-Type: application/json" \
     -d '{"goal": "Learn Python", "level": "beginner"}'
   ```

3. **Monitor model usage**:
   ```bash
   # Flower UI (Celery task monitoring)
   ./scripts/local-flower.sh
   # Visit: http://localhost:5555
   ```

4. **Explore model registry**:
   ```python
   from ml_services.utils.model_registry import get_global_registry
   registry = get_global_registry()
   print(registry.get_all_model_status())
   ```

---

## Additional Resources

- **Model Configs**: `backend/ml_services/configs/model_configs.py`
- **Registry Code**: `backend/ml_services/utils/model_registry.py`
- **Services**: `backend/ml_services/services/`
- **HuggingFace Models**: https://huggingface.co/models
- **PyTorch Docs**: https://pytorch.org/docs/
- **Transformers Docs**: https://huggingface.co/docs/transformers

---

## Support

**Issues?**
- See: `docs/TROUBLESHOOTING.md`
- Check: `test_ml_setup.py` output
- Ask: Team Slack #ml-setup channel

**Contributing**:
- Report bugs: GitHub Issues
- Suggest models: Team discussions
- Optimize: Submit PRs with benchmarks
