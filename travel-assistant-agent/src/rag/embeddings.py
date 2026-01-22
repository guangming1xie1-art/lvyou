"""
Embedding适配器工厂模块
使用适配器模式为多个厂商的嵌入模型提供统一接口
支持：OpenAI、Qwen (DashScope)、GLM (智谱)、Kimi (Moonshot)、HuggingFace
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class EmbeddingAdapter(ABC):
    """
    嵌入模型适配器抽象基类
    为所有厂商的嵌入模型提供统一接口
    """
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        嵌入单个查询文本
        
        Args:
            text: 输入文本
            
        Returns:
            文本的向量表示 (List[float])
        """
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        嵌入多个文档文本
        
        Args:
            texts: 输入文本列表
            
        Returns:
            文本列表的向量表示 (List[List[float]])
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        获取当前Embedding模型的维度
        
        Returns:
            向量维度 (int)
        """
        pass


class OpenAIEmbeddingAdapter(EmbeddingAdapter):
    """OpenAI嵌入模型适配器"""
    
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None, **kwargs):
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError(
                "OpenAIEmbeddingAdapter requires langchain-openai. "
                "Install it with: pip install langchain-openai"
            )
        
        init_kwargs = {
            "model": model,
            "api_key": api_key,
        }
        if base_url:
            init_kwargs["base_url"] = base_url
        
        # 添加额外的配置参数
        init_kwargs.update(kwargs)
        
        self._client = OpenAIEmbeddings(**init_kwargs)
        self._model = model
        logger.info(f"Initialized OpenAIEmbeddingAdapter with model: {model}")
    
    def embed_query(self, text: str) -> List[float]:
        try:
            return self._client.embed_query(text)
        except Exception as e:
            logger.error(f"OpenAI embed_query failed: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return self._client.embed_documents(texts)
        except Exception as e:
            logger.error(f"OpenAI embed_documents failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        return dimension_map.get(self._model, 1536)


class QwenEmbeddingAdapter(EmbeddingAdapter):
    """Qwen (DashScope) 嵌入模型适配器"""
    
    def __init__(self, model: str, api_key: str, **kwargs):
        try:
            from langchain_community.embeddings import DashScopeEmbeddings
        except ImportError:
            raise ImportError(
                "QwenEmbeddingAdapter requires dashscope and langchain-community. "
                "Install them with: pip install dashscope langchain-community"
            )
        
        init_kwargs = {
            "model": model,
            "dashscope_api_key": api_key,
        }
        
        # 添加额外的配置参数
        init_kwargs.update(kwargs)
        
        self._client = DashScopeEmbeddings(**init_kwargs)
        self._model = model
        logger.info(f"Initialized QwenEmbeddingAdapter with model: {model}")
    
    def embed_query(self, text: str) -> List[float]:
        try:
            return self._client.embed_query(text)
        except Exception as e:
            logger.error(f"Qwen embed_query failed: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return self._client.embed_documents(texts)
        except Exception as e:
            logger.error(f"Qwen embed_documents failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        # Qwen 模型维度
        dimension_map = {
            "text-embedding-v1": 1536,
            "text-embedding-v2": 1536,
        }
        return dimension_map.get(self._model, 1536)


class GLMEmbeddingAdapter(EmbeddingAdapter):
    """GLM (智谱AI) 嵌入模型适配器"""
    
    def __init__(self, model: str, api_key: str, **kwargs):
        try:
            from langchain_community.embeddings import ZhipuAIEmbeddings
        except ImportError:
            raise ImportError(
                "GLMEmbeddingAdapter requires zhipuai and langchain-community. "
                "Install them with: pip install zhipuai langchain-community"
            )
        
        init_kwargs = {
            "model": model,
            "api_key": api_key,
        }
        
        # 添加额外的配置参数
        init_kwargs.update(kwargs)
        
        self._client = ZhipuAIEmbeddings(**init_kwargs)
        self._model = model
        logger.info(f"Initialized GLMEmbeddingAdapter with model: {model}")
    
    def embed_query(self, text: str) -> List[float]:
        try:
            return self._client.embed_query(text)
        except Exception as e:
            logger.error(f"GLM embed_query failed: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return self._client.embed_documents(texts)
        except Exception as e:
            logger.error(f"GLM embed_documents failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        # GLM 模型维度
        dimension_map = {
            "embedding-2": 1024,
            "embedding-3": 2048,
        }
        return dimension_map.get(self._model, 1024)


class KimiEmbeddingAdapter(EmbeddingAdapter):
    """Kimi (Moonshot) 嵌入模型适配器"""
    
    def __init__(self, model: str, api_key: str, base_url: Optional[str] = None, **kwargs):
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError(
                "KimiEmbeddingAdapter requires langchain-openai. "
                "Install it with: pip install langchain-openai"
            )
        
        # Kimi 使用兼容 OpenAI 的接口
        init_kwargs = {
            "model": model,
            "api_key": api_key,
            "base_url": base_url or "https://api.moonshot.cn/v1",
        }
        
        # 添加额外的配置参数
        init_kwargs.update(kwargs)
        
        self._client = OpenAIEmbeddings(**init_kwargs)
        self._model = model
        logger.info(f"Initialized KimiEmbeddingAdapter with model: {model}")
    
    def embed_query(self, text: str) -> List[float]:
        try:
            return self._client.embed_query(text)
        except Exception as e:
            logger.error(f"Kimi embed_query failed: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return self._client.embed_documents(texts)
        except Exception as e:
            logger.error(f"Kimi embed_documents failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        # Kimi 模型维度
        dimension_map = {
            "moonshot-v1": 2048,
        }
        return dimension_map.get(self._model, 2048)


class HuggingFaceEmbeddingAdapter(EmbeddingAdapter):
    """HuggingFace 嵌入模型适配器"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            raise ImportError(
                "HuggingFaceEmbeddingAdapter requires langchain-huggingface and sentence-transformers. "
                "Install them with: pip install langchain-huggingface sentence-transformers"
            )
        
        init_kwargs = {
            "model_name": model,
        }
        
        if api_key:
            init_kwargs["token"] = api_key
        
        # 添加额外的配置参数
        init_kwargs.update(kwargs)
        
        self._client = HuggingFaceEmbeddings(**init_kwargs)
        self._model = model
        logger.info(f"Initialized HuggingFaceEmbeddingAdapter with model: {model}")
    
    def embed_query(self, text: str) -> List[float]:
        try:
            return self._client.embed_query(text)
        except Exception as e:
            logger.error(f"HuggingFace embed_query failed: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            return self._client.embed_documents(texts)
        except Exception as e:
            logger.error(f"HuggingFace embed_documents failed: {e}")
            raise
    
    def get_dimension(self) -> int:
        try:
            # 尝试获取模型维度
            sample_embedding = self._client.embed_query("test")
            return len(sample_embedding)
        except Exception as e:
            logger.warning(f"Failed to get dimension from model, using default 768: {e}")
            return 768


class EmbeddingFactory:
    """
    Embedding模型工厂
    使用缓存机制避免重复初始化，支持多厂商模型
    """
    
    # 缓存不同配置的embedding实例
    _cache: Dict[str, EmbeddingAdapter] = {}
    
    # 默认模型映射
    DEFAULT_MODELS = {
        "openai": "text-embedding-3-small",
        "qwen": "text-embedding-v2",
        "glm": "embedding-2",
        "kimi": "moonshot-v1",
        "huggingface": "sentence-transformers/all-MiniLM-L6-v2",
    }
    
    # 提供商到适配器类的映射
    PROVIDER_ADAPTERS = {
        "openai": OpenAIEmbeddingAdapter,
        "qwen": QwenEmbeddingAdapter,
        "glm": GLMEmbeddingAdapter,
        "kimi": KimiEmbeddingAdapter,
        "huggingface": HuggingFaceEmbeddingAdapter,
    }
    
    @classmethod
    def get_embeddings(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> EmbeddingAdapter:
        """
        获取Embedding模型适配器
        
        Args:
            provider: 厂商名称 (openai, qwen, glm, kimi, huggingface)
                     默认从环境变量 EMBEDDING_PROVIDER 读取，默认为 "openai"
            model: 模型名称，默认为厂商的推荐模型
            api_key: API密钥，默认从环境变量读取
            **kwargs: 额外的配置参数
            
        Returns:
            EmbeddingAdapter 实例
            
        Examples:
            # 使用 OpenAI
            embeddings = EmbeddingFactory.get_embeddings(provider="openai")
            
            # 使用 Qwen
            embeddings = EmbeddingFactory.get_embeddings(provider="qwen")
            vec = embeddings.embed_query("北京旅游")
            
            # 使用 GLM
            embeddings = EmbeddingFactory.get_embeddings(provider="glm")
            vec = embeddings.embed_query("北京旅游")
        """
        # 获取提供商
        provider = provider or os.getenv("EMBEDDING_PROVIDER", "openai").lower()
        
        # 获取模型名称
        if not model:
            model = os.getenv("EMBEDDING_MODEL") or cls.DEFAULT_MODELS.get(provider, "")
        
        # 创建缓存键
        cache_key = f"{provider}:{model}"
        
        # 检查缓存
        if cache_key in cls._cache:
            logger.debug(f"Using cached embedding instance: {cache_key}")
            return cls._cache[cache_key]
        
        # 获取适配器类
        adapter_class = cls.PROVIDER_ADAPTERS.get(provider)
        if not adapter_class:
            raise ValueError(
                f"Unsupported embedding provider: '{provider}'. "
                f"Supported providers: {list(cls.PROVIDER_ADAPTERS.keys())}"
            )
        
        # 获取API密钥
        if not api_key:
            api_key = cls._get_api_key(provider)
        
        if not api_key:
            raise ValueError(
                f"API key not found for provider '{provider}'. "
                f"Please set the appropriate environment variable."
            )
        
        # 获取额外的配置
        config = cls._get_provider_config(provider)
        config.update(kwargs)
        
        try:
            # 创建适配器实例
            adapter = adapter_class(model=model, api_key=api_key, **config)
            
            # 缓存实例
            cls._cache[cache_key] = adapter
            logger.info(f"Created and cached embedding adapter: {cache_key}")
            
            return adapter
            
        except ImportError as e:
            logger.error(f"Failed to import required packages for {provider}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize {provider} embedding adapter: {e}")
            raise
    
    @classmethod
    def _get_api_key(cls, provider: str) -> Optional[str]:
        """获取提供商的API密钥"""
        env_vars = {
            "openai": ["OPENAI_API_KEY", "EMBEDDING_API_KEY"],
            "qwen": ["DASHSCOPE_API_KEY"],
            "glm": ["ZHIPUAI_API_KEY"],
            "kimi": ["MOONSHOT_API_KEY"],
            "huggingface": ["HUGGINGFACE_API_KEY"],
        }
        
        for env_var in env_vars.get(provider, []):
            api_key = os.getenv(env_var)
            if api_key:
                return api_key
        
        return None
    
    @classmethod
    def _get_provider_config(cls, provider: str) -> Dict[str, Any]:
        """获取提供商的额外配置"""
        config = {}
        
        if provider == "openai":
            base_url = os.getenv("OPENAI_BASE_URL")
            if base_url:
                config["base_url"] = base_url
        
        return config
    
    @classmethod
    def reset_cache(cls):
        """重置缓存（主要用于测试）"""
        cls._cache.clear()
        logger.info("EmbeddingFactory cache reset")
    
    @classmethod
    def get_cached_providers(cls) -> List[str]:
        """获取已缓存的提供商列表"""
        return list(cls._cache.keys())


# 向后兼容的辅助方法
def embed_text(text: str, provider: Optional[str] = None) -> List[float]:
    """
    嵌入单个文本（向后兼容）
    
    Args:
        text: 输入文本
        provider: 厂商名称
        
    Returns:
        文本的向量表示
    """
    embeddings = EmbeddingFactory.get_embeddings(provider=provider)
    return embeddings.embed_query(text)


def embed_texts(texts: List[str], provider: Optional[str] = None) -> List[List[float]]:
    """
    嵌入多个文本（向后兼容）
    
    Args:
        texts: 输入文本列表
        provider: 厂商名称
        
    Returns:
        文本列表的向量表示
    """
    embeddings = EmbeddingFactory.get_embeddings(provider=provider)
    return embeddings.embed_documents(texts)
