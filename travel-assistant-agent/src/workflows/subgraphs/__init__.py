"""
【第1层】子图模块包

包含四个独立的子图模块：
- common: 共享工具和状态定义
- collect: 信息收集子图
- search: 搜索子图
- recommend: 推荐子图
- booking: 预订子图
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
