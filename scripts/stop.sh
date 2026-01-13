#!/bin/bash

set -e

echo "🛑 Stopping Travel Assistant Services..."
echo "================================================"

# Parse arguments
env="dev"
all=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --prod|-p)
            env="prod"
            shift
            ;;
        --all|-a)
            all=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./scripts/stop.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --prod, -p    Stop production environment"
            echo "  --all, -a     Also remove volumes and networks"
            echo "  --help, -h    Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./scripts/stop.sh              # Stop development environment"
            echo "  ./scripts/stop.sh --prod       # Stop production environment"
            echo "  ./scripts/stop.sh --prod --all # Stop and cleanup everything"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

if [ "$env" = "prod" ]; then
    compose_file="docker-compose.prod.yml"
    echo "Stopping production environment..."
else
    compose_file="docker-compose.yml"
    echo "Stopping development environment..."
fi

# Stop containers
if [ "$all" = true ]; then
    echo "🧹 Stopping containers and cleaning up volumes/networks..."
    docker-compose -f $compose_file down -v --remove-orphans
    
    # Clean up unused resources
    echo "🧹 Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    
    echo "✅ All containers, volumes, and networks removed"
else
    echo "⏹️  Stopping containers (keeping volumes)..."
    docker-compose -f $compose_file down
    
    container_count=$(docker-compose -f $compose_file ps -q | wc -l)
    if [ $container_count -eq 0 ]; then
        echo "✅ All containers stopped"
    else
        echo "❌ Some containers may still be running"
    fi
fi

echo "================================================"
echo "Services stopped successfully"
