# JWT Token Forwarding - Quick Start Guide

## 概述

实现了Agent调用Java微服务时的JWT token转发，确保完整的认证链路。

## 关键修改

### 1. MCP Client (`travel-assistant-agent/src/agents/mcp_client.py`)
- 支持接收JWT token、user_id、username参数
- 自动在HTTP请求中添加Authorization header和用户上下文headers

### 2. Java客户端工具 (`travel-assistant-agent/src/utils/java_client.py`)
- 新增高级封装类，提供重试、超时、统一错误处理
- 专用方法：search_flights(), search_hotels(), create_booking()等

### 3. API路由 (`travel-assistant-agent/src/api/routes.py`)
- 修改search、recommend、book端点
- 在调用MCP Client时传递JWT token和用户信息

## 配置要求

**⚠️ 关键：JWT_SECRET_KEY必须在Agent和Java服务中保持一致！**

```bash
# .env文件中
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JAVA_API_BASE_URL=http://localhost:8080/api
```

## 快速测试

```bash
# 1. 启动服务
cd travel-assistant
docker-compose up -d

cd ../travel-assistant-agent
python -m uvicorn src.main:app --reload

# 2. 运行测试脚本
cd travel-assistant-agent
./test_jwt_forwarding.sh
```

## 验证JWT转发

检查Agent日志：
```bash
tail -f travel-assistant-agent/logs/app.log | grep -i "jwt\|authorization"
```

应该看到：
```
Added Authorization header with token
MCP tool called successfully with JWT auth
```

检查Java服务日志：
```bash
docker logs travel-assistant-gateway | grep -i "authorization"
```

## HTTP Headers格式

转发到Java服务的Headers：
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-User-ID: <user_id>
X-Username: <username>
```

## 文档

- **详细文档**: `travel-assistant-agent/JWT_FORWARDING_README.md`
- **实现总结**: `JWT_FORWARDING_IMPLEMENTATION_SUMMARY.md`
- **测试脚本**: `travel-assistant-agent/test_jwt_forwarding.sh`

## 文件清单

**新增文件**:
- `travel-assistant-agent/src/utils/java_client.py` - Java服务客户端
- `travel-assistant-agent/test_jwt_forwarding.sh` - 测试脚本
- `travel-assistant-agent/JWT_FORWARDING_README.md` - 详细文档
- `JWT_FORWARDING_IMPLEMENTATION_SUMMARY.md` - 实现总结

**修改文件**:
- `travel-assistant-agent/src/agents/mcp_client.py` - MCP Client增强
- `travel-assistant-agent/src/api/routes.py` - API路由修改
- `.env.example` - 配置更新
- `travel-assistant-agent/.env.example` - Agent配置更新

## 故障排查

### JWT验证失败 (401)
- 检查JWT_SECRET_KEY是否在Agent和Java中一致
- 检查token是否过期

### Authorization header未转发
- 确认routes.py中传递了user_token参数
- 检查MCP Client是否接收到token

### 更多问题
查看详细文档：`travel-assistant-agent/JWT_FORWARDING_README.md`
