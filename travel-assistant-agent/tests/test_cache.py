"""
缓存功能测试
"""
import pytest
import time
from src.cache import RedisCache, CacheManager


@pytest.fixture
def redis_cache():
    """创建 Redis 缓存实例"""
    cache = RedisCache(
        host='localhost',
        port=6379,
        db=15,  # 使用测试数据库
    )
    yield cache
    # 测试后清理
    cache.flush_db()
    cache.close()


@pytest.fixture
def cache_manager(redis_cache):
    """创建缓存管理器实例"""
    return CacheManager(redis_cache)


class TestRedisCache:
    """Redis 缓存基础功能测试"""

    def test_connection(self, redis_cache):
        """测试 Redis 连接"""
        assert redis_cache.is_available()

    def test_set_and_get(self, redis_cache):
        """测试基本的设置和获取"""
        key = "test_key"
        value = {"message": "Hello, World!"}
        
        # 设置值
        result = redis_cache.set(key, value)
        assert result is True
        
        # 获取值
        retrieved = redis_cache.get(key)
        assert retrieved == value

    def test_get_nonexistent_key(self, redis_cache):
        """测试获取不存在的键"""
        result = redis_cache.get("nonexistent_key")
        assert result is None

    def test_delete(self, redis_cache):
        """测试删除键"""
        key = "test_delete"
        value = {"data": "test"}
        
        # 设置并验证
        redis_cache.set(key, value)
        assert redis_cache.exists(key)
        
        # 删除并验证
        result = redis_cache.delete(key)
        assert result is True
        assert not redis_cache.exists(key)

    def test_ttl(self, redis_cache):
        """测试 TTL 过期"""
        key = "test_ttl"
        value = {"data": "expires soon"}
        ttl = 2  # 2 秒
        
        # 设置带 TTL 的值
        redis_cache.set(key, value, ttl=ttl)
        
        # 立即检查应该存在
        assert redis_cache.exists(key)
        
        # 等待过期
        time.sleep(ttl + 0.5)
        
        # 应该已过期
        assert not redis_cache.exists(key)
        assert redis_cache.get(key) is None

    def test_get_ttl(self, redis_cache):
        """测试获取剩余 TTL"""
        key = "test_get_ttl"
        value = {"data": "test"}
        ttl = 60
        
        redis_cache.set(key, value, ttl=ttl)
        
        remaining_ttl = redis_cache.ttl(key)
        assert remaining_ttl is not None
        assert 50 < remaining_ttl <= 60

    def test_incr(self, redis_cache):
        """测试计数器递增"""
        key = "test_counter"
        
        # 递增不存在的键（从 0 开始）
        result = redis_cache.incr(key, 1)
        assert result == 1
        
        # 再次递增
        result = redis_cache.incr(key, 5)
        assert result == 6

    def test_delete_pattern(self, redis_cache):
        """测试按模式删除"""
        # 设置多个键
        redis_cache.set("search:1", {"data": "1"})
        redis_cache.set("search:2", {"data": "2"})
        redis_cache.set("recommend:1", {"data": "3"})
        
        # 删除所有 search 相关的键
        count = redis_cache.delete_pattern("search:*")
        assert count == 2
        
        # 验证删除结果
        assert not redis_cache.exists("search:1")
        assert not redis_cache.exists("search:2")
        assert redis_cache.exists("recommend:1")

    def test_get_stats(self, redis_cache):
        """测试获取统计信息"""
        stats = redis_cache.get_stats()
        
        assert stats["available"] is True
        assert "used_memory_human" in stats
        assert "hit_rate" in stats


class TestCacheManager:
    """缓存管理器测试"""

    def test_search_cache(self, cache_manager):
        """测试搜索缓存"""
        # 准备数据
        search_data = {
            "outbound_flights": [{"id": "1", "price": 500}],
            "return_flights": [{"id": "2", "price": 450}],
            "hotels": [{"id": "h1", "price": 100}]
        }
        
        # 设置缓存
        result = cache_manager.set_search_cache(
            data=search_data,
            origin="Beijing",
            destination="Tokyo",
            departure_date="2025-02-01",
            return_date="2025-02-10",
            passengers=2
        )
        assert result is True
        
        # 获取缓存
        cached = cache_manager.get_search_cache(
            origin="Beijing",
            destination="Tokyo",
            departure_date="2025-02-01",
            return_date="2025-02-10",
            passengers=2
        )
        
        assert cached is not None
        assert cached["outbound_flights"] == search_data["outbound_flights"]
        assert cached["hotels"] == search_data["hotels"]

    def test_recommend_cache(self, cache_manager):
        """测试推荐缓存"""
        # 准备数据
        recommend_data = {
            "destination_info": {"name": "Tokyo"},
            "attractions": [{"name": "Tokyo Tower"}],
            "weather_forecast": [{"date": "2025-02-01", "temp": 15}]
        }
        
        # 设置缓存
        result = cache_manager.set_recommend_cache(
            data=recommend_data,
            destination="Tokyo",
            interests=["culture", "food"],
            budget="medium"
        )
        assert result is True
        
        # 获取缓存
        cached = cache_manager.get_recommend_cache(
            destination="Tokyo",
            interests=["culture", "food"],
            budget="medium"
        )
        
        assert cached is not None
        assert cached["destination_info"] == recommend_data["destination_info"]

    def test_destination_cache(self, cache_manager):
        """测试目的地信息缓存"""
        # 准备数据
        dest_data = {
            "name": "Tokyo",
            "country": "Japan",
            "description": "Capital of Japan"
        }
        
        # 设置缓存
        result = cache_manager.set_destination_cache("Tokyo", dest_data)
        assert result is True
        
        # 获取缓存
        cached = cache_manager.get_destination_cache("Tokyo")
        
        assert cached is not None
        assert cached["name"] == "Tokyo"
        assert cached["country"] == "Japan"

    def test_task_status_cache(self, cache_manager):
        """测试任务状态缓存"""
        task_id = "task-123"
        status_data = {
            "status": "processing",
            "progress": 0.5,
            "message": "Searching flights..."
        }
        
        # 设置缓存
        result = cache_manager.set_task_status(task_id, status_data)
        assert result is True
        
        # 获取缓存
        cached = cache_manager.get_task_status(task_id)
        
        assert cached is not None
        assert cached["status"] == "processing"
        assert cached["progress"] == 0.5

    def test_cache_key_consistency(self, cache_manager):
        """测试缓存键生成的一致性"""
        # 相同参数应该生成相同的键
        key1 = cache_manager._generate_key(
            "search",
            origin="Beijing",
            destination="Tokyo",
            date="2025-02-01"
        )
        
        key2 = cache_manager._generate_key(
            "search",
            destination="Tokyo",
            origin="Beijing",
            date="2025-02-01"
        )
        
        # 参数顺序不同，但生成的键应该相同（因为内部排序）
        assert key1 == key2

    def test_cache_invalidation(self, cache_manager):
        """测试缓存失效"""
        # 设置多个缓存
        cache_manager.set_search_cache(
            data={"test": "1"},
            origin="Beijing",
            destination="Tokyo",
            departure_date="2025-02-01"
        )
        
        cache_manager.set_search_cache(
            data={"test": "2"},
            origin="Shanghai",
            destination="Osaka",
            departure_date="2025-02-05"
        )
        
        # 使所有搜索缓存失效
        cache_manager.invalidate_all(namespace="search")
        
        # 验证缓存已清除
        cached1 = cache_manager.get_search_cache(
            origin="Beijing",
            destination="Tokyo",
            departure_date="2025-02-01"
        )
        assert cached1 is None

    def test_cache_stats(self, cache_manager):
        """测试缓存统计"""
        stats = cache_manager.get_stats()
        
        assert "available" in stats
        if stats["available"]:
            assert "hit_rate" in stats
            assert "keyspace_hits" in stats
            assert "keyspace_misses" in stats


class TestCachePerformance:
    """缓存性能测试"""

    def test_bulk_operations(self, cache_manager):
        """测试批量操作性能"""
        import time
        
        # 写入 100 个缓存项
        start_time = time.time()
        for i in range(100):
            cache_manager.set_search_cache(
                data={"test": i},
                origin=f"Origin{i}",
                destination=f"Dest{i}",
                departure_date="2025-02-01"
            )
        write_time = time.time() - start_time
        
        print(f"\n写入 100 项耗时: {write_time:.3f}s")
        assert write_time < 5.0  # 应该在 5 秒内完成
        
        # 读取 100 个缓存项
        start_time = time.time()
        for i in range(100):
            cache_manager.get_search_cache(
                origin=f"Origin{i}",
                destination=f"Dest{i}",
                departure_date="2025-02-01"
            )
        read_time = time.time() - start_time
        
        print(f"读取 100 项耗时: {read_time:.3f}s")
        assert read_time < 2.0  # 应该在 2 秒内完成

    def test_large_value(self, redis_cache):
        """测试大值存储"""
        import time
        
        # 创建一个大的数据结构（约 1MB）
        large_data = {
            "flights": [
                {"id": f"flight_{i}", "data": "x" * 1000}
                for i in range(1000)
            ]
        }
        
        # 测试写入
        start_time = time.time()
        result = redis_cache.set("large_key", large_data, ttl=300)
        write_time = time.time() - start_time
        
        assert result is True
        print(f"\n写入大值（~1MB）耗时: {write_time:.3f}s")
        assert write_time < 1.0
        
        # 测试读取
        start_time = time.time()
        retrieved = redis_cache.get("large_key")
        read_time = time.time() - start_time
        
        assert retrieved is not None
        assert len(retrieved["flights"]) == 1000
        print(f"读取大值（~1MB）耗时: {read_time:.3f}s")
        assert read_time < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
