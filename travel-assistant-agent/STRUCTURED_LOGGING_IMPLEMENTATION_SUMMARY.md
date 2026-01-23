# 结构化日志系统实现总结

## 实现完成时间
2026-01-23

## 任务目标
统一Agent项目的日志系统，实现结构化日志、请求追踪、日志分类输出，便于维护、监控和故障排查。

## 已完成的工作

### 1. ✅ 创建结构化日志工具 (`src/utils/structured_logger.py`)
- 实现 `StructuredLogger` 类管理日志系统
- 实现 `CustomJsonFormatter` 自定义JSON格式化器
- 实现 `RequestIdFilter` 添加请求上下文到日志
- 提供便捷函数：`get_app_logger()`, `get_error_logger()`, `set_request_context()` 等
- 支持日志分类：应用日志、访问日志、错误日志

### 2. ✅ 添加依赖 (`requirements.txt`)
- 添加 `python-json-logger>=2.0.7`

### 3. ✅ 创建日志配置 (`src/config/logging_config.py`)
- 从环境变量读取日志配置
- 支持配置日志级别、目录、文件名等

### 4. ✅ 更新主应用 (`src/main.py`)
- 初始化结构化日志系统
- 添加请求追踪中间件
- 自动为每个请求生成 request_id
- 记录请求/响应信息和耗时
- 在响应头中添加 X-Request-ID

### 5. ✅ 更新环境变量配置 (`.env.example`)
- 添加日志配置项：
  - `LOG_LEVEL`: 日志级别
  - `LOG_DIR`: 日志目录
  - `APP_LOG_FILE`: 应用日志文件名
  - `ACCESS_LOG_FILE`: 访问日志文件名
  - `ERROR_LOG_FILE`: 错误日志文件名
  - `LOG_ENABLE_CONSOLE`: 是否输出到控制台

### 6. ✅ 更新向后兼容层 (`src/utils/logger.py`)
- 保留旧的 `app_logger` 和 `logger` 导出
- 内部使用新的结构化日志系统
- 保持向后兼容，旧代码无需修改

### 7. ✅ 更新认证路由 (`src/api/auth_routes.py`)
- 使用新的结构化日志系统
- 记录详细的用户操作信息
- 记录错误时包含完整上下文

### 8. ✅ 更新认证API客户端 (`src/utils/auth_api_client.py`)
- 使用新的结构化日志系统
- 记录Java服务调用的详细信息
- 记录错误时包含服务信息和堆栈

### 9. ✅ 创建测试脚本 (`test_structured_logging.py`)
- 测试基本日志功能
- 测试请求上下文追踪
- 测试错误日志和异常追踪
- 验证JSON格式有效性
- 验证日志文件分类

### 10. ✅ 创建使用指南 (`STRUCTURED_LOGGING_GUIDE.md`)
- 详细的使用说明
- 日志输出示例
- 最佳实践
- 与监控工具集成方法
- 故障排查指南

## 技术特点

### 1. JSON结构化格式
所有日志统一为JSON格式，便于机器解析和搜索：
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

### 2. 请求链路追踪
- 每个请求自动生成唯一的 `request_id`
- 支持从请求头 `X-Request-ID` 读取或自动生成
- 所有日志自动包含 `request_id`、`user_id`、`trace_id`
- 可追踪完整的请求链路：前端 → Agent → Java → 数据库

### 3. 日志分类输出
- **应用日志** (`logs/app.log`): 所有应用级别的日志
- **访问日志** (`logs/access.log`): HTTP请求/响应日志
- **错误日志** (`logs/error.log`): 错误和异常日志

### 4. 完整的上下文信息
每条日志包含：
- `timestamp`: ISO 8601格式的时间戳
- `level`: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `logger`: Logger名称
- `module`: 文件名和行号
- `function`: 函数名
- `request_id`: 请求ID
- `user_id`: 用户ID
- `trace_id`: 追踪ID
- `service`: 服务名称
- 自定义字段（以 `extra_` 前缀添加）

### 5. 异常堆栈追踪
错误日志包含完整的异常信息：
```json
{
  "exception": {
    "type": "ConnectError",
    "message": "All connection attempts failed",
    "traceback": ["Traceback...", "..."]
  }
}
```

### 6. 可配置化管理
- 支持通过环境变量配置日志级别、输出目录等
- 支持控制台和文件双输出
- 支持按日志级别分类输出

### 7. 向后兼容
- 旧的 `from utils.logger import app_logger` 仍然可用
- 旧代码无需修改即可工作
- 建议逐步迁移到新系统

## 使用示例

### 基本使用
```python
from utils.structured_logger import get_app_logger

logger = get_app_logger(__name__)

logger.info(
    "User login successful",
    extra={
        "extra_username": "admin",
        "extra_ip": "192.168.1.100"
    }
)
```

### 错误处理
```python
from utils.structured_logger import get_error_logger

error_logger = get_error_logger()

try:
    result = call_api()
except Exception as e:
    error_logger.error(
        "API call failed",
        exc_info=True,
        extra={
            "extra_api": "auth-service",
            "extra_endpoint": "/auth/login",
            "extra_error": str(e)
        }
    )
    raise
```

### 请求追踪
```python
from utils.structured_logger import set_request_context, clear_request_context

# 请求开始时
set_request_context(
    request_id="req-123",
    user_id="user-001"
)

# 处理请求...
logger.info("Processing request")

# 请求结束时
clear_request_context()
```

## 日志分析示例

### 追踪完整请求链路
```bash
# 查找特定请求的所有日志
grep "abc-123-def-456" logs/*.log | jq .

# 按时间排序
grep "abc-123-def-456" logs/*.log | jq -s 'sort_by(.timestamp)'
```

### 查找错误
```bash
# 查看所有错误
cat logs/error.log | jq .

# 查找特定类型的错误
cat logs/error.log | jq 'select(.exception.type == "ConnectError")'
```

### 性能分析
```bash
# 查找慢请求（耗时超过1秒）
cat logs/app.log | jq 'select(.duration_ms > 1000)'

# 统计平均响应时间
cat logs/app.log | jq -s '[.[] | select(.duration_ms)] | map(.duration_ms) | add / length'
```

## 验收标准完成情况

- ✅ 创建了 `StructuredLogger` 类和相关日志工具
- ✅ 所有日志都是JSON格式，便于解析和收集
- ✅ 每个请求有唯一的request_id，可追踪完整链路
- ✅ 日志包含完整上下文（时间、模块、行号、函数名、user_id等）
- ✅ 日志分为应用/访问/错误三个类别，输出到不同文件
- ✅ 异常情况包含完整的堆栈信息
- ✅ 支持日志级别和输出目标的配置化管理
- ✅ 创建了中间件，为每个请求自动生成和追踪request_id
- ✅ 关键模块（auth_routes.py, auth_api_client.py）已更新为使用新的结构化日志
- ✅ 日志目录自动创建（logs/）
- ✅ 支持控制台和文件输出

## 测试结果

运行 `test_structured_logging.py` 测试脚本，所有测试通过：
- ✅ 基本日志功能正常
- ✅ 请求上下文追踪正常
- ✅ 错误日志和异常追踪正常
- ✅ JSON格式有效
- ✅ 日志文件分类正常

## 优势

1. **可追踪性**: 每个请求有唯一ID，可追踪从前端到数据库的完整链路
2. **可搜索性**: JSON格式便于用grep/jq等工具快速搜索
3. **易于集成**: 可集成ELK、Datadog、Sentry等监控工具
4. **结构化**: 统一的日志格式，便于自动化分析和告警
5. **可维护性**: 清晰的日志级别、模块和上下文信息，易于定位问题
6. **性能友好**: 异步日志处理，不阻塞业务逻辑
7. **灵活配置**: 通过环境变量控制日志级别、输出目标等

## 后续建议

1. **逐步迁移**: 将其他模块的日志也迁移到新系统
2. **集成监控**: 配置ELK或Datadog采集日志
3. **告警规则**: 基于日志设置告警规则
4. **日志清理**: 配置日志轮转和清理策略
5. **性能监控**: 基于 `duration_ms` 字段监控API性能

## 相关文档

- [结构化日志使用指南](./STRUCTURED_LOGGING_GUIDE.md)
- [测试脚本](./test_structured_logging.py)
- [日志配置](./src/config/logging_config.py)
- [结构化日志工具](./src/utils/structured_logger.py)

## 备注

- 所有日志文件存放在 `logs/` 目录
- 日志文件已添加到 `.gitignore`
- 支持通过环境变量 `LOG_LEVEL` 动态调整日志级别
- 旧代码保持向后兼容，可以平滑迁移
