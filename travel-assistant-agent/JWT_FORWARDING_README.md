# JWT Token Forwarding - Agent to Java Services

## 概述

本功能实现了Agent调用Java微服务API时的JWT token转发，确保完整的认证链路传播。

## 架构设计

```
Client -> Agent (FastAPI) -> Java Services (Spring Boot)
         [JWT验证]          [JWT转发]     [JWT验证]
```

### 认证流程

1. **客户端认证**：用户通过Agent的`/api/auth/login`登录，获取JWT token
2. **Agent验证**：客户端调用Agent API时携带JWT，Agent验证token有效性
3. **Token转发**：Agent调用Java服务时，在HTTP headers中转发JWT
4. **Java验证**：Java服务接收并验证JWT，识别用户身份

## 实现细节

### 1. MCP Client增强 (`src/agents/mcp_client.py`)

**修改内容**：
- `MCPClient.__init__()` - 新增`token`, `user_id`, `username`参数
- `_get_auth_headers()` - 构建包含JWT的请求headers
- `call_tool()` - 在HTTP请求中添加Authorization header
- `get_mcp_client()` - 支持传递JWT token参数

**示例代码**：
```python
# 创建带JWT认证的MCP Client
mcp_client = get_mcp_client(
    token=user_token,
    user_id=current_user.id,
    username=current_user.username
)
```

### 2. Java服务客户端 (`src/utils/java_client.py`)

新增的高级封装工具类，提供：
- 统一的JWT header构建
- 重试机制和超时控制
- 用户上下文传递
- 针对各个Java服务的专用方法

**示例使用**：
```python
from utils.java_client import create_java_client

# 创建客户端
java_client = create_java_client(
    token=jwt_token,
    user_id=user.id,
    username=user.username
)

# 搜索航班
flights = await java_client.search_flights(
    origin="Beijing",
    destination="Tokyo",
    departure_date="2025-03-15"
)

# 创建预订
booking = await java_client.create_booking(booking_data)
```

### 3. API路由修改 (`src/api/routes.py`)

修改了所有调用Java API的端点：
- `/api/agent/search` - 搜索航班和酒店
- `/api/agent/recommend` - 获取推荐
- `/api/agent/book` - 创建预订

**修改模式**：
```python
@router.post("/search")
async def search_travel(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user),
    user_token: str = Depends(get_user_token),  # 获取JWT token
    ...
):
    # 创建带JWT的MCP client
    mcp_client = get_mcp_client(
        token=user_token,
        user_id=current_user.id,
        username=current_user.username
    )
    
    # MCP client会自动在HTTP请求中添加JWT
    result = await mcp_client.call_skill("search_flights", {...})
```

### 4. HTTP Headers

转发到Java服务的Headers：

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
Accept: application/json
X-User-ID: <user_id>
X-Username: <username>
```

## 配置要求

### 关键配置项

在`.env`文件中，以下配置**必须在Agent和Java服务中保持一致**：

```bash
# CRITICAL: 必须与Java服务使用相同的secret
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
```

### Java服务URL配置

```bash
# Java API Gateway
JAVA_API_BASE_URL=http://localhost:8080/api

# Individual Services (可选，直接访问)
JAVA_FLIGHT_SERVICE_URL=http://localhost:8080/api/flights
JAVA_HOTEL_SERVICE_URL=http://localhost:8080/api/hotels
JAVA_BOOKING_SERVICE_URL=http://localhost:8080/api/bookings
JAVA_ATTRACTION_SERVICE_URL=http://localhost:8080/api/attractions
JAVA_RECOMMENDATION_SERVICE_URL=http://localhost:8080/api/recommendations

# Timeout and Retry
JAVA_API_TIMEOUT=30
JAVA_API_MAX_RETRIES=3
```

## 测试

### 自动化测试脚本

运行集成测试：

```bash
cd travel-assistant-agent
./test_jwt_forwarding.sh
```

测试脚本会：
1. ✅ 注册新用户
2. ✅ 登录获取JWT token
3. ✅ 调用search API（验证JWT转发）
4. ✅ 调用recommend API（验证JWT转发）
5. ✅ 检查响应和日志

### 手动测试

**1. 启动服务**

```bash
# 启动Java服务（通过docker-compose）
cd travel-assistant
docker-compose up -d

# 启动Agent
cd travel-assistant-agent
python -m uvicorn src.main:app --reload --port 8000
```

**2. 注册用户**

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

**3. 登录获取Token**

```bash
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }' | jq -r '.tokens.access_token')

echo "Token: $TOKEN"
```

**4. 调用搜索API**

```bash
curl -X POST http://localhost:8000/api/agent/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Beijing",
    "destination": "Tokyo",
    "departure_date": "2025-03-15",
    "passengers": 2,
    "cabin_class": "economy",
    "include_hotels": false
  }'
```

**5. 验证日志**

**Agent端日志**：
```bash
tail -f logs/app.log | grep -i "authorization\|jwt\|x-user"
```

应该看到：
```
Added Authorization header with token
MCP tool search_flights called successfully with JWT auth
```

**Java服务日志**：
```bash
docker logs travel-assistant-gateway | grep -i "authorization\|jwt"
```

应该看到：
```
Received request with Authorization: Bearer eyJ...
User authenticated: user_id=123, username=testuser
```

## 故障排查

### 问题1: JWT验证失败

**症状**：Java服务返回401 Unauthorized

**原因**：
- Agent和Java使用了不同的`JWT_SECRET_KEY`
- JWT token已过期
- Token格式不正确

**解决**：
```bash
# 1. 检查Agent的JWT_SECRET_KEY
grep JWT_SECRET_KEY travel-assistant-agent/.env

# 2. 检查Java的JWT_SECRET_KEY
grep JWT_SECRET_KEY travel-assistant/auth-service/src/main/resources/application.yml

# 3. 确保两者相同
```

### 问题2: Authorization header未转发

**症状**：Java服务日志中看不到Authorization header

**原因**：
- MCP Client未接收到token参数
- routes.py中未传递user_token

**解决**：
```python
# 检查routes.py中是否正确调用
mcp_client = get_mcp_client(
    token=user_token,  # 确保传递了这个参数
    user_id=current_user.id,
    username=current_user.username
)
```

### 问题3: X-User-ID header缺失

**症状**：Java服务无法识别用户ID

**原因**：
- `current_user.id`为None
- MCP Client未设置user_id

**检查**：
```python
# 在routes.py中添加日志
app_logger.info(f"Current user: id={current_user.id}, username={current_user.username}")
```

## 安全最佳实践

1. **Secret Key管理**
   - 使用强随机密钥：`openssl rand -hex 32`
   - 在生产环境中使用环境变量，不要硬编码
   - 定期轮换密钥（配合refresh token机制）

2. **Token过期时间**
   - Access token: 15-30分钟
   - Refresh token: 7天
   - 根据安全需求调整

3. **HTTPS传输**
   - 生产环境必须使用HTTPS
   - 设置`REQUIRE_HTTPS=true`

4. **日志安全**
   - 不要在日志中打印完整的JWT token
   - 只记录token的前几个字符（用于调试）

## 性能优化

1. **连接池**
   - httpx客户端自动使用连接池
   - 配置：`API_CONNECTION_POOL_MAX=100`

2. **缓存**
   - MCP Client内置Redis缓存
   - 缓存TTL: 1小时（可配置）

3. **超时控制**
   - 默认超时：30秒
   - 可配置：`JAVA_API_TIMEOUT=30`

4. **重试机制**
   - 自动重试3次（指数退避）
   - 可配置：`JAVA_API_MAX_RETRIES=3`

## 相关文件

```
travel-assistant-agent/
├── src/
│   ├── agents/
│   │   └── mcp_client.py          # MCP Client (JWT支持)
│   ├── api/
│   │   └── routes.py               # API路由 (JWT转发)
│   ├── utils/
│   │   └── java_client.py          # Java服务客户端
│   └── auth/
│       └── dependencies.py         # JWT验证依赖
├── .env.example                     # 环境配置示例
├── test_jwt_forwarding.sh          # 集成测试脚本
└── JWT_FORWARDING_README.md        # 本文档
```

## 参考资料

- [JWT.io](https://jwt.io/) - JWT标准
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Spring Security JWT](https://spring.io/guides/gs/securing-web/)
- [httpx Documentation](https://www.python-httpx.org/)

## 更新日志

- **2025-01-23**: 初始实现
  - MCP Client支持JWT转发
  - 创建JavaServiceClient工具类
  - 更新所有API路由
  - 添加测试脚本和文档
