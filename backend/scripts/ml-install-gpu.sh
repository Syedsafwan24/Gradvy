#!/bin/bash
# backend/scripts/ml-install-gpu.sh
# Install ML dependencies for systems with NVIDIA GPU
# RELEVANT FILES: requirements-ml-base.txt, requirements-ml-gpu.txt

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================"
echo "Gradvy ML GPU Installation"
echo "========================================"
echo ""

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}✗ Error: No NVIDIA GPU detected${NC}"
    echo ""
    echo "This script requires an NVIDIA GPU."
    echo "For CPU-only installation, use: ./scripts/ml-install-cpu.sh"
    exit 1
fi

echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
echo ""
nvidia-smi --query-gpu=name,memory.total,driver_version,cuda_version --format=csv,noheader
echo ""

# Install base dependencies first
echo "========================================="
echo "Step 1: Installing base ML dependencies"
echo "========================================="
echo ""

pip install -r requirements-ml-base.txt

echo ""
echo -e "${GREEN}✓ Base dependencies installed${NC}"

# Install GPU-specific dependencies
echo ""
echo "========================================="
echo "Step 2: Installing GPU acceleration"
echo "========================================="
echo ""
echo "Select CUDA version:"
echo "  1) CUDA 11.8 (recommended - RTX 20/30/40 series, Tesla, A100)"
echo "  2) CUDA 12.1 (newer GPUs - RTX 40 series with latest drivers)"
echo ""
read -p "Choice [1-2]: " cuda_choice
cuda_choice=${cuda_choice:-1}

echo ""
if [ "$cuda_choice" = "2" ]; then
    echo "Installing PyTorch with CUDA 12.1..."
    echo "Download size: ~2-3 GB"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    echo "Installing PyTorch with CUDA 11.8..."
    echo "Download size: ~2-3 GB"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
fi

echo ""
echo "Installing bitsandbytes (quantization library)..."
pip install bitsandbytes>=0.39.0

echo ""
echo -e "${GREEN}✓ GPU installation complete${NC}"

# Verify installation
echo ""
echo "========================================="
echo "Verification"
echo "========================================="
echo ""

python -c "
import sys
import torch
import transformers
import sentence_transformers

print('Installation Details:')
print(f'  PyTorch: {torch.__version__}')
print(f'  Transformers: {transformers.__version__}')
print(f'  Sentence-Transformers: {sentence_transformers.__version__}')
print('')
print('GPU Information:')
print(f'  CUDA available: {torch.cuda.is_available()}')

if torch.cuda.is_available():
    print(f'  CUDA version: {torch.version.cuda}')
    print(f'  GPU count: {torch.cuda.device_count()}')
    print(f'  GPU name: {torch.cuda.get_device_name(0)}')
    print(f'  GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('  WARNING: CUDA not available! GPU installation may have failed.')
    sys.exit(1)

print('')
try:
    import bitsandbytes
    print('  Quantization: Available (bitsandbytes installed)')
except ImportError:
    print('  Quantization: Not available (bitsandbytes not installed)')

print('')
print('✓ GPU installation verified successfully!')
" || {
    echo ""
    echo -e "${RED}✗ Verification failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check CUDA drivers: nvidia-smi"
    echo "  2. Verify CUDA version matches PyTorch"
    echo "  3. See: docs/ML_SETUP.md for help"
    exit 1
}

echo ""
echo "Next steps:"
echo "  1. Run: python test_ml_setup.py (comprehensive verification)"
echo "  2. See: docs/ML_SETUP.md (complete setup guide)"
echo ""
