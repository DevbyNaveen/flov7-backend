#!/bin/bash

# Production Deployment Script for Flov7
# This script handles production deployment with additional safety checks

set -e

echo "🚀 Starting Production Deployment for Flov7..."

# Check if running as root (not recommended for production)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root is not recommended for production deployment."
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if production environment file exists
if [ ! -f "docker/.env.prod" ]; then
    echo "❌ Production environment file docker/.env.prod not found."
    echo "Please create it from docker/.env.example and configure production values."
    exit 1
fi

# Backup current deployment
echo "💾 Creating backup of current deployment..."
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database if running
if docker-compose -f docker/docker-compose.prod.yml ps postgres | grep -q "Up"; then
    echo "📦 Backing up database..."
    docker-compose -f docker/docker-compose.prod.yml exec -T postgres pg_dump -U temporal temporal > "$BACKUP_DIR/database_backup.sql"
fi

# Backup volumes
echo "📦 Backing up volumes..."
docker run --rm -v flov7_postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
docker run --rm -v flov7_redis_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .

echo "✅ Backup completed in $BACKUP_DIR"

# Run deployment
echo "🚀 Running production deployment..."
./scripts/deploy.sh prod

# Post-deployment checks
echo "🔍 Running post-deployment checks..."

# Check if all services are running
echo "Checking service status..."
docker-compose -f docker/docker-compose.prod.yml ps

# Run health checks
echo "Running comprehensive health checks..."
sleep 30

# Test API endpoints through nginx
echo "Testing API endpoints through nginx..."
curl -f http://localhost/health || echo "❌ Nginx health check failed"
curl -f http://localhost/health/api-gateway || echo "❌ API Gateway health check failed"
curl -f http://localhost/health/ai-service || echo "❌ AI Service health check failed"
curl -f http://localhost/health/workflow-service || echo "❌ Workflow Service health check failed"

# Check database connectivity
echo "Testing database connectivity..."
docker-compose -f docker/docker-compose.prod.yml exec -T postgres pg_isready -U temporal || echo "❌ Database connectivity check failed"

# Check Redis connectivity
echo "Testing Redis connectivity..."
docker-compose -f docker/docker-compose.prod.yml exec -T redis redis-cli ping || echo "❌ Redis connectivity check failed"

echo ""
echo "✅ Production deployment completed!"
echo ""
echo "🔗 Production URLs:"
echo "- API Gateway: https://localhost/api"
echo "- AI Service: https://localhost/ai"
echo "- Workflow Service: https://localhost/workflow"
echo "- Overall Health: https://localhost/health"
echo "- Service Health Checks:"
echo "  - API Gateway: https://localhost/health/api-gateway"
echo "  - AI Service: https://localhost/health/ai-service"
echo "  - Workflow Service: https://localhost/health/workflow-service"
echo "- Temporal Web UI: http://localhost:8088"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000"
echo ""
echo "📊 Monitoring:"
echo "- Check logs: docker-compose -f docker/docker-compose.prod.yml logs -f"
echo "- Monitor resources: docker stats"
echo "- View service status: docker-compose -f docker/docker-compose.prod.yml ps"
echo ""
echo "🔄 Rollback (if needed):"
echo "- Restore from backup: ./scripts/rollback.sh $BACKUP_DIR"
