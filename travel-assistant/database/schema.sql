-- =============================================================================
-- Travel Assistant Database Schema
-- 数据库初始化脚本 - 包含核心表结构
-- =============================================================================
-- 创建时间: 2025-01-20
-- 版本: v1.0.0
-- 描述: travel-assistant 项目的核心数据库表结构
-- =============================================================================

-- 启用必要的 PostgreSQL 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- =============================================================================
-- 1. 用户表 (users)
-- 用户基础信息和偏好设置
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    -- 基础字段
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email CITEXT UNIQUE NOT NULL,                    -- 邮箱 (唯一，支持大小写不敏感)
    username VARCHAR(100) UNIQUE NOT NULL,           -- 用户名 (唯一)
    password_hash VARCHAR(255) NOT NULL,             -- 密码哈希
    
    -- 个人信息
    full_name VARCHAR(255),                          -- 全名
    
    -- 用户偏好设置
    preferences_json JSONB,                          -- 用户偏好 (JSON格式)
    travel_style VARCHAR(50) DEFAULT 'relaxed',      -- 旅游风格: relaxed, adventure, cultural
    budget_level VARCHAR(50) DEFAULT 'mid',          -- 预算等级: luxury, mid, budget
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE              -- 最后登录时间
);

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_travel_style ON users(travel_style);
CREATE INDEX IF NOT EXISTS idx_users_budget_level ON users(budget_level);

-- =============================================================================
-- 2. 酒店表 (hotels)
-- 酒店基础信息和价格库存
-- =============================================================================
CREATE TABLE IF NOT EXISTS hotels (
    -- 基础字段
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,                      -- 酒店名称
    destination VARCHAR(100) NOT NULL,              -- 目的地
    
    -- 价格和评分
    price DECIMAL(10,2) NOT NULL,                   -- 价格 (每晚)
    rating DECIMAL(3,1) CHECK (rating >= 0 AND rating <= 5),  -- 评分 (0-5)
    
    -- 详细信息
    description TEXT,                               -- 酒店描述
    facilities JSONB,                               -- 设施列表 (JSON数组)
    
    -- 入住时间
    check_in_time TIME DEFAULT '15:00:00',          -- 入住时间
    check_out_time TIME DEFAULT '11:00:00',         -- 退房时间
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 酒店表索引
CREATE INDEX IF NOT EXISTS idx_hotels_destination ON hotels(destination);
CREATE INDEX IF NOT EXISTS idx_hotels_price ON hotels(price);
CREATE INDEX IF NOT EXISTS idx_hotels_rating ON hotels(rating);
CREATE INDEX IF NOT EXISTS idx_hotels_created_at ON hotels(created_at);
CREATE INDEX IF NOT EXISTS idx_hotels_destination_price ON hotels(destination, price);
CREATE INDEX IF NOT EXISTS idx_hotels_destination_rating ON hotels(destination, rating);

-- =============================================================================
-- 3. 航班表 (flights)
-- 航班信息和价格库存
-- =============================================================================
CREATE TABLE IF NOT EXISTS flights (
    -- 基础字段
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    origin VARCHAR(100) NOT NULL,                   -- 出发地
    destination VARCHAR(100) NOT NULL,              -- 目的地
    
    -- 日期和时间
    departure_date DATE NOT NULL,                  -- 出发日期
    return_date DATE,                               -- 返回日期 (可选，单程为NULL)
    departure_time TIME NOT NULL,                  -- 出发时间
    arrival_time TIME NOT NULL,                    -- 到达时间
    
    -- 价格和库存
    price DECIMAL(10,2) NOT NULL,                  -- 价格
    available_seats INTEGER DEFAULT 0,             -- 可用座位数
    
    -- 航班详情
    airline VARCHAR(100) NOT NULL,                 -- 航空公司
    flight_number VARCHAR(50) NOT NULL,            -- 航班号
    duration_minutes INTEGER NOT NULL,              -- 飞行时长 (分钟)
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 航班表索引
CREATE INDEX IF NOT EXISTS idx_flights_origin_destination ON flights(origin, destination);
CREATE INDEX IF NOT EXISTS idx_flights_departure_date ON flights(departure_date);
CREATE INDEX IF NOT EXISTS idx_flights_price ON flights(price);
CREATE INDEX IF NOT EXISTS idx_flights_airline ON flights(airline);
CREATE INDEX IF NOT EXISTS idx_flights_created_at ON flights(created_at);
CREATE INDEX IF NOT EXISTS idx_flights_route_date ON flights(origin, destination, departure_date);

-- =============================================================================
-- 4. 景点表 (attractions)
-- 旅游景点信息和评价
-- =============================================================================
CREATE TABLE IF NOT EXISTS attractions (
    -- 基础字段
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    destination VARCHAR(100) NOT NULL,              -- 目的地
    name VARCHAR(255) NOT NULL,                      -- 景点名称
    
    -- 分类和评价
    category VARCHAR(50) NOT NULL,                  -- 分类: museum, park, historic, food, entertainment, etc.
    rating DECIMAL(3,1) CHECK (rating >= 0 AND rating <= 5),  -- 评分 (0-5)
    
    -- 详细信息
    description TEXT,                               -- 景点描述
    opening_hours VARCHAR(100),                     -- 营业时间 (文本格式)
    ticket_price DECIMAL(10,2),                     -- 门票价格
    
    -- 地理位置
    latitude DECIMAL(10,8),                        -- 纬度
    longitude DECIMAL(11,8),                       -- 经度
    
    -- 联系信息
    phone VARCHAR(20),                              -- 电话
    website VARCHAR(500),                           -- 网站
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 景点表索引
CREATE INDEX IF NOT EXISTS idx_attractions_destination ON attractions(destination);
CREATE INDEX IF NOT EXISTS idx_attractions_category ON attractions(category);
CREATE INDEX IF NOT EXISTS idx_attractions_rating ON attractions(rating);
CREATE INDEX IF NOT EXISTS idx_attractions_name ON attractions(name);
CREATE INDEX IF NOT EXISTS idx_attractions_created_at ON attractions(created_at);
CREATE INDEX IF NOT EXISTS idx_attractions_destination_category ON attractions(destination, category);
CREATE INDEX IF NOT EXISTS idx_attractions_destination_rating ON attractions(destination, rating);

-- =============================================================================
-- 5. RAG 知识库表 (rag_documents) - 可选
-- 用于存储AI助手的知识库文档和向量数据
-- =============================================================================
CREATE TABLE IF NOT EXISTS rag_documents (
    -- 基础字段
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,               -- 实体类型: hotel, attraction, flight, guide
    entity_id UUID,                                 -- 关联的实体ID
    
    -- 文档内容
    content TEXT NOT NULL,                         -- 文档内容
    
    -- 向量数据 (需要 pgvector 扩展)
    embedding VECTOR(384),                          -- 向量嵌入 (384维)
    
    -- 元数据
    source VARCHAR(100),                           -- 来源: review, wiki, user_guide, official
    metadata JSONB,                                -- 额外元数据
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RAG文档表索引
CREATE INDEX IF NOT EXISTS idx_rag_documents_entity_type ON rag_documents(entity_type);
CREATE INDEX IF NOT EXISTS idx_rag_documents_entity_id ON rag_documents(entity_id);
CREATE INDEX IF NOT EXISTS idx_rag_documents_source ON rag_documents(source);
CREATE INDEX IF NOT EXISTS idx_rag_documents_created_at ON rag_documents(created_at);
CREATE INDEX IF NOT EXISTS idx_rag_documents_embedding ON rag_documents USING ivfflat (embedding vector_cosine_ops);

-- =============================================================================
-- 6. 审计日志表 (audit_logs) - 可选
-- 记录系统操作日志，用于审计和分析
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    -- 基础字段
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,                                   -- 用户ID (可为NULL，匿名操作)
    
    -- 操作信息
    action VARCHAR(100) NOT NULL,                  -- 操作类型: search, book, recommend, login, etc.
    resource_type VARCHAR(50),                      -- 资源类型
    resource_id UUID,                              -- 资源ID
    
    -- 详细信息
    details JSONB,                                 -- 操作详情 (JSON格式)
    ip_address INET,                               -- IP地址
    user_agent TEXT,                               -- 用户代理
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 审计日志表索引
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address);

-- =============================================================================
-- 触发器函数: 自动更新 updated_at 字段
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建触发器
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_hotels_updated_at 
    BEFORE UPDATE ON hotels 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_flights_updated_at 
    BEFORE UPDATE ON flights 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attractions_updated_at 
    BEFORE UPDATE ON attractions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rag_documents_updated_at 
    BEFORE UPDATE ON rag_documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 注释和说明
-- =============================================================================

-- 表关系说明:
-- 1. users: 用户基础表，所有用户相关数据的主表
-- 2. hotels: 酒店信息表，存储酒店基础信息
-- 3. flights: 航班信息表，存储航班路线和时间信息  
-- 4. attractions: 景点信息表，存储旅游景点数据
-- 5. rag_documents: RAG知识库表，存储AI助手使用的向量数据
-- 6. audit_logs: 审计日志表，记录系统操作历史

-- 索引策略:
-- 1. 所有主键和外键字段都有索引
-- 2. 常用查询字段创建了复合索引
-- 3. 地理位置查询支持 (lat/lng)
-- 4. 时间范围查询优化 (created_at, departure_date)

-- 数据类型选择:
-- 1. UUID 作为主键，避免ID泄露
-- 2. JSONB 存储灵活的配置和偏好数据
-- 3. DECIMAL 用于精确的金钱计算
-- 4. TIMESTAMP WITH TIME ZONE 统一时区处理

-- 安全考虑:
-- 1. 密码只存储哈希值
-- 2. 邮箱和用户名唯一性约束
-- 3. 评分字段范围检查约束
-- 4. 敏感操作记录审计日志

-- 性能优化:
-- 1. 合理的索引策略
-- 2. 向量检索优化 (IVFFlat索引)
-- 3. 分区准备 (按日期分区用于大数据量场景)

-- 扩展性:
-- 1. JSON字段支持灵活扩展
-- 2. 模块化设计便于后续添加新功能
-- 3. 标准化命名规范便于维护

-- =============================================================================
-- 初始化完成
-- =============================================================================