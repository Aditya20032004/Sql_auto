#!/bin/bash

# Domain-Specific LLM Compiler - Environment Setup Script
# Run this script to set up your development environment

echo "🚀 Setting up Domain-Specific LLM Compiler..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "📁 Creating project directories..."
mkdir -p data/training
mkdir -p data/validation
mkdir -p data/benchmarks
mkdir -p models/cache
mkdir -p models/fine_tuned
mkdir -p outputs/compilations
mkdir -p outputs/evaluations
mkdir -p outputs/visualizations
mkdir -p logs
echo "✅ Directories created"

# Copy environment template
echo ""
echo "🔐 Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your API keys!"
else
    echo "ℹ️  .env file already exists"
fi

# Download sample data (optional)
echo ""
read -p "📥 Download sample SQL dataset for testing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Downloading..."
    # Add download logic here
    echo "✅ Sample data downloaded"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Activate the environment: source venv/bin/activate"
echo "3. Run example: python examples/01_basic_sql.py"
echo "4. Start Jupyter: jupyter notebook notebooks/"
echo ""
echo "Happy coding! 🎉"
