# Travel Assistant Database

本目录包含 Travel Assistant 项目的数据库初始化脚本和相关文档。

## 目录结构

```
database/
├── schema.sql              # 数据库表结构创建脚本
├── init-sample-data.sql   # 示例数据 (可选)
└── README.md              # 本文档
```

## 快速开始

### 1. 创建数据库

```sql
-- 创建数据库
CREATE DATABASE travel_assistant;

-- 连接到数据库
\c travel_assistant;
```

### 2. 运行初始化脚本

```bash
# 方法1: 使用 psql 命令行
psql -U postgres -d travel_assistant -f database/schema.sql

# 方法2: 在 psql 客户端中执行
\i database/schema.sql

# 方法3: 使用 docker exec (如果使用 Docker)
docker exec -it travel_assistant-db psql -U postgres -d travel_assistant -f /docker-entrypoint-initdb.d/schema.sql
```

### 3. 验证表结构

```sql
-- 查看所有表
\dt

-- 查看表结构
\d users
\d hotels
\d flights
\d attractions

-- 查看索引
\di
```

## 表结构说明

### 1. 用户表 (users)

存储用户基础信息和偏好设置。

**核心字段:**
- `id`: UUID 主键
- `email`: 邮箱 (唯一，大小写不敏感)
- `username`: 用户名 (唯一)
- `password_hash`: 密码哈希
- `full_name`: 全名
- `preferences_json`: 用户偏好 (JSON格式)
- `travel_style`: 旅游风格 (relaxed, adventure, cultural)
- `budget_level`: 预算等级 (luxury, mid, budget)

**常用查询场景:**
- 用户登录验证
- 用户信息查询
- 基于偏好推荐

**索引优化:**
- 邮箱、用户名唯一索引
- 旅游风格、预算等级查询索引

### 2. 酒店表 (hotels)

存储酒店基础信息和价格库存。

**核心字段:**
- `id`: UUID 主键
- `name`: 酒店名称
- `destination`: 目的地
- `price`: 价格 (每晚)
- `rating`: 评分 (0-5)
- `description`: 酒店描述
- `facilities`: 设施列表 (JSON数组)
- `check_in_time`: 入住时间
- `check_out_time`: 退房时间

**常用查询场景:**
- 按目的地搜索酒店
- 按价格和评分筛选
- 酒店详情查询

**索引优化:**
- 目的地 + 价格复合索引
- 目的地 + 评分复合索引

### 3. 航班表 (flights)

存储航班信息和价格库存。

**核心字段:**
- `id`: UUID 主键
- `origin`: 出发地
- `destination`: 目的地
- `departure_date`: 出发日期
- `return_date`: 返回日期 (单程为NULL)
- `departure_time`: 出发时间
- `arrival_time`: 到达时间
- `price`: 价格
- `airline`: 航空公司
- `flight_number`: 航班号
- `duration_minutes`: 飞行时长
- `available_seats`: 可用座位数

**常用查询场景:**
- 按路线搜索航班
- 按日期筛选
- 价格比较

**索引优化:**
- 路线 + 日期复合索引
- 出发地 + 目的地组合索引

### 4. 景点表 (attractions)

存储旅游景点信息。

**核心字段:**
- `id`: UUID 主键
- `destination`: 目的地
- `name`: 景点名称
- `category`: 分类 (museum, park, historic, food, entertainment等)
- `rating`: 评分 (0-5)
- `description`: 景点描述
- `opening_hours`: 营业时间
- `ticket_price`: 门票价格
- `latitude`: 纬度
- `longitude`: 经度
- `phone`: 电话
- `website`: 网站

**常用查询场景:**
- 按目的地和分类查询景点
- 地理位置附近搜索
- 评分排序

**索引优化:**
- 目的地 + 分类复合索引
- 目的地 + 评分复合索引

### 5. RAG 知识库表 (rag_documents) - 可选

存储AI助手的知识库文档和向量数据。

**核心字段:**
- `id`: UUID 主键
- `entity_type`: 实体类型 (hotel, attraction, flight, guide)
- `entity_id`: 关联的实体ID
- `content`: 文档内容
- `embedding`: 向量嵌入 (384维)
- `source`: 来源 (review, wiki, user_guide, official)
- `metadata`: 额外元数据

**用途:**
- AI助手知识库
- 向量搜索
- 智能推荐

**依赖:**
- 需要 `pgvector` 扩展支持向量操作

### 6. 审计日志表 (audit_logs) - 可选

记录系统操作日志，用于审计和分析。

**核心字段:**
- `id`: UUID 主键
- `user_id`: 用户ID
- `action`: 操作类型 (search, book, recommend, login等)
- `resource_type`: 资源类型
- `resource_id`: 资源ID
- `details`: 操作详情 (JSON格式)
- `ip_address`: IP地址
- `user_agent`: 用户代理

**用途:**
- 用户行为分析
- 系统安全审计
- 业务数据分析

## 索引策略

### 1. 单列索引
- 所有主键字段
- 常用查询字段 (email, username, destination等)

### 2. 复合索引
- `users`: 常用查询组合
- `hotels`: (destination, price), (destination, rating)
- `flights`: (origin, destination), (origin, destination, departure_date)
- `attractions`: (destination, category), (destination, rating)

### 3. 特殊索引
- 向量索引: `rag_documents.embedding` 使用 IVFFlat 索引
- 全文搜索准备: 可基于 content 字段创建全文搜索索引

## 数据类型说明

### 1. 主键类型
- `UUID`: 使用 `uuid-ossp` 扩展生成，避免ID泄露

### 2. 精确数值
- `DECIMAL(10,2)`: 价格字段，确保精度
- `DECIMAL(3,1)`: 评分字段，范围0-5

### 3. 时间处理
- `TIMESTAMP WITH TIME ZONE`: 统一时区处理
- `DATE`: 日期字段
- `TIME`: 时间字段

### 4. 灵活数据
- `JSONB`: 偏好设置、元数据等灵活字段
- `VECTOR`: 向量数据 (需要pgvector扩展)

## 安全考虑

### 1. 密码安全
- 只存储密码哈希值
- 使用 `bcrypt` 或类似算法

### 2. 数据完整性
- 邮箱、用户名唯一性约束
- 评分字段范围检查约束

### 3. 审计跟踪
- 所有表都有 created_at, updated_at 字段
- 自动触发器更新 updated_at
- 详细的审计日志记录

## 性能优化

### 1. 索引优化
- 基于查询模式设计索引
- 避免过度索引影响写入性能

### 2. 分区准备
- 大数据量场景可按日期分区
- `audit_logs` 适合按月分区

### 3. 连接池配置
- 建议配置合适的连接池大小
- 监控慢查询并优化

## 扩展功能

### 1. 分区表 (大数据量场景)
```sql
-- 按月分区审计日志
CREATE TABLE audit_logs_2025_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### 2. 全文搜索
```sql
-- 为景点描述添加全文搜索
CREATE INDEX idx_attractions_description_fts ON attractions 
    USING gin(to_tsvector('english', description));
```

### 3. 向量搜索 (需要pgvector)
```sql
-- 相似度搜索
SELECT entity_id, content 
FROM rag_documents 
WHERE embedding <-> '[0.1,0.2,0.3]' < 0.5 
ORDER BY embedding <-> '[0.1,0.2,0.3]' 
LIMIT 10;
```

## 维护脚本

### 1. 清理旧数据
```sql
-- 清理90天前的审计日志
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days';
```

### 2. 更新统计信息
```sql
-- 更新表统计信息
ANALYZE users, hotels, flights, attractions;
```

### 3. 重建索引
```sql
-- 重建所有索引
REINDEX DATABASE travel_assistant;
```

## Docker 部署

如果使用 Docker Compose，可以将初始化脚本挂载到 PostgreSQL 容器中：

```yaml
# docker-compose.yml 片段
services:
  postgres:
    environment:
      POSTGRES_DB: travel_assistant
    volumes:
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5433:5432"
```

## 版本历史

- **v1.0.0** (2025-01-20): 初始版本，包含核心表结构和索引

## 注意事项

1. **扩展依赖**: RAG功能需要安装 `pgvector` 扩展
2. **性能监控**: 建议监控慢查询和索引使用情况
3. **数据备份**: 定期备份重要数据
4. **安全更新**: 定期更新密码哈希算法
5. **扩展性**: JSON字段提供了良好的扩展性，但需要注意查询性能

## 支持和反馈

如有问题或建议，请联系开发团队或提交 Issue。