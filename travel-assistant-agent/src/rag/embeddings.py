"""
Embeddings工厂模块
提供Embedding模型的统一管理和工厂模式
"""
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class EmbeddingFactory:
    """Embedding模型工厂"""
    
    _instance: Optional[Embeddings] = None
    
    @classmethod
    def get_embeddings(
        cls,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> Embeddings:
        """
        获取Embedding模型单例
        
        Args:
            model: Embedding模型名称，默认从环境变量读取
            api_key: API密钥，默认从环境变量读取
            base_url: API基础URL（用于自定义API服务端点）
            
        Returns:
            Embedding模型实例
        """
        if cls._instance is None:
            embedding_model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            openai_api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("EMBEDDING_API_KEY")
            openai_base_url = base_url or os.getenv("EMBEDDING_BASE_URL")
            
            # 构建初始化参数
            init_kwargs = {
                "model": embedding_model,
                "api_key": openai_api_key,
            }
            
            if openai_base_url:
                init_kwargs["base_url"] = openai_base_url
            
            try:
                cls._instance = OpenAIEmbeddings(**init_kwargs)
                logger.info(f"Initialized Embedding model: {embedding_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Embedding model: {e}")
                raise
        
        return cls._instance
    
    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        """
        嵌入单个文本
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示
        """
        embeddings = cls.get_embeddings()
        try:
            return embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            raise
    
    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        """
        嵌入多个文本
        
        Args:
            texts: 输入文本列表
            
        Returns:
            文本列表的向量表示
        """
        embeddings = cls.get_embeddings()
        try:
            return embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            raise
    
    @classmethod
    def reset_instance(cls):
        """重置单例（主要用于测试）"""
        cls._instance = None
        logger.info("EmbeddingFactory instance reset")
    
    @classmethod
    def get_embedding_dimension(cls) -> int:
        """
        获取当前Embedding模型的维度
        
        Returns:
            向量维度
        """
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        
        # 常见模型的维度映射
        dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            "text-embedding-ada-001": 1024,
        }
        
        return dimension_map.get(model, 1536)
