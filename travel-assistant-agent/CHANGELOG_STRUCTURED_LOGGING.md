# Changelog - 结构化日志系统

## [2.1.0] - 2026-01-23

### 新增 (Added)

#### 核心功能
- ✨ **结构化日志系统** (`src/utils/structured_logger.py`)
  - JSON格式日志输出
  - 请求链路追踪（request_id）
  - 日志分类输出（应用/访问/错误）
  - 完整的异常堆栈追踪
  - 可配置化管理

- ✨ **日志配置模块** (`src/config/logging_config.py`)
  - 支持环境变量配置
  - 灵活的日志级别和输出目标设置

- ✨ **请求追踪中间件** (在 `src/main.py` 中)
  - 自动为每个请求生成唯一ID
  - 记录请求/响应信息和耗时
  - 在响应头中添加 X-Request-ID

#### 依赖
- 📦 添加 `python-json-logger>=2.0.7` 到 `requirements.txt`

#### 文档
- 📚 **使用指南** (`STRUCTURED_LOGGING_GUIDE.md`)
  - 详细的使用说明和示例
  - 最佳实践和故障排查
  - 与监控工具集成方法

- 📚 **实现总结** (`STRUCTURED_LOGGING_IMPLEMENTATION_SUMMARY.md`)
  - 完整的实现细节
  - 技术特点和优势
  - 测试结果和后续建议

- 📚 **测试脚本** (`test_structured_logging.py`)
  - 自动化测试脚本
  - 验证日志系统各项功能

### 修改 (Changed)

#### 更新的文件
- 🔄 `src/main.py`
  - 初始化结构化日志系统
  - 添加请求追踪中间件
  - 记录请求/响应日志

- 🔄 `src/api/auth_routes.py`
  - 使用新的结构化日志系统
  - 添加详细的操作日志和错误追踪

- 🔄 `src/utils/auth_api_client.py`
  - 使用新的结构化日志系统
  - 记录Java服务调用的详细信息

- 🔄 `src/utils/logger.py`
  - 更新为向后兼容层
  - 内部使用新的结构化日志系统

- 🔄 `.env.example`
  - 添加日志配置项：
    - `LOG_LEVEL`
    - `LOG_DIR`
    - `APP_LOG_FILE`
    - `ACCESS_LOG_FILE`
    - `ERROR_LOG_FILE`
    - `LOG_ENABLE_CONSOLE`

### 特性 (Features)

#### 1. JSON结构化格式
所有日志统一为JSON格式，便于机器解析：
```json
{
  "timestamp": "2026-01-23T07:49:06.123Z",
  "level": "INFO",
  "message": "User login attempt",
  "request_id": "abc-123",
  "user_id": "admin"
}
```

#### 2. 请求链路追踪
- 每个请求唯一的 `request_id`
- 可追踪完整请求链路
- 支持从请求头传递追踪ID

#### 3. 日志分类输出
- `logs/app.log` - 应用日志
- `logs/access.log` - 访问日志
- `logs/error.log` - 错误日志

#### 4. 完整上下文信息
每条日志包含：
- timestamp (ISO 8601)
- level (日志级别)
- logger (Logger名称)
- module (文件名:行号)
- function (函数名)
- request_id (请求ID)
- user_id (用户ID)
- 自定义字段

#### 5. 异常堆栈追踪
错误日志包含完整异常信息和堆栈

### 向后兼容 (Backward Compatibility)

- ✅ 旧的 `from utils.logger import app_logger` 仍然可用
- ✅ 旧代码无需修改即可工作
- ✅ 建议逐步迁移到新系统

### 使用示例

#### 基本使用
```python
from utils.structured_logger import get_app_logger

logger = get_app_logger(__name__)
logger.info("操作成功", extra={"extra_user": "admin"})
```

#### 错误处理
```python
from utils.structured_logger import get_error_logger

error_logger = get_error_logger()
try:
    risky_operation()
except Exception as e:
    error_logger.error("操作失败", exc_info=True)
```

#### 请求追踪
```python
from utils.structured_logger import set_request_context

set_request_context(
    request_id="req-123",
    user_id="user-001"
)
```

### 测试

运行测试脚本：
```bash
python test_structured_logging.py
```

所有测试通过 ✅

### 日志分析

#### 追踪请求链路
```bash
grep "abc-123" logs/*.log | jq .
```

#### 查找错误
```bash
cat logs/error.log | jq 'select(.exception.type == "ConnectError")'
```

#### 性能分析
```bash
cat logs/app.log | jq 'select(.duration_ms > 1000)'
```

### 优势

1. **可追踪性** - 完整的请求链路追踪
2. **可搜索性** - JSON格式便于搜索分析
3. **易于集成** - 支持ELK、Datadog等工具
4. **结构化** - 统一的日志格式
5. **可维护性** - 清晰的上下文信息
6. **灵活配置** - 环境变量配置

### 后续计划

- [ ] 迁移其他模块到新日志系统
- [ ] 集成ELK/Datadog监控
- [ ] 配置日志告警规则
- [ ] 实施日志清理策略

### 相关链接

- [使用指南](./STRUCTURED_LOGGING_GUIDE.md)
- [实现总结](./STRUCTURED_LOGGING_IMPLEMENTATION_SUMMARY.md)
- [测试脚本](./test_structured_logging.py)

---

**注意**: 本次更新保持向后兼容，旧代码无需修改。建议逐步迁移到新的结构化日志系统以获得更好的可观测性。
