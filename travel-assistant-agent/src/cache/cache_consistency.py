"""
缓存一致性方案

提供两种策略：
1. 消息队列通知 - Java 服务发布事件，Python 消费并清除缓存
2. 短 TTL + 主动刷新 - 提前刷新即将过期的缓存
"""
import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

from conf import settings

logger = logging.getLogger(__name__)


class CacheEventType(Enum):
    """缓存事件类型"""
    PRICE_UPDATED = "price_updated"
    INVENTORY_UPDATED = "inventory_updated"
    HOTEL_UPDATED = "hotel_updated"
    FLIGHT_UPDATED = "flight_updated"
    USER_PREFERENCE_UPDATED = "user_preference_updated"
    BOOKING_CANCELLED = "booking_cancelled"


@dataclass
class CacheInvalidationRule:
    """缓存失效规则"""
    event_type: CacheEventType
    key_patterns: list[str]
    namespace: str


class CacheInvalidationConsumer:
    """
    缓存失效消费者
    
    监听消息队列，接收 Java 服务发布的缓存失效事件
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self._rules: list[CacheInvalidationRule] = []
        self._subscription_task: Optional[asyncio.Task] = None
        self._register_default_rules()
    
    def _register_default_rules(self):
        """注册默认失效规则"""
        self._rules = [
            CacheInvalidationRule(
                event_type=CacheEventType.PRICE_UPDATED,
                key_patterns=["search:*", "recommend:*"],
                namespace="travel_assistant"
            ),
            CacheInvalidationRule(
                event_type=CacheEventType.INVENTORY_UPDATED,
                key_patterns=["search:*", "booking:*"],
                namespace="travel_assistant"
            ),
            CacheInvalidationRule(
                event_type=CacheEventType.HOTEL_UPDATED,
                key_patterns=["hotel:*", "recommend:*"],
                namespace="travel_assistant"
            ),
            CacheInvalidationRule(
                event_type=CacheEventType.FLIGHT_UPDATED,
                key_patterns=["flight:*", "search:*"],
                namespace="travel_assistant"
            ),
            CacheInvalidationRule(
                event_type=CacheEventType.USER_PREFERENCE_UPDATED,
                key_patterns=["preference:*", "memory:*"],
                namespace="travel_assistant"
            ),
            CacheInvalidationRule(
                event_type=CacheEventType.BOOKING_CANCELLED,
                key_patterns=["booking:*"],
                namespace="travel_assistant"
            ),
        ]
    
    async def start(self):
        """启动消费者"""
        self._subscription_task = asyncio.create_task(self._listen_messages())
        logger.info("Cache invalidation consumer started")
    
    async def stop(self):
        """停止消费者"""
        if self._subscription_task:
            self._subscription_task.cancel()
            try:
                await self._subscription_task
            except asyncio.CancelledError:
                pass
        logger.info("Cache invalidation consumer stopped")
    
    async def _listen_messages(self):
        """监听消息队列"""
        while True:
            try:
                if self.redis and self.redis.is_available():
                    message = await self.redis.blpop("cache_invalidation:queue", timeout=5)
                    if message:
                        _, msg_data = message
                        await self.on_message(json.loads(msg_data))
                else:
                    await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error listening to cache invalidation queue: {e}")
                await asyncio.sleep(1)
    
    async def on_message(self, message: dict):
        """
        处理缓存失效消息
        
        Args:
            message: 消息格式
                {
                    "type": "price_updated",
                    "entity_id": "hotel_123",
                    "entity_type": "hotel",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
        """
        event_type = message.get("type")
        entity_id = message.get("entity_id")
        
        logger.info(f"Received cache invalidation event: {event_type}, entity: {entity_id}")
        
        for rule in self._rules:
            if rule.event_type.value == event_type:
                for pattern in rule.key_patterns:
                    full_pattern = f"{rule.namespace}:{pattern}"
                    if entity_id:
                        full_pattern = f"{full_pattern}:*{entity_id}*"
                    
                    await self._invalidate_pattern(full_pattern)
    
    async def _invalidate_pattern(self, pattern: str):
        """使匹配模式的所有缓存失效"""
        try:
            if self.redis and self.redis.is_available():
                keys = await self.redis.keys(pattern)
                if keys:
                    deleted = await self.redis.delete(*keys)
                    logger.info(f"Invalidated {deleted} cache keys matching pattern: {pattern}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache pattern {pattern}: {e}")
    
    async def invalidate(self, key: str):
        """使指定缓存失效"""
        try:
            if self.redis and self.redis.is_available():
                await self.redis.delete(key)
                logger.info(f"Invalidated cache key: {key}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache key {key}: {e}")
    
    def register_rule(self, event_type: CacheEventType, key_patterns: list[str]):
        """注册自定义失效规则"""
        self._rules.append(CacheInvalidationRule(
            event_type=event_type,
            key_patterns=key_patterns,
            namespace="travel_assistant"
        ))


class SmartCache:
    """
    智能缓存 - 短 TTL + 主动刷新
    
    特点：
    1. 使用较短的 TTL
    2. 缓存即将过期时异步刷新
    3. 不阻塞主请求
    """
    
    def __init__(
        self,
        redis_client,
        default_ttl: int = 300,
        refresh_threshold: int = 60
    ):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.refresh_threshold = refresh_threshold
        self._refresh_tasks: Dict[str, asyncio.Task] = {}
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """
        获取缓存，如果不存在则调用 factory 生成
        
        Args:
            key: 缓存键
            factory: 数据生成函数
            ttl: 缓存过期时间
            
        Returns:
            缓存值或 factory 生成的值
        """
        if not self.redis or not self.redis.is_available():
            return await self._call_factory(factory)
        
        try:
            value = await self.redis.get(key)
            
            if value is not None:
                asyncio.create_task(self._refresh_if_needed(key, factory, ttl))
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        result = await self._call_factory(factory)
        
        try:
            await self.redis.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(result, ensure_ascii=False)
            )
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
        
        return result
    
    async def _refresh_if_needed(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int]
    ):
        """如果缓存即将过期，提前刷新"""
        if key in self._refresh_tasks:
            return
        
        try:
            cache_ttl = await self.redis.ttl(key)
            
            if 0 < cache_ttl < self.refresh_threshold:
                self._refresh_tasks[key] = asyncio.create_task(
                    self._do_refresh(key, factory, ttl)
                )
        except Exception as e:
            logger.warning(f"Failed to check TTL for refresh: {e}")
    
    async def _do_refresh(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int]
    ):
        """执行缓存刷新"""
        try:
            result = await self._call_factory(factory)
            await self.redis.setex(
                key,
                ttl or self.default_ttl,
                json.dumps(result, ensure_ascii=False)
            )
            logger.debug(f"Cache refreshed: {key}")
        except Exception as e:
            logger.warning(f"Cache refresh failed for {key}: {e}")
        finally:
            self._refresh_tasks.pop(key, None)
    
    async def _call_factory(self, factory: Callable[[], Any]) -> Any:
        """调用工厂函数"""
        if asyncio.iscoroutinefunction(factory):
            return await factory()
        return factory()


class CacheConsistencyManager:
    """
    缓存一致性管理器
    
    整合消息队列通知和智能缓存两种方案
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.consumer = CacheInvalidationConsumer(redis_client)
        self.smart_cache = SmartCache(redis_client)
    
    async def start(self):
        """启动管理器"""
        await self.consumer.start()
        logger.info("Cache consistency manager started")
    
    async def stop(self):
        """停止管理器"""
        await self.consumer.stop()
        logger.info("Cache consistency manager stopped")
    
    def get_smart_cache(self) -> SmartCache:
        """获取智能缓存实例"""
        return self.smart_cache


cache_consistency_manager: Optional[CacheConsistencyManager] = None


async def init_cache_consistency(redis_client) -> CacheConsistencyManager:
    """初始化缓存一致性管理器"""
    global cache_consistency_manager
    cache_consistency_manager = CacheConsistencyManager(redis_client)
    await cache_consistency_manager.start()
    return cache_consistency_manager
