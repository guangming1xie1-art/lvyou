"""
LLMFactory 单元测试

测试 LLMFactory 的各项功能：
- 模型配置查找
- LLM 实例创建
- 成本估算
- 备选 provider 降级
"""
import os
import pytest
from unittest.mock import patch, MagicMock

# 设置测试环境变量
os.environ["DEEPSEEK_API_KEY"] = "test_deepseek_key"
os.environ["DASHSCOPE_API_KEY"] = "test_dashscope_key"
os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_key"


class TestModelTier:
    """测试 ModelTier 枚举"""
    
    def test_tier_values(self):
        from config.llm_config import ModelTier
        
        assert ModelTier.CHEAP.value == "cheap"
        assert ModelTier.STANDARD.value == "standard"
        assert ModelTier.POWER.value == "power"
    
    def test_tier_comparison(self):
        from config.llm_config import ModelTier
        
        # 测试字符串比较
        assert ModelTier.CHEAP == ModelTier("cheap")
        assert ModelTier.STANDARD == ModelTier("standard")
        assert ModelTier.POWER == ModelTier("power")


class TestLLMProvider:
    """测试 LLMProvider 枚举"""
    
    def test_provider_values(self):
        from config.llm_config import LLMProvider
        
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.DEEPSEEK.value == "deepseek"
        assert LLMProvider.DASHSCOPE.value == "dashscope"
        assert LLMProvider.ZHIPU.value == "zhipu"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
    
    def test_is_configured(self):
        from config.llm_config import LLMProvider
        
        # 测试配置检查
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test_key"}, clear=False):
            assert LLMProvider.DEEPSEEK.is_configured() == True
        
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}, clear=False):
            assert LLMProvider.DEEPSEEK.is_configured() == False


class TestModelConfig:
    """测试 ModelConfig 数据类"""
    
    def test_model_config_creation(self):
        from config.llm_config import ModelConfig, LLMProvider, ModelTier
        
        config = ModelConfig(
            name="test-model",
            display_name="Test Model",
            provider=LLMProvider.DEEPSEEK,
            tier=ModelTier.CHEAP,
            base_url="https://api.test.com/v1",
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.001
        )
        
        assert config.name == "test-model"
        assert config.provider == LLMProvider.DEEPSEEK
        assert config.tier == ModelTier.CHEAP
        assert config.max_tokens == 4096


class TestMODELCONFIGS:
    """测试 MODEL_CONFIGS 字典"""
    
    def test_all_tiers_have_models(self):
        from config.llm_config import MODEL_CONFIGS, ModelTier
        
        cheap_models = [m for m in MODEL_CONFIGS.values() if m.tier == ModelTier.CHEAP]
        standard_models = [m for m in MODEL_CONFIGS.values() if m.tier == ModelTier.STANDARD]
        power_models = [m for m in MODEL_CONFIGS.values() if m.tier == ModelTier.POWER]
        
        # 每个层级至少有一个模型
        assert len(cheap_models) >= 3
        assert len(standard_models) >= 3
        assert len(power_models) >= 3
    
    def test_expected_models_exist(self):
        from config.llm_config import MODEL_CONFIGS
        
        # 便宜层
        assert "deepseek-chat" in MODEL_CONFIGS
        assert "qwen-plus" in MODEL_CONFIGS
        assert "gpt-4o-mini" in MODEL_CONFIGS
        
        # 标准层
        assert "qwen-turbo" in MODEL_CONFIGS
        assert "glm-4" in MODEL_CONFIGS
        assert "gpt-4o" in MODEL_CONFIGS
        
        # 强力层
        assert "claude-3-5-sonnet-20241022" in MODEL_CONFIGS
        assert "qwen-max" in MODEL_CONFIGS
        assert "deepseek-reasoner" in MODEL_CONFIGS
    
    def test_all_models_have_cost_info(self):
        from config.llm_config import MODEL_CONFIGS
        
        for name, config in MODEL_CONFIGS.items():
            assert config.cost_per_1k_tokens >= 0, f"{name} missing cost info"


class TestLLMFactory:
    """测试 LLMFactory 工厂类"""
    
    def test_create_llm_deepseek(self):
        from config.llm_config import LLMFactory, ModelTier
        
        llm = LLMFactory.create_llm("deepseek", ModelTier.CHEAP)
        
        assert llm is not None
        # 验证是 ChatOpenAI 实例
        from langchain_openai import ChatOpenAI
        assert isinstance(llm, ChatOpenAI)
    
    def test_create_llm_dashscope(self):
        from config.llm_config import LLMFactory, ModelTier
        
        llm = LLMFactory.create_llm("dashscope", ModelTier.STANDARD)
        
        assert llm is not None
        from langchain_openai import ChatOpenAI
        assert isinstance(llm, ChatOpenAI)
    
    def test_create_llm_with_custom_params(self):
        from config.llm_config import LLMFactory, ModelTier
        
        llm = LLMFactory.create_llm(
            "deepseek", 
            ModelTier.CHEAP,
            temperature=0.5,
            max_tokens=2048
        )
        
        assert llm is not None
    
    def test_get_default_llm(self):
        from config.llm_config import LLMFactory, ModelTier
        
        # 测试获取各层级的默认 LLM
        cheap_llm = LLMFactory.get_default_llm(ModelTier.CHEAP)
        standard_llm = LLMFactory.get_default_llm(ModelTier.STANDARD)
        power_llm = LLMFactory.get_default_llm(ModelTier.POWER)
        
        assert cheap_llm is not None
        assert standard_llm is not None
        assert power_llm is not None
    
    def test_get_tier_for_provider(self):
        from config.llm_config import LLMFactory, ModelTier
        
        assert LLMFactory.get_tier_for_provider("deepseek") == ModelTier.CHEAP
        assert LLMFactory.get_tier_for_provider("qwen-turbo") == ModelTier.STANDARD
        assert LLMFactory.get_tier_for_provider("claude") == ModelTier.POWER
    
    def test_list_available_models(self):
        from config.llm_config import LLMFactory
        
        models = LLMFactory.list_available_models()
        
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # 检查返回的模型信息格式
        for name, info in models.items():
            assert "display_name" in info
            assert "provider" in info
            assert "tier" in info
            assert "configured" in info
    
    def test_get_cost_estimate(self):
        from config.llm_config import LLMFactory
        
        # 测试成本估算
        cost = LLMFactory.get_cost_estimate("deepseek", 1000, 500)
        assert cost >= 0
        
        # 测试标准输入输出
        cost = LLMFactory.get_cost_estimate("claude", 5000, 2000)
        assert cost >= 0
    
    def test_is_provider_available(self):
        from config.llm_config import LLMFactory
        
        # DeepSeek 已配置
        assert LLMFactory.is_provider_available("deepseek") == True
        
        # 虚构的 provider
        assert LLMFactory.is_provider_available("nonexistent") == False


class TestLLMFactoryFallback:
    """测试 LLMFactory 降级机制"""
    
    def test_fallback_chain_exists(self):
        from config.llm_config import LLMFactory, ModelTier
        
        # 检查降级链是否存在
        assert ModelTier.CHEAP in LLMFactory.FALLBACK_CHAINS
        assert ModelTier.STANDARD in LLMFactory.FALLBACK_CHAINS
        assert ModelTier.POWER in LLMFactory.FALLBACK_CHAINS
    
    def test_get_fallback_provider(self):
        from config.llm_config import LLMFactory, ModelTier
        
        # 测试获取备选 provider
        fallback = LLMFactory._get_fallback_provider(ModelTier.CHEAP)
        assert isinstance(fallback, str)
        assert len(fallback) > 0


class TestLLMFactoryEdgeCases:
    """测试 LLMFactory 边界情况"""
    
    def test_create_llm_with_invalid_provider(self):
        from config.llm_config import LLMFactory, ModelTier
        
        # 使用不存在的 provider 应该返回降级 LLM
        llm = LLMFactory.create_llm("nonexistent_provider", ModelTier.CHEAP)
        
        # 仍然应该返回一个可用的 LLM（可能是降级版本）
        assert llm is not None
    
    def test_create_llm_without_tier(self):
        from config.llm_config import LLMFactory
        
        # 不指定 tier 应该也能工作
        llm = LLMFactory.create_llm("deepseek")
        assert llm is not None
    
    def test_cost_estimate_unknown_provider(self):
        from config.llm_config import LLMFactory
        
        # 未知 provider 应该返回默认成本
        cost = LLMFactory.get_cost_estimate("unknown", 1000, 500)
        assert cost >= 0


class TestLLMIntegration:
    """测试 LLM 集成"""
    
    def test_cheap_llm_has_different_cost_than_power(self):
        from config.llm_config import MODEL_CONFIGS, ModelTier
        
        cheap_configs = [c for c in MODEL_CONFIGS.values() if c.tier == ModelTier.CHEAP]
        power_configs = [c for c in MODEL_CONFIGS.values() if c.tier == ModelTier.POWER]
        
        # 便宜层应该比强力层便宜
        cheap_avg_cost = sum(c.cost_per_1k_tokens for c in cheap_configs) / len(cheap_configs)
        power_avg_cost = sum(c.cost_per_1k_tokens for c in power_configs) / len(power_configs)
        
        assert cheap_avg_cost < power_avg_cost
    
    def test_all_providers_have_base_url_or_special_handling(self):
        from config.llm_config import MODEL_CONFIGS
        
        for name, config in MODEL_CONFIGS.items():
            if config.provider.value != "anthropic":
                assert config.base_url is not None, f"{name} missing base_url"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
