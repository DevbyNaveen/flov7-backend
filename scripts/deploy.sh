#!/bin/bash

# Flov7 Deployment Script
echo "🚀 Deploying Flov7 Backend Services..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed. Please install Docker Compose first."
    exit 1
fi

# Build and deploy all services
echo "📦 Building Docker images..."
docker-compose -f docker/docker-compose.yml build

echo "🔄 Starting services..."
docker-compose -f docker/docker-compose.yml up -d

echo "✅ Deployment complete!"
echo ""
echo "Services are now running:"
echo "- API Gateway: http://localhost:8000"
echo "- AI Service: http://localhost:8001"
echo "- Workflow Service: http://localhost:8002"
echo "- Redis: redis://localhost:6379"
echo "- Temporal: http://localhost:7233"

echo ""
echo "Check service status with: docker-compose -f docker/docker-compose.yml ps"
