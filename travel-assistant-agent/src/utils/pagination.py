"""
分页和排序工具
提供统一的分页和排序功能
"""
from typing import List, Dict, Any, Callable
import math


def paginate_results(
    items: List[Any],
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    对结果进行分页

    Args:
        items: 要分页的项目列表
        page: 页码（从 1 开始）
        page_size: 每页数量

    Returns:
        包含分页数据和元数据的字典
    """
    # 确保参数有效
    page = max(1, page)
    page_size = max(1, min(100, page_size))  # 最大 100 per page
    
    # 计算分页
    total = len(items)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # 确保页码在有效范围内
    page = min(page, total_pages)
    
    # 计算起止索引
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)
    
    # 获取当前页数据
    page_items = items[start_idx:end_idx]
    
    # 返回分页结果
    return {
        "items": page_items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
        }
    }


def sort_items(
    items: List[Dict[str, Any]],
    sort_by: str = "price",
    sort_order: str = "asc",
    default_value: Any = float('inf')
) -> List[Dict[str, Any]]:
    """
    对项目进行排序

    Args:
        items: 要排序的项目列表
        sort_by: 排序字段
        sort_order: 排序顺序 (asc/desc)
        default_value: 缺失字段的默认值

    Returns:
        排序后的项目列表
    """
    if not items:
        return items
    
    # 确保排序顺序有效
    reverse = sort_order.lower() == "desc"
    
    # 排序函数，处理缺失字段
    def get_sort_key(item: Dict[str, Any]) -> Any:
        # 支持嵌套字段（如 "price.amount"）
        keys = sort_by.split(".")
        value = item
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default_value
        
        # 确保数值可比较
        if value is None:
            return default_value
        
        return value
    
    try:
        return sorted(items, key=get_sort_key, reverse=reverse)
    except Exception:
        # 如果排序失败，返回原列表
        return items


def sort_flights(
    flights: List[Dict[str, Any]],
    sort_by: str = "price"
) -> List[Dict[str, Any]]:
    """
    对航班进行排序

    支持的排序字段:
    - price: 价格（升序）
    - duration: 飞行时长（升序）
    - departure: 起飞时间（升序）
    - arrival: 到达时间（升序）
    - stops: 转机次数（升序）

    Args:
        flights: 航班列表
        sort_by: 排序字段

    Returns:
        排序后的航班列表
    """
    sort_configs = {
        "price": ("price", "asc", float('inf')),
        "duration": ("duration", "asc", float('inf')),
        "departure": ("departure_time", "asc", ""),
        "arrival": ("arrival_time", "asc", ""),
        "stops": ("stops", "asc", float('inf')),
    }
    
    if sort_by not in sort_configs:
        sort_by = "price"
    
    field, order, default = sort_configs[sort_by]
    return sort_items(flights, field, order, default)


def sort_hotels(
    hotels: List[Dict[str, Any]],
    sort_by: str = "price"
) -> List[Dict[str, Any]]:
    """
    对酒店进行排序

    支持的排序字段:
    - price: 价格（升序）
    - rating: 评分（降序）
    - distance: 距离市中心距离（升序）
    - popularity: 受欢迎程度（降序）

    Args:
        hotels: 酒店列表
        sort_by: 排序字段

    Returns:
        排序后的酒店列表
    """
    sort_configs = {
        "price": ("price", "asc", float('inf')),
        "rating": ("rating", "desc", 0),
        "distance": ("distance_from_center", "asc", float('inf')),
        "popularity": ("popularity_score", "desc", 0),
    }
    
    if sort_by not in sort_configs:
        sort_by = "price"
    
    field, order, default = sort_configs[sort_by]
    return sort_items(hotels, field, order, default)


def filter_by_price_range(
    items: List[Dict[str, Any]],
    min_price: float = None,
    max_price: float = None,
    price_field: str = "price"
) -> List[Dict[str, Any]]:
    """
    按价格范围过滤项目

    Args:
        items: 项目列表
        min_price: 最低价格
        max_price: 最高价格
        price_field: 价格字段名

    Returns:
        过滤后的项目列表
    """
    if not items:
        return items
    
    filtered = items
    
    if min_price is not None:
        filtered = [
            item for item in filtered
            if item.get(price_field, 0) >= min_price
        ]
    
    if max_price is not None:
        filtered = [
            item for item in filtered
            if item.get(price_field, float('inf')) <= max_price
        ]
    
    return filtered


def aggregate_stats(items: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
    """
    计算字段的统计信息

    Args:
        items: 项目列表
        field: 要统计的字段

    Returns:
        统计信息字典
    """
    if not items:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "avg": None,
            "median": None
        }
    
    values = []
    for item in items:
        value = item.get(field)
        if value is not None and isinstance(value, (int, float)):
            values.append(value)
    
    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "avg": None,
            "median": None
        }
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    median = (
        sorted_values[n // 2] if n % 2 == 1
        else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    )
    
    return {
        "count": n,
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / n,
        "median": median
    }
