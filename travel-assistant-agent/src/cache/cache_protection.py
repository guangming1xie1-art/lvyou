"""
缓存击穿防护机制

提供分布式锁 + 双重检查模式，防止缓存击穿
"""
import asyncio
import json
import logging
import time
from typing import Any, Callable, Optional, Union
from contextlib import asynccontextmanager

from redis.exceptions import LockError

logger = logging.getLogger(__name__)


class CacheBreachProtection:
    """缓存击穿防护器"""
    
    def __init__(self, redis_client, default_ttl: int = 3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self._local_locks: dict = {}
        self._local_locks_lock = asyncio.Lock()
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
        lock_timeout: int = 30,
        lock_blocking_timeout: float = 5.0
    ) -> Any:
        """
        获取缓存值，如果不存在则调用 factory 生成并缓存
        
        实现逻辑：
        1. 先尝试从缓存获取
        2. 获取分布式锁（防止击穿）
        3. 双重检查（获取锁后再次检查缓存）
        4. 调用 factory 生成数据
        5. 写入缓存
        
        Args:
            key: 缓存键
            factory: 数据生成函数（可以是 sync 或 async）
            ttl: 缓存过期时间（秒）
            lock_timeout: 锁超时时间（秒）
            lock_blocking_timeout: 获取锁等待时间（秒）
            
        Returns:
            缓存的值或 factory 生成的值
        """
        if not self.redis or not self.redis.is_available():
            return await self._call_factory(factory)
        
        try:
            cached = await self.redis.get(key)
            if cached is not None:
                logger.debug(f"Cache hit: {key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        lock_key = f"lock:{key}"
        
        async with self._get_lock(lock_key, lock_timeout, lock_blocking_timeout):
            try:
                cached = await self.redis.get(key)
                if cached is not None:
                    logger.debug(f"Cache hit after lock: {key}")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache get after lock failed: {e}")
            
            result = await self._call_factory(factory)
            
            try:
                await self.redis.setex(key, ttl or self.default_ttl, json.dumps(result, ensure_ascii=False))
                logger.debug(f"Cache set: {key}")
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")
            
            return result
    
    async def get_or_set_many(
        self,
        keys: list[str],
        key_factory_map: dict[str, Callable[[], Any]],
        ttl: Optional[int] = None,
        lock_timeout: int = 30,
        lock_blocking_timeout: float = 5.0
    ) -> dict[str, Any]:
        """
        批量获取/设置缓存
        
        Args:
            keys: 缓存键列表
            key_factory_map: 键到工厂函数的映射
            ttl: 缓存过期时间
            lock_timeout: 锁超时时间
            lock_blocking_timeout: 获取锁等待时间
            
        Returns:
            键到值的映射
        """
        result = {}
        
        if not self.redis or not self.redis.is_available():
            for key in keys:
                result[key] = await self._call_factory(key_factory_map.get(key, lambda: None))
            return result
        
        uncached_keys = []
        
        try:
            cached_values = await self.redis.mget(keys)
            for key, cached in zip(keys, cached_values):
                if cached is not None:
                    result[key] = json.loads(cached)
                else:
                    uncached_keys.append(key)
        except Exception as e:
            logger.warning(f"Cache mget failed: {e}")
            uncached_keys = keys.copy()
        
        if not uncached_keys:
            return result
        
        lock_tasks = []
        locked_keys = set()
        
        for key in uncached_keys:
            lock_key = f"lock:{key}"
            lock = await self._get_lock(lock_key, lock_timeout, lock_blocking_timeout)
            lock_tasks.append((key, lock))
        
        for key, lock in lock_tasks:
            try:
                async with lock:
                    locked_keys.add(key)
                    
                    try:
                        cached = await self.redis.get(key)
                        if cached is not None:
                            result[key] = json.loads(cached)
                            continue
                    except Exception as e:
                        logger.warning(f"Cache get after lock failed: {e}")
                    
                    factory = key_factory_map.get(key, lambda: None)
                    value = await self._call_factory(factory)
                    result[key] = value
                    
                    try:
                        await self.redis.setex(key, ttl or self.default_ttl, json.dumps(value, ensure_ascii=False))
                    except Exception as e:
                        logger.warning(f"Cache set failed: {e}")
            except Exception as e:
                logger.warning(f"Lock acquisition failed for {key}: {e}")
                factory = key_factory_map.get(key, lambda: None)
                result[key] = await self._call_factory(factory)
        
        return result
    
    async def _call_factory(self, factory: Callable[[], Any]) -> Any:
        """调用工厂函数，支持 sync 和 async"""
        if asyncio.iscoroutinefunction(factory):
            return await factory()
        else:
            return factory()
    
    async def _get_lock(
        self,
        lock_key: str,
        timeout: int,
        blocking_timeout: float
    ) -> asyncio.Lock:
        """获取分布式锁或本地锁"""
        
        if not self.redis or not self.redis.is_available():
            return await self._get_local_lock(lock_key)
        
        try:
            lock = self.redis.client.lock(
                lock_key,
                timeout=timeout,
                blocking_timeout=blocking_timeout
            )
            
            acquired = await asyncio.to_thread(lock.acquire)
            if acquired:
                return _AsyncRedisLock(lock)
            else:
                logger.warning(f"Failed to acquire lock: {lock_key}")
                return await self._get_local_lock(lock_key)
        except Exception as e:
            logger.warning(f"Redis lock failed, using local lock: {e}")
            return await self._get_local_lock(lock_key)
    
    async def _get_local_lock(self, key: str) -> asyncio.Lock:
        """获取本地锁（Redis 不可用时的降级方案）"""
        async with self._local_locks_lock:
            if key not in self._local_locks:
                self._local_locks[key] = asyncio.Lock()
            return self._local_locks[key]
    
    async def invalidate(self, key: str) -> bool:
        """使缓存失效"""
        if not self.redis or not self.redis.is_available():
            return False
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """使匹配模式的所有缓存失效"""
        if not self.redis or not self.redis.is_available():
            return 0
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache pattern invalidation failed: {e}")
            return 0


class _AsyncRedisLock:
    """异步 Redis 锁包装器"""
    
    def __init__(self, lock):
        self._lock = lock
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            self._lock.release()
        except Exception as e:
            logger.warning(f"Lock release failed: {e}")


class CacheWithProtection:
    """
    缓存防护类的别名，保持向后兼容
    """
    
    def __init__(self, redis_cache, default_ttl: int = 3600):
        self.protection = CacheBreachProtection(redis_cache, default_ttl)
    
    async def get_or_set(self, key: str, factory: Callable, ttl: int = 3600):
        return await self.protection.get_or_set(key, factory, ttl)
