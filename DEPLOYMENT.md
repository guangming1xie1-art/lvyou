# Production Deployment Guide

Complete guide for deploying Travel Assistant to production environments.

## 📋 Pre-Deployment Checklist

### Environment Preparation
- [ ] Server with Docker and Docker Compose installed
- [ ] Domain name configured (if applicable)
- [ ] SSL certificates ready (Let's Encrypt recommended)
- [ ] Firewall configured (allow ports 80, 443, 22)
- [ ] Sufficient disk space (>10GB free)
- [ ] RAM requirements met (minimum 2GB, recommended 4GB+)

### Application Configuration
- [ ] `.env` file created with production values
- [ ] `JWT_SECRET_KEY` generated (use `openssl rand -hex 32`)
- [ ] Database credentials set
- [ ] Redis password configured (if needed)
- [ ] CORS origins configured
- [ ] External API keys added (Claude, etc.)

### Security Considerations
- [ ] SSH keys configured (disable password auth)
- [ ] Fail2ban installed
- [ ] Automatic security updates enabled
- [ ] Non-root Docker user configured
- [ ] Secrets encrypted/managed

## 🚀 Deployment Steps

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Enable Docker on boot
sudo systemctl enable docker

# Install additional tools
sudo apt install -y curl git htop
```

### 2. Deploy Application

```bash
# Clone repository
git clone https://github.com/your-org/travel-assistant.git
cd travel-assistant

# Copy and configure environment
cp .env.example .env
# Edit .env with production values
vim .env

# Verify configuration
./scripts/health-check.sh

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor deployment
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Initial Configuration

```bash
# Wait for services to be ready
sleep 30

# Initialize database
docker-compose -f docker-compose.prod.yml exec agent_backend python -c "
from src.utils.db import init_db
init_db()
print('Database initialized')
"

# Create admin user (if needed)
docker-compose -f docker-compose.prod.yml exec agent_backend python -c "
# Add admin user creation script here if needed
"

# Run health check
./scripts/health-check.sh
```

### 4. Configure Reverse Proxy (Optional)

If using external Nginx:

```nginx
# /etc/nginx/sites-available/travel-assistant
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔧 Configuration Details

### Environment Variables

```bash
# Core settings
APP_ENV=production
JWT_SECRET_KEY=your-super-secret-key-here
CORS_ORIGINS=https://your-domain.com

# Database
DB_HOST=postgres
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_NAME=travel_assistant

# Redis
REDIS_HOST=redis
REDIS_ENABLED=true

# Frontend
VITE_AGENT_API_BASE_URL=https://your-domain.com
VITE_APP_NAME=Travel Assistant Pro

# Production specific
ENABLE_HTTPS_REDIRECT=true
SLOW_REQUEST_THRESHOLD=0.5
```

### Resource Limits

```yaml
# docker-compose.prod.yml
agent_backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '0.5'
        memory: 512M
```

## 🛡️ Security Configuration

### Docker Security
```bash
# Run containers with non-root user
USER appuser

# Read-only root filesystem (where possible)
read_only: true

# Drop unnecessary capabilities
cap_drop:
  - ALL
cap_add:
  - CHOWN
  - SETUID
  - SETGID
```

### Network Security
```bash
# Only expose necessary ports
# Use internal networks for inter-service communication
# Implement network policies if using Kubernetes
```

### Secrets Management
```bash
# Use Docker secrets if using Docker Swarm
echo "your-secret" | docker secret create jwt_secret -

# Or use environment files with restricted permissions
chmod 600 .env
```

## 📊 Monitoring Setup

### Application Monitoring
```bash
# Install cAdvisor for container metrics
docker run -d \
  --name=cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --publish=8080:8080 \
  gcr.io/cadvisor/cadvisor:latest

# Install Node Exporter
docker run -d \
  --name=node-exporter \
  --volume=/proc:/host/proc:ro \
  --volume=/sys:/host/sys:ro \
  --volume=/:/rootfs:ro \
  --publish=9100:9100 \
  prom/node-exporter:latest
```

### Log Aggregation
```bash
# Use Docker's logging driver to forward to central system
logging:
  driver: "syslog"
  options:
    syslog-address: "tcp://logs.example.com:514"
    tag: "travel-assistant"
```

## 🚀 Scaling Considerations

### Horizontal Scaling
```bash
# Scale backend instances
docker-compose up -d --scale agent_backend=3

# Implement load balancer
# Use external LB or Docker swarm
```

### Database Replication
```bash
# PostgreSQL Streaming Replication
# Configure primary and standby servers
```

### Redis Clustering
```bash
# Redis Sentinel for high availability
# Or Redis Cluster for sharding
```

## 🔄 CI/CD Pipeline

### GitHub Actions Deployment
```yaml
# Create .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: easingthemes/ssh-deploy@v2.1.5
      env:
        SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        REMOTE_HOST: ${{ secrets.REMOTE_HOST }}
        REMOTE_USER: ${{ secrets.REMOTE_USER }}
        TARGET: /opt/travel-assistant
        
    - name: Execute deployment
      run: |
        ssh ${{ secrets.REMOTE_USER }}@${{ secrets.REMOTE_HOST }} \
          "cd /opt/travel-assistant && ./scripts/update-prod.sh"
```

## 💾 Backup Strategies

### Database Backups
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/travel-assistant"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# PostgreSQL backup
docker-compose exec -T postgres pg_dump -U postgres travel_assistant > $BACKUP_DIR/db_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-bucket/backups/
```

### Application Data Backup
```bash
# Backup uploads, logs, etc.
tar czf /backups/travel-assistant/app_$(date +%Y%m%d).tar.gz /opt/travel-assistant/logs/
```

## 🚨 Disaster Recovery

### Recovery Procedures
```bash
# Restore database
gunzip < /backups/db_20240101.sql.gz | docker-compose exec -T postgres psql -U postgres

# Restore application data
tar xzf /backups/app_20240101.tar.gz -C /opt/travel-assistant/

# Restart services
docker-compose restart
```

### Emergency Contacts
- Technical Lead: [Name] - [Phone]
- DevOps Team: [Name] - [Phone]
- Infrastructure Team: [Name] - [Phone]

## 📈 Performance Tuning

### Application Optimization
```bash
# Adjust worker processes based on CPU cores
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_users_email ON users(email);
```

### Redis Optimization
```bash
# Redis configuration for better performance
maxmemory 1gb
maxmemory-policy allkeys-lru
tcp-keepalive 60
timeout 300
```

## 📝 Maintenance Tasks

### Daily Tasks
- [ ] Check application logs for errors
- [ ] Monitor disk space
- [ ] Verify backups ran successfully

### Weekly Tasks
- [ ] Review performance metrics
- [ ] Check for security updates
- [ ] Analyze slow queries
- [ ] Review user activity logs

### Monthly Tasks
- [ ] Update Docker images
- [ ] Full system backup test
- [ ] Security audit
- [ ] Performance review

### Quarterly Tasks
- [ ] Disaster recovery drill
- [ ] Capacity planning review
- [ ] Security assessment
- [ ] Architecture review

## 📞 Support and Escalation

### Issue Severity Levels
- **Critical**: System down, data loss
- **High**: Major feature broken, performance severely degraded
- **Medium**: Minor feature issues, intermittent problems
- **Low**: Questions, minor bugs, documentation issues

### Escalation Path
1. **Level 1**: On-call developer
2. **Level 2**: Technical lead
3. **Level 3**: Engineering manager
4. **Level 4**: CTO/VP Engineering

## 📚 Additional Resources

- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Performance](https://redis.io/topics/performance)

---

**Next Steps**:
1. Review configuration with your team
2. Test deployment in staging environment
3. Set up monitoring and alerting
4. Create runbooks for common issues
5. Schedule disaster recovery drill
