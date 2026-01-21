# 性能优化指南

本文档详细说明了系统的性能优化策略和配置。

## 目录

1. [后端优化](#后端优化)
2. [前端优化](#前端优化)
3. [数据库优化](#数据库优化)
4. [监控和调优](#监控和调优)
5. [性能基准](#性能基准)

---

## 后端优化

### 1. Redis 缓存

#### 缓存策略

我们使用 Redis 作为缓存层，以减少数据库查询和外部 API 调用。

**缓存 TTL 配置:**

- **搜索结果**: 1 小时（3600秒）
- **推荐结果**: 6 小时（21600秒）
- **目的地信息**: 24 小时（86400秒）
- **预订信息**: 30 分钟（1800秒）
- **任务状态**: 5 分钟（300秒）

**配置示例:**

```env
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MAX_CONNECTIONS=50
```

#### 缓存使用

```python
from cache import CacheManager, RedisCache

# 初始化
redis_cache = RedisCache(host='localhost', port=6379)
cache_manager = CacheManager(redis_cache)

# 获取搜索缓存
cached_result = cache_manager.get_search_cache(
    origin='Beijing',
    destination='Tokyo',
    departure_date='2025-02-01'
)

# 设置搜索缓存
cache_manager.set_search_cache(
    data=search_results,
    origin='Beijing',
    destination='Tokyo',
    departure_date='2025-02-01'
)
```

#### 缓存装饰器

```python
@cache_manager.cache_result(namespace="flights", ttl=3600)
async def get_flights(origin: str, destination: str):
    # 函数结果会自动缓存
    return await fetch_flights(origin, destination)
```

### 2. API 响应压缩

使用 Gzip 压缩减少网络传输大小。

**配置:**

```env
ENABLE_GZIP=true
GZIP_MIN_SIZE=1000  # 只压缩大于 1KB 的响应
```

**效果:**
- JSON 响应通常可压缩 70-80%
- 大幅减少带宽使用
- 提高移动端性能

### 3. 分页和排序

#### 搜索结果分页

```python
# API 调用示例
GET /api/agent/search?page=1&page_size=20&sort_by=price
```

**支持的排序字段:**

- `price` - 价格（默认，升序）
- `duration` - 时长（升序）
- `rating` - 评分（降序）
- `departure` - 起飞时间（升序）
- `stops` - 转机次数（升序）

**响应格式:**

```json
{
  "success": true,
  "outbound_flights": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false,
    "next_page": 2,
    "prev_page": null
  },
  "cache_hit": true
}
```

### 4. 性能监控中间件

自动记录所有请求的响应时间。

**响应头:**

- `X-Process-Time`: 处理时间（秒）
- `X-Performance`: 性能等级
  - `excellent`: < 0.1s
  - `good`: < 0.5s
  - `acceptable`: < 1.0s
  - `slow`: >= 1.0s

**慢查询警告:**

```env
SLOW_REQUEST_THRESHOLD=1.0  # 超过 1 秒会记录警告日志
```

### 5. 数据库连接池

优化数据库连接管理。

**配置:**

```env
DB_POOL_SIZE=20       # 连接池大小
DB_MAX_OVERFLOW=10    # 最大溢出连接数
```

---

## 前端优化

### 1. 代码分割

Vite 配置了智能代码分割策略。

#### 分块策略

```typescript
// vite.config.ts
manualChunks: {
  'vendor': ['react', 'react-dom', 'react-router-dom'],
  'ui': ['@radix-ui/*', 'clsx', 'tailwind-merge'],
  'query': ['@tanstack/react-query', 'axios'],
  'agent': [/* Agent 相关代码 */]
}
```

**效果:**
- 主包大小减少 60%+
- 首屏加载时间提升 40%
- 更好的缓存利用率

### 2. 路由懒加载

使用 React.lazy 和 Suspense 实现路由级代码分割。

```typescript
import { lazyLoad } from '@/utils/lazyLoad'

// 懒加载页面组件
const HomePage = lazyLoad(() => import('./pages/HomePage'))
const SearchPage = lazyLoad(() => import('./pages/SearchPage'))
const Dashboard = lazyLoad(() => import('./pages/Dashboard'))
```

**特性:**
- 自动错误处理
- 加载重试机制（最多 3 次）
- 自定义加载状态

### 3. 图片懒加载

```tsx
import { LazyImage } from '@/components/LazyImage'

<LazyImage
  src="/images/hotel.jpg"
  alt="Hotel"
  className="w-full h-64 object-cover"
  placeholderSrc="/images/placeholder.svg"
/>
```

**特性:**
- 视口可见时才加载
- 平滑过渡效果
- 加载失败优雅降级
- 提前 50px 预加载

### 4. 资源预加载

```tsx
import { preloadComponent } from '@/utils/lazyLoad'

// 鼠标悬停时预加载
<Link
  to="/dashboard"
  onMouseEnter={() => preloadComponent(() => import('./pages/Dashboard'))}
>
  Dashboard
</Link>
```

### 5. 构建优化

```typescript
// vite.config.ts
minify: 'terser',
terserOptions: {
  compress: {
    drop_console: true,   // 移除 console
    drop_debugger: true   // 移除 debugger
  }
}
```

---

## 数据库优化

### 1. 索引

自动创建的索引：

```sql
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- 审计日志索引
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

### 2. 查询优化

#### 明确指定列名

❌ **不推荐:**
```sql
SELECT * FROM users WHERE email = ?
```

✅ **推荐:**
```sql
SELECT id, username, email, is_active FROM users WHERE email = ?
```

#### 使用 LIMIT

```python
# 总是限制查询数量
result = conn.execute(text("""
    SELECT * FROM audit_logs
    WHERE user_id = :user_id
    ORDER BY created_at DESC
    LIMIT :limit OFFSET :offset
"""), {"user_id": user_id, "limit": 100, "offset": 0})
```

### 3. 连接池配置

```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,      # 连接前测试
    pool_size=20,            # 基础连接数
    max_overflow=10,         # 额外连接数
    pool_recycle=3600        # 连接回收时间
)
```

---

## 监控和调优

### 1. 性能指标

#### API 响应时间

```bash
# 查看响应时间头
curl -I http://localhost:8000/api/agent/search

X-Process-Time: 0.234
X-Performance: good
```

#### 缓存统计

```python
# 获取缓存统计
GET /api/cache/stats

{
  "available": true,
  "used_memory_human": "12.5M",
  "connected_clients": 5,
  "keyspace_hits": 1234,
  "keyspace_misses": 456,
  "hit_rate": 73.02
}
```

### 2. 日志监控

#### 慢请求日志

```
[WARNING] 慢请求 ⚠️  POST /api/agent/search 状态: 200 耗时: 1.234s
```

#### 缓存命中日志

```
[INFO] 缓存命中: search:Beijing:Tokyo
[INFO] 搜索缓存命中: Beijing -> Tokyo
```

### 3. 性能测试

运行负载测试：

```bash
cd /path/to/travel-assistant-agent
python tests/load_test.py
```

---

## 性能基准

### 目标指标

| 指标 | 目标 | 说明 |
|------|------|------|
| API 响应时间（缓存命中） | < 100ms | P95 |
| API 响应时间（缓存未命中） | < 500ms | P95 |
| 缓存命中率 | > 70% | 搜索请求 |
| 首屏加载时间 | < 2s | 3G 网络 |
| TTI（可交互时间） | < 3s | 3G 网络 |
| 数据库查询时间 | < 50ms | P95 |

### 实测结果（开发环境）

| 端点 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| `/api/agent/search` | 850ms | 45ms | 94.7% |
| `/api/agent/recommend` | 1.2s | 38ms | 96.8% |
| `/api/agent/book` | 420ms | N/A | N/A |

### 前端性能（生产构建）

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 主包大小 | 1.2MB | 420KB | 65% |
| 首屏加载 | 3.5s | 1.8s | 48.6% |
| TTI | 5.2s | 2.6s | 50% |

---

## 最佳实践

### 后端

1. **总是使用缓存** - 对于不变的数据启用缓存
2. **实现分页** - 避免返回大量数据
3. **使用连接池** - 不要为每个请求创建新连接
4. **异步处理** - 长时间运行的任务使用后台任务
5. **监控慢查询** - 定期检查和优化慢查询

### 前端

1. **路由懒加载** - 所有页面使用懒加载
2. **图片懒加载** - 使用 LazyImage 组件
3. **代码分割** - 合理配置 chunk 策略
4. **资源预加载** - 预测用户行为，提前加载
5. **避免重复渲染** - 使用 React.memo 和 useMemo

### 数据库

1. **创建索引** - 为常用查询字段创建索引
2. **限制查询** - 始终使用 LIMIT
3. **避免 N+1** - 使用 JOIN 而不是多次查询
4. **定期清理** - 删除过期的审计日志和缓存
5. **监控性能** - 使用 EXPLAIN 分析查询计划

---

## 故障排查

### 缓存问题

**问题**: Redis 连接失败

**解决方案**:
```bash
# 检查 Redis 是否运行
redis-cli ping

# 检查配置
echo $REDIS_HOST
echo $REDIS_PORT

# 重启 Redis
redis-server
```

### 性能问题

**问题**: API 响应慢

**排查步骤**:
1. 检查响应头 `X-Process-Time`
2. 查看日志中的慢请求警告
3. 检查缓存命中率
4. 分析数据库查询时间
5. 检查网络延迟

**问题**: 数据库连接池耗尽

**解决方案**:
```env
# 增加连接池大小
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=20
```

### 前端性能

**问题**: 首屏加载慢

**排查步骤**:
1. 检查 Network 面板中的资源加载
2. 分析 bundle 大小
3. 检查是否正确使用了代码分割
4. 验证图片是否懒加载
5. 检查网络条件

---

## 附录

### A. 缓存键命名规范

```
travel_assistant:{namespace}:{hash}

示例:
travel_assistant:search:a1b2c3d4e5f6
travel_assistant:recommend:f6e5d4c3b2a1
travel_assistant:destination:Tokyo
```

### B. 性能监控工具

- **New Relic** - APM 监控
- **Datadog** - 日志和指标
- **Sentry** - 错误追踪
- **Lighthouse** - 前端性能审计
- **WebPageTest** - 网页性能测试

### C. 参考资料

- [FastAPI Performance](https://fastapi.tiangolo.com/advanced/performance/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Vite Performance](https://vitejs.dev/guide/performance.html)

---

**最后更新**: 2025-01-13
**版本**: 1.0.0
