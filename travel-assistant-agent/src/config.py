"""
配置管理模块
使用 Pydantic Settings 管理环境变量配置
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_delimiter=",",
    )

    # Application
    app_name: str = Field(default="travel-assistant-agent", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Claude API
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
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
