# Travel Assistant - Spring Cloud Microservices

旅游助手 MVP 微服务架构项目，基于 Spring Cloud 构建。

## 技术栈

- **Spring Boot 3.2.x**
- **Spring Cloud 2023.x**
- **Spring Cloud Alibaba (Nacos)**
- **Spring Cloud Gateway**
- **PostgreSQL 16**
- **MyBatis-Plus 3.5**
- **JWT Authentication**
- **Docker & Docker Compose**

## 项目结构

```
travel-assistant/
├── pom.xml                          # 父项目 POM
├── docker-compose.yml               # Docker Compose 配置
├── init-scripts/                    # 数据库初始化脚本
│   ├── 00-nacos-init.sql
│   └── 01-init.sql
├── common/                          # 共享模块
│   ├── src/main/java/com/travel/assistant/common/
│   │   ├── config/          # 配置类
│   │   ├── controller/      # 控制器
│   │   ├── dto/             # 数据传输对象
│   │   ├── entity/          # 实体类
│   │   ├── exception/       # 异常处理
│   │   └── utils/           # 工具类
│   └── src/main/resources/
│       └── application.yml
├── gateway/                         # API 网关
│   ├── src/main/java/com/travel/assistant/gateway/
│   │   ├── config/          # 路由配置
│   │   └── filter/          # 网关过滤器
│   └── src/main/resources/
│       └── application.yml
├── auth-service/                    # 认证服务
├── travel-request-service/          # 旅游请求服务
├── travel-plan-service/             # 旅游计划服务
└── order-service/                   # 订单服务
```

## 端口规划

| 服务 | 端口 | 说明 |
|------|------|------|
| Gateway | 8080 | API 网关入口 |
| Auth Service | 8081 | 认证服务 |
| Travel Request Service | 8082 | 旅游请求管理 |
| Travel Plan Service | 8083 | 旅游计划管理 |
| Order Service | 8084 | 订单管理 |
| PostgreSQL | 5432 | 主数据库 |
| Nacos | 8848 | 服务发现和配置中心 |
| Redis | 6379 | 缓存服务 |

## 快速开始

### 1. 环境要求

- JDK 17+
- Maven 3.8+
- Docker & Docker Compose
- PostgreSQL 16 (可选，本地开发)

### 2. 本地开发

#### 方式一：使用 Docker Compose

```bash
# 启动所有服务
cd travel-assistant
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 方式二：本地运行

```bash
# 1. 启动 PostgreSQL
docker run -d --name postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=travel_assistant \
  postgres:16-alpine

# 2. 启动 Nacos
docker run -d --name nacos \
  -p 8848:8848 \
  -e MODE=standalone \
  nacos/nacos-server:v2.3.2

# 3. 构建并运行各服务
cd travel-assistant
mvn clean install -DskipTests

# 依次启动各服务（按依赖顺序）
java -jar gateway/target/gateway-1.0.0-SNAPSHOT.jar
java -jar auth-service/target/auth-service-1.0.0-SNAPSHOT.jar
java -jar travel-request-service/target/travel-request-service-1.0.0-SNAPSHOT.jar
java -jar travel-plan-service/target/travel-plan-service-1.0.0-SNAPSHOT.jar
java -jar order-service/target/order-service-1.0.0-SNAPSHOT.jar
```

### 3. 测试 API

#### 健康检查

```bash
# Gateway 健康检查
curl http://localhost:8080/health

# Auth Service 健康检查
curl http://localhost:8081/health

# Travel Request Service 健康检查
curl http://localhost:8082/health

# Travel Plan Service 健康检查
curl http://localhost:8083/health

# Order Service 健康检查
curl http://localhost:8084/health
```

#### 用户认证

```bash
# 登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 注册
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"password123","confirmPassword":"password123"}'
```

#### 认证后访问其他接口

```bash
# 设置环境变量
TOKEN="your-jwt-token"

# 访问旅游请求接口
curl -X GET http://localhost:8080/api/travel-request/list \
  -H "Authorization: Bearer $TOKEN"
```

## API 文档

启动服务后，可通过以下地址访问 Swagger API 文档：

| 服务 | Swagger UI | OpenAPI JSON |
|------|------------|--------------|
| Gateway | http://localhost:8080/doc.html | http://localhost:8080/v3/api-docs |
| Auth Service | http://localhost:8081/doc.html | http://localhost:8081/v3/api-docs |
| Travel Request | http://localhost:8082/doc.html | http://localhost:8082/v3/api-docs |
| Travel Plan | http://localhost:8083/doc.html | http://localhost:8083/v3/api-docs |
| Order | http://localhost:8084/doc.html | http://localhost:8084/v3/api-docs |

## 配置说明

### Nacos 配置

服务启动后，可以在 Nacos 控制台 (http://localhost:8848/nacos) 中管理配置：

- 用户名：`nacos`
- 密码：`nacos`

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| POSTGRES_HOST | localhost | PostgreSQL 主机 |
| POSTGRES_PORT | 5432 | PostgreSQL 端口 |
| POSTGRES_DB | travel_assistant | 数据库名称 |
| POSTGRES_USERNAME | postgres | 数据库用户名 |
| POSTGRES_PASSWORD | postgres | 数据库密码 |
| NACOS_SERVER_ADDR | localhost:8848 | Nacos 服务器地址 |
| REDIS_HOST | localhost | Redis 主机 |
| REDIS_PORT | 6379 | Redis 端口 |
| JWT_SECRET | (见配置) | JWT 密钥 |
| JWT_EXPIRATION | 86400000 | JWT 过期时间(ms) |

## 目录说明

### common 模块

提供所有微服务共享的组件：

- **BaseEntity**: 基础实体类，包含审计字段
- **Result**: 统一响应封装
- **ResultCode**: 结果状态码枚举
- **PageRequest/PageResponse**: 分页请求/响应
- **JwtUtils**: JWT 工具类
- **LoginUser**: 登录用户信息
- **GlobalExceptionHandler**: 全局异常处理器
- **ResultResponseAdvice**: 统一响应处理
- **HealthController**: 健康检查控制器
- **MybatisPlusConfig**: MyBatis-Plus 配置
- **OpenApiConfig**: Swagger/OpenAPI 配置

### gateway 模块

API 网关服务：

- **GatewayRouteConfig**: 路由配置
- **AuthGatewayFilter**: JWT 认证过滤器
- **CorsConfig**: 跨域配置

### auth-service 模块

认证服务：

- **User**: 用户实体
- **AuthController**: 认证接口控制器
- **AuthService**: 认证业务逻辑

### travel-request-service 模块

旅游请求服务（待实现具体功能）：

- **TravelRequest**: 旅游请求实体

### travel-plan-service 模块

旅游计划服务（待实现具体功能）：

- **TravelPlan**: 旅游计划实体

### order-service 模块

订单服务（待实现具体功能）：

- **Order**: 订单实体

## 后续开发

1. **实现各服务业务逻辑**: 在对应 service 包中实现具体业务
2. **数据库表映射**: 使用 MyBatis-Plus Generator 生成 Mapper
3. **单元测试**: 为核心功能编写测试用例
4. **监控集成**: 添加 Spring Boot Actuator 监控
5. **链路追踪**: 集成 SkyWalking 或 Zipkin

## License

Apache License 2.0
