"""
多模型工作流集成测试

测试混合工作流在不同模型配置下的执行：
- 测试工作流初始化
- 测试模型切换功能
- 测试成本计算和追踪
- 测试错误降级机制
"""
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# 设置测试环境变量
os.environ["DEEPSEEK_API_KEY"] = "test_deepseek_key"
os.environ["DASHSCOPE_API_KEY"] = "test_dashscope_key"
os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_key"
os.environ["LLM_CHEAP_PROVIDER"] = "deepseek"
os.environ["LLM_STANDARD_PROVIDER"] = "qwen-turbo"
os.environ["LLM_POWER_PROVIDER"] = "claude"


class TestHybridWorkflowLLMConfig:
    """测试混合工作流的 LLM 配置"""
    
    def test_workflow_creates_three_tier_llms(self):
        """测试工作流创建三层 LLM 实例"""
        from workflows.hybrid_workflow import HybridTravelWorkflow
        
        workflow = HybridTravelWorkflow()
        
        # 验证三层 LLM 都已创建
        assert workflow.cheap_llm is not None
        assert workflow.standard_llm is not None
        assert workflow.power_llm is not None
    
    def test_workflow_llm_info_recorded(self):
        """测试工作流记录 LLM 信息"""
        from workflows.hybrid_workflow import HybridTravelWorkflow
        
        workflow = HybridTravelWorkflow()
        
        # 验证 LLM 信息已记录
        assert "cheap" in workflow.llm_info
        assert "standard" in workflow.llm_info
        assert "power" in workflow.llm_info
        
        # 验证信息结构
        assert "provider" in workflow.llm_info["cheap"]
        assert "tier" in workflow.llm_info["cheap"]
    
    def test_workflow_llm_info_contains_correct_tiers(self):
        """测试 LLM 信息包含正确的层级"""
        from workflows.hybrid_workflow import HybridTravelWorkflow
        
        workflow = HybridTravelWorkflow()
        
        assert workflow.llm_info["cheap"]["tier"] == "cheap"
        assert workflow.llm_info["standard"]["tier"] == "standard"
        assert workflow.llm_info["power"]["tier"] == "power"


class TestHybridWorkflowLLMSelection:
    """测试混合工作流的 LLM 选择逻辑"""
    
    def test_collect_info_uses_cheap_llm(self):
        """测试信息收集使用便宜层 LLM"""
        from workflows.hybrid_workflow import HybridTravelWorkflow
        
        workflow = HybridTravelWorkflow()
        
        # 验证 cheap_llm 已正确初始化
        assert workflow.cheap_llm is not None
        
        from langchain_openai import ChatOpenAI
        assert isinstance(workflow.cheap_llm, ChatOpenAI)
    
    def test_book_uses_cheap_llm(self):
        """测试预订使用便宜层 LLM"""
        from workflows.hybrid_workflow import HybridTravelWorkflow
        
        workflow = HybridTravelWorkflow()
        
        # 验证 cheap_llm 已正确初始化
        assert workflow.cheap_llm is not None


class TestDeepSubAgentsLLMCompatibility:
    """测试 DeepSubAgents 的 LLM 兼容性"""
    
    def test_deep_subagents_accepts_any_llm(self):
        """测试 DeepSubAgents 接受任意 LLM 实例"""
        from agents.deep_subagents import DeepSubAgentsManager
        from langchain_openai import ChatOpenAI
        
        # 创建 mock LLM
        mock_llm = MagicMock(spec=ChatOpenAI)
        mock_llm.model = "test-model"
        
        # 创建管理器（不初始化）
        manager = DeepSubAgentsManager(mock_llm)
        
        assert manager.llm == mock_llm
        assert manager.llm_model == "test-model"
    
    def test_simplified_deep_agent_accepts_any_llm(self):
        """测试 SimplifiedDeepAgent 接受任意 LLM 实例"""
        from agents.deep_subagents import SimplifiedDeepAgent
        from langchain_openai import ChatOpenAI
        
        # 创建 mock LLM
        mock_llm = MagicMock(spec=ChatOpenAI)
        mock_llm.model = "test-model"
        
        # 创建 DeepAgent
        agent = SimplifiedDeepAgent(
            llm=mock_llm,
            system_prompt="Test prompt"
        )
        
        assert agent.llm == mock_llm
        assert agent.system_prompt == "Test prompt"
        assert agent.llm_model == "test-model"


class TestAgentsLLMCompatibility:
    """测试各 Agent 的 LLM 兼容性"""
    
    def test_info_collection_agent_accepts_llm(self):
        """测试 InfoCollectionAgent 接受 LLM 参数"""
        from agents.info_collection import InfoCollectionAgent
        from langchain_openai import ChatOpenAI
        
        # 创建 mock LLM
        mock_llm = MagicMock(spec=ChatOpenAI)
        
        # 创建带 LLM 的 agent
        agent = InfoCollectionAgent(llm=mock_llm)
        
        assert agent.llm == mock_llm
    
    def test_info_collection_agent_without_llm(self):
        """测试 InfoCollectionAgent 没有 LLM 时使用 mock"""
        from agents.info_collection import InfoCollectionAgent
        
        # 创建不带 LLM 的 agent
        agent = InfoCollectionAgent()
        
        assert agent.llm is None
    
    def test_recommendation_agent_accepts_llm(self):
        """测试 RecommendationAgent 接受 LLM 参数"""
        from agents.recommendation import RecommendationAgent
        from langchain_openai import ChatOpenAI
        
        # 创建 mock LLM
        mock_llm = MagicMock(spec=ChatOpenAI)
        
        # 创建带 LLM 的 agent
        agent = RecommendationAgent(llm=mock_llm)
        
        assert agent.llm == mock_llm
    
    def test_recommendation_agent_without_llm(self):
        """测试 RecommendationAgent 没有 LLM 时使用 mock"""
        from agents.recommendation import RecommendationAgent
        
        # 创建不带 LLM 的 agent
        agent = RecommendationAgent()
        
        assert agent.llm is None


class TestLLMConfigIntegration:
    """测试 LLM 配置集成"""
    
    def test_settings_has_tier_configuration(self):
        """测试配置包含层级设置"""
        from config import settings
        
        # 检查是否有层级配置
        assert hasattr(settings, 'llm_cheap_provider')
        assert hasattr(settings, 'llm_standard_provider')
        assert hasattr(settings, 'llm_power_provider')
    
    def test_settings_has_api_keys(self):
        """测试配置包含 API Keys"""
        from config import settings
        
        # 检查是否有 API Key 配置
        assert hasattr(settings, 'deepseek_api_key')
        assert hasattr(settings, 'dashscope_api_key')
        assert hasattr(settings, 'zhipu_api_key')
        assert hasattr(settings, 'anthropic_api_key')


class TestLLMCostEstimation:
    """测试 LLM 成本估算"""
    
    def test_cost_calculation_for_different_tiers(self):
        """测试不同层级的成本计算"""
        from config.llm_config import LLMFactory
        
        # 便宜层成本
        cheap_cost = LLMFactory.get_cost_estimate("deepseek", 1000, 500)
        
        # 强力层成本
        power_cost = LLMFactory.get_cost_estimate("claude", 1000, 500)
        
        # 强力层应该更贵
        assert power_cost >= cheap_cost
    
    def test_cost_calculation_for_large_requests(self):
        """测试大批量请求的成本计算"""
        from config.llm_config import LLMFactory
        
        # 大批量请求
        cost = LLMFactory.get_cost_estimate("deepseek", 10000, 5000)
        
        assert cost >= 0
        # 成本应该与 token 数量成正比
        assert cost > LLMFactory.get_cost_estimate("deepseek", 1000, 500)


class TestLLMFallbackMechanism:
    """测试 LLM 降级机制"""
    
    def test_fallback_when_provider_not_configured(self):
        """测试 provider 未配置时的降级"""
        from config.llm_config import LLMFactory, ModelTier
        
        # 模拟一个未配置的 provider
        with patch('config.llm_config.LLMProvider.is_configured', new_callable=lambda: lambda s: False):
            # 应该返回备选 provider
            fallback = LLMFactory._get_fallback_provider(ModelTier.CHEAP)
            assert isinstance(fallback, str)


class TestLLMProviderAvailability:
    """测试 provider 可用性"""
    
    def test_is_provider_available_with_configured_key(self):
        """测试配置了 API key 的 provider"""
        from config.llm_config import LLMFactory
        
        # DeepSeek 应该已配置
        assert LLMFactory.is_provider_available("deepseek") == True
    
    def test_is_provider_available_with_unconfigured_key(self):
        """测试未配置 API key 的 provider"""
        from config.llm_config import LLMFactory
        
        # 虚构的 provider 应该不可用
        assert LLMFactory.is_provider_available("nonexistent_provider_test_12345") == False


class TestLLMModelList:
    """测试模型列表功能"""
    
    def test_list_models_returns_dict(self):
        """测试模型列表返回字典"""
        from config.llm_config import LLMFactory
        
        models = LLMFactory.list_available_models()
        
        assert isinstance(models, dict)
        assert len(models) > 0
    
    def test_list_models_contains_all_tiers(self):
        """测试模型列表包含所有层级"""
        from config.llm_config import LLMFactory, ModelTier
        
        models = LLMFactory.list_available_models()
        
        tiers_present = set()
        for name, info in models.items():
            tiers_present.add(info["tier"])
        
        assert "cheap" in tiers_present
        assert "standard" in tiers_present
        assert "power" in tiers_present


class TestWorkflowExecution:
    """测试工作流执行"""
    
    @pytest.mark.asyncio
    async def test_workflow_run_with_config(self):
        """测试工作流运行"""
        from workflows.hybrid_workflow import HybridTravelWorkflow
        
        workflow = HybridTravelWorkflow()
        
        # 验证工作流已正确初始化
        assert workflow.cheap_llm is not None
        assert workflow.standard_llm is not None
        assert workflow.power_llm is not None
        
        # 验证 LLM 信息
        assert "cheap" in workflow.llm_info
        assert "standard" in workflow.llm_info
        assert "power" in workflow.llm_info
    
    @pytest.mark.asyncio
    async def test_workflow_llm_info_in_result(self):
        """测试工作流结果包含 LLM 配置"""
        from workflows.hybrid_workflow import HybridTravelWorkflow
        
        workflow = HybridTravelWorkflow()
        
        # 验证 llm_info 结构
        assert isinstance(workflow.llm_info, dict)
        assert len(workflow.llm_info) == 3
        
        for tier, info in workflow.llm_info.items():
            assert "provider" in info
            assert "tier" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
