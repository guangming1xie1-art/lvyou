"""增强的日志系统，支持结构化日志、请求追踪等"""

import json
import time
import sys
import os
import uuid
import inspect
from pathlib import Path
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, Optional
from loguru import logger as loguru_logger

try:
    from config import settings
except ModuleNotFoundError:
    from config import settings

class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self):
        self._request_id = None
        self._logger = loguru_logger
        self._setup_logger()
    
    def _setup_logger(self):
        """配置日志格式"""
        # 移除默认处理器
        self._logger.remove()
        
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 添加文件处理器（JSON格式）
        self._logger.add(
            "logs/agent-{time:YYYY-MM-DD}.log",
            format=self._format_record,
            level="INFO",
            rotation="00:00",
            retention="7 days",
            encoding="utf-8"
        )
        
        # 添加控制台处理器（人类可读）
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[request_id]}</cyan> | "
            "{message}"
        )
        self._logger.add(
            sys.stdout,
            format=log_format,
            level=getattr(settings, "log_level", "INFO"),
            colorize=True
        )
    
    def _format_record(self, record):
        """格式化日志记录为JSON"""
        log_data = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "message": record["message"],
            "request_id": record["extra"].get("request_id", "unknown")
        }
        
        # 添加额外的上下文信息
        if record["extra"]:
            for key, value in record["extra"].items():
                if key != "request_id":
                    log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False) + "\n"
    
    def set_request_id(self, request_id: str):
        """设置请求ID用于追踪"""
        self._request_id = request_id
    
    def get_request_id(self) -> str:
        """获取当前请求ID"""
        return self._request_id or str(uuid.uuid4())
    
    @contextmanager
    def with_request_id(self, request_id: str = None):
        """上下文管理器：临时设置请求ID"""
        old_request_id = self._request_id
        self._request_id = request_id or str(uuid.uuid4())
        try:
            yield self._request_id
        finally:
            self._request_id = old_request_id
    
    def _get_logger(self):
        return self._logger.bind(request_id=self._request_id or "unknown")
    
    def info(self, message: str, **extra):
        """记录INFO级别日志"""
        self._get_logger().bind(**extra).info(message)
    
    def error(self, message: str, exception: Exception = None, **extra):
        """记录ERROR级别日志"""
        if exception:
            extra["exception"] = str(exception)
            extra["exception_type"] = type(exception).__name__
        self._get_logger().bind(**extra).error(message)
    
    def warning(self, message: str, **extra):
        """记录WARNING级别日志"""
        self._get_logger().bind(**extra).warning(message)
    
    def debug(self, message: str, **extra):
        """记录DEBUG级别日志"""
        self._get_logger().bind(**extra).debug(message)

# 全局日志实例
app_logger = StructuredLogger()
# 为了兼容之前的代码，可能有些地方直接导入 logger
logger = app_logger

def log_execution(func):
    """装饰器：自动记录函数执行情况"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.time()
        
        app_logger.debug(f"Starting {func_name}", function=func_name)
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            app_logger.info(
                f"Completed {func_name}",
                function=func_name,
                duration_ms=int(duration * 1000),
                status="success"
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            app_logger.error(
                f"Failed {func_name}: {str(e)}",
                function=func_name,
                duration_ms=int(duration * 1000),
                exception=e
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        func_name = func.__name__
        start_time = time.time()
        
        app_logger.debug(f"Starting {func_name}", function=func_name)
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            app_logger.info(
                f"Completed {func_name}",
                function=func_name,
                duration_ms=int(duration * 1000),
                status="success"
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            app_logger.error(
                f"Failed {func_name}: {str(e)}",
                function=func_name,
                duration_ms=int(duration * 1000),
                exception=e
            )
            raise
    
    # 根据函数是否是async来返回相应的 wrapper
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
