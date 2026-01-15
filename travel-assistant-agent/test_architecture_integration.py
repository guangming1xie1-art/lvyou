"""
完整的三层架构集成测试
测试 LLM 多模型接口 → LangGraph 工作流 → DeepAgent 子智能体的完整流程
"""
import asyncio
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class TestMultiModelInterface:
    """测试 Phase 1.2: 多模型统一接口"""

    def test_module_import(self):
        """测试模块导入"""
        from src.llm import LLMFactory, ModelProvider, ModelConfig, MODELS
        assert LLMFactory is not None
        assert ModelProvider is not None
        assert ModelConfig is not None
        assert MODELS is not None

    def test_model_provider_enum(self):
        """测试 ModelProvider 枚举"""
        from src.llm import ModelProvider

        assert ModelProvider.OPENAI.value == "openai"
        assert ModelProvider.CLAUDE.value == "claude"
        assert ModelProvider.QWEN.value == "qwen"
        assert ModelProvider.DEEPSEEK.value == "deepseek"
        assert ModelProvider.GLM.value == "glm"

    def test_model_configs(self):
        """测试模型配置"""
        from src.llm import MODELS, ModelProvider

        # 检查配置完整性
        assert "gpt-4" in MODELS
        assert "gpt-4-turbo" in MODELS
        assert "claude-3.5-sonnet" in MODELS
        assert "qwen-max" in MODELS
        assert "deepseek-v3" in MODELS
        assert "glm-4" in MODELS

        # 检查单个模型配置
        gpt4_config = MODELS["gpt-4"]
        assert gpt4_config.name == "GPT-4"
        assert gpt4_config.provider == ModelProvider.OPENAI
        assert gpt4_config.model_id == "gpt-4"
        assert gpt4_config.base_url == "https://api.openai.com/v1"
        assert gpt4_config.api_key_env == "OPENAI_API_KEY"
        assert gpt4_config.input_cost == 0.03
        assert gpt4_config.output_cost == 0.06

    def test_list_available_models(self):
        """测试列出可用模型"""
        from src.llm import LLMFactory

        models = LLMFactory.list_available_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "gpt-4" in models
        assert "claude-3.5-sonnet" in models

    def test_get_model_config(self):
        """测试获取模型配置"""
        from src.llm import LLMFactory

        config = LLMFactory.get_model_config("gpt-4")
        assert config.name == "GPT-4"
        assert config.provider.value == "openai"

    def test_get_model_cost(self):
        """测试成本计算"""
        from src.llm import LLMFactory

        # 测试 GPT-4 成本
        cost = LLMFactory.get_model_cost("gpt-4", input_tokens=1000, output_tokens=500)
        expected = (1000 * 0.03 / 1_000_000) + (500 * 0.06 / 1_000_000)
        assert abs(cost - expected) < 1e-9

        # 测试带缓存的成本
        cost_with_cache = LLMFactory.get_model_cost(
            "gpt-4",
            input_tokens=1000,
            output_tokens=500,
            cache_read_tokens=200
        )
        expected_cache = (1000 * 0.03 / 1_000_000) + (500 * 0.06 / 1_000_000) + (200 * 0.0075 / 1_000_000)
        assert abs(cost_with_cache - expected_cache) < 1e-9

    def test_create_model(self):
        """测试创建模型实例（需要 API Key）"""
        from src.llm import LLMFactory

        # 这个测试需要实际的 API Key，所以只是验证不会崩溃
        # 在没有 API Key 的情况下会抛出异常
        try:
            llm = LLMFactory.create_model("gpt-4")
            assert llm is not None
        except ValueError as e:
            # 如果没有 API Key，这是预期的
            assert "API key" in str(e).lower()


class TestLangGraphWorkflow:
    """测试 Phase 1.3: LangGraph 工作流"""

    def test_module_import(self):
        """测试模块导入"""
        from src.workflows.conversation import ConversationWorkflow, ConversationState
        assert ConversationWorkflow is not None
        assert ConversationState is not None

    def test_conversation_workflow_init(self):
        """测试对话工作流初始化"""
        from src.workflows.conversation import ConversationWorkflow

        workflow = ConversationWorkflow()
        assert workflow is not None
        assert hasattr(workflow, 'workflow')
        assert hasattr(workflow, 'is_available')

    def test_conversation_state_structure(self):
        """测试对话状态结构"""
        from src.workflows.conversation import ConversationState
        from typing import get_type_hints

        # 检查状态包含所有必要字段
        state: ConversationState = {
            "user_message": "test",
            "conversation_history": [],
            "messages": [],
            "intent": "",
            "user_requirements": {},
            "search_query": None,
            "search_results": None,
            "search_executed": False,
            "recommend_parameters": None,
            "recommendations": None,
            "recommend_executed": False,
            "booking_details": None,
            "booking_confirmed": False,
            "booking_result": None,
            "response": "",
            "workflow_status": "active",
            "error_message": None,
            "cost_tokens": {}
        }

        assert state["user_message"] == "test"
        assert state["workflow_status"] == "active"

    def test_node_imports(self):
        """测试节点导入"""
        from src.workflows.conversation.nodes import (
            process_entry,
            route_intent,
            should_route,
            plan_search,
            execute_search,
            plan_recommend,
            execute_recommend,
            plan_booking,
            execute_booking,
            generate_response
        )

        assert callable(process_entry)
        assert callable(route_intent)
        assert callable(should_route)
        assert callable(plan_search)
        assert callable(execute_search)
        assert callable(plan_recommend)
        assert callable(execute_recommend)
        assert callable(plan_booking)
        assert callable(execute_booking)
        assert callable(generate_response)


class TestDeepAgentSubagents:
    """测试 Phase 1.4: DeepAgent 子智能体"""

    def test_module_import(self):
        """测试模块导入"""
        from src.agents.subagents import SearchAgent, RecommendationAgent, BookingAgent
        assert SearchAgent is not None
        assert RecommendationAgent is not None
        assert BookingAgent is not None

    def test_base_agent(self):
        """测试基础 Agent 类"""
        from src.agents.subagents.base import BaseAgent

        assert hasattr(BaseAgent, 'name')
        assert hasattr(BaseAgent, 'description')
        assert hasattr(BaseAgent, 'tools')
        assert hasattr(BaseAgent, 'execute')
        assert hasattr(BaseAgent, 'stream')
        assert hasattr(BaseAgent, '_track_tokens')

    def test_search_agent_init(self):
        """测试搜索智能体初始化"""
        from src.agents.subagents import SearchAgent

        agent = SearchAgent(llm=None)
        assert agent.name == "SearchAgent"
        assert agent.description == "旅游搜索专家，擅长搜索航班、酒店和景点信息"
        assert agent.tools == []

    def test_recommendation_agent_init(self):
        """测试推荐智能体初始化"""
        from src.agents.subagents import RecommendationAgent

        agent = RecommendationAgent(llm=None)
        assert agent.name == "RecommendationAgent"
        assert agent.description == "旅游推荐专家，擅长个性化行程规划和预算建议"
        assert agent.tools == []

    def test_booking_agent_init(self):
        """测试预订智能体初始化"""
        from src.agents.subagents import BookingAgent

        agent = BookingAgent(llm=None)
        assert agent.name == "BookingAgent"
        assert agent.description == "旅游预订专家，擅长航班、酒店、门票预订服务"
        assert agent.tools == []

    def test_tools_import(self):
        """测试工具导入"""
        from src.agents.subagents.tools import (
            search_flights,
            search_hotels,
            search_attractions,
            generate_itinerary,
            calculate_budget,
            recommend_experiences,
            book_flight,
            book_hotel,
            book_ticket
        )

        assert callable(search_flights)
        assert callable(search_hotels)
        assert callable(search_attractions)
        assert callable(generate_itinerary)
        assert callable(calculate_budget)
        assert callable(recommend_experiences)
        assert callable(book_flight)
        assert callable(book_hotel)
        assert callable(book_ticket)


class TestIntegration:
    """测试三层架构集成"""

    def test_full_integration(self):
        """测试完整集成"""
        # 导入所有模块
        from src.llm import LLMFactory
        from src.workflows.conversation import ConversationWorkflow
        from src.agents.subagents import SearchAgent, RecommendationAgent, BookingAgent

        # 创建工作流
        workflow = ConversationWorkflow()
        assert workflow is not None

        # 创建子智能体
        search_agent = SearchAgent(llm=None)
        recommend_agent = RecommendationAgent(llm=None)
        booking_agent = BookingAgent(llm=None)

        assert search_agent is not None
        assert recommend_agent is not None
        assert booking_agent is not None

        print("✓ 三层架构集成测试通过")

    def test_architecture_layers(self):
        """测试三层架构各层"""
        # 第一层：多模型接口
        from src.llm import LLMFactory, MODELS
        assert len(MODELS) >= 6  # 至少6个模型

        # 第二层：工作流编排
        from src.workflows.conversation import (
            ConversationWorkflow,
            process_entry,
            route_intent,
            generate_response
        )
        assert ConversationWorkflow is not None
        assert callable(process_entry)
        assert callable(route_intent)
        assert callable(generate_response)

        # 第三层：子智能体
        from src.agents.subagents import SearchAgent, RecommendationAgent, BookingAgent
        assert SearchAgent is not None
        assert RecommendationAgent is not None
        assert BookingAgent is not None

        print("✓ 三层架构各层测试通过")


class TestFileStructure:
    """测试文件结构完整性"""

    def test_llm_module_structure(self):
        """测试 LLM 模块文件结构"""
        import os

        llm_dir = os.path.join(os.path.dirname(__file__), 'src/llm')
        required_files = [
            '__init__.py',
            'models.py',
            'factory.py',
            'base.py'
        ]

        for file in required_files:
            file_path = os.path.join(llm_dir, file)
            assert os.path.exists(file_path), f"LLM module file missing: {file}"

        print("✓ LLM 模块文件结构完整")

    def test_workflow_module_structure(self):
        """测试工作流模块文件结构"""
        import os

        workflow_dir = os.path.join(os.path.dirname(__file__), 'src/workflows/conversation')
        required_files = [
            '__init__.py',
            'conversation.py',
            'state.py'
        ]

        for file in required_files:
            file_path = os.path.join(workflow_dir, file)
            assert os.path.exists(file_path), f"Workflow module file missing: {file}"

        # 检查 nodes 子目录
        nodes_dir = os.path.join(workflow_dir, 'nodes')
        required_node_files = [
            '__init__.py',
            'entry.py',
            'router.py',
            'search.py',
            'recommend.py',
            'booking.py',
            'response.py'
        ]

        for file in required_node_files:
            file_path = os.path.join(nodes_dir, file)
            assert os.path.exists(file_path), f"Workflow node file missing: {file}"

        print("✓ 工作流模块文件结构完整")

    def test_subagents_module_structure(self):
        """测试子智能体模块文件结构"""
        import os

        subagents_dir = os.path.join(os.path.dirname(__file__), 'src/agents/subagents')
        required_files = [
            '__init__.py',
            'base.py',
            'search_agent.py',
            'recommend_agent.py',
            'booking_agent.py'
        ]

        for file in required_files:
            file_path = os.path.join(subagents_dir, file)
            assert os.path.exists(file_path), f"Subagent module file missing: {file}"

        # 检查 tools 子目录
        tools_dir = os.path.join(subagents_dir, 'tools')
        required_tool_files = [
            '__init__.py',
            'search_tools.py',
            'recommend_tools.py',
            'booking_tools.py'
        ]

        for file in required_tool_files:
            file_path = os.path.join(tools_dir, file)
            assert os.path.exists(file_path), f"Subagent tool file missing: {file}"

        print("✓ 子智能体模块文件结构完整")


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("运行完整的三层架构测试")
    print("=" * 80)

    test_classes = [
        ("Phase 1.2: 多模型统一接口", TestMultiModelInterface),
        ("Phase 1.3: LangGraph 工作流", TestLangGraphWorkflow),
        ("Phase 1.4: DeepAgent 子智能体", TestDeepAgentSubagents),
        ("集成测试", TestIntegration),
        ("文件结构测试", TestFileStructure)
    ]

    total_tests = 0
    passed_tests = 0

    for phase_name, test_class in test_classes:
        print(f"\n{'=' * 80}")
        print(f"{phase_name}")
        print(f"{'=' * 80}")

        test_instance = test_class()

        # 获取所有测试方法
        test_methods = [m for m in dir(test_instance) if m.startswith('test_')]

        for test_method_name in test_methods:
            total_tests += 1
            test_method = getattr(test_instance, test_method_name)

            try:
                print(f"  [测试] {test_method_name}...", end=" ")
                test_method()
                print("✓ 通过")
                passed_tests += 1
            except AssertionError as e:
                print(f"✗ 失败: {e}")
            except Exception as e:
                print(f"✗ 错误: {e}")

    print(f"\n{'=' * 80}")
    print(f"测试结果: {passed_tests}/{total_tests} 通过")
    print(f"{'=' * 80}")

    return passed_tests, total_tests


if __name__ == "__main__":
    passed, total = run_all_tests()
    sys.exit(0 if passed == total else 1)
