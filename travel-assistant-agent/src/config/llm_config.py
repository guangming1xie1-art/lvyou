"""
LLM 配置模块
统一管理多模型配置，支持分层调用（便宜/标准/强力）
"""

import os
import logging
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

# 使用标准 logging 避免循环导入
logger = logging.getLogger(__name__)


class ModelTier(str, Enum):
    """模型层级枚举"""

    CHEAP = "cheap"  # 便宜层 - 简单任务
    STANDARD = "standard"  # 标准层 - 中等复杂任务
    POWER = "power"  # 强力层 - 复杂推理任务


class LLMProvider(str, Enum):
    """LLM 提供商枚举"""

    # OpenAI 兼容提供商
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    DASHSCOPE = "dashscope"  # 阿里云通义千问
    ZHIPU = "zhipu"  # 智谱 AI
    ANTHROPIC = "anthropic"

    @property
    def is_configured(self) -> bool:
        """检查是否配置了 API Key"""
        return bool(self.get_api_key())

    def get_api_key(self) -> Optional[str]:
        """获取 API Key"""
        key_map = {
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.DEEPSEEK: "DEEPSEEK_API_KEY",
            LLMProvider.DASHSCOPE: "DASHSCOPE_API_KEY",
            LLMProvider.ZHIPU: "ZHIPU_API_KEY",
            LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
        }
        return os.getenv(key_map.get(self, ""))


@dataclass
class ModelConfig:
    """模型配置数据类"""

    name: str  # 模型名称
    display_name: str  # 显示名称
    provider: LLMProvider  # 提供商
    tier: ModelTier  # 层级
    base_url: Optional[str] = None  # API 基础 URL
    max_tokens: int = 4096  # 最大输出 tokens
    temperature: float = 0.7  # 温度参数
    cost_per_1k_tokens: float = 0.0  # 每 1k tokens 成本（ USD）


# 所有支持的模型配置
MODEL_CONFIGS: Dict[str, ModelConfig] = {
    # ============ 便宜层 (CHEAP) ============
    "deepseek-chat": ModelConfig(
        name="deepseek-chat",
        display_name="DeepSeek Chat",
        provider=LLMProvider.DEEPSEEK,
        tier=ModelTier.CHEAP,
        base_url="https://api.deepseek.com/v1",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1k_tokens=0.0014,  # ¥0.0014 = ~$0.0002
    ),
    "qwen-plus": ModelConfig(
        name="qwen-plus",
        display_name="通义千问 Plus",
        provider=LLMProvider.DASHSCOPE,
        tier=ModelTier.CHEAP,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1k_tokens=0.005,  # ¥0.005
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        display_name="GPT-4o Mini",
        provider=LLMProvider.OPENAI,
        tier=ModelTier.CHEAP,
        base_url="https://api.openai.com/v1",
        max_tokens=16384,
        temperature=0.7,
        cost_per_1k_tokens=0.15,  # $0.15/1M input
    ),
    # ============ 标准层 (STANDARD) ============
    "qwen-turbo": ModelConfig(
        name="qwen-turbo",
        display_name="通义千问 Turbo",
        provider=LLMProvider.DASHSCOPE,
        tier=ModelTier.STANDARD,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        max_tokens=8192,
        temperature=0.7,
        cost_per_1k_tokens=0.008,  # ¥0.008
    ),
    "glm-4": ModelConfig(
        name="glm-4",
        display_name="GLM-4",
        provider=LLMProvider.ZHIPU,
        tier=ModelTier.STANDARD,
        base_url="https://open.bigmodel.cn/api/paas/v4",
        max_tokens=4096,
        temperature=0.7,
        cost_per_1k_tokens=0.01,  # ¥0.01
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        display_name="GPT-4o",
        provider=LLMProvider.OPENAI,
        tier=ModelTier.STANDARD,
        base_url="https://api.openai.com/v1",
        max_tokens=16384,
        temperature=0.7,
        cost_per_1k_tokens=5.0,  # $5.00/1M input
    ),
    # ============ 强力层 (POWER) ============
    "claude-3-5-sonnet-20241022": ModelConfig(
        name="claude-3-5-sonnet-20241022",
        display_name="Claude 3.5 Sonnet",
        provider=LLMProvider.ANTHROPIC,
        tier=ModelTier.POWER,
        base_url=None,  # Anthropic 使用原生 SDK
        max_tokens=4096,
        temperature=0.3,
        cost_per_1k_tokens=3.0,  # $3.00/1M input
    ),
    "qwen-max": ModelConfig(
        name="qwen-max",
        display_name="通义千问 Max",
        provider=LLMProvider.DASHSCOPE,
        tier=ModelTier.POWER,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        max_tokens=8192,
        temperature=0.7,
        cost_per_1k_tokens=0.05,  # ¥0.05
    ),
    "deepseek-reasoner": ModelConfig(
        name="deepseek-reasoner",
        display_name="DeepSeek Reasoner",
        provider=LLMProvider.DEEPSEEK,
        tier=ModelTier.POWER,
        base_url="https://api.deepseek.com/v1",
        max_tokens=4096,
        temperature=0.3,
        cost_per_1k_tokens=0.0028,  # ¥0.0028（深度推理，性价比高）
    ),
}


class LLMFactory:
    """LLM 工厂类 - 创建和管理 LLM 实例"""

    # 默认 provider 配置
    DEFAULT_CHEAP_PROVIDER = "deepseek"
    DEFAULT_STANDARD_PROVIDER = "qwen-turbo"
    DEFAULT_POWER_PROVIDER = "claude"

    # 各层级的备选 provider（按优先级排序）
    FALLBACK_CHAINS: Dict[ModelTier, list] = {
        ModelTier.CHEAP: ["deepseek", "qwen-plus", "gpt-4o-mini", "qwen-turbo"],
        ModelTier.STANDARD: ["qwen-turbo", "glm-4", "gpt-4o", "qwen-max"],
        ModelTier.POWER: ["claude", "deepseek-reasoner", "qwen-max", "gpt-4o"],
    }

    @classmethod
    def create_llm(
        cls,
        provider: str,
        tier: Optional[ModelTier] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Any:
        """
        创建 ChatOpenAI 实例

        Args:
            provider: 提供商名称 (如 "deepseek", "qwen-turbo", "claude")
            tier: 模型层级，用于查找配置
            temperature: 温度参数
            max_tokens: 最大输出 tokens
            **kwargs: 额外参数

        Returns:
            ChatOpenAI 实例或兼容的 LLM 实例
        """
        provider = provider.lower().strip()

        # 查找模型配置
        model_config = cls._find_model_config(provider, tier)

        if model_config is None:
            logger.warning(
                f"No model config found for provider: {provider}, tier: {tier}"
            )
            # 使用默认配置创建
            return cls._create_fallback_llm(provider, temperature, max_tokens)

        # 获取 API Key
        api_key = model_config.provider.get_api_key()

        if not api_key:
            logger.warning(
                f"API key not configured for provider: {model_config.provider.value}"
            )
            # 尝试使用备选 provider
            fallback = cls._get_fallback_provider(tier or ModelTier.CHEAP)
            return cls.create_llm(fallback, tier, temperature, max_tokens, **kwargs)

        # 创建 LLM 实例
        return cls._create_llm_instance(
            model_config, api_key, temperature, max_tokens, **kwargs
        )

    @classmethod
    def _find_model_config(
        cls, provider: str, tier: Optional[ModelTier]
    ) -> Optional[ModelConfig]:
        """查找模型配置"""
        provider_enum = (
            LLMProvider(provider)
            if provider in [p.value for p in LLMProvider]
            else None
        )

        # 遍历配置查找匹配的模型
        for config in MODEL_CONFIGS.values():
            if provider_enum and config.provider == provider_enum:
                if tier is None or config.tier == tier:
                    return config
            # 通过 provider 名称匹配
            if config.provider.value == provider:
                if tier is None or config.tier == tier:
                    return config

        return None

    @classmethod
    def _create_llm_instance(
        cls,
        config: ModelConfig,
        api_key: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
    ) -> Any:
        """创建 LLM 实例"""
        # 通用参数
        model_kwargs = {
            "model": config.name,
            "openai_api_key": api_key,
        }

        # 设置温度和 max_tokens
        if temperature is not None:
            model_kwargs["temperature"] = temperature
        else:
            model_kwargs["temperature"] = config.temperature

        if max_tokens is not None:
            model_kwargs["max_tokens"] = max_tokens
        else:
            model_kwargs["max_tokens"] = config.max_tokens

        # 根据 provider 类型创建不同的实例
        if config.provider == LLMProvider.ANTHROPIC:
            # Anthropic 需要使用原生 SDK
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                anthropic_api_key=api_key,
                model=config.name,
                temperature=model_kwargs.get("temperature", config.temperature),
                max_tokens=model_kwargs.get("max_tokens", config.max_tokens),
            )
        else:
            # OpenAI 兼容的模型使用 ChatOpenAI
            from langchain_openai import ChatOpenAI

            if config.base_url:
                model_kwargs["openai_api_base"] = config.base_url

            return ChatOpenAI(**model_kwargs)

    @classmethod
    def _create_fallback_llm(
        cls, provider: str, temperature: Optional[float], max_tokens: Optional[int]
    ) -> Any:
        """创建降级 LLM 实例"""
        logger.info(f"Creating fallback LLM for provider: {provider}")

        # 创建基本的 ChatOpenAI 实例
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY", "")

        return ChatOpenAI(
            model=provider,
            api_key=api_key,
            temperature=temperature or 0.7,
            max_tokens=max_tokens or 4096,
            base_url=None,
        )

    @classmethod
    def _get_fallback_provider(cls, tier: ModelTier) -> str:
        """获取备选 provider"""
        fallbacks = cls.FALLBACK_CHAINS.get(tier, ["deepseek"])
        for fallback in fallbacks:
            provider = LLMProvider(fallback)
            if provider.is_configured:
                return fallback
        return fallbacks[0]

    @classmethod
    def get_default_llm(cls, tier: ModelTier = ModelTier.STANDARD) -> Any:
        """
        获取默认 LLM 实例

        Args:
            tier: 模型层级

        Returns:
            默认 LLM 实例
        """
        provider_map = {
            ModelTier.CHEAP: cls.DEFAULT_CHEAP_PROVIDER,
            ModelTier.STANDARD: cls.DEFAULT_STANDARD_PROVIDER,
            ModelTier.POWER: cls.DEFAULT_POWER_PROVIDER,
        }

        provider = provider_map.get(tier, cls.DEFAULT_STANDARD_PROVIDER)
        return cls.create_llm(provider, tier)

    @classmethod
    def get_tier_for_provider(cls, provider: str) -> Optional[ModelTier]:
        """获取 provider 对应的层级"""
        provider = provider.lower()
        # 首先尝试通过模型名称匹配
        if provider in MODEL_CONFIGS:
            return MODEL_CONFIGS[provider].tier
        # 然后尝试通过 provider 值匹配
        for config in MODEL_CONFIGS.values():
            if config.provider.value == provider:
                return config.tier
        return None

    @classmethod
    def list_available_models(cls) -> Dict[str, Dict[str, Any]]:
        """列出所有可用的模型配置"""
        available = {}
        for name, config in MODEL_CONFIGS.items():
            is_ready = config.provider.is_configured
            available[name] = {
                "display_name": config.display_name,
                "provider": config.provider.value,
                "tier": config.tier.value,
                "cost_per_1k_tokens": config.cost_per_1k_tokens,
                "configured": is_ready,
                "base_url": config.base_url,
            }
        return available

    @classmethod
    def get_cost_estimate(
        cls, provider: str, input_tokens: int, output_tokens: int
    ) -> float:
        """
        估算请求成本

        Args:
            provider: 提供商名称
            input_tokens: 输入 tokens
            output_tokens: 输出 tokens

        Returns:
            预估成本（USD）
        """
        provider = provider.lower()

        for config in MODEL_CONFIGS.values():
            if config.provider.value == provider:
                total_tokens = input_tokens + output_tokens
                return (total_tokens / 1000) * config.cost_per_1k_tokens

        # 默认成本估算（假设为 GPT-4o 级别）
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * 0.005

    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """检查 provider 是否可用"""
        try:
            provider_enum = LLMProvider(provider)
            return provider_enum.is_configured
        except ValueError:
            # 尝试通过模型名称查找
            for config in MODEL_CONFIGS.values():
                if config.name == provider or config.provider.value == provider:
                    return config.provider.is_configured
            return False
