#!/bin/bash

# Flov7 Backend Project Setup Script
echo "🚀 Setting up Flov7 Backend Project..."

# Check if Python 3.11+ is installed
if ! python3 --version | grep -q "Python 3.1[1-9]"; then
    echo "❌ Python 3.11+ is required. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install common dependencies
echo "📚 Installing common dependencies..."
pip install fastapi uvicorn pydantic python-dotenv

# Copy environment file
echo "⚙️  Setting up environment configuration..."
cp docker/.env.example .env

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure your environment variables in .env"
echo "2. Run: source venv/bin/activate"
echo "3. Start developing!"
echo ""
echo "For development with Docker:"
echo "docker-compose -f docker/docker-compose.dev.yml up"
