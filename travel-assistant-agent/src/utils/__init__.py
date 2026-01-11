"""
工具模块

提供各种通用工具和客户端：
- 日志: app_logger
- 数据库: db_manager
- API 客户端: api_client, backend_client
- Claude 客户端: claude_client
- Java API 客户端: java_api_client
"""

from utils.logger import app_logger
from utils.db import db_manager
from utils.api_client import APIClient, BackendAPIClient, backend_client
from utils.claude import ClaudeClient, claude_client
from utils.java_api_client import (
    java_api_client,
    JavaAPIClient,
    JavaAPIError,
    JavaAPITimeoutError,
    JavaAPINotFoundError,
    JavaAPIValidationError,
    JavaAPIServerError,
    JavaAPIAuthError,
    MockDataGenerator
)

__all__ = [
    # Logger
    "app_logger",

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
    "JavaAPIError",
    "JavaAPITimeoutError",
    "JavaAPINotFoundError",
    "JavaAPIValidationError",
    "JavaAPIServerError",
    "JavaAPIAuthError",
    "MockDataGenerator"
]
