"""
RAG模块单元测试
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock


class TestEmbeddingFactory:
    """Embedding工厂测试"""

    def test_get_embeddings_singleton(self):
        """测试Embedding单例模式"""
        from src.rag.embeddings import EmbeddingFactory
        
        # 模拟环境变量
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("src.rag.embeddings.OpenAIEmbeddings") as mock_embeddings:
                mock_instance = MagicMock()
                mock_embeddings.return_value = mock_instance
                
                # 重置单例
                EmbeddingFactory.reset_instance()
                
                # 获取实例两次，应该返回同一个实例
                emb1 = EmbeddingFactory.get_embeddings()
                emb2 = EmbeddingFactory.get_embeddings()
                
                assert emb1 is emb2
                mock_embeddings.assert_called_once()

    def test_embed_text(self):
        """测试文本嵌入"""
        from src.rag.embeddings import EmbeddingFactory
        
        EmbeddingFactory.reset_instance()
        
        mock_embeddings = MagicMock()
        mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        
        with patch("src.rag.embeddings.OpenAIEmbeddings", return_value=mock_embeddings):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                EmbeddingFactory._instance = None
                result = EmbeddingFactory.embed_text("test text")
                
                assert result == [0.1, 0.2, 0.3]
                mock_embeddings.embed_query.assert_called_once_with("test text")

    def test_embed_texts(self):
        """测试批量文本嵌入"""
        from src.rag.embeddings import EmbeddingFactory
        
        EmbeddingFactory.reset_instance()
        
        mock_embeddings = MagicMock()
        mock_embeddings.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        with patch("src.rag.embeddings.OpenAIEmbeddings", return_value=mock_embeddings):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                EmbeddingFactory._instance = None
                result = EmbeddingFactory.embed_texts(["text1", "text2"])
                
                assert result == [[0.1, 0.2], [0.3, 0.4]]
                mock_embeddings.embed_documents.assert_called_once_with(["text1", "text2"])


class TestVectorStoreManager:
    """向量存储管理器测试"""

    def test_init_creates_vectorstore(self):
        """测试初始化创建向量存储"""
        from src.rag.vectorstore import VectorStoreManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = VectorStoreManager(store_path=tmpdir, recreate=True)
            
            assert manager.vectorstore is not None
            assert os.path.exists(tmpdir)

    def test_add_documents(self):
        """测试添加文档"""
        from src.rag.vectorstore import VectorStoreManager
        from langchain.schema import Document
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = VectorStoreManager(store_path=tmpdir, recreate=True)
            
            docs = [
                Document(page_content="test doc 1", metadata={"id": "1"}),
                Document(page_content="test doc 2", metadata={"id": "2"})
            ]
            
            ids = manager.add_documents(docs)
            
            assert len(ids) == 2
            assert manager.get_document_count() == 2

    def test_search(self):
        """测试向量搜索"""
        from src.rag.vectorstore import VectorStoreManager
        from langchain.schema import Document
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = VectorStoreManager(store_path=tmpdir, recreate=True)
            
            # 添加测试文档
            docs = [
                Document(page_content="Paris is a beautiful city", metadata={"city": "paris"}),
                Document(page_content="Tokyo has amazing food", metadata={"city": "tokyo"}),
            ]
            manager.add_documents(docs)
            
            # 搜索
            results = manager.search("city travel", k=2)
            
            assert len(results) >= 1

    def test_search_with_filter(self):
        """测试带过滤条件的搜索"""
        from src.rag.vectorstore import VectorStoreManager
        from langchain.schema import Document
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = VectorStoreManager(store_path=tmpdir, recreate=True)
            
            docs = [
                Document(page_content="Paris hotels", metadata={"city": "paris", "type": "hotel"}),
                Document(page_content="Paris attractions", metadata={"city": "paris", "type": "attraction"}),
            ]
            manager.add_documents(docs)
            
            # 过滤搜索
            results = manager.search("Paris", k=5, filter={"type": "hotel"})
            
            assert len(results) >= 1


class TestHybridRetriever:
    """混合检索器测试"""

    def test_init(self):
        """测试初始化"""
        from src.rag.retriever import HybridRetriever
        
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = HybridRetriever(vectorstore=None)
            
            assert retriever.vectorstore is not None

    def test_add_documents(self):
        """测试添加文档"""
        from src.rag.retriever import HybridRetriever
        from langchain.schema import Document
        
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = HybridRetriever()
            
            docs = [
                Document(page_content="Flight to Paris costs $500", metadata={"type": "flight"}),
                Document(page_content="Hotel in Paris is expensive", metadata={"type": "hotel"})
            ]
            
            retriever.add_documents(docs)
            
            stats = retriever.get_stats()
            assert stats["bm25_corpus_size"] == 2

    def test_retrieve(self):
        """测试混合检索"""
        from src.rag.retriever import HybridRetriever
        from langchain.schema import Document
        
        with tempfile.TemporaryDirectory() as tmpdir:
            retriever = HybridRetriever()
            
            docs = [
                Document(page_content="Best flights to Paris", metadata={"type": "flight"}),
                Document(page_content="Paris hotel recommendations", metadata={"type": "hotel"}),
                Document(page_content="Tokyo travel guide", metadata={"type": "guide"}),
            ]
            
            retriever.add_documents(docs)
            
            # 检索
            results = retriever.retrieve("Paris flight hotel", k=2)
            
            assert len(results) >= 1


class TestKnowledgeBase:
    """知识库测试"""

    def test_add_knowledge(self):
        """测试添加知识"""
        from src.rag.knowledge_base import KnowledgeBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            kb = KnowledgeBase(store_path=tmpdir)
            
            texts = [
                "Paris is the capital of France",
                "The Eiffel Tower is in Paris"
            ]
            
            kb.add_knowledge(texts)
            
            assert kb.get_document_count() == 2

    def test_search(self):
        """测试知识搜索"""
        from src.rag.knowledge_base import KnowledgeBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            kb = KnowledgeBase(store_path=tmpdir)
            
            texts = [
                "Paris has many museums",
                "The Louvre is famous",
                "Tokyo has cherry blossoms"
            ]
            
            kb.add_knowledge(texts)
            
            results = kb.search("Paris museums", k=2)
            
            assert len(results) >= 1

    def test_get_relevant_context(self):
        """测试获取相关上下文"""
        from src.rag.knowledge_base import KnowledgeBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            kb = KnowledgeBase(store_path=tmpdir)
            
            texts = [
                "Paris museums are world-famous",
                "The Louvre contains the Mona Lisa",
                "Tokyo has ancient temples"
            ]
            
            kb.add_knowledge(texts)
            
            context = kb.get_relevant_context("Paris culture", k=2)
            
            assert "Paris" in context or "Louvre" in context


class TestTravelKnowledgeBase:
    """旅游知识库测试"""

    def test_add_category_knowledge(self):
        """测试按类别添加知识"""
        from src.rag.knowledge_base import TravelKnowledgeBase
        
        with tempfile.TemporaryDirectory() as tmpdir:
            kb = TravelKnowledgeBase(store_path=tmpdir)
            
            # 添加航班知识
            kb.add_flight_knowledge(
                ["Direct flights available", "Economy class prices"],
                destinations=["Paris", "Tokyo"]
            )
            
            # 添加酒店知识
            kb.add_hotel_knowledge(
                ["5-star hotels downtown", "Budget options available"],
                destinations=["Paris"]
            )
            
            # 按类别搜索
            flight_results = kb.search_flights("flights")
            hotel_results = kb.search_hotels("hotels")
            
            assert len(flight_results) >= 1
            assert len(hotel_results) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
