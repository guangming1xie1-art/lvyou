# Gateway MCP 改造文档

## 概述

将 Gateway 从自定义 REST API 改造为标准 Spring AI MCP Server，实现与 Python MultiServerMCPClient 的标准 MCP 协议兼容。

## 架构变化

### 改造前
```
Python MCP Client (MultiServerMCPClient)
    ↓ (期望标准 MCP Protocol)
Gateway (自定义 REST API /mcp/*)
    ↓ (HTTP/REST)
Microservices
```

### 改造后
```
Python MCP Client (MultiServerMCPClient)
    ↓ (标准 MCP Protocol)
Gateway (Spring AI MCP Server)
    ↓ (HTTP/WebClient 负载均衡)
Microservices
```

## 修改文件列表

### 1. Parent POM 配置 (`travel-assistant/pom.xml`)
- 添加 `spring-ai.version` 属性 (1.0.0-M6)
- 添加 Spring AI BOM 依赖管理
- 添加 Spring Milestones 仓库

### 2. Gateway POM 配置 (`travel-assistant/gateway/pom.xml`)
- 添加 `spring-ai-mcp-server-spring-boot-starter` 依赖

### 3. MCP Server 配置 (`travel-assistant/gateway/src/main/resources/application.yml`)
- 添加 Spring AI MCP Server 配置：
```yaml
spring:
  ai:
    mcp:
      server:
        enabled: true
        name: travel-gateway-mcp
        version: 1.0.0
```

### 4. TravelMcpTools 类 (`travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/tools/TravelMcpTools.java`)
新创建的类，实现8个标准 MCP 工具：

#### 酒店工具
- `search_hotels` - 搜索酒店
- `get_hotel_details` - 获取酒店详情

#### 航班工具
- `search_flights` - 搜索航班
- `get_flight_details` - 获取航班详情

#### 景点工具
- `search_attractions` - 搜索景点
- `get_attraction_details` - 获取景点详情

#### 预订工具
- `create_booking` - 创建预订
- `get_booking_status` - 获取预订状态

#### 推荐工具
- `get_recommendations` - 获取个性化推荐

所有工具使用：
- `@Tool` 注解定义工具名称和描述
- `@ToolParam` 注解定义参数
- WebClient 负载均衡调用下游服务 (`lb://service-name`)

### 5. JWT 认证过滤器 (`travel-assistant/gateway/src/main/java/com/travelassistant/gateway/filter/JwtAuthenticationFilter.java`)
- 添加 Spring AI MCP Server 标准端点到公开路由列表：
  - `/mcp` - MCP 根路径
  - `/mcp/initialize` - 初始化端点
  - `/mcp/tools/list` - 工具列表端点
  - `/mcp/tools/call` - 工具调用端点

### 6. MCPController 废弃标记 (`travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPController.java`)
- 添加 `@Deprecated` 注解到类和方法
- 更新日志消息，提示使用标准 MCP 端点
- 更新健康检查端点，指示新架构状态

## 标准 MCP 端点

Spring AI MCP Server 自动提供以下标准端点：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/mcp` | GET/POST | MCP 协议入口 |
| `/mcp/initialize` | POST | MCP 初始化 |
| `/mcp/tools/list` | GET | 获取工具列表 |
| `/mcp/tools/call` | POST | 调用工具 |

## 向后兼容性

旧的 REST API 端点仍然可用（已标记为废弃）：
- `GET /mcp/tools` → 请使用 `GET /mcp/tools/list`
- `GET /mcp/tools/{toolName}` → 请使用标准 MCP 协议
- `POST /mcp/tools/{toolName}/call` → 请使用 `POST /mcp/tools/call`
- `POST /mcp/initialize` → 请使用 `POST /mcp/initialize` (标准协议)

## Python Agent 集成

Python Agent 使用 `MultiServerMCPClient` 连接 Gateway：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

connections = {
    "java_api": {
        "url": "http://localhost:9000/mcp",
        "transport": "http"
    }
}

client = MultiServerMCPClient(connections=connections)
tools = await client.get_tools()
```

## 负载均衡

所有工具通过 WebClient 使用 Spring Cloud LoadBalancer：
- 服务地址格式: `lb://service-name`
- 支持 Nacos 服务发现
- 自动负载均衡到可用实例

## 依赖关系

```
spring-ai-mcp-server-spring-boot-starter (1.0.0-M6)
    ↓
spring-boot-starter-webflux (reactive)
    ↓
WebClient + LoadBalancer
    ↓
Microservices (hotel/flight/attraction/booking/recommendation)
```

## 验证清单

- [x] Gateway POM 添加 Spring AI MCP Server 依赖
- [x] Parent POM 添加 Spring AI BOM 和仓库
- [x] application.yml 添加 MCP Server 配置
- [x] TravelMcpTools 实现8个工具
- [x] 所有工具使用 @Tool 和 @ToolParam 注解
- [x] WebClient 使用负载均衡 (lb://)
- [x] MCPController 添加废弃标记
- [x] JwtAuthenticationFilter 添加新端点到公开路由
- [x] 旧端点保留用于向后兼容

## 后续建议

1. 在 Python Agent 中测试标准 MCP 协议连接
2. 验证所有工具调用正常工作
3. 监控日志确保负载均衡正常
4. 逐步迁移旧客户端到标准协议
5. 未来版本可考虑移除废弃的 REST API
