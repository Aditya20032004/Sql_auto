# Text-to-SQL Generator

AI model that converts natural language to SQL queries using TensorFlow.

## Functionality:
✅ Complete TensorFlow training pipeline
✅ Spider dataset integration (8000 examples)
✅ Gradio web interface
✅ Fuzzy accuracy metrics
✅ Trained model excluded (too large for git)

## Tech Stack
- **Model**: Google Flan-T5-base (250M parameters)
- **Framework**: TensorFlow 2.15 + CUDA 12.2
- **Dataset**: Spider (8,035 examples)
- **Interface**: Gradio

## Performance
- **Semantic Similarity**: 71.7%
- **Keyword Match**: 91.8%
- **Exact Match**: 15.8%

## Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Train model**
```bash
python -m examples.train_pipelines
```

3. **Run web interface**
```bash
python app.py
```

## Project Structure
```
├── src/
│   ├── dataset_builder.py    # Spider dataset loader
│   ├── model_trainer.py       # Training pipeline
│   └── model_loader.py        # Inference engine
├── examples/
│   ├── train_pipelines.py     # Training script
│   └── test_fuzzy_accuracy.py # Evaluation metrics
├── app.py                     # Gradio web UI
└── data/
    └── processed/             # Spider dataset
```

## Usage

**Training**
```python
from src.dataset_builder import spider_dataset
from src.model_trainer import train

dataset = spider_dataset(max_examples=8000)
train(dataset, epochs=5, learning_rate=0.0001, batch_size=4)
```

**Inference**
```python
from src.model_loader import load_model, generate

model, tokenizer = load_model()
sql = generate("Find all students with GPA above 3.5", model, tokenizer)
```

## Requirements
- Python 3.9+
- NVIDIA GPU with 6GB+ VRAM (recommended)
- CUDA 12.2 + cuDNN 8.9.7
