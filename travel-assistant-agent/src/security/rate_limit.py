"""
Rate limiting for API endpoints
"""
import asyncio
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from ..utils.logger import app_logger
from ..config import settings


class RateLimiter:
    """Rate limiter for API endpoints"""
    
    def __init__(
        self,
        requests_per_minute: int = 100,
        requests_per_hour: int = 5000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # In-memory storage for rate limit tracking
        # In production, use Redis or similar
        self._minute_store: Dict[str, list] = {}
        self._hour_store: Dict[str, list] = {}
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start_cleanup_task(self):
        """Start background task to clean up old entries"""
        async def cleanup():
            while True:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._cleanup_old_entries()
        
        self._cleanup_task = asyncio.create_task(cleanup())
    
    async def _cleanup_old_entries(self):
        """Remove old entries from rate limit stores"""
        current_time = time.time()
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        # Clean minute store
        for user_id, timestamps in self._minute_store.items():
            self._minute_store[user_id] = [
                ts for ts in timestamps if ts > minute_ago
            ]
            if not self._minute_store[user_id]:
                del self._minute_store[user_id]
        
        # Clean hour store
        for user_id, timestamps in self._hour_store.items():
            self._hour_store[user_id] = [
                ts for ts in timestamps if ts > hour_ago
            ]
            if not self._hour_store[user_id]:
                del self._hour_store[user_id]
    
    def _get_user_identifier(self, request: Request) -> str:
        """Get user identifier from request"""
        # Try to get from token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # For simplicity, use the token itself as identifier
            # In production, decode token and use user_id
            return auth_header[:50]  # Use first 50 chars
        
        # Fallback to IP address
        return request.client.host if request.client else "unknown"
    
    async def check_limit(self, request: Request, user_id: str = None) -> bool:
        """
        Check if request should be rate limited
        
        Args:
            request: FastAPI request
            user_id: User ID (优先使用 user_id 做限流标识) ✅ 新增
        
        Returns:
            True if request is allowed, False otherwise
        
        Raises:
            HTTPException: If rate limit exceeded
        """
        # ✅ 优先使用 user_id，如果没有则使用 IP
        identifier = user_id if user_id else self._get_user_identifier(request)
        
        current_time = time.time()
        
        # Check minute limit
        if identifier not in self._minute_store:
            self._minute_store[identifier] = []
        
        # Filter timestamps from last minute
        self._minute_store[identifier] = [
            ts for ts in self._minute_store[identifier] if current_time - ts < 60
        ]
        
        if len(self._minute_store[identifier]) >= self.requests_per_minute:
            app_logger.warning(f"Rate limit exceeded (minute) for identifier: {identifier}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + 60))
                }
            )
        
        # Check hour limit
        if identifier not in self._hour_store:
            self._hour_store[identifier] = []
        
        # Filter timestamps from last hour
        self._hour_store[identifier] = [
            ts for ts in self._hour_store[identifier] if current_time - ts < 3600
        ]
        
        if len(self._hour_store[identifier]) >= self.requests_per_hour:
            app_logger.warning(f"Rate limit exceeded (hour) for identifier: {identifier}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour",
                headers={
                    "Retry-After": "3600",
                    "X-RateLimit-Limit": str(self.requests_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + 3600))
                }
            )
        
        # Record this request
        self._minute_store[identifier].append(current_time)
        self._hour_store[identifier].append(current_time)
        
        return True
    
    async def get_rate_limit_info(self, request: Request) -> Dict[str, int]:
        """
        Get current rate limit info for user
        
        Args:
            request: FastAPI request
        
        Returns:
            Dictionary with rate limit info
        """
        user_id = self._get_user_identifier(request)
        current_time = time.time()
        
        minute_count = 0
        hour_count = 0
        
        if user_id in self._minute_store:
            minute_count = len([
                ts for ts in self._minute_store[user_id] if current_time - ts < 60
            ])
        
        if user_id in self._hour_store:
            hour_count = len([
                ts for ts in self._hour_store[user_id] if current_time - ts < 3600
            ])
        
        return {
            "limit_per_minute": self.requests_per_minute,
            "limit_per_hour": self.requests_per_hour,
            "used_per_minute": minute_count,
            "used_per_hour": hour_count,
            "remaining_per_minute": self.requests_per_minute - minute_count,
            "remaining_per_hour": self.requests_per_hour - hour_count
        }


# Global rate limiter instance
rate_limiter = RateLimiter()
