#!/bin/bash
# backend/scripts/ml-install.sh
# Gradvy ML Dependency Auto-Installer
# Auto-detects GPU and installs appropriate ML dependencies
# RELEVANT FILES: requirements-ml-base.txt, requirements-ml-gpu.txt, test_ml_setup.py

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "Gradvy ML Dependency Installer"
echo "========================================"
echo ""

# Detect GPU
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
    GPU_AVAILABLE=true

    # Show GPU info
    echo ""
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
else
    echo -e "${YELLOW}✗ No NVIDIA GPU detected${NC}"
    GPU_AVAILABLE=false
fi

# Install base dependencies (CPU-compatible)
echo "========================================"
echo "Step 1: Installing base ML dependencies"
echo "========================================"
echo "This includes: PyTorch (CPU), Transformers, Sentence-Transformers"
echo "Download size: ~1-2 GB"
echo ""

pip install -r requirements-ml-base.txt

echo ""
echo -e "${GREEN}✓ Base ML dependencies installed${NC}"

# Install GPU add-ons if GPU is available
if [ "$GPU_AVAILABLE" = true ]; then
    echo ""
    echo "========================================="
    echo "Step 2: GPU Acceleration (Optional)"
    echo "========================================="
    echo ""
    read -p "Install GPU acceleration (CUDA + quantization)? [Y/n]: " install_gpu
    install_gpu=${install_gpu:-Y}

    if [[ "$install_gpu" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Select CUDA version:"
        echo "  1) CUDA 11.8 (recommended - RTX 20/30/40 series, Tesla)"
        echo "  2) CUDA 12.1 (newer GPUs - RTX 40 series)"
        echo ""
        read -p "Choice [1-2]: " cuda_choice
        cuda_choice=${cuda_choice:-1}

        echo ""
        if [ "$cuda_choice" = "2" ]; then
            echo "Installing PyTorch with CUDA 12.1..."
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        else
            echo "Installing PyTorch with CUDA 11.8..."
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        fi

        echo ""
        echo "Installing bitsandbytes (quantization library)..."
        pip install bitsandbytes>=0.39.0

        echo ""
        echo -e "${GREEN}✓ GPU installation complete${NC}"
        echo ""
        echo "Verifying CUDA setup..."
        python -c "import torch; print(f'  CUDA available: {torch.cuda.is_available()}'); print(f'  CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'  GPU count: {torch.cuda.device_count() if torch.cuda.is_available() else 0}')"
        python -c "import bitsandbytes; print('  bitsandbytes: OK')" 2>/dev/null || echo -e "${YELLOW}  bitsandbytes: Not available${NC}"
    else
        echo ""
        echo -e "${YELLOW}Skipping GPU installation (CPU-only mode)${NC}"
        echo "Note: Quantization disabled, models run in float16"
    fi
else
    echo ""
    echo "========================================="
    echo "CPU-Only Installation Complete"
    echo "========================================="
    echo ""
    echo -e "${YELLOW}Note: Quantization disabled (models run in float16)${NC}"
    echo "This is normal for CPU-only systems."
fi

# Final summary
echo ""
echo "========================================"
echo "Installation Summary"
echo "========================================"
python -c "
import sys
try:
    import torch
    import transformers
    import sentence_transformers

    print(f'✓ PyTorch: {torch.__version__}')
    print(f'✓ Transformers: {transformers.__version__}')
    print(f'✓ Sentence-Transformers: {sentence_transformers.__version__}')
    print(f'✓ Device: {"CUDA" if torch.cuda.is_available() else "CPU"}')

    try:
        import bitsandbytes
        print(f'✓ Quantization: Available')
    except ImportError:
        print(f'○ Quantization: Disabled (CPU mode)')

    print('')
    print('✓ ML dependencies installed successfully!')

except ImportError as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
"

echo ""
echo "Next steps:"
echo "  1. Run: python test_ml_setup.py (verify installation)"
echo "  2. See: docs/ML_SETUP.md (complete setup guide)"
echo ""
