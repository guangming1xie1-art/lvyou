"""【第2层】CompiledSubAgent 包装器

为每个业务模块创建 CompiledSubAgent，包装对应的 StateGraph 子图。
"""

from __future__ import annotations

from typing import Optional
import logging

from deepagents import CompiledSubAgent

from src.workflows.subgraphs import (
    build_collect_info_graph,
    build_search_graph,
    build_recommend_graph,
    build_booking_graph,
)

logger = logging.getLogger(__name__)


# ============ 创建 4 个 CompiledSubAgent 实例（懒加载单例） ============

_info_collection_agent: Optional[CompiledSubAgent] = None
_search_agent: Optional[CompiledSubAgent] = None
_recommend_agent: Optional[CompiledSubAgent] = None
_booking_agent: Optional[CompiledSubAgent] = None


def get_info_collection_agent() -> CompiledSubAgent:
    """获取信息收集子代理（懒加载）"""
    global _info_collection_agent
    if _info_collection_agent is None:
        _info_collection_agent = CompiledSubAgent(
            name="info_collection",
            runnable=build_collect_info_graph(),
            system_prompt="你是信息收集员，只负责收集需求并总结。",
        )
    return _info_collection_agent


def get_search_agent() -> CompiledSubAgent:
    """获取搜索子代理（懒加载）"""
    global _search_agent
    if _search_agent is None:
        _search_agent = CompiledSubAgent(
            name="search",
            runnable=build_search_graph(),
            system_prompt="你是搜索员，收到需求总结后返回目的地 JSON。",
        )
    return _search_agent


def get_recommend_agent() -> CompiledSubAgent:
    """获取推荐子代理（懒加载）"""
    global _recommend_agent
    if _recommend_agent is None:
        _recommend_agent = CompiledSubAgent(
            name="recommend",
            runnable=build_recommend_graph(),
            system_prompt="你是推荐员，基于需求和搜索结果生成个性化方案。",
        )
    return _recommend_agent


def get_booking_agent() -> CompiledSubAgent:
    """获取预订子代理（懒加载）"""
    global _booking_agent
    if _booking_agent is None:
        _booking_agent = CompiledSubAgent(
            name="booking",
            runnable=build_booking_graph(),
            system_prompt="你是预订员，完成用户选定的预订。",
        )
    return _booking_agent


__all__ = [
    "CompiledSubAgent",
    "get_info_collection_agent",
    "get_search_agent",
    "get_recommend_agent",
    "get_booking_agent",
]
