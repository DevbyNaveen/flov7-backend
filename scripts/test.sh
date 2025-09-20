#!/bin/bash

# Flov7 Testing Script
echo "🧪 Running Flov7 Backend Tests..."

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

# Install test dependencies if not already installed
echo "📚 Installing test dependencies..."
pip install -r tests/requirements-test.txt

# Run unit tests
echo "🔬 Running unit tests..."
python -m pytest tests/unit/ -v

# Run integration tests
echo "🔗 Running integration tests..."
python -m pytest tests/integration/ -v

# Run end-to-end tests
echo "🔄 Running end-to-end tests..."
python -m pytest tests/e2e/ -v

echo "✅ All tests completed!"
