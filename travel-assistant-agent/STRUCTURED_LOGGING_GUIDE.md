# 结构化日志系统使用指南

## 概述

本项目已实现完整的结构化日志系统，支持：
- ✅ JSON格式日志输出
- ✅ 请求链路追踪（request_id）
- ✅ 日志分类输出（应用/访问/错误）
- ✅ 完整的异常堆栈追踪
- ✅ 可配置的日志级别和输出目标
- ✅ 便于集成ELK、Datadog等监控工具

## 快速开始

### 1. 基本使用

```python
from utils.structured_logger import get_app_logger

logger = get_app_logger(__name__)

# 记录信息日志
logger.info("用户登录成功")

# 记录警告
logger.warning("API响应时间过长")

# 记录错误
try:
    # some code
    pass
except Exception as e:
    logger.error("操作失败", exc_info=True)
```

### 2. 添加额外字段

```python
logger.info(
    "Java auth-service调用成功",
    extra={
        "extra_username": "admin",
        "extra_service": "auth-service",
        "extra_status_code": 200,
        "extra_duration_ms": 125.5
    }
)
```

**重要**：所有自定义字段必须以 `extra_` 前缀开头，日志输出时会自动去掉前缀。

### 3. 请求追踪

在中间件或请求处理开始时设置请求上下文：

```python
from utils.structured_logger import set_request_context, clear_request_context
import uuid

# 设置请求上下文
request_id = str(uuid.uuid4())
set_request_context(
    request_id=request_id,
    user_id="user-123"
)

# 之后的所有日志都会自动包含 request_id 和 user_id
logger.info("处理用户请求")

# 请求结束时清除上下文
clear_request_context()
```

### 4. 错误日志

使用专门的错误logger记录错误：

```python
from utils.structured_logger import get_error_logger

error_logger = get_error_logger()

try:
    # 可能出错的代码
    result = risky_operation()
except Exception as e:
    error_logger.error(
        "操作失败",
        exc_info=True,  # 包含完整堆栈信息
        extra={
            "extra_operation": "risky_operation",
            "extra_input": input_data
        }
    )
    raise
```

## 日志输出示例

### 应用日志 (logs/app.log)

```json
{
  "message": "User login attempt",
  "timestamp": "2026-01-23T07:49:06.123Z",
  "level": "INFO",
  "logger": "api.auth_routes",
  "module": "auth_routes.py:92",
  "function": "login",
  "request_id": "abc-123-def-456",
  "user_id": "admin",
  "trace_id": "abc-123-def-456",
  "service": "travel-assistant-agent",
  "username": "admin"
}
```

### 错误日志 (logs/error.log)

```json
{
  "message": "Java auth-service login failed",
  "timestamp": "2026-01-23T07:49:09.456Z",
  "level": "ERROR",
  "logger": "utils.auth_api_client",
  "module": "auth_api_client.py:145",
  "function": "login",
  "request_id": "abc-123-def-456",
  "user_id": "admin",
  "trace_id": "abc-123-def-456",
  "service": "travel-assistant-agent",
  "exception": {
    "type": "ConnectError",
    "message": "All connection attempts failed",
    "traceback": ["Traceback...", "..."]
  },
  "username": "admin",
  "service": "auth-service",
  "error": "All connection attempts failed"
}
```

## 配置

### 环境变量

在 `.env` 文件中配置日志系统：

```bash
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 日志目录
LOG_DIR=logs

# 日志文件名
APP_LOG_FILE=app.log
ACCESS_LOG_FILE=access.log
ERROR_LOG_FILE=error.log

# 是否输出到控制台
LOG_ENABLE_CONSOLE=true
```

## 日志分析

### 1. 追踪完整请求链路

使用 request_id 搜索所有相关日志：

```bash
# 查找特定请求的所有日志
grep "abc-123-def-456" logs/*.log | jq .

# 按时间排序
grep "abc-123-def-456" logs/*.log | jq -s 'sort_by(.timestamp)'
```

### 2. 查找错误日志

```bash
# 查看所有错误
cat logs/error.log | jq .

# 查找特定类型的错误
cat logs/error.log | jq 'select(.exception.type == "ConnectError")'

# 统计错误类型
cat logs/error.log | jq -r '.exception.type' | sort | uniq -c
```

### 3. 性能分析

```bash
# 查找慢请求（耗时超过1秒）
cat logs/app.log | jq 'select(.duration_ms > 1000)'

# 统计平均响应时间
cat logs/app.log | jq -s '[.[] | select(.duration_ms)] | map(.duration_ms) | add / length'
```

### 4. 用户行为分析

```bash
# 查找特定用户的所有操作
grep '"user_id": "admin"' logs/*.log | jq .

# 统计用户操作频率
grep 'user_id' logs/app.log | jq -r '.user_id' | sort | uniq -c
```

## 最佳实践

### 1. 日志级别使用

- **DEBUG**: 详细的调试信息，生产环境通常不开启
- **INFO**: 重要的业务流程信息，如用户登录、API调用等
- **WARNING**: 警告信息，如API响应慢、资源使用率高等
- **ERROR**: 错误信息，需要人工介入处理

### 2. 日志消息格式

```python
# ❌ 不好的做法
logger.info(f"user {username} login at {timestamp} from {ip}")

# ✅ 好的做法
logger.info(
    "User login",
    extra={
        "extra_username": username,
        "extra_timestamp": timestamp,
        "extra_ip": ip
    }
)
```

### 3. 错误处理

```python
# ✅ 总是包含完整的上下文信息
try:
    result = call_external_api(data)
except Exception as e:
    error_logger.error(
        "External API call failed",
        exc_info=True,  # 包含堆栈信息
        extra={
            "extra_api": "external-service",
            "extra_endpoint": "/api/data",
            "extra_request_data": data,
            "extra_error": str(e)
        }
    )
    raise
```

### 4. 请求追踪

```python
# 在HTTP请求处理开始时
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    
    set_request_context(
        request_id=request_id,
        user_id=get_user_from_request(request)
    )
    
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        clear_request_context()
```

## 与监控工具集成

### ELK Stack

日志已经是JSON格式，可直接被Logstash采集：

```yaml
# logstash.conf
input {
  file {
    path => "/path/to/logs/*.log"
    codec => json
  }
}

filter {
  # 添加自定义过滤规则
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "travel-assistant-%{+YYYY.MM.dd}"
  }
}
```

### Datadog

使用Datadog Agent采集日志：

```yaml
# datadog.yaml
logs:
  - type: file
    path: /path/to/logs/app.log
    service: travel-assistant-agent
    source: python
    sourcecategory: application
```

### Sentry

错误日志可以集成到Sentry：

```python
import sentry_sdk

sentry_sdk.init(dsn="your-dsn")

# 错误会自动发送到Sentry
try:
    risky_operation()
except Exception as e:
    error_logger.error("Operation failed", exc_info=True)
    raise
```

## 故障排查

### 问题1: 日志文件为空

**原因**: 日志级别设置过高，或没有flush
**解决**: 检查 `LOG_LEVEL` 配置，确保日志级别正确

### 问题2: request_id 显示为 "N/A"

**原因**: 没有设置请求上下文
**解决**: 在请求处理开始时调用 `set_request_context()`

### 问题3: 自定义字段没有出现在日志中

**原因**: 字段名没有 `extra_` 前缀
**解决**: 所有自定义字段必须以 `extra_` 开头

## 迁移指南

### 从旧的日志系统迁移

旧代码仍然可以工作（向后兼容），但建议逐步迁移：

```python
# 旧代码（仍然可用）
from utils.logger import app_logger
app_logger.info(f"User login: {username}")

# 新代码（推荐）
from utils.structured_logger import get_app_logger
logger = get_app_logger(__name__)
logger.info("User login", extra={"extra_username": username})
```

## 测试

运行测试脚本验证日志系统：

```bash
cd /path/to/travel-assistant-agent
python test_structured_logging.py
```

## 总结

结构化日志系统提供了：
- 统一的JSON格式，便于机器解析
- 完整的请求链路追踪
- 详细的错误上下文
- 灵活的配置选项
- 与监控工具的无缝集成

遵循本指南的最佳实践，可以大大提高系统的可观测性和问题定位效率。
