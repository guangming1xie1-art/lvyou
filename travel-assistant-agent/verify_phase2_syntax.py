#!/usr/bin/env python3
"""
Phase 2 模块验证 - 语法和结构验证
"""
import ast
import os
import sys


def check_python_syntax(filepath):
    """检查Python文件语法"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)


def extract_classes_and_functions(filepath):
    """提取类名和函数名"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code)
        
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return classes, functions
    except Exception as e:
        return [], []


def main():
    print("=" * 60)
    print("Phase 2 成本优化体系 - 语法和结构验证")
    print("=" * 60)
    
    all_passed = True
    
    base_path = "/home/engine/project/travel-assistant-agent"
    
    # RAG模块文件
    rag_files = [
        ("src/rag/__init__.py", "RAG模块初始化"),
        ("src/rag/embeddings.py", "Embeddings工厂"),
        ("src/rag/vectorstore.py", "向量存储管理"),
        ("src/rag/retriever.py", "混合检索器"),
        ("src/rag/knowledge_base.py", "知识库管理"),
    ]
    
    # 缓存模块文件
    cache_files = [
        ("src/cache/__init__.py", "缓存模块初始化"),
        ("src/cache/cache_key.py", "缓存键生成"),
        ("src/cache/prompt_cache.py", "Prompt缓存管理"),
        ("src/cache/cache_strategy.py", "缓存策略"),
    ]
    
    # 更新后的文件
    updated_files = [
        ("src/config.py", "配置模块"),
        ("src/workflows/conversation/nodes/search.py", "搜索节点"),
    ]
    
    all_files = rag_files + cache_files + updated_files
    
    print("\n📁 文件语法检查")
    print("-" * 40)
    
    for rel_path, desc in all_files:
        filepath = os.path.join(base_path, rel_path)
        
        if not os.path.exists(filepath):
            print(f"  ✗ {desc}: 文件不存在")
            all_passed = False
            continue
        
        valid, error = check_python_syntax(filepath)
        
        if valid:
            print(f"  ✓ {desc}: 语法正确")
        else:
            print(f"  ✗ {desc}: 语法错误 - {error}")
            all_passed = False
    
    print("\n📋 类和函数检查")
    print("-" * 40)
    
    rag_classes_expected = {
        "src/rag/embeddings.py": ["EmbeddingFactory"],
        "src/rag/vectorstore.py": ["VectorStoreManager"],
        "src/rag/retriever.py": ["HybridRetriever"],
        "src/rag/knowledge_base.py": ["KnowledgeBase", "TravelKnowledgeBase"],
    }
    
    cache_classes_expected = {
        "src/cache/cache_key.py": ["CacheKeyGenerator"],
        "src/cache/prompt_cache.py": ["PromptCacheManager"],
        "src/cache/cache_strategy.py": ["CacheStrategy", "CacheManager"],
    }
    
    for rel_path, expected_classes in rag_classes_expected.items():
        filepath = os.path.join(base_path, rel_path)
        classes, _ = extract_classes_and_functions(filepath)
        
        for expected in expected_classes:
            if expected in classes:
                print(f"  ✓ {expected} (RAG)")
            else:
                print(f"  ✗ {expected} (RAG) - 未找到")
                all_passed = False
    
    for rel_path, expected_classes in cache_classes_expected.items():
        filepath = os.path.join(base_path, rel_path)
        classes, _ = extract_classes_and_functions(filepath)
        
        for expected in expected_classes:
            if expected in classes:
                print(f"  ✓ {expected} (Cache)")
            else:
                print(f"  ✗ {expected} (Cache) - 未找到")
                all_passed = False
    
    print("\n📦 导出检查")
    print("-" * 40)
    
    # 检查 __all__ 导出
    rag_init_path = os.path.join(base_path, "src/rag/__init__.py")
    cache_init_path = os.path.join(base_path, "src/cache/__init__.py")
    
    for init_path, module_name in [(rag_init_path, "RAG"), (cache_init_path, "Cache")]:
        if os.path.exists(init_path):
            content = open(init_path).read()
            if "__all__" in content:
                print(f"  ✓ {module_name} 模块导出配置正确")
            else:
                print(f"  ⚠ {module_name} 模块缺少 __all__ 导出")
    
    print("\n📊 文件统计")
    print("-" * 40)
    
    rag_count = len([f for f in os.listdir(os.path.join(base_path, "src/rag")) if f.endswith('.py')])
    cache_count = len([f for f in os.listdir(os.path.join(base_path, "src/cache")) if f.endswith('.py')])
    
    print(f"  RAG模块: {rag_count} 个Python文件")
    print(f"  缓存模块: {cache_count} 个Python文件")
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有文件语法和结构检查通过！")
        print("\n注意: 模块导入测试需要安装依赖包:")
        print("  pip install langchain langchain-community redis rank-bm25")
    else:
        print("❌ 部分检查未通过，请修复后再试")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
