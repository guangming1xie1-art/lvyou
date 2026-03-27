"""
错误处理和重试机制

提供：
1. 自定义异常类
2. 重试装饰器
3. 错误处理中间件
"""
import asyncio
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import time

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorCode(Enum):
    """错误代码"""
    UNKNOWN = "unknown"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND = "not_found"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    TIMEOUT_ERROR = "timeout_error"
    NETWORK_ERROR = "network_error"
    INTERNAL_ERROR = "internal_error"


class TemporaryError(Exception):
    """临时错误，可以重试"""
    pass


class PermanentError(Exception):
    """永久错误，不应重试"""
    pass


class ServiceUnavailableError(TemporaryError):
    """服务不可用错误"""
    def __init__(self, service_name: str, message: str = "Service unavailable"):
        self.service_name = service_name
        self.message = message
        super().__init__(f"{service_name}: {message}")


class TimeoutError(TemporaryError):
    """超时错误"""
    pass


class NetworkError(TemporaryError):
    """网络错误"""
    pass


class ValidationError(PermanentError):
    """验证错误"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class AuthenticationError(PermanentError):
    """认证错误"""
    pass


class AuthorizationError(PermanentError):
    """授权错误"""
    pass


@dataclass
class ErrorDetail:
    """错误详情"""
    code: ErrorCode
    message: str
    field: Optional[str] = None
    service: Optional[str] = None
    retry_after: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)


class ErrorResponse:
    """错误响应"""
    
    def __init__(self, error: ErrorDetail, status_code: int = 500):
        self.error = error
        self.status_code = status_code
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "error": {
                "code": self.error.code.value,
                "message": self.error.message
            }
        }
        if self.error.field:
            result["error"]["field"] = self.error.field
        if self.error.service:
            result["error"]["service"] = self.error.service
        if self.error.retry_after:
            result["error"]["retry_after"] = self.error.retry_after
        if self.error.details:
            result["error"]["details"] = self.error.details
        return result


def get_error_response(
    error: Exception,
    default_message: str = "An error occurred"
) -> ErrorResponse:
    """根据异常类型生成错误响应"""
    
    if isinstance(error, ServiceUnavailableError):
        return ErrorResponse(
            ErrorDetail(
                code=ErrorCode.SERVICE_UNAVAILABLE,
                message=error.message or "Service temporarily unavailable",
                service=error.service_name,
                retry_after=30
            ),
            status_code=503
        )
    
    elif isinstance(error, TimeoutError):
        return ErrorResponse(
            ErrorDetail(
                code=ErrorCode.TIMEOUT_ERROR,
                message="Request timeout, please try again",
                retry_after=10
            ),
            status_code=504
        )
    
    elif isinstance(error, NetworkError):
        return ErrorResponse(
            ErrorDetail(
                code=ErrorCode.NETWORK_ERROR,
                message="Network error, please check your connection",
                retry_after=5
            ),
            status_code=502
        )
    
    elif isinstance(error, ValidationError):
        return ErrorResponse(
            ErrorDetail(
                code=ErrorCode.VALIDATION_ERROR,
                message=error.message,
                field=error.field
            ),
            status_code=400
        )
    
    elif isinstance(error, AuthenticationError):
        return ErrorResponse(
            ErrorDetail(
                code=ErrorCode.AUTHENTICATION_ERROR,
                message="Authentication failed"
            ),
            status_code=401
        )
    
    elif isinstance(error, AuthorizationError):
        return ErrorResponse(
            ErrorDetail(
                code=ErrorCode.AUTHORIZATION_ERROR,
                message="Permission denied"
            ),
            status_code=403
        )
    
    elif isinstance(error, PermanentError):
        return ErrorResponse(
            ErrorDetail(
                code=ErrorCode.INTERNAL_ERROR,
                message=str(error) or default_message
            ),
            status_code=500
        )
    
    else:
        return ErrorResponse(
            ErrorDetail(
                code=ErrorCode.UNKNOWN,
                message=default_message
            ),
            status_code=500
        )


def with_retry(
    max_attempts: int = 3,
    wait_min: int = 1,
    wait_max: int = 10,
    retry_on: tuple = (TemporaryError, TimeoutError, NetworkError)
):
    """
    重试装饰器
    
    Usage:
        @with_retry(max_attempts=3, wait_min=1, wait_max=10)
        async def call_service():
            ...
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_attempts:
                        wait_time = min(wait_min * (2 ** (attempt - 1)), wait_max)
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                except PermanentError:
                    raise
                except Exception as e:
                    logger.exception(f"Unexpected error in {func.__name__}")
                    raise
            
            raise last_exception
        
        return wrapper
    return decorator


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self._handlers: Dict[Type[Exception], Callable[[Exception], ErrorResponse]] = {}
    
    def register(self, exception_type: Type[Exception]):
        """注册异常处理器"""
        def decorator(func: Callable[[Exception], ErrorResponse]):
            self._handlers[exception_type] = func
            return func
        return decorator
    
    def handle(self, error: Exception) -> ErrorResponse:
        """处理异常"""
        for exc_type, handler in self._handlers.items():
            if isinstance(error, exc_type):
                return handler(error)
        
        return get_error_response(error)


error_handler = ErrorHandler()


async def safe_execute(
    func: Callable[..., Awaitable[T]],
    fallback: Optional[T] = None,
    default_error: str = "Operation failed"
) -> T:
    """
    安全执行函数，捕获所有异常
    
    Usage:
        result = await safe_execute(
            some_async_function,
            fallback={"error": "default"},
            default_error="Function failed"
        )
    """
    try:
        return await func()
    except Exception as e:
        logger.exception(f"Error in {func.__name__}: {e}")
        if fallback is not None:
            return fallback
        raise


class NodeErrorHandler:
    """工作流节点错误处理器"""
    
    NODE_ERROR_MESSAGES = {
        "collect_info": "信息收集遇到问题，请稍后重试",
        "search": "搜索服务暂时不可用，请稍后重试",
        "recommend": "推荐服务暂时不可用，请稍后重试",
        "booking": "预订服务暂时不可用，请稍后重试",
        "common": "处理遇到问题，请稍后重试"
    }
    
    @staticmethod
    def handle_node_error(node_name: str, error: Exception) -> Dict[str, Any]:
        """处理工作流节点错误"""
        
        if isinstance(error, TemporaryError):
            logger.warning(f"Temporary error in {node_name}: {error}")
            return {
                "error": "temporary_error",
                "message": NodeErrorHandler.NODE_ERROR_MESSAGES.get(node_name, NodeErrorHandler.NODE_ERROR_MESSAGES["common"]),
                "retryable": True,
                "node": node_name
            }
        elif isinstance(error, PermanentError):
            logger.error(f"Permanent error in {node_name}: {error}")
            return {
                "error": "error",
                "message": str(error) or NodeErrorHandler.NODE_ERROR_MESSAGES.get(node_name, "处理失败"),
                "retryable": False,
                "node": node_name
            }
        else:
            logger.exception(f"Unexpected error in {node_name}")
            return {
                "error": "internal_error",
                "message": "服务器内部错误，请稍后重试",
                "retryable": False,
                "node": node_name
            }
    
    @staticmethod
    def get_fallback_response(node_name: str) -> Dict[str, Any]:
        """获取降级响应"""
        return {
            "error": "service_unavailable",
            "message": NodeErrorHandler.NODE_ERROR_MESSAGES.get(node_name, "服务暂时不可用"),
            "fallback": True,
            "node": node_name
        }
