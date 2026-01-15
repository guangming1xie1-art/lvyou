"""
Memory Pool Management

This module provides memory pool management for efficient memory usage
in high-concurrency scenarios.
"""

from typing import Dict, Any, Optional
import asyncio
from collections import deque
import logging
import time

logger = logging.getLogger(__name__)


class MemoryPool:
    """Memory Pool Manager
    
    Manages memory allocation and deallocation with size limits
    and usage tracking for high-concurrency scenarios.
    """
    
    def __init__(
        self,
        max_size: int = 100,
        item_size_limit: int = 10 * 1024 * 1024  # 10MB
    ):
        """Initialize memory pool
        
        Args:
            max_size: Maximum number of items in the pool
            item_size_limit: Maximum size per item in bytes
        """
        self.max_size = max_size
        self.item_size_limit = item_size_limit
        self.pool: deque = deque(maxlen=max_size)
        self.lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            "allocated": 0,
            "freed": 0,
            "current": 0,
            "rejected": 0,
            "total_bytes_allocated": 0,
            "total_bytes_freed": 0
        }
        
        logger.info(
            f"Initialized memory pool: max_size={max_size}, item_size_limit={item_size_limit}"
        )
    
    async def allocate(self, key: str, size: int) -> bool:
        """Allocate memory for an item
        
        Args:
            key: Unique identifier for the item
            size: Size in bytes
            
        Returns:
            True if allocated successfully, False otherwise
        """
        async with self.lock:
            # Check item size limit
            if size > self.item_size_limit:
                logger.warning(
                    f"Item too large: {size} > {self.item_size_limit} bytes for key {key}"
                )
                self.stats["rejected"] += 1
                return False
            
            # Check pool capacity
            if len(self.pool) >= self.max_size:
                logger.warning(f"Memory pool is full, rejecting allocation for key {key}")
                self.stats["rejected"] += 1
                return False
            
            # Allocate memory
            self.pool.append({
                "key": key,
                "size": size,
                "timestamp": time.time()
            })
            
            self.stats["allocated"] += 1
            self.stats["current"] = len(self.pool)
            self.stats["total_bytes_allocated"] += size
            
            logger.debug(f"Allocated {size} bytes for key {key}")
            return True
    
    async def free(self, key: str) -> bool:
        """Free memory for an item
        
        Args:
            key: Unique identifier for the item
            
        Returns:
            True if freed successfully, False otherwise
        """
        async with self.lock:
            freed_size = 0
            original_len = len(self.pool)
            
            # Remove item with matching key
            self.pool = deque(
                (item for item in self.pool if item["key"] != key),
                maxlen=self.max_size
            )
            
            freed_size = original_len - len(self.pool)
            if freed_size > 0:
                self.stats["freed"] += 1
                self.stats["current"] = len(self.pool)
                self.stats["total_bytes_freed"] += freed_size
                logger.debug(f"Freed {freed_size} bytes for key {key}")
                return True
            
            logger.warning(f"Key {key} not found in memory pool")
            return False
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get item from memory pool
        
        Args:
            key: Unique identifier for the item
            
        Returns:
            Item dictionary or None if not found
        """
        async with self.lock:
            for item in self.pool:
                if item["key"] == key:
                    return item
            return None
    
    async def clear(self):
        """Clear all items from the pool"""
        async with self.lock:
            cleared_count = len(self.pool)
            self.pool.clear()
            self.stats["freed"] += cleared_count
            self.stats["current"] = 0
            logger.info(f"Cleared {cleared_count} items from memory pool")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory pool statistics
        
        Returns:
            Dictionary containing statistics
        """
        return {
            **self.stats,
            "pool_size": len(self.pool),
            "max_size": self.max_size,
            "utilization": len(self.pool) / self.max_size if self.max_size > 0 else 0,
            "avg_item_size": (
                self.stats["total_bytes_allocated"] / self.stats["allocated"]
                if self.stats["allocated"] > 0 else 0
            )
        }


class ObjectPool:
    """Object Pool for efficient object reuse
    
    Manages a pool of reusable objects to reduce allocation overhead
    in high-concurrency scenarios.
    """
    
    def __init__(
        self,
        factory,
        reset: Optional[callable] = None,
        max_size: int = 50
    ):
        """Initialize object pool
        
        Args:
            factory: Callable that creates new objects
            reset: Optional callable that resets objects before reuse
            max_size: Maximum number of objects in the pool
        """
        self.factory = factory
        self.reset = reset
        self.max_size = max_size
        self.pool: deque = deque(maxlen=max_size)
        self.lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            "created": 0,
            "reused": 0,
            "acquired": 0,
            "released": 0,
            "current_size": 0
        }
        
        logger.info(f"Initialized object pool with factory {factory.__name__}")
    
    async def acquire(self) -> Any:
        """Acquire an object from the pool
        
        Returns:
            Object instance
        """
        async with self.lock:
            self.stats["acquired"] += 1
            
            # Try to get from pool
            if len(self.pool) > 0:
                obj = self.pool.popleft()
                self.stats["reused"] += 1
                self.stats["current_size"] = len(self.pool)
                logger.debug("Reused object from pool")
                return obj
            
            # Create new object
            obj = self.factory()
            self.stats["created"] += 1
            logger.debug("Created new object")
            return obj
    
    async def release(self, obj: Any):
        """Release an object back to the pool
        
        Args:
            obj: Object to release
        """
        async with self.lock:
            self.stats["released"] += 1
            
            # Reset object if reset function is provided
            if self.reset:
                try:
                    self.reset(obj)
                except Exception as e:
                    logger.error(f"Error resetting object: {e}")
                    return
            
            # Add to pool if not full
            if len(self.pool) < self.max_size:
                self.pool.append(obj)
                self.stats["current_size"] = len(self.pool)
                logger.debug(f"Returned object to pool (size: {len(self.pool)})")
            else:
                logger.debug("Pool is full, discarding object")
    
    async def clear(self):
        """Clear all objects from the pool"""
        async with self.lock:
            cleared = len(self.pool)
            self.pool.clear()
            self.stats["current_size"] = 0
            logger.info(f"Cleared {cleared} objects from pool")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get object pool statistics
        
        Returns:
            Dictionary containing statistics
        """
        return {
            **self.stats,
            "max_size": self.max_size,
            "utilization": len(self.pool) / self.max_size if self.max_size > 0 else 0,
            "reuse_rate": (
                self.stats["reused"] / self.stats["acquired"]
                if self.stats["acquired"] > 0 else 0
            )
        }


__all__ = [
    "MemoryPool",
    "ObjectPool",
]
