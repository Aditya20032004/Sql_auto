# SQL_auto — English to SQL Query Generator

Fine-tuned language model that converts plain English questions into SQL queries, so people who don't know SQL can query a database in normal language. Built and trained end-to-end on a local machine.

## Overview

Most "text-to-SQL" tools are either rule-based pattern matchers or need a paid API and a cloud GPU. This project fine-tunes **Google's Flan-T5-base** (a sequence-to-sequence transformer) on the **WikiSQL** dataset using a **pure TensorFlow backend** (`transformers.TFAutoModelForSeq2SeqLM`, no PyTorch), and trains it **locally on a single laptop** rather than in the cloud — which meant working within tight GPU memory limits (small batch sizes, gradient clipping, early stopping) instead of just scaling up.

Given a table schema and a question in plain English, the model generates the corresponding SQL query.

**Example:**
```
Input:  CREATE TABLE employees (Name TEXT, Department TEXT, Salary REAL);
        Question: What are the names of employees in the Engineering department?

Output: SELECT Name FROM employees WHERE Department = 'Engineering'
```

## Features

- 🧠 Fine-tuned Flan-T5-base seq2seq model (not a rule-based/regex system)
- ⚙️ Pure TensorFlow training and inference pipeline
- 💻 Trained locally — no cloud compute, with memory-growth/GPU config, gradient clipping, and early stopping to work within local hardware limits
- 📊 Trained and validated on the WikiSQL dataset (~56K examples used for training)
- 🖥️ Gradio web app (`app.py`) for interactive querying with schema input
- 🧪 Evaluation scripts with similarity scoring against ground-truth SQL

## Project Structure

```
Sql_auto/
├── app.py                     # Gradio app — interactive SQL generation UI
├── src/
│   ├── dataset_builder.py     # Builds training data (custom examples, Spider, WikiSQL)
│   ├── model_trainer.py       # Fine-tunes Flan-T5 on TensorFlow
│   ├── model_loader.py        # Loads a trained model and generates SQL from a prompt
│   └── core/logger.py         # Logging setup
├── examples/
│   ├── train_pipelines.py     # End-to-end training pipeline (dataset build + train + save)
│   ├── test_trained_models.py # Runs the trained model against sample prompts
│   ├── calculate_accuracy.py  # Quick similarity check on 15 hand-written cases
│   └── wikisql_validation.py  # Full validation run — computes the metrics below
├── models/
│   ├── trained_sql_model/     # Model fine-tuned on hand-written SQL examples
│   └── trained_wikisql_model/ # Model fine-tuned on WikiSQL (used by app.py)
├── data/                      # Processed datasets (WikiSQL, Spider)
├── scripts/                   # Setup and data extraction helpers
├── similarity_analysis.txt    # Logged evaluation runs
└── vercel-deploy/             # Lightweight rule-based demo for quick web hosting
                                # (kept separate since the full TF model is too heavy for serverless)
```

## Setup

```bash
git clone https://github.com/Aditya20032004/Sql_auto.git
cd Sql_auto
pip install -r requirements.txt
```

Requires: `tensorflow==2.15.0`, `transformers==4.30.0`, `datasets`, `gradio==4.44.1`

## Usage

### Run the app locally
```bash
python app.py
```
Enter a schema (`CREATE TABLE ...`) and a question, or just a question to use a default schema, and get a generated SQL query back through the Gradio interface.

### Train the model yourself
```bash
python examples/train_pipelines.py
```
This builds the WikiSQL training set, fine-tunes Flan-T5-base, and saves the model to `models/trained_wikisql_model/`.

### Test a trained model
```bash
python examples/test_trained_models.py
```

## Results

Evaluated on a held-out WikiSQL validation split (`examples/wikisql_validation.py`, 8,421 examples):

| Metric | Score |
|---|---|
| Semantic similarity | **96.14%** |
| Exact match | **61.23%** |
| Training examples | 56,355 |
| Validation examples | 8,421 |
| Final training loss | 0.0206 (epoch 18) |

Most non-exact matches were near misses — a missing `COUNT`, a reordered clause, or a slightly different column reference — rather than structurally wrong queries, which is what the high similarity score vs. lower exact-match score reflects.

## Why this project

This started as an idea to help non-technical users query a SQL database using plain English instead of writing SQL by hand. Initially pointed toward a different project topic, I built this on my own to test whether a small, locally-trained model could do it — from writing the dataset pipeline to fine-tuning and evaluating the model entirely on a laptop, without cloud GPUs.

## Tech Stack

TensorFlow · HuggingFace Transformers (TF backend) · Flan-T5-base · WikiSQL · Gradio · Python
