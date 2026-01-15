"""
LLM 工厂类
提供统一的 LLM 实例创建接口，支持多模型切换
"""
from typing import Optional, List, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)


class LLMFactory:
    """LLM工厂类，支持多模型切换"""

    _instances: Dict[str, Any] = {}

    @classmethod
    def create_model(
        cls,
        name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        创建LLM实例

        Args:
            name: 模型名称，如果为None则使用LLM_DEFAULT_MODEL
            **kwargs: 覆盖模型配置的参数

        Returns:
            ChatOpenAI实例
        """
        if name is None:
            name = os.getenv("LLM_DEFAULT_MODEL", "gpt-4")

        # 从缓存返回
        if name in cls._instances:
            return cls._instances[name]

        # 动态导入，避免循环依赖
        from .models import MODELS

        if name not in MODELS:
            raise ValueError(f"Unknown model: {name}")

        config = MODELS[name]
        api_key = os.getenv(config.api_key_env)

        if not api_key:
            raise ValueError(f"Missing API key: {config.api_key_env}")

        # 构建ChatOpenAI实例
        llm = cls._create_llm_instance(config, api_key, **kwargs)

        cls._instances[name] = llm
        return llm

    @classmethod
    def _create_llm_instance(
        cls,
        config,
        api_key: str,
        **kwargs
    ) -> Any:
        """创建具体的 LLM 实例"""
        # 根据 provider 创建不同的实例
        if config.provider.value == "claude":
            # Anthropic Claude 需要使用原生 SDK
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=config.model_id,
                    anthropic_api_key=api_key,
                    temperature=kwargs.get("temperature", config.temperature),
                    max_tokens=kwargs.get("max_tokens", config.max_tokens),
                    top_p=kwargs.get("top_p", config.top_p),
                )
            except ImportError:
                logger.warning("langchain_anthropic not available, using OpenAI-compatible interface")
                # 降级使用 OpenAI 兼容接口
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=config.model_id,
                    base_url=config.base_url,
                    api_key=api_key,
                    temperature=kwargs.get("temperature", config.temperature),
                    max_tokens=kwargs.get("max_tokens", config.max_tokens),
                    top_p=kwargs.get("top_p", config.top_p),
                )
        else:
            # OpenAI 兼容接口
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=config.model_id,
                base_url=config.base_url,
                api_key=api_key,
                temperature=kwargs.get("temperature", config.temperature),
                max_tokens=kwargs.get("max_tokens", config.max_tokens),
                top_p=kwargs.get("top_p", config.top_p),
            )

    @classmethod
    def list_available_models(cls) -> List[str]:
        """列出所有可用模型"""
        from .models import MODELS
        return list(MODELS.keys())

    @classmethod
    def get_model_config(cls, name: str):
        """获取模型配置"""
        from .models import MODELS
        if name not in MODELS:
            raise ValueError(f"Unknown model: {name}")
        return MODELS[name]

    @classmethod
    def get_model_cost(
        cls,
        name: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_read_tokens: int = 0
    ) -> float:
        """计算模型使用成本（单位：美元）"""
        config = cls.get_model_config(name)

        cost = (
            input_tokens * config.input_cost / 1_000_000 +
            output_tokens * config.output_cost / 1_000_000
        )

        if cache_read_tokens > 0 and config.cache_read_cost:
            cost += cache_read_tokens * config.cache_read_cost / 1_000_000

        return cost
