# 缓存策略文档

本文档详细说明系统的缓存架构、策略和最佳实践。

## 目录

1. [缓存架构](#缓存架构)
2. [缓存策略](#缓存策略)
3. [TTL 配置](#ttl-配置)
4. [缓存失效](#缓存失效)
5. [缓存键设计](#缓存键设计)
6. [使用指南](#使用指南)
7. [监控和维护](#监控和维护)

---

## 缓存架构

### 整体架构

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  API Layer  │
└──────┬──────┘
       │
       ↓
┌─────────────┐    命中 →  ┌─────────────┐
│Cache Manager│ ──────────→ │Redis Cache  │
└──────┬──────┘             └─────────────┘
       │ 未命中
       ↓
┌─────────────┐
│Backend/Java │
│    API      │
└─────────────┘
```

### 技术栈

- **Redis**: 分布式缓存存储
- **CacheManager**: 缓存管理抽象层
- **RedisCache**: Redis 客户端封装

---

## 缓存策略

### 1. 缓存穿透（Cache-Aside）

这是我们的主要缓存策略。

**流程:**

1. 查询缓存
2. 如果命中，直接返回
3. 如果未命中：
   - 查询数据源
   - 将结果写入缓存
   - 返回结果

**实现:**

```python
async def search_travel(request: SearchRequest, use_cache: bool = True):
    # 1. 尝试从缓存获取
    if use_cache and cache_manager:
        cached = cache_manager.get_search_cache(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date
        )
        if cached:
            return cached  # 缓存命中
    
    # 2. 缓存未命中，查询数据源
    result = await fetch_from_backend(request)
    
    # 3. 写入缓存
    if cache_manager and result:
        cache_manager.set_search_cache(
            data=result,
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date
        )
    
    return result
```

### 2. 缓存预热（Cache Warming）

对于热门数据，可以提前加载到缓存。

```python
async def warm_cache():
    """预热缓存 - 加载热门目的地"""
    hot_destinations = ["Tokyo", "Paris", "New York", "London"]
    
    for destination in hot_destinations:
        data = await fetch_destination_info(destination)
        cache_manager.set_destination_cache(destination, data)
```

### 3. 缓存更新策略

**Write-Through（同步写入）:**
- 数据更新时同时更新缓存
- 保证数据一致性
- 适用于预订、用户信息等

**Write-Behind（异步写入）:**
- 先更新缓存，异步更新数据库
- 提高写入性能
- 适用于统计数据、日志等

---

## TTL 配置

### 默认 TTL 值

| 数据类型 | TTL | 原因 |
|---------|-----|------|
| 搜索结果 | 1 小时 | 价格和可用性变化快 |
| 推荐结果 | 6 小时 | 内容相对稳定 |
| 目的地信息 | 24 小时 | 基础信息变化慢 |
| 预订信息 | 30 分钟 | 需要保持较新状态 |
| 任务状态 | 5 分钟 | 短期状态数据 |
| 用户会话 | 15 分钟 | 与 JWT token 同步 |

### 动态 TTL

某些缓存可以根据数据特性动态调整 TTL：

```python
def calculate_dynamic_ttl(data: dict) -> int:
    """根据数据特性计算 TTL"""
    base_ttl = 3600  # 1 小时
    
    # 如果价格波动大，缩短 TTL
    if data.get("price_volatility") == "high":
        return base_ttl // 2  # 30 分钟
    
    # 如果库存紧张，缩短 TTL
    if data.get("availability") == "limited":
        return base_ttl // 4  # 15 分钟
    
    # 如果数据稳定，延长 TTL
    if data.get("is_stable"):
        return base_ttl * 2  # 2 小时
    
    return base_ttl
```

---

## 缓存失效

### 1. 主动失效

#### 基于时间的失效

使用 TTL 自动过期：

```python
# 设置带 TTL 的缓存
cache_manager.set_search_cache(
    data=results,
    ttl=3600  # 1 小时后自动过期
)
```

#### 基于事件的失效

当数据更新时主动删除缓存：

```python
async def update_booking(booking_id: str, updates: dict):
    """更新预订并删除相关缓存"""
    # 更新数据
    await db.update_booking(booking_id, updates)
    
    # 删除缓存
    cache_manager.delete_booking_cache(booking_id)
    
    # 也可以删除相关的搜索缓存
    cache_manager.invalidate_search_cache(
        origin=updates["origin"],
        destination=updates["destination"]
    )
```

### 2. 缓存失效模式

#### 按模式删除

```python
# 删除所有搜索相关的缓存
cache_manager.invalidate_all(namespace="search")

# 删除特定目的地的所有缓存
cache_manager.delete_pattern("travel_assistant:*:Tokyo:*")
```

#### 批量失效

```python
def invalidate_user_cache(user_id: str):
    """删除用户相关的所有缓存"""
    patterns = [
        f"*:user:{user_id}:*",       # 用户数据
        f"*:booking:{user_id}:*",     # 预订记录
        f"*:preference:{user_id}:*",  # 用户偏好
    ]
    
    for pattern in patterns:
        cache_manager.delete_pattern(pattern)
```

---

## 缓存键设计

### 命名规范

```
{prefix}:{namespace}:{hash}

示例:
travel_assistant:search:md5(origin:destination:date:...)
travel_assistant:recommend:md5(destination:interests:budget)
travel_assistant:destination:Tokyo
```

### 键生成算法

```python
def _generate_key(self, namespace: str, *args, **kwargs) -> str:
    """生成缓存键"""
    key_parts = [namespace]
    
    # 添加位置参数
    for arg in args:
        if isinstance(arg, (dict, list)):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(arg))
    
    # 添加关键字参数（排序确保一致性）
    for k in sorted(kwargs.keys()):
        v = kwargs[k]
        if isinstance(v, (dict, list)):
            key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        else:
            key_parts.append(f"{k}:{v}")
    
    # 生成哈希
    key_str = ":".join(key_parts)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"{self.prefix}:{namespace}:{key_hash}"
```

### 键的特性

1. **确定性**: 相同输入总是生成相同的键
2. **唯一性**: 不同输入生成不同的键
3. **可读性**: 包含命名空间便于管理
4. **简洁性**: 使用哈希避免键过长

---

## 使用指南

### 基本使用

#### 初始化

```python
from src.cache import RedisCache, CacheManager

# 创建 Redis 客户端
redis_cache = RedisCache(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50
)

# 创建缓存管理器
cache_manager = CacheManager(redis_cache)
```

#### 搜索缓存

```python
# 获取缓存
cached = cache_manager.get_search_cache(
    origin='Beijing',
    destination='Tokyo',
    departure_date='2025-02-01',
    return_date='2025-02-10',
    passengers=2
)

# 设置缓存
cache_manager.set_search_cache(
    data=search_results,
    origin='Beijing',
    destination='Tokyo',
    departure_date='2025-02-01',
    return_date='2025-02-10',
    passengers=2
)
```

#### 推荐缓存

```python
# 获取缓存
cached = cache_manager.get_recommend_cache(
    destination='Tokyo',
    interests=['culture', 'food'],
    budget='medium'
)

# 设置缓存
cache_manager.set_recommend_cache(
    data=recommendations,
    destination='Tokyo',
    interests=['culture', 'food'],
    budget='medium'
)
```

### 高级使用

#### 装饰器缓存

```python
@cache_manager.cache_result(namespace="hotels", ttl=7200)
async def get_hotels(destination: str, check_in: str, check_out: str):
    """函数结果自动缓存"""
    return await fetch_hotels(destination, check_in, check_out)
```

#### 条件缓存

```python
async def search_with_cache(request: SearchRequest):
    # 仅对非紧急搜索使用缓存
    use_cache = not request.is_urgent
    
    if use_cache:
        cached = cache_manager.get_search_cache(...)
        if cached:
            return cached
    
    result = await perform_search(request)
    
    if use_cache:
        cache_manager.set_search_cache(data=result, ...)
    
    return result
```

#### 缓存分层

```python
# L1: 内存缓存（快速但容量小）
memory_cache = {}

# L2: Redis 缓存（较快且分布式）
redis_cache = cache_manager

async def get_with_layered_cache(key: str):
    # 先查 L1
    if key in memory_cache:
        return memory_cache[key]
    
    # 再查 L2
    result = redis_cache.get(key)
    if result:
        memory_cache[key] = result  # 回填 L1
        return result
    
    # 查数据源
    result = await fetch_from_source(key)
    
    # 写入两层缓存
    memory_cache[key] = result
    redis_cache.set(key, result)
    
    return result
```

---

## 监控和维护

### 缓存统计

```python
# 获取缓存统计信息
stats = cache_manager.get_stats()

print(f"缓存可用: {stats['available']}")
print(f"内存使用: {stats['used_memory_human']}")
print(f"命中率: {stats['hit_rate']}%")
print(f"命中次数: {stats['keyspace_hits']}")
print(f"未命中次数: {stats['keyspace_misses']}")
```

### 监控指标

#### 关键指标

1. **命中率** (Hit Rate)
   - 目标: > 70%
   - 公式: `hits / (hits + misses) * 100`

2. **内存使用** (Memory Usage)
   - 目标: < 80% 容量
   - 监控: `used_memory / maxmemory`

3. **响应时间** (Latency)
   - 目标: < 10ms
   - 监控 P95、P99

4. **逐出率** (Eviction Rate)
   - 目标: 尽可能低
   - 表示内存不足导致的数据驱逐

#### 监控 API

```python
@router.get("/api/cache/stats")
async def get_cache_stats():
    """获取缓存统计"""
    if not cache_manager or not cache_manager.redis.is_available():
        return {"available": False}
    
    return cache_manager.get_stats()
```

### 维护任务

#### 定期清理

```python
import asyncio
from datetime import datetime, timedelta

async def cleanup_old_cache():
    """清理过期缓存（定期任务）"""
    while True:
        try:
            # 删除超过 7 天的审计日志缓存
            cutoff = datetime.now() - timedelta(days=7)
            cache_manager.delete_pattern(f"*:audit:*:{cutoff.timestamp()}")
            
            # 等待 24 小时
            await asyncio.sleep(86400)
        except Exception as e:
            logger.error(f"缓存清理失败: {e}")
            await asyncio.sleep(3600)  # 失败后 1 小时重试
```

#### 缓存预热

```python
async def warm_popular_destinations():
    """预热热门目的地缓存"""
    destinations = await get_popular_destinations()
    
    for dest in destinations:
        try:
            info = await fetch_destination_info(dest)
            cache_manager.set_destination_cache(dest, info)
        except Exception as e:
            logger.error(f"预热失败 {dest}: {e}")
```

#### 健康检查

```python
async def cache_health_check() -> bool:
    """检查缓存系统健康状态"""
    if not cache_manager:
        return False
    
    # 测试写入
    test_key = "health_check_test"
    test_value = {"timestamp": datetime.now().isoformat()}
    
    if not cache_manager.redis.set(test_key, test_value, ttl=60):
        return False
    
    # 测试读取
    result = cache_manager.redis.get(test_key)
    if not result:
        return False
    
    # 清理测试键
    cache_manager.redis.delete(test_key)
    
    return True
```

---

## 故障处理

### 常见问题

#### 1. Redis 连接失败

**症状**: 应用无法连接到 Redis

**排查**:
```bash
# 检查 Redis 是否运行
redis-cli ping

# 检查连接配置
cat .env | grep REDIS

# 查看 Redis 日志
tail -f /var/log/redis/redis-server.log
```

**解决**:
- 启动 Redis: `redis-server`
- 检查网络: `telnet localhost 6379`
- 验证密码: `redis-cli -a your_password`

#### 2. 缓存命中率低

**症状**: 命中率 < 50%

**原因**:
- TTL 设置过短
- 缓存键不稳定（参数顺序问题）
- 查询模式不适合缓存

**解决**:
```python
# 检查键生成是否稳定
key1 = cache_manager._generate_key("search", origin="A", dest="B")
key2 = cache_manager._generate_key("search", dest="B", origin="A")
# key1 应该等于 key2（参数排序）

# 适当延长 TTL
cache_manager.TTL_SEARCH = 7200  # 2 小时

# 查看统计
stats = cache_manager.get_stats()
print(f"命中率: {stats['hit_rate']}%")
```

#### 3. 内存不足

**症状**: Redis 内存使用率 > 90%

**解决**:
```bash
# 检查内存使用
redis-cli info memory

# 手动清理
redis-cli FLUSHDB  # 警告：清空当前数据库

# 或配置 LRU 逐出策略
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

**预防**:
```python
# 配置合理的 TTL
# 定期清理过期数据
# 监控内存使用
```

---

## 最佳实践

### DO（推荐）

✅ **总是检查缓存可用性**
```python
if cache_manager and cache_manager.redis.is_available():
    cached = cache_manager.get_search_cache(...)
```

✅ **使用适当的 TTL**
```python
# 根据数据特性设置 TTL
cache_manager.set_search_cache(data, ttl=3600)  # 搜索: 1 小时
cache_manager.set_destination_cache(data, ttl=86400)  # 目的地: 24 小时
```

✅ **处理缓存失败**
```python
try:
    cached = cache_manager.get_search_cache(...)
    if cached:
        return cached
except Exception as e:
    logger.warning(f"缓存读取失败: {e}")
    # 降级到数据源
```

✅ **监控缓存性能**
```python
stats = cache_manager.get_stats()
if stats['hit_rate'] < 50:
    logger.warning("缓存命中率过低")
```

### DON'T（不推荐）

❌ **不要缓存敏感数据**
```python
# 不要缓存密码、token 等
cache_manager.set("user_password", password)  # 危险！
```

❌ **不要使用过长的 TTL**
```python
# 避免数据过时
cache_manager.set_search_cache(data, ttl=604800)  # 7 天太长！
```

❌ **不要忽略缓存失败**
```python
# 不要假设缓存总是可用
cached = cache_manager.get(...)  # 可能返回 None
return cached.get("data")  # AttributeError!
```

❌ **不要缓存个性化数据**
```python
# 用户特定的数据不适合共享缓存
cache_manager.set("recommendations", user_specific_data)
# 应该包含用户 ID: cache_manager.set(f"recommendations:{user_id}", data)
```

---

## 参考资料

- [Redis 官方文档](https://redis.io/documentation)
- [缓存策略模式](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [FastAPI Caching](https://fastapi.tiangolo.com/advanced/middleware/)

---

**最后更新**: 2025-01-13
**版本**: 1.0.0
