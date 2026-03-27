"""
监控指标集成

提供 Prometheus 指标采集，包括：
- 请求计数
- 请求延迟
- LLM Token 使用量
- 缓存命中率
- 记忆加载时间
- 自定义业务指标
"""
import time
import logging
from typing import Callable, Optional
from functools import wraps
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, Info
    from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
    from prometheus_client import push_to_gateway, delete_from_gateway
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not available, metrics disabled")
    Counter = Histogram = Gauge = Summary = Info = None


@dataclass
class MetricConfig:
    """指标配置"""
    enabled: bool = True
    push_gateway_url: Optional[str] = None
    job_name: str = "travel_assistant_agent"
    instance: str = "agent"


class MetricsCollector:
    """
    指标收集器
    
    提供统一的指标定义和采集接口
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._config = MetricConfig()
        self._metrics = {}
        
        if PROMETHEUS_AVAILABLE:
            self._init_metrics()
    
    def _init_metrics(self):
        """初始化指标"""
        registry = CollectorRegistry()
        
        self._metrics["registry"] = registry
        
        self._metrics["request_count"] = Counter(
            "agent_requests_total",
            "Total agent requests",
            ["endpoint", "method", "status"],
            registry=registry
        )
        
        self._metrics["request_latency"] = Histogram(
            "agent_request_duration_seconds",
            "Agent request latency in seconds",
            ["endpoint", "method"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=registry
        )
        
        self._metrics["llm_token_usage"] = Counter(
            "llm_tokens_total",
            "LLM token usage",
            ["model", "type", "endpoint"],
            registry=registry
        )
        
        self._metrics["llm_request_duration"] = Histogram(
            "llm_request_duration_seconds",
            "LLM request duration in seconds",
            ["model", "endpoint"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
            registry=registry
        )
        
        self._metrics["cache_hit_rate"] = Gauge(
            "cache_hit_rate",
            "Cache hit rate",
            ["cache_type"],
            registry=registry
        )
        
        self._metrics["cache_hits"] = Counter(
            "cache_hits_total",
            "Total cache hits",
            ["cache_type"],
            registry=registry
        )
        
        self._metrics["cache_misses"] = Counter(
            "cache_misses_total",
            "Total cache misses",
            ["cache_type"],
            registry=registry
        )
        
        self._metrics["memory_load_duration"] = Histogram(
            "memory_load_duration_seconds",
            "Memory load duration in seconds",
            ["memory_type"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
            registry=registry
        )
        
        self._metrics["workflow_duration"] = Histogram(
            "workflow_duration_seconds",
            "Workflow execution duration in seconds",
            ["workflow_name", "stage"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0],
            registry=registry
        )
        
        self._metrics["active_sessions"] = Gauge(
            "active_sessions",
            "Number of active sessions",
            registry=registry
        )
        
        self._metrics["active_users"] = Gauge(
            "active_users",
            "Number of active users",
            registry=registry
        )
        
        self._metrics["error_count"] = Counter(
            "agent_errors_total",
            "Total agent errors",
            ["error_type", "endpoint"],
            registry=registry
        )
        
        self._metrics["java_service_calls"] = Histogram(
            "java_service_call_duration_seconds",
            "Java service call duration in seconds",
            ["service", "method"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=registry
        )
        
        self._metrics["mcp_tool_invocations"] = Counter(
            "mcp_tool_invocations_total",
            "Total MCP tool invocations",
            ["tool_name", "status"],
            registry=registry
        )
    
    def inc_request(self, endpoint: str, method: str, status: int):
        """增加请求计数"""
        if "request_count" in self._metrics:
            self._metrics["request_count"].labels(
                endpoint=endpoint,
                method=method,
                status=str(status)
            ).inc()
    
    def observe_request_latency(self, endpoint: str, method: str, duration: float):
        """观察请求延迟"""
        if "request_latency" in self._metrics:
            self._metrics["request_latency"].labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
    
    def inc_llm_token(self, model: str, token_type: str, endpoint: str, count: int = 1):
        """增加 LLM Token 使用量"""
        if "llm_token_usage" in self._metrics:
            self._metrics["llm_token_usage"].labels(
                model=model,
                type=token_type,
                endpoint=endpoint
            ).inc(count)
    
    def observe_llm_duration(self, model: str, endpoint: str, duration: float):
        """观察 LLM 请求时长"""
        if "llm_request_duration" in self._metrics:
            self._metrics["llm_request_duration"].labels(
                model=model,
                endpoint=endpoint
            ).observe(duration)
    
    def set_cache_hit_rate(self, cache_type: str, rate: float):
        """设置缓存命中率"""
        if "cache_hit_rate" in self._metrics:
            self._metrics["cache_hit_rate"].labels(cache_type=cache_type).set(rate)
    
    def inc_cache_hits(self, cache_type: str):
        """增加缓存命中计数"""
        if "cache_hits" in self._metrics:
            self._metrics["cache_hits"].labels(cache_type=cache_type).inc()
    
    def inc_cache_misses(self, cache_type: str):
        """增加缓存未命中计数"""
        if "cache_misses" in self._metrics:
            self._metrics["cache_misses"].labels(cache_type=cache_type).inc()
    
    def observe_memory_load(self, memory_type: str, duration: float):
        """观察记忆加载时间"""
        if "memory_load_duration" in self._metrics:
            self._metrics["memory_load_duration"].labels(memory_type=memory_type).observe(duration)
    
    def observe_workflow(self, workflow_name: str, stage: str, duration: float):
        """观察工作流执行时间"""
        if "workflow_duration" in self._metrics:
            self._metrics["workflow_duration"].labels(
                workflow_name=workflow_name,
                stage=stage
            ).observe(duration)
    
    def set_active_sessions(self, count: int):
        """设置活跃会话数"""
        if "active_sessions" in self._metrics:
            self._metrics["active_sessions"].set(count)
    
    def set_active_users(self, count: int):
        """设置活跃用户数"""
        if "active_users" in self._metrics:
            self._metrics["active_users"].set(count)
    
    def inc_error(self, error_type: str, endpoint: str):
        """增加错误计数"""
        if "error_count" in self._metrics:
            self._metrics["error_count"].labels(
                error_type=error_type,
                endpoint=endpoint
            ).inc()
    
    def observe_java_service_call(self, service: str, method: str, duration: float):
        """观察 Java 服务调用时间"""
        if "java_service_calls" in self._metrics:
            self._metrics["java_service_calls"].labels(
                service=service,
                method=method
            ).observe(duration)
    
    def inc_mcp_invocation(self, tool_name: str, status: str):
        """增加 MCP 工具调用计数"""
        if "mcp_tool_invocations" in self._metrics:
            self._metrics["mcp_tool_invocations"].labels(
                tool_name=tool_name,
                status=status
            ).inc()
    
    def get_metrics(self) -> bytes:
        """获取 Prometheus 指标数据"""
        if "registry" in self._metrics:
            return generate_latest(self._registry())
        return b""
    
    def _registry(self):
        """获取注册表"""
        return self._metrics.get("registry")
    
    def push_to_gateway(self):
        """推送到 Push Gateway"""
        if self._config.push_gateway_url and "registry" in self._metrics:
            try:
                push_to_gateway(
                    self._config.push_gateway_url,
                    job=self._config.job_name,
                    grouping_key={"instance": self._config.instance},
                    registry=self._metrics["registry"]
                )
            except Exception as e:
                logger.error(f"Failed to push metrics to gateway: {e}")


metrics_collector = MetricsCollector()


def track_request_metrics(endpoint: str):
    """请求指标装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            method = func.__name__
            start_time = time.time()
            status = 200
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 500
                metrics_collector.inc_error(type(e).__name__, endpoint)
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.inc_request(endpoint, method, status)
                metrics_collector.observe_request_latency(endpoint, method, duration)
        
        return wrapper
    return decorator


def track_llm_metrics(model: str, endpoint: str):
    """LLM 指标装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            prompt_tokens = 0
            completion_tokens = 0
            
            try:
                result = await func(*args, **kwargs)
                
                if isinstance(result, dict):
                    prompt_tokens = result.get("usage", {}).get("prompt_tokens", 0)
                    completion_tokens = result.get("usage", {}).get("completion_tokens", 0)
                
                return result
            finally:
                duration = time.time() - start_time
                metrics_collector.observe_llm_duration(model, endpoint, duration)
                
                if prompt_tokens > 0:
                    metrics_collector.inc_llm_token(model, "prompt", endpoint, prompt_tokens)
                if completion_tokens > 0:
                    metrics_collector.inc_llm_token(model, "completion", endpoint, completion_tokens)
        
        return wrapper
    return decorator


@asynccontextmanager
async def track_duration(metric_name: str, **labels):
    """跟踪执行时长的上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.debug(f"{metric_name} took {duration:.3f}s")


class MetricsMiddleware:
    """FastAPI 指标中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        path = scope.get("path", "/")
        method = scope.get("method", "GET")
        
        start_time = time.time()
        status = 200
        
        async def send_wrapper(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message.get("status", 200)
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            status = 500
            metrics_collector.inc_error(type(e).__name__, path)
            raise
        finally:
            duration = time.time() - start_time
            metrics_collector.inc_request(path, method, status)
            metrics_collector.observe_request_latency(path, method, duration)
