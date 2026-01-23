# 数据库 Schema 修改汇总

**修改日期**: 2025-01-23
**目标**: 与 Java 实体类字段保持一致

---

## 修改清单

### 一、schema.sql 修改

#### 表级别修改

| 表名 | 主要修改 | 状态 |
|-------|----------|------|
| users | 添加 password_hash, is_active, last_login；ID 改为 BIGSERIAL | ✅ 完成 |
| hotels | 移除 created_by/updated_by；保留 check_in_date/out_date | ✅ 完成 |
| flights | 移除多余字段；duration_minutes 改为 duration | ✅ 完成 |
| attractions | 添加 tags 字段；移除多余字段 | ✅ 完成 |
| rag_documents | 新增表定义 | ✅ 完成 |
| audit_logs | 新增表定义 | ✅ 完成 |
| 触发器 | 为所有表添加 updated_at 自动更新触发器 | ✅ 完成 |

#### 字段修改详情

##### users 表
| 操作 | 字段 | 旧值 | 新值 |
|------|------|-------|------|
| 修改 | id | UUID | BIGSERIAL |
| 新增 | password_hash | - | VARCHAR(255) NOT NULL |
| 新增 | is_active | - | BOOLEAN DEFAULT TRUE |
| 新增 | last_login | - | TIMESTAMP NULL |
| 删除 | created_by | UUID | - |
| 删除 | updated_by | UUID | - |
| 保留 | preferences_json | - | JSONB NOT NULL DEFAULT '{}'::jsonb |
| 保留 | created_at, updated_at | - | TIMESTAMP |

##### hotels 表
| 操作 | 字段 | 旧值 | 新值 |
|------|------|-------|------|
| 删除 | check_in_time | TIME | - |
| 删除 | check_out_time | TIME | - |
| 删除 | created_by | UUID | - |
| 删除 | updated_by | UUID | - |
| 保留 | check_in_date | - | DATE |
| 保留 | check_out_date | - | DATE |

##### flights 表
| 操作 | 字段 | 旧值 | 新值 |
|------|------|-------|------|
| 删除 | departure_time | TIME | - |
| 删除 | arrival_time | TIME | - |
| 删除 | flight_number | VARCHAR | - |
| 删除 | available_seats | INTEGER | - |
| 重命名 | duration_minutes | INTEGER | duration (INTEGER) |
| 删除 | created_by | UUID | - |
| 删除 | updated_by | UUID | - |

##### attractions 表
| 操作 | 字段 | 旧值 | 新值 |
|------|------|-------|------|
| 删除 | ticket_price | NUMERIC | - |
| 删除 | latitude | NUMERIC | - |
| 删除 | longitude | NUMERIC | - |
| 删除 | phone | VARCHAR | - |
| 删除 | website | VARCHAR | - |
| 新增 | tags | - | JSONB NOT NULL DEFAULT '[]'::jsonb |
| 删除 | created_by | UUID | - |
| 删除 | updated_by | UUID | - |

##### rag_documents 表（新增）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键，gen_random_uuid() |
| entity_type | VARCHAR(50) | 实体类型（hotel/attraction/flight） |
| entity_id | UUID | 关联实体ID |
| content | TEXT | 文档内容 |
| source | VARCHAR(100) | 来源（review/wiki/official/airline） |
| metadata | JSONB | 元数据 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间（触发器自动更新） |

##### audit_logs 表（新增）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL | 主键，自增 |
| user_id | BIGINT | 用户ID（外键） |
| action | VARCHAR(100) | 操作类型（search/book/recommend） |
| resource_type | VARCHAR(50) | 资源类型（hotels/flights/attractions） |
| resource_id | UUID | 资源ID |
| details | JSONB | 操作详情 |
| ip_address | VARCHAR(255) | IP地址 |
| user_agent | VARCHAR(512) | 用户代理 |
| created_at | TIMESTAMP | 创建时间 |

---

### 二、init-sample-data.sql 修改

#### users 表数据
| 操作 | 字段 | 说明 |
|------|------|------|
| 删除 | full_name | 移除字段 |
| 删除 | travel_style | 合并到 preferences_json |
| 删除 | budget_level | 合并到 preferences_json |
| 新增 | password_hash | 所有用户：'$2a$10$rOzK4Z8kB7mV5jA.xxXxAu' |
| 新增 | is_active | 所有用户：TRUE |
| 新增 | last_login | 所有用户：NULL |

**数据条数**: 5 条

#### hotels 表数据
| 操作 | 字段 | 说明 |
|------|------|------|
| 删除 | check_in_time | 移除时间字段 |
| 删除 | check_out_time | 移除时间字段 |
| 新增 | check_in_date | 日期格式：'YYYY-MM-DD' |
| 新增 | check_out_date | 日期格式：'YYYY-MM-DD' |

**数据条数**: 8 条

#### flights 表数据
| 操作 | 字段 | 说明 |
|------|------|------|
| 删除 | departure_time | 移除 |
| 删除 | arrival_time | 移除 |
| 删除 | flight_number | 移除 |
| 删除 | available_seats | 移除 |
| 重命名 | duration_minutes | 改为 duration（分钟） |

**数据条数**: 10 条

#### attractions 表数据
| 操作 | 字段 | 说明 |
|------|------|------|
| 删除 | ticket_price | 移除 |
| 删除 | latitude | 移除 |
| 删除 | longitude | 移除 |
| 删除 | phone | 移除 |
| 删除 | website | 移除 |
| 新增 | tags | JSON 数组，每个景点包含 4-6 个标签 |

**Tags 策略**:
- 历史景点: `["historic", "culture", "architecture", "unesco"]`
- 自然景观: `["nature", "landscape", "lake", "mountain"]`
- 主题公园: `["entertainment", "family", "theme_park"]`
- 文化景点: `["culture", "temple", "religion", "traditional"]`
- 动物园/野生动物: `["wildlife", "animals", "nature", "family"]`
- 美食街区: `["food", "nightlife", "traditional", "shopping"]`

**数据条数**: 20 条

#### rag_documents 表数据
| 操作 | 说明 |
|------|------|
| 修改 flight 查询条件 | 使用 origin, destination, airline 代替 flight_number |

**数据条数**: 4 条

#### audit_logs 表数据
| 操作 | 说明 |
|------|------|
| 无修改 | 数据保持不变 |

**数据条数**: 5 条

---

## 验证结果

### Schema 验证
✅ 所有表结构与 Java 实体类完全一致
✅ users 表使用 BIGSERIAL（匹配 auth-service User.java）
✅ 其他表使用 UUID（匹配对应实体类）
✅ 所有表都有 updated_at 触发器自动更新
✅ JSON 字段使用 JSONB 类型
✅ 索引配置完整

### 数据验证
✅ 所有 INSERT 语句字段与 Schema 匹配
✅ 无不存在的字段引用
✅ 数据类型正确
✅ JSON/JSONB 格式正确
✅ 外键引用有效

### 数据条数统计
| 表名 | 预期条数 | 说明 |
|------|----------|------|
| users | 5 | 示例用户 |
| hotels | 8 | 示例酒店 |
| flights | 10 | 示例航班 |
| attractions | 20 | 示例景点 |
| rag_documents | 4 | RAG 文档 |
| audit_logs | 5 | 审计日志 |

---

## PostgreSQL 特定语法说明

### ID 自增
```sql
-- PostgreSQL 语法
id BIGSERIAL PRIMARY KEY

-- 对应的 MySQL 语法（如需迁移）
id BIGINT AUTO_INCREMENT PRIMARY KEY
```

### UUID 生成
```sql
-- PostgreSQL 语法（需要 pgcrypto 扩展）
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- 对应的 MySQL 语法
id UUID PRIMARY KEY DEFAULT UUID()
```

### 时间戳自动更新
```sql
-- PostgreSQL 语法（使用触发器）
CREATE TRIGGER trg_set_updated_at_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- 对应的 MySQL 语法
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

---

## 文件清单

| 文件 | 行数 | 状态 | 说明 |
|------|------|------|------|
| schema.sql | 318 | ✅ 已修复 | 完整数据库 Schema |
| init-sample-data.sql | 261 | ✅ 已修复 | 完整示例数据 |
| DB_SCHEMA_FIXES_SUMMARY.md | - | ✅ 新增 | 详细修复说明 |
| CHANGES_SUMMARY.md | - | ✅ 新增 | 修改汇总（本文件） |

---

## 后续建议

1. **数据迁移**: 如果已有生产数据，需要编写迁移脚本
2. **索引优化**: 根据实际查询模式调整索引
3. **性能监控**: 监控慢查询，优化索引策略
4. **备份策略**: 定期备份 schema 和数据
5. **版本管理**: 考虑使用 Flyway/Liquibase 管理数据库版本

---

**修复完成**: 2025-01-23
**验证状态**: ✅ 全部通过
