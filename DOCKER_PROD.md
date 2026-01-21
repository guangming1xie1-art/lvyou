# Docker Production Deployment Guide

Complete production deployment guide for Travel Assistant using Docker containers.

## 🎯 Overview

This guide covers deploying the Travel Assistant application stack to production environments using Docker containers and Docker Compose.

**Stack Components:**
- Frontend: React + Nginx (Port 3000)
- Backend: FastAPI (Port 8000)
- Database: PostgreSQL (Port 5432)
- Cache: Redis (Port 6379)

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04/22.04 LTS recommended)
- **CPU**: 2+ cores
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 20GB minimum (50GB recommended)
- **Network**: Public IP with SSH access

### Software Requirements
- Docker 24.0.0+
- Docker Compose 2.20.0+
- Git 2.30.0+
- curl
- openssl

### Network Requirements
- Ports 80/443 (HTTP/HTTPS)
- Port 22 (SSH)
- Port 8000 (API - optional, for debugging)

## 🚀 Quick Start

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y docker.io docker-compose git curl openssl

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/your-org/travel-assistant.git
cd travel-assistant

# Create production environment file
cp .env.example .env

# Edit configuration (set secrets, etc.)
vim .env

# Deploy to production
./scripts/start-prod.sh
```

### 3. Verify Deployment

```bash
# Check service status
./scripts/health-check.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Test endpoints
curl http://localhost:3000        # Frontend
curl http://localhost:8000/health # Backend
```

## 🔐 Security Configuration

### 1. Generate Strong Secrets

```bash
# JWT secret (HS256)
openssl rand -hex 32 > jwt_secret.txt

# Database password
openssl rand -hex 16 > db_password.txt

# Redis password (optional)
openssl rand -hex 16 > redis_password.txt
```

### 2. Configure Environment File

```bash
# .env file
# ====================
# DATABASE
# ====================
DB_USER=travel_user
echo "Enter DB_PASSWORD from db_password.txt"
DB_NAME=travel_assistant_production

# ====================
# JWT AUTHENTICATION
# ====================
echo "Enter JWT_SECRET_KEY from jwt_secret.txt"
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ====================
# REDIS
# ====================
REDIS_ENABLED=true
REDIS_HOST=redis
REDIS_PORT=6379

# ====================
# API CONFIGURATION
# ====================
APP_ENV=production
CORS_ORIGINS=https://your-domain.com
ENABLE_GZIP=true
ENABLE_HTTPS_REDIRECT=true
SLOW_REQUEST_THRESHOLD=0.5
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# ====================
# EXTERNAL SERVICES
# ====================
ANTHROPIC_API_KEY=your_claude_api_key
JAVA_API_BASE_URL=http://your-backend:8080/api
```

### 3. File Permissions

```bash
# Protect sensitive files
chmod 600 .env docker-compose.prod.yml

# Protect sensitive directories
chmod 700 scripts/
chmod 600 scripts/*.sh
```

## 🔧 Advanced Configuration

### Custom Domain Setup

```bash
# Configure domain in .env
CORS_ORIGINS=https://travel-assistant.yourcompany.com
VITE_AGENT_API_BASE_URL=https://travel-assistant.yourcompany.com

# Optional: If using external Nginx
# Update docker-compose.prod.yml to expose only 8000
# Remove frontend port mapping and configure external nginx
```

### SSL/TLS with Let's Encrypt

```bash
# Using external Nginx with Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx -d travel-assistant.yourcompany.com

# Auto-renewal
echo "0 12 * * * root certbot renew --quiet" | sudo tee -a /etc/crontab
```

### Database Optimization

```bash
# Create production database with optimized settings
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres <<EOF
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '2GB';
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET checkpoint_timeout = '10min';
ALTER SYSTEM SET max_wal_size = '1GB';
SELECT pg_reload_conf();
EOF
```

### Redis Optimization

```bash
# Update redis command in docker-compose.prod.yml
command: redis-server 
  --appendonly yes  
  --maxmemory 512mb
  --maxmemory-policy allkeys-lru
  --tcp-keepalive 60
  --timeout 300
```

## 📊 Monitoring and Logging

### 1. Built-in Monitoring

The application includes built-in monitoring endpoints:

```bash
# Application health
curl http://localhost:8000/health

# Performance metrics
curl http://localhost:8000/metrics

# API documentation
curl http://localhost:8000/docs
```

### 2. Container Monitoring

```bash
# Real-time container stats
docker stats $(docker-compose -f docker-compose.prod.yml ps -q)

# Resource usage report
docker system df
docker system df -v

# Container logs with filtering
docker-compose -f docker-compose.prod.yml logs -f --tail=100 agent_backend | grep ERROR
```

### 3. Log Aggregation

```bash
# Optional: Configure centralized logging
# 1. Install Logstash/Fluentd/Vector
# 2. Update docker-compose.prod.yml logging section

logging:
  driver: "syslog"
  options:
    syslog-address: "tcp://logs.example.com:514"
    tag: "travel-assistant"
```

### 4. Application Performance Monitoring

```bash
# Built-in performance headers
# X-Process-Time: response time
# X-Performance: performance rating (excellent/good/acceptable/slow)
# X-Cache-Hit: true/false

curl -I http://localhost:8000/api/v1/search

# Look for:
# X-Process-Time: 0.045
# X-Performance: excellent
# X-Cache-Hit: true
```

## 🚀 Deployment Scenarios

### Scenario 1: Zero-Downtime Update

```bash
# Deploy new version with rolling updates
docker-compose -f docker-compose.prod.yml up -d --no-deps --build agent_backend

# Wait for health check
curl -f http://localhost:8000/health

# Update frontend
docker-compose -f docker-compose.prod.yml up -d --no-deps --build frontend
```

### Scenario 2: Rollback Procedure

```bash
# List previous images
docker images | grep agent_backend

# Rollback to previous version
docker-compose -f docker-compose.prod.yml stop agent_backend
docker-compose -f docker-compose.prod.yml rm agent_backend

# Run previous version
# Use specific image tag or commit hash
docker run -d --name travel-assistant-agent \
  --network travel-network-prod \
  -p 8000:8000 \
  ghcr.io/your-org/agent-backend:previous-tag
```

### Scenario 3: Scaling Services

```bash
# Scale backend horizontally
docker-compose -f docker-compose.prod.yml up -d --scale agent_backend=3

# Note: Requires external load balancer
# Consider using Docker Swarm or Kubernetes for production scaling
```

### Scenario 4: Database Migration

```bash
# Backup first
./scripts/stop.sh --prod
docker-compose -f docker-compose.prod.yml up -d postgres

docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres travel_assistant > backup_pre_migration.sql

# Apply migrations
docker-compose -f docker-compose.prod.yml exec agent_backend \
  python -c "from src.utils.db import init_db; init_db()"

# Restart services
./scripts/start-prod.sh
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Common causes:
# - Port conflicts: netstat -tuln | grep :[port]
# - Permission issues: ls -la docker-compose.prod.yml
# - Missing environment: docker-compose -f docker-compose.prod.yml config
```

#### 2. Database Connection Failures
```bash
# Test PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U postgres

# Check backend connection
docker-compose -f docker-compose.prod.yml exec agent_backend \
  curl postgres:5432

# Reset database (data loss!)
docker-compose -f docker-compose.prod.yml stop postgres
docker-compose -f docker-compose.prod.yml rm postgres
docker volume rm travel-assistant_postgres-data
docker-compose -f docker-compose.prod.yml up -d postgres
```

#### 3. Redis Connection Issues
```bash
# Test Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Check Redis logs
docker-compose -f docker-compose.prod.yml logs redis

# Reset Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
```

#### 4. Performance Issues
```bash
# Check resource usage
docker stats $(docker-compose -f docker-compose.prod.yml ps -q)

# Analyze slow requests
# Built-in performance headers in response:
curl -I -H "X-Request-ID: debug-$(date +%s)" http://localhost:8000/docs

# Check PostgreSQL slow queries
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

#### 5. Memory Issues
```bash
# Check container memory
docker stats --no-stream

# View logs for OOM errors
dmesg | grep -i oom

# Increase container memory (update docker-compose.prod.yml)
deploy:
  resources:
    limits:
      memory: 4G
```

### Debug Commands

```bash
# Enter container for debugging
docker-compose -f docker-compose.prod.yml exec agent_backend bash

# Install debugging tools (inside container)
apt-get update && apt-get install -y curl telnet net-tools

# Check network connectivity (inside container)
curl http://localhost:8000/health      # Local
curl http://postgres:5432               # PostgreSQL
curl http://redis:6379                  # Redis

# Test database queries (inside container)
python -c "
from conf import settings
from utils.db import get_db_connection
conn = get_db_connection()
print('Database connection successful')
"
```

## 💾 Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# /opt/travel-assistant/backup.sh

BACKUP_DIR="/backups/travel-assistant/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres travel_assistant | gzip > $BACKUP_DIR/database.sql.gz

# Configuration backup
cp .env docker-compose.prod.yml $BACKUP_DIR/

# Sync to S3 (optional)
aws s3 cp $BACKUP_DIR s3://your-bucket/backups/ --recursive

# Cleanup old backups (keep 30 days)
find /backups/travel-assistant -type d -mtime +30 -exec rm -rf {} +
```

### Recovery Procedures

```bash
# Database recovery
gunzip < backup.sql.gz | docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres travel_assistant

# Full system recovery
tar xzf backup.tar.gz -C /
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Performance Tuning

### Application-Level

```bash
# Backend optimization
# Update docker-compose.prod.yml
command: >
  python -m uvicorn
  src.main:app
  --host 0.0.0.0
  --port 8000
  --workers 8                  # Match CPU cores
  --loop uvloop                # Faster event loop
  --http httptools             # Faster HTTP parser
```

### Database-Level

```yaml
# PostgreSQL optimization
environment:
  - POSTGRES_DB=travel_assistant
  - POSTGRES_USER=travel_user
  - POSTGRES_PASSWORD=your_password
  - POSTGRES_INITDB_ARGS="--auth-host=scram-sha-256"
  - PGDATA=/var/lib/postgresql/data/pgdata
```

```bash
# PostgreSQL performance tuning (run inside container)
psql -U postgres -c "
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '2GB';
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET checkpoint_timeout = '10min';
ALTER SYSTEM SET max_wal_size = '1GB';
SELECT pg_reload_conf();
"
```

### System-Level

```bash
# Linux kernel optimization
# /etc/sysctl.conf
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535

# Apply settings
sysctl -p
```

## 🏥 Maintenance Tasks

### Daily
- [ ] Check application health
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Verify backup status

### Weekly
- [ ] Performance review
- [ ] Security updates check
- [ ] Metrics analysis
- [ ] Log cleanup

### Monthly
- [ ] Full system backup test
- [ ] Dependency updates
- [ ] Security audit
- [ ] Capacity planning review

### Quarterly
- [ ] Disaster recovery drill
- [ ] Architecture review
- [ ] Cost optimization review

## 📚 Additional Resources

- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Production](https://docs.docker.com/compose/production/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/production/)
- [PostgreSQL Production](https://www.postgresql.org/docs/current/admin.html)
- [Redis Production](https://redis.io/topics/admin)

## 🆘 Emergency Contacts

- **Technical Lead**: [Name] - [Email] - [Phone]
- **DevOps Team**: [Name] - [Email] - [Phone]
- **Infrastructure Team**: [Name] - [Email] - [Phone]

## 📄 Version Information

- Docker: 24.0.0+
- Docker Compose: 2.20.0+
- PostgreSQL: 15-alpine
- Redis: 7-alpine
- Node.js: 18-alpine
- Python: 3.11-slim
- Nginx: alpine

---

**For production deployments, always:**
1. Test in staging first
2. Create backups before changes
3. Monitor system health after deployment
4. Have rollback procedures ready
5. Document any custom configurations