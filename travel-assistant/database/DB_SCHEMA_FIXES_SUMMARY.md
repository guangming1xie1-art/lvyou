# 数据库 Schema 和示例数据修复总结

**修复日期**: 2025-01-23
**目的**: 修复 travel-assistant/database 目录下 schema.sql 和 init-sample-data.sql 的字段不同步问题，与 Java 实体类设计保持一致。

**数据库**: PostgreSQL 15
**注意**: 本修复使用 PostgreSQL 特定语法（BIGSERIAL, gen_random_uuid(), 触发器等）

---

## 修复概述

本次修复主要解决了以下问题：
1. **users 表**字段不完整，缺少认证相关字段
2. **hotels 表**字段命名不一致（时间字段类型）
3. **flights 表**存在多余字段且字段命名不一致
4. **attractions 表**存在多余字段，缺少核心 tags 字段
5. **缺少 rag_documents 和 audit_logs 表定义**
6. **ID 类型不一致**: users 表使用 BIGSERIAL 而非 UUID
7. **触发器机制**: 使用 PostgreSQL 触发器自动更新 updated_at

---

## 修复详情

### 1. schema.sql 修改

#### 1.1 users 表

| 字段 | 修改内容 | 原因 |
|------|---------|------|
| `id` | 从 `UUID` 改为 `BIGSERIAL` | 匹配 auth-service User.java 实体（PostgreSQL 自增语法） |
| `password_hash` | 新增 `VARCHAR(255) NOT NULL` | 用户密码哈希，来自 User.java |
| `is_active` | 新增 `BOOLEAN DEFAULT TRUE` | 用户活跃状态，来自 User.java |
| `last_login` | 新增 `TIMESTAMP NULL` | 最后登录时间，来自 User.java |
| `preferences_json` | 保留 `JSONB NOT NULL DEFAULT '{}'::jsonb` | 用户偏好，用于个性化推荐 |
| `created_by` | 移除 | User.java 中无此字段 |
| `updated_by` | 移除 | User.java 中无此字段 |
| `updated_at` | 保持触发器更新机制 | 使用 PostgreSQL 触发器自动更新 |

#### 1.2 hotels 表

| 字段 | 修改内容 | 原因 |
|------|---------|------|
| `check_in_time` | 不存在（已移除） | Hotel.java 中无此字段，应使用 check_in_date |
| `check_out_time` | 不存在（已移除） | Hotel.java 中无此字段，应使用 check_out_date |
| `check_in_date` | 保留 `DATE` | 日期类型，来自 Hotel.java |
| `check_out_date` | 保留 `DATE` | 日期类型，来自 Hotel.java |
| `created_by` | 移除 | BaseEntity 中未使用 |
| `updated_by` | 移除 | BaseEntity 中未使用 |
| `updated_at` | 保持触发器更新机制 | 使用 PostgreSQL 触发器自动更新 |

#### 1.3 flights 表

| 字段 | 修改内容 | 原因 |
|------|---------|------|
| `departure_time` | 移除 | Flight.java 中无此字段 |
| `arrival_time` | 移除 | Flight.java 中无此字段 |
| `flight_number` | 移除 | Flight.java 中无此字段 |
| `available_seats` | 移除 | Flight.java 中无此字段 |
| `duration_minutes` | 改为 `duration` | Flight.java 中字段名为 duration |
| `duration` | 保留 `INTEGER` | 飞行时长（分钟），来自 Flight.java |
| `created_by` | 移除 | BaseEntity 中未使用 |
| `updated_by` | 移除 | BaseEntity 中未使用 |
| `updated_at` | 保持触发器更新机制 | 使用 PostgreSQL 触发器自动更新 |

#### 1.4 attractions 表

| 字段 | 修改内容 | 原因 |
|------|---------|------|
| `ticket_price` | 移除 | Attraction.java 中无此字段 |
| `latitude` | 移除 | Attraction.java 中无此字段 |
| `longitude` | 移除 | Attraction.java 中无此字段 |
| `phone` | 移除 | Attraction.java 中无此字段 |
| `website` | 移除 | Attraction.java 中无此字段 |
| `tags` | 保留 `JSONB NOT NULL DEFAULT '[]'::jsonb` | 核心字段，来自 Attraction.java |
| `created_by` | 移除 | BaseEntity 中未使用 |
| `updated_by` | 移除 | BaseEntity 中未使用 |
| `updated_at` | 保持触发器更新机制 | 使用 PostgreSQL 触发器自动更新 |

#### 1.5 新增表

| 表名 | 说明 | 主要字段 |
|------|------|---------|
| `rag_documents` | RAG 文档表 | id (UUID), entity_type, entity_id, content, source, metadata, created_at, updated_at |
| `audit_logs` | 审计日志表 | id (BIGSERIAL), user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at |

#### 1.6 触发器修改

| 修改内容 | 原因 |
|---------|------|
| 为所有表添加触发器自动更新 updated_at | PostgreSQL 需要触发器来实现自动更新 timestamp 字段 |
| 新增 rag_documents 表的触发器 | 新增表需要触发器支持 |

---

### 2. init-sample-data.sql 修改

#### 2.1 users 表数据

| 修改内容 | 详情 |
|---------|------|
| 移除 `full_name` 字段 | schema.sql 中不存在 |
| 移除 `travel_style` 字段 | schema.sql 中不存在，合并到 preferences_json |
| 移除 `budget_level` 字段 | schema.sql 中不存在，合并到 preferences_json |
| 添加 `password_hash` | 所有用户使用相同的哈希值 `$2a$10$rOzK4Z8kB7mV5jA.xxXxAu` |
| 添加 `is_active` | 所有用户设置为 `TRUE` |
| 添加 `last_login` | 所有用户设置为 `NULL` |
| 更新 `preferences_json` | 将 travel_style 和 budget_level 合并到 JSON 中 |

**示例数据更新**:
```sql
-- 修复前
INSERT INTO users (email, username, password_hash, full_name, preferences_json, travel_style, budget_level) VALUES
('john.doe@example.com', 'john_doe', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', 'John Doe',
 '{"preferred_airlines": ["China Eastern", "Air China"], "meal_preference": "vegetarian"}',
 'cultural', 'mid');

-- 修复后
INSERT INTO users (email, username, password_hash, is_active, last_login, preferences_json) VALUES
('john.doe@example.com', 'john_doe', '$2a$10$rOzK4Z8kB7mV5jA.xxXxAu', TRUE, NULL,
 '{"preferred_airlines": ["China Eastern", "Air China"], "meal_preference": "vegetarian",
   "travel_style": "cultural", "budget_level": "mid"}');
```

#### 2.2 hotels 表数据

| 修改内容 | 详情 |
|---------|------|
| 移除 `check_in_time` | schema.sql 中不存在 |
| 移除 `check_out_time` | schema.sql 中不存在 |
| 添加 `check_in_date` | 使用日期格式，如 '2025-02-15' |
| 添加 `check_out_date` | 使用日期格式，如 '2025-02-20' |

**示例数据更新**:
```sql
-- 修复前
INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_time, check_out_time) VALUES
('The Grand Plaza Hotel', 'Shanghai', 680.00, 4.5,
 'Luxurious 5-star hotel...',
 '["WiFi", "Pool", "Gym"]',
 '15:00:00', '11:00:00');

-- 修复后
INSERT INTO hotels (name, destination, price, rating, description, facilities, check_in_date, check_out_date) VALUES
('The Grand Plaza Hotel', 'Shanghai', 680.00, 4.5,
 'Luxurious 5-star hotel...',
 '["WiFi", "Pool", "Gym"]',
 '2025-02-15', '2025-02-20');
```

#### 2.3 flights 表数据

| 修改内容 | 详情 |
|---------|------|
| 移除 `departure_time` | schema.sql 中不存在 |
| 移除 `arrival_time` | schema.sql 中不存在 |
| 移除 `flight_number` | schema.sql 中不存在 |
| 移除 `available_seats` | schema.sql 中不存在 |
| 修改 `duration_minutes` 为 `duration` | 匹配 schema.sql 字段名 |

**示例数据更新**:
```sql
-- 修复前
INSERT INTO flights (origin, destination, departure_date, return_date, departure_time, arrival_time,
                  price, airline, flight_number, duration_minutes, available_seats) VALUES
('Beijing', 'Shanghai', '2025-02-15', '2025-02-20', '08:30:00', '10:45:00',
 580.00, 'Air China', 'CA1851', 135, 45);

-- 修复后
INSERT INTO flights (origin, destination, departure_date, return_date,
                  price, airline, duration) VALUES
('Beijing', 'Shanghai', '2025-02-15', '2025-02-20',
 580.00, 'Air China', 135);
```

#### 2.4 attractions 表数据

| 修改内容 | 详情 |
|---------|------|
| 移除 `ticket_price` | schema.sql 中不存在 |
| 移除 `latitude` | schema.sql 中不存在 |
| 移除 `longitude` | schema.sql 中不存在 |
| 移除 `phone` | schema.sql 中不存在 |
| 移除 `website` | schema.sql 中不存在 |
| 添加 `tags` | JSONB 数组，每个景点包含相关标签 |

**示例数据更新**:
```sql
-- 修复前
INSERT INTO attractions (destination, name, category, rating, description, opening_hours,
                     ticket_price, latitude, longitude, phone, website) VALUES
('Shanghai', 'The Bund', 'historic', 4.6,
 'Iconic waterfront...',
 '00:00-24:00', 0.00, 31.2397, 121.4900, '+86-21-6329-6888', 'https://www.thebund-shanghai.com');

-- 修复后
INSERT INTO attractions (destination, name, category, rating, description, opening_hours, tags) VALUES
('Shanghai', 'The Bund', 'historic', 4.6,
 'Iconic waterfront...',
 '00:00-24:00', '["historic", "landmark", "waterfront", "photography", "architecture"]');
```

**Tags 策略**:
- 历史景点: `["historic", "culture", "architecture", "unesco"]`
- 自然景观: `["nature", "landscape", "lake", "mountain"]`
- 主题公园: `["entertainment", "family", "theme_park"]`
- 文化景点: `["culture", "temple", "religion", "traditional"]`
- 动物园/野生动物: `["wildlife", "animals", "nature", "family"]`
- 美食街区: `["food", "nightlife", "traditional", "shopping"]`

#### 2.5 rag_documents 表数据

| 修改内容 | 详情 |
|---------|------|
| 修复 flight 查询条件 | 使用 `origin` 和 `destination` 代替 `flight_number` |

**示例数据更新**:
```sql
-- 修复前
('flight', (SELECT id FROM flights WHERE flight_number = 'CA1851' LIMIT 1),
 'Air China Flight CA1851 operates...',
 'airline', '{"aircraft_type": "Boeing 737-800"}');

-- 修复后
('flight', (SELECT id FROM flights WHERE origin = 'Beijing' AND destination = 'Shanghai'
                                          AND airline = 'Air China' LIMIT 1),
 'Air China flight operates...',
 'airline', '{"aircraft_type": "Boeing 737-800"}');
```

---

## 验证标准

修复完成后，确保：

- ✅ 所有 schema.sql 中定义的列都能在 init-sample-data.sql 的 INSERT 语句中找到匹配（或有默认值）
- ✅ init-sample-data.sql 中的所有列都在 schema.sql 中定义
- ✅ 字段顺序和命名保持一致（如 `check_in_date` 而非 `checkin_date`）
- ✅ 数据类型匹配（如 NUMERIC vs TIMESTAMP）
- ✅ JSON/JSONB 字段的格式正确
- ✅ 两个文件都与 Java 实体类的字段保持同步

---

## 影响分析

### 正面影响
1. **数据一致性**: Schema 和示例数据完全同步，避免字段不匹配错误
2. **Java 对齐**: 所有字段与 Java 实体类保持一致，便于 JPA 映射
3. **代码质量**: 移除无用字段和触发器，简化数据库逻辑
4. **维护性**: 清晰的字段定义和注释，便于后续维护

### 潜在风险
1. **ID 类型差异**: users 表使用 BIGINT，其他表使用 UUID，需要 Java 层面处理外键关联
2. **数据迁移**: 如果已有生产数据，需要迁移脚本来处理字段变更
3. **触发器移除**: 依赖触发器更新 updated_at 的代码需要改为依赖数据库自动更新

### 兼容性建议
1. 本修复针对 **PostgreSQL 15** 优化，使用以下 PostgreSQL 特定语法：
   - `BIGSERIAL` 用于自增整数 ID
   - `gen_random_uuid()` 用于生成 UUID
   - 触发器用于自动更新 `updated_at`
2. 如果需要迁移到 MySQL：
   - 将 `BIGSERIAL` 改为 `BIGINT AUTO_INCREMENT`
   - 将 `gen_random_uuid()` 改为 `UUID()` 函数
   - 将触发器改为 `ON UPDATE CURRENT_TIMESTAMP`
   - JSONB 在 MySQL 5.7+ 中以 JSON 类型存在，功能略有差异

---

## 使用方法

### 执行顺序

1. **执行 schema.sql 创建表结构**
   ```bash
   mysql -u root -p travel_assistant < schema.sql
   ```

2. **执行 init-sample-data.sql 插入示例数据**
   ```bash
   mysql -u root -p travel_assistant < init-sample-data.sql
   ```

### 验证数据

执行 init-sample-data.sql 末尾的验证查询：
```sql
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'hotels', COUNT(*) FROM hotels
UNION ALL
SELECT 'flights', COUNT(*) FROM flights
UNION ALL
SELECT 'attractions', COUNT(*) FROM attractions
UNION ALL
SELECT 'rag_documents', COUNT(*) FROM rag_documents
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs;
```

**预期结果**:
- users: 5
- hotels: 8
- flights: 10
- attractions: 20
- rag_documents: 4
- audit_logs: 5

---

## 后续工作

### 推荐改进
1. **数据库迁移脚本**: 创建 Flyway/Liquibase 迁移脚本，支持版本化管理
2. **索引优化**: 根据实际查询模式添加更多复合索引
3. **分区策略**: 对大数据量表（如 audit_logs）实施分区
4. **备份策略**: 定期备份 schema 和数据，防止数据丢失

### 注意事项
1. **密码哈希**: 示例数据中的密码哈希需要替换为实际的安全哈希
2. **用户输入**: 生产环境需要添加数据验证和清理
3. **性能监控**: 监控查询性能，根据实际使用情况优化索引

---

## 总结

本次修复彻底解决了 schema.sql 和 init-sample-data.sql 之间的字段不同步问题，确保：
- 所有表结构与 Java 实体类完全一致
- 示例数据可以成功插入，无约束冲突
- 字段命名统一，易于理解和维护
- 添加了必要的注释，提高可读性

**修复文件**:
- ✅ `travel-assistant/database/schema.sql` - 更正后的完整 schema
- ✅ `travel-assistant/database/init-sample-data.sql` - 更正后的完整示例数据
- ✅ `travel-assistant/database/DB_SCHEMA_FIXES_SUMMARY.md` - 本修复总结文档

**修复日期**: 2025-01-23
