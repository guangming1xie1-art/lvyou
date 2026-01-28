"""
测试 collect 阶段的信息验证和工作流路由
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'travel-assistant-agent', 'src'))

from workflows.main_workflow import run_main_workflow_async


async def test_scenario_1_valid_date():
    """测试场景1：有效日期 - 应该继续到 search 阶段"""
    print("\n" + "="*80)
    print("测试场景1：有效日期 (2026年2月28日)")
    print("="*80)

    user_message = "我现在在大连，2026年2月28号出发，想去北京玩3天"
    result = await run_main_workflow_async(user_message)

    collected_info = result.get("collected_info", {})
    print(f"\n收集到的信息: {collected_info}")
    print(f"complete 状态: {collected_info.get('complete', False)}")
    print(f"消息: {collected_info.get('message', 'N/A')}")

    # 检查结果
    assert collected_info.get('complete') == True, "✅ 有效日期应该设置 complete=true"
    assert result.get('search_results') is not None, "✅ 应该执行到 search 阶段"

    print("\n✅ 测试场景1通过！")
    return True


async def test_scenario_2_invalid_date():
    """测试场景2：无效日期 (2月30日) - 应该停止并返回澄清消息"""
    print("\n" + "="*80)
    print("测试场景2：无效日期 (2026年2月30日)")
    print("="*80)

    user_message = "我现在在大连，2026年2月30号，想去北京玩3天"
    result = await run_main_workflow_async(user_message)

    collected_info = result.get("collected_info", {})
    print(f"\n收集到的信息: {collected_info}")
    print(f"complete 状态: {collected_info.get('complete', False)}")
    print(f"消息: {collected_info.get('message', 'N/A')}")

    # 检查结果
    assert collected_info.get('complete') == False, "❌ 无效日期应该设置 complete=false"
    assert result.get('search_results') is None, "❌ 不应该执行到 search 阶段"
    assert '2月30' in collected_info.get('message', '') or '不存在' in collected_info.get('message', ''), \
        "❌ 消息应该指出日期错误"

    print("\n✅ 测试场景2通过！")
    return True


async def test_scenario_3_missing_destination():
    """测试场景3：缺失目的地信息 - 应该停止并要求澄清"""
    print("\n" + "="*80)
    print("测试场景3：缺失目的地信息")
    print("="*80)

    user_message = "我想在2026年3月15号出去玩3天"
    result = await run_main_workflow_async(user_message)

    collected_info = result.get("collected_info", {})
    print(f"\n收集到的信息: {collected_info}")
    print(f"complete 状态: {collected_info.get('complete', False)}")
    print(f"消息: {collected_info.get('message', 'N/A')}")

    # 检查结果
    assert collected_info.get('complete') == False, "❌ 缺失目的地应该设置 complete=false"
    assert result.get('search_results') is None, "❌ 不应该执行到 search 阶段"
    assert '目的地' in collected_info.get('message', '') or '哪里' in collected_info.get('message', ''), \
        "❌ 消息应该询问目的地"

    print("\n✅ 测试场景3通过！")
    return True


async def test_scenario_4_missing_both():
    """测试场景4：同时缺失目的地和日期 - 应该停止"""
    print("\n" + "="*80)
    print("测试场景4：同时缺失目的地和日期")
    print("="*80)

    user_message = "我想出去玩几天"
    result = await run_main_workflow_async(user_message)

    collected_info = result.get("collected_info", {})
    print(f"\n收集到的信息: {collected_info}")
    print(f"complete 状态: {collected_info.get('complete', False)}")
    print(f"消息: {collected_info.get('message', 'N/A')}")

    # 检查结果
    assert collected_info.get('complete') == False, "❌ 信息不完整应该设置 complete=false"
    assert result.get('search_results') is None, "❌ 不应该执行到 search 阶段"

    print("\n✅ 测试场景4通过！")
    return True


async def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("开始测试 collect 阶段的信息验证和工作流路由")
    print("="*80)

    tests = [
        ("场景1：有效日期", test_scenario_1_valid_date),
        ("场景2：无效日期", test_scenario_2_invalid_date),
        ("场景3：缺失目的地", test_scenario_3_missing_destination),
        ("场景4：缺失关键信息", test_scenario_4_missing_both),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} 失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("="*80)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
