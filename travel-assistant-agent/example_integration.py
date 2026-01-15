"""
三层架构集成示例
演示如何将 LLM 接口、LangGraph 工作流、DeepAgent 子智能体整合使用
"""
import asyncio
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def example_simple_workflow():
    """简单的工作流示例"""
    print("=" * 80)
    print("示例 1: 使用对话工作流")
    print("=" * 80)

    from src.workflows.conversation import ConversationWorkflow

    # 创建工作流
    workflow = ConversationWorkflow()

    # 测试不同类型的消息
    test_messages = [
        "搜索北京的景点",
        "推荐上海5天的旅游行程",
        "预订明天去广州的机票"
    ]

    for message in test_messages:
        print(f"\n用户消息: {message}")
        print("-" * 80)

        try:
            # 执行工作流
            result = await workflow.invoke(message)

            # 输出结果
            print(f"意图: {result.get('intent', 'N/A')}")
            print(f"状态: {result.get('workflow_status', 'N/A')}")
            print(f"\n回复:\n{result.get('response', 'N/A')}")

            if result.get('error_message'):
                print(f"\n错误: {result['error_message']}")

        except Exception as e:
            print(f"执行失败: {str(e)}")

        print()


async def example_subagent_direct():
    """直接使用子智能体的示例"""
    print("=" * 80)
    print("示例 2: 直接使用子智能体")
    print("=" * 80)

    from src.agents.subagents import SearchAgent, RecommendationAgent, BookingAgent

    # 创建智能体
    search_agent = SearchAgent(llm=None)
    recommend_agent = RecommendationAgent(llm=None)
    booking_agent = BookingAgent(llm=None)

    # 1. 搜索
    print("\n1. 搜索任务")
    print("-" * 80)
    search_input = {
        "user_requirements": {
            "destination": "北京",
            "duration_days": 5
        },
        "user_message": "搜索北京的旅游信息"
    }

    search_result = await search_agent.execute(search_input)
    print(f"搜索结果: {len(search_result.get('search_results', {}).get('flights', []))} 个航班, "
          f"{len(search_result.get('search_results', {}).get('hotels', []))} 家酒店, "
          f"{len(search_result.get('search_results', {}).get('attractions', []))} 个景点")

    # 2. 推荐
    print("\n2. 推荐任务")
    print("-" * 80)
    recommend_input = {
        "user_requirements": {
            "destination": "北京",
            "duration_days": 5,
            "budget": 5000
        },
        "search_results": search_result.get("search_results", {})
    }

    recommend_result = await recommend_agent.execute(recommend_input)
    print(f"推荐结果: {len(recommend_result.get('recommendations', {}))} 个推荐类别")

    # 3. 预订
    print("\n3. 预订任务")
    print("-" * 80)
    booking_input = {
        "booking_details": {
            "destination": "北京",
            "travel_date": "2024-06-01",
            "passengers": 1,
            "duration_days": 5
        },
        "recommendations": recommend_result.get("recommendations", {})
    }

    booking_result = await booking_agent.execute(booking_input)
    print(f"预订结果: {'成功' if booking_result.get('booking_result', {}).get('confirmed') else '失败'}")
    if booking_result.get('booking_result'):
        print(f"预订编号: {booking_result['booking_result'].get('booking_id', 'N/A')}")
        print(f"总价: ¥{booking_result['booking_result'].get('total_price', 0):.2f}")


async def example_streaming_subagent():
    """流式执行子智能体的示例"""
    print("\n" + "=" * 80)
    print("示例 3: 流式执行子智能体")
    print("=" * 80)

    from src.agents.subagents import RecommendationAgent

    # 创建推荐智能体
    recommend_agent = RecommendationAgent(llm=None)

    # 流式执行
    recommend_input = {
        "user_requirements": {
            "destination": "杭州",
            "duration_days": 3,
            "budget": 3000
        },
        "search_results": {}
    }

    print("\n流式执行推荐任务...")
    print("-" * 80)

    async for chunk in recommend_agent.stream(recommend_input):
        chunk_type = chunk.get("type", "unknown")
        message = chunk.get("message", "")

        if chunk_type == "progress":
            print(f"[进度] {message}")
        elif chunk_type == "result":
            category = chunk.get("category", "")
            print(f"[结果] {category}: {str(chunk.get('data', {}))[:100]}...")
        elif chunk_type == "completed":
            print(f"[完成] {message}")
        elif chunk_type == "error":
            print(f"[错误] {message}")

    print()


async def example_llm_factory():
    """LLM 工厂示例"""
    print("\n" + "=" * 80)
    print("示例 4: 使用 LLM 工厂")
    print("=" * 80)

    from src.llm import LLMFactory

    # 1. 列出所有可用模型
    print("\n1. 可用模型列表")
    print("-" * 80)
    models = LLMFactory.list_available_models()
    print(f"共 {len(models)} 个模型:")
    for i, model in enumerate(models, 1):
        config = LLMFactory.get_model_config(model)
        print(f"  {i}. {model} ({config.display_name}) - {config.provider.value}")

    # 2. 获取模型配置
    print("\n2. 模型配置详情")
    print("-" * 80)
    model_name = "gpt-4"
    config = LLMFactory.get_model_config(model_name)
    print(f"模型: {model_name}")
    print(f"  显示名称: {config.display_name}")
    print(f"  提供商: {config.provider.value}")
    print(f"  模型 ID: {config.model_id}")
    print(f"  API 基础 URL: {config.base_url}")
    print(f"  最大 Tokens: {config.max_tokens}")
    print(f"  温度: {config.temperature}")
    print(f"  输入成本: ${config.input_cost}/1M tokens")
    print(f"  输出成本: ${config.output_cost}/1M tokens")

    # 3. 计算成本
    print("\n3. 成本计算")
    print("-" * 80)
    input_tokens = 1000
    output_tokens = 500
    cache_read_tokens = 200

    cost = LLMFactory.get_model_cost(
        model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read_tokens
    )

    print(f"模型: {model_name}")
    print(f"  输入 Tokens: {input_tokens}")
    print(f"  输出 Tokens: {output_tokens}")
    print(f"  缓存读取 Tokens: {cache_read_tokens}")
    print(f"  总成本: ${cost:.6f}")

    # 4. 比较不同模型的成本
    print("\n4. 模型成本对比（1000 输入 + 500 输出 tokens）")
    print("-" * 80)
    models_to_compare = ["gpt-4", "claude-3.5-sonnet", "deepseek-v3", "glm-4"]

    print(f"{'模型':<25} {'提供商':<15} {'成本':<15}")
    print("-" * 55)

    for model in models_to_compare:
        try:
            config = LLMFactory.get_model_config(model)
            cost = LLMFactory.get_model_cost(model, 1000, 500)
            print(f"{model:<25} {config.provider.value:<15} ${cost:.6f}")
        except ValueError:
            print(f"{model:<25} {'N/A':<15} {'N/A':<15}")


async def example_full_integration():
    """完整集成示例"""
    print("\n" + "=" * 80)
    print("示例 5: 完整三层架构集成")
    print("=" * 80)

    print("\n架构层次:")
    print("  第一层: LLM 多模型接口 (src/llm/)")
    print("  第二层: LangGraph 工作流 (src/workflows/conversation/)")
    print("  第三层: DeepAgent 子智能体 (src/agents/subagents/)")
    print()

    from src.llm import LLMFactory
    from src.workflows.conversation import ConversationWorkflow
    from src.agents.subagents import SearchAgent, RecommendationAgent, BookingAgent

    # 初始化
    print("初始化三层架构...")
    print("-" * 80)

    # 第一层：获取可用模型
    models = LLMFactory.list_available_models()
    print(f"✓ 第一层: 加载了 {len(models)} 个模型配置")

    # 第二层：创建工作流
    workflow = ConversationWorkflow()
    print(f"✓ 第二层: 创建了对话工作流 (可用: {workflow.is_available})")

    # 第三层：创建子智能体
    search_agent = SearchAgent(llm=None)
    recommend_agent = RecommendationAgent(llm=None)
    booking_agent = BookingAgent(llm=None)
    print(f"✓ 第三层: 创建了 3 个子智能体")

    print("\n执行完整流程:")
    print("-" * 80)

    user_message = "我想去成都旅游3天，预算4000元"
    print(f"用户: {user_message}\n")

    # 使用工作流处理
    result = await workflow.invoke(user_message)

    print(f"工作流结果:")
    print(f"  意图: {result.get('intent', 'N/A')}")
    print(f"  状态: {result.get('workflow_status', 'N/A')}")
    print(f"\n{result.get('response', 'N/A')}")

    print("\n" + "=" * 80)
    print("✓ 完整集成演示完成")
    print("=" * 80)


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("三层架构集成示例")
    print("=" * 80)
    print()

    try:
        # 运行各个示例
        await example_llm_factory()
        await example_simple_workflow()
        await example_subagent_direct()
        await example_streaming_subagent()
        await example_full_integration()

        print("\n" + "=" * 80)
        print("所有示例运行完成！")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
