"""
超简化混合工作流测试
只测试基本架构和类定义，不依赖外部API
"""
import sys
import os
from typing import Dict, Any

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_classes():
    """测试基本类定义"""
    print("🚀 测试基本类定义...")
    
    try:
        # 测试 Token 追踪器
        from utils.token_tracker import TokenTracker
        tracker = TokenTracker()
        print("✅ TokenTracker 类定义正确")
        
        # 测试状态定义
        from workflows.hybrid_workflow import HybridWorkflowState
        print("✅ HybridWorkflowState 定义正确")
        
        # 测试工作流类
        from workflows.hybrid_workflow import HybridTravelWorkflow
        print("✅ HybridTravelWorkflow 类定义正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本类测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_workflow():
    """测试简化工作流"""
    print("\n🔧 测试简化工作流...")
    
    try:
        from workflows.hybrid_workflow import HybridTravelWorkflow
        
        # 创建工作流实例（不初始化LLM）
        workflow = HybridTravelWorkflow()
        print("✅ 工作流实例创建成功")
        
        # 测试条件分支函数
        test_state_good = {"search_quality": 0.8}
        decision = workflow._should_continue_after_search(test_state_good)
        print(f"✅ 高质量搜索 -> {decision}")
        
        test_state_bad = {"search_quality": 0.3}
        decision = workflow._should_continue_after_search(test_state_bad)
        print(f"✅ 低质量搜索 -> {decision}")
        
        # 测试错误重试逻辑
        error_retry = "网络超时"
        should_retry = workflow._should_retry_error(error_retry, {})
        print(f"✅ 错误重试测试: '{error_retry}' -> {'可重试' if should_retry else '不可重试'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 简化工作流测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_schema_definitions():
    """测试架构定义"""
    print("\n📋 测试架构定义...")
    
    try:
        from models.schemas import (
            TokenUsageStats, PerformanceReport, WorkflowNodeStats,
            AgentStatsResponse, HybridWorkflowRequest, HybridWorkflowResponse
        )
        
        print("✅ 所有 Pydantic 模型定义正确")
        
        # 测试创建实例
        request = HybridWorkflowRequest(
            user_message="测试消息",
            use_deep_agent=True
        )
        print(f"✅ HybridWorkflowRequest 实例创建成功: {request.user_message}")
        
        return True
        
    except Exception as e:
        print(f"❌ 架构定义测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    try:
        from config import settings
        
        # 检查关键配置项
        assert hasattr(settings, 'claude_model')
        assert hasattr(settings, 'anthropic_api_key')
        assert hasattr(settings, 'workflow_quality_threshold')
        assert hasattr(settings, 'workflow_max_retries')
        
        print(f"✅ 配置加载成功")
        print(f"   - Claude 模型: {settings.claude_model}")
        print(f"   - 工作流质量阈值: {settings.workflow_quality_threshold}")
        print(f"   - 最大重试次数: {settings.workflow_max_retries}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🎯 超简化混合工作流架构测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("基本类定义", test_basic_classes),
        ("简化工作流", test_simple_workflow),
        ("架构定义", test_schema_definitions),
        ("配置", test_configuration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
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
        print("🎉 所有架构测试通过！混合工作流基本架构实现成功。")
        print("📝 接下来可以配置 Anthropic API key 进行完整功能测试")
    else:
        print("⚠️  部分测试失败，请检查实现。")
    
    return failed == 0


if __name__ == "__main__":
    main()