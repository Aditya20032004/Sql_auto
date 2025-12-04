# Text-to-SQL Generator with WikiSQL

A fine-tuned language model that converts natural language questions into executable SQL queries. This project trains Google's Flan-T5-base model on the WikiSQL dataset to generate accurate SQL queries from natural language inputs, with schema-aware context for improved understanding.

## About This Project

This is a complete end-to-end machine learning pipeline for Text-to-SQL generation that:

**What it does:**
- Takes natural language questions + database schema as input
- Generates syntactically correct SQL queries
- Handles single-table queries with WHERE clauses, aggregations, and comparisons
- Validates predictions against ground truth using multiple metrics
- Provides schema-enhanced training for context-aware SQL generation

**Key Features:**
- 🧠 **Schema-Enhanced Training**: Includes CREATE TABLE statements with column names and data types in input context
- 🎯 **Smart Column Handling**: Automatically cleans special characters in column names (spaces, slashes) for SQL compatibility
- 📊 **Comprehensive Validation**: Multi-metric evaluation (exact match, similarity, normalization)
- 🚀 **Production Optimizations**: Beam search, early stopping, GPU memory management
- 💾 **Version Control**: Git LFS integration for managing large model weights (1.2GB)
- 🔍 **Fuzzy Matching**: Normalized SQL comparison to handle formatting variations

## Advantages

**1. Schema-Aware Context**
- Unlike basic text-to-SQL models, includes full table schema in input
- Model learns column names, data types, and table structure
- Reduces hallucination of non-existent columns

**2. Robust Training Pipeline**
- Early stopping with patience to prevent overfitting
- -100 padding masking to ignore pad tokens in loss calculation
- GPU memory growth configuration for efficient VRAM usage
- Full WikiSQL dataset support (56,355 training examples)

**3. Smart Evaluation**
- SQL normalization (whitespace, quotes, case-insensitive comparison)
- Column name cleaning to align training and validation formats
- Similarity scoring alongside exact match for partial credit
- Comprehensive logging of predictions vs expected outputs

**4. Optimized Inference**
- Beam search (num_beams=3) for exploring multiple generation paths
- No repetition constraints to prevent redundant phrases
- Temperature-free deterministic generation for consistency

**5. Real-World Ready**
- Handles messy column names (spaces, special characters)
- Works with single-table SQL queries (SELECT, WHERE, aggregations)
- Extensible to multi-table joins and complex queries
- Clean separation of training, inference, and validation code

## Tech Stack
- **Model**: Google Flan-T5-base (250M parameters)
- **Framework**: TensorFlow 2.15 + CUDA 12.2
- **Dataset**: WikiSQL (56,355 train / 8,421 validation examples)
- **Infrastructure**: Git LFS for model weights
- **GPU**: NVIDIA RTX 4050 (6GB VRAM)

## Performance
**Current Model (10K examples, 30 epochs):**
- **Training Loss**: 0.30 (overfit from 0.19 at 10 epochs)
- **Similarity**: 87.99%
- **Exact Match**: 25.40% (before column name fix)

**Expected (56K examples, beam search + column fix):**
- **Exact Match**: 50-65%
- **Similarity**: 90-95%

## What's Implemented

### ✅ Core Training Features
1. **Schema-Enhanced Dataset Preparation**
   - CREATE TABLE format with column names and SQL data types
   - Column name cleaning (spaces → underscores, slashes → underscores)
   - Input format: `CREATE TABLE table_name (col1 TEXT, col2 REAL);Question: ...`
   - 56,355 WikiSQL training examples loaded from HuggingFace cache

2. **-100 Padding Masking**
   - Replaces pad tokens with -100 in labels (not inputs)
   - Loss function ignores -100 tokens during backpropagation
   - Prevents model from learning to predict padding

3. **Early Stopping**
   - Monitors training loss with patience=5 epochs
   - Automatically restores best weights when training stops
   - Prevents overfitting (proved by 0.19→0.30 loss at 10→30 epochs)

4. **GPU Memory Optimization**
   - TensorFlow memory growth enabled
   - Prevents allocating all 6GB VRAM at startup
   - Allows gradual memory allocation as needed

5. **Full WikiSQL Training Pipeline**
   - Scales from 10K to 56,355 examples (full dataset)
   - Learning rate: 0.00015 (3x default)
   - Max epochs: 20 with early stopping
   - Batch size: 1 (optimal for 6GB GPU, batch_size=4 causes OOM)

### ✅ Inference Optimizations
6. **Beam Search Generation**
   - num_beams=3 (explores 3 generation paths)
   - early_stopping=True (stops when beams complete)
   - no_repeat_ngram_size=2 (prevents phrase repetition)
   - Improves SQL quality over greedy decoding

7. **Deterministic Generation**
   - Removed temperature-based sampling
   - Beam search provides structured exploration
   - More consistent SQL output for production use

### ✅ Validation & Metrics
8. **SQL Normalization for Comparison**
   - Lowercase conversion
   - Whitespace collapse (multiple spaces → single space)
   - Quote standardization (' → ")
   - Operator spacing (= → " = ", , → ", ")

9. **Column Name Alignment**
   - `clean_column_names_in_sql()` function
   - Converts expected SQL from "School/Club Team" to "School_Club_Team"
   - Regex-based word boundary replacement
   - Fixes training vs validation column name mismatch

10. **Dual Metric Evaluation**
    - **Exact Match**: Normalized SQL comparison (0 or 100%)
    - **Similarity**: SequenceMatcher ratio (0-100% fuzzy score)
    - Logs both original and cleaned expected SQL for debugging

### ✅ Version Control & Infrastructure
11. **Git LFS Integration**
    - .gitattributes configured for *.h5 files
    - Successfully tracks 1.2GB model weights (tf_model.h5)
    - Committed and pushed to GitHub (models/trained_wikisql_model/)

12. **Comprehensive Logging**
    - All training steps logged to logs/project.log
    - Validation results with per-example predictions
    - Loss monitoring and early stopping events

### ❌ Not Implemented (Future Work)
- ❌ **Gradient Accumulation**: Simulate batch_size=4 (complex with TF's model.fit())
- ❌ **Hyperparameter Tuning**: Grid search across lr/patience/epochs (time-intensive)
- ❌ **Data Augmentation**: Question paraphrasing, synonym replacement
- ❌ **Constrained Decoding**: Force valid tokens based on schema
- ❌ **Post-Processing**: Convert cleaned columns back to original format
- ❌ **Multi-table Joins**: Currently single-table queries only



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


## Personal loggs
Recommendations (Easiest → Hardest):
Quick Wins (Do These First):
✅ Lower temperature to 0.1 (1 line change, might help 2-5%)
✅ Add beam search num_beams=3 (1 line change, might help 5-10%)
✅ Post-processing of predictions (10 lines, might help 3-5%)(Not required done alternatively)

Medium Effort:
⚠️ Gradient accumulation to simulate batch_size=4 (avoid OOM, might help 5-10%)(cannot perform)
⚠️ Hyperparameter tuning (multiple training runs, might help 5-15%)
Advanced (Later):
❌ Data augmentation (requires building augmentation pipeline)
❌ Constrained decoding (requires SQL parser + custom generation loop)
