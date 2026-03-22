"""
admin-agent 配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "admin-agent"
    app_version: str = "1.0.0"
    debug: bool = False
    
    server_host: str = "0.0.0.0"
    server_port: int = 8091
    
    database_url: Optional[str] = None
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "travel_assistant"
    db_user: str = "postgres"
    db_password: str = "postgres"
    
    faiss_index_path: str = "./data/faiss"
    
    embedding_model: str = "text-embedding-ada-002"
    openai_api_key: Optional[str] = None
    
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    @property
    def async_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
