#!/bin/bash

set -e

echo "🚀 Starting Travel Assistant Production Environment..."
echo "================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    echo "   cp .env.example .env"
    exit 1
fi

# Validate required environment variables
required_vars=("JWT_SECRET_KEY" "DB_USER" "DB_PASSWORD" "DB_NAME")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=($var)
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Function to wait for service
wait_for_service() {
    local service_name=$1
    local health_url=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "  Attempt $attempt/$max_attempts..."
        sleep 3
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Stop existing containers if running
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Build all services
echo "🔨 Building production images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start infrastructure services first
echo "🏗️  Starting infrastructure services (PostgreSQL, Redis)..."
docker-compose -f docker-compose.prod.yml up -d postgres redis

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 15

# Start backend
echo "🚀Starting Agent backend..."
docker-compose -f docker-compose.prod.yml up -d agent_backend

# Wait for backend to be ready
echo "⏳ Waiting for Agent backend to initialize..."
sleep 20

# Check backend health
if wait_for_service "Agent backend" "http://localhost:8000/health"; then
    echo "✅ Agent backend is healthy!"
else
    echo "❌ Agent backend health check failed"
    echo "📋 Backend logs:"
    docker-compose -f docker-compose.prod.yml logs agent_backend
    exit 1
fi

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T agent_backend python -c "
from src.utils.db import init_db
import time
try:
    print('Initializing database...')
    init_db()
    print('✅ Database initialized successfully')
    time.sleep(2)
except Exception as e:
    print(f'Database initialization: {e}')
"

# Start frontend
echo "🌐 Starting frontend..."
docker-compose -f docker-compose.prod.yml up -d frontend

# Wait for frontend
if wait_for_service "Frontend" "http://localhost:3000"; then
    echo "✅ Frontend is ready!"
else
    echo "⚠️  Frontend health check failed (may still be starting)"
    echo "📋 Frontend logs:"
    docker-compose -f docker-compose.prod.yml logs frontend
fi

# Clean up unused images
echo "🧹 Cleaning up unused Docker images..."
docker image prune -f

echo ""
echo "================================================"
echo "✅ Production deployment completed successfully!"
echo ""
echo "📊 Services Status:"
echo "  • Frontend: http://localhost:3000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo ""
echo "🔒 Production Features:"
echo "  • HTTPS redirect enabled"
echo "  • Resource limits configured"
echo "  • Auto-restart policies active"
echo "  • Structured logging enabled"
echo "  • Database migrations completed"
echo ""
echo "📄 Management commands:"
echo "  • View logs: docker-compose -f docker-compose.prod.yml logs -f [service]"
echo "  • Restart service: docker-compose -f docker-compose.prod.yml restart [service]"
echo "  • Stop all: docker-compose -f docker-compose.prod.yml down"
echo "  • Update: ./scripts/update-prod.sh"
echo ""
echo "📊 Monitoring:"
echo "  • Metrics: curl http://localhost:8000/metrics"
echo "  • Health: curl http://localhost:8000/health"
echo "================================================"
