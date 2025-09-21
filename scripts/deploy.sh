#!/bin/bash

# Flov7 Deployment Script
# Enhanced version with environment support and health checks

set -e  # Exit on any error

# Configuration
ENVIRONMENT=${1:-dev}
COMPOSE_FILE="docker/docker-compose.yml"
ENV_FILE="docker/.env"

if [ "$ENVIRONMENT" = "prod" ]; then
    COMPOSE_FILE="docker/docker-compose.prod.yml"
    ENV_FILE="docker/.env.prod"
fi

echo "🚀 Deploying Flov7 Backend Services (Environment: $ENVIRONMENT)..."

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

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file $ENV_FILE not found. Please create it from the example."
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose -f $COMPOSE_FILE down --remove-orphans

# Pull latest images for production
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "📥 Pulling latest images..."
    docker-compose -f $COMPOSE_FILE pull
fi

# Build and deploy all services
echo "📦 Building Docker images..."
docker-compose -f $COMPOSE_FILE build --no-cache

echo "🔄 Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Health checks
echo "🏥 Performing health checks..."

check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "Checking $service_name..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        echo "⏳ Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed health check"
    return 1
}

# Perform health checks through nginx
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "Checking $service_name..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        echo "⏳ Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed health check"
    return 1
}

# Perform health checks through nginx
check_service "Nginx" "http://localhost/health"
check_service "API Gateway" "http://localhost/health/api-gateway"
check_service "AI Service" "http://localhost/health/ai-service"
check_service "Workflow Service" "http://localhost/health/workflow-service"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Services are now running:"
echo "- API Gateway: http://localhost/api"
echo "  - Docs: http://localhost/api/docs"
echo "- AI Service: http://localhost/ai"
echo "  - Docs: http://localhost/ai/docs"
echo "- Workflow Service: http://localhost/workflow"
echo "  - Docs: http://localhost/workflow/docs"
echo "- Overall Health: http://localhost/health"
echo "- Service Health Checks:"
echo "  - API Gateway: http://localhost/health/api-gateway"
echo "  - AI Service: http://localhost/health/ai-service"
echo "  - Workflow Service: http://localhost/health/workflow-service"
echo "- Redis: redis://localhost:6379"
echo "- Temporal: http://localhost:7233"

if [ "$ENVIRONMENT" = "prod" ]; then
    echo "- Temporal Web UI: http://localhost:8088"
    echo "- Prometheus: http://localhost:9090"
    echo "- Grafana: http://localhost:3000"
fi

echo ""
echo "Useful commands:"
echo "- Check service status: docker-compose -f $COMPOSE_FILE ps"
echo "- View logs: docker-compose -f $COMPOSE_FILE logs -f [service_name]"
echo "- Stop services: docker-compose -f $COMPOSE_FILE down"
echo "- Restart service: docker-compose -f $COMPOSE_FILE restart [service_name]"
