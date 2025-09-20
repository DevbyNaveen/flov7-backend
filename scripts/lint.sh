#!/bin/bash

# Flov7 Code Linting Script
echo "🧹 Linting Flov7 Backend Code..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install linting dependencies if not already installed
echo "📚 Installing linting dependencies..."
pip install flake8 black isort

# Run flake8 linting
echo "🔍 Running flake8 linting..."
flake8 --max-line-length=88 --extend-ignore=E203,W503 .

# Run black formatting check
echo "🎨 Checking code formatting with black..."
black --check .

# Run isort import sorting check
echo "📦 Checking import sorting with isort..."
isort --check-only .

echo "✅ Linting completed!"
