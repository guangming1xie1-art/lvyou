"""
日志配置

从环境变量读取日志相关配置
"""
import os

# 日志配置
LOGGING_CONFIG = {
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_dir": os.getenv("LOG_DIR", "logs"),
    "app_log_file": os.getenv("APP_LOG_FILE", "app.log"),
    "access_log_file": os.getenv("ACCESS_LOG_FILE", "access.log"),
    "error_log_file": os.getenv("ERROR_LOG_FILE", "error.log"),
    "enable_console": os.getenv("LOG_ENABLE_CONSOLE", "true").lower() == "true",
}
