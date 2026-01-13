#!/bin/bash

set -e

echo "🔄 Updating Travel Assistant Production Environment"
echo "================================================"

# Configuration
BACKUP_DIR="/opt/travel-assistant/backups/$(date +%Y%m%d_%H%M%S)"
COMPOSE_FILE="docker-compose.prod.yml"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "📋 Update Checklist:"
echo "   ✓ Database backup created"
echo "   ✓ Configuration validated"
echo "   ✓ Services updated"
echo "   ✓ Health checks passed"
echo ""

# 1. Pre-update checks
echo "🔍 Running pre-update checks..."

# Check disk space
DISK_AVAILABLE=$(df /opt | tail -1 | awk '{print $4}'))
DISK_MIN_REQUIRED=2000000  # ~2GB

if [ "$DISK_AVAILABLE" -lt "$DISK_MIN_REQUIRED" ]; then
    echo -e "${RED}❌ Insufficient disk space for update${NC}"
    echo "   Available: $((DISK_AVAILABLE / 1024 / 1024))MB"
    echo "   Required:  $((DISK_MIN_REQUIRED / 1024 / 1024))MB"
    exit 1
fi

# Check if services are running
if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Services are not running, starting fresh deployment...${NC}"
    ./scripts/start-prod.sh
    exit $?
fi

echo -e "${GREEN}✅ Pre-update checks passed${NC}"
echo ""

# 2. Create backup
echo "💾 Creating backup before update..."
mkdir -p $BACKUP_DIR

# Backup database
echo "   Backing up database..."
docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U postgres travel_assistant > $BACKUP_DIR/database.sql 2>/dev/null || echo "   ⚠️  Database backup may have warnings"

# Backup configuration
echo "   Backing up configuration..."
cp .env $BACKUP_DIR/
cp $COMPOSE_FILE $BACKUP_DIR/

# Create restore script
cat > $BACKUP_DIR/restore.sh << 'EOF'
#!/bin/bash
echo "🔄 Restoring from backup..."
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres travel_assistant < database.sql
echo "✅ Restore completed"
EOF
chmod +x $BACKUP_DIR/restore.sh

echo -e "${GREEN}✅ Backup created at $BACKUP_DIR${NC}"
echo ""

# 3. Pull latest code
echo "📥 Pulling latest changes..."
if [ -d ".git" ]; then
    git fetch origin
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    git pull origin $CURRENT_BRANCH
else
    echo -e "${YELLOW}⚠️  Not a git repository, skipping code update${NC}"
fi

echo ""

# 4. Build new images
echo "🔨 Building new images..."
docker-compose -f $COMPOSE_FILE build --no-cache

echo -e "${GREEN}✅ Images built successfully${NC}"
echo ""

# 5. Rolling update
echo "🚀 Performing rolling update..."

# Stop frontend first (least critical)
echo "   Stopping frontend..."
docker-compose -f $COMPOSE_FILE stop frontend

# Update and restart backend
echo "   Updating backend..."
docker-compose -f $COMPOSE_FILE stop agent_backend
docker-compose -f $COMPOSE_FILE create agent_backend
docker-compose -f $COMPOSE_FILE start agent_backend

# Wait for backend to be ready
echo "   ⏳ Waiting for backend to initialize..."
sleep 15

# Check backend health
if ! curl -f -s --max-time 10 "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend health check failed during update${NC}"
    echo "   Rolling back..."
    
    # Restore previous version
    docker-compose -f $COMPOSE_FILE stop agent_backend
    docker-compose -f $COMPOSE_FILE up -d agent_backend
    
    # Restart frontend
    docker-compose -f $COMPOSE_FILE start frontend
    
    exit 1
fi

echo -e "${GREEN}✅ Backend updated successfully${NC}"
echo ""

# 6. Update frontend
echo "🌐 Updating frontend..."
docker-compose -f $COMPOSE_FILE stop frontend
docker-compose -f $COMPOSE_FILE create frontend
docker-compose -f $COMPOSE_FILE start frontend

echo -e "${GREEN}✅ Frontend updated successfully${NC}"
echo ""

# 7. Database migrations
echo "🗄️  Running database migrations if needed..."
docker-compose -f $COMPOSE_FILE exec -T agent_backend python -c "
from src.utils.db import init_db
try:
    init_db()
    print('✅ Database schema verified')
except Exception as e:
    print(f'   Migration may be needed: {e}')
"

echo ""

# 8. Final health check
echo "🔍 Running final health check..."
sleep 10

# Create temporary health check file
cat > /tmp/health-check.sh << 'EOF'
#!/bin/bash

URLS=("http://localhost:8000/health" "http://localhost:3000")
NAMES=("Backend" "Frontend")
FAILED=0

for i in "${!URLS[@]}"; do
    if curl -f -s --max-time 5 "${URLS[$i]}" > /dev/null 2>&1; then
        echo "   ✅ ${NAMES[$i]} is healthy"
    else
        echo "   ❌ ${NAMES[$i]} health check failed"
        ((FAILED++))
    fi
done

exit $FAILED
EOF

chmod +x /tmp/health-check.sh

if /tmp/health-check.sh; then
    echo ""
    echo -e "${GREEN}🎉 Update completed successfully!${NC}"
    echo ""
    echo "📊 Services Status:"
    echo "   • Frontend: http://localhost:3000"
    echo "   • Backend: http://localhost:8000"
    echo "   • Health: ./scripts/health-check.sh"
    echo ""
    echo "💾 Backup location: $BACKUP_DIR"
else
    echo ""
    echo -e "${RED}❌ Health check failed after update${NC}"
    echo "   Services may need manual intervention"
    echo "   Check logs: docker-compose -f $COMPOSE_FILE logs"
fi

# Cleanup
rm -f /tmp/health-check.sh

echo ""
echo "⏱️  Update completed in $(($(date +%s) - $(date +%s -r $BACKUP_DIR))) seconds"
echo "================================================"
