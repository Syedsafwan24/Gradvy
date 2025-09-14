# Local ML Models Storage

This directory contains locally hosted machine learning models for the Gradvy learning platform.

## Directory Structure

```
ML_Models/
├── models/         # Model weights and architecture files
├── tokenizers/     # Tokenizer files for text processing
├── cache/          # Model loading cache (auto-generated)
├── configs/        # Model configuration files
└── README.md       # This file
```

## Supported Models

### 1. Code Generation & Evaluation
- **CodeLlama-7B-Instruct**: Code generation, explanation, and debugging
- **StarCoder-7B**: Code completion and analysis

### 2. Text Generation & Questions
- **Mistral-7B-Instruct**: General instruction following and content generation
- **FLAN-T5-XL**: Structured question generation and educational content

### 3. Embeddings & Similarity
- **sentence-transformers/all-MiniLM-L6-v2**: Text embeddings for content matching
- **CodeBERT**: Code similarity and semantic understanding

## Prerequisites & Installation

First install ML dependencies:

```bash
# From the backend directory
pip install -r requirements.txt
```

Models are automatically downloaded when first accessed by the ML services. Manual installation:

```bash
# From the backend directory
python manage.py download_models --model=mistral-7b-instruct
python manage.py download_models --model=codellama-7b-instruct
python manage.py download_models --all
```

## Storage Requirements

- **Mistral-7B**: ~13GB
- **CodeLlama-7B**: ~13GB
- **FLAN-T5-XL**: ~11GB
- **Embedding Models**: ~400MB total

**Total Estimated**: ~40GB for full model suite

## Configuration

Model configurations are stored in `ml_services/configs/model_configs.py` and override configs in `configs/` directory.

## Privacy & Security

- Models run locally - no data sent to external APIs
- User data is sanitized before model processing
- Models operate in isolated environments
- Audit logs track all model interactions

## Performance Optimization

- Models use quantization for reduced memory usage
- Intelligent caching prevents redundant loading
- Batch processing for multiple requests
- GPU acceleration when available

## Monitoring

Model performance and resource usage tracked via:
- Memory usage monitoring
- Inference latency tracking
- Error rate monitoring
- Cache hit/miss rates