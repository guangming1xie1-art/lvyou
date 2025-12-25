-- Nacos 配置数据库初始化脚本
-- 创建 nacos_config 数据库（如果不存在会自动创建）

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    nickname VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    avatar VARCHAR(500),
    status INTEGER DEFAULT 1,
    role VARCHAR(20) DEFAULT 'USER',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT,
    update_by BIGINT,
    deleted INTEGER DEFAULT 0
);

-- 创建旅游请求表
CREATE TABLE IF NOT EXISTS t_travel_request (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    destination VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget DECIMAL(12, 2),
    traveler_count INTEGER DEFAULT 1,
    travel_mode VARCHAR(20),
    accommodationPreference VARCHAR(200),
    special_requirements TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT,
    update_by BIGINT,
    deleted INTEGER DEFAULT 0
);

-- 创建旅游计划表
CREATE TABLE IF NOT EXISTS t_travel_plan (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    travel_request_id BIGINT,
    destination VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days INTEGER,
    total_budget DECIMAL(12, 2),
    actual_cost DECIMAL(12, 2),
    itinerary TEXT,
    transportation TEXT,
    accommodation TEXT,
    remarks TEXT,
    status VARCHAR(20) DEFAULT 'DRAFT',
    ai_generated_plan TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT,
    update_by BIGINT,
    deleted INTEGER DEFAULT 0
);

-- 创建订单表
CREATE TABLE IF NOT EXISTS t_order (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    travel_plan_id BIGINT,
    order_no VARCHAR(50) NOT NULL UNIQUE,
    order_type VARCHAR(20) NOT NULL,
    supplier_name VARCHAR(100),
    supplier_order_no VARCHAR(100),
    departure VARCHAR(200),
    destination VARCHAR(200),
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP,
    contact_name VARCHAR(50),
    contact_phone VARCHAR(20),
    amount DECIMAL(12, 2),
    payment_status VARCHAR(20) DEFAULT 'UNPAID',
    status VARCHAR(20) DEFAULT 'PENDING',
    cancel_reason VARCHAR(500),
    remarks TEXT,
    details TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    create_by BIGINT,
    update_by BIGINT,
    deleted INTEGER DEFAULT 0
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_travel_request_user_id ON t_travel_request(user_id);
CREATE INDEX IF NOT EXISTS idx_travel_request_status ON t_travel_request(status);
CREATE INDEX IF NOT EXISTS idx_travel_plan_user_id ON t_travel_plan(user_id);
CREATE INDEX IF NOT EXISTS idx_travel_plan_status ON t_travel_plan(status);
CREATE INDEX IF NOT EXISTS idx_order_user_id ON t_order(user_id);
CREATE INDEX IF NOT EXISTS idx_order_order_no ON t_order(order_no);
CREATE INDEX IF NOT EXISTS idx_order_status ON t_order(status);
CREATE INDEX IF NOT EXISTS idx_order_payment_status ON t_order(payment_status);
