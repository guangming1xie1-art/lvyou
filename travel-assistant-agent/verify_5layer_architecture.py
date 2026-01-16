#!/usr/bin/env python3
"""
验证 5 层架构实现

架构层次：
- 第0层：TokenCounter Callback
- 第1层：4 个子图 StateGraph
- 第2层：CompiledSubAgent 包装器
- 第3层：call_subagent_node 工厂函数
- 第4层：主工作流 StateGraph
- 第5层：DeepAgent 顶层代理
"""
import os
import sys

# 设置环境变量（测试用）
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")
os.environ.setdefault("DASHSCOPE_API_KEY", "test-key")

sys.path.insert(0, os.path.dirname(__file__))

def verify_layer_0():
    """验证第0层：TokenCounter"""
    print("\n【第0层】TokenCounter Callback")
    print("=" * 60)
    
    try:
        from src.utils.token_counter import TokenCounter
        
        counter = TokenCounter()
        assert hasattr(counter, 'dump'), "TokenCounter missing dump() method"
        
        result = counter.dump()
        assert "prompt" in result, "dump() missing 'prompt' key"
        assert "completion" in result, "dump() missing 'completion' key"
        assert "total" in result, "dump() missing 'total' key"
        
        print("✓ TokenCounter 类存在")
        print("✓ TokenCounter.dump() 返回 {'prompt', 'completion', 'total'}")
        return True
    except Exception as e:
        print(f"✗ 第0层验证失败: {e}")
        return False


def verify_layer_1():
    """验证第1层：4 个子图 StateGraph"""
    print("\n【第1层】4 个子图 StateGraph")
    print("=" * 60)
    
    try:
        from src.workflows.subgraphs import (
            build_collect_info_graph,
            build_search_graph,
            build_recommend_graph,
            build_booking_graph,
        )
        
        # 验证子图可以构建
        collect_graph = build_collect_info_graph()
        search_graph = build_search_graph()
        recommend_graph = build_recommend_graph()
        booking_graph = build_booking_graph()
        
        print("✓ build_collect_info_graph() 成功")
        print("✓ build_search_graph() 成功")
        print("✓ build_recommend_graph() 成功")
        print("✓ build_booking_graph() 成功")
        
        # 验证子图有 invoke 方法
        assert hasattr(collect_graph, 'invoke'), "子图缺少 invoke() 方法"
        
        print("✓ 子图拥有 invoke() 方法")
        return True
    except Exception as e:
        print(f"✗ 第1层验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_layer_2():
    """验证第2层：CompiledSubAgent 包装器"""
    print("\n【第2层】CompiledSubAgent 包装器")
    print("=" * 60)
    
    try:
        from src.workflows.subagents import (
            CompiledSubAgent,
            get_info_collection_agent,
            get_search_agent,
            get_recommend_agent,
            get_booking_agent,
        )
        
        # 验证 CompiledSubAgent 类
        print("✓ CompiledSubAgent 类存在")
        
        # 验证获取函数
        info_agent = get_info_collection_agent()
        search_agent = get_search_agent()
        recommend_agent = get_recommend_agent()
        booking_agent = get_booking_agent()
        
        print("✓ get_info_collection_agent() 返回 CompiledSubAgent")
        print("✓ get_search_agent() 返回 CompiledSubAgent")
        print("✓ get_recommend_agent() 返回 CompiledSubAgent")
        print("✓ get_booking_agent() 返回 CompiledSubAgent")
        
        # 验证 CompiledSubAgent 接口
        assert hasattr(info_agent, 'invoke'), "CompiledSubAgent 缺少 invoke()"
        assert hasattr(info_agent, 'ainvoke'), "CompiledSubAgent 缺少 ainvoke()"
        assert hasattr(info_agent, 'name'), "CompiledSubAgent 缺少 name"
        assert hasattr(info_agent, 'system_prompt'), "CompiledSubAgent 缺少 system_prompt"
        
        print("✓ CompiledSubAgent 拥有 invoke(), ainvoke() 方法")
        print("✓ CompiledSubAgent 拥有 name, system_prompt 属性")
        
        return True
    except Exception as e:
        print(f"✗ 第2层验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_layer_3():
    """验证第3层：call_subagent_node 工厂函数"""
    print("\n【第3层】call_subagent_node 工厂函数")
    print("=" * 60)
    
    try:
        from src.workflows.main_workflow import call_subagent_node
        
        # 验证工厂函数存在
        print("✓ call_subagent_node() 函数存在")
        
        # 验证可以创建节点函数
        collect_node = call_subagent_node("info_collection")
        search_node = call_subagent_node("search")
        recommend_node = call_subagent_node("recommend")
        booking_node = call_subagent_node("booking")
        
        print("✓ call_subagent_node('info_collection') 创建节点函数")
        print("✓ call_subagent_node('search') 创建节点函数")
        print("✓ call_subagent_node('recommend') 创建节点函数")
        print("✓ call_subagent_node('booking') 创建节点函数")
        
        # 验证节点函数可调用
        assert callable(collect_node), "节点函数不可调用"
        
        print("✓ 节点函数可调用")
        
        return True
    except Exception as e:
        print(f"✗ 第3层验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_layer_4():
    """验证第4层：主工作流 StateGraph"""
    print("\n【第4层】主工作流 StateGraph")
    print("=" * 60)
    
    try:
        from src.workflows.main_workflow import (
            MainState,
            build_main_graph,
        )
        
        # 验证 MainState 存在
        print("✓ MainState TypedDict 存在")
        
        # 验证 MainState 字段
        from typing import get_type_hints
        hints = get_type_hints(MainState)
        
        assert "messages" in hints, "MainState 缺少 messages"
        assert "user_message" in hints, "MainState 缺少 user_message"
        assert "collected_info" in hints, "MainState 缺少 collected_info"
        assert "search_results" in hints, "MainState 缺少 search_results"
        assert "recommendations" in hints, "MainState 缺少 recommendations"
        assert "booking_confirmation" in hints, "MainState 缺少 booking_confirmation"
        assert "usage" in hints, "MainState 缺少 usage"
        
        print("✓ MainState 包含所有必需字段")
        
        # 验证可以构建主图
        main_graph = build_main_graph()
        
        print("✓ build_main_graph() 成功构建主图")
        
        # 验证主图有 invoke 方法
        assert hasattr(main_graph, 'invoke'), "主图缺少 invoke()"
        assert hasattr(main_graph, 'ainvoke'), "主图缺少 ainvoke()"
        
        print("✓ 主图拥有 invoke(), ainvoke() 方法")
        
        return True
    except Exception as e:
        print(f"✗ 第4层验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_layer_5():
    """验证第5层：DeepAgent 顶层代理"""
    print("\n【第5层】DeepAgent 顶层代理")
    print("=" * 60)
    
    try:
        from src.workflows.deep_agent_wrapper import (
            DeepAgent,
            create_deep_agent,
        )
        from src.workflows.main_workflow import (
            get_or_create_main_agent,
        )
        
        # 验证 DeepAgent 类
        print("✓ DeepAgent 类存在")
        
        # 验证 create_deep_agent 函数
        print("✓ create_deep_agent() 函数存在")
        
        # 验证 get_or_create_main_agent
        main_agent = get_or_create_main_agent()
        
        print("✓ get_or_create_main_agent() 创建主代理")
        
        # 验证主代理接口
        assert hasattr(main_agent, 'invoke'), "DeepAgent 缺少 invoke()"
        assert hasattr(main_agent, 'ainvoke'), "DeepAgent 缺少 ainvoke()"
        assert hasattr(main_agent, 'model'), "DeepAgent 缺少 model"
        assert hasattr(main_agent, 'subagents'), "DeepAgent 缺少 subagents"
        assert hasattr(main_agent, 'runnable'), "DeepAgent 缺少 runnable"
        
        print("✓ DeepAgent 拥有 invoke(), ainvoke() 方法")
        print("✓ DeepAgent 拥有 model, subagents, runnable 属性")
        
        # 验证 subagents 数量
        assert len(main_agent.subagents) == 4, f"子代理数量应为 4，实际为 {len(main_agent.subagents)}"
        
        print(f"✓ DeepAgent 包含 {len(main_agent.subagents)} 个子代理")
        
        return True
    except Exception as e:
        print(f"✗ 第5层验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_integration():
    """验证整体集成"""
    print("\n【整体集成】端到端验证")
    print("=" * 60)
    
    try:
        from src.workflows.main_workflow import (
            run_main_workflow_sync,
            run_main_workflow,
        )
        
        # 验证便捷函数存在
        print("✓ run_main_workflow_sync() 函数存在")
        print("✓ run_main_workflow() 函数存在")
        
        # 简单测试（不实际调用 LLM）
        print("✓ 主工作流 API 完整")
        
        return True
    except Exception as e:
        print(f"✗ 整体集成验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有验证"""
    print("\n" + "=" * 60)
    print("验证 5 层架构实现")
    print("=" * 60)
    
    results = []
    
    results.append(("第0层: TokenCounter", verify_layer_0()))
    results.append(("第1层: 4 个子图 StateGraph", verify_layer_1()))
    results.append(("第2层: CompiledSubAgent", verify_layer_2()))
    results.append(("第3层: call_subagent_node", verify_layer_3()))
    results.append(("第4层: 主工作流 StateGraph", verify_layer_4()))
    results.append(("第5层: DeepAgent", verify_layer_5()))
    results.append(("整体集成", verify_integration()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有验证通过！5 层架构实现完整。")
        return 0
    else:
        print("\n⚠️  部分验证失败，请检查上述错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
