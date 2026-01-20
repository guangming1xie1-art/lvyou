# Travel Assistant - Spring Cloud 微服务架构

本目录用于承载旅游助手后端 **Spring Cloud 微服务** 的完整架构（与根目录的前端/agent 子项目相互独立）。

## 目录结构

```
travel-assistant/
├── pom.xml                   # Maven 父项目（多模块）
├── common/                   # 共享模块（响应体、DTO、JWT 工具、转换器等）
├── gateway/                  # Spring Cloud Gateway（API 网关）
├── auth-service/             # 认证服务（提供 JWT 生成和验证）
├── user-service/            # 用户管理服务
├── hotel-service/           # 酒店搜索服务
├── flight-service/          # 航班搜索服务
├── attraction-service/      # 景点推荐服务
├── booking-service/         # 预订服务
├── recommendation-service/  # 智能推荐服务
└── docker-compose.yml       # Nacos + PostgreSQL + 各微服务编排
```

## 微服务架构

系统采用标准的微服务架构，包含以下核心服务：

- **gateway** - API 网关 (端口: 8080)
- **auth-service** - 认证服务 (8081)
- **user-service** - 用户管理服务 (8082)
- **hotel-service** - 酒店搜索服务 (8083)
- **flight-service** - 航班搜索服务 (8084)
- **attraction-service** - 景点推荐服务 (8085)
- **booking-service** - 预订服务 (8086)
- **recommendation-service** - 智能推荐服务 (8087)

所有服务通过 Nacos 进行服务注册与发现，支持动态配置管理。

## 技术栈

- Spring Boot 3.2.5
- Spring Cloud 2023.0.2
- Spring Cloud Alibaba Nacos 2023.0.1.0（服务发现 + 配置中心）
- Spring Cloud Gateway
- PostgreSQL 15+
- Maven（多模块构建）
- JWT 认证
- OpenAPI/Swagger（API 文档）

## 本地启动（Docker Compose 推荐）

在仓库根目录执行：

```bash
cd travel-assistant
docker compose up --build
```

启动后：

- Nacos 控制台：http://localhost:8848/nacos （默认账号/密码：nacos/nacos）
- API 网关：http://localhost:8080
- 各微服务通过网关统一访问
- Swagger UI 文档：http://localhost:8080/swagger-ui.html （需通过网关路由）

> Compose 中 PostgreSQL 映射到宿主机端口 **5433**（避免与其他子项目冲突）。

## 本地启动（不使用 Docker）

确保本机已启动：

- PostgreSQL：`jdbc:postgresql://localhost:5432/travel_assistant`
- Nacos：`localhost:8848`

然后分别启动服务（示例：Gateway）：

```bash
cd travel-assistant
mvn -pl gateway -am spring-boot:run
```

按依赖顺序依次启动：gateway → 其他微服务

## 网关路由

网关在 `gateway/src/main/resources/application.yml` 中配置了基础路由：

- `/api/auth/**` → `lb://auth-service`
- `/api/users/**` → `lb://user-service`
- `/api/hotels/**` → `lb://hotel-service`
- `/api/flights/**` → `lb://flight-service`
- `/api/attractions/**` → `lb://attraction-service`
- `/api/bookings/**` → `lb://booking-service`
- `/api/recommendations/**` → `lb://recommendation-service`

并开启了 discovery locator：

- `/{serviceId}/**` 可直接路由到 Nacos 中注册的服务（serviceId 小写）。

## API 响应格式标准化

`common` 模块提供统一响应体：

```json
{
  "code": 0,
  "message": "OK",
  "data": {},
  "timestamp": "2025-01-01T00:00:00Z"
}
```

各服务通过 `ApiResponse.success(...) / ApiResponse.error(...)` 返回。

## JWT 认证

- `common` 模块提供 `JwtUtil`（JJWT/HS256）
- `auth-service` 提供 `/api/auth/login` 接口生成 JWT
- `gateway` 提供统一鉴权过滤器

配置项：

- `app.jwt.secret`（至少 32 字节）
- `app.jwt.ttl`（如 `24h`）

## 健康检查

每个服务都提供：

- `GET /health`：自定义健康检查
- `GET /actuator/health`：Spring Boot Actuator 健康检查
- `GET /actuator/info`：服务信息

## 数据库设计

采用 PostgreSQL，每个微服务拥有独立的数据库模式：

- **user-service**：用户表、用户偏好表
- **hotel-service**：酒店信息表
- **flight-service**：航班信息表
- **attraction-service**：景点信息表
- **booking-service**：预订记录表
- **recommendation-service**：推荐缓存表

支持 JSONB 类型存储复杂数据结构。

## 文档

- **项目总体文档**：参见根目录 `README.md`
- **API 规范**：[OPENSPEC_WORKFLOW.md](../OPENSPEC_WORKFLOW.md)
- **部署指南**：[DEPLOYMENT.md](../DEPLOYMENT.md)
- **Docker 实现总结**：[DOCKER_IMPLEMENTATION_SUMMARY.md](../DOCKER_IMPLEMENTATION_SUMMARY.md)

## 说明

当前已实现完整的微服务架构，包含：

- 服务注册与发现（Nacos）
- API 网关统一入口
- JWT 统一认证
- 标准化的 API 响应格式
- 各微服务独立数据库模式
- OpenAPI 文档自动生成
- 健康检查和监控

业务功能已实现用户管理、酒店搜索、航班搜索、景点推荐、预订、智能推荐等核心功能。
