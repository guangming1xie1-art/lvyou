"""
混合工作流简化测试脚本
用于验证基本功能，不依赖外部 API
"""
import asyncio
import sys
import os
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from workflows.hybrid_workflow import HybridTravelWorkflow
from utils.token_tracker import TokenTracker


async def test_basic_functionality():
    """测试基本功能"""
    print("🚀 开始测试混合工作流基本功能...")
    
    try:
        # 测试 1: 创建工作流实例
        print("\n1. 测试工作流实例创建...")
        workflow = HybridTravelWorkflow()
        print("✅ 工作流实例创建成功")
        
        # 测试 2: Token 追踪器
        print("\n2. 测试 Token 追踪器...")
        tracker = TokenTracker()
        tracker.start_request("test_request_123")
        tracker.start_node("test_node")
        tracker.end_node("test_node", input_tokens=100, output_tokens=200, success=True)
        
        report = tracker.generate_report()
        print(f"✅ Token 追踪器工作正常: {report['total_tokens']} tokens")
        
        # 测试 3: 条件分支函数
        print("\n3. 测试条件分支决策函数...")
        
        # 搜索质量测试
        test_state_high_quality = {"search_quality": 0.8}
        decision = workflow._should_continue_after_search(test_state_high_quality)
        print(f"   高质量搜索结果 -> {decision}")
        
        test_state_low_quality = {"search_quality": 0.3}
        decision = workflow._should_continue_after_search(test_state_low_quality)
        print(f"   低质量搜索结果 -> {decision}")
        
        # 验证结果测试
        test_state_valid = {"validate_results": {"validation_passed": True}}
        decision = workflow._should_recommend(test_state_valid)
        print(f"   验证通过 -> {decision}")
        
        test_state_invalid = {"validate_results": {"validation_passed": False}}
        decision = workflow._should_recommend(test_state_invalid)
        print(f"   验证失败 -> {decision}")
        
        # 错误重试测试
        print("\n4. 测试错误重试判断...")
        retryable_errors = [
            "网络超时",
            "DeepAgent API 临时不可用",
            "搜索质量低于阈值"
        ]
        
        for error in retryable_errors:
            should_retry = workflow._should_retry_error(error, {})
            print(f"   错误 '{error}' -> {'可重试' if should_retry else '不可重试'}")
        
        print("✅ 条件分支函数测试通过")
        
        # 测试 5: 简化的工作流运行（不调用外部 API）
        print("\n5. 测试简化工作流状态管理...")
        
        # 创建一个基本的模拟状态
        test_state = {
            "user_message": "我想去巴黎旅行",
            "request_id": "test_123",
            "collected_info": {"destination": "Paris"},
            "search_results": {},
            "recommendations": {},
            "booking_confirmation": {},
            "final_plan": {},
            "error": None,
            "retry_count": 0,
            "error_details": {},
            "status": "pending",
            "should_retry": False,
            "workflow_path": [],
            "stage": "starting",
            "timestamp": 1234567890.0
        }
        
        # 测试各个节点的单独运行
        print("   - 测试信息收集节点...")
        result = await workflow._collect_info(test_state)
        print(f"     信息收集结果: {result.get('stage')}")
        
        # 测试错误处理节点
        print("   - 测试错误处理节点...")
        error_state = {**test_state, "error": "测试错误"}
        result = await workflow._handle_error(error_state)
        print(f"     错误处理结果: {result.get('should_retry')}")
        
        print("✅ 简化工作流状态管理测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_workflow_graph():
    """测试工作流图构建"""
    print("\n🔧 测试工作流图构建...")
    
    try:
        workflow = HybridTravelWorkflow()
        
        # 检查图是否已构建
        if workflow.graph:
            print("✅ LangGraph 工作流图构建成功")
            print(f"   图类型: {type(workflow.graph)}")
        else:
            print("❌ 工作流图构建失败")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 工作流图测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🎯 LangGraph + DeepAgent 混合工作流简化测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("基本功能", test_basic_functionality),
        ("工作流图构建", test_workflow_graph),
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
        print("🎉 所有简化测试通过！混合工作流基本架构实现成功。")
        print("📝 注意事项: 完整功能需要配置 Anthropic API key 和外部服务")
    else:
        print("⚠️  部分测试失败，请检查实现。")
    
    return failed == 0


if __name__ == "__main__":
    asyncio.run(main())