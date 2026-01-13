"""
缓存管理器
提供高级缓存功能，包括缓存键生成、TTL 管理等
"""
import hashlib
import json
import logging
from typing import Any, Callable, Optional
from functools import wraps

from .redis_cache import RedisCache

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""

    # 缓存 TTL 配置（秒）
    TTL_SEARCH = 3600  # 1小时
    TTL_RECOMMEND = 21600  # 6小时
    TTL_DESTINATION = 86400  # 24小时
    TTL_BOOKING = 1800  # 30分钟
    TTL_TASK_STATUS = 300  # 5分钟
    TTL_DEFAULT = 3600  # 1小时

    def __init__(self, redis_cache: RedisCache):
        """
        初始化缓存管理器

        Args:
            redis_cache: Redis 缓存实例
        """
        self.redis = redis_cache
        self.prefix = "travel_assistant"

    def _generate_key(self, namespace: str, *args, **kwargs) -> str:
        """
        生成缓存键

        Args:
            namespace: 命名空间（如 "search", "recommend"）
            args: 位置参数
            kwargs: 关键字参数

        Returns:
            缓存键
        """
        # 将参数转换为可哈希的字符串
        key_parts = [namespace]
        
        # 添加位置参数
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True, ensure_ascii=False))
            else:
                key_parts.append(str(arg))
        
        # 添加关键字参数（按键排序以确保一致性）
        for k in sorted(kwargs.keys()):
            v = kwargs[k]
            if isinstance(v, (dict, list)):
                key_parts.append(f"{k}:{json.dumps(v, sort_keys=True, ensure_ascii=False)}")
            else:
                key_parts.append(f"{k}:{v}")
        
        # 生成哈希键
        key_str = ":".join(key_parts)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        
        return f"{self.prefix}:{namespace}:{key_hash}"

    def get_search_cache(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1,
        **kwargs
    ) -> Optional[dict]:
        """
        获取搜索结果缓存

        Args:
            origin: 出发地
            destination: 目的地
            departure_date: 出发日期
            return_date: 返程日期（可选）
            passengers: 乘客数
            **kwargs: 其他搜索参数

        Returns:
            缓存的搜索结果，如果不存在返回 None
        """
        key = self._generate_key(
            "search",
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            **kwargs
        )
        result = self.redis.get(key)
        if result:
            logger.info(f"搜索缓存命中: {origin} -> {destination}")
        return result

    def set_search_cache(
        self,
        data: dict,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1,
        **kwargs
    ) -> bool:
        """
        设置搜索结果缓存

        Args:
            data: 搜索结果数据
            origin: 出发地
            destination: 目的地
            departure_date: 出发日期
            return_date: 返程日期（可选）
            passengers: 乘客数
            **kwargs: 其他搜索参数

        Returns:
            是否设置成功
        """
        key = self._generate_key(
            "search",
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            **kwargs
        )
        success = self.redis.set(key, data, ttl=self.TTL_SEARCH)
        if success:
            logger.info(f"搜索缓存已设置: {origin} -> {destination}")
        return success

    def get_recommend_cache(
        self,
        destination: str,
        interests: Optional[list] = None,
        budget: Optional[str] = None,
        **kwargs
    ) -> Optional[dict]:
        """
        获取推荐结果缓存

        Args:
            destination: 目的地
            interests: 兴趣列表
            budget: 预算
            **kwargs: 其他参数

        Returns:
            缓存的推荐结果
        """
        key = self._generate_key(
            "recommend",
            destination=destination,
            interests=interests,
            budget=budget,
            **kwargs
        )
        result = self.redis.get(key)
        if result:
            logger.info(f"推荐缓存命中: {destination}")
        return result

    def set_recommend_cache(
        self,
        data: dict,
        destination: str,
        interests: Optional[list] = None,
        budget: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        设置推荐结果缓存

        Args:
            data: 推荐结果数据
            destination: 目的地
            interests: 兴趣列表
            budget: 预算
            **kwargs: 其他参数

        Returns:
            是否设置成功
        """
        key = self._generate_key(
            "recommend",
            destination=destination,
            interests=interests,
            budget=budget,
            **kwargs
        )
        success = self.redis.set(key, data, ttl=self.TTL_RECOMMEND)
        if success:
            logger.info(f"推荐缓存已设置: {destination}")
        return success

    def get_destination_cache(self, destination: str) -> Optional[dict]:
        """
        获取目的地信息缓存

        Args:
            destination: 目的地名称

        Returns:
            缓存的目的地信息
        """
        key = self._generate_key("destination", destination=destination)
        result = self.redis.get(key)
        if result:
            logger.info(f"目的地缓存命中: {destination}")
        return result

    def set_destination_cache(self, destination: str, data: dict) -> bool:
        """
        设置目的地信息缓存

        Args:
            destination: 目的地名称
            data: 目的地信息

        Returns:
            是否设置成功
        """
        key = self._generate_key("destination", destination=destination)
        success = self.redis.set(key, data, ttl=self.TTL_DESTINATION)
        if success:
            logger.info(f"目的地缓存已设置: {destination}")
        return success

    def get_task_status(self, task_id: str) -> Optional[dict]:
        """
        获取任务状态缓存

        Args:
            task_id: 任务 ID

        Returns:
            任务状态信息
        """
        key = self._generate_key("task_status", task_id=task_id)
        return self.redis.get(key)

    def set_task_status(self, task_id: str, status: dict) -> bool:
        """
        设置任务状态缓存

        Args:
            task_id: 任务 ID
            status: 状态信息

        Returns:
            是否设置成功
        """
        key = self._generate_key("task_status", task_id=task_id)
        return self.redis.set(key, status, ttl=self.TTL_TASK_STATUS)

    def invalidate_search_cache(self, origin: str, destination: str):
        """
        使搜索缓存失效

        Args:
            origin: 出发地
            destination: 目的地
        """
        pattern = f"{self.prefix}:search:*"
        count = self.redis.delete_pattern(pattern)
        logger.info(f"已清除 {count} 个搜索缓存")

    def invalidate_all(self, namespace: Optional[str] = None):
        """
        使所有缓存失效

        Args:
            namespace: 命名空间，None 表示所有
        """
        if namespace:
            pattern = f"{self.prefix}:{namespace}:*"
        else:
            pattern = f"{self.prefix}:*"
        
        count = self.redis.delete_pattern(pattern)
        logger.info(f"已清除 {count} 个缓存（命名空间: {namespace or 'all'}）")

    def cache_result(
        self,
        namespace: str,
        ttl: Optional[int] = None,
        key_func: Optional[Callable] = None
    ):
        """
        缓存装饰器

        Args:
            namespace: 缓存命名空间
            ttl: 过期时间（秒）
            key_func: 自定义键生成函数

        Returns:
            装饰器函数
        """
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_key(namespace, *args, **kwargs)

                # 尝试从缓存获取
                cached = self.redis.get(cache_key)
                if cached is not None:
                    logger.debug(f"缓存命中: {cache_key}")
                    return cached

                # 执行函数
                result = await func(*args, **kwargs)

                # 缓存结果
                cache_ttl = ttl or self.TTL_DEFAULT
                self.redis.set(cache_key, result, ttl=cache_ttl)
                logger.debug(f"缓存已设置: {cache_key}")

                return result

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_key(namespace, *args, **kwargs)

                # 尝试从缓存获取
                cached = self.redis.get(cache_key)
                if cached is not None:
                    logger.debug(f"缓存命中: {cache_key}")
                    return cached

                # 执行函数
                result = func(*args, **kwargs)

                # 缓存结果
                cache_ttl = ttl or self.TTL_DEFAULT
                self.redis.set(cache_key, result, ttl=cache_ttl)
                logger.debug(f"缓存已设置: {cache_key}")

                return result

            # 根据函数类型返回对应的包装器
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def get_stats(self) -> dict:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        return self.redis.get_stats()
