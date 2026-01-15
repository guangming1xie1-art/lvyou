"""
High Concurrency Optimization Module

This module provides high concurrency optimization for the Travel Assistant Agent,
including memory pool management, connection pool management, streaming responses,
and rate limiting.
"""

from .memory_pool import MemoryPool, ObjectPool
from .connection_pool import ConnectionPool
from .streaming import StreamingManager
from .rate_limiter import RateLimiter

__version__ = "1.0.0"

__all__ = [
    # Memory Management
    "MemoryPool",
    "ObjectPool",
    
    # Connection Management
    "ConnectionPool",
    
    # Streaming
    "StreamingManager",
    
    # Rate Limiting
    "RateLimiter",
]
