#!/usr/bin/env python3
"""
RAG和缓存模块验证脚本
验证文件结构完整性和导入正确性
"""
import os
import sys
import subprocess

# 添加项目路径
sys.path.insert(0, "/home/engine/project/travel-assistant-agent")


def check_file_exists(filepath, description):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {filepath}")
    return exists


def check_module_import(module_name, description):
    """检查模块能否正确导入"""
    try:
        __import__(module_name)
        print(f"  ✓ {description}: 导入成功")
        return True
    except Exception as e:
        print(f"  ✗ {description}: 导入失败 - {e}")
        return False


def check_class_in_module(module_name, class_name):
    """检查类是否存在"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"  ✓ {class_name} 类存在")
        return True
    except Exception as e:
        print(f"  ✗ {class_name} 类不存在 - {e}")
        return False


def main():
    print("=" * 60)
    print("Phase 2 成本优化体系验证")
    print("=" * 60)
    
    all_passed = True
    
    # 1. 检查文件结构
    print("\n📁 文件结构检查")
    print("-" * 40)
    
    base_path = "/home/engine/project/travel-assistant-agent/src"
    
    # RAG模块
    rag_files = [
        ("/home/engine/project/travel-assistant-agent/src/rag/__init__.py", "RAG模块初始化"),
        ("/home/engine/project/travel-assistant-agent/src/rag/embeddings.py", "Embeddings工厂"),
        ("/home/engine/project/travel-assistant-agent/src/rag/vectorstore.py", "向量存储管理"),
        ("/home/engine/project/travel-assistant-agent/src/rag/retriever.py", "混合检索器"),
        ("/home/engine/project/travel-assistant-agent/src/rag/knowledge_base.py", "知识库管理"),
    ]
    
    for filepath, desc in rag_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 缓存模块
    cache_files = [
        ("/home/engine/project/travel-assistant-agent/src/cache/__init__.py", "缓存模块初始化"),
        ("/home/engine/project/travel-assistant-agent/src/cache/cache_key.py", "缓存键生成"),
        ("/home/engine/project/travel-assistant-agent/src/cache/prompt_cache.py", "Prompt缓存管理"),
        ("/home/engine/project/travel-assistant-agent/src/cache/cache_strategy.py", "缓存策略"),
    ]
    
    for filepath, desc in cache_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 更新后的文件
    updated_files = [
        ("/home/engine/project/travel-assistant-agent/src/config.py", "配置更新"),
        ("/home/engine/project/travel-assistant-agent/src/workflows/conversation/nodes/search.py", "搜索节点更新"),
    ]
    
    for filepath, desc in updated_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 测试文件
    test_files = [
        ("/home/engine/project/travel-assistant-agent/tests/test_rag.py", "RAG单元测试"),
        ("/home/engine/project/travel-assistant-agent/tests/test_cache.py", "缓存单元测试"),
        ("/home/engine/project/travel-assistant-agent/tests/test_rag_cache_integration.py", "集成测试"),
    ]
    
    for filepath, desc in test_files:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 2. 检查模块导入
    print("\n📦 模块导入检查")
    print("-" * 40)
    
    rag_imports = [
        ("src.rag", "RAG模块"),
        ("src.rag.embeddings", "Embeddings模块"),
        ("src.rag.vectorstore", "VectorStore模块"),
        ("src.rag.retriever", "Retriever模块"),
        ("src.rag.knowledge_base", "KnowledgeBase模块"),
    ]
    
    for module, desc in rag_imports:
        if not check_module_import(module, desc):
            all_passed = False
    
    cache_imports = [
        ("src.cache", "缓存模块"),
        ("src.cache.cache_key", "CacheKey模块"),
        ("src.cache.prompt_cache", "PromptCache模块"),
        ("src.cache.cache_strategy", "CacheStrategy模块"),
    ]
    
    for module, desc in cache_imports:
        if not check_module_import(module, desc):
            all_passed = False
    
    # 3. 检查类定义
    print("\n📋 类定义检查")
    print("-" * 40)
    
    rag_classes = [
        ("src.rag.embeddings", "EmbeddingFactory"),
        ("src.rag.vectorstore", "VectorStoreManager"),
        ("src.rag.retriever", "HybridRetriever"),
        ("src.rag.knowledge_base", "KnowledgeBase"),
        ("src.rag.knowledge_base", "TravelKnowledgeBase"),
    ]
    
    for module, cls in rag_classes:
        if not check_class_in_module(module, cls):
            all_passed = False
    
    cache_classes = [
        ("src.cache.cache_key", "CacheKeyGenerator"),
        ("src.cache.prompt_cache", "PromptCacheManager"),
        ("src.cache.cache_strategy", "CacheStrategy"),
        ("src.cache.cache_strategy", "CacheManager"),
    ]
    
    for module, cls in cache_classes:
        if not check_class_in_module(module, cls):
            all_passed = False
    
    # 4. 检查配置
    print("\n⚙️ 配置检查")
    print("-" * 40)
    
    try:
        from src.config import settings
        
        config_checks = [
            ("vector_store_path", hasattr(settings, "vector_store_path")),
            ("embedding_model", hasattr(settings, "embedding_model")),
            ("hybrid_search_enabled", hasattr(settings, "hybrid_search_enabled")),
            ("prompt_cache_enabled", hasattr(settings, "prompt_cache_enabled")),
            ("cache_ttl_search", hasattr(settings, "cache_ttl_search")),
        ]
        
        for name, exists in config_checks:
            status = "✓" if exists else "✗"
            print(f"  {status} {name}: {'存在' if exists else '缺失'}")
            if not exists:
                all_passed = False
                
    except Exception as e:
        print(f"  ✗ 配置检查失败: {e}")
        all_passed = False
    
    # 5. 检查依赖
    print("\n📚 依赖检查")
    print("-" * 40)
    
    try:
        import langchain_community
        print(f"  ✓ langchain_community: 已安装")
    except ImportError:
        print(f"  ✗ langchain_community: 未安装")
        all_passed = False
    
    try:
        import rank_bm25
        print(f"  ✓ rank_bm25: 已安装")
    except ImportError:
        print(f"  ⚠ rank_bm25: 未安装（BM25功能将受限）")
    
    try:
        import redis
        print(f"  ✓ redis: 已安装")
    except ImportError:
        print(f"  ✗ redis: 未安装")
        all_passed = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有检查通过！")
    else:
        print("❌ 部分检查未通过，请修复后再试")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
