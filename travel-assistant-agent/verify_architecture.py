"""
简化的架构验证脚本
验证三层架构的文件结构完整性，不需要依赖项
"""
import os
import sys


def verify_file_exists(filepath, description):
    """验证文件是否存在"""
    if os.path.exists(filepath):
        print(f"  ✓ {description}")
        return True
    else:
        print(f"  ✗ 缺失: {description}")
        return False


def main():
    print("=" * 80)
    print("三层架构完整性验证")
    print("=" * 80)

    total_files = 0
    passed_files = 0

    # Phase 1.2: 多模型统一接口
    print("\nPhase 1.2: 多模型统一接口 (LLM)")
    print("-" * 80)

    llm_files = {
        "src/llm/__init__.py": "LLM 模块初始化",
        "src/llm/models.py": "模型配置数据类",
        "src/llm/factory.py": "LLM 工厂类",
        "src/llm/base.py": "LLM 基础模块"
    }

    for filepath, description in llm_files.items():
        total_files += 1
        if verify_file_exists(filepath, description):
            passed_files += 1

    # Phase 1.3: LangGraph 工作流
    print("\nPhase 1.3: LangGraph 工作流")
    print("-" * 80)

    workflow_files = {
        "src/workflows/conversation/__init__.py": "对话工作流初始化",
        "src/workflows/conversation/conversation.py": "对话工作流主文件",
        "src/workflows/conversation/state.py": "工作流状态定义",
        "src/workflows/conversation/nodes/__init__.py": "节点模块初始化",
        "src/workflows/conversation/nodes/entry.py": "入口节点",
        "src/workflows/conversation/nodes/router.py": "路由节点",
        "src/workflows/conversation/nodes/search.py": "搜索节点",
        "src/workflows/conversation/nodes/recommend.py": "推荐节点",
        "src/workflows/conversation/nodes/booking.py": "预订节点",
        "src/workflows/conversation/nodes/response.py": "响应节点"
    }

    for filepath, description in workflow_files.items():
        total_files += 1
        if verify_file_exists(filepath, description):
            passed_files += 1

    # Phase 1.4: DeepAgent 子智能体
    print("\nPhase 1.4: DeepAgent 子智能体")
    print("-" * 80)

    subagent_files = {
        "src/agents/subagents/__init__.py": "子智能体模块初始化",
        "src/agents/subagents/base.py": "子智能体基类",
        "src/agents/subagents/search_agent.py": "搜索智能体",
        "src/agents/subagents/recommend_agent.py": "推荐智能体",
        "src/agents/subagents/booking_agent.py": "预订智能体",
        "src/agents/subagents/tools/__init__.py": "工具模块初始化",
        "src/agents/subagents/tools/search_tools.py": "搜索工具",
        "src/agents/subagents/tools/recommend_tools.py": "推荐工具",
        "src/agents/subagents/tools/booking_tools.py": "预订工具"
    }

    for filepath, description in subagent_files.items():
        total_files += 1
        if verify_file_exists(filepath, description):
            passed_files += 1

    # 验证配置文件
    print("\n配置文件")
    print("-" * 80)

    config_files = {
        ".env.example": "环境变量示例文件"
    }

    for filepath, description in config_files.items():
        total_files += 1
        if verify_file_exists(filepath, description):
            passed_files += 1

    # 验证内容
    print("\n内容验证")
    print("-" * 80)

    # 验证 models.py 包含所有模型
    models_path = "src/llm/models.py"
    if os.path.exists(models_path):
        with open(models_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_models = [
            'gpt-4',
            'gpt-4-turbo',
            'claude-3.5-sonnet',
            'claude-3-opus',
            'qwen-max',
            'deepseek-v3',
            'glm-4'
        ]

        for model in required_models:
            total_files += 1
            if model in content:
                print(f"  ✓ 模型配置包含: {model}")
                passed_files += 1
            else:
                print(f"  ✗ 模型配置缺失: {model}")

    # 验证 nodes 包含所有节点
    nodes_path = "src/workflows/conversation/nodes/__init__.py"
    if os.path.exists(nodes_path):
        with open(nodes_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_nodes = [
            'process_entry',
            'route_intent',
            'should_route',
            'plan_search',
            'execute_search',
            'plan_recommend',
            'execute_recommend',
            'plan_booking',
            'execute_booking',
            'generate_response'
        ]

        for node in required_nodes:
            total_files += 1
            if node in content:
                print(f"  ✓ 节点导出: {node}")
                passed_files += 1
            else:
                print(f"  ✗ 节点导出缺失: {node}")

    # 验证 subagents 包含所有智能体
    subagents_path = "src/agents/subagents/__init__.py"
    if os.path.exists(subagents_path):
        with open(subagents_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_agents = [
            'SearchAgent',
            'RecommendationAgent',
            'BookingAgent'
        ]

        for agent in required_agents:
            total_files += 1
            if agent in content:
                print(f"  ✓ 智能体导出: {agent}")
                passed_files += 1
            else:
                print(f"  ✗ 智能体导出缺失: {agent}")

    # 验证 tools 包含所有工具
    tools_path = "src/agents/subagents/tools/__init__.py"
    if os.path.exists(tools_path):
        with open(tools_path, 'r', encoding='utf-8') as f:
            content = f.read()

        required_tools = [
            'search_flights',
            'search_hotels',
            'search_attractions',
            'generate_itinerary',
            'calculate_budget',
            'recommend_experiences',
            'book_flight',
            'book_hotel',
            'book_ticket'
        ]

        for tool in required_tools:
            total_files += 1
            if tool in content:
                print(f"  ✓ 工具导出: {tool}")
                passed_files += 1
            else:
                print(f"  ✗ 工具导出缺失: {tool}")

    # 最终结果
    print("\n" + "=" * 80)
    print(f"验证结果: {passed_files}/{total_files} 通过")
    if passed_files == total_files:
        print("✓ 所有检查通过！三层架构实现完整。")
    else:
        print(f"✗ {total_files - passed_files} 项检查失败")
    print("=" * 80)

    return passed_files == total_files


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
