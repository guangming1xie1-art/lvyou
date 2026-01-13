"""
Redis 缓存实现
提供基础的 Redis 操作和连接管理
"""
import json
import logging
from typing import Any, Optional
import redis
from redis.connection import ConnectionPool

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis 缓存客户端"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 50,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        decode_responses: bool = True,
    ):
        """
        初始化 Redis 连接

        Args:
            host: Redis 主机地址
            port: Redis 端口
            db: 数据库编号
            password: Redis 密码
            max_connections: 最大连接数
            socket_timeout: 套接字超时（秒）
            socket_connect_timeout: 连接超时（秒）
            decode_responses: 是否解码响应为字符串
        """
        try:
            self.pool = ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                max_connections=max_connections,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
                decode_responses=decode_responses,
            )
            self.client = redis.Redis(connection_pool=self.pool)
            # 测试连接
            self.client.ping()
            logger.info(f"Redis 连接成功: {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Redis 连接失败: {e}")
            # 使用模拟客户端以便在没有 Redis 时仍可运行
            self.client = None
        except Exception as e:
            logger.error(f"Redis 初始化错误: {e}")
            self.client = None

    def is_available(self) -> bool:
        """检查 Redis 是否可用"""
        if self.client is None:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在返回 None
        """
        if not self.is_available():
            return None

        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"缓存命中: {key}")
                return json.loads(value)
            logger.debug(f"缓存未命中: {key}")
            return None
        except json.JSONDecodeError:
            logger.error(f"JSON 解码失败: {key}")
            return None
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示永不过期

        Returns:
            是否设置成功
        """
        if not self.is_available():
            return False

        try:
            serialized = json.dumps(value, ensure_ascii=False)
            if ttl:
                result = self.client.setex(key, ttl, serialized)
            else:
                result = self.client.set(key, serialized)
            
            if result:
                logger.debug(f"缓存设置成功: {key} (TTL: {ttl}s)")
            return bool(result)
        except (TypeError, ValueError) as e:
            logger.error(f"值序列化失败 {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        if not self.is_available():
            return False

        try:
            result = self.client.delete(key)
            if result:
                logger.debug(f"缓存删除成功: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        按模式删除缓存

        Args:
            pattern: 模式（例如 "search:*"）

        Returns:
            删除的键数量
        """
        if not self.is_available():
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                logger.info(f"删除 {count} 个缓存键（模式: {pattern}）")
                return count
            return 0
        except Exception as e:
            logger.error(f"按模式删除缓存失败 {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        检查键是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        if not self.is_available():
            return False

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"检查缓存存在失败 {key}: {e}")
            return False

    def ttl(self, key: str) -> Optional[int]:
        """
        获取键的剩余生存时间

        Args:
            key: 缓存键

        Returns:
            剩余秒数，-1 表示永不过期，-2 表示不存在，None 表示错误
        """
        if not self.is_available():
            return None

        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"获取 TTL 失败 {key}: {e}")
            return None

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 缓存键
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        if not self.is_available():
            return False

        try:
            result = self.client.expire(key, ttl)
            if result:
                logger.debug(f"设置过期时间成功: {key} (TTL: {ttl}s)")
            return bool(result)
        except Exception as e:
            logger.error(f"设置过期时间失败 {key}: {e}")
            return False

    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递增计数器

        Args:
            key: 缓存键
            amount: 递增量

        Returns:
            递增后的值，失败返回 None
        """
        if not self.is_available():
            return None

        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"递增失败 {key}: {e}")
            return None

    def get_stats(self) -> dict:
        """
        获取 Redis 统计信息

        Returns:
            统计信息字典
        """
        if not self.is_available():
            return {"available": False}

        try:
            info = self.client.info()
            return {
                "available": True,
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"available": False, "error": str(e)}

    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """计算缓存命中率"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

    def flush_db(self) -> bool:
        """
        清空当前数据库的所有缓存
        警告: 此操作会删除所有数据！

        Returns:
            是否成功
        """
        if not self.is_available():
            return False

        try:
            self.client.flushdb()
            logger.warning("已清空 Redis 数据库")
            return True
        except Exception as e:
            logger.error(f"清空数据库失败: {e}")
            return False

    def close(self):
        """关闭连接池"""
        if self.pool:
            self.pool.disconnect()
            logger.info("Redis 连接池已关闭")
