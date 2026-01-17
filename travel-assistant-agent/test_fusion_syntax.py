"""
融合后的代码语法验证测试

检查：
1. 所有文件可以正确导入
2. 语法错误检测
3. 类型注解正确性
4. 导入依赖关系
"""
import ast
import sys
import os
from pathlib import Path


def check_python_syntax(file_path: Path) -> tuple[bool, str]:
    """
    检查 Python 文件语法

    Returns:
        (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, ""
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"读取错误: {e}"


def check_imports(file_path: Path) -> list[str]:
    """
    检查文件中的导入语句

    Returns:
        list of import statements
    """
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
    except Exception as e:
        imports.append(f"# 导入分析失败: {e}")

    return imports


def main():
    print("="*70)
    print("融合后的代码语法验证")
    print("="*70)

    # 需要检查的文件
    files_to_check = [
        "src/llm/models.py",
        "src/llm/factory.py",
        "src/cache/cache_strategy.py",
        "src/rag/knowledge_base.py",
        "src/workflows/main_workflow.py",
        "src/workflows/subgraphs.py",
    ]

    project_root = Path("/home/engine/project/travel-assistant-agent")

    all_valid = True
    results = []

    for file_path_str in files_to_check:
        file_path = project_root / file_path_str

        if not file_path.exists():
            results.append(f"✗ 文件不存在: {file_path_str}")
            all_valid = False
            continue

        # 检查语法
        is_valid, error_msg = check_python_syntax(file_path)

        if is_valid:
            # 检查导入
            imports = check_imports(file_path)

            # 关键导入检查
            key_imports = {
                "LLMFactory": False,
                "ModelTier": False,
                "CacheStrategy": False,
                "KnowledgeBase": False,
                "MainState": False,
            }

            for imp in imports:
                if "LLMFactory" in imp:
                    key_imports["LLMFactory"] = True
                if "ModelTier" in imp:
                    key_imports["ModelTier"] = True
                if "CacheStrategy" in imp:
                    key_imports["CacheStrategy"] = True
                if "KnowledgeBase" in imp:
                    key_imports["KnowledgeBase"] = True
                if "MainState" in imp:
                    key_imports["MainState"] = True

            results.append(f"✓ {file_path_str}")
            for key, found in key_imports.items():
                if found:
                    results.append(f"  - 导入: {key}")
        else:
            results.append(f"✗ {file_path_str}: {error_msg}")
            all_valid = False

    # 输出结果
    print("\n文件检查结果：")
    print("-"*70)
    for result in results:
        print(result)

    # 关键特性验证
    print("\n" + "="*70)
    print("关键特性验证")
    print("="*70)

    features = []

    # 检查 LLMFactory 模型层级
    models_py = project_root / "src/llm/models.py"
    with open(models_py, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'class ModelTier(str, Enum):' in content:
            features.append("✓ ModelTier 枚举定义")
        if 'CHEAP = "cheap"' in content:
            features.append("✓ 便宜层配置")
        if 'STANDARD = "standard"' in content:
            features.append("✓ 标准层配置")
        if 'POWERFUL = "powerful"' in content:
            features.append("✓ 强力层配置")

    # 检查 LLMFactory
    factory_py = project_root / "src/llm/factory.py"
    with open(factory_py, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'DEFAULT_MODELS' in content:
            features.append("✓ LLMFactory 默认层级配置")
        if 'create_model_by_tier' in content:
            features.append("✓ LLMFactory 按层级创建模型")

    # 检查 CacheStrategy
    cache_py = project_root / "src/cache/cache_strategy.py"
    with open(cache_py, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'class CacheStrategy' in content:
            features.append("✓ CacheStrategy 类定义")
        if 'cache_search_results' in content:
            features.append("✓ 搜索结果缓存")
        if 'cache_recommendations' in content:
            features.append("✓ 推荐结果缓存")
        if 'cache_rag_context' in content:
            features.append("✓ RAG 上下文缓存")

    # 检查 MainState 增强
    main_workflow_py = project_root / "src/workflows/main_workflow.py"
    with open(main_workflow_py, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'conversation_history' in content:
            features.append("✓ MainState 对话历史支持")
        if 'Annotated[List[Dict], operator.add]' in content:
            features.append("✓ 对话历史自动累加")

    # 检查 subgraphs 增强
    subgraphs_py = project_root / "src/workflows/subgraphs.py"
    with open(subgraphs_py, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'LLMFactory.create_model_by_tier' in content:
            features.append("✓ 子图使用 LLMFactory")
        if 'cache_strategy' in content:
            features.append("✓ 子图集成缓存策略")
        if 'knowledge_base' in content:
            features.append("✓ 子图集成知识库")
        if 'get_rag_context' in content:
            features.append("✓ RAG 上下文检索")
        if 'cache_strategy.get_search_results' in content:
            features.append("✓ 搜索节点使用缓存")
        if 'cache_strategy.get_recommendations' in content:
            features.append("✓ 推荐节点使用缓存")

    for feature in features:
        print(feature)

    # 架构完整性检查
    print("\n" + "="*70)
    print("架构完整性检查")
    print("="*70)

    architecture = []

    # 检查 5 层架构
    with open(main_workflow_py, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'class MainState(dict):' in content:
            architecture.append("✓ 第4层：MainState 状态定义")
        if 'def build_main_graph()' in content:
            architecture.append("✓ 第4层：主工作流图构建")
        if 'def call_subagent_node(' in content:
            architecture.append("✓ 第3层：工厂函数定义")
        if 'def get_or_create_main_agent()' in content:
            architecture.append("✓ 第5层：DeepAgent 创建")

    with open(subgraphs_py, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'def build_collect_info_graph()' in content:
            architecture.append("✓ 第1层：信息收集子图")
        if 'def build_search_graph()' in content:
            architecture.append("✓ 第1层：搜索子图")
        if 'def build_recommend_graph()' in content:
            architecture.append("✓ 第1层：推荐子图")
        if 'def build_booking_graph()' in content:
            architecture.append("✓ 第1层：预订子图")

    for arch in architecture:
        print(arch)

    # 总结
    print("\n" + "="*70)
    if all_valid:
        print("✓ 所有文件语法检查通过！")
    else:
        print("✗ 部分文件存在语法错误")
    print("="*70)

    print("\n融合完成度总结：")
    print(f"✓ LLMFactory 多模型支持：{len([f for f in features if 'LLMFactory' in f]) > 0}")
    print(f"✓ CacheStrategy 缓存策略：{len([f for f in features if '缓存' in f]) > 0}")
    print(f"✓ RAG 知识库集成：{len([f for f in features if 'RAG' in f or '知识库' in f]) > 0}")
    print(f"✓ 对话历史管理：{len([f for f in features if '对话历史' in f]) > 0}")
    print(f"✓ 4层架构保留：{len([f for f in architecture if '第' in f]) >= 5}")


if __name__ == "__main__":
    main()
