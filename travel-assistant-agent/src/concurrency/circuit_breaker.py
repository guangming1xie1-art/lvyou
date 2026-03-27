"""
熔断机制实现

提供服务级别的熔断保护，防止故障级联
"""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 正常关闭
    OPEN = "open"          # 熔断开启
    HALF_OPEN = "half_open"  # 半开状态


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    fail_max: int = 5           # 连续失败次数阈值
    reset_timeout: int = 30      # 重置超时时间（秒）
    half_open_max_calls: int = 3  # 半开状态允许的调用次数
    success_threshold: int = 2    # 从半开恢复到关闭需要的成功次数


@dataclass
class CircuitBreakerStats:
    """熔断器统计"""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    state: CircuitState = CircuitState.CLOSED
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0


class CircuitBreaker:
    """
    熔断器实现
    
    状态转换：
    - CLOSED -> OPEN: 连续失败达到 fail_max
    - OPEN -> HALF_OPEN: 经过 reset_timeout 后
    - HALF_OPEN -> CLOSED: 成功达到 success_threshold 次
    - HALF_OPEN -> OPEN: 任何一次失败
    """
    
    def __init__(
        self,
        name: str,
        fail_max: int = 5,
        reset_timeout: int = 30,
        success_threshold: int = 2,
        half_open_max_calls: int = 3
    ):
        self.name = name
        self.config = CircuitBreakerConfig(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            success_threshold=success_threshold,
            half_open_max_calls=half_open_max_calls
        )
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """获取当前状态"""
        if self.stats.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                return CircuitState.HALF_OPEN
        return self.stats.state
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        if self.stats.last_failure_time is None:
            return False
        return (time.time() - self.stats.last_failure_time) >= self.config.reset_timeout
    
    async def call(
        self,
        func: Callable[..., Awaitable[T]],
        *args,
        fallback: Optional[Callable[[], T]] = None,
        **kwargs
    ) -> T:
        """
        执行被熔断器保护的调用
        
        Args:
            func: 要执行的异步函数
            *args: 位置参数
            fallback: 降级函数（可选）
            **kwargs: 关键字参数
            
        Returns:
            函数执行结果或降级结果
        """
        async with self._lock:
            current_state = self.state
            
            if current_state == CircuitState.OPEN:
                self.stats.total_calls += 1
                logger.warning(f"Circuit breaker OPEN for {self.name}, returning fallback")
                if fallback:
                    return fallback()
                raise CircuitBreakerOpenError(f"Circuit breaker is OPEN for {self.name}")
            
            if current_state == CircuitState.HALF_OPEN:
                if self.stats.success_count >= self.config.half_open_max_calls:
                    self._reset()
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            if fallback:
                logger.info(f"Call failed for {self.name}, using fallback")
                return fallback()
            raise
    
    async def _on_success(self):
        """处理成功调用"""
        async with self._lock:
            self.stats.total_successes += 1
            
            if self.stats.state == CircuitState.HALF_OPEN:
                self.stats.success_count += 1
                if self.stats.success_count >= self.config.success_threshold:
                    logger.info(f"Circuit breaker CLOSED for {self.name}")
                    self._reset()
            else:
                self.stats.failure_count = 0
    
    async def _on_failure(self):
        """处理失败调用"""
        async with self._lock:
            self.stats.total_failures += 1
            self.stats.failure_count += 1
            self.stats.last_failure_time = time.time()
            
            if self.stats.state == CircuitState.CLOSED:
                if self.stats.failure_count >= self.config.fail_max:
                    logger.warning(f"Circuit breaker OPEN for {self.name} after {self.stats.failure_count} failures")
                    self.stats.state = CircuitState.OPEN
            elif self.stats.state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit breaker re-OPENED for {self.name} after failure in half-open state")
                self.stats.state = CircuitState.OPEN
                self.stats.success_count = 0
    
    def _reset(self):
        """重置熔断器"""
        self.stats.state = CircuitState.CLOSED
        self.stats.failure_count = 0
        self.stats.success_count = 0
        self.stats.last_failure_time = None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.stats.failure_count,
            "success_count": self.stats.success_count,
            "total_calls": self.stats.total_calls,
            "total_failures": self.stats.total_failures,
            "total_successes": self.stats.total_successes,
            "last_failure_time": self.stats.last_failure_time
        }


class CircuitBreakerOpenError(Exception):
    """熔断器开启异常"""
    pass


class CircuitBreakerManager:
    """
    熔断器管理器
    
    管理多个服务的熔断器
    """
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    def get_or_create(
        self,
        name: str,
        fail_max: int = 5,
        reset_timeout: int = 30,
        success_threshold: int = 2
    ) -> CircuitBreaker:
        """获取或创建熔断器"""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                fail_max=fail_max,
                reset_timeout=reset_timeout,
                success_threshold=success_threshold
            )
        return self._breakers[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """获取熔断器"""
        return self._breakers.get(name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有熔断器的统计信息"""
        return {name: breaker.get_stats() for name, breaker in self._breakers.items()}
    
    def reset_all(self):
        """重置所有熔断器"""
        for breaker in self._breakers.values():
            breaker._reset()
        logger.info("All circuit breakers reset")


def circuit_breaker(
    name: str,
    fail_max: int = 5,
    reset_timeout: int = 30,
    success_threshold: int = 2,
    fallback: Optional[Callable] = None
):
    """
    熔断器装饰器
    
    Usage:
        @circuit_breaker("user-service", fail_max=3)
        async def call_user_service():
            ...
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        breaker = CircuitBreaker(
            name=name,
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            success_threshold=success_threshold
        )
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, fallback=fallback, **kwargs)
        
        wrapper._circuit_breaker = breaker
        return wrapper
    
    return decorator


circuit_breaker_manager = CircuitBreakerManager()
