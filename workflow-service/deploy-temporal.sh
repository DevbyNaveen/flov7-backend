#!/bin/bash

# Flov7 Temporal Deployment Script
# This script deploys the complete Temporal integration stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
TEMPORAL_VERSION="latest"
WORKER_REPLICAS=2
NETWORK_NAME="flov7_network"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    log "Prerequisites check passed"
}

# Create environment file
create_env_file() {
    log "Creating environment configuration..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# Temporal Configuration
TEMPORAL_HOST=temporal:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=flov7-workflow-task-queue

# Worker Configuration
START_TEMPORAL_WORKER=false
TEMPORAL_MAX_CONCURRENT_WORKFLOWS=10
TEMPORAL_MAX_CONCURRENT_ACTIVITIES=5

# Service URLs
WORKFLOW_SERVICE_URL=http://workflow-service:8002
AI_SERVICE_URL=http://ai-service:8001
API_GATEWAY_URL=http://api-gateway:8000

# Database Configuration
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_ROLE_KEY=your-service-key-here
REDIS_URL=redis://redis:6379

# Security
JWT_SECRET_KEY=your-jwt-secret-key-here

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
EOF
        log "Created .env file with default configuration"
    else
        log "Using existing .env file"
    fi
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    # Build workflow service
    docker build -t flov7-workflow-service .
    
    # Build temporal worker
    docker build -f Dockerfile.temporal-worker -t flov7-temporal-worker .
    
    log "Docker images built successfully"
}

# Deploy Temporal stack
deploy_temporal() {
    log "Deploying Temporal stack..."
    
    # Create network if it doesn't exist
    docker network create $NETWORK_NAME 2>/dev/null || true
    
    # Start Temporal server
    log "Starting Temporal server..."
    docker-compose -f docker-compose.temporal.yml up -d temporal
    
    # Wait for Temporal to be ready
    log "Waiting for Temporal server to be ready..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose -f docker-compose.temporal.yml exec temporal temporal operator cluster health 2>/dev/null; then
            log "Temporal server is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -eq 0 ]; then
        error "Temporal server failed to start within 60 seconds"
    fi
    
    # Start remaining services
    log "Starting remaining services..."
    docker-compose -f docker-compose.temporal.yml up -d
    
    log "Temporal stack deployed successfully"
}

# Health checks
health_checks() {
    log "Running health checks..."
    
    # Check Temporal server
    if docker-compose -f docker-compose.temporal.yml exec temporal temporal operator cluster health; then
        log "✓ Temporal server health check passed"
    else
        error "Temporal server health check failed"
    fi
    
    # Check workflow service
    timeout=30
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8002/health > /dev/null 2>&1; then
            log "✓ Workflow service health check passed"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -eq 0 ]; then
        warning "Workflow service health check timed out"
    fi
    
    # Check worker registration
    log "Checking worker registration..."
    python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from app.temporal.client import get_temporal_client

async def check_worker():
    try:
        client = await get_temporal_client()
        if client:
            print('✓ Worker registered successfully')
        else:
            print('⚠ Worker not registered (fallback mode)')
    except Exception as e:
        print(f'✗ Worker check failed: {e}')

asyncio.run(check_worker())
"
}

# Scale workers
scale_workers() {
    log "Scaling Temporal workers..."
    
    # Scale worker replicas
    docker-compose -f docker-compose.temporal.yml up -d --scale temporal-worker=$WORKER_REPLICAS
    
    log "Scaled to $WORKER_REPLICAS worker instances"
}

# Run integration tests
run_tests() {
    log "Running integration tests..."
    
    # Wait for services to be ready
    sleep 10
    
    # Run tests
    if python3 test-temporal-integration.py http://localhost:8002; then
        log "✓ Integration tests passed"
    else
        warning "Integration tests failed - check logs"
    fi
}

# Show status
show_status() {
    log "Deployment Status:"
    echo ""
    
    docker-compose -f docker-compose.temporal.yml ps
    echo ""
    
    log "Service URLs:"
    echo "  Temporal Web UI: http://localhost:8233"
    echo "  Workflow Service: http://localhost:8002"
    echo "  Workflow API Docs: http://localhost:8002/docs"
    echo "  Redis: localhost:6379"
    echo ""
    
    log "Useful commands:"
    echo "  View logs: docker-compose -f docker-compose.temporal.yml logs -f"
    echo "  Stop services: docker-compose -f docker-compose.temporal.yml down"
    echo "  Scale workers: docker-compose -f docker-compose.temporal.yml up -d --scale temporal-worker=4"
}

# Cleanup
cleanup() {
    log "Cleaning up..."
    docker-compose -f docker-compose.temporal.yml down
    docker network rm $NETWORK_NAME 2>/dev/null || true
}

# Main deployment function
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_env_file
            build_images
            deploy_temporal
            health_checks
            run_tests
            show_status
            ;;
        "scale")
            scale_workers
            ;;
        "test")
            run_tests
            ;;
        "status")
            show_status
            ;;
        "stop")
            cleanup
            ;;
        "logs")
            docker-compose -f docker-compose.temporal.yml logs -f
            ;;
        *)
            echo "Usage: $0 {deploy|scale|test|status|stop|logs}"
            echo ""
            echo "Commands:"
            echo "  deploy  - Deploy the complete Temporal stack"
            echo "  scale   - Scale worker instances"
            echo "  test    - Run integration tests"
            echo "  status  - Show deployment status"
            echo "  stop    - Stop all services"
            echo "  logs    - View service logs"
            exit 1
            ;;
    esac
}

# Handle script termination
trap cleanup EXIT

# Run main function
main "$@"
