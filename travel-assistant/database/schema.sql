-- =============================================================================
-- Travel Assistant Database Schema
-- 统一数据库 Schema 与 Java 实体类字段定义（PostgreSQL）
--
-- 说明：
-- 1) 本脚本聚焦核心业务实体：users / hotels / flights / attractions / rag_documents / audit_logs / bookings
-- 2) 所有表均包含审计字段 created_at/updated_at（使用触发器自动刷新）
-- 3) users 和 audit_logs 表使用 BIGSERIAL 自增 ID
-- 4) 其他表使用 UUID 主键以匹配对应实体类
-- 5) JSON 字段使用 JSONB，配合应用侧 JsonbConverter 进行序列化/反序列化
-- 6) FIX: 2025-01-23 - 修复字段不同步问题，与 Java 实体类保持一致
-- 7) FIX: 2025-01-24 - 添加bookings表以支持booking-service
-- =============================================================================

-- 启用 gen_random_uuid()（PostgreSQL pgcrypto 扩展）
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =============================================================================
-- 通用函数：自动维护 updated_at
-- =============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 表 1：users - 用户表
-- 用于登录与个性化推荐（偏好 JSON）
-- FIXED: 与 Java 实体类保持一致，添加 password_hash, is_active, last_login 字段
-- FIXED: id 类型从 UUID 改为 BIGSERIAL 以匹配 auth-service User.java（PostgreSQL 语法）
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,

  -- 账户信息
  email VARCHAR(255) NOT NULL UNIQUE,
  username VARCHAR(100) NOT NULL UNIQUE,

  -- 认证信息（FIXED: 添加以匹配 User.java）
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP NULL,

  -- 用户偏好（用于个性化推荐）
  -- 示例：{"budget_level":"mid","travel_style":"adventure","preferred_destinations":["Paris"],"interests":["beach"]}
  preferences_json JSONB NOT NULL DEFAULT '{}'::jsonb,

  -- 审计字段
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- users 索引（唯一约束已自动生成索引；此处为查询场景补充/显式声明）
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

COMMENT ON TABLE users IS '用户表：用于登录、认证与个性化推荐（preferences_json）';
COMMENT ON COLUMN users.id IS '主键：BIGINT，自增';
COMMENT ON COLUMN users.email IS '用户邮箱：唯一且必填，用于登录';
COMMENT ON COLUMN users.username IS '用户名：唯一且必填（展示/登录标识之一）';
COMMENT ON COLUMN users.password_hash IS '密码哈希：BCrypt 加密后的密码（FIXED: 新增）';
COMMENT ON COLUMN users.is_active IS '账户状态：是否激活，默认 TRUE（FIXED: 新增）';
COMMENT ON COLUMN users.last_login IS '最后登录时间：可为空（FIXED: 新增）';
COMMENT ON COLUMN users.preferences_json IS '用户偏好 JSON：预算/风格/兴趣/偏好目的地等，用于推荐';
COMMENT ON COLUMN users.created_at IS '创建时间：记录第一次创建时间';
COMMENT ON COLUMN users.updated_at IS '更新时间：最后一次修改时间（FIXED: 移除 created_by/updated_by）';

-- =============================================================================
-- 表 2：hotels - 酒店表
-- =============================================================================
CREATE TABLE IF NOT EXISTS hotels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 酒店信息
  name VARCHAR(255) NOT NULL,
  destination VARCHAR(100) NOT NULL,

  -- 价格与评分
  price NUMERIC(10,2) NOT NULL,
  rating NUMERIC(2,1) NOT NULL DEFAULT 0.0,

  -- 介绍与设施
  description TEXT,
  facilities JSONB NOT NULL DEFAULT '[]'::jsonb,

  -- 日期字段（业务中通常来自搜索参数，可为空以便存储基础酒店信息）
  check_in_date DATE,
  check_out_date DATE,

  -- 审计字段（FIXED: 移除 created_by/updated_by 以保持一致性）
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT chk_hotels_rating_range CHECK (rating >= 0 AND rating <= 5)
);

-- hotels 索引
CREATE INDEX IF NOT EXISTS idx_hotels_destination ON hotels(destination);
CREATE INDEX IF NOT EXISTS idx_hotels_destination_price ON hotels(destination, price);
CREATE INDEX IF NOT EXISTS idx_hotels_rating ON hotels(rating);
CREATE INDEX IF NOT EXISTS idx_hotels_created_at ON hotels(created_at);

COMMENT ON TABLE hotels IS '酒店表：酒店基础信息、价格与设施；check_in/out_date 通常来自搜索参数';
COMMENT ON COLUMN hotels.id IS '主键：UUID，默认 gen_random_uuid() 自动生成';
COMMENT ON COLUMN hotels.name IS '酒店名称：必填，最长 255';
COMMENT ON COLUMN hotels.destination IS '目的地城市：必填，最长 100，用于检索与聚合（建立索引）';
COMMENT ON COLUMN hotels.price IS '每晚价格：NUMERIC(10,2)，精确到分（¥/晚）';
COMMENT ON COLUMN hotels.rating IS '酒店评分：0-5，精度 0.1；默认 0；带范围校验';
COMMENT ON COLUMN hotels.description IS '酒店介绍：详细描述（可为空）';
COMMENT ON COLUMN hotels.facilities IS '设施列表：JSON 数组，例如 ["WiFi","Pool","Gym"]';
COMMENT ON COLUMN hotels.check_in_date IS '入住日期：通常由用户搜索条件产生；可用于缓存/记录最近一次搜索结果';
COMMENT ON COLUMN hotels.check_out_date IS '退住日期：通常由用户搜索条件产生；可用于缓存/记录最近一次搜索结果';
COMMENT ON COLUMN hotels.created_at IS '创建时间：记录第一次创建时间';
COMMENT ON COLUMN hotels.updated_at IS '更新时间：最后一次修改时间（FIXED: 移除 created_by/updated_by）';

-- =============================================================================
-- 表 3：flights - 航班表
-- =============================================================================
CREATE TABLE IF NOT EXISTS flights (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  --航班号
  flight_no VARCHAR(10) NOT NULL,
  -- 航线信息
  origin VARCHAR(100) NOT NULL,
  destination VARCHAR(100) NOT NULL,

  -- 日期
  departure_date DATE NOT NULL,
  return_date DATE,

  -- 价格与航空公司
  price NUMERIC(10,2) NOT NULL,
  airline VARCHAR(100) NOT NULL,

  -- 飞行时长（分钟）
  duration INTEGER,

  -- 审计字段（FIXED: 移除 created_by/updated_by 以保持一致性）
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT chk_flights_duration_non_negative CHECK (duration IS NULL OR duration >= 0)
);

-- flights 索引
CREATE INDEX IF NOT EXISTS idx_flights_route ON flights(origin, destination);
CREATE INDEX IF NOT EXISTS idx_flights_departure_date ON flights(departure_date);
CREATE INDEX IF NOT EXISTS idx_flights_route_departure_date ON flights(origin, destination, departure_date);
CREATE INDEX IF NOT EXISTS idx_flights_created_at ON flights(created_at);

COMMENT ON TABLE flights IS '航班表：航线、出发/返回日期、价格、航空公司及时长';
COMMENT ON COLUMN flights.id IS '主键：UUID，默认 gen_random_uuid() 自动生成';
COMMENT ON COLUMN flights.flight_no IS '航班号';
COMMENT ON COLUMN flights.origin IS '出发城市代码/名称：必填，如 "Shanghai" 或 "SHA"';
COMMENT ON COLUMN flights.destination IS '目的地城市代码/名称：必填';
COMMENT ON COLUMN flights.departure_date IS '出发日期：必填；常用搜索条件（建立索引）';
COMMENT ON COLUMN flights.return_date IS '返回日期：可为空；单程航班为 NULL，用于往返航班';
COMMENT ON COLUMN flights.price IS '单人票价：NUMERIC(10,2)，精确到分';
COMMENT ON COLUMN flights.airline IS '航空公司名称：必填，如 "China Eastern"';
COMMENT ON COLUMN flights.duration IS '飞行时长：单位分钟，如 120 表示 2 小时；可为空';
COMMENT ON COLUMN flights.created_at IS '创建时间：记录第一次创建时间';
COMMENT ON COLUMN flights.updated_at IS '更新时间：最后一次修改时间（FIXED: 移除 created_by/updated_by）';

-- =============================================================================
-- 表 4：attractions - 景点表
-- tags 为核心字段（JSON 数组），配合 GIN 索引进行标签检索
-- =============================================================================
CREATE TABLE IF NOT EXISTS attractions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 基本信息
  destination VARCHAR(100) NOT NULL,
  name VARCHAR(255) NOT NULL,

  -- 分类与评分
  category VARCHAR(50),
  description TEXT,
  rating NUMERIC(2,1) NOT NULL DEFAULT 0.0,
  opening_hours VARCHAR(100),

  -- 核心字段：标签数组（JSON）
  -- 示例：夏季海滩 ["summer","beach","family","swimming"]
  --       冬季滑雪 ["winter","skiing","snow","adventure"]
  tags TEXT[] NOT NULL DEFAULT '{}',

  -- 审计字段（FIXED: 移除 created_by/updated_by 以保持一致性）
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT chk_attractions_rating_range CHECK (rating >= 0 AND rating <= 5)
);

-- attractions 索引
CREATE INDEX IF NOT EXISTS idx_attractions_destination ON attractions(destination);
CREATE INDEX IF NOT EXISTS idx_attractions_category ON attractions(category);
CREATE INDEX IF NOT EXISTS idx_attractions_rating ON attractions(rating);
CREATE INDEX IF NOT EXISTS idx_attractions_created_at ON attractions(created_at);

-- ⭐ tags 查询加速：GIN 索引
CREATE INDEX IF NOT EXISTS idx_attractions_tags_gin ON attractions USING GIN (tags);

COMMENT ON TABLE attractions IS '景点表：景点信息、评分与标签（tags）用于分类/搜索/推荐';
COMMENT ON COLUMN attractions.id IS '主键：UUID，默认 gen_random_uuid() 自动生成';
COMMENT ON COLUMN attractions.destination IS '景点所在城市：必填；常用搜索条件（建立索引）';
COMMENT ON COLUMN attractions.name IS '景点名称：必填，最长 255';
COMMENT ON COLUMN attractions.category IS '景点分类：如 Museum/Park/Historic/Food/Beach 等（建立索引）';
COMMENT ON COLUMN attractions.description IS '景点详细介绍：可为空';
COMMENT ON COLUMN attractions.rating IS '景点评分：0-5；默认 0；可用于排序/过滤（建立索引）';
COMMENT ON COLUMN attractions.opening_hours IS '营业时间：如 "09:00-18:00" 或 "09:00-18:00, 周一休息"';
COMMENT ON COLUMN attractions.tags IS '核心字段：景点标签数组（JSONB），用于分类、搜索与 RAG/推荐；使用 GIN 索引加速';
COMMENT ON COLUMN attractions.created_at IS '创建时间：记录第一次创建时间';
COMMENT ON COLUMN attractions.updated_at IS '更新时间：最后一次修改时间（FIXED: 移除 created_by/updated_by）';

-- =============================================================================
-- 触发器：维护 updated_at
-- =============================================================================
DROP TRIGGER IF EXISTS trg_set_updated_at_users ON users;
CREATE TRIGGER trg_set_updated_at_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_set_updated_at_hotels ON hotels;
CREATE TRIGGER trg_set_updated_at_hotels
BEFORE UPDATE ON hotels
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_set_updated_at_flights ON flights;
CREATE TRIGGER trg_set_updated_at_flights
BEFORE UPDATE ON flights
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_set_updated_at_attractions ON attractions;
CREATE TRIGGER trg_set_updated_at_attractions
BEFORE UPDATE ON attractions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_set_updated_at_rag_documents ON rag_documents;
CREATE TRIGGER trg_set_updated_at_rag_documents
BEFORE UPDATE ON rag_documents
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- =============================================================================
-- 表 5：rag_documents - RAG 文档表（FIXED: 新增以支持 init-sample-data.sql）
-- =============================================================================
CREATE TABLE IF NOT EXISTS rag_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 关联实体
  entity_type VARCHAR(50) NOT NULL, -- 'hotel', 'attraction', 'flight' 等
  entity_id UUID NOT NULL,

  -- 文档内容
  content TEXT NOT NULL,
  source VARCHAR(100), -- 'review', 'wiki', 'official', 'airline' 等
  metadata JSONB DEFAULT '{}'::jsonb,

  -- 审计字段
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- rag_documents 索引
CREATE INDEX IF NOT EXISTS idx_rag_documents_entity ON rag_documents(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_rag_documents_source ON rag_documents(source);
CREATE INDEX IF NOT EXISTS idx_rag_documents_created_at ON rag_documents(created_at);

COMMENT ON TABLE rag_documents IS 'RAG 文档表：存储用于 RAG 检索的文档内容';
COMMENT ON COLUMN rag_documents.id IS '主键：UUID';
COMMENT ON COLUMN rag_documents.entity_type IS '实体类型：hotel/attraction/flight 等';
COMMENT ON COLUMN rag_documents.entity_id IS '实体ID：关联到对应表的 UUID';
COMMENT ON COLUMN rag_documents.content IS '文档内容：用于语义检索的文本';
COMMENT ON COLUMN rag_documents.source IS '来源类型：review/wiki/official/airline 等';
COMMENT ON COLUMN rag_documents.metadata IS '元数据：JSON 格式，如 {"rating": 4.5}';

-- =============================================================================
-- 表 6：audit_logs - 审计日志表（FIXED: 新增以支持 init-sample-data.sql）
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGSERIAL PRIMARY KEY,

  -- 操作信息
  user_id BIGINT NULL, -- 关联到 users 表
  action VARCHAR(100) NOT NULL, -- 'search', 'book', 'recommend' 等

  endpoint      VARCHAR(255),                 -- 请求路径
  method        VARCHAR(10),                  -- GET / POST / PUT / DELETE …
  status_code   INTEGER,                      -- HTTP 响应码

  -- 请求信息
  ip_address VARCHAR(255),
  user_agent VARCHAR(512),

  -- 审计字段
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- audit_logs 索引
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

COMMENT ON TABLE audit_logs IS '审计日志表：记录用户操作和系统事件';
COMMENT ON COLUMN audit_logs.id            IS '主键，自增';
COMMENT ON COLUMN audit_logs.user_id       IS '用户ID，关联 users.id';
COMMENT ON COLUMN audit_logs.action        IS '操作类型';
COMMENT ON COLUMN audit_logs.endpoint      IS '请求接口路径';
COMMENT ON COLUMN audit_logs.method        IS 'HTTP 方法';
COMMENT ON COLUMN audit_logs.status_code   IS '响应状态码';
COMMENT ON COLUMN audit_logs.ip_address    IS '客户端 IP';
COMMENT ON COLUMN audit_logs.user_agent    IS '客户端 UA';
COMMENT ON COLUMN audit_logs.created_at    IS '日志创建时间';

-- =============================================================================
-- 表 7：bookings - 预订表
-- =============================================================================
CREATE TABLE IF NOT EXISTS bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- 用户和预订信息
  user_id UUID NOT NULL,
  booking_type VARCHAR(50) NOT NULL, -- 'HOTEL', 'FLIGHT', 'ATTRACTION'
  resource_id UUID NOT NULL, -- 对应的酒店/航班/景点 ID

  -- 预订详情
  booking_date TIMESTAMP NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'CONFIRMED', 'CANCELLED'
  total_price NUMERIC(10,2),
  notes TEXT,

  -- 审计字段
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- bookings 索引
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_booking_type ON bookings(booking_type);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_booking_date ON bookings(booking_date);
CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);
CREATE INDEX IF NOT EXISTS idx_bookings_resource_type_id ON bookings(booking_type, resource_id);

COMMENT ON TABLE bookings IS '预订表：记录用户对酒店、航班、景点的预订';
COMMENT ON COLUMN bookings.id IS '主键：UUID，默认 gen_random_uuid() 自动生成';
COMMENT ON COLUMN bookings.user_id IS '用户ID：关联用户，必填';
COMMENT ON COLUMN bookings.booking_type IS '预订类型：HOTEL/FLIGHT/ATTRACTION，必填';
COMMENT ON COLUMN bookings.resource_id IS '资源ID：关联的酒店/航班/景点ID，必填';
COMMENT ON COLUMN bookings.booking_date IS '预订时间：用户发起预订的时间，必填';
COMMENT ON COLUMN bookings.status IS '预订状态：PENDING/CONFIRMED/CANCELLED，默认PENDING';
COMMENT ON COLUMN bookings.total_price IS '总价：预订总金额，精确到分';
COMMENT ON COLUMN bookings.notes IS '备注：预订备注信息';
COMMENT ON COLUMN bookings.created_by IS '创建者ID：创建预订的用户ID';
COMMENT ON COLUMN bookings.updated_by IS '更新者ID：更新预订的用户ID';
COMMENT ON COLUMN bookings.created_at IS '创建时间：记录第一次创建时间';
COMMENT ON COLUMN bookings.updated_at IS '更新时间：最后一次修改时间';

-- =============================================================================
-- 触发器：bookings 表 updated_at 自动更新
-- =============================================================================
DROP TRIGGER IF EXISTS trg_set_updated_at_bookings ON bookings;
CREATE TRIGGER trg_set_updated_at_bookings
BEFORE UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- =============================================================================
-- 记忆系统表结构（从 schema_memory.sql 整合）
-- 用途：存储四层记忆系统的数据
-- 兼容性：与现有 users 表保持一致，使用 BIGINT 作为 user_id
-- =============================================================================

-- =============================================================================
-- 表 8：conversations - 对话会话表
-- 作用：存储每次对话会话的基本信息，对应左侧历史列表中的每一个条目
-- =============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    summary TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    CONSTRAINT fk_conversations_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conv_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conv_updated ON conversations(updated_at);
CREATE INDEX IF NOT EXISTS idx_conv_status ON conversations(status);

DROP TRIGGER IF EXISTS trg_set_updated_at_conversations ON conversations;
CREATE TRIGGER trg_set_updated_at_conversations
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE conversations IS '对话会话表：存储每次对话会话的基本信息';

-- =============================================================================
-- 表 9：conversation_messages - 对话消息表
-- 关联关系：多对一，多条消息属于一个会话
-- =============================================================================
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id BIGINT NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_msg_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    CONSTRAINT fk_msg_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_msg_conv ON conversation_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_msg_user ON conversation_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_msg_created ON conversation_messages(created_at);

COMMENT ON TABLE conversation_messages IS '对话消息表：存储会话中的每条消息';

-- =============================================================================
-- 表 10：user_preferences - 用户偏好表
-- 作用：存储用户的固定偏好，用于长期记忆（第4层）
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    preference_type VARCHAR(50) NOT NULL,
    preference_value TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.5,
    source VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_preferences_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, preference_type)
);

CREATE INDEX IF NOT EXISTS idx_pref_user ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_pref_type ON user_preferences(preference_type);
CREATE INDEX IF NOT EXISTS idx_pref_confidence ON user_preferences(confidence);

DROP TRIGGER IF EXISTS trg_set_updated_at_preferences ON user_preferences;
CREATE TRIGGER trg_set_updated_at_preferences
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

COMMENT ON TABLE user_preferences IS '用户偏好表：存储用户的固定偏好，用于长期记忆';

-- =============================================================================
-- 表 11：task_cases - 历史任务案例表
-- 作用：存储用户的历史旅游任务，用于长期记忆和案例参考
-- =============================================================================
CREATE TABLE IF NOT EXISTS task_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    destination VARCHAR(255),
    duration_days INT,
    budget_range VARCHAR(50),
    preferences JSONB DEFAULT '[]',
    plan_summary TEXT,
    satisfaction FLOAT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_task_cases_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_case_user ON task_cases(user_id);
CREATE INDEX IF NOT EXISTS idx_case_dest ON task_cases(destination);
CREATE INDEX IF NOT EXISTS idx_case_satisfaction ON task_cases(satisfaction);

COMMENT ON TABLE task_cases IS '历史任务案例表：存储用户的历史旅游任务';

-- =============================================================================
-- 表 12：vector_memories - 向量存储元数据表
-- 作用：存储向量数据库中数据的元数据，用于关联关系型数据库和向量数据库
-- =============================================================================
CREATE TABLE IF NOT EXISTS vector_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    memory_type VARCHAR(50),
    content TEXT NOT NULL,
    embedding_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vector_memories_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_vec_user ON vector_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_vec_type ON vector_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_vec_embedding ON vector_memories(embedding_id);

COMMENT ON TABLE vector_memories IS '向量存储元数据表：存储向量数据库的元数据';

-- =============================================================================
-- 辅助视图
-- =============================================================================

-- 会话统计视图
CREATE OR REPLACE VIEW v_session_stats AS
SELECT 
    c.id AS conversation_id,
    c.user_id,
    c.session_id,
    c.title,
    c.status,
    c.summary,
    COUNT(cm.id) AS message_count,
    c.created_at,
    c.updated_at
FROM conversations c
LEFT JOIN conversation_messages cm ON c.id = cm.conversation_id
GROUP BY c.id, c.user_id, c.session_id, c.title, c.status, c.summary, c.created_at, c.updated_at;

-- 用户偏好汇总视图
CREATE OR REPLACE VIEW v_user_preferences_summary AS
SELECT 
    up.user_id,
    COUNT(*) AS preference_count,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'type', up.preference_type,
            'value', up.preference_value,
            'confidence', up.confidence,
            'source', up.source
        )
    ) AS preferences
FROM user_preferences up
GROUP BY up.user_id;

-- =============================================================================
-- 清理函数（用于定期清理过期数据）
-- =============================================================================

-- 删除过期的会话（保留30天）
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM conversations 
    WHERE status = 'archived' 
    AND updated_at < NOW() - INTERVAL '30 days';
    
    RAISE NOTICE 'Deleted % expired sessions', ROW_COUNT;
END;
$$ LANGUAGE plpgsql;

-- 删除低置信度的偏好（置信度 < 0.3）
CREATE OR REPLACE FUNCTION cleanup_low_confidence_preferences()
RETURNS void AS $$
BEGIN
    DELETE FROM user_preferences 
    WHERE confidence < 0.3 
    AND updated_at < NOW() - INTERVAL '7 days';
    
    RAISE NOTICE 'Deleted % low confidence preferences', ROW_COUNT;
END;
$$ LANGUAGE plpgsql;