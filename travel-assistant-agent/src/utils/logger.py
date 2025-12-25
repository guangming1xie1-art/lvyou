"""
日志配置模块
使用 Loguru 进行结构化日志记录
"""
import sys
from pathlib import Path

from loguru import logger

from config import settings


def setup_logger():
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    if settings.is_production:
        Path("logs").mkdir(parents=True, exist_ok=True)

        logger.add(
            "logs/app.log",
            format=log_format,
            level="INFO",
            rotation="500 MB",
            retention="10 days",
            compression="zip",
            enqueue=True,
        )

        logger.add(
            "logs/error.log",
            format=log_format,
            level="ERROR",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            enqueue=True,
        )

    return logger


app_logger = setup_logger()
