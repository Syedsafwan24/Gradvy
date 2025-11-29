#!/bin/bash
# backend/scripts/ml-install-cpu.sh
# Install ML dependencies for CPU-only systems (no NVIDIA GPU)
# RELEVANT FILES: requirements-ml-cpu.txt, requirements-ml-base.txt

set -e

echo "========================================"
echo "Gradvy ML CPU-Only Installation"
echo "========================================"
echo ""
echo "Installing ML dependencies for CPU-only systems..."
echo "Download size: ~1-2 GB"
echo ""

# Install CPU dependencies
pip install -r requirements-ml-cpu.txt

echo ""
echo "✓ CPU-only installation complete"
echo ""
echo "Installation details:"
python -c "
import torch
import transformers
import sentence_transformers

print(f'  PyTorch: {torch.__version__}')
print(f'  Transformers: {transformers.__version__}')
print(f'  Sentence-Transformers: {sentence_transformers.__version__}')
print(f'  Device: CPU')
print(f'  Quantization: Disabled (CPU mode)')
print('')
print('✓ ML dependencies installed successfully!')
print('')
print('Note: Models will run in float16 without quantization.')
print('Performance will be slower than GPU, but fully functional.')
"

echo ""
echo "Next steps:"
echo "  1. Run: python test_ml_setup.py (verify installation)"
echo "  2. See: docs/ML_SETUP.md (complete setup guide)"
echo ""
