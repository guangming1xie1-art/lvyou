"""
工作流模块 - 提供四个独立的 LangGraph 工作流

结构：
- common: 共享工具、状态定义、组件
- collect: 信息收集工作流
- search: 搜索工作流（规划+执行两阶段）
- recommend: 推荐工作流（规划+执行两阶段）
- booking: 预订工作流
"""

from .common import SubState
from .collect import build_collect_info_graph
from .search import build_search_graph
from .recommend import build_recommend_graph
from .booking import build_booking_graph

__all__ = [
    "SubState",
    "build_collect_info_graph",
    "build_search_graph",
    "build_recommend_graph",
    "build_booking_graph",
]
