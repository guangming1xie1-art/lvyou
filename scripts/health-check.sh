#!/bin/bash

set -e

echo "🏥 Health Check - Travel Assistant Infrastructure"
echo "================================================="

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
REDIS_HOST="localhost"
REDIS_PORT="6379"
TIMEOUT=5

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Results
PASSED=0
FAILED=0
WARNINGS=0

# Check function
check_service() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "• Checking $name..."
    
    if curl -f -s --max-time "$TIMEOUT" "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# Check with custom command
check_command() {
    local name=$1
    local command=$2
    
    echo -n "• Checking $name..."
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

echo ""
echo "🔍 Container Status:"
echo "-------------------"
docker-compose ps

echo ""
echo "🌐 HTTP Services:"
echo "------------------"

# Frontend check
check_service "Frontend" "$FRONTEND_URL"

# Backend health check
check_service "Backend Health" "$BACKEND_URL/health"

# API Docs check
check_service "API Documentation" "$BACKEND_URL/docs"

# Metrics endpoint (optional)
if curl -f -s --max-time "$TIMEOUT" "$BACKEND_URL/metrics" > /dev/null 2>&1; then
    echo -e "• Checking Metrics endpoint...${GREEN}✅ OK${NC}"
    ((PASSED++))
else
    echo -e "• Checking Metrics endpoint...${YELLOW}⚠️  NOT AVAILABLE${NC}"
    ((WARNINGS++))
fi

echo ""
echo "🗄️  Database Services:"
echo "---------------------"

# PostgreSQL check
check_command "PostgreSQL" "docker-compose exec -T postgres pg_isready -U postgres"

# Redis check  
check_command "Redis" "docker-compose exec -T redis redis-cli ping"

echo ""
echo "📊 Container Resource Usage:"
echo "----------------------------"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo ""
echo "🐳 Docker System Info:"
echo "---------------------"
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker-compose --version)"
echo "Active containers: $(docker ps --format '{{.Names}}' | grep 'travel-assistant' | wc -l)"

echo ""
echo "📈 Performance Metrics:"
echo "----------------------"

# Backend response time
if curl -f -s --max-time "$TIMEOUT" -w "@curl-format.txt" "$BACKEND_URL/health" > /dev/null 2>&1; then
    RESPONSE_TIME=$(curl -s --max-time "$TIMEOUT" -w "%{time_total}" "$BACKEND_URL/health" -o /dev/null)
    echo "Backend response time: ${RESPONSE_TIME}s"
    
    if (( $(echo "$RESPONSE_TIME < 0.1" | bc -l) )); then
        echo -e "Performance rating: ${GREEN}Excellent${NC}"
    elif (( $(echo "$RESPONSE_TIME < 0.5" | bc -l) )); then
        echo -e "Performance rating: ${GREEN}Good${NC}"
    elif (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
        echo -e "Performance rating: ${YELLOW}Acceptable${NC}"
    else
        echo -e "Performance rating: ${RED}Slow${NC}"
    fi
fi

echo ""
echo "================================================="
echo "📊 Health Check Summary:"
echo "================================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo "================================================="

# Exit code
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All systems operational!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services are experiencing issues${NC}"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "  • View logs: docker-compose logs -f [service]"
    echo "  • Restart services: ./scripts/stop.sh && ./scripts/start-dev.sh"
    echo "  • Check disk space: df -h"
    echo "  • Check memory: free -h"
    echo ""
    exit 1
fi
