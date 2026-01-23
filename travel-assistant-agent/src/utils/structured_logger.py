"""
结构化日志系统

提供统一的JSON格式日志、请求追踪、日志分类输出功能
"""
import json
import logging
import uuid
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar
import traceback

# 上下文变量：存储请求级别的追踪信息
request_context: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})


class RequestIdFilter(logging.Filter):
    """添加request_id和其他上下文信息到日志记录"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        context = request_context.get({})
        
        # 添加request_id
        if not hasattr(record, 'request_id'):
            record.request_id = context.get('request_id', 'N/A')
        
        # 添加user_id
        if not hasattr(record, 'user_id'):
            record.user_id = context.get('user_id', 'N/A')
        
        # 添加trace_id
        if not hasattr(record, 'trace_id'):
            record.trace_id = context.get('trace_id', record.request_id)
        
        # 添加服务名称
        if not hasattr(record, 'service'):
            record.service = 'travel-assistant-agent'
        
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """自定义JSON日志格式化器"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # 添加时间戳（ISO 8601格式）
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # 添加logger名称
        log_record['logger'] = record.name
        
        # 添加模块和行号
        log_record['module'] = f"{record.filename}:{record.lineno}"
        
        # 添加函数名
        log_record['function'] = record.funcName
        
        # 添加日志级别
        log_record['level'] = record.levelname
        
        # 添加上下文信息
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        if hasattr(record, 'trace_id'):
            log_record['trace_id'] = record.trace_id
        
        if hasattr(record, 'service'):
            log_record['service'] = record.service
        
        # 如果有异常，添加异常堆栈
        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # 添加自定义字段（从record中提取以extra_开头的属性）
        for key, value in record.__dict__.items():
            if key.startswith('extra_'):
                log_record[key[6:]] = value  # 移除extra_前缀


class StructuredLogger:
    """结构化日志管理器"""
    
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取或创建一个logger实例"""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        return cls._loggers[name]
    
    @classmethod
    def setup_logging(
        cls,
        log_level: str = "INFO",
        log_dir: str = "logs",
        app_log_file: str = "app.log",
        access_log_file: str = "access.log",
        error_log_file: str = "error.log",
        enable_console: bool = True
    ) -> None:
        """
        设置日志系统
        
        参数:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: 日志目录
            app_log_file: 应用日志文件
            access_log_file: 访问日志文件
            error_log_file: 错误日志文件
            enable_console: 是否输出到控制台
        """
        import os
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置根logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # 添加filter
        request_filter = RequestIdFilter()
        
        # JSON格式化器
        json_formatter = CustomJsonFormatter()
        
        # 1. 应用日志处理器（到文件 + 控制台）
        app_logger = cls.get_logger('app')
        app_logger.setLevel(log_level)
        
        # 应用日志到文件
        app_file_handler = logging.FileHandler(f"{log_dir}/{app_log_file}")
        app_file_handler.setLevel(log_level)
        app_file_handler.setFormatter(json_formatter)
        app_file_handler.addFilter(request_filter)
        app_logger.addHandler(app_file_handler)
        
        # 应用日志到控制台
        if enable_console:
            app_console_handler = logging.StreamHandler(sys.stdout)
            app_console_handler.setLevel(log_level)
            app_console_handler.setFormatter(json_formatter)
            app_console_handler.addFilter(request_filter)
            app_logger.addHandler(app_console_handler)
        
        # 2. 访问日志处理器（只到文件）
        access_logger = cls.get_logger('access')
        access_logger.setLevel(logging.INFO)
        access_logger.propagate = False
        
        access_file_handler = logging.FileHandler(f"{log_dir}/{access_log_file}")
        access_file_handler.setLevel(logging.INFO)
        access_file_handler.setFormatter(json_formatter)
        access_file_handler.addFilter(request_filter)
        access_logger.addHandler(access_file_handler)
        
        # 3. 错误日志处理器（到文件 + 控制台）
        error_logger = cls.get_logger('error')
        error_logger.setLevel(logging.ERROR)
        error_logger.propagate = False
        
        error_file_handler = logging.FileHandler(f"{log_dir}/{error_log_file}")
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(json_formatter)
        error_file_handler.addFilter(request_filter)
        error_logger.addHandler(error_file_handler)
        
        if enable_console:
            error_console_handler = logging.StreamHandler(sys.stderr)
            error_console_handler.setLevel(logging.ERROR)
            error_console_handler.setFormatter(json_formatter)
            error_console_handler.addFilter(request_filter)
            error_logger.addHandler(error_console_handler)


# 便捷函数：获取app logger
def get_app_logger(name: str) -> logging.Logger:
    """获取应用logger"""
    return StructuredLogger.get_logger(name)


# 便捷函数：获取访问logger
def get_access_logger(name: str = 'access') -> logging.Logger:
    """获取访问logger"""
    return StructuredLogger.get_logger(name)


# 便捷函数：获取错误logger
def get_error_logger(name: str = 'error') -> logging.Logger:
    """获取错误logger"""
    return StructuredLogger.get_logger(name)


# 便捷函数：设置请求上下文
def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    **kwargs
) -> None:
    """
    设置请求上下文
    
    参数:
        request_id: 请求ID（如果为空则生成UUID）
        user_id: 用户ID
        trace_id: 追踪ID（如果为空则使用request_id）
        **kwargs: 其他自定义字段
    """
    request_id = request_id or str(uuid.uuid4())
    trace_id = trace_id or request_id
    
    context = {
        'request_id': request_id,
        'user_id': user_id,
        'trace_id': trace_id,
        **kwargs
    }
    
    request_context.set(context)


# 便捷函数：清除请求上下文
def clear_request_context() -> None:
    """清除请求上下文"""
    request_context.set({})


# 便捷函数：获取当前请求ID
def get_request_id() -> str:
    """获取当前请求ID"""
    return request_context.get({}).get('request_id', 'N/A')
