"""
缓存策略模块
提供高级缓存功能和Cache-Aside模式实现
"""
from .redis_cache import RedisCache
from .cache_key import CacheKeyGenerator
from typing import Optional, Any, Callable, Dict, List
import logging
import os

logger = logging.getLogger(__name__)


class CacheStrategy:
    """缓存策略管理（高级缓存功能）"""
    
    # TTL配置（秒）- 可通过环境变量覆盖
    TTL_CONFIG = {
        "search_results": int(os.getenv("CACHE_TTL_SEARCH", "3600")),       # 1小时
        "recommendations": int(os.getenv("CACHE_TTL_RECOMMEND", "21600")),  # 6小时
        "rag_context": int(os.getenv("CACHE_TTL_RAG", "3600")),            # 1小时
        "booking_info": int(os.getenv("CACHE_TTL_BOOKING", "1800")),       # 30分钟
        "user_preferences": int(os.getenv("CACHE_TTL_USER_PREFS", "86400")), # 24小时
        "destination": int(os.getenv("CACHE_TTL_DESTINATION", "86400")),    # 24小时
        "workflow_state": int(os.getenv("CACHE_TTL_WORKFLOW", "3600")),     # 1小时
        "default": 3600,  # 默认1小时
    }
    
    def __init__(
        self,
        redis_cache: Optional[RedisCache] = None,
        prefix: str = "travel_assistant"
    ):
        """
        初始化缓存策略
        
        Args:
            redis_cache: Redis缓存实例
            prefix: 缓存键前缀
        """
        self.redis = redis_cache or RedisCache()
        self.prefix = prefix
    
    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable,
        cache_type: str = "default",
        ttl: Optional[int] = None
    ) -> Any:
        """
        获取或计算值（Cache-Aside模式）
        
        Args:
            key: 缓存键
            compute_fn: 计算函数
            cache_type: 缓存类型
            ttl: 过期时间
            
        Returns:
            缓存值或计算结果
        """
        # 尝试从缓存获取
        cached_value = self.redis.get(key)
        if cached_value is not None:
            logger.debug(f"Cache HIT: {key}")
            return cached_value
        
        logger.debug(f"Cache MISS: {key}, computing...")
        
        # 计算值
        value = compute_fn()
        
        # 存储到缓存
        cache_ttl = ttl or self.TTL_CONFIG.get(cache_type, self.TTL_CONFIG["default"])
        self.redis.set(key, value, ttl=cache_ttl)
        
        return value
    
    async def get_or_compute_async(
        self,
        key: str,
        compute_fn: Callable,
        cache_type: str = "default",
        ttl: Optional[int] = None
    ) -> Any:
        """
        异步获取或计算值（Cache-Aside模式）
        
        Args:
            key: 缓存键
            compute_fn: 异步计算函数
            cache_type: 缓存类型
            ttl: 过期时间
            
        Returns:
            缓存值或计算结果
        """
        cached_value = self.redis.get(key)
        if cached_value is not None:
            logger.debug(f"Cache HIT (async): {key}")
            return cached_value
        
        logger.debug(f"Cache MISS (async): {key}, computing...")
        
        value = await compute_fn()
        
        cache_ttl = ttl or self.TTL_CONFIG.get(cache_type, self.TTL_CONFIG["default"])
        self.redis.set(key, value, ttl=cache_ttl)
        
        return value
    
    def cache_search_results(
        self,
        query: str,
        results: Dict,
        origin: Optional[str] = None,
        destination: Optional[str] = None
    ) -> bool:
        """
        缓存搜索结果
        
        Args:
            query: 搜索查询
            results: 搜索结果
            origin: 出发地
            destination: 目的地
            
        Returns:
            是否缓存成功
        """
        key = CacheKeyGenerator.generate_search_key(
            query, origin, destination
        )
        key = f"{self.prefix}:search:{key}"
        return self.redis.set(key, results, ttl=self.TTL_CONFIG["search_results"])
    
    def get_search_results(
        self,
        query: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None
    ) -> Optional[Dict]:
        """
        获取缓存的搜索结果
        
        Args:
            query: 搜索查询
            origin: 出发地
            destination: 目的地
            
        Returns:
            缓存的搜索结果
        """
        key = CacheKeyGenerator.generate_search_key(
            query, origin, destination
        )
        key = f"{self.prefix}:search:{key}"
        return self.redis.get(key)
    
    def cache_recommendations(
        self,
        user_id: str,
        recommendations: Dict,
        interests: Optional[List[str]] = None,
        budget: Optional[str] = None
    ) -> bool:
        """
        缓存推荐结果
        
        Args:
            user_id: 用户ID
            recommendations: 推荐结果
            interests: 兴趣列表
            budget: 预算
            
        Returns:
            是否缓存成功
        """
        key = CacheKeyGenerator.generate_recommend_key(
            user_id, interests, budget
        )
        key = f"{self.prefix}:recommend:{key}"
        return self.redis.set(key, recommendations, ttl=self.TTL_CONFIG["recommendations"])
    
    def get_recommendations(
        self,
        user_id: str,
        interests: Optional[List[str]] = None,
        budget: Optional[str] = None
    ) -> Optional[Dict]:
        """
        获取缓存的推荐结果
        
        Args:
            user_id: 用户ID
            interests: 兴趣列表
            budget: 预算
            
        Returns:
            缓存的推荐结果
        """
        key = CacheKeyGenerator.generate_recommend_key(
            user_id, interests, budget
        )
        key = f"{self.prefix}:recommend:{key}"
        return self.redis.get(key)
    
    def cache_rag_context(
        self,
        query: str,
        context: str
    ) -> bool:
        """
        缓存RAG上下文
        
        Args:
            query: 查询文本
            context: RAG上下文
            
        Returns:
            是否缓存成功
        """
        key = CacheKeyGenerator.generate_rag_context_key(query)
        key = f"{self.prefix}:rag_context:{key}"
        return self.redis.set(key, context, ttl=self.TTL_CONFIG["rag_context"])
    
    def get_rag_context(self, query: str) -> Optional[str]:
        """
        获取缓存的RAG上下文
        
        Args:
            query: 查询文本
            
        Returns:
            缓存的RAG上下文
        """
        key = CacheKeyGenerator.generate_rag_context_key(query)
        key = f"{self.prefix}:rag_context:{key}"
        return self.redis.get(key)
    
    def cache_user_preferences(
        self,
        user_id: str,
        preferences: Dict
    ) -> bool:
        """
        缓存用户偏好
        
        Args:
            user_id: 用户ID
            preferences: 用户偏好
            
        Returns:
            是否缓存成功
        """
        key = CacheKeyGenerator.generate_user_preferences_key(user_id)
        key = f"{self.prefix}:user_prefs:{key}"
        return self.redis.set(key, preferences, ttl=self.TTL_CONFIG["user_preferences"])
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """
        获取缓存的用户偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            缓存的用户偏好
        """
        key = CacheKeyGenerator.generate_user_preferences_key(user_id)
        key = f"{self.prefix}:user_prefs:{key}"
        return self.redis.get(key)
    
    def cache_destination_info(
        self,
        destination: str,
        info: Dict
    ) -> bool:
        """
        缓存目的地信息
        
        Args:
            destination: 目的地
            info: 目的地信息
            
        Returns:
            是否缓存成功
        """
        key = CacheKeyGenerator.generate_destination_key(destination)
        key = f"{self.prefix}:destination:{key}"
        return self.redis.set(key, info, ttl=self.TTL_CONFIG["destination"])
    
    def get_destination_info(self, destination: str) -> Optional[Dict]:
        """
        获取缓存的目的地信息
        
        Args:
            destination: 目的地
            
        Returns:
            缓存的目的地信息
        """
        key = CacheKeyGenerator.generate_destination_key(destination)
        key = f"{self.prefix}:destination:{key}"
        return self.redis.get(key)
    
    def invalidate_user_cache(self, user_id: str) -> int:
        """
        清空用户相关缓存
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除的缓存数量
        """
        pattern = f"{self.prefix}:*{user_id}*"
        return self.redis.delete_pattern(pattern)
    
    def invalidate_search_cache(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None
    ) -> int:
        """
        清空搜索相关缓存
        
        Args:
            origin: 出发地
            destination: 目的地
            
        Returns:
            删除的缓存数量
        """
        if origin or destination:
            pattern = f"{self.prefix}:search:*"
        else:
            pattern = f"{self.prefix}:search:*"
        return self.redis.delete_pattern(pattern)
    
    def invalidate_all(self, namespace: Optional[str] = None) -> int:
        """
        清空所有缓存
        
        Args:
            namespace: 命名空间
            
        Returns:
            删除的缓存数量
        """
        if namespace:
            pattern = f"{self.prefix}:{namespace}:*"
        else:
            pattern = f"{self.prefix}:*"
        return self.redis.delete_pattern(pattern)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        redis_stats = self.redis.get_stats()
        
        return {
            "redis": redis_stats,
            "ttl_config": self.TTL_CONFIG,
            "prefix": self.prefix
        }


class CacheManager:
    """缓存管理器（保留原有接口）"""
    
    # 缓存 TTL 配置（秒）
    TTL_SEARCH = 3600
    TTL_RECOMMEND = 21600
    TTL_DESTINATION = 86400
    TTL_BOOKING = 1800
    TTL_TASK_STATUS = 300
    TTL_DEFAULT = 3600
    
    def __init__(self, redis_cache: Optional[RedisCache] = None):
        """
        初始化缓存管理器
        
        Args:
            redis_cache: Redis缓存实例
        """
        self.redis = redis_cache or RedisCache()
        self.prefix = "travel_assistant"
    
    def _generate_key(self, namespace: str, *args, **kwargs) -> str:
        """生成缓存键"""
        return CacheKeyGenerator.generate_key(namespace, *args, **kwargs)
    
    def get_search_cache(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1,
        **kwargs
    ) -> Optional[dict]:
        """获取搜索结果缓存"""
        key = self._generate_key(
            "search",
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            **kwargs
        )
        key = f"{self.prefix}:{key}"
        return self.redis.get(key)
    
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
        """设置搜索结果缓存"""
        key = self._generate_key(
            "search",
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            **kwargs
        )
        key = f"{self.prefix}:{key}"
        return self.redis.set(key, data, ttl=self.TTL_SEARCH)
    
    def get_recommend_cache(
        self,
        destination: str,
        interests: Optional[list] = None,
        budget: Optional[str] = None,
        **kwargs
    ) -> Optional[dict]:
        """获取推荐结果缓存"""
        key = self._generate_key(
            "recommend",
            destination=destination,
            interests=interests,
            budget=budget,
            **kwargs
        )
        key = f"{self.prefix}:{key}"
        return self.redis.get(key)
    
    def set_recommend_cache(
        self,
        data: dict,
        destination: str,
        interests: Optional[list] = None,
        budget: Optional[str] = None,
        **kwargs
    ) -> bool:
        """设置推荐结果缓存"""
        key = self._generate_key(
            "recommend",
            destination=destination,
            interests=interests,
            budget=budget,
            **kwargs
        )
        key = f"{self.prefix}:{key}"
        return self.redis.set(key, data, ttl=self.TTL_RECOMMEND)
    
    def invalidate_all(self, namespace: Optional[str] = None) -> int:
        """使所有缓存失效"""
        if namespace:
            pattern = f"{self.prefix}:{namespace}:*"
        else:
            pattern = f"{self.prefix}:*"
        return self.redis.delete_pattern(pattern)
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        return self.redis.get_stats()
