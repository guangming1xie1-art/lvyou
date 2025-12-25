"""
API 客户端工具
用于与后端服务和外部 API 通信
"""
from typing import Any, Dict, Optional
import httpx
from config import settings
from utils.logger import app_logger


class APIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            response = await self.client.get(path, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            app_logger.error(f"HTTP GET error: {e}")
            raise

    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            response = await self.client.post(path, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            app_logger.error(f"HTTP POST error: {e}")
            raise

    async def close(self):
        await self.client.aclose()


class BackendAPIClient(APIClient):
    def __init__(self):
        super().__init__(base_url=settings.backend_api_url)

    async def get_destinations(self, params: Optional[Dict[str, Any]] = None):
        return await self.get("/destinations", params=params)

    async def get_attractions(self, destination_id: int):
        return await self.get(f"/destinations/{destination_id}/attractions")

    async def create_itinerary(self, data: Dict[str, Any]):
        return await self.post("/itineraries", json=data)


backend_client = BackendAPIClient()
