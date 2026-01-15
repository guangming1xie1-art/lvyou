"""
缓存模块单元测试
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
import json


class TestCacheKeyGenerator:
    """缓存键生成器测试"""

    def test_generate_key_basic(self):
        """测试基本键生成"""
        from src.cache.cache_key import CacheKeyGenerator
        
        key = CacheKeyGenerator.generate_key("test", "arg1", "arg2", kw="value")
        
        assert len(key) == 32  # MD5哈希长度
        assert key.isalnum()

    def test_generate_key_consistency(self):
        """测试键生成一致性"""
        from src.cache.cache_key import CacheKeyGenerator
        
        key1 = CacheKeyGenerator.generate_key("search", query="Paris", type="hotel")
        key2 = CacheKeyGenerator.generate_key("search", query="Paris", type="hotel")
        
        assert key1 == key2

    def test_generate_search_key(self):
        """测试搜索键生成"""
        from src.cache.cache_key import CacheKeyGenerator
        
        key = CacheKeyGenerator.generate_search_key(
            query="Paris hotels",
            origin="Beijing",
            destination="Paris",
            date="2024-01-01"
        )
        
        assert len(key) == 32

    def test_generate_conversation_key(self):
        """测试对话键生成"""
        from src.cache.cache_key import CacheKeyGenerator
        
        key = CacheKeyGenerator.generate_conversation_key("conv123")
        
        assert len(key) == 32


class TestPromptCacheManager:
    """Prompt缓存管理器测试"""

    def test_init(self):
        """测试初始化"""
        from src.cache.prompt_cache import PromptCacheManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PromptCacheManager(enable_cache=True, cache_dir=tmpdir)
            
            assert cache.enable_cache is True
            assert cache.cache_dir == tmpdir

    def test_cache_system_prompt(self):
        """测试缓存系统提示"""
        from src.cache.prompt_cache import PromptCacheManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PromptCacheManager(enable_cache=True, cache_dir=tmpdir)
            
            result = cache.cache_system_prompt("You are a travel assistant")
            
            assert result["cached"] is True
            assert cache.get_system_prompt() == "You are a travel assistant"

    def test_cache_rag_context(self):
        """测试缓存RAG上下文"""
        from src.cache.prompt_cache import PromptCacheManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PromptCacheManager(enable_cache=True, cache_dir=tmpdir)
            
            context = "Paris has many museums"
            result = cache.cache_rag_context(context, "Paris museums")
            
            assert result["cached"] is True
            assert cache.get_rag_context("Paris museums") == context

    def test_cache_ttl(self):
        """测试缓存过期"""
        from src.cache.prompt_cache import PromptCacheManager
        from datetime import datetime, timedelta
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PromptCacheManager(enable_cache=True, cache_dir=tmpdir)
            
            # 添加一个短期缓存
            cache.cache_system_prompt("Test")
            
            # 模拟时间过期（修改文件）
            cache_path = os.path.join(tmpdir, "system_prompt_v1.cache")
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            data["expires_at"] = (datetime.now() - timedelta(hours=1)).isoformat()
            
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            
            # 获取应该返回None
            result = cache.get_system_prompt()
            assert result is None

    def test_build_cached_messages(self):
        """测试构建缓存消息"""
        from src.cache.prompt_cache import PromptCacheManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PromptCacheManager(enable_cache=True, cache_dir=tmpdir)
            
            messages = cache.build_cached_messages(
                system_prompt="You are a travel assistant",
                rag_context="Paris is beautiful",
                user_message="What to do in Paris?"
            )
            
            assert len(messages) == 3
            assert messages[0]["role"] == "user"
            assert "cache_control" in messages[0]["content"][0]

    def test_calculate_token_savings(self):
        """测试计算Token节省"""
        from src.cache.prompt_cache import PromptCacheManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PromptCacheManager(enable_cache=True, cache_dir=tmpdir)
            
            savings = cache.calculate_token_savings(
                cache_hits=10,
                cached_tokens=1000,
                input_cost_per_million=3.0  # Claude $3/1M
            )
            
            assert savings["cache_hits"] == 10
            assert savings["saved_tokens_total"] == 10000
            assert savings["savings_usd"] > 0

    def test_clear_cache(self):
        """测试清空缓存"""
        from src.cache.prompt_cache import PromptCacheManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PromptCacheManager(enable_cache=True, cache_dir=tmpdir)
            
            cache.cache_system_prompt("Test1")
            cache.cache_system_prompt("Test2")
            
            count = cache.clear()
            
            assert count >= 2
            assert cache.get_system_prompt() is None


class TestCacheStrategy:
    """缓存策略测试"""

    def test_init(self):
        """测试初始化"""
        from src.cache.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy()
        
        assert strategy.prefix == "travel_assistant"

    @patch('src.cache.cache_strategy.RedisCache')
    def test_get_or_compute(self, mock_redis_class):
        """测试Cache-Aside模式"""
        from src.cache.cache_strategy import CacheStrategy
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = None  # 模拟缓存未命中
        mock_redis_class.return_value = mock_redis
        
        strategy = CacheStrategy(redis_cache=mock_redis)
        
        compute_count = [0]
        
        def compute_fn():
            compute_count[0] += 1
            return "computed_value"
        
        result = strategy.get_or_compute("test_key", compute_fn)
        
        assert result == "computed_value"
        assert compute_count[0] == 1
        mock_redis.set.assert_called_once()

    @patch('src.cache.cache_strategy.RedisCache')
    def test_get_or_compute_cache_hit(self, mock_redis_class):
        """测试缓存命中"""
        from src.cache.cache_strategy import CacheStrategy
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = "cached_value"
        mock_redis_class.return_value = mock_redis
        
        strategy = CacheStrategy(redis_cache=mock_redis)
        
        compute_count = [0]
        
        def compute_fn():
            compute_count[0] += 1
            return "computed_value"
        
        result = strategy.get_or_compute("test_key", compute_fn)
        
        assert result == "cached_value"
        assert compute_count[0] == 0  # 不应该调用compute_fn

    @patch('src.cache.cache_strategy.RedisCache')
    def test_cache_search_results(self, mock_redis_class):
        """测试缓存搜索结果"""
        from src.cache.cache_strategy import CacheStrategy
        
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        
        strategy = CacheStrategy(redis_cache=mock_redis)
        
        results = {"flights": [], "hotels": []}
        success = strategy.cache_search_results(
            "Paris hotels",
            results,
            destination="Paris"
        )
        
        assert success is True
        mock_redis.set.assert_called_once()

    @patch('src.cache.cache_strategy.RedisCache')
    def test_get_search_results(self, mock_redis_class):
        """测试获取搜索结果"""
        from src.cache.cache_strategy import CacheStrategy
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = {"flights": [], "hotels": []}
        mock_redis_class.return_value = mock_redis
        
        strategy = CacheStrategy(redis_cache=mock_redis)
        
        results = strategy.get_search_results("Paris hotels", destination="Paris")
        
        assert results is not None
        assert "flights" in results


class TestCacheManager:
    """缓存管理器测试"""

    @patch('src.cache.cache_manager.RedisCache')
    def test_init(self, mock_redis_class):
        """测试初始化"""
        from src.cache.cache_manager import CacheManager
        
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        
        manager = CacheManager(redis_cache=mock_redis)
        
        assert manager.prefix == "travel_assistant"

    @patch('src.cache.cache_manager.RedisCache')
    def test_search_cache(self, mock_redis_class):
        """测试搜索缓存"""
        from src.cache.cache_manager import CacheManager
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = {"results": "test"}
        mock_redis_class.return_value = mock_redis
        
        manager = CacheManager(redis_cache=mock_redis)
        
        result = manager.get_search_cache(
            origin="Beijing",
            destination="Paris",
            departure_date="2024-01-01"
        )
        
        assert result == {"results": "test"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
