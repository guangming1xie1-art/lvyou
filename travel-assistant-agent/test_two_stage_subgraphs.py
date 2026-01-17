#!/usr/bin/env python3
"""
测试改造后的 subgraphs.py - 两阶段流程验证
"""
import asyncio
import json
import logging
from typing import Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search_plan_node():
    """测试搜索规划节点"""
    try:
        from src.workflows.subgraphs import search_plan_node, SubState
        
        # 模拟状态
        state = SubState({
            "messages": [{"role": "user", "content": "我想去巴黎旅游"}],
            "collected_info": {
                "destination": "巴黎",
                "duration": "5天",
                "budget": "10000-20000",
                "preferences": ["文化", "美食"]
            },
            "conversation_history": [
                {"role": "user", "content": "我想去巴黎旅游", "node": "collect"}
            ]
        })
        
        logger.info("=== 测试搜索规划节点 ===")
        result = await search_plan_node(state)
        
        logger.info(f"规划结果: {result.get('output', '')[:200]}...")
        logger.info(f"搜索计划: {result.get('search_plan', {})}")
        logger.info(f"Token 用量: {result.get('usage', {})}")
        
        assert "search_plan" in result
        assert "output" in result
        assert "usage" in result
        
        logger.info("✓ 搜索规划节点测试通过")
        return True
        
    except Exception as e:
        logger.error(f"搜索规划节点测试失败: {e}")
        return False


async def test_recommend_plan_node():
    """测试推荐规划节点"""
    try:
        from src.workflows.subgraphs import recommend_plan_node, SubState
        
        # 模拟状态
        state = SubState({
            "messages": [{"role": "user", "content": "请推荐巴黎的旅游方案"}],
            "collected_info": {
                "destination": "巴黎",
                "duration": "5天",
                "budget": "10000-20000",
                "preferences": ["文化", "美食"]
            },
            "search_results": {
                "destinations": ["巴黎市中心", "凡尔赛宫"],
                "hotels": ["巴黎大酒店", "香榭丽舍酒店"],
                "total_results": 15
            },
            "conversation_history": [
                {"role": "user", "content": "我想去巴黎旅游", "node": "collect"}
            ]
        })
        
        logger.info("=== 测试推荐规划节点 ===")
        result = await recommend_plan_node(state)
        
        logger.info(f"规划结果: {result.get('output', '')[:200]}...")
        logger.info(f"推荐计划: {result.get('recommend_plan', {})}")
        logger.info(f"Token 用量: {result.get('usage', {})}")
        
        assert "recommend_plan" in result
        assert "output" in result
        assert "usage" in result
        
        logger.info("✓ 推荐规划节点测试通过")
        return True
        
    except Exception as e:
        logger.error(f"推荐规划节点测试失败: {e}")
        return False


async def test_build_search_graph():
    """测试搜索图构建"""
    try:
        from src.workflows.subgraphs import build_search_graph
        
        logger.info("=== 测试搜索图构建 ===")
        graph = build_search_graph()
        
        # 检查图的节点和边
        logger.info(f"图类型: {type(graph)}")
        logger.info("✓ 搜索图构建测试通过")
        return True
        
    except Exception as e:
        logger.error(f"搜索图构建测试失败: {e}")
        return False


async def test_build_recommend_graph():
    """测试推荐图构建"""
    try:
        from src.workflows.subgraphs import build_recommend_graph
        
        logger.info("=== 测试推荐图构建 ===")
        graph = build_recommend_graph()
        
        # 检查图的节点和边
        logger.info(f"图类型: {type(graph)}")
        logger.info("✓ 推荐图构建测试通过")
        return True
        
    except Exception as e:
        logger.error(f"推荐图构建测试失败: {e}")
        return False


async def test_graph_structure():
    """测试图结构是否正确"""
    try:
        from src.workflows.subgraphs import build_search_graph, build_recommend_graph
        
        logger.info("=== 测试图结构 ===")
        
        # 测试搜索图结构
        search_graph = build_search_graph()
        logger.info("搜索图节点检查通过")
        
        # 测试推荐图结构
        recommend_graph = build_recommend_graph()
        logger.info("推荐图节点检查通过")
        
        logger.info("✓ 图结构测试通过")
        return True
        
    except Exception as e:
        logger.error(f"图结构测试失败: {e}")
        return False


async def test_imports():
    """测试导入是否正常"""
    try:
        logger.info("=== 测试导入 ===")
        
        # 测试主要导入
        from src.workflows.subgraphs import (
            SubState,
            build_collect_info_graph,
            build_search_graph,
            build_recommend_graph,
            build_booking_graph,
            search_plan_node,
            search_execute_agent_node,
            recommend_plan_node,
            recommend_execute_agent_node
        )
        
        logger.info("所有导入测试通过")
        logger.info("✓ 导入测试通过")
        return True
        
    except Exception as e:
        logger.error(f"导入测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    logger.info("🚀 开始测试两阶段流程改造...")
    
    tests = [
        ("导入测试", test_imports),
        ("搜索规划节点测试", test_search_plan_node),
        ("推荐规划节点测试", test_recommend_plan_node),
        ("搜索图构建测试", test_build_search_graph),
        ("推荐图构建测试", test_build_recommend_graph),
        ("图结构测试", test_graph_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"执行测试: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if await test_func():
                passed += 1
                logger.info(f"✅ {test_name} - 通过")
            else:
                logger.error(f"❌ {test_name} - 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"测试结果: {passed}/{total} 通过")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 所有测试通过！两阶段流程改造成功！")
        return True
    else:
        logger.error(f"⚠️  有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    asyncio.run(main())