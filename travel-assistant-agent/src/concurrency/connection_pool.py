"""
Connection Pool Management

This module provides async connection pool management for efficient
resource usage in high-concurrency scenarios.
"""

from typing import Optional, Dict, Any, List
import asyncio
from asyncio import Semaphore, Lock
import logging
import time

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Async Connection Pool
    
    Manages a pool of connections with concurrency limits,
    timeout handling, and statistics tracking.
    """
    
    def __init__(
        self,
        max_connections: int = 10,
        timeout: float = 30.0,
        idle_timeout: float = 300.0
    ):
        """Initialize connection pool
        
        Args:
            max_connections: Maximum number of concurrent connections
            timeout: Maximum time to wait for a connection (seconds)
            idle_timeout: Maximum time a connection can be idle (seconds)
        """
        self.max_connections = max_connections
        self.timeout = timeout
        self.idle_timeout = idle_timeout
        
        self.semaphore = Semaphore(max_connections)
        self.active_connections = 0
        self.idle_connections = 0
        self.lock = Lock()
        
        # Statistics
        self.stats = {
            "acquired": 0,
            "released": 0,
            "rejected": 0,
            "timeouts": 0,
            "peak_active": 0
        }
        
        logger.info(
            f"Initialized connection pool: max={max_connections}, timeout={timeout}s"
        )
    
    async def acquire(self) -> bool:
        """Acquire a connection
        
        Returns:
            True if acquired successfully, False otherwise
        """
        try:
            # Wait for semaphore with timeout
            await asyncio.wait_for(
                self.semaphore.acquire(),
                timeout=self.timeout
            )
            
            async with self.lock:
                self.active_connections += 1
                self.stats["acquired"] += 1
                
                # Track peak
                if self.active_connections > self.stats["peak_active"]:
                    self.stats["peak_active"] = self.active_connections
                
                logger.debug(
                    f"Acquired connection (active: {self.active_connections}/{self.max_connections})"
                )
                return True
        
        except asyncio.TimeoutError:
            async with self.lock:
                self.stats["timeouts"] += 1
                self.stats["rejected"] += 1
            
            logger.warning("Connection acquisition timeout")
            return False
        
        except Exception as e:
            async with self.lock:
                self.stats["rejected"] += 1
            
            logger.error(f"Error acquiring connection: {e}")
            return False
    
    async def release(self):
        """Release a connection"""
        async with self.lock:
            if self.active_connections > 0:
                self.active_connections -= 1
                self.stats["released"] += 1
                self.idle_connections += 1
                logger.debug(
                    f"Released connection (active: {self.active_connections}/{self.max_connections})"
                )
            
        self.semaphore.release()
    
    async def __aenter__(self):
        """Async context manager entry"""
        acquired = await self.acquire()
        if not acquired:
            raise RuntimeError("Failed to acquire connection")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.release()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics
        
        Returns:
            Dictionary containing statistics
        """
        return {
            **self.stats,
            "active": self.active_connections,
            "idle": self.idle_connections,
            "available": self.max_connections - self.active_connections,
            "max_connections": self.max_connections,
            "utilization": self.active_connections / self.max_connections,
            "rejection_rate": (
                self.stats["rejected"] / (self.stats["acquired"] + self.stats["rejected"])
                if (self.stats["acquired"] + self.stats["rejected"]) > 0 else 0
            )
        }
    
    async def close_all(self):
        """Close all connections and reset pool"""
        async with self.lock:
            self.active_connections = 0
            self.idle_connections = 0
            
            # Release all semaphores
            for _ in range(self.max_connections):
                try:
                    self.semaphore.release_nowait()
                except:
                    pass
            
            logger.info("Closed all connections and reset pool")


class DatabaseConnectionPool(ConnectionPool):
    """Specialized connection pool for database connections"""
    
    def __init__(
        self,
        max_connections: int = 20,
        timeout: float = 30.0,
        idle_timeout: float = 300.0,
        connection_factory = None
    ):
        """Initialize database connection pool
        
        Args:
            max_connections: Maximum number of concurrent connections
            timeout: Maximum time to wait for a connection
            idle_timeout: Maximum time a connection can be idle
            connection_factory: Optional factory function for creating connections
        """
        super().__init__(max_connections, timeout, idle_timeout)
        self.connection_factory = connection_factory
        self._connections: List[Any] = []
    
    async def get_connection(self) -> Optional[Any]:
        """Get a database connection
        
        Returns:
            Connection object or None if failed
        """
        if not await self.acquire():
            return None
        
        # Try to get existing connection from pool
        if self._connections:
            conn = self._connections.pop()
            logger.debug("Reused existing database connection")
            return conn
        
        # Create new connection if factory is available
        if self.connection_factory:
            try:
                conn = await self.connection_factory()
                logger.debug("Created new database connection")
                return conn
            except Exception as e:
                logger.error(f"Error creating database connection: {e}")
                await self.release()
                return None
        
        # Return placeholder if no factory
        return {"acquired": True}
    
    async def return_connection(self, conn: Any):
        """Return a connection to the pool
        
        Args:
            conn: Connection object to return
        """
        if len(self._connections) < self.max_connections:
            self._connections.append(conn)
            logger.debug(f"Returned connection to pool (pool size: {len(self._connections)})")
        
        await self.release()
    
    async def close_all(self):
        """Close all database connections"""
        # Close all connections in pool
        for conn in self._connections:
            try:
                if hasattr(conn, 'close'):
                    await conn.close()
                elif callable(getattr(conn, 'close', None)):
                    conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        
        self._connections.clear()
        await super().close_all()


class APIConnectionPool(ConnectionPool):
    """Specialized connection pool for API connections"""
    
    def __init__(
        self,
        max_connections: int = 100,
        timeout: float = 10.0,
        idle_timeout: float = 60.0,
        max_retries: int = 3
    ):
        """Initialize API connection pool
        
        Args:
            max_connections: Maximum number of concurrent API requests
            timeout: Maximum time to wait for a connection
            idle_timeout: Maximum time a connection can be idle
            max_retries: Maximum number of retries for failed requests
        """
        super().__init__(max_connections, timeout, idle_timeout)
        self.max_retries = max_retries
        self.request_stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "retries": 0
        }
    
    async def make_request(
        self,
        request_func,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """Make an API request with connection pool management
        
        Args:
            request_func: Async function to execute the request
            *args: Positional arguments for request_func
            **kwargs: Keyword arguments for request_func
            
        Returns:
            Request result or None if failed
        """
        if not await self.acquire():
            return None
        
        self.request_stats["total"] += 1
        
        # Try request with retries
        for attempt in range(self.max_retries + 1):
            try:
                result = await request_func(*args, **kwargs)
                self.request_stats["successful"] += 1
                return result
            
            except Exception as e:
                if attempt < self.max_retries:
                    self.request_stats["retries"] += 1
                    logger.warning(
                        f"API request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                    )
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    self.request_stats["failed"] += 1
                    logger.error(f"API request failed after {self.max_retries} retries: {e}")
                    return None
            
            finally:
                await self.release()
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics including request stats
        
        Returns:
            Dictionary containing statistics
        """
        base_stats = super().get_stats()
        base_stats["requests"] = self.request_stats
        base_stats["success_rate"] = (
            self.request_stats["successful"] / self.request_stats["total"]
            if self.request_stats["total"] > 0 else 0
        )
        return base_stats


__all__ = [
    "ConnectionPool",
    "DatabaseConnectionPool",
    "APIConnectionPool",
]
