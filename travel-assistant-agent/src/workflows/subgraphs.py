"""
【第1层】4 个子图 StateGraph（增强版）- 向后兼容层

⚠️  已废弃 ⚠️
    请使用新的模块化导入方式：
    from src.workflows.subgraphs import (
        SubState,
        build_collect_info_graph,
        build_search_graph,
        build_recommend_graph,
        build_booking_graph,
    )

本文件保留用于向后兼容导入，使用 src.workflows.subgraphs 包作为实际实现。
"""
from src.workflows.subgraphs import (
    SubState,
    build_collect_info_graph,
    build_search_graph,
    build_recommend_graph,
    build_booking_graph,
)

__all__ = [
    "SubState",
    "build_collect_info_graph",
    "build_search_graph",
    "build_recommend_graph",
    "build_booking_graph",
]
