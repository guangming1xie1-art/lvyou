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
    vector_store_path: str = Field(default="./data/vector_store", alias="VECTOR_STORE_PATH")
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
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS"
    )

    # MCP (Model Context Protocol)
    mcp_enabled: bool = Field(default=True, alias="MCP_ENABLED")
    mcp_server_url: str = Field(
        default="http://localhost:8765",
        alias="MCP_SERVER_URL"
    )
    mcp_transport: str = Field(default="stdio", alias="MCP_TRANSPORT")

    # Java API
    java_api_base_url: str = Field(
        default="http://localhost:8080/api",
        alias="JAVA_API_BASE_URL"
    )
    java_api_timeout: int = Field(default=30, alias="JAVA_API_TIMEOUT")
    java_api_max_retries: int = Field(default=3, alias="JAVA_API_MAX_RETRIES")
    java_api_auth_token: str = Field(default="", alias="JAVA_API_AUTH_TOKEN")

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
        default="your-super-secret-key-change-in-production",
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
