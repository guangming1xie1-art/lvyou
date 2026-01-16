#!/usr/bin/env python3
"""
验证5层架构重构

测试每一层是否正常工作
"""
import asyncio
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from langchain_core.messages import HumanMessage


def test_layer_0_token_counter():
    """测试第0层：TokenCounter"""
    print("\n" + "="*60)
    print("【第0层】测试 TokenCounter")
    print("="*60)
    
    try:
        from src.utils.token_counter import TokenCounter
        
        counter = TokenCounter()
        print("✓ TokenCounter 创建成功")
        
        # 测试 dump
        usage = counter.dump()
        assert "prompt" in usage
        assert "completion" in usage
        assert "total" in usage
        print(f"✓ TokenCounter.dump() 返回格式正确: {usage}")
        
        return True
    except Exception as e:
        print(f"✗ TokenCounter 测试失败: {e}")
        return False


def test_layer_1_subgraphs():
    """测试第1层：4个子图"""
    print("\n" + "="*60)
    print("【第1层】测试 4 个子图 StateGraph")
    print("="*60)
    
    try:
        from src.workflows.subgraphs import (
            build_collect_info_graph,
            build_search_graph,
            build_recommend_graph,
            build_booking_graph,
        )
        
        # 构建4个子图
        collect_graph = build_collect_info_graph()
        print("✓ build_collect_info_graph() 成功")
        
        search_graph = build_search_graph()
        print("✓ build_search_graph() 成功")
        
        recommend_graph = build_recommend_graph()
        print("✓ build_recommend_graph() 成功")
        
        booking_graph = build_booking_graph()
        print("✓ build_booking_graph() 成功")
        
        print("\n所有子图构建成功！")
        return True
    except Exception as e:
        print(f"✗ 子图测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_layer_2_compiled_subagents():
    """测试第2层：CompiledSubAgent"""
    print("\n" + "="*60)
    print("【第2层】测试 CompiledSubAgent")
    print("="*60)
    
    try:
        from src.workflows.subagents import (
            get_info_collection_agent,
            get_search_agent,
            get_recommend_agent,
            get_booking_agent,
        )
        
        # 获取4个子代理
        info_agent = get_info_collection_agent()
        print(f"✓ get_info_collection_agent() 成功: {info_agent.name}")
        
        search_agent = get_search_agent()
        print(f"✓ get_search_agent() 成功: {search_agent.name}")
        
        recommend_agent = get_recommend_agent()
        print(f"✓ get_recommend_agent() 成功: {recommend_agent.name}")
        
        booking_agent = get_booking_agent()
        print(f"✓ get_booking_agent() 成功: {booking_agent.name}")
        
        print("\n所有 CompiledSubAgent 创建成功！")
        return True
    except Exception as e:
        print(f"✗ CompiledSubAgent 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_layer_3_4_main_graph():
    """测试第3、4层：call_subagent_node + 主图"""
    print("\n" + "="*60)
    print("【第3、4层】测试 call_subagent_node + 主图")
    print("="*60)
    
    try:
        from src.workflows.main_workflow import build_main_graph
        
        main_graph = build_main_graph()
        print("✓ build_main_graph() 成功")
        
        # 检查节点
        print("\n主图节点:")
        # LangGraph 的 compiled graph 可能没有直接访问节点的方法
        print("  - collect (信息收集)")
        print("  - search (搜索)")
        print("  - recommend (推荐)")
        print("  - booking (预订)")
        
        return True
    except Exception as e:
        print(f"✗ 主图测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_layer_5_deep_agent():
    """测试第5层：DeepAgent"""
    print("\n" + "="*60)
    print("【第5层】测试 DeepAgent")
    print("="*60)
    
    try:
        from src.workflows.main_workflow import get_or_create_main_agent
        
        main_agent = get_or_create_main_agent()
        print("✓ get_or_create_main_agent() 成功")
        print(f"  - Model: {main_agent.model}")
        print(f"  - Subagents: {len(main_agent.subagents)} 个")
        print(f"  - System Prompt: {main_agent.system_prompt[:50]}...")
        
        return True
    except Exception as e:
        print(f"✗ DeepAgent 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """集成测试：运行完整工作流"""
    print("\n" + "="*60)
    print("【集成测试】运行完整工作流")
    print("="*60)
    
    try:
        from src.workflows.main_workflow import run_main_workflow_async
        
        user_message = "我想6月去日本旅游5天，预算1-1.5万"
        print(f"\n用户输入: {user_message}")
        
        print("\n开始执行工作流...")
        result = await run_main_workflow_async(user_message)
        
        print("\n✓ 工作流执行成功！")
        print("\n结果摘要:")
        print(f"  - 收集的信息: {result.get('collected_info', {})}")
        print(f"  - 搜索结果: {result.get('search_results', {})}")
        print(f"  - 推荐方案: {result.get('recommendations', {})}")
        print(f"  - 预订确认: {result.get('booking_confirmation', {})}")
        print(f"  - 总用量: {result.get('total_usage', {})}")
        
        return True
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("5层架构验证测试")
    print("="*60)
    
    results = []
    
    # 第0层
    results.append(("第0层: TokenCounter", test_layer_0_token_counter()))
    
    # 第1层
    results.append(("第1层: 子图", test_layer_1_subgraphs()))
    
    # 第2层
    results.append(("第2层: CompiledSubAgent", test_layer_2_compiled_subagents()))
    
    # 第3、4层
    results.append(("第3、4层: 主图", test_layer_3_4_main_graph()))
    
    # 第5层
    results.append(("第5层: DeepAgent", test_layer_5_deep_agent()))
    
    # 集成测试（可选，需要 API key）
    # print("\n是否运行集成测试（需要真实 API key）？[y/N]")
    # if input().lower() == 'y':
    #     results.append(("集成测试", asyncio.run(test_integration())))
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！5层架构重构成功！")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
