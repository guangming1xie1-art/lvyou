"""
多厂商嵌入模型适配器测试
演示如何使用适配器模式切换不同的嵌入模型
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag.embeddings import EmbeddingFactory, EmbeddingAdapter
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_embedding_adapter(provider: str, test_text: str = "北京旅游"):
    """
    测试指定提供商的嵌入适配器
    
    Args:
        provider: 提供商名称 (openai, qwen, glm, kimi, huggingface)
        test_text: 测试文本
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing {provider.upper()} Embedding Adapter")
    logger.info(f"{'='*60}")
    
    try:
        # 获取嵌入适配器
        embeddings: EmbeddingAdapter = EmbeddingFactory.get_embeddings(provider=provider)
        
        # 测试单文本嵌入
        logger.info(f"\n1. 测试单文本嵌入:")
        logger.info(f"   文本: '{test_text}'")
        vector = embeddings.embed_query(test_text)
        logger.info(f"   向量维度: {len(vector)}")
        logger.info(f"   前5个值: {vector[:5]}")
        
        # 测试多文本嵌入
        logger.info(f"\n2. 测试多文本嵌入:")
        texts = ["北京故宫", "上海外滩", "广州塔"]
        logger.info(f"   文本: {texts}")
        vectors = embeddings.embed_documents(texts)
        logger.info(f"   生成 {len(vectors)} 个向量")
        logger.info(f"   每个向量维度: {len(vectors[0])}")
        
        # 测试获取维度
        logger.info(f"\n3. 测试获取维度:")
        dimension = embeddings.get_dimension()
        logger.info(f"   模型维度: {dimension}")
        
        # 验证维度一致性
        assert len(vector) == dimension, f"单文本向量维度 ({len(vector)}) 与 get_dimension() ({dimension}) 不一致"
        assert len(vectors[0]) == dimension, f"多文本向量维度 ({len(vectors[0])}) 与 get_dimension() ({dimension}) 不一致"
        
        logger.info(f"\n✅ {provider.upper()} 适配器测试通过!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ {provider.upper()} 适配器测试失败: {e}")
        return False


def test_backward_compatibility():
    """测试向后兼容性"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing Backward Compatibility")
    logger.info(f"{'='*60}")
    
    try:
        from rag.embeddings import embed_text, embed_texts
        
        # 测试 embed_text
        logger.info(f"\n1. 测试 embed_text():")
        vector = embed_text("向后兼容测试")
        logger.info(f"   向量维度: {len(vector)}")
        
        # 测试 embed_texts
        logger.info(f"\n2. 测试 embed_texts():")
        vectors = embed_texts(["测试1", "测试2", "测试3"])
        logger.info(f"   生成 {len(vectors)} 个向量")
        
        logger.info(f"\n✅ 向后兼容性测试通过!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 向后兼容性测试失败: {e}")
        return False


def test_cache_mechanism():
    """测试缓存机制"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing Cache Mechanism")
    logger.info(f"{'='*60}")
    
    try:
        # 第一次获取
        logger.info(f"\n1. 第一次获取 OpenAI 适配器:")
        embeddings1 = EmbeddingFactory.get_embeddings(provider="openai")
        cached_providers = EmbeddingFactory.get_cached_providers()
        logger.info(f"   缓存中的提供商: {cached_providers}")
        
        # 第二次获取（应该从缓存中返回）
        logger.info(f"\n2. 第二次获取 OpenAI 适配器（应该使用缓存）:")
        embeddings2 = EmbeddingFactory.get_embeddings(provider="openai")
        cached_providers = EmbeddingFactory.get_cached_providers()
        logger.info(f"   缓存中的提供商: {cached_providers}")
        
        # 验证是同一个实例
        assert embeddings1 is embeddings2, "两次获取的不是同一个实例，缓存可能未生效"
        
        logger.info(f"\n✅ 缓存机制测试通过!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 缓存机制测试失败: {e}")
        return False


def test_switching_providers():
    """测试切换不同提供商"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing Provider Switching")
    logger.info(f"{'='*60}")
    
    try:
        test_text = "切换提供商测试"
        
        # 测试 OpenAI (如果配置了 API key)
        if os.getenv("OPENAI_API_KEY"):
            logger.info(f"\n1. 测试 OpenAI 提供商:")
            openai_embeddings = EmbeddingFactory.get_embeddings(provider="openai")
            vector1 = openai_embeddings.embed_query(test_text)
            logger.info(f"   OpenAI 向量维度: {len(vector1)}")
        
        # 测试其他提供商 (演示统一的接口)
        providers = ["qwen", "glm", "kimi", "huggingface"]
        for provider in providers:
            logger.info(f"\n2. 测试 {provider.upper()} 提供商:")
            try:
                embeddings = EmbeddingFactory.get_embeddings(provider=provider)
                vector = embeddings.embed_query(test_text)
                logger.info(f"   {provider.upper()} 向量维度: {len(vector)}")
                
                # 验证所有提供商都使用相同的接口
                # 这个调用方式对所有提供商都是一样的！
                vectors = embeddings.embed_documents(["测试1", "测试2"])
                logger.info(f"   多文本嵌入成功，维度: {len(vectors[0])}")
                
            except ValueError as e:
                if "API key not found" in str(e):
                    logger.info(f"   ❌ 未配置 {provider.upper()} API key，跳过测试")
                else:
                    logger.error(f"   ❌ {provider.upper()} 测试失败: {e}")
            except ImportError as e:
                logger.info(f"   ⚠️  缺少依赖: {e}")
        
        logger.info(f"\n✅ 提供商切换测试完成!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 提供商切换测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    logger.info("="*60)
    logger.info("Multi-Vendor Embedding Adapter Test Suite")
    logger.info("="*60)
    
    # 测试缓存机制
    cache_test = test_cache_mechanism()
    
    # 测试向后兼容性
    compat_test = test_backward_compatibility()
    
    # 测试一个提供商（OpenAI）
    if os.getenv("OPENAI_API_KEY"):
        openai_test = test_embedding_adapter("openai")
    else:
        logger.info("\n⚠️  未配置 OPENAI_API_KEY，跳过 OpenAI 测试")
        openai_test = None
    
    # 测试其他提供商（无需特定 API key）
    logger.info("\n" + "="*60)
    logger.info("测试提供商切换（演示统一接口）:")
    logger.info("="*60)
    provider_test = test_switching_providers()
    
    # 总结
    logger.info("\n" + "="*60)
    logger.info("Test Summary")
    logger.info("="*60)
    
    tests = {
        "Cache Mechanism": cache_test,
        "Backward Compatibility": compat_test,
        "Provider Switching": provider_test,
    }
    
    if openai_test is not None:
        tests["OpenAI Adapter"] = openai_test
    
    passed = sum(1 for result in tests.values() if result is True)
    total = len(tests)
    
    for test_name, result in tests.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:.<40} {status}")
    
    logger.info(f"\n总计: {passed}/{total} 测试通过")
    
    # 清空缓存
    EmbeddingFactory.reset_cache()
    logger.info("\n缓存已清空")


if __name__ == "__main__":
    main()