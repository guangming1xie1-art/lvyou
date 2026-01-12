"""
工具模块

提供各种通用工具和客户端：
- 日志: app_logger
- 数据库: db_manager
- API 客户端: api_client, backend_client
- Claude 客户端: claude_client
- Java API 客户端: java_api_client
"""

from .logger import app_logger, log_execution
from .db import db_manager
from .api_client import APIClient, BackendAPIClient, backend_client
from .claude import ClaudeClient, claude_client
from .java_api_client import (
    java_api_client,
    JavaAPIClient,
    MockDataGenerator
)
from .exceptions import (
    AgentException, AgentExecutionError, SkillExecutionError,
    JavaAPIError, JavaAPITimeoutError, JavaAPINotFoundError,
    JavaAPIValidationError, JavaAPIServerError, JavaAPIAuthError,
    ValidationError, TimeoutError
)
from .metrics import metrics
from .log_viewer import LogViewer

__all__ = [
    # Logger
    "app_logger",
    "log_execution",

    # Database
    "db_manager",

    # API Clients
    "APIClient",
    "BackendAPIClient",
    "backend_client",

    # Claude
    "ClaudeClient",
    "claude_client",

    # Java API Client
    "java_api_client",
    "JavaAPIClient",
    "MockDataGenerator",

    # Exceptions
    "AgentException",
    "AgentExecutionError",
    "SkillExecutionError",
    "JavaAPIError",
    "JavaAPITimeoutError",
    "JavaAPINotFoundError",
    "JavaAPIValidationError",
    "JavaAPIServerError",
    "JavaAPIAuthError",
    "ValidationError",
    "TimeoutError",

    # Metrics and Logging
    "metrics",
    "LogViewer"
]
