# Memory Service - 记忆系统微服务

## 概述

Memory Service 是旅游助手系统的记忆管理微服务，负责存储和管理四层记忆系统的数据。

**服务信息：**
- 服务名称：memory-service
- 端口：8088
- 基础路径：/api/memory
- 技术栈：Spring Boot 3.2 + PostgreSQL + JPA

## 功能特性

### 1. 会话管理
- 创建、查询、更新、删除会话
- 会话归档和过期管理
- 会话统计和重置

### 2. 消息管理
- 保存和查询对话消息
- 支持分页查询
- 消息类型和元数据支持

### 3. 用户偏好管理
- 保存和查询用户偏好
- 偏好类型分类（目的地、预算、酒店等级等）
- 置信度管理和更新

### 4. 任务案例管理
- 保存历史任务案例
- 案例检索和查询
- 满意度和反馈记录

### 5. 向量记忆管理
- 保存向量记忆元数据
- 向量检索接口
- 偏好提取功能

## 项目结构

```
memory-service/
├── src/main/java/com/travelassistant/memory/
│   ├── controller/          # 控制器层
│   │   └── MemoryController.java
│   ├── service/            # 服务层
│   │   ├── ConversationService.java
│   │   ├── MessageService.java
│   │   ├── PreferenceService.java
│   │   ├── TaskCaseService.java
│   │   └── VectorMemoryService.java
│   ├── repository/         # 数据访问层
│   │   ├── ConversationRepository.java
│   │   ├── ConversationMessageRepository.java
│   │   ├── UserPreferenceRepository.java
│   │   ├── TaskCaseRepository.java
│   │   └── VectorMemoryRepository.java
│   ├── entity/             # 实体类
│   │   ├── Conversation.java
│   │   ├── ConversationMessage.java
│   │   ├── UserPreference.java
│   │   ├── TaskCase.java
│   │   └── VectorMemory.java
│   ├── dto/                # 数据传输对象
│   │   ├── RequestDTOs.java
│   │   ├── ResponseDTOs.java
│   │   └── InternalDTOs.java
│   └── MemoryServiceApplication.java
├── src/main/resources/
│   └── application.yml     # 配置文件
├── k8s/                     # Kubernetes部署文件
│   └── memory-service.yaml
├── Dockerfile              # Docker镜像构建文件
└── pom.xml                 # Maven配置文件
```

## 快速开始

### 前置要求

- Java 17+
- Maven 3.8+
- PostgreSQL 12+
- （可选）Docker

### 数据库配置

1. 创建数据库：
```sql
CREATE DATABASE travel_assistant;
```

2. 执行建表脚本：
```bash
psql -U postgres -d travel_assistant -f database/schema_memory.sql
```

### 本地运行

1. 修改配置文件 `src/main/resources/application.yml`：
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/travel_assistant
    username: postgres
    password: your_password
```

2. 编译和运行：
```bash
mvn clean install
mvn spring-boot:run
```

3. 访问服务：
```
http://localhost:8088/api/memory
```

### Docker运行

1. 构建镜像：
```bash
docker build -t memory-service:1.0.0 .
```

2. 运行容器：
```bash
docker run -p 8088:8088 \
  -e DB_PASSWORD=your_password \
  memory-service:1.0.0
```

### Kubernetes部署

1. 创建命名空间：
```bash
kubectl create namespace travel-assistant
```

2. 部署服务：
```bash
kubectl apply -f k8s/memory-service.yaml
```

3. 查看状态：
```bash
kubectl get pods -n travel-assistant
kubectl get svc -n travel-assistant
```

## API文档

详细的API文档请参考：[JAVA_MEMORY_SERVICE_API.md](../JAVA_MEMORY_SERVICE_API.md)

### 主要API端点

#### 会话管理
- `POST /api/memory/conversations` - 创建会话
- `GET /api/memory/conversations/{sessionId}` - 获取会话详情
- `GET /api/memory/conversations/user/{userId}` - 获取用户会话列表
- `POST /api/memory/conversations/{sessionId}/summary` - 更新会话摘要
- `POST /api/memory/conversations/{sessionId}/archive` - 归档会话
- `DELETE /api/memory/conversations/{sessionId}` - 删除会话

#### 消息管理
- `POST /api/memory/messages` - 保存消息
- `GET /api/memory/sessions/{sessionId}/messages` - 获取消息列表

#### 用户偏好管理
- `POST /api/memory/preferences` - 保存偏好
- `GET /api/memory/preferences` - 获取用户偏好
- `PUT /api/memory/preferences/{preferenceId}` - 更新偏好
- `DELETE /api/memory/preferences/{preferenceId}` - 删除偏好

#### 任务案例管理
- `POST /api/memory/task-cases` - 保存任务案例
- `GET /api/memory/task-cases` - 获取任务案例

#### 向量记忆管理
- `POST /api/memory/memories` - 保存向量记忆
- `POST /api/memory/memories/search` - 检索向量记忆
- `POST /api/memory/memories/extract-preferences` - 提取偏好

#### 会话统计
- `GET /api/memory/sessions/{sessionId}/stats` - 获取会话统计
- `POST /api/memory/sessions/{sessionId}/reset` - 重置会话

## 配置说明

### 数据库配置
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/travel_assistant
    username: postgres
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 10
```

### 向量数据库配置
```yaml
vector:
  db:
    type: faiss  # faiss or milvus
    host: localhost
    port: 19530
    index-path: ./data/vector_index
```

### 日志配置
```yaml
logging:
  level:
    root: INFO
    com.travelassistant.memory: DEBUG
  file:
    name: logs/memory-service.log
```

## 监控和健康检查

服务提供了以下监控端点：

- `/actuator/health` - 健康检查
- `/actuator/info` - 服务信息
- `/actuator/metrics` - 性能指标

## 性能优化

### 数据库优化
- 使用HikariCP连接池
- 配置JPA批处理
- 创建必要的索引

### 缓存优化
- 支持Redis缓存（可选）
- 会话数据缓存
- 偏好数据缓存

### 向量检索优化
- 支持FAISS本地索引
- 支持Milvus分布式向量库
- 复合检索（向量+BM25）

## 测试

### 单元测试
```bash
mvn test
```

### 集成测试
```bash
mvn verify
```

## 故障排查

### 常见问题

1. **数据库连接失败**
   - 检查数据库URL、用户名、密码
   - 确认数据库服务是否运行
   - 检查网络连接

2. **端口被占用**
   - 修改 `server.port` 配置
   - 检查端口占用情况

3. **内存不足**
   - 调整JVM参数：`-Xmx2g -Xms1g`
   - 优化数据库连接池配置

## 版本历史

- **v1.0.0** (2025-01-01)
  - 初始版本
  - 实现基本的会话管理
  - 实现用户偏好管理
  - 实现任务案例管理
  - 实现向量记忆管理

## 联系方式

如有问题，请联系开发团队或提交Issue。
