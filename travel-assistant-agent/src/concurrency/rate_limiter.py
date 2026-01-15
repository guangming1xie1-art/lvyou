"""
Rate Limiting

This module provides rate limiting capabilities using token bucket
and sliding window algorithms.
"""

from typing import Optional, Dict, Any
import asyncio
import time
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token Bucket Rate Limiter
    
    Implements rate limiting using the token bucket algorithm.
    Allows bursts up to a maximum size with a steady refill rate.
    """
    
    def __init__(
        self,
        rate: float,  # tokens per second
        burst: Optional[float] = None,  # maximum tokens (defaults to rate * 2)
        initial_tokens: Optional[float] = None
    ):
        """Initialize token bucket rate limiter
        
        Args:
            rate: Token refill rate (tokens per second)
            burst: Maximum bucket size (defaults to rate * 2)
            initial_tokens: Initial token count (defaults to burst)
        """
        self.rate = rate
        self.burst = burst or (rate * 2)
        self.tokens = initial_tokens if initial_tokens is not None else self.burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            "requests": 0,
            "allowed": 0,
            "denied": 0,
            "wait_time": 0.0
        }
        
        logger.info(
            f"Initialized rate limiter: rate={rate}/s, burst={burst}"
        )
    
    async def acquire(self, tokens: float = 1) -> bool:
        """Acquire tokens without blocking
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens were acquired, False otherwise
        """
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Refill tokens
            self.tokens = min(
                self.burst,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            self.stats["requests"] += 1
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.stats["allowed"] += 1
                logger.debug(f"Acquired {tokens} tokens (remaining: {self.tokens:.2f})")
                return True
            else:
                self.stats["denied"] += 1
                logger.debug(
                    f"Denied {tokens} tokens (available: {self.tokens:.2f})"
                )
                return False
    
    async def wait_if_needed(self, tokens: float = 1):
        """Wait until tokens are available
        
        Args:
            tokens: Number of tokens needed
        """
        while True:
            acquired = await self.acquire(tokens)
            if acquired:
                break
            
            # Calculate wait time and sleep
            async with self.lock:
                now = time.time()
                needed = tokens - self.tokens
                wait_time = needed / self.rate
                logger.debug(f"Waiting {wait_time:.3f}s for {needed:.2f} tokens")
            
            await asyncio.sleep(min(wait_time, 0.1))  # Sleep in small increments
        
        self.stats["wait_time"] += wait_time
    
    async def acquire_with_timeout(
        self,
        tokens: float = 1,
        timeout: float = 5.0
    ) -> bool:
        """Try to acquire tokens with a timeout
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if tokens were acquired, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.acquire(tokens):
                return True
            await asyncio.sleep(0.01)
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics
        
        Returns:
            Dictionary containing statistics
        """
        return {
            **self.stats,
            "rate": self.rate,
            "burst": self.burst,
            "current_tokens": self.tokens,
            "utilization": (
                (self.burst - self.tokens) / self.burst
                if self.burst > 0 else 0
            ),
            "allow_rate": (
                self.stats["allowed"] / self.stats["requests"]
                if self.stats["requests"] > 0 else 0
            )
        }
    
    async def reset(self):
        """Reset rate limiter state"""
        async with self.lock:
            self.tokens = self.burst
            self.last_update = time.time()
            self.stats = {
                "requests": 0,
                "allowed": 0,
                "denied": 0,
                "wait_time": 0.0
            }
        logger.info("Rate limiter reset")


class SlidingWindowRateLimiter:
    """Sliding Window Rate Limiter
    
    Implements rate limiting using a sliding window algorithm.
    More accurate than simple fixed window but uses more memory.
    """
    
    def __init__(
        self,
        window_size: float,  # window size in seconds
        max_requests: int  # maximum requests in window
    ):
        """Initialize sliding window rate limiter
        
        Args:
            window_size: Time window size in seconds
            max_requests: Maximum number of requests allowed in window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests: deque = deque()
        self.lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            "requests": 0,
            "allowed": 0,
            "denied": 0
        }
        
        logger.info(
            f"Initialized sliding window rate limiter: "
            f"window={window_size}s, max={max_requests}"
        )
    
    async def is_allowed(self) -> bool:
        """Check if request is allowed
        
        Returns:
            True if request is allowed, False otherwise
        """
        async with self.lock:
            now = time.time()
            
            # Remove old requests outside the window
            cutoff = now - self.window_size
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            self.stats["requests"] += 1
            
            # Check if under limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                self.stats["allowed"] += 1
                logger.debug(
                    f"Request allowed (window: {len(self.requests)}/{self.max_requests})"
                )
                return True
            else:
                self.stats["denied"] += 1
                logger.debug(
                    f"Request denied (window: {len(self.requests)}/{self.max_requests})"
                )
                return False
    
    async def wait_if_needed(self):
        """Wait until request is allowed"""
        while True:
            allowed = await self.is_allowed()
            if allowed:
                break
            
            # Calculate wait time
            async with self.lock:
                if self.requests:
                    oldest = self.requests[0]
                    wait_time = (oldest + self.window_size) - time.time()
                    wait_time = max(0, wait_time)
                else:
                    wait_time = 0
            
            if wait_time > 0:
                await asyncio.sleep(min(wait_time, 0.1))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics
        
        Returns:
            Dictionary containing statistics
        """
        now = time.time()
        cutoff = now - self.window_size
        
        # Count current window requests
        current_requests = sum(
            1 for req in self.requests
            if req >= cutoff
        )
        
        return {
            **self.stats,
            "window_size": self.window_size,
            "max_requests": self.max_requests,
            "current_requests": current_requests,
            "window_utilization": current_requests / self.max_requests,
            "allow_rate": (
                self.stats["allowed"] / self.stats["requests"]
                if self.stats["requests"] > 0 else 0
            )
        }
    
    async def reset(self):
        """Reset rate limiter state"""
        async with self.lock:
            self.requests.clear()
            self.stats = {
                "requests": 0,
                "allowed": 0,
                "denied": 0
            }
        logger.info("Sliding window rate limiter reset")


class MultiRateLimiter:
    """Multi-key Rate Limiter
    
    Manages multiple rate limiters keyed by identifier
    (e.g., user ID, IP address).
    """
    
    def __init__(
        self,
        rate: float,
        burst: Optional[float] = None,
        limiter_type: str = "token_bucket"  # "token_bucket" or "sliding_window"
    ):
        """Initialize multi-key rate limiter
        
        Args:
            rate: Rate limit (requests per second)
            burst: Burst size for token bucket
            limiter_type: Type of rate limiter to use
        """
        self.rate = rate
        self.burst = burst or (rate * 2)
        self.limiter_type = limiter_type
        self.limiters: Dict[Any, Any] = {}
        self.lock = asyncio.Lock()
        
        # Cleanup configuration
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        self.limiter_ttl = 3600  # 1 hour
        
        logger.info(
            f"Initialized multi-key rate limiter: rate={rate}/s, type={limiter_type}"
        )
    
    async def acquire(self, key: Any, tokens: float = 1) -> bool:
        """Acquire tokens for a specific key
        
        Args:
            key: Identifier for the rate limiter
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens were acquired, False otherwise
        """
        # Get or create limiter for key
        limiter = await self._get_limiter(key)
        return await limiter.acquire(tokens)
    
    async def is_allowed(self, key: Any) -> bool:
        """Check if request is allowed for a specific key
        
        Args:
            key: Identifier for the rate limiter
            
        Returns:
            True if request is allowed, False otherwise
        """
        limiter = await self._get_limiter(key)
        
        if self.limiter_type == "sliding_window":
            return await limiter.is_allowed()
        else:
            return await limiter.acquire()
    
    async def wait_if_needed(self, key: Any, tokens: float = 1):
        """Wait until tokens are available for a specific key
        
        Args:
            key: Identifier for the rate limiter
            tokens: Number of tokens needed
        """
        limiter = await self._get_limiter(key)
        await limiter.wait_if_needed(tokens)
    
    async def _get_limiter(self, key: Any) -> Any:
        """Get or create limiter for key"""
        async with self.lock:
            # Periodic cleanup
            await self._cleanup()
            
            if key not in self.limiters:
                if self.limiter_type == "sliding_window":
                    self.limiters[key] = SlidingWindowRateLimiter(
                        window_size=1.0,
                        max_requests=int(self.rate)
                    )
                else:
                    self.limiters[key] = RateLimiter(
                        rate=self.rate,
                        burst=self.burst
                    )
            
            self.limiters[key].last_access = time.time()
            return self.limiters[key]
    
    async def _cleanup(self):
        """Remove stale limiters"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        stale_keys = [
            key for key, limiter in self.limiters.items()
            if (now - limiter.last_access) > self.limiter_ttl
        ]
        
        for key in stale_keys:
            del self.limiters[key]
        
        self.last_cleanup = now
        if stale_keys:
            logger.info(f"Cleaned up {len(stale_keys)} stale limiters")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics
        
        Returns:
            Dictionary containing statistics
        """
        limiter_count = len(self.limiters)
        return {
            "type": self.limiter_type,
            "rate": self.rate,
            "burst": self.burst,
            "active_limiters": limiter_count,
            "last_cleanup": self.last_cleanup
        }
    
    async def get_limiter_stats(self, key: Any) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific limiter
        
        Args:
            key: Limiter key
            
        Returns:
            Statistics dictionary or None if not found
        """
        limiter = self.limiters.get(key)
        if limiter:
            return limiter.get_stats()
        return None


__all__ = [
    "RateLimiter",
    "SlidingWindowRateLimiter",
    "MultiRateLimiter",
]
