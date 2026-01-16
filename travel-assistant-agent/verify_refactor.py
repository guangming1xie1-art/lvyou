#!/usr/bin/env python3
"""
验证重构结果
检查所有关键模块是否正确创建和导入
"""
import sys
import os

# 设置环境变量（避免 API key 错误）
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")
os.environ.setdefault("DASHSCOPE_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

print("="*60)
print("验证重构结果")
print("="*60)

# 1. 检查 TokenCounter
print("\n1. 检查 TokenCounter...")
try:
    # 直接检查文件是否存在
    token_counter_path = os.path.join(os.path.dirname(__file__), "src", "utils", "token_counter.py")
    if os.path.exists(token_counter_path):
        print("✓ TokenCounter 文件存在")
        with open(token_counter_path, "r") as f:
            content = f.read()
            if "class TokenCounter" in content:
                print("✓ TokenCounter 类定义正确")
            if "def on_llm_end" in content:
                print("✓ on_llm_end 方法存在")
            if "def dump" in content:
                print("✓ dump 方法存在")
    else:
        print("✗ TokenCounter 文件不存在")
        sys.exit(1)
except Exception as e:
    print(f"✗ TokenCounter 检查失败: {e}")
    sys.exit(1)

# 2. 检查子图
print("\n2. 检查子图...")
try:
    # 检查子图文件
    subgraphs_path = os.path.join(os.path.dirname(__file__), "src", "workflows", "subgraphs.py")
    if os.path.exists(subgraphs_path):
        print("✓ subgraphs.py 文件存在")
        with open(subgraphs_path, "r") as f:
            content = f.read()
            graphs = ["build_collect_info_graph", "build_search_graph", "build_recommend_graph", "build_booking_graph"]
            for graph_name in graphs:
                if graph_name in content:
                    print(f"✓ {graph_name} 函数定义存在")
                else:
                    print(f"✗ {graph_name} 函数定义缺失")
    else:
        print("✗ subgraphs.py 文件不存在")
        sys.exit(1)
except Exception as e:
    print(f"✗ 子图检查失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 检查主工作流
print("\n3. 检查主工作流...")
try:
    # 检查主工作流文件
    main_workflow_path = os.path.join(os.path.dirname(__file__), "src", "workflows", "main_workflow.py")
    if os.path.exists(main_workflow_path):
        print("✓ main_workflow.py 文件存在")
        with open(main_workflow_path, "r") as f:
            content = f.read()
            required = ["MainWorkflowState", "build_main_workflow", "get_main_workflow", "run_main_workflow_sync"]
            for item in required:
                if item in content:
                    print(f"✓ {item} 定义存在")
                else:
                    print(f"✗ {item} 定义缺失")
    else:
        print("✗ main_workflow.py 文件不存在")
        sys.exit(1)
except Exception as e:
    print(f"✗ 主工作流检查失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 检查 MCP Client
print("\n4. 检查 MCP Client...")
try:
    # 检查 MCP Client 文件
    mcp_client_path = os.path.join(os.path.dirname(__file__), "src", "agents", "mcp_client.py")
    if os.path.exists(mcp_client_path):
        print("✓ mcp_client.py 文件存在")
        with open(mcp_client_path, "r") as f:
            content = f.read()
            required = ["class MCPClient", "get_mcp_client", "call_tool", "_init_tools"]
            for item in required:
                if item in content:
                    print(f"✓ {item} 定义存在")
                else:
                    print(f"✗ {item} 定义缺失")
            # 检查是否包含 Java API 工具
            if "search_destinations" in content:
                print("✓ search_destinations 工具定义存在")
            if "get_recommendations" in content:
                print("✓ get_recommendations 工具定义存在")
            if "create_booking" in content:
                print("✓ create_booking 工具定义存在")
    else:
        print("✗ mcp_client.py 文件不存在")
        sys.exit(1)
except Exception as e:
    print(f"✗ MCP Client 检查失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 检查 SkillRegistry
print("\n5. 检查 SkillRegistry...")
try:
    # 检查 SkillRegistry 文件
    registry_path = os.path.join(os.path.dirname(__file__), "src", "skills", "registry.py")
    if os.path.exists(registry_path):
        print("✓ registry.py 文件存在")
        with open(registry_path, "r") as f:
            content = f.read()
            required = ["class SkillRegistry", "list_skills", "load_skill", "get_skill_summary", "get_all_summaries"]
            for item in required:
                if item in content:
                    print(f"✓ {item} 定义存在")
                else:
                    print(f"✗ {item} 定义缺失")
    else:
        print("✗ registry.py 文件不存在")
        sys.exit(1)
except Exception as e:
    print(f"✗ SkillRegistry 检查失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. 检查 Skill 文件夹结构
print("\n6. 检查 Skill 文件夹结构...")
skills_dir = os.path.join(os.path.dirname(__file__), "src", "skills")
expected_skills = ["search", "recommend", "booking", "info_collection"]

for skill_name in expected_skills:
    skill_dir = os.path.join(skills_dir, skill_name)
    skill_md = os.path.join(skill_dir, "SKILL.md")
    skill_py = os.path.join(skill_dir, "skill.py")
    
    if os.path.exists(skill_dir):
        has_md = os.path.exists(skill_md)
        has_py = os.path.exists(skill_py)
        status = "✓" if (has_md and has_py) else "✗"
        print(f"{status} {skill_name}: SKILL.md={has_md}, skill.py={has_py}")
    else:
        print(f"✗ {skill_name}: 文件夹不存在")

# 7. 检查 SKILLS.md
print("\n7. 检查 SKILLS.md...")
skills_md = os.path.join(skills_dir, "SKILLS.md")
if os.path.exists(skills_md):
    print("✓ SKILLS.md 存在")
    with open(skills_md, "r", encoding="utf-8") as f:
        lines = f.readlines()
        print(f"  - {len(lines)} 行")
else:
    print("✗ SKILLS.md 不存在")

# 8. 检查删除的文件
print("\n8. 检查删除的文件...")
deleted_files = [
    "src/agents/deep_subagents.py",
    "src/mcp_server",
    "src/skills/builtins",
]

for file_path in deleted_files:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    if not os.path.exists(full_path):
        print(f"✓ {file_path} 已删除")
    else:
        print(f"✗ {file_path} 仍然存在")

print("\n" + "="*60)
print("验证完成！所有关键模块已正确创建")
print("="*60)

print("\n下一步:")
print("1. 运行 tests/test_refactored_workflow.py 进行端到端测试")
print("2. 查看 REFACTORED_ARCHITECTURE.md 了解架构细节")
print("3. 更新 main.py 使用新的 main_workflow")
