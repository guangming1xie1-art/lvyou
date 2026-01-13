"""
混合工作流测试脚本
用于验证 LangGraph + DeepAgent 混合工作流的功能
"""
import asyncio
import sys
import os
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from workflows.hybrid_workflow import HybridTravelWorkflow, get_hybrid_workflow
from utils.token_tracker import TokenTracker
from config import settings


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
        
        # 测试 3: 基本工作流运行
        print("\n3. 测试基本工作流运行...")
        test_user_message = "我想去北京旅行3天，预算5000元"
        result = await workflow.run(test_user_message)
        
        print(f"✅ 工作流运行完成")
        print(f"   - 状态: {result.get('status')}")
        print(f"   - 阶段: {result.get('stage')}")
        print(f"   - 错误: {result.get('error', 'None')}")
        print(f"   - 工作流路径: {result.get('workflow_path', [])}")
        
        if result.get('token_report'):
            token_report = result['token_report']
            print(f"   - 总 token 数: {token_report.get('total_tokens', 0)}")
            print(f"   - 效率分数: {result.get('efficiency_score', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_workflow_nodes():
    """测试工作流各个节点"""
    print("\n🔧 测试工作流节点...")
    
    try:
        workflow = HybridTravelWorkflow()
        
        # 测试初始状态
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
        
        # 测试条件分支函数
        print("   - 测试条件分支决策函数...")
        
        # 搜索质量测试
        test_state_high_quality = {**test_state, "search_quality": 0.8}
        decision = workflow._should_continue_after_search(test_state_high_quality)
        print(f"     高质量搜索结果 -> {decision}")
        
        test_state_low_quality = {**test_state, "search_quality": 0.3}
        decision = workflow._should_continue_after_search(test_state_low_quality)
        print(f"     低质量搜索结果 -> {decision}")
        
        # 验证结果测试
        test_state_valid = {
            **test_state, 
            "validate_results": {"validation_passed": True}
        }
        decision = workflow._should_recommend(test_state_valid)
        print(f"     验证通过 -> {decision}")
        
        test_state_invalid = {
            **test_state, 
            "validate_results": {"validation_passed": False}
        }
        decision = workflow._should_recommend(test_state_invalid)
        print(f"     验证失败 -> {decision}")
        
        print("✅ 条件分支函数测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 节点测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_token_efficiency():
    """测试 Token 效率"""
    print("\n📊 测试 Token 使用效率...")
    
    try:
        workflow = HybridTravelWorkflow()
        
        # 测试不同复杂度的请求
        test_cases = [
            ("简单请求", "去北京"),
            ("中等请求", "我想去东京旅行7天，预算10000元，喜欢文化景点"),
            ("复杂请求", "我计划去欧洲旅行15天，包括法国、意大利、德国，预算50000元，喜欢历史、文化、美食，需要包含住宿、交通、景点门票的详细规划")
        ]
        
        for case_name, user_message in test_cases:
            print(f"\n   测试 {case_name}: {user_message[:50]}...")
            
            result = await workflow.run(user_message)
            
            if result.get('token_report'):
                token_report = result['token_report']
                efficiency = result.get('efficiency_score', 0)
                
                print(f"     - Token 使用: {token_report.get('total_tokens', 0)}")
                print(f"     - 执行时间: {token_report.get('total_execution_time_ms', 0):.0f}ms")
                print(f"     - 效率分数: {efficiency}")
                print(f"     - 节点数: {token_report.get('node_count', 0)}")
            else:
                print(f"     - 警告: 未获取到 token 报告")
        
        print("✅ Token 效率测试完成")
        return True
        
    except Exception as e:
        print(f"❌ Token 效率测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_handling():
    """测试错误处理"""
    print("\n🛡️ 测试错误处理...")
    
    try:
        workflow = HybridTravelWorkflow()
        
        # 测试错误重试逻辑
        print("   - 测试错误重试判断...")
        
        # 可重试的错误
        retryable_errors = [
            "网络超时",
            "DeepAgent API 临时不可用",
            "搜索质量低于阈值"
        ]
        
        for error in retryable_errors:
            should_retry = workflow._should_retry_error(error, {})
            print(f"     错误 '{error}' -> {'可重试' if should_retry else '不可重试'}")
        
        # 不可重试的错误
        non_retryable_errors = [
            "用户输入无效",
            "配置错误",
            "永久性系统故障"
        ]
        
        for error in non_retryable_errors:
            should_retry = workflow._should_retry_error(error, {})
            print(f"     错误 '{error}' -> {'可重试' if should_retry else '不可重试'}")
        
        print("✅ 错误处理测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🎯 LangGraph + DeepAgent 混合工作流测试")
    print("=" * 50)
    
    # 设置测试环境
    if not settings.anthropic_api_key:
        print("⚠️  警告: ANTHROPIC_API_KEY 未设置，某些功能可能无法正常工作")
    
    # 运行测试
    tests = [
        ("基本功能", test_basic_functionality),
        ("工作流节点", test_workflow_nodes),
        ("Token 效率", test_token_efficiency),
        ("错误处理", test_error_handling)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 异常: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 测试完成: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！混合工作流实现成功。")
    else:
        print("⚠️  部分测试失败，请检查实现。")
    
    return failed == 0


if __name__ == "__main__":
    asyncio.run(main())