"""
【第2层】CompiledSubAgent 包装器

使用 deepagents.CompiledSubAgent 包装子图
每个 CompiledSubAgent 提供统一的 invoke() 接口
"""
from deepagents import CompiledSubAgent
from src.workflows.subgraphs import (
    build_collect_info_graph,
    build_search_graph,
    build_recommend_graph,
    build_booking_graph,
)
import logging

logger = logging.getLogger(__name__)


# ============ 全局实例（懒加载）============

_info_collection_agent = None
_search_agent = None
_recommend_agent = None
_booking_agent = None


def get_info_collection_agent() -> CompiledSubAgent:
    """获取信息收集子代理"""
    global _info_collection_agent
    if _info_collection_agent is None:
        logger.info("Creating info_collection_agent...")
        _info_collection_agent = CompiledSubAgent(
            name="info_collection",
            runnable=build_collect_info_graph(),
            system_prompt="你是信息收集员，只负责收集用户的旅游需求并总结。"
        )
    return _info_collection_agent


def get_search_agent() -> CompiledSubAgent:
    """获取搜索子代理"""
    global _search_agent
    if _search_agent is None:
        logger.info("Creating search_agent...")
        _search_agent = CompiledSubAgent(
            name="search",
            runnable=build_search_graph(),
            system_prompt="你是搜索员，收到需求总结后返回目的地、酒店、航班等信息。"
        )
    return _search_agent


def get_recommend_agent() -> CompiledSubAgent:
    """获取推荐子代理"""
    global _recommend_agent
    if _recommend_agent is None:
        logger.info("Creating recommend_agent...")
        _recommend_agent = CompiledSubAgent(
            name="recommend",
            runnable=build_recommend_graph(),
            system_prompt="你是推荐员，基于用户需求和搜索结果生成个性化旅游方案。"
        )
    return _recommend_agent


def get_booking_agent() -> CompiledSubAgent:
    """获取预订子代理"""
    global _booking_agent
    if _booking_agent is None:
        logger.info("Creating booking_agent...")
        _booking_agent = CompiledSubAgent(
            name="booking",
            runnable=build_booking_graph(),
            system_prompt="你是预订员，完成用户选定的预订。"
        )
    return _booking_agent


__all__ = [
    "get_info_collection_agent",
    "get_search_agent",
    "get_recommend_agent",
    "get_booking_agent",
]
