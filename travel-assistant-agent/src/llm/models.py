"""
LLM 模型配置数据类
定义支持的 LLM 模型和相关配置
"""
from enum import Enum
from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """LLM 提供商枚举"""
    OPENAI = "openai"
    CLAUDE = "claude"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    GLM = "glm"
    MODELSCOPE = "modelscope"


class ModelTier(str, Enum):
    """LLM 层级枚举"""
    CHEAP = "cheap"      # 便宜层：信息收集、预订
    STANDARD = "standard"  # 标准层：搜索、推荐
    POWERFUL = "powerful"  # 强力层：复杂推理


class ModelConfig(BaseModel):
    """模型配置"""
    name: str                              # 模型名称
    provider: ModelProvider                # 服务商
    model_id: str                         # 模型ID（用于API调用）
    base_url: str                         # API基础URL
    api_key_env: str                      # API KEY环境变量名
    max_tokens: int = 4096                # 最大token数
    temperature: float = 0.7              # 温度
    top_p: float = 1.0                    # Top P
    # 成本参数（单位：美元/1M tokens）
    input_cost: float                     # 输入成本
    output_cost: float                    # 输出成本
    cache_read_cost: Optional[float] = None  # 缓存读取成本
    enable_thinking: bool = False # 取消思考模式

    class Config:
        use_enum_values = True


# 预置模型配置
MODELS: Dict[str, ModelConfig] = {
    # ============ OpenAI ============
    "gpt-4": ModelConfig(
        name="GPT-4",
        provider=ModelProvider.OPENAI,
        model_id="gpt-4",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        max_tokens=8192,
        input_cost=0.03,
        output_cost=0.06,
        cache_read_cost=0.0075,
        enable_thinking=False,
    ),
    "gpt-4-turbo": ModelConfig(
        name="GPT-4 Turbo",
        provider=ModelProvider.OPENAI,
        model_id="gpt-4-turbo",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        max_tokens=128000,
        input_cost=0.01,
        output_cost=0.03,
        cache_read_cost=0.0025,
        enable_thinking=False,
    ),

    # ============ Anthropic Claude ============
    "claude-3.5-sonnet": ModelConfig(
        name="Claude 3.5 Sonnet",
        provider=ModelProvider.CLAUDE,
        model_id="claude-3-5-sonnet-20241022",
        base_url="https://api.anthropic.com",
        api_key_env="ANTHROPIC_API_KEY",
        max_tokens=200000,
        input_cost=0.003,
        output_cost=0.015,
        cache_read_cost=0.0003,
        enable_thinking=False,
    ),
    "claude-3-opus": ModelConfig(
        name="Claude 3 Opus",
        provider=ModelProvider.CLAUDE,
        model_id="claude-3-opus-20240229",
        base_url="https://api.anthropic.com",
        api_key_env="ANTHROPIC_API_KEY",
        max_tokens=200000,
        input_cost=0.015,
        output_cost=0.075,
        cache_read_cost=0.00375,
        enable_thinking=False,
    ),

    # ============ Qwen ============
    "qwen-max": ModelConfig(
        name="Qwen Max",
        provider=ModelProvider.QWEN,
        model_id="qwen-max",
        base_url="https://dashscope.aliyuncs.com/api/v1",
        api_key_env="DASHSCOPE_API_KEY",
        max_tokens=8192,
        input_cost=0.0005,
        output_cost=0.0015,
        cache_read_cost=None,
        enable_thinking=False,
    ),

    # ============ DeepSeek ============
    "deepseek-v3": ModelConfig(
        name="DeepSeek V3",
        provider=ModelProvider.DEEPSEEK,
        model_id="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key_env="DEEPSEEK_API_KEY",
        max_tokens=64000,
        input_cost=0.0002,
        output_cost=0.001,
        cache_read_cost=None,
        enable_thinking=False,
    ),

    # ============ GLM ============
    "glm-4": ModelConfig(
        name="GLM-4",
        provider=ModelProvider.GLM,
        # model_id="glm-4-0520",
        model_id="glm-4.7-flash",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key_env="ZHIPU_API_KEY",
        max_tokens=8192,
        input_cost=0.0001,
        output_cost=0.0003,
        cache_read_cost=None,
        enable_thinking=False,
    ),
    "modelscope": ModelConfig(
        name="Qwen3-32B",
        provider=ModelProvider.MODELSCOPE,
        model_id="Qwen/Qwen3-32B",
        base_url="https://api-inference.modelscope.cn/v1/",
        api_key_env="MODEL_SCOPE_API_KEY",
        max_tokens=8192,
        input_cost=0.0001,
        output_cost=0.0003,
        cache_read_cost=None,
        enable_thinking=False,
    )
}
