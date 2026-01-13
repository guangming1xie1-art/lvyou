#!/bin/bash

set -e

echo "🚀 Starting Travel Assistant Development Environment..."
echo "================================================"

# Check if .env file exists, create if not
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please review and update .env file with your configuration"
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
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services (excluding frontend for dev)
echo "🔨 Building services..."
docker-compose build agent_backend postgres redis

echo "🏃 Starting core services..."
docker-compose up -d postgres redis

# Wait for PostgreSQL
echo "🗄️  Waiting for PostgreSQL..."
sleep 10

# Start backend
echo "🚀 Starting Agent backend..."
docker-compose up -d agent_backend

# Wait for backend to be ready
echo "⏳ Waiting for Agent backend to be ready..."
sleep 15

# Check backend health
if wait_for_service "Agent backend" "http://localhost:8000/health"; then
    echo "✅ Agent backend is healthy!"
else
    echo "❌ Agent backend health check failed"
    echo "📋 Logs:"
    docker-compose logs agent_backend
    exit 1
fi

# Run database migrations if needed
echo "🗄️  Running database migrations..."
docker-compose exec -T agent_backend python -c "
from src.utils.db import init_db
try:
    init_db()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️  Database initialization: {e}')
"

# Start frontend
echo "🌐 Starting frontend..."
docker-compose up -d frontend

# Wait for frontend
if wait_for_service "Frontend" "http://localhost:3000"; then
    echo "✅ Frontend is ready!"
else
    echo "⚠️  Frontend health check failed (may still be starting)"
fi

echo ""
echo "================================================"
echo "🎉 Development environment is ready!"
echo ""
echo "📊 Services Status:"
echo "  • Frontend: http://localhost:3000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"
echo ""
echo "📄 View logs:"
echo "  • All: docker-compose logs -f"
echo "  • Backend: docker-compose logs -f agent_backend"
echo "  • Frontend: docker-compose logs -f frontend"
echo ""
echo "🛠️  Development:"
echo "  • Backend code changes will require rebuild: docker-compose build agent_backend && docker-compose restart agent_backend"
echo "  • Frontend is served by Nginx (static build)"
echo ""
echo "⚡ Useful commands:"
echo "  • Restart backend: docker-compose restart agent_backend"
echo "  • Check metrics: curl http://localhost:8000/metrics"
echo "================================================"
