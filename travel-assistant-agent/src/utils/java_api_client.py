"""
Java API 客户端工具

用于与 Java 后端服务通信的统一接口。
提供搜索、推荐、预订等功能的 API 调用方法。
支持异步请求、重试机制、超时控制和统一错误处理。

使用方式:
    from utils.java_api_client import java_api_client, JavaAPIClient

    # 搜索航班
    flights = await java_api_client.search_flights(
        origin="Beijing",
        destination="Tokyo",
        departure_date="2025-02-01",
        passengers=2
    )
"""
from typing import Any, Dict, List, Optional
import asyncio
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import settings
from utils.logger import app_logger


# =============================================================================
# 自定义异常类
# =============================================================================

class JavaAPIError(Exception):
    """Java API 通用异常"""
    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class JavaAPITimeoutError(JavaAPIError):
    """超时异常"""
    pass


class JavaAPINotFoundError(JavaAPIError):
    """资源不存在异常 (404)"""
    pass


class JavaAPIValidationError(JavaAPIError):
    """验证错误异常 (400)"""
    pass


class JavaAPIServerError(JavaAPIError):
    """服务器错误异常 (5xx)"""
    pass


class JavaAPIAuthError(JavaAPIError):
    """认证错误异常 (401/403)"""
    pass


# =============================================================================
# Mock 数据生成器 (用于测试，在Java API不可用时返回模拟数据)
# =============================================================================

class MockDataGenerator:
    """生成模拟数据的工具类"""

    @staticmethod
    def generate_mock_flights(
        origin: str,
        destination: str,
        departure_date: str,
        passengers: int,
        cabin_class: str = "economy"
    ) -> List[Dict[str, Any]]:
        """生成模拟航班数据"""
        cabin_multiplier = {
            "economy": 1.0,
            "premium_economy": 1.5,
            "business": 3.0,
            "first": 5.0
        }.get(cabin_class, 1.0)

        airlines = ["Air China", "Japan Airlines", "ANA", "Delta", "United"]
        base_price = 500 + hash(f"{origin}{destination}") % 1000

        flights = []
        for i in range(5):
            flights.append({
                "flight_id": f"FL{hash(f'{origin}{destination}{i}') % 100000:06d}",
                "airline": airlines[i % len(airlines)],
                "origin": origin,
                "destination": destination,
                "departure_time": f"{departure_date}T0{i+6}:00:00",
                "arrival_time": f"{departure_date}T0{i+8 + (i % 3)}:30:00",
                "duration_hours": 3 + (i % 4),
                "cabin_class": cabin_class,
                "price": int(base_price * cabin_multiplier * (0.9 + i * 0.05)),
                "available_seats": 10 + i * 5,
                "stops": i % 2,
                "aircraft": f"Boeing {737 + i % 3}"
            })
        return flights

    @staticmethod
    def generate_mock_hotels(
        destination: str,
        check_in: str,
        check_out: str,
        guests: int
    ) -> List[Dict[str, Any]]:
        """生成模拟酒店数据"""
        hotels = []
        hotel_names = [
            f"Grand {destination} Hotel",
            f"{destination} Marriott",
            f"Hilton {destination}",
            f"{destination} Sheraton",
            f"Royal {destination} Resort"
        ]
        star_ratings = [5, 4, 4, 5, 3]

        for i in range(5):
            nights = 3  # 默认3晚
            base_price = 100 + star_ratings[i] * 50
            hotels.append({
                "hotel_id": f"HTL{hash(f'{destination}{i}') % 100000:06d}",
                "name": hotel_names[i],
                "destination": destination,
                "address": f"{i+1} Main Street, {destination}",
                "star_rating": star_ratings[i],
                "rating": 4.0 + (i % 5) * 0.2,
                "review_count": 100 + i * 50,
                "price_per_night": int(base_price * (0.9 + i * 0.05)),
                "total_price": int(base_price * nights * (0.9 + i * 0.05)),
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant"][:2 + i % 3],
                "images": [f"https://example.com/hotel_{i}.jpg"]
            })
        return hotels

    @staticmethod
    def generate_mock_destination_info(destination: str) -> Dict[str, Any]:
        """生成模拟目的地信息"""
        return {
            "name": destination,
            "country": "Japan" if destination.lower() in ["tokyo", "osaka", "kyoto"] else "Unknown",
            "description": f"{destination} 是一个迷人的旅游目的地，拥有丰富的文化和自然景观。",
            "best_season": "春季和秋季",
            "average_temperature": 15,
            "currency": "JPY",
            "language": "日语",
            "time_zone": "UTC+9",
            "highlights": [
                f"{destination} 著名景点 1",
                f"{destination} 著名景点 2",
                f"{destination} 著名景点 3"
            ],
            "local_cuisine": ["拉面", "寿司", "烤肉"],
            "transportation_tips": "建议购买交通卡以便出行"
        }

    @staticmethod
    def generate_mock_attractions(destination: str) -> List[Dict[str, Any]]:
        """生成模拟景点数据"""
        attractions = []
        attraction_names = [
            f"{destination} 必游景点",
            f"{destination} 文化遗址",
            f"{destination} 自然公园",
            f"{destination} 博物馆",
            f"{destination} 购物区"
        ]
        categories = ["culture", "nature", "museum", "shopping", "entertainment"]

        for i in range(5):
            attractions.append({
                "attraction_id": f"ATTR{hash(f'{destination}{i}') % 100000:06d}",
                "name": attraction_names[i],
                "destination": destination,
                "category": categories[i % len(categories)],
                "rating": 4.0 + (i % 5) * 0.2,
                "review_count": 50 + i * 20,
                "opening_hours": "09:00-18:00",
                "ticket_price": 500 + i * 100,
                "description": f"这是 {attraction_names[i]} 的详细介绍。",
                "address": f"{i+1} Tourism Street, {destination}",
                "duration_hours": 2 + i % 3
            })
        return attractions

    @staticmethod
    def generate_mock_weather_forecast(destination: str, date: str) -> Dict[str, Any]:
        """生成模拟天气预报"""
        return {
            "destination": destination,
            "date": date,
            "temperature": 10 + hash(date) % 15,
            "weather": "晴朗" if hash(date) % 3 != 0 else "多云",
            "humidity": 40 + hash(f"{destination}{date}") % 40,
            "wind_speed": 10 + hash(f"{date}") % 20,
            "precipitation_chance": hash(f"{destination}{date}") % 50,
            "clothing_suggestion": "建议穿着轻薄衣物，携带雨具"
        }

    @staticmethod
    def generate_mock_booking_confirmation(booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成模拟预订确认"""
        import uuid
        return {
            "booking_id": f"BK{uuid.uuid4().hex[:12].upper()}",
            "status": "confirmed",
            "confirmation_number": f"CNF{uuid.uuid4().hex[:8].upper()}",
            "created_at": "2025-01-15T10:30:00",
            "payment_status": "paid",
            "total_amount": booking_data.get("estimated_budget", 5000),
            "details": booking_data
        }


# =============================================================================
# Java API 客户端类
# =============================================================================

class JavaAPIClient:
    """
    Java 后端 API 客户端

    提供与 Java 后端服务通信的统一接口，支持：
    - 异步 HTTP 请求
    - 指数退避重试机制
    - 超时控制
    - 统一错误处理
    - Mock 数据 fallback

    使用单例模式确保全局只有一个客户端实例。

    Attributes:
        base_url: Java API 的基础 URL
        timeout: 请求超时时间（秒）
        max_retries: 最大重试次数
        use_mock_on_failure: 当 API 不可用时是否返回 mock 数据
    """

    _instance: Optional['JavaAPIClient'] = None
    _client: Optional[httpx.AsyncClient] = None

    def __new__(cls) -> 'JavaAPIClient':
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化 Java API 客户端"""
        if self._client is not None:
            return

        # 从配置获取参数
        self.base_url = settings.java_api_base_url or "http://localhost:8080/api"
        self.timeout = settings.java_api_timeout or 30
        self.max_retries = settings.java_api_max_retries or 3
        self.use_mock_on_failure = True  # 默认开启 mock fallback

        # 初始化 HTTP 客户端
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_headers()
        )

        app_logger.info(f"JavaAPIClient initialized: base_url={self.base_url}")

    def _get_headers(self) -> Dict[str, str]:
        """获取默认请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if settings.java_api_auth_token:
            headers["Authorization"] = f"Bearer {settings.java_api_auth_token}"
        return headers

    def _update_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """更新请求头"""
        default_headers = self._get_headers()
        if headers:
            default_headers.update(headers)
        return default_headers

    # =============================================================================
    # 内部请求方法
    # =============================================================================

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json: Dict = None,
        headers: Dict = None
    ) -> Dict[str, Any]:
        """
        内部 HTTP 请求方法

        处理请求执行、响应解析和错误处理。

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点路径
            params: URL 查询参数
            json: 请求体 JSON 数据
            headers: 自定义请求头

        Returns:
            API 响应数据 (字典格式)

        Raises:
            JavaAPITimeoutError: 请求超时时
            JavaAPINotFoundError: 资源不存在时
            JavaAPIValidationError: 参数验证错误时
            JavaAPIServerError: 服务器错误时
            JavaAPIAuthError: 认证错误时
            JavaAPIError: 其他 API 错误时
        """
        url = endpoint
        request_headers = self._update_headers(headers)

        app_logger.debug(f"API Request: {method} {url} params={params}")

        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=request_headers
            )

            return await self._handle_response(response)

        except httpx.TimeoutException:
            app_logger.error(f"API Timeout: {method} {url}")
            raise JavaAPITimeoutError(
                f"Request timeout after {self.timeout}s",
                status_code=408
            )
        except httpx.ConnectError as e:
            app_logger.warning(f"API Connection Error: {e}")
            if self.use_mock_on_failure:
                app_logger.info("Falling back to mock data")
                return self._get_mock_response(endpoint, json)
            raise JavaAPIError(f"Failed to connect to Java API: {e}")

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        处理 API 响应

        统一解析响应格式，处理业务逻辑错误。

        Args:
            response: HTTP 响应对象

        Returns:
            解析后的响应数据

        Raises:
            各类型 API 异常
        """
        status_code = response.status_code

        # 解析响应内容
        try:
            data = response.json()
        except Exception as e:
            app_logger.error(f"Failed to parse response: {e}")
            raise JavaAPIError(f"Invalid response format: {e}")

        # 检查 HTTP 状态码
        if status_code == 200:
            # 成功响应，检查业务逻辑
            if isinstance(data, dict):
                if data.get("success"):
                    return data.get("data", data)
                else:
                    error_info = data.get("error", {})
                    raise JavaAPIError(
                        message=error_info.get("message", "API error"),
                        status_code=status_code,
                        response=data
                    )
            return data

        # 处理 HTTP 错误状态码
        if status_code == 400:
            raise JavaAPIValidationError(
                message=data.get("error", {}).get("message", "Validation error"),
                status_code=status_code,
                response=data
            )
        elif status_code == 401:
            raise JavaAPIAuthError(
                message="Unauthorized - Invalid or missing authentication",
                status_code=status_code,
                response=data
            )
        elif status_code == 403:
            raise JavaAPIAuthError(
                message="Forbidden - Insufficient permissions",
                status_code=status_code,
                response=data
            )
        elif status_code == 404:
            raise JavaAPINotFoundError(
                message=data.get("error", {}).get("message", "Resource not found"),
                status_code=status_code,
                response=data
            )
        elif status_code >= 500:
            raise JavaAPIServerError(
                message=data.get("error", {}).get("message", "Internal server error"),
                status_code=status_code,
                response=data
            )
        else:
            raise JavaAPIError(
                message=f"Unexpected status code: {status_code}",
                status_code=status_code,
                response=data
            )

    def _get_mock_response(self, endpoint: str, json: Dict = None) -> Dict[str, Any]:
        """
        获取 Mock 响应数据

        当 Java API 不可用时，返回模拟数据。

        Args:
            endpoint: API 端点路径
            json: 请求数据

        Returns:
            Mock 响应数据
        """
        mock_data = {}
        data = json or {}

        if "flights" in endpoint:
            mock_data = {
                "success": True,
                "data": MockDataGenerator.generate_mock_flights(
                    origin=data.get("origin", ""),
                    destination=data.get("destination", ""),
                    departure_date=data.get("departure_date", ""),
                    passengers=data.get("passengers", 1),
                    cabin_class=data.get("cabin_class", "economy")
                )
            }
        elif "hotels" in endpoint:
            mock_data = {
                "success": True,
                "data": MockDataGenerator.generate_mock_hotels(
                    destination=data.get("destination", ""),
                    check_in=data.get("check_in", ""),
                    check_out=data.get("check_out", ""),
                    guests=data.get("guests", 2)
                )
            }
        elif "destination" in endpoint and "info" in endpoint:
            mock_data = {
                "success": True,
                "data": MockDataGenerator.generate_mock_destination_info(
                    data.get("destination", "")
                )
            }
        elif "attractions" in endpoint:
            mock_data = {
                "success": True,
                "data": MockDataGenerator.generate_mock_attractions(
                    data.get("destination", "")
                )
            }
        elif "weather" in endpoint:
            mock_data = {
                "success": True,
                "data": MockDataGenerator.generate_mock_weather_forecast(
                    data.get("destination", ""),
                    data.get("date", "")
                )
            }
        elif "booking" in endpoint and "create" in endpoint:
            mock_data = {
                "success": True,
                "data": MockDataGenerator.generate_mock_booking_confirmation(data)
            }
        else:
            mock_data = {
                "success": True,
                "data": {"message": "Mock response for testing"}
            }

        return mock_data

    # =============================================================================
    # 搜索相关方法 (SearchAgent)
    # =============================================================================

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        passengers: int,
        return_date: str = None,
        cabin_class: str = "economy",
        trip_type: str = "roundtrip"  # roundtrip, oneway, multicity
    ) -> Dict[str, Any]:
        """
        搜索航班

        Args:
            origin: 出发地 (城市代码或名称，如 "Beijing" 或 "PEK")
            destination: 目的地 (城市代码或名称，如 "Tokyo" 或 "NRT")
            departure_date: 出发日期 (YYYY-MM-DD)
            passengers: 乘客数量
            return_date: 返回日期 (可选，YYYY-MM-DD，单程时可不传)
            cabin_class: 舱位等级 (economy, premium_economy, business, first)
            trip_type: 行程类型 (roundtrip, oneway, multicity)

        Returns:
            包含以下键的字典:
                - outbound_flights: 去程航班列表
                - return_flights: 返程航班列表 (单程时为空)
                - search_params: 搜索参数
        """
        endpoint = "/v1/flights/search"
        payload = {
            "origin": origin,
            "destination": destination,
            "departureDate": departure_date,
            "passengers": passengers,
            "cabinClass": cabin_class,
            "tripType": trip_type
        }

        if return_date:
            payload["returnDate"] = return_date

        app_logger.info(f"Searching flights: {origin} -> {destination}")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "outbound_flights": response.get("outboundFlights", response.get("data", [])),
            "return_flights": response.get("returnFlights", []),
            "search_params": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": passengers,
                "cabin_class": cabin_class,
                "trip_type": trip_type
            }
        }

    async def search_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int,
        rooms: int = 1,
        hotel_class: str = None,
        price_min: float = None,
        price_max: float = None,
        amenities: List[str] = None
    ) -> Dict[str, Any]:
        """
        搜索酒店

        Args:
            destination: 目的地城市
            check_in: 入住日期 (YYYY-MM-DD)
            check_out: 退房日期 (YYYY-MM-DD)
            guests: 入住人数
            rooms: 房间数量
            hotel_class: 酒店星级 (3, 4, 5 等)
            price_min: 最低价格
            price_max: 最高价格
            amenities: 设施要求列表 (如 ["WiFi", "Pool"])

        Returns:
            酒店列表和搜索结果信息
        """
        endpoint = "/v1/hotels/search"
        payload = {
            "destination": destination,
            "checkIn": check_in,
            "checkOut": check_out,
            "guests": guests,
            "rooms": rooms
        }

        if hotel_class:
            payload["hotelClass"] = hotel_class
        if price_min:
            payload["priceMin"] = price_min
        if price_max:
            payload["priceMax"] = price_max
        if amenities:
            payload["amenities"] = amenities

        app_logger.info(f"Searching hotels in {destination}")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "hotels": response.get("hotels", response.get("data", [])),
            "search_params": {
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "rooms": rooms,
                "hotel_class": hotel_class,
                "price_range": {"min": price_min, "max": price_max},
                "amenities": amenities
            },
            "total_count": len(response.get("hotels", response.get("data", [])))
        }

    async def compare_flights(
        self,
        flight_ids: List[str],
        sort_by: str = "price"  # price, duration, departure_time
    ) -> Dict[str, Any]:
        """
        比较多个航班

        Args:
            flight_ids: 要比较的航班 ID 列表
            sort_by: 排序方式 (price, duration, departure_time, arrival_time)

        Returns:
            比较结果和排序后的航班列表
        """
        endpoint = "/v1/flights/compare"
        payload = {
            "flightIds": flight_ids,
            "sortBy": sort_by
        }

        app_logger.info(f"Comparing {len(flight_ids)} flights")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "flights": response.get("flights", response.get("data", [])),
            "sorted_by": sort_by,
            "cheapest": response.get("cheapest"),
            "fastest": response.get("fastest"),
            "best_value": response.get("bestValue")
        }

    async def filter_by_budget(
        self,
        search_results: Dict[str, Any],
        max_price: float,
        price_type: str = "total"  # total, per_night
    ) -> Dict[str, Any]:
        """
        按预算过滤搜索结果

        Args:
            search_results: 搜索结果字典 (包含 flights 或 hotels)
            max_price: 最大预算
            price_type: 价格类型 (total, per_night)

        Returns:
            过滤后的结果
        """
        endpoint = "/v1/search/filter"
        payload = {
            "searchResults": search_results,
            "maxPrice": max_price,
            "priceType": price_type
        }

        app_logger.info(f"Filtering results with max budget: {max_price}")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "filtered_results": response.get("filteredResults", response.get("data", {})),
            "original_count": response.get("originalCount", 0),
            "filtered_count": response.get("filteredCount", 0),
            "max_price": max_price
        }

    # =============================================================================
    # 推荐相关方法 (RecommendationAgent)
    # =============================================================================

    async def get_destination_info(self, destination: str) -> Dict[str, Any]:
        """
        获取目的地详细信息

        Args:
            destination: 目的地城市或国家名称

        Returns:
            目的地详细信息
        """
        endpoint = f"/v1/destinations/{destination}/info"

        app_logger.info(f"Getting destination info for: {destination}")

        response = await self._request("GET", endpoint)

        return {
            "destination": destination,
            "info": response
        }

    async def get_attractions(
        self,
        destination: str,
        category: str = None,
        sort_by: str = "rating"
    ) -> Dict[str, Any]:
        """
        获取目的地景点信息

        Args:
            destination: 目的地城市
            category: 景点类别 (culture, nature, museum, shopping, entertainment)
            sort_by: 排序方式 (rating, price, review_count)

        Returns:
            景点列表和相关信息
        """
        endpoint = f"/v1/destinations/{destination}/attractions"
        params = {"sortBy": sort_by}

        if category:
            params["category"] = category

        app_logger.info(f"Getting attractions for: {destination}")

        response = await self._request("GET", endpoint, params=params)

        return {
            "destination": destination,
            "attractions": response.get("attractions", response.get("data", [])),
            "categories": response.get("categories", []),
            "total_count": len(response.get("attractions", response.get("data", [])))
        }

    async def get_weather_forecast(
        self,
        destination: str,
        start_date: str,
        end_date: str = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取天气预报

        Args:
            destination: 目的地
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (可选)
            days: 预报天数 (默认7天)

        Returns:
            天气预报列表
        """
        endpoint = "/v1/weather/forecast"
        payload = {
            "destination": destination,
            "startDate": start_date,
            "days": days
        }

        if end_date:
            payload["endDate"] = end_date

        app_logger.info(f"Getting weather forecast for {destination}")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "destination": destination,
            "forecast": response.get("forecast", response.get("data", [])),
            "generated_at": response.get("generatedAt")
        }

    async def get_destination_reviews(
        self,
        destination: str,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "recent"  # recent, rating_high, rating_low
    ) -> Dict[str, Any]:
        """
        获取目的地评价

        Args:
            destination: 目的地
            page: 页码
            page_size: 每页数量
            sort_by: 排序方式

        Returns:
            评价列表和分页信息
        """
        endpoint = f"/v1/destinations/{destination}/reviews"
        params = {
            "page": page,
            "pageSize": page_size,
            "sortBy": sort_by
        }

        app_logger.info(f"Getting reviews for: {destination}")

        response = await self._request("GET", endpoint, params=params)

        return {
            "destination": destination,
            "reviews": response.get("reviews", response.get("data", [])),
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": response.get("totalCount", 0),
                "total_pages": response.get("totalPages", 0)
            },
            "average_rating": response.get("averageRating"),
            "rating_distribution": response.get("ratingDistribution")
        }

    async def get_travel_recommendations(
        self,
        destination: str,
        travel_style: str = None,  # adventure, relaxation, culture, foodie
        budget: str = None,  # budget, moderate, luxury
        duration: int = None,
        interests: List[str] = None
    ) -> Dict[str, Any]:
        """
        获取个性化旅行推荐

        Args:
            destination: 目的地
            travel_style: 旅行风格
            budget: 预算等级
            duration: 旅行天数
            interests: 兴趣列表

        Returns:
            推荐方案列表
        """
        endpoint = "/v1/recommendations"
        payload = {
            "destination": destination
        }

        if travel_style:
            payload["travelStyle"] = travel_style
        if budget:
            payload["budget"] = budget
        if duration:
            payload["duration"] = duration
        if interests:
            payload["interests"] = interests

        app_logger.info(f"Getting recommendations for: {destination}")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "destination": destination,
            "recommendations": response.get("recommendations", response.get("data", [])),
            "generated_at": response.get("generatedAt")
        }

    # =============================================================================
    # 预订相关方法 (BookingAgent)
    # =============================================================================

    async def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建预订

        Args:
            booking_data: 预订信息字典，包含:
                - user_id: 用户ID
                - flight_id: 航班ID (可选)
                - hotel_id: 酒店ID (可选)
                - passengers: 乘客信息列表
                - check_in: 入住日期 (酒店)
                - check_out: 退房日期 (酒店)
                - contact_info: 联系信息
                - special_requests: 特殊要求 (可选)

        Returns:
            预订确认信息
        """
        endpoint = "/v1/bookings"
        payload = booking_data

        app_logger.info(f"Creating booking for user: {booking_data.get('user_id')}")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "booking_id": response.get("bookingId"),
            "confirmation_number": response.get("confirmationNumber"),
            "status": response.get("status"),
            "total_amount": response.get("totalAmount"),
            "created_at": response.get("createdAt"),
            "details": response
        }

    async def process_payment(
        self,
        booking_id: str,
        payment_method: str,  # credit_card, debit_card, paypal
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理支付

        Args:
            booking_id: 预订ID
            payment_method: 支付方式
            payment_data: 支付详情 (卡号、有效期等)

        Returns:
            支付结果
        """
        endpoint = f"/v1/bookings/{booking_id}/payment"
        payload = {
            "paymentMethod": payment_method,
            **payment_data
        }

        app_logger.info(f"Processing payment for booking: {booking_id}")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "payment_id": response.get("paymentId"),
            "status": response.get("status"),
            "amount": response.get("amount"),
            "transaction_time": response.get("transactionTime")
        }

    async def confirm_booking(self, booking_id: str) -> Dict[str, Any]:
        """
        确认预订

        Args:
            booking_id: 预订ID

        Returns:
            确认后的预订信息
        """
        endpoint = f"/v1/bookings/{booking_id}/confirm"

        app_logger.info(f"Confirming booking: {booking_id}")

        response = await self._request("POST", endpoint)

        return {
            "booking_id": booking_id,
            "status": response.get("status"),
            "confirmation_number": response.get("confirmationNumber"),
            "confirmed_at": response.get("confirmedAt")
        }

    async def get_booking_status(self, booking_id: str) -> Dict[str, Any]:
        """
        获取预订状态

        Args:
            booking_id: 预订ID

        Returns:
            预订详细信息和当前状态
        """
        endpoint = f"/v1/bookings/{booking_id}"

        app_logger.info(f"Getting booking status: {booking_id}")

        response = await self._request("GET", endpoint)

        return {
            "booking_id": booking_id,
            "status": response.get("status"),
            "payment_status": response.get("paymentStatus"),
            "flight_details": response.get("flightDetails"),
            "hotel_details": response.get("hotelDetails"),
            "passengers": response.get("passengers"),
            "total_amount": response.get("totalAmount"),
            "created_at": response.get("createdAt"),
            "last_updated": response.get("lastUpdated")
        }

    async def cancel_booking(
        self,
        booking_id: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """
        取消预订

        Args:
            booking_id: 预订ID
            reason: 取消原因

        Returns:
            取消结果
        """
        endpoint = f"/v1/bookings/{booking_id}/cancel"
        payload = {"reason": reason} if reason else {}

        app_logger.info(f"Cancelling booking: {booking_id}")

        response = await self._request("POST", endpoint, json=payload)

        return {
            "booking_id": booking_id,
            "status": response.get("status"),
            "cancellation_fee": response.get("cancellationFee"),
            "refund_amount": response.get("refundAmount"),
            "cancelled_at": response.get("cancelledAt")
        }

    async def get_itinerary(self, booking_id: str) -> Dict[str, Any]:
        """
        获取详细行程单

        Args:
            booking_id: 预订ID

        Returns:
            完整行程信息
        """
        endpoint = f"/v1/bookings/{booking_id}/itinerary"

        app_logger.info(f"Getting itinerary for booking: {booking_id}")

        response = await self._request("GET", endpoint)

        return {
            "itinerary_id": response.get("itineraryId"),
            "booking_id": booking_id,
            "flights": response.get("flights", []),
            "hotels": response.get("hotels", []),
            "activities": response.get("activities", []),
            "day_by_day": response.get("dayByDay", []),
            "total_cost": response.get("totalCost"),
            "pdf_url": response.get("pdfUrl")
        }

    # =============================================================================
    # 辅助方法
    # =============================================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        检查 Java API 服务是否可用。

        Returns:
            健康状态信息
        """
        try:
            response = await self._request("GET", "/health")
            return {
                "status": "healthy",
                "service": "java-api",
                "response": response
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "java-api",
                "error": str(e)
            }

    async def close(self):
        """关闭客户端连接"""
        if self._client:
            await self._client.aclose()
            self._client = None
            app_logger.info("JavaAPIClient connection closed")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


# =============================================================================
# 全局单例实例
# =============================================================================

java_api_client = JavaAPIClient()
