"""
验证 collect 工作流修改的实现完整性
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'travel-assistant-agent', 'src'))

def verify_collect_module():
    """验证 collect.py 模块"""
    print("\n" + "="*80)
    print("验证 collect.py 模块")
    print("="*80)

    try:
        from workflows.subgraphs.collect import (
            build_collect_info_graph,
            _route_collect_main,
            collect_info_node
        )
        print("✅ 成功导入所有函数和类")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 检查 _route_collect_main 函数
    print("\n检查 _route_collect_main 函数...")
    test_state = {
        "collected_info": {
            "complete": True
        }
    }
    route = _route_collect_main(test_state)
    print(f"✅ _route_collect_main 对于 complete=True 返回: {route}")
    assert route == "search", f"期望返回 'search'，实际返回 '{route}'"

    test_state = {
        "collected_info": {
            "complete": False
        }
    }
    route = _route_collect_main(test_state)
    print(f"✅ _route_collect_main 对于 complete=False 返回: {route}")
    assert route == "end", f"期望返回 'end'，实际返回 '{route}'"

    # 检查 build_collect_info_graph 函数
    print("\n检查 build_collect_info_graph 函数...")
    graph = build_collect_info_graph()
    print(f"✅ 成功构建工作流图")
    print(f"✅ 工作流图类型: {type(graph)}")

    # 检查图结构
    try:
        print(f"✅ 工作流图节点: {graph.nodes}")
        print(f"✅ 工作流图边: {graph.edges}")
    except Exception as e:
        print(f"⚠️  无法获取图结构: {e}")

    return True


def verify_main_workflow():
    """验证 main_workflow.py 模块"""
    print("\n" + "="*80)
    print("验证 main_workflow.py 模块")
    print("="*80)

    try:
        from workflows.main_workflow import (
            build_main_graph,
            _route_collect_main,
            MainState
        )
        print("✅ 成功导入所有函数和类")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 检查 _route_collect_main 是否正确导入
    print("\n检查 _route_collect_main 函数导入...")
    test_state = {
        "collected_info": {
            "complete": True,
            "message": "Test"
        }
    }
    route = _route_collect_main(test_state)
    print(f"✅ _route_collect_main 导入正确，返回: {route}")
    assert route == "search", f"期望返回 'search'，实际返回 '{route}'"

    # 检查 build_main_graph 函数
    print("\n检查 build_main_graph 函数...")
    graph = build_main_graph()
    print(f"✅ 成功构建主工作流图")
    print(f"✅ 主工作流图类型: {type(graph)}")

    # 检查图结构
    try:
        print(f"✅ 主工作流图节点: {graph.nodes}")
        print(f"✅ 主工作流图边: {graph.edges}")
    except Exception as e:
        print(f"⚠️  无法获取图结构: {e}")

    return True


def verify_prompt_content():
    """验证系统提示词内容"""
    print("\n" + "="*80)
    print("验证系统提示词内容")
    print("="*80)

    from workflows.subgraphs.collect import collect_info_node
    import inspect

    # 获取函数源码
    source = inspect.getsource(collect_info_node)

    # 检查关键内容
    checks = [
        ("complete = true", "提示词包含 complete=true 的说明"),
        ("complete = false", "提示词包含 complete=false 的说明"),
        ("规则 1", "提示词包含规则1"),
        ("规则 2", "提示词包含规则2"),
        ("2月30号", "提示词包含错误日期示例"),
        ("critical", "提示词强调 critical"),
        ("message", "提示词包含 message 字段"),
    ]

    for keyword, description in checks:
        if keyword in source:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - 未找到关键词 '{keyword}'")
            return False

    return True


def main():
    """运行所有验证"""
    print("\n" + "="*80)
    print("开始验证 collect 工作流修改的实现")
    print("="*80)

    results = []

    # 验证各个模块
    results.append(("collect 模块", verify_collect_module()))
    results.append(("main_workflow 模块", verify_main_workflow()))
    results.append(("系统提示词内容", verify_prompt_content()))

    # 汇总结果
    print("\n" + "="*80)
    print("验证结果汇总")
    print("="*80)

    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("\n" + "="*80)
    if all_passed:
        print("🎉 所有验证通过！实现完整且正确。")
    else:
        print("⚠️  部分验证失败，请检查上述问题。")
    print("="*80 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
