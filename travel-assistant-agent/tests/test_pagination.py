"""
分页功能测试
"""
import pytest
from src.utils.pagination import (
    paginate_results,
    sort_items,
    sort_flights,
    sort_hotels,
    filter_by_price_range,
    aggregate_stats
)


class TestPagination:
    """分页功能测试"""

    def test_basic_pagination(self):
        """测试基本分页"""
        items = list(range(1, 101))  # 1-100
        
        result = paginate_results(items, page=1, page_size=10)
        
        assert len(result["items"]) == 10
        assert result["items"] == list(range(1, 11))
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["total"] == 100
        assert result["pagination"]["total_pages"] == 10
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_prev"] is False

    def test_last_page(self):
        """测试最后一页"""
        items = list(range(1, 101))
        
        result = paginate_results(items, page=10, page_size=10)
        
        assert len(result["items"]) == 10
        assert result["items"] == list(range(91, 101))
        assert result["pagination"]["has_next"] is False
        assert result["pagination"]["has_prev"] is True

    def test_partial_last_page(self):
        """测试不满的最后一页"""
        items = list(range(1, 96))  # 95 items
        
        result = paginate_results(items, page=10, page_size=10)
        
        assert len(result["items"]) == 5
        assert result["items"] == list(range(91, 96))
        assert result["pagination"]["total_pages"] == 10

    def test_empty_results(self):
        """测试空结果"""
        items = []
        
        result = paginate_results(items, page=1, page_size=10)
        
        assert len(result["items"]) == 0
        assert result["pagination"]["total"] == 0
        assert result["pagination"]["total_pages"] == 1

    def test_invalid_page_number(self):
        """测试无效页码"""
        items = list(range(1, 51))
        
        # 页码过大，应该返回最后一页
        result = paginate_results(items, page=100, page_size=10)
        assert result["pagination"]["page"] == 5
        
        # 页码为 0，应该变为 1
        result = paginate_results(items, page=0, page_size=10)
        assert result["pagination"]["page"] == 1

    def test_page_size_limits(self):
        """测试页面大小限制"""
        items = list(range(1, 201))
        
        # 超过最大值（100），应该限制为 100
        result = paginate_results(items, page=1, page_size=150)
        assert len(result["items"]) == 100
        
        # 小于 1，应该变为 1
        result = paginate_results(items, page=1, page_size=0)
        assert len(result["items"]) >= 1


class TestSorting:
    """排序功能测试"""

    def test_sort_by_number_asc(self):
        """测试数值升序排序"""
        items = [
            {"id": 1, "price": 500},
            {"id": 2, "price": 300},
            {"id": 3, "price": 700},
        ]
        
        sorted_items = sort_items(items, sort_by="price", sort_order="asc")
        
        assert sorted_items[0]["price"] == 300
        assert sorted_items[1]["price"] == 500
        assert sorted_items[2]["price"] == 700

    def test_sort_by_number_desc(self):
        """测试数值降序排序"""
        items = [
            {"id": 1, "rating": 4.5},
            {"id": 2, "rating": 4.8},
            {"id": 3, "rating": 4.2},
        ]
        
        sorted_items = sort_items(items, sort_by="rating", sort_order="desc")
        
        assert sorted_items[0]["rating"] == 4.8
        assert sorted_items[1]["rating"] == 4.5
        assert sorted_items[2]["rating"] == 4.2

    def test_sort_with_missing_field(self):
        """测试字段缺失的排序"""
        items = [
            {"id": 1, "price": 500},
            {"id": 2},  # 缺少 price
            {"id": 3, "price": 300},
        ]
        
        sorted_items = sort_items(items, sort_by="price", sort_order="asc")
        
        # 缺失字段的应该排在最后
        assert sorted_items[0]["price"] == 300
        assert sorted_items[1]["price"] == 500
        assert "price" not in sorted_items[2]

    def test_sort_empty_list(self):
        """测试空列表排序"""
        items = []
        
        sorted_items = sort_items(items, sort_by="price")
        
        assert sorted_items == []


class TestFlightSorting:
    """航班排序测试"""

    def test_sort_flights_by_price(self):
        """测试按价格排序航班"""
        flights = [
            {"id": "F1", "price": 800, "duration": 300},
            {"id": "F2", "price": 600, "duration": 250},
            {"id": "F3", "price": 1000, "duration": 200},
        ]
        
        sorted_flights = sort_flights(flights, sort_by="price")
        
        assert sorted_flights[0]["id"] == "F2"
        assert sorted_flights[1]["id"] == "F1"
        assert sorted_flights[2]["id"] == "F3"

    def test_sort_flights_by_duration(self):
        """测试按时长排序航班"""
        flights = [
            {"id": "F1", "price": 800, "duration": 300},
            {"id": "F2", "price": 600, "duration": 250},
            {"id": "F3", "price": 1000, "duration": 200},
        ]
        
        sorted_flights = sort_flights(flights, sort_by="duration")
        
        assert sorted_flights[0]["id"] == "F3"
        assert sorted_flights[1]["id"] == "F2"
        assert sorted_flights[2]["id"] == "F1"

    def test_sort_flights_by_stops(self):
        """测试按转机次数排序"""
        flights = [
            {"id": "F1", "stops": 2},
            {"id": "F2", "stops": 0},
            {"id": "F3", "stops": 1},
        ]
        
        sorted_flights = sort_flights(flights, sort_by="stops")
        
        assert sorted_flights[0]["stops"] == 0
        assert sorted_flights[1]["stops"] == 1
        assert sorted_flights[2]["stops"] == 2


class TestHotelSorting:
    """酒店排序测试"""

    def test_sort_hotels_by_price(self):
        """测试按价格排序酒店"""
        hotels = [
            {"id": "H1", "price": 150, "rating": 4.5},
            {"id": "H2", "price": 100, "rating": 4.2},
            {"id": "H3", "price": 200, "rating": 4.8},
        ]
        
        sorted_hotels = sort_hotels(hotels, sort_by="price")
        
        assert sorted_hotels[0]["id"] == "H2"
        assert sorted_hotels[1]["id"] == "H1"
        assert sorted_hotels[2]["id"] == "H3"

    def test_sort_hotels_by_rating(self):
        """测试按评分排序酒店（降序）"""
        hotels = [
            {"id": "H1", "price": 150, "rating": 4.5},
            {"id": "H2", "price": 100, "rating": 4.2},
            {"id": "H3", "price": 200, "rating": 4.8},
        ]
        
        sorted_hotels = sort_hotels(hotels, sort_by="rating")
        
        assert sorted_hotels[0]["rating"] == 4.8
        assert sorted_hotels[1]["rating"] == 4.5
        assert sorted_hotels[2]["rating"] == 4.2


class TestFiltering:
    """过滤功能测试"""

    def test_filter_by_min_price(self):
        """测试最低价格过滤"""
        items = [
            {"id": 1, "price": 100},
            {"id": 2, "price": 200},
            {"id": 3, "price": 300},
        ]
        
        filtered = filter_by_price_range(items, min_price=150)
        
        assert len(filtered) == 2
        assert all(item["price"] >= 150 for item in filtered)

    def test_filter_by_max_price(self):
        """测试最高价格过滤"""
        items = [
            {"id": 1, "price": 100},
            {"id": 2, "price": 200},
            {"id": 3, "price": 300},
        ]
        
        filtered = filter_by_price_range(items, max_price=250)
        
        assert len(filtered) == 2
        assert all(item["price"] <= 250 for item in filtered)

    def test_filter_by_price_range(self):
        """测试价格范围过滤"""
        items = [
            {"id": 1, "price": 100},
            {"id": 2, "price": 200},
            {"id": 3, "price": 300},
            {"id": 4, "price": 400},
        ]
        
        filtered = filter_by_price_range(items, min_price=150, max_price=350)
        
        assert len(filtered) == 2
        assert all(150 <= item["price"] <= 350 for item in filtered)


class TestAggregation:
    """聚合功能测试"""

    def test_aggregate_stats(self):
        """测试统计聚合"""
        items = [
            {"id": 1, "price": 100},
            {"id": 2, "price": 200},
            {"id": 3, "price": 300},
            {"id": 4, "price": 400},
            {"id": 5, "price": 500},
        ]
        
        stats = aggregate_stats(items, "price")
        
        assert stats["count"] == 5
        assert stats["min"] == 100
        assert stats["max"] == 500
        assert stats["avg"] == 300
        assert stats["median"] == 300

    def test_aggregate_stats_odd_count(self):
        """测试奇数个项目的统计"""
        items = [
            {"id": 1, "value": 10},
            {"id": 2, "value": 20},
            {"id": 3, "value": 30},
        ]
        
        stats = aggregate_stats(items, "value")
        
        assert stats["median"] == 20

    def test_aggregate_stats_even_count(self):
        """测试偶数个项目的统计"""
        items = [
            {"id": 1, "value": 10},
            {"id": 2, "value": 20},
            {"id": 3, "value": 30},
            {"id": 4, "value": 40},
        ]
        
        stats = aggregate_stats(items, "value")
        
        assert stats["median"] == 25  # (20 + 30) / 2

    def test_aggregate_stats_empty(self):
        """测试空列表统计"""
        items = []
        
        stats = aggregate_stats(items, "price")
        
        assert stats["count"] == 0
        assert stats["min"] is None
        assert stats["max"] is None
        assert stats["avg"] is None


class TestIntegration:
    """集成测试 - 分页 + 排序 + 过滤"""

    def test_combined_operations(self):
        """测试组合操作"""
        # 准备数据
        flights = [
            {"id": f"F{i}", "price": 500 + i * 50, "duration": 200 + i * 10}
            for i in range(20)
        ]
        
        # 1. 价格过滤
        filtered = filter_by_price_range(flights, min_price=600, max_price=900)
        assert len(filtered) < len(flights)
        
        # 2. 按价格排序
        sorted_flights = sort_flights(filtered, sort_by="price")
        
        # 3. 分页
        result = paginate_results(sorted_flights, page=1, page_size=5)
        
        # 验证
        assert len(result["items"]) <= 5
        assert result["pagination"]["total"] == len(filtered)
        
        # 验证排序正确
        prices = [f["price"] for f in result["items"]]
        assert prices == sorted(prices)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
