"""
Java Service Client - 用于调用Java微服务API并转发JWT

这个客户端封装了对Java后端服务的HTTP调用，并确保JWT token被正确传递。
"""

import httpx
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from conf import settings

logger = logging.getLogger(__name__)


class JavaServiceClient:
    """
    Java微服务客户端，统一处理JWT转发和HTTP调用
    
    功能：
    - 自动添加JWT Authorization header
    - 传递用户上下文 (X-User-ID, X-Username)
    - 重试机制和超时控制
    - 统一错误处理
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        初始化Java服务客户端
        
        Args:
            base_url: Java API基础URL (默认从配置读取)
            token: JWT access token
            user_id: 用户ID
            username: 用户名
            timeout: 请求超时时间(秒)
        """
        self.base_url = base_url or settings.java_api_base_url
        self.token = token
        self.user_id = user_id
        self.username = username
        self.timeout = timeout
        
        logger.debug(f"JavaServiceClient initialized with base_url: {self.base_url}")
    
    def get_headers(self) -> Dict[str, str]:
        """
        构建请求Headers，包含JWT和用户上下文
        
        Returns:
            Headers字典
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 添加JWT Authorization header
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        # 添加用户上下文headers
        if self.user_id:
            headers["X-User-ID"] = str(self.user_id)
        if self.username:
            headers["X-Username"] = self.username
        
        return headers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发起HTTP请求（带重试机制）
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            endpoint: API端点路径
            data: 请求体数据
            params: URL查询参数
            
        Returns:
            响应数据
            
        Raises:
            httpx.HTTPError: HTTP请求失败
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.get_headers()
        
        logger.info(f"[JavaServiceClient] {method} {url}")
        logger.debug(f"Headers: {headers}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )
            
            response.raise_for_status()
            return response.json()
    
    # ============== 航班搜索服务 ==============
    
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1,
        cabin_class: str = "economy"
    ) -> Dict[str, Any]:
        """
        搜索航班
        
        Args:
            origin: 出发地
            destination: 目的地
            departure_date: 出发日期 (YYYY-MM-DD)
            return_date: 返程日期 (可选)
            passengers: 乘客数量
            cabin_class: 舱位等级
            
        Returns:
            航班搜索结果
        """
        try:
            return await self._request(
                method="POST",
                endpoint="/flights/search",
                data={
                    "origin": origin,
                    "destination": destination,
                    "departureDate": departure_date,
                    "returnDate": return_date,
                    "passengers": passengers,
                    "cabinClass": cabin_class
                }
            )
        except Exception as e:
            logger.error(f"Flight search failed: {e}")
            raise
    
    # ============== 酒店搜索服务 ==============
    
    async def search_hotels(
        self,
        destination: str,
        check_in_date: str,
        check_out_date: str,
        guests: int = 1,
        rooms: int = 1,
        min_rating: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        搜索酒店
        
        Args:
            destination: 目的地
            check_in_date: 入住日期 (YYYY-MM-DD)
            check_out_date: 退房日期 (YYYY-MM-DD)
            guests: 客人数量
            rooms: 房间数量
            min_rating: 最低评分
            
        Returns:
            酒店搜索结果
        """
        try:
            data = {
                "destination": destination,
                "checkInDate": check_in_date,
                "checkOutDate": check_out_date,
                "guests": guests,
                "rooms": rooms
            }
            if min_rating is not None:
                data["minRating"] = min_rating
            
            return await self._request(
                method="POST",
                endpoint="/hotels/search",
                data=data
            )
        except Exception as e:
            logger.error(f"Hotel search failed: {e}")
            raise
    
    # ============== 景点服务 ==============
    
    async def get_attractions(
        self,
        destination: str,
        category: Optional[str] = None,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        获取景点信息
        
        Args:
            destination: 目的地
            category: 景点类别 (可选)
            max_results: 最大结果数量
            
        Returns:
            景点列表
        """
        try:
            params = {
                "destination": destination,
                "maxResults": max_results
            }
            if category:
                params["category"] = category
            
            return await self._request(
                method="GET",
                endpoint="/attractions",
                params=params
            )
        except Exception as e:
            logger.error(f"Get attractions failed: {e}")
            raise
    
    # ============== 预订服务 ==============
    
    async def create_booking(
        self,
        booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建预订
        
        Args:
            booking_data: 预订详情
            
        Returns:
            预订结果
        """
        try:
            return await self._request(
                method="POST",
                endpoint="/bookings",
                data=booking_data
            )
        except Exception as e:
            logger.error(f"Create booking failed: {e}")
            raise
    
    async def get_booking(
        self,
        booking_id: str
    ) -> Dict[str, Any]:
        """
        获取预订详情
        
        Args:
            booking_id: 预订ID
            
        Returns:
            预订详情
        """
        try:
            return await self._request(
                method="GET",
                endpoint=f"/bookings/{booking_id}"
            )
        except Exception as e:
            logger.error(f"Get booking failed: {e}")
            raise
    
    # ============== 推荐服务 ==============
    
    async def get_recommendations(
        self,
        destination: str,
        interests: Optional[list] = None,
        budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        获取旅游推荐
        
        Args:
            destination: 目的地
            interests: 兴趣列表
            budget: 预算
            
        Returns:
            推荐结果
        """
        try:
            data = {
                "destination": destination
            }
            if interests:
                data["interests"] = interests
            if budget is not None:
                data["budget"] = budget
            
            return await self._request(
                method="POST",
                endpoint="/recommendations",
                data=data
            )
        except Exception as e:
            logger.error(f"Get recommendations failed: {e}")
            raise


# ============== 工厂函数 ==============

def create_java_client(
    token: Optional[str] = None,
    user_id: Optional[str] = None,
    username: Optional[str] = None
) -> JavaServiceClient:
    """
    创建Java服务客户端实例
    
    Args:
        token: JWT access token
        user_id: 用户ID
        username: 用户名
        
    Returns:
        JavaServiceClient实例
    """
    return JavaServiceClient(
        token=token,
        user_id=user_id,
        username=username
    )


__all__ = [
    "JavaServiceClient",
    "create_java_client"
]
