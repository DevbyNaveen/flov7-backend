#!/bin/bash

# Health Check Script for Flov7 Services
# This script provides comprehensive health checks for all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🏥 Flov7 Health Check Report"
echo "============================"

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local description=$3
    
    echo -n "Checking $service_name... "
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
        if [ "$4" = "--verbose" ]; then
            curl -s "$url" | jq '.' 2>/dev/null || curl -s "$url"
        fi
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
        echo "  URL: $url"
        echo "  Description: $description"
    fi
}

# Function to check database connectivity
check_database() {
    echo -n "Checking PostgreSQL database... "
    if docker-compose -f docker/docker-compose.yml exec -T postgres pg_isready -U temporal > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
    fi
}

# Function to check Redis connectivity
check_redis() {
    echo -n "Checking Redis cache... "
    if docker-compose -f docker/docker-compose.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
    fi
}

# Function to check Temporal connectivity
check_temporal() {
    echo -n "Checking Temporal server... "
    if docker-compose -f docker/docker-compose.yml exec -T temporal temporal server health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
    fi
}

# Check all services
echo ""
echo "🔍 Service Health Checks:"
echo "-------------------------"
check_service "Nginx Proxy" "http://localhost/health" "Main nginx load balancer"
check_service "API Gateway" "http://localhost/health/api-gateway" "Main API Gateway service"
check_service "AI Service" "http://localhost/health/ai-service" "AI workflow generation service"
check_service "Workflow Service" "http://localhost/health/workflow-service" "Workflow execution service"

# Check infrastructure
echo ""
echo "🗄️ Infrastructure Checks:"
echo "-------------------------"
check_database
check_redis
check_temporal

# Check service status
echo ""
echo "🐳 Docker Container Status:"
echo "---------------------------"
docker-compose -f docker/docker-compose.yml ps

# Check resource usage
echo ""
echo "📊 Resource Usage:"
echo "------------------"
echo "Container resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""
echo "✅ Health check completed!"
