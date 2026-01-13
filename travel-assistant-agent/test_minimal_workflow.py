"""
简化混合工作流测试
测试基本功能，不依赖外部 API
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_minimal_workflow():
    """测试最小化工作流"""
    print("🚀 测试最小化混合工作流...")
    
    try:
        from workflows.minimal_workflow import get_minimal_workflow
        
        # 获取工作流实例
        workflow = await get_minimal_workflow()
        print("✅ 工作流实例创建成功")
        
        # 测试工作流运行
        test_message = "我想去北京旅行5天，预算3000元"
        result = await workflow.run(test_message)
        
        print("✅ 工作流运行完成")
        print(f"   - 状态: {result.get('status')}")
        print(f"   - 阶段: {result.get('stage')}")
        print(f"   - 错误: {result.get('error', 'None')}")
        print(f"   - 工作流路径: {result.get('workflow_path', [])}")
        
        # 检查结果
        if result.get('status') == 'completed':
            print("✅ 工作流成功完成")
            
            # 检查各个阶段的结果
            collected_info = result.get('collected_info', {})
            search_results = result.get('search_results', {})
            recommendations = result.get('recommendations', {})
            booking = result.get('booking_confirmation', {})
            
            print(f"   - 收集信息: {len(collected_info)} 项")
            print(f"   - 搜索结果: {search_results.get('search_quality', 0):.2f} 质量分")
            print(f"   - 推荐方案: {len(recommendations.get('recommendations', []))} 个")
            print(f"   - 预订状态: {booking.get('booking_status', 'None')}")
            
        else:
            print("❌ 工作流未成功完成")
            
        # 检查 token 报告
        token_report = result.get('token_report')
        if token_report:
            print(f"   - 总 token 数: {token_report.get('total_tokens', 0)}")
            print(f"   - 效率分数: {result.get('efficiency_score', 0):.2f}")
        
        return result.get('status') == 'completed'
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_workflow_components():
    """测试工作流组件"""
    print("\n🔧 测试工作流组件...")
    
    try:
        from workflows.minimal_workflow import MinimalHybridWorkflow, WorkflowState
        from utils.token_tracker import TokenTracker
        
        # 测试状态创建
        state = WorkflowState(
            user_message="测试消息",
            request_id="test_123"
        )
        print("✅ 状态对象创建成功")
        
        # 测试 Token 追踪器
        tracker = TokenTracker()
        tracker.start_request("test_request")
        tracker.start_node("test_node")
        tracker.end_node("test_node", input_tokens=100, output_tokens=200, success=True)
        
        report = tracker.generate_report()
        print(f"✅ Token 追踪器工作正常: {report['total_tokens']} tokens")
        
        # 测试工作流实例
        workflow = MinimalHybridWorkflow()
        print("✅ 工作流实例创建成功")
        
        # 测试条件分支函数
        test_state = WorkflowState(search_quality=0.8)
        decision = workflow._should_continue_after_search(test_state)
        print(f"✅ 高质量搜索决策: {decision}")
        
        test_state_low = WorkflowState(search_quality=0.3)
        decision_low = workflow._should_continue_after_search(test_state_low)
        print(f"✅ 低质量搜索决策: {decision_low}")
        
        # 测试错误重试逻辑
        should_retry = workflow._should_retry_error("网络超时")
        print(f"✅ 错误重试测试: '网络超时' -> {'可重试' if should_retry else '不可重试'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 组件测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_end_to_end():
    """端到端测试"""
    print("\n🌟 端到端测试...")
    
    try:
        from workflows.minimal_workflow import get_minimal_workflow
        
        workflow = await get_minimal_workflow()
        
        # 测试不同复杂度的请求
        test_cases = [
            ("简单请求", "去北京"),
            ("中等请求", "我想去东京旅行7天，预算10000元，喜欢文化景点"),
            ("复杂请求", "我计划去欧洲旅行15天，包括法国、意大利、德国，预算50000元，喜欢历史、文化、美食")
        ]
        
        for case_name, user_message in test_cases:
            print(f"\n   测试 {case_name}: {user_message[:50]}...")
            
            result = await workflow.run(user_message)
            
            if result.get('token_report'):
                token_report = result['token_report']
                efficiency = result.get('efficiency_score', 0)
                
                print(f"     - Token 使用: {token_report.get('total_tokens', 0)}")
                print(f"     - 执行时间: {token_report.get('total_execution_time_ms', 0):.0f}ms")
                print(f"     - 效率分数: {efficiency:.2f}")
                print(f"     - 节点数: {token_report.get('node_count', 0)}")
                print(f"     - 状态: {result.get('status')}")
            else:
                print(f"     - 警告: 未获取到 token 报告")
        
        print("✅ 端到端测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 端到端测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🎯 简化混合工作流完整测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("工作流组件", test_workflow_components),
        ("最小化工作流", test_minimal_workflow),
        ("端到端测试", test_end_to_end),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                failed += 1
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 异常: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 测试完成: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！简化混合工作流实现成功。")
        print("📝 这个版本展示了混合工作流的核心架构和逻辑")
        print("🚀 可以扩展为完整的 LangGraph + DeepAgent 实现")
    else:
        print("⚠️  部分测试失败，请检查实现。")
    
    return failed == 0


if __name__ == "__main__":
    asyncio.run(main())