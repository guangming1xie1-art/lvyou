#!/usr/bin/env python3
"""
验证5层架构重构 - 语法检查

仅检查文件是否可以导入，不执行运行时测试
"""
import sys
from pathlib import Path
import ast

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))


def check_file_syntax(filepath: str) -> bool:
    """检查 Python 文件语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"  ✗ 语法错误: {e}")
        return False
    except Exception as e:
        print(f"  ✗ 其他错误: {e}")
        return False


def test_layer_0():
    """测试第0层：TokenCounter"""
    print("\n" + "="*60)
    print("【第0层】TokenCounter - 语法检查")
    print("="*60)
    
    filepath = "src/utils/token_counter.py"
    print(f"检查文件: {filepath}")
    
    if check_file_syntax(filepath):
        print("✓ 语法正确")
        return True
    return False


def test_layer_1():
    """测试第1层：子图"""
    print("\n" + "="*60)
    print("【第1层】子图 (subgraphs.py) - 语法检查")
    print("="*60)
    
    filepath = "src/workflows/subgraphs.py"
    print(f"检查文件: {filepath}")
    
    if check_file_syntax(filepath):
        print("✓ 语法正确")
        
        # 检查是否包含必要的函数
        with open(filepath, 'r') as f:
            content = f.read()
        
        required_functions = [
            "build_collect_info_graph",
            "build_search_graph",
            "build_recommend_graph",
            "build_booking_graph",
        ]
        
        for func in required_functions:
            if func in content:
                print(f"  ✓ 包含函数: {func}")
            else:
                print(f"  ✗ 缺少函数: {func}")
                return False
        
        return True
    return False


def test_layer_2():
    """测试第2层：CompiledSubAgent"""
    print("\n" + "="*60)
    print("【第2层】CompiledSubAgent (subagents.py) - 语法检查")
    print("="*60)
    
    filepath = "src/workflows/subagents.py"
    print(f"检查文件: {filepath}")
    
    if check_file_syntax(filepath):
        print("✓ 语法正确")
        
        # 检查是否包含必要的函数
        with open(filepath, 'r') as f:
            content = f.read()
        
        required_functions = [
            "get_info_collection_agent",
            "get_search_agent",
            "get_recommend_agent",
            "get_booking_agent",
        ]
        
        for func in required_functions:
            if func in content:
                print(f"  ✓ 包含函数: {func}")
            else:
                print(f"  ✗ 缺少函数: {func}")
                return False
        
        # 检查是否导入 deepagents
        if "from deepagents import CompiledSubAgent" in content:
            print("  ✓ 导入 deepagents.CompiledSubAgent")
        else:
            print("  ✗ 缺少 deepagents 导入")
            return False
        
        return True
    return False


def test_layer_3_4_5():
    """测试第3、4、5层：主工作流"""
    print("\n" + "="*60)
    print("【第3、4、5层】主工作流 (main_workflow.py) - 语法检查")
    print("="*60)
    
    filepath = "src/workflows/main_workflow.py"
    print(f"检查文件: {filepath}")
    
    if check_file_syntax(filepath):
        print("✓ 语法正确")
        
        # 检查是否包含必要的函数和类
        with open(filepath, 'r') as f:
            content = f.read()
        
        required_items = [
            ("class MainState", "MainState 类定义"),
            ("def call_subagent_node", "第3层：call_subagent_node 工厂函数"),
            ("def build_main_graph", "第4层：build_main_graph 主图构建"),
            ("def get_or_create_main_agent", "第5层：get_or_create_main_agent DeepAgent"),
            ("from deepagents import create_deep_agent", "deepagents 导入"),
            ("operator.add", "operator.add 累加器"),
        ]
        
        for item, desc in required_items:
            if item in content:
                print(f"  ✓ {desc}")
            else:
                print(f"  ✗ 缺少: {desc}")
                return False
        
        return True
    return False


def test_mcp_client():
    """测试 MCP Client"""
    print("\n" + "="*60)
    print("【MCP】MCP Client - 语法检查")
    print("="*60)
    
    filepath = "src/agents/mcp_client.py"
    print(f"检查文件: {filepath}")
    
    if check_file_syntax(filepath):
        print("✓ 语法正确")
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        if "class MCPClient" in content:
            print("  ✓ 包含 MCPClient 类")
        
        if "get_tool_summaries_text" in content:
            print("  ✓ 包含 get_tool_summaries_text 方法")
        else:
            print("  ! get_tool_summaries_text 方法未找到")
        
        return True
    return False


def test_skills_registry():
    """测试 Skills Registry"""
    print("\n" + "="*60)
    print("【Skills】Skills Registry - 语法检查")
    print("="*60)
    
    filepath = "src/skills/registry.py"
    print(f"检查文件: {filepath}")
    
    if check_file_syntax(filepath):
        print("✓ 语法正确")
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        if "class SkillRegistry" in content:
            print("  ✓ 包含 SkillRegistry 类")
        
        if "get_all_summaries_text" in content:
            print("  ✓ 包含 get_all_summaries_text 方法")
        else:
            print("  ! get_all_summaries_text 方法未找到")
        
        return True
    return False


def test_skills_md():
    """测试 SKILLS.md"""
    print("\n" + "="*60)
    print("【Skills】SKILLS.md - 文件检查")
    print("="*60)
    
    filepath = "src/skills/SKILLS.md"
    print(f"检查文件: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✓ 文件存在")
        
        # 检查是否包含4个技能
        skills = ["search", "recommend", "booking", "info_collection"]
        for skill in skills:
            if skill in content:
                print(f"  ✓ 包含 skill: {skill}")
            else:
                print(f"  ✗ 缺少 skill: {skill}")
                return False
        
        return True
    except FileNotFoundError:
        print("  ✗ 文件不存在")
        return False


def test_deepagents_library():
    """测试 deepagents 库导入"""
    print("\n" + "="*60)
    print("【库测试】deepagents v0.2.7 库 - 导入检查")
    print("="*60)
    
    try:
        from deepagents import create_deep_agent, CompiledSubAgent
        print("✓ 成功导入 deepagents 库")
        print("✓ create_deep_agent:", create_deep_agent)
        print("✓ CompiledSubAgent:", CompiledSubAgent)
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_mcp_client_library():
    """测试 langchain_mcp_adapters 库"""
    print("\n" + "="*60)
    print("【库测试】langchain_mcp_adapters 库 - 导入检查")
    print("="*60)
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        print("✓ 成功导入 MultiServerMCPClient")
        print("✓ MultiServerMCPClient:", MultiServerMCPClient)
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("5层架构重构 - 语法验证")
    print("="*60)
    
    results = []
    
    # deepagents 库测试
    results.append(("deepagents v0.2.7 库", test_deepagents_library()))
    
    # langchain_mcp_adapters 库测试
    results.append(("langchain_mcp_adapters 库", test_mcp_client_library()))
    
    # 第0层
    results.append(("第0层: TokenCounter", test_layer_0()))
    
    # 第1层
    results.append(("第1层: 子图", test_layer_1()))
    
    # 第2层
    results.append(("第2层: CompiledSubAgent", test_layer_2()))
    
    # 第3、4、5层
    results.append(("第3、4、5层: 主工作流", test_layer_3_4_5()))
    
    # MCP Client
    results.append(("MCP Client", test_mcp_client()))
    
    # Skills Registry
    results.append(("Skills Registry", test_skills_registry()))
    
    # SKILLS.md
    results.append(("SKILLS.md", test_skills_md()))
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！5层架构重构完成！")
        print("\n✅ 使用真正的库：")
        print("  - deepagents v0.2.7: CompiledSubAgent, create_deep_agent")
        print("  - langchain_mcp_adapters: MultiServerMCPClient")
        print("\n📁 文件结构:")
        print("  第0层: src/utils/token_counter.py")
        print("  第1层: src/workflows/subgraphs.py")
        print("  第2层: src/workflows/subagents.py")
        print("  第3、4、5层: src/workflows/main_workflow.py")
        print("  MCP: src/agents/mcp_client.py")
        print("  Skills: src/skills/registry.py, src/skills/SKILLS.md")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
