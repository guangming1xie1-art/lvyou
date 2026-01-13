# 快速开始指南 - 性能优化版本

本指南帮助你快速启动带有性能优化的旅行助手系统。

## 前置要求

### 必需
- Python 3.9+
- Node.js 16+
- Redis 7+
- PostgreSQL 15+

### 可选（推荐）
- Docker & Docker Compose

## 方式一：使用 Docker Compose（推荐）

### 1. 启动所有服务

```bash
# 克隆项目（如果需要）
cd /path/to/travel-assistant

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 2. 验证服务

```bash
# 检查服务状态
docker-compose ps

# 应该看到：
# - redis (健康)
# - postgres (健康)
# - agent (健康)
# - frontend (运行中)
```

### 3. 访问应用

- **前端**: http://localhost:3000
- **Agent API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

### 4. 测试性能

```bash
# 进入 agent 容器
docker-compose exec agent bash

# 运行负载测试
python tests/load_test.py

# 运行缓存测试
pytest tests/test_cache.py -v

# 运行分页测试
pytest tests/test_pagination.py -v
```

## 方式二：本地开发

### 1. 启动 Redis

```bash
# 使用 Docker
docker run -d -p 6379:6379 redis:7-alpine

# 或直接运行
redis-server
```

### 2. 启动 PostgreSQL

```bash
# 使用 Docker
docker run -d \
  -p 5432:5432 \
  -e POSTGRES_DB=travel_assistant \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  postgres:15-alpine

# 或使用本地安装
psql -U postgres -c "CREATE DATABASE travel_assistant;"
```

### 3. 启动 Agent 服务

```bash
cd travel-assistant-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 编辑 .env 文件
# 确保配置：
# REDIS_ENABLED=true
# REDIS_HOST=localhost
# REDIS_PORT=6379
# DB_HOST=localhost
# DB_PORT=5432

# 启动服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 启动前端

```bash
cd travel-assistant-front

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 编辑 .env 文件
# VITE_AGENT_API_BASE_URL=http://localhost:8000

# 启动开发服务器
npm run dev
```

### 5. 验证安装

```bash
# 检查 Redis
redis-cli ping
# 应返回: PONG

# 检查 Agent API
curl http://localhost:8000/health
# 应返回: {"status": "healthy", ...}

# 检查缓存统计
curl http://localhost:8000/api/cache/stats
# 应返回缓存统计信息

# 检查前端
curl http://localhost:3000
# 应返回 HTML 页面
```

## 性能优化验证

### 1. 测试缓存效果

```bash
cd travel-assistant-agent

# 第一次请求（应该未命中缓存）
curl -X POST http://localhost:8000/api/agent/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "origin": "Beijing",
    "destination": "Tokyo",
    "departure_date": "2025-02-01",
    "passengers": 2
  }'

# 查看响应头中的 X-Process-Time
# 第一次应该较慢（如 850ms）

# 第二次请求（应该命中缓存）
# 重复上面的请求
# 第二次应该很快（如 45ms）
# 响应中 cache_hit 应为 true
```

### 2. 测试分页

```bash
# 获取第一页
curl "http://localhost:8000/api/agent/search?page=1&page_size=10&sort_by=price" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"origin":"Beijing","destination":"Tokyo","departure_date":"2025-02-01"}'

# 响应中应该包含 pagination 对象：
# {
#   "pagination": {
#     "page": 1,
#     "page_size": 10,
#     "total": 156,
#     "total_pages": 16,
#     "has_next": true
#   }
# }
```

### 3. 运行负载测试

```bash
cd travel-assistant-agent

# 运行完整的负载测试
python tests/load_test.py

# 你应该看到：
# - 缓存命中率 > 70%
# - 平均响应时间（缓存命中）< 100ms
# - 平均响应时间（未命中）< 500ms
```

### 4. 检查前端优化

```bash
cd travel-assistant-front

# 构建生产版本
npm run build

# 检查 bundle 大小
ls -lh dist/assets/

# 你应该看到：
# - vendor-*.js (React 等核心库，~200KB gzipped)
# - ui-*.js (UI 组件，~50KB gzipped)
# - query-*.js (React Query，~30KB gzipped)
# - 主入口文件 (~150KB gzipped)
# 总计应该 < 500KB gzipped
```

## 监控性能

### 实时监控

```bash
# 查看 Agent 日志
tail -f logs/app.log

# 你应该看到：
# [INFO] 缓存命中: search:Beijing:Tokyo
# [INFO] GET /api/agent/search 状态: 200 耗时: 0.045s
# [WARNING] 慢请求 ⚠️  POST /api/agent/search 耗时: 1.234s (如果有慢请求)
```

### Redis 监控

```bash
# 进入 Redis CLI
redis-cli

# 查看缓存键
KEYS travel_assistant:*

# 查看内存使用
INFO memory

# 查看命中率
INFO stats
```

### 数据库监控

```bash
# 进入 PostgreSQL
psql -U postgres -d travel_assistant

# 查看索引
\di

# 查看表大小
\dt+

# 查看慢查询（如果启用了 pg_stat_statements）
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

## 常见问题

### Redis 连接失败

**问题**: `Redis connection failed`

**解决**:
```bash
# 检查 Redis 是否运行
redis-cli ping

# 如果未运行，启动 Redis
redis-server

# 或使用 Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 缓存命中率低

**问题**: 缓存命中率 < 50%

**排查**:
```python
# 检查缓存键是否一致
from src.cache import CacheManager, RedisCache

redis = RedisCache()
manager = CacheManager(redis)

# 查看缓存键
redis.client.keys("travel_assistant:*")
```

### 数据库连接失败

**问题**: `Database connection failed`

**解决**:
```bash
# 检查 PostgreSQL 是否运行
psql -U postgres -l

# 检查连接配置
cat .env | grep DB_

# 重置数据库（如果需要）
psql -U postgres -c "DROP DATABASE IF EXISTS travel_assistant;"
psql -U postgres -c "CREATE DATABASE travel_assistant;"
```

### 前端构建失败

**问题**: `Build failed with Vite`

**解决**:
```bash
cd travel-assistant-front

# 清理缓存
rm -rf node_modules dist

# 重新安装
npm install

# 构建
npm run build
```

## 性能调优建议

### 1. 增加缓存 TTL（如果数据变化不频繁）

编辑 `src/cache/cache_manager.py`:
```python
TTL_SEARCH = 7200  # 从 1 小时改为 2 小时
TTL_RECOMMEND = 43200  # 从 6 小时改为 12 小时
```

### 2. 增加连接池大小（高负载时）

编辑 `.env`:
```env
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=20
REDIS_MAX_CONNECTIONS=100
```

### 3. 调整分页大小

编辑 API 请求:
```bash
# 较小的页面加载更快
?page=1&page_size=10

# 较大的页面减少请求次数
?page=1&page_size=50
```

### 4. 启用 CDN（生产环境）

对于静态资源，使用 CDN 可以大幅提升加载速度：
- 前端静态文件（JS、CSS、图片）
- 第三方库（从 CDN 加载 React 等）

## 下一步

1. **查看文档**
   - `PERFORMANCE.md` - 完整的性能优化指南
   - `CACHING_STRATEGY.md` - 缓存策略详解
   - `PERFORMANCE_OPTIMIZATION_SUMMARY.md` - 实施总结

2. **运行测试**
   ```bash
   pytest tests/test_cache.py -v
   pytest tests/test_pagination.py -v
   python tests/load_test.py
   ```

3. **配置监控**
   - 设置 APM 监控（New Relic、Datadog）
   - 配置日志聚合（ELK、Loki）
   - 设置告警（慢查询、高错误率）

4. **持续优化**
   - 定期查看性能指标
   - 根据实际使用情况调整 TTL
   - 优化慢查询
   - 监控缓存命中率

## 获取帮助

- 查看日志: `docker-compose logs -f agent`
- 查看文档: `PERFORMANCE.md`, `CACHING_STRATEGY.md`
- 运行健康检查: `curl http://localhost:8000/health`

---

**祝你使用愉快！** 🚀
