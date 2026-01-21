"""
向后兼容导入层 - 使用来自 subgraphs/ 包的 API

NOTE: 如果你的代码原本导入：
    from workflows.subgraphs import build_search_graph

继续保持这个导入方式即可，内部已重定向到 subgraphs/ 包。

新代码建议改为：
    from workflows.subgraphs import build_search_graph
"""

from .subgraphs import (
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
