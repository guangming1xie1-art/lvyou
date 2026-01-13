"""
性能监控中间件
记录请求响应时间、慢查询警告等
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    性能监控中间件
    - 记录每个请求的处理时间
    - 对慢请求发出警告
    - 添加响应时间头
    """

    def __init__(
        self,
        app: ASGIApp,
        slow_request_threshold: float = 1.0,
        log_all_requests: bool = True,
    ):
        """
        初始化性能监控中间件

        Args:
            app: ASGI 应用
            slow_request_threshold: 慢请求阈值（秒）
            log_all_requests: 是否记录所有请求
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.log_all_requests = log_all_requests

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录性能指标

        Args:
            request: 请求对象
            call_next: 下一个中间件

        Returns:
            响应对象
        """
        # 记录开始时间
        start_time = time.time()

        # 处理请求
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录错误
            process_time = time.time() - start_time
            logger.error(
                f"请求处理异常: {request.method} {request.url.path} "
                f"耗时: {process_time:.3f}s 错误: {str(e)}"
            )
            raise

        # 计算处理时间
        process_time = time.time() - start_time

        # 添加性能头
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        # 日志记录
        log_message = (
            f"{request.method} {request.url.path} "
            f"状态: {response.status_code} "
            f"耗时: {process_time:.3f}s"
        )

        # 慢请求警告
        if process_time > self.slow_request_threshold:
            logger.warning(f"慢请求 ⚠️  {log_message}")
        elif self.log_all_requests:
            logger.info(log_message)

        # 添加性能分类
        if process_time < 0.1:
            response.headers["X-Performance"] = "excellent"
        elif process_time < 0.5:
            response.headers["X-Performance"] = "good"
        elif process_time < 1.0:
            response.headers["X-Performance"] = "acceptable"
        else:
            response.headers["X-Performance"] = "slow"

        return response


class RequestLogger:
    """请求日志记录器（用于统计分析）"""

    def __init__(self):
        self.requests = []
        self.max_records = 1000

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        process_time: float,
    ):
        """
        记录请求信息

        Args:
            method: HTTP 方法
            path: 请求路径
            status_code: 状态码
            process_time: 处理时间
        """
        record = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "process_time": process_time,
            "timestamp": time.time(),
        }

        self.requests.append(record)

        # 限制记录数量
        if len(self.requests) > self.max_records:
            self.requests = self.requests[-self.max_records:]

    def get_stats(self) -> dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        if not self.requests:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "slowest_request": None,
                "fastest_request": None,
            }

        process_times = [r["process_time"] for r in self.requests]
        slowest = max(self.requests, key=lambda x: x["process_time"])
        fastest = min(self.requests, key=lambda x: x["process_time"])

        return {
            "total_requests": len(self.requests),
            "avg_response_time": sum(process_times) / len(process_times),
            "max_response_time": max(process_times),
            "min_response_time": min(process_times),
            "slowest_request": {
                "method": slowest["method"],
                "path": slowest["path"],
                "time": slowest["process_time"],
            },
            "fastest_request": {
                "method": fastest["method"],
                "path": fastest["path"],
                "time": fastest["process_time"],
            },
            "slow_requests_count": sum(
                1 for t in process_times if t > 1.0
            ),
        }

    def clear(self):
        """清空记录"""
        self.requests = []


# 全局请求日志记录器实例
request_logger = RequestLogger()
