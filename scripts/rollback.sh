#!/bin/bash

# Rollback Script for Flov7
# Restores services from a backup

set -e

BACKUP_DIR=${1}

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ Usage: $0 <backup_directory>"
    echo "Available backups:"
    ls -la backups/ 2>/dev/null || echo "No backups found"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory $BACKUP_DIR not found"
    exit 1
fi

echo "🔄 Starting rollback from backup: $BACKUP_DIR"

# Confirm rollback
read -p "⚠️  This will stop current services and restore from backup. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelled"
    exit 1
fi

# Stop current services
echo "🛑 Stopping current services..."
docker-compose -f docker/docker-compose.prod.yml down

# Restore database
if [ -f "$BACKUP_DIR/database_backup.sql" ]; then
    echo "📥 Restoring database..."
    
    # Start only postgres for restoration
    docker-compose -f docker/docker-compose.prod.yml up -d postgres
    sleep 10
    
    # Drop and recreate database
    docker-compose -f docker/docker-compose.prod.yml exec -T postgres psql -U temporal -c "DROP DATABASE IF EXISTS temporal;"
    docker-compose -f docker/docker-compose.prod.yml exec -T postgres psql -U temporal -c "CREATE DATABASE temporal;"
    
    # Restore from backup
    docker-compose -f docker/docker-compose.prod.yml exec -T postgres psql -U temporal temporal < "$BACKUP_DIR/database_backup.sql"
    
    echo "✅ Database restored"
fi

# Restore volumes
if [ -f "$BACKUP_DIR/postgres_data.tar.gz" ]; then
    echo "📥 Restoring postgres data..."
    docker run --rm -v flov7_postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
fi

if [ -f "$BACKUP_DIR/redis_data.tar.gz" ]; then
    echo "📥 Restoring redis data..."
    docker run --rm -v flov7_redis_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
fi

# Restart all services
echo "🔄 Starting all services..."
docker-compose -f docker/docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Health checks
echo "🏥 Performing health checks..."
curl -f http://localhost:8000/health && echo "✅ API Gateway is healthy" || echo "❌ API Gateway health check failed"
curl -f http://localhost:8001/health && echo "✅ AI Service is healthy" || echo "❌ AI Service health check failed"
curl -f http://localhost:8002/health && echo "✅ Workflow Service is healthy" || echo "❌ Workflow Service health check failed"

echo ""
echo "✅ Rollback completed!"
echo "Services have been restored from backup: $BACKUP_DIR"
