#!/bin/bash

# Enhanced Production Deployment Script for Flov7
# This script handles production deployment with SSL, monitoring, and health checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-prod}
COMPOSE_FILE="docker/docker-compose.prod.yml"
ENV_FILE="docker/.env.prod"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}🚀 Enhanced Production Deployment for Flov7${NC}"
echo "=========================================="

# Check if running as root (not recommended for production)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: Running as root is not recommended for production deployment.${NC}"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if production environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Production environment file $ENV_FILE not found.${NC}"
    echo "Please create it from docker/.env.example and configure production values."
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f "docker/ssl/cert.pem" ] || [ ! -f "docker/ssl/key.pem" ]; then
    echo -e "${YELLOW}⚠️  SSL certificates not found. Creating self-signed certificates for development...${NC}"
    mkdir -p docker/ssl
    openssl req -x509 -newkey rsa:4096 -keyout docker/ssl/key.pem -out docker/ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    echo -e "${GREEN}✅ SSL certificates created in docker/ssl/${NC}"
fi

# Pre-deployment checks
echo -e "${BLUE}🔍 Pre-deployment checks...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is required but not installed.${NC}"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is required but not installed.${NC}"
    exit 1
fi

# Check disk space (require at least 2GB free)
AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
REQUIRED_SPACE=2097152  # 2GB in KB
if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    echo -e "${YELLOW}⚠️  Warning: Low disk space. At least 2GB recommended.${NC}"
fi

# Backup current deployment
echo -e "${BLUE}💾 Creating backup of current deployment...${NC}"
mkdir -p "$BACKUP_DIR"

# Backup database if running
if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
    echo -e "${BLUE}📦 Backing up database...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U temporal temporal > "$BACKUP_DIR/database_backup.sql"
    echo -e "${GREEN}✅ Database backup completed${NC}"
fi

# Backup volumes
echo -e "${BLUE}📦 Backing up volumes...${NC}"
docker run --rm -v flov7_postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data . || true
docker run --rm -v flov7_redis_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/redis_data.tar.gz -C /data . || true
docker run --rm -v flov7_temporal_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/temporal_data.tar.gz -C /data . || true

echo -e "${GREEN}✅ Backup completed in $BACKUP_DIR${NC}"

# Stop existing services
echo -e "${BLUE}🛑 Stopping existing services...${NC}"
docker-compose -f "$COMPOSE_FILE" down --remove-orphans --timeout 30

# Pull latest images
echo -e "${BLUE}📥 Pulling latest images...${NC}"
docker-compose -f "$COMPOSE_FILE" pull

# Build and deploy all services
echo -e "${BLUE}📦 Building Docker images...${NC}"
docker-compose -f "$COMPOSE_FILE" build --no-cache

echo -e "${BLUE}🔄 Starting services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Health checks
echo -e "${BLUE}🏥 Performing comprehensive health checks...${NC}"

# Function to check service health with retry
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "Checking $service_name... "
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ HEALTHY${NC}"
            return 0
        fi
        echo -n "."
        sleep 3
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ FAILED${NC}"
    return 1
}

# Check all services
echo ""
echo -e "${BLUE}🔍 Service Health Checks:${NC}"
check_service "Nginx Proxy" "http://localhost/health"
check_service "API Gateway" "http://localhost/health/api-gateway"
check_service "AI Service" "http://localhost/health/ai-service"
check_service "Workflow Service" "http://localhost/health/workflow-service"

# Check infrastructure
echo -e "${BLUE}🗄️ Infrastructure Checks:${NC}"
if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U temporal > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL${NC}"
else
    echo -e "${RED}❌ PostgreSQL${NC}"
fi

if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis${NC}"
else
    echo -e "${RED}❌ Redis${NC}"
fi

# Check service status
echo -e "${BLUE}🐳 Container Status:${NC}"
docker-compose -f "$COMPOSE_FILE" ps

# Resource usage
echo -e "${BLUE}📊 Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""
echo -e "${GREEN}✅ Production deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}🔗 Production URLs:${NC}"
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
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "- Check logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "- Monitor resources: docker stats"
echo "- View service status: docker-compose -f $COMPOSE_FILE ps"
echo "- Run health check: ./scripts/health-check.sh"
echo ""
echo -e "${BLUE}🔄 Rollback (if needed):${NC}"
echo "- Restore from backup: ./scripts/rollback.sh $BACKUP_DIR"
echo ""
echo -e "${YELLOW}⚠️  Note: Using self-signed SSL certificates.${NC}"
echo "For production, replace with valid SSL certificates in docker/ssl/"
