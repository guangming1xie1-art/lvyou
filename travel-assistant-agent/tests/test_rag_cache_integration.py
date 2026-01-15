"""
RAG和缓存集成测试
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, MagicMock


class TestRAGIntegration:
    """RAG集成测试"""

    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_full_rag_pipeline(self, temp_dir):
        """测试完整RAG流程"""
        from src.rag.knowledge_base import KnowledgeBase
        from src.rag.retriever import HybridRetriever
        
        # 1. 初始化知识库
        kb = KnowledgeBase(store_path=temp_dir)
        
        # 2. 添加知识
        texts = [
            "Paris is the capital of France, known as the City of Light",
            "The Eiffel Tower is Paris's most famous landmark",
            "Paris has many world-class museums including the Louvre",
            "French cuisine is famous worldwide",
            "The best time to visit Paris is spring or fall"
        ]
        
        kb.add_knowledge(texts)
        
        # 3. 搜索验证
        results = kb.search("Paris landmarks museums", k=3)
        
        assert len(results) >= 1
        
        # 4. 获取上下文
        context = kb.get_relevant_context("What to visit in Paris?", k=3)
        
        assert "Paris" in context or "Eiffel" in context

    def test_hybrid_search(self, temp_dir):
        """测试混合搜索"""
        from src.rag.retriever import HybridRetriever
        from langchain.schema import Document
        
        retriever = HybridRetriever()
        
        # 添加文档
        docs = [
            Document(page_content="Direct flights from Beijing to Paris", metadata={"type": "flight"}),
            Document(page_content="Paris hotel near Eiffel Tower", metadata={"type": "hotel"}),
            Document(page_content="Best attractions in Paris", metadata={"type": "attraction"}),
            Document(page_content="Tokyo has direct flights from Beijing", metadata={"type": "flight"}),
        ]
        
        retriever.add_documents(docs)
        
        # 搜索
        results = retriever.retrieve("Paris flight hotel", k=3)
        
        assert len(results) >= 1

    def test_knowledge_base_with_metadata(self, temp_dir):
        """测试带元数据的知识库"""
        from src.rag.knowledge_base import TravelKnowledgeBase
        
        kb = TravelKnowledgeBase(store_path=temp_dir)
        
        # 添加各类知识
        kb.add_flight_knowledge(
            ["Business class available", "Economy class from $500"],
            destinations=["Paris"]
        )
        
        kb.add_hotel_knowledge(
            ["Luxury hotels downtown", "Budget options near airport"],
            destinations=["Paris"]
        )
        
        kb.add_attraction_knowledge(
            ["Eiffel Tower tours", "Louvre Museum tickets"],
            destinations=["Paris"]
        )
        
        # 按类别搜索
        flights = kb.search_flights("flights")
        hotels = kb.search_hotels("hotels")
        attractions = kb.search_attractions("attractions")
        
        assert len(flights) >= 1
        assert len(hotels) >= 1
        assert len(attractions) >= 1


class TestCacheIntegration:
    """缓存集成测试"""

    @pytest.fixture
    def mock_redis(self):
        """模拟Redis"""
        with patch('src.cache.cache_strategy.RedisCache') as mock_class:
            mock_redis = MagicMock()
            mock_redis.is_available.return_value = True
            mock_redis.get.return_value = None
            mock_redis.set.return_value = True
            mock_class.return_value = mock_redis
            yield mock_redis

    def test_cache_strategy_search_results(self, mock_redis):
        """测试缓存策略搜索结果"""
        from src.cache.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(redis_cache=mock_redis)
        
        # 缓存搜索结果
        results = {"flights": [{"id": 1, "price": 500}]}
        strategy.cache_search_results("Paris", results, destination="Paris")
        
        # 验证Redis.set被调用
        mock_redis.set.assert_called()
        
        # 获取搜索结果
        mock_redis.get.return_value = results
        cached = strategy.get_search_results("Paris", destination="Paris")
        
        assert cached == results

    def test_cache_strategy_recommendations(self, mock_redis):
        """测试缓存策略推荐结果"""
        from src.cache.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(redis_cache=mock_redis)
        
        recommendations = {"hotels": [], "attractions": []}
        strategy.cache_recommendations(
            "user123",
            recommendations,
            interests=["culture", "food"],
            budget="medium"
        )
        
        mock_redis.set.assert_called()

    def test_cache_strategy_rag_context(self, mock_redis):
        """测试缓存策略RAG上下文"""
        from src.cache.cache_strategy import CacheStrategy
        
        strategy = CacheStrategy(redis_cache=mock_redis)
        
        context = "Paris has many museums and historical sites"
        strategy.cache_rag_context("Paris museums", context)
        
        mock_redis.set.assert_called()


class TestPromptCacheIntegration:
    """Prompt缓存集成测试"""

    def test_build_anthropic_messages(self):
        """测试构建Anthropic消息"""
        from src.cache.prompt_cache import PromptCacheManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = PromptCacheManager(enable_cache=True, cache_dir=tmpdir)
            
            messages = [
                {"role": "user", "content": "What to do in Paris?"}
            ]
            
            result = cache.build_anthropic_messages(
                system_prompt="You are a travel assistant",
                messages=messages,
                use_cache=True
            )
            
            assert result["model"] == "claude-3-5-sonnet-20241022"
            assert "system" in result
            assert len(result["system"]) == 1
            assert "cache_control" in result["system"][0]


class TestSearchNodeIntegration:
    """搜索节点集成测试"""

    @pytest.mark.asyncio
    async def test_plan_search_with_rag(self):
        """测试带RAG的搜索规划"""
        from src.workflows.conversation.nodes.search import plan_search
        
        state = {
            "user_message": "我想去巴黎旅游",
            "user_requirements": {
                "destination": "Paris",
                "budget": "中等",
                "travelers": 2,
                "dates": "2024-05"
            }
        }
        
        # Mock依赖
        with patch('src.workflows.conversation.nodes.search.get_cache_strategy') as mock_cache:
            mock_strategy = MagicMock()
            mock_strategy.get_rag_context.return_value = None
            mock_cache.return_value = mock_strategy
            
            with patch('src.workflows.conversation.nodes.search.get_knowledge_base') as mock_kb:
                mock_knowledge_base = MagicMock()
                mock_knowledge_base.get_relevant_context.return_value = "Paris is a beautiful city"
                mock_kb.return_value = mock_knowledge_base
                
                with patch('src.workflows.conversation.nodes.search.LLMFactory') as mock_llm:
                    result = await plan_search(state)
                    
                    assert "search_query" in result
                    assert "destination" in result
                    assert result["stage"] == "search_planning"

    @pytest.mark.asyncio
    async def test_execute_search_with_cache(self):
        """测试带缓存的搜索执行"""
        from src.workflows.conversation.nodes.search import execute_search
        
        state = {
            "search_query": "Paris flights",
            "search_type": "flight",
            "destination": "Paris",
            "user_requirements": {"budget": "中等"}
        }
        
        with patch('src.workflows.conversation.nodes.search.get_cache_strategy') as mock_cache:
            mock_strategy = MagicMock()
            mock_strategy.get_search_results.return_value = None  # 缓存未命中
            mock_cache.return_value = mock_strategy
            
            result = await execute_search(state)
            
            assert "search_results" in result
            assert result["search_executed"] is True
            assert len(result["search_results"]) >= 1


class TestFullWorkflowIntegration:
    """完整工作流集成测试"""

    @pytest.mark.asyncio
    async def test_search_workflow_with_cache(self):
        """测试带缓存的搜索工作流"""
        from src.workflows.conversation.nodes.search import plan_search, execute_search
        
        initial_state = {
            "user_message": "帮我找东京的酒店",
            "user_requirements": {
                "destination": "Tokyo",
                "budget": "500-800",
                "travelers": 2
            }
        }
        
        # 1. 规划搜索
        with patch('src.workflows.conversation.nodes.search.get_cache_strategy') as mock_cache:
            mock_strategy = MagicMock()
            mock_strategy.get_rag_context.return_value = None
            mock_strategy.get_search_results.return_value = None
            mock_cache.return_value = mock_strategy
            
            with patch('src.workflows.conversation.nodes.search.get_knowledge_base') as mock_kb:
                mock_knowledge_base = MagicMock()
                mock_knowledge_base.get_relevant_context.return_value = "Tokyo has many hotels"
                mock_kb.return_value = mock_knowledge_base
                
                plan_state = await plan_search(initial_state)
                
                # 2. 执行搜索
                execute_state = await execute_search(plan_state)
                
                assert execute_state["search_executed"] is True
                assert any(r["type"] == "hotel" for r in execute_state["search_results"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
