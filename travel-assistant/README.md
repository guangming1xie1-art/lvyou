# Travel Assistant - Spring Cloud 微服务基础架构（MVP）

本目录用于承载旅游助手后端 **Spring Cloud 微服务** 的基础框架（与根目录的前端/agent 子项目相互独立）。

## 目录结构

```
travel-assistant/
├── pom.xml                   # Maven 父项目（多模块）
├── common/                   # 共享模块（响应体、JWT 工具、通用实体等）
├── gateway/                  # Spring Cloud Gateway（API 网关）
├── auth-service/             # 认证服务（MVP：提供 login 生成 JWT）
├── travel-request-service/   # 行程需求服务（占位服务）
├── travel-plan-service/      # 行程规划服务（占位服务）
├── order-service/            # 订单服务（占位服务）
└── docker-compose.yml        # Nacos + PostgreSQL + 各微服务编排
```

## 技术栈

- Spring Boot 3.x
- Spring Cloud 2023.x
- Spring Cloud Alibaba Nacos（服务发现 + 配置中心）
- Spring Cloud Gateway
- PostgreSQL
- Maven（多模块构建）

## 本地启动（Docker Compose 推荐）

在仓库根目录执行：

```bash
cd travel-assistant
docker compose up --build
```

启动后：

- Nacos 控制台：http://localhost:8848/nacos （默认账号/密码：nacos/nacos）
- 网关：http://localhost:8080
- Auth Service：http://localhost:8081
- Travel Request Service：http://localhost:8082
- Travel Plan Service：http://localhost:8083
- Order Service：http://localhost:8084

> Compose 中 PostgreSQL 映射到宿主机端口 **5433**（避免与其他子项目冲突）。

## 本地启动（不使用 Docker）

确保本机已启动：

- PostgreSQL：`jdbc:postgresql://localhost:5432/travel_assistant`
- Nacos：`localhost:8848`

然后分别启动服务（示例：Auth Service）：

```bash
cd travel-assistant
mvn -pl auth-service -am spring-boot:run
```

## 网关路由

网关在 `gateway/src/main/resources/application.yml` 中配置了基础路由：

- `/api/auth/**` → `lb://auth-service`
- `/api/requests/**` → `lb://travel-request-service`
- `/api/plans/**` → `lb://travel-plan-service`
- `/api/orders/**` → `lb://order-service`

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

## JWT 工具

- `common` 模块提供 `JwtUtil`（JJWT/HS256）
- `auth-service` 提供 `/api/auth/login` 接口生成 JWT（MVP 阶段不接入用户表）

配置项：

- `app.jwt.secret`（至少 32 字节）
- `app.jwt.ttl`（如 `12h`）

## 健康检查

每个服务都提供：

- `GET /health`：自定义健康检查（MVP）
- `GET /actuator/health`：Spring Boot Actuator 健康检查（需在 `management.endpoints.web.exposure` 中暴露）

## 说明与下一步

当前为 **微服务骨架**：

- 服务均已接入 Nacos（服务发现 + 可选配置中心 import）
- 服务均配置 PostgreSQL 数据源（`spring-boot-starter-data-jpa`），可用于后续落库
- 业务领域的实体、Repository、鉴权过滤器、网关鉴权/限流等将在后续迭代中补齐
