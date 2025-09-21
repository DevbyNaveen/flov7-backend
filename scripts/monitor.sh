#!/bin/bash

# Monitoring Script for Flov7
# Provides real-time monitoring and health checks

ENVIRONMENT=${1:-dev}
COMPOSE_FILE="docker/docker-compose.yml"

if [ "$ENVIRONMENT" = "prod" ]; then
    COMPOSE_FILE="docker/docker-compose.prod.yml"
fi

show_help() {
    echo "Flov7 Monitoring Script"
    echo ""
    echo "Usage: $0 [environment] [command]"
    echo ""
    echo "Environments:"
    echo "  dev   - Development environment (default)"
    echo "  prod  - Production environment"
    echo ""
    echo "Commands:"
    echo "  status    - Show service status"
    echo "  logs      - Show service logs"
    echo "  health    - Run health checks"
    echo "  stats     - Show resource usage"
    echo "  monitor   - Real-time monitoring dashboard"
    echo ""
}

show_status() {
    echo "📊 Service Status ($ENVIRONMENT)"
    echo "================================"
    docker-compose -f $COMPOSE_FILE ps
    echo ""
}

show_logs() {
    echo "📝 Service Logs ($ENVIRONMENT)"
    echo "=============================="
    docker-compose -f $COMPOSE_FILE logs --tail=50 -f
}

run_health_checks() {
    echo "🏥 Health Checks ($ENVIRONMENT)"
    echo "==============================="
    
    check_endpoint() {
        local name=$1
        local url=$2
        
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $name: Healthy"
        else
            echo "❌ $name: Unhealthy"
        fi
    }
    
    check_endpoint "API Gateway" "http://localhost:8000/health"
    check_endpoint "AI Service" "http://localhost:8001/health"
    check_endpoint "Workflow Service" "http://localhost:8002/health"
    
    # Check database connectivity
    if docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U temporal > /dev/null 2>&1; then
        echo "✅ PostgreSQL: Connected"
    else
        echo "❌ PostgreSQL: Connection failed"
    fi
    
    # Check Redis connectivity
    if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis: Connected"
    else
        echo "❌ Redis: Connection failed"
    fi
    
    echo ""
}

show_stats() {
    echo "📈 Resource Usage ($ENVIRONMENT)"
    echo "==============================="
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""
}

monitor_dashboard() {
    echo "🖥️  Real-time Monitoring Dashboard ($ENVIRONMENT)"
    echo "================================================="
    echo "Press Ctrl+C to exit"
    echo ""
    
    while true; do
        clear
        echo "🖥️  Flov7 Monitoring Dashboard - $(date)"
        echo "Environment: $ENVIRONMENT"
        echo "================================================="
        
        # Service status
        echo ""
        echo "📊 Services:"
        docker-compose -f $COMPOSE_FILE ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}"
        
        # Health checks
        echo ""
        echo "🏥 Health Status:"
        curl -f -s http://localhost:8000/health > /dev/null 2>&1 && echo "✅ API Gateway" || echo "❌ API Gateway"
        curl -f -s http://localhost:8001/health > /dev/null 2>&1 && echo "✅ AI Service" || echo "❌ AI Service"
        curl -f -s http://localhost:8002/health > /dev/null 2>&1 && echo "✅ Workflow Service" || echo "❌ Workflow Service"
        
        # Resource usage
        echo ""
        echo "📈 Resource Usage:"
        docker stats --no-stream --format "{{.Name}}: CPU {{.CPUPerc}} | Memory {{.MemUsage}}" | head -10
        
        # Recent logs (last 5 lines)
        echo ""
        echo "📝 Recent Activity:"
        docker-compose -f $COMPOSE_FILE logs --tail=3 --no-color 2>/dev/null | tail -5
        
        sleep 5
    done
}

# Main script logic
case "${2:-status}" in
    "help"|"-h"|"--help")
        show_help
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "health")
        run_health_checks
        ;;
    "stats")
        show_stats
        ;;
    "monitor")
        monitor_dashboard
        ;;
    *)
        echo "Unknown command: ${2}"
        show_help
        exit 1
        ;;
esac
