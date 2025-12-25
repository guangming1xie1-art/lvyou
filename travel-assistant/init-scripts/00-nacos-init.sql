-- Nacos Configuration Database Setup
-- This script creates the database and tables required for Nacos with PostgreSQL

-- Create nacos_config database
\c nacos_config;

-- Create config_info table
CREATE TABLE IF NOT EXISTS config_info (
    id BIGSERIAL PRIMARY KEY,
    data_id VARCHAR(255) NOT NULL,
    group_id VARCHAR(128) NOT NULL,
    content TEXT NOT NULL,
    md5 VARCHAR(32),
    gmt_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gmt_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    src_user TEXT,
    src_ip VARCHAR(50),
    app_name VARCHAR(128),
    tenant_id VARCHAR(128) DEFAULT '',
    c_desc VARCHAR(256),
    c_use VARCHAR(64),
    effect VARCHAR(32),
    type VARCHAR(64),
    c_schema TEXT,
    encrypted_data_key TEXT
);

-- Create config_info_aggr table
CREATE TABLE IF NOT EXISTS config_info_aggr (
    id BIGSERIAL PRIMARY KEY,
    data_id VARCHAR(255) NOT NULL,
    group_id VARCHAR(128) NOT NULL,
    datum_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    gmt_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (data_id, group_id, datum_id)
);

-- Create config_info_beta table
CREATE TABLE IF NOT EXISTS config_info_beta (
    id BIGSERIAL PRIMARY KEY,
    data_id VARCHAR(255) NOT NULL,
    group_id VARCHAR(128) NOT NULL,
    content TEXT NOT NULL,
    beta_ips VARCHAR(1024),
    md5 VARCHAR(32),
    gmt_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gmt_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    src_user TEXT,
    src_ip VARCHAR(50),
    app_name VARCHAR(128),
    tenant_id VARCHAR(128) DEFAULT '',
    encrypted_data_key TEXT
);

-- Create config_info_tag table
CREATE TABLE IF NOT EXISTS config_info_tag (
    id BIGSERIAL PRIMARY KEY,
    data_id VARCHAR(255) NOT NULL,
    group_id VARCHAR(128) NOT NULL,
    tag_id VARCHAR(128) NOT NULL,
    content TEXT NOT NULL,
    md5 VARCHAR(32),
    gmt_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gmt_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    src_user TEXT,
    src_ip VARCHAR(50),
    app_name VARCHAR(128),
    tenant_id VARCHAR(128) DEFAULT '',
    encrypted_data_key TEXT
);

-- Create config_tags_relation table
CREATE TABLE IF NOT EXISTS config_tags_relation (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    tag_name VARCHAR(128) NOT NULL,
    tag_type VARCHAR(64),
    data_id VARCHAR(255) NOT NULL,
    group_id VARCHAR(128) NOT NULL,
    tenant_id VARCHAR(128) DEFAULT '',
    nid BIGSERIAL NOT NULL,
    UNIQUE (tag_name, tag_type, data_id, group_id, tenant_id)
);

-- Create group_capacity table
CREATE TABLE IF NOT EXISTS group_capacity (
    id BIGSERIAL PRIMARY KEY,
    group_id VARCHAR(128) NOT NULL,
    quota INT NOT NULL DEFAULT 0,
    usage INT NOT NULL DEFAULT 0,
    max_size INT NOT NULL DEFAULT 0,
    max_aggr_count INT NOT NULL DEFAULT 0,
    max_aggr_size INT NOT NULL DEFAULT 0,
    max_history_count INT NOT NULL DEFAULT 0,
    gmt_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gmt_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tenant_capacity table
CREATE TABLE IF NOT EXISTS tenant_capacity (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    quota INT NOT NULL DEFAULT 0,
    usage INT NOT NULL DEFAULT 0,
    max_size INT NOT NULL DEFAULT 0,
    max_aggr_count INT NOT NULL DEFAULT 0,
    max_aggr_size INT NOT NULL DEFAULT 0,
    max_history_count INT NOT NULL DEFAULT 0,
    gmt_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gmt_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tenant_info table
CREATE TABLE IF NOT EXISTS tenant_info (
    id BIGSERIAL PRIMARY KEY,
   kp VARCHAR(128) NOT NULL,
    tenant_id VARCHAR(128) NOT NULL,
    tenant_name VARCHAR(256) DEFAULT '',
    tenant_desc VARCHAR(256),
    create_resource VARCHAR(256) DEFAULT '',
    modify_resource VARCHAR(256) DEFAULT '',
    gmt_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gmt_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(500) NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1
);

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    role VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL,
    PRIMARY KEY (role, username)
);

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    role VARCHAR(50) NOT NULL,
    resource VARCHAR(128) NOT NULL,
    action VARCHAR(8) NOT NULL,
    PRIMARY KEY (role, resource, action)
);

-- Create user_role_idx table
CREATE TABLE IF NOT EXISTS user_role_idx (
    user_name VARCHAR(128) NOT NULL,
    role_name VARCHAR(128) NOT NULL,
    PRIMARY KEY (user_name, role_name)
);

-- Create role_permission_idx table
CREATE TABLE IF NOT EXISTS role_permission_idx (
    role_name VARCHAR(128) NOT NULL,
    resource VARCHAR(128) NOT NULL,
    action VARCHAR(8) NOT NULL,
    PRIMARY KEY (role_name, resource, action)
);

-- Create his_config_info table
CREATE TABLE IF NOT EXISTS his_config_info (
    id BIGINT NOT NULL,
    nid BIGINT NOT NULL,
    data_id VARCHAR(255) NOT NULL,
    group_id VARCHAR(128) NOT NULL,
    content TEXT NOT NULL,
    md5 VARCHAR(32),
    gmt_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gmt_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    src_user TEXT,
    src_ip VARCHAR(50),
    app_name VARCHAR(128),
    tenant_id VARCHAR(128) DEFAULT '',
    encrypted_data_key TEXT,
    PRIMARY KEY (nid)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_config_info_data_id ON config_info(data_id);
CREATE INDEX IF NOT EXISTS idx_config_info_group_id ON config_info(group_id);
CREATE INDEX IF NOT EXISTS idx_config_info_tenant_id ON config_info(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenant_info_tenant_id ON tenant_info(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_enabled ON users(enabled);

-- Insert default admin user (password: nacos)
INSERT INTO users (username, password, enabled) VALUES ('nacos', '$2a$10$Eu4/Z8OJ6V6fmfv2F1E5pe4T9BK7r7NK7F5Y5Z5Z5Z5Z5Z5Z5Z5Z5', 1)
ON CONFLICT (username) DO NOTHING;
INSERT INTO roles (role, username) VALUES ('ROLE_ADMIN', 'nacos')
ON CONFLICT (role, username) DO NOTHING;
