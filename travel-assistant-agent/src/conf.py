"""
配置管理模块
使用 Pydantic Settings 管理环境变量配置
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Version(BaseSettings):
    """版本信息配置"""
    langchain_version: str = "1.0.0"
    langgraph_version: str = "1.0.0"
    deepagent_version: str = "0.2.7"
    pydantic_version: str = "2.5.0"
    python_jose_version: str = "3.3.0"
    redis_version: str = "5.0.0"
    httpx_version: str = "0.26.0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_delimiter=",",
    )

    # Version
    version: Version = Version()

    # Application
    app_name: str = Field(default="travel-assistant-agent", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # ============ LLM Provider API Keys ============
    # DeepSeek (便宜层主力)
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    # 阿里云通义千问 (标准层)
    dashscope_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    # 智谱 AI GLM
    zhipu_api_key: str = Field(default="", alias="ZHIPU_API_KEY")
    # OpenAI 兼容
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    # Anthropic Claude (强力层)
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # ============ LLM Tier Strategy ============
    # 便宜层默认提供商
    llm_cheap_provider: str = Field(
        default="deepseek",
        alias="LLM_CHEAP_PROVIDER"
    )
    # 标准层默认提供商
    llm_standard_provider: str = Field(
        default="qwen-turbo",
        alias="LLM_STANDARD_PROVIDER"
    )
    # 强力层默认提供商
    llm_power_provider: str = Field(
        default="claude",
        alias="LLM_POWER_PROVIDER"
    )
    # LLM 通用参数
    llm_temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=4096, alias="LLM_MAX_TOKENS")

    # ============ Vector Store Configuration ============
    vector_store_type: str = Field(default="faiss", alias="VECTOR_STORE_TYPE")
    vector_store_path: str = Field(default="E:/lvyou/lvyou/travel-assistant-agent/data/vector_store", alias="VECTOR_STORE_PATH")
    vector_dimension: int = Field(default=1536, alias="VECTOR_DIMENSION")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_api_key: str = Field(default="", alias="EMBEDDING_API_KEY")
    embedding_base_url: str = Field(default="", alias="EMBEDDING_BASE_URL")
    hybrid_search_enabled: bool = Field(default=True, alias="HYBRID_SEARCH_ENABLED")
    top_k_rerank: int = Field(default=5, alias="TOP_K_RERANK")
    hybrid_search_vector_weight: float = Field(default=0.6, alias="HYBRID_SEARCH_VECTOR_WEIGHT")
    hybrid_search_bm25_weight: float = Field(default=0.4, alias="HYBRID_SEARCH_BM25_WEIGHT")

    # ============ Prompt Cache Configuration ============
    prompt_cache_enabled: bool = Field(default=True, alias="PROMPT_CACHE_ENABLED")
    prompt_cache_dir: str = Field(default=".prompt_cache", alias="PROMPT_CACHE_DIR")
    system_prompt_cache_ttl: int = Field(default=86400, alias="SYSTEM_PROMPT_CACHE_TTL")
    tool_definitions_cache_ttl: int = Field(default=86400, alias="TOOL_DEFINITIONS_CACHE_TTL")
    rag_context_cache_ttl: int = Field(default=3600, alias="RAG_CONTEXT_CACHE_TTL")

    # ============ Cache TTL Configuration ============
    cache_ttl_search: int = Field(default=3600, alias="CACHE_TTL_SEARCH")
    cache_ttl_recommend: int = Field(default=21600, alias="CACHE_TTL_RECOMMEND")
    cache_ttl_rag: int = Field(default=3600, alias="CACHE_TTL_RAG")
    cache_ttl_booking: int = Field(default=1800, alias="CACHE_TTL_BOOKING")
    cache_ttl_user_prefs: int = Field(default=86400, alias="CACHE_TTL_USER_PREFS")

    # ============ Legacy Claude API (保留兼容性) ============
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        alias="CLAUDE_MODEL"
    )
    claude_max_tokens: int = Field(default=4096, alias="CLAUDE_MAX_TOKENS")
    claude_temperature: float = Field(default=0.7, alias="CLAUDE_TEMPERATURE")

    # PostgreSQL
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/travel_assistant",
        alias="DATABASE_URL"
    )
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="travel_assistant", alias="DB_NAME")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="postgres", alias="DB_PASSWORD")

    # Backend API
    backend_api_url: str = Field(
        default="http://localhost:3000/api",
        alias="BACKEND_API_URL"
    )

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed origins for CORS"
    )

    # MCP (Model Context Protocol)
    mcp_enabled: bool = Field(default=True, alias="MCP_ENABLED")
    mcp_server_url: str = Field(
        default="http://localhost:8765",
        alias="MCP_SERVER_URL"
    )
    mcp_transport: str = Field(default="stdio", alias="MCP_TRANSPORT")

    # Java API
    java_api_url: str = Field(
        default="http://localhost:9000",
        alias="JAVA_API_URL"
    )
    java_api_base_url: str = Field(
        default="http://localhost:9000/api",
        alias="JAVA_API_BASE_URL"
    )
    java_api_timeout: int = Field(default=30, alias="JAVA_API_TIMEOUT")
    java_api_max_retries: int = Field(default=3, alias="JAVA_API_MAX_RETRIES")
    java_api_auth_token: str = Field(default="", alias="JAVA_API_AUTH_TOKEN")
    
    # MCP Protocol
    mcp_protocol: str = Field(
        default="http",
        alias="MCP_PROTOCOL"
    )
    mcp_server_url: str = Field(
        default="http://localhost:8080/mcp",
        alias="MCP_SERVER_URL"
    )

    # DeepAgent Configuration
    deepagent_enabled: bool = Field(default=True, alias="DEEPAGENT_ENABLED")
    # DeepAgent 使用的模型（可配置为 provider:model 格式，如 "claude:claude-3-5-sonnet"）
    deepagent_search_model: str = Field(
        default="claude",
        alias="DEEPAGENT_SEARCH_MODEL"
    )
    deepagent_recommend_model: str = Field(
        default="claude",
        alias="DEEPAGENT_RECOMMEND_MODEL"
    )
    # DeepAgent tier（搜索和推荐通常需要标准或强力层）
    deepagent_search_tier: str = Field(
        default="standard",
        alias="DEEPAGENT_SEARCH_TIER"
    )
    deepagent_recommend_tier: str = Field(
        default="standard",
        alias="DEEPAGENT_RECOMMEND_TIER"
    )
    deepagent_temperature: float = Field(default=0.3, alias="DEEPAGENT_TEMPERATURE")
    deepagent_max_tokens: int = Field(default=4096, alias="DEEPAGENT_MAX_TOKENS")

    # Workflow Configuration
    workflow_max_retries: int = Field(default=2, alias="WORKFLOW_MAX_RETRIES")
    workflow_retry_delay: float = Field(default=1.0, alias="WORKFLOW_RETRY_DELAY")
    workflow_quality_threshold: float = Field(default=0.6, alias="WORKFLOW_QUALITY_THRESHOLD")

    # JWT Authentication
    jwt_secret_key: str = Field(
        default="your-super-secret-key-change-in-production-32bytes",
        alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # Security
    require_https: bool = Field(default=False, alias="REQUIRE_HTTPS")
    min_password_length: int = Field(default=8, alias="MIN_PASSWORD_LENGTH")
    require_special_chars: bool = Field(default=True, alias="REQUIRE_SPECIAL_CHARS")

    # Redis Cache
    redis_enabled: bool = Field(default=True, alias="REDIS_ENABLED")
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    redis_max_connections: int = Field(default=50, alias="REDIS_MAX_CONNECTIONS")

    # Performance
    enable_gzip: bool = Field(default=True, alias="ENABLE_GZIP")
    gzip_min_size: int = Field(default=1000, alias="GZIP_MIN_SIZE")
    slow_request_threshold: float = Field(default=1.0, alias="SLOW_REQUEST_THRESHOLD")
    db_pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")

    # ============ MCP (Model Context Protocol) V2 ============
    mcp_v2_enabled: bool = Field(default=True, alias="MCP_V2_ENABLED")
    mcp_v2_tools_enabled: bool = Field(default=True, alias="MCP_V2_TOOLS_ENABLED")
    mcp_v2_resources_enabled: bool = Field(default=True, alias="MCP_V2_RESOURCES_ENABLED")
    mcp_v2_max_websockets: int = Field(default=100, alias="MCP_V2_MAX_WEBSOCKETS")
    mcp_v2_request_timeout: float = Field(default=30.0, alias="MCP_V2_REQUEST_TIMEOUT")



    # ============ Memory System Configuration ============
    # 记忆系统配置
    memory_system_enabled: bool = Field(default=True, alias="MEMORY_SYSTEM_ENABLED")
    memory_gateway_enabled: bool = Field(default=True, alias="MEMORY_GATEWAY_ENABLED")
    memory_retriever_enabled: bool = Field(default=True, alias="MEMORY_RETRIEVER_ENABLED")
    
    # 长期记忆检索配置
    long_term_memory_enabled: bool = Field(default=True, alias="LONG_TERM_MEMORY_ENABLED")
    long_term_memory_top_k: int = Field(default=10, alias="LONG_TERM_MEMORY_TOP_K")
    long_term_memory_use_hybrid: bool = Field(default=True, alias="LONG_TERM_MEMORY_USE_HYBRID")
    
    # 记忆缓存配置
    memory_cache_enabled: bool = Field(default=True, alias="MEMORY_CACHE_ENABLED")
    memory_cache_ttl: int = Field(default=3600, alias="MEMORY_CACHE_TTL")
    memory_cache_max_size: int = Field(default=1000, alias="MEMORY_CACHE_MAX_SIZE")

    # ============ Query Rewrite Configuration ============
    # Query改写配置
    query_rewrite_enabled: bool = Field(default=True, alias="QUERY_REWRITE_ENABLED")
    query_rewrite_confidence_threshold: float = Field(default=0.7, alias="QUERY_REWRITE_CONFIDENCE_THRESHOLD")
    query_rewrite_use_local_model: bool = Field(default=True, alias="QUERY_REWRITE_USE_LOCAL_MODEL")
    query_rewrite_local_model: str = Field(default="qwen-7b", alias="QUERY_REWRITE_LOCAL_MODEL")
    query_rewrite_cloud_model: str = Field(default="gpt-4", alias="QUERY_REWRITE_CLOUD_MODEL")

    # ============ Session Management Configuration ============
    # 会话管理配置
    session_manager_enabled: bool = Field(default=True, alias="SESSION_MANAGER_ENABLED")
    session_max_tokens: int = Field(default=4000, alias="SESSION_MAX_TOKENS")
    session_window_strategy: str = Field(default="sliding_window", alias="SESSION_WINDOW_STRATEGY")
    session_compression_threshold: float = Field(default=0.8, alias="SESSION_COMPRESSION_THRESHOLD")
    session_reset_threshold: float = Field(default=0.95, alias="SESSION_RESET_THRESHOLD")

    # ============ Concurrency & Rate Limiting ============
    # Connection Pool
    connection_pool_max_connections: int = Field(default=100, alias="CONNECTION_POOL_MAX_CONNECTIONS")
    connection_pool_timeout: float = Field(default=30.0, alias="CONNECTION_POOL_TIMEOUT")
    connection_pool_idle_timeout: float = Field(default=300.0, alias="CONNECTION_POOL_IDLE_TIMEOUT")

    # Database Connection Pool
    db_connection_pool_enabled: bool = Field(default=True, alias="DB_CONNECTION_POOL_ENABLED")
    db_connection_pool_max: int = Field(default=20, alias="DB_CONNECTION_POOL_MAX")

    # API Connection Pool
    api_connection_pool_max: int = Field(default=100, alias="API_CONNECTION_POOL_MAX")
    api_connection_pool_timeout: float = Field(default=10.0, alias="API_CONNECTION_POOL_TIMEOUT")
    api_connection_pool_max_retries: int = Field(default=3, alias="API_CONNECTION_POOL_MAX_RETRIES")

    # Memory Pool
    memory_pool_enabled: bool = Field(default=True, alias="MEMORY_POOL_ENABLED")
    memory_pool_max_size: int = Field(default=100, alias="MEMORY_POOL_MAX_SIZE")
    memory_pool_item_size_limit: int = Field(default=10*1024*1024, alias="MEMORY_POOL_ITEM_SIZE_LIMIT")

    # Rate Limiting
    rate_limiting_enabled: bool = Field(default=True, alias="RATE_LIMITING_ENABLED")
    rate_limit_default_rate: float = Field(default=1000.0, alias="RATE_LIMIT_DEFAULT_RATE")
    rate_limit_default_burst: float = Field(default=2000.0, alias="RATE_LIMIT_DEFAULT_BURST")
    rate_limit_per_user_rate: float = Field(default=10.0, alias="RATE_LIMIT_PER_USER_RATE")
    rate_limit_per_user_burst: float = Field(default=20.0, alias="RATE_LIMIT_PER_USER_BURST")

    # Streaming
    streaming_enabled: bool = Field(default=True, alias="STREAMING_ENABLED")
    streaming_buffer_size: int = Field(default=1000, alias="STREAMING_BUFFER_SIZE")
    streaming_flush_interval: float = Field(default=1.0, alias="STREAMING_FLUSH_INTERVAL")
    streaming_heartbeat_interval: float = Field(default=30.0, alias="STREAMING_HEARTBEAT_INTERVAL")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
