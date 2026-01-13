# Docker Configuration and Usage Guide

This guide covers the Docker containerization setup for the Travel Assistant project.

## 🚀 Quick Start

### Development Environment
```bash
# Start all services (initial setup)
./scripts/start-dev.sh

# Or manually:
docker-compose up -d
```

### Production Deployment
```bash
# Deploy to production
./scripts/start-prod.sh

# Use production compose file directly
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Services Overview

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| Frontend | 3000 | React + Nginx | `http://localhost:3000/health` |
| Backend | 8000 | FastAPI Agent | `http://localhost:8000/health` |
| PostgreSQL | 5432 | Database | `pg_isready` |
| Redis | 6379 | Cache | `redis-cli ping` |

## 🔧 Docker Commands Reference

### Container Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart agent_backend

# View logs
docker-compose logs -f                    # All services
docker-compose logs -f agent_backend     # Backend only
docker-compose logs -f frontend          # Frontend only

# Check service status
docker-compose ps

# Execute commands in container
docker-compose exec agent_backend bash
docker-compose exec frontend sh
```

### Image Management
```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build agent_backend

# Clean up unused images
docker image prune

# View images
docker images | grep travel-assistant
```

### Volume Management
```bash
# View volumes
docker volume ls

# View volume details
docker volume inspect travel-assistant_postgres-data
docker volume inspect travel-assistant_redis-data

# Clean up volumes (warning: data loss!)
docker-compose down -v
```

### Network Management
```bash
# View networks
docker network ls

# Inspect network
docker network inspect travel-network

# Test connectivity
docker-compose exec agent_backend curl http://redis:6379
docker-compose exec agent_backend curl http://postgres:5432
```

## 🎯 Common Tasks

### View Application Logs
```bash
# Real-time logs with filter
docker-compose logs -f agent_backend | grep ERROR
docker-compose logs -f --tail=100 agent_backend

# View logs from specific time
docker-compose logs agent_backend --since=1h
docker-compose logs agent_backend --timestamps
```

### Access Application Shell
```bash
# Backend shell
docker-compose exec agent_backend bash

# Inside container you can:
# python -c "from src.utils.db import init_db; init_db()"
# python -m pytest tests/

# Frontend shell
docker-compose exec frontend sh
```

### Monitor Resources
```bash
# Real-time resource usage
docker stats

# Filtering for our services
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker ps --format "{{.Names}}" | grep travel-assistant)

# Check disk usage
docker system df
docker system df -v
```

### Database Operations
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d travel_assistant

# Redis CLI
docker-compose exec redis redis-cli

# Backup PostgreSQL
docker-compose exec postgres pg_dump -U postgres travel_assistant > backup.sql

# Restore PostgreSQL
cat backup.sql | docker-compose exec -T postgres psql -U postgres -d travel_assistant
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart agent_backend

# Restart with no cache (force rebuild)
docker-compose build --no-cache agent_backend
docker-compose up -d --force-recreate agent_backend
```

## 🔍 Troubleshooting

### Container Won't Start
```bash
# Check logs for errors
docker-compose logs [service-name]

# Common issues:
# 1. Port conflicts
docker-compose config | grep "published:"  # Check used ports
netstat -tuln | grep :3000              # Check if port is in use

# 2. Database connection errors
docker-compose exec agent_backend curl http://postgres:5432

# 3. Permission issues
ls -la docker-compose.yml  # Check file permissions
```

### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U postgres

# View PostgreSQL logs
docker-compose logs postgres

# Reset database (warning: data loss!)
docker-compose down -v postgres
docker-compose up -d postgres

# Reinitialize database
docker-compose exec agent_backend python -c "from src.utils.db import init_db; init_db()"
```

### Redis Connection Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# View Redis logs
docker-compose logs redis

# Flush Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

### Performance Issues
```bash
# Check container resources
docker stats [container-name]

# Check for memory leaks
docker-compose exec agent_backend ps aux

# View slow queries (PostgreSQL)
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check Redis memory
docker-compose exec redis redis-cli INFO memory
```

### Network Issues
```bash
# Test connectivity between containers
docker-compose exec agent_backend curl http://localhost:8000/health
docker-compose exec agent_backend ping -c 3 postgres
docker-compose exec agent_backend ping -c 3 redis

# Check network configuration
docker network inspect travel-network
```

### Build Issues
```bash
# Debug build errors
docker-compose build --no-cache

# Check build logs in detail
docker-compose build 2>&1 | tee build.log

# Clean build cache
docker builder prune
```

## 🔧 Development Workflow

### Making Code Changes
```bash
# Backend changes (require rebuild)
vim travel-assistant-agent/src/api/routes.py
docker-compose build agent_backend
docker-compose restart agent_backend

# Frontend changes
docker-compose restart frontend  # If using dev server
```

### Testing Changes
```bash
# Run health check
./scripts/health-check.sh

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test frontend
curl http://localhost:3000
```

### Debugging in Container
```bash
# Install debugging tools
docker-compose exec agent_backend apt-get update
docker-compose exec agent_backend apt-get install -y vim curl telnet

# View application logs
# Backend logs include: request time, cache hits, errors
docker-compose logs -f agent_backend | grep -E "(ERROR|WARNING|cache hit)"

# Monitor real-time traffic
docker-compose exec agent_backend tail -f /app/logs/app.log
```

## 🛡️ Security Best Practices

### Running in Production
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Verify security settings
docker-compose exec agent_backend id  # Should be non-root user

# Check exposed ports
docker-compose config | grep "published:"  # Should only expose necessary ports

# Scan for vulnerabilities
docker scan [image-name]  # Requires Docker Hub login
```

### Managing Secrets
```bash
# Never commit secrets to git
grep -r "password\|secret\|key" --include="*.yml" --include="*.yaml" docker-compose*

# Use environment files
chmod 600 .env  # Restrict .env file permissions
```

## 📊 Monitoring and Maintenance

### Regular Maintenance Tasks
```bash
# Daily: Check logs for errors
docker-compose logs --tail=100 | grep ERROR

# Weekly: Review disk usage
docker system df
docker system prune --volumes

# Monthly: Update images
docker-compose pull
docker-compose up -d --force-recreate

# Quarterly: Backup volumes
docker run --rm -v [volume-name]:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

### Backup Strategies
```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres travel_assistant > "backup_$(date +%Y%m%d).sql"

# Volume backup
docker run --rm -v travel-assistant_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
docker run --rm -v travel-assistant_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data
```

## 📚 Useful Aliases

Add to your `.bashrc` or `.zshrc`:
```bash
# Travel Assistant shortcuts
alias tadev='cd /path/to/travel-assistant && ./scripts/start-dev.sh'
alias taup='docker-compose up -d'
alias tdown='docker-compose down'
alias talogs='docker-compose logs -f'
alias tastats='docker stats $(docker ps --format "{{.Names}}" | grep travel-assistant)'
alias tahealth='./scripts/health-check.sh'
alias taprod='./scripts/start-prod.sh'
```

## 🆘 Emergency Commands

```bash
# Complete reset (WARNING: data loss!)
docker-compose down -v --remove-orphans
docker system prune -a --volumes

# Force rebuild everything
docker-compose build --no-cache
docker-compose up -d --force-recreate --build

# Debug container start
docker-compose up --no-start
```

## 📖 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [Production Deployment Guide](./DOCKER_PROD.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)