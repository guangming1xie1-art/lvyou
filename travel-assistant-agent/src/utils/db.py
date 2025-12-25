"""
数据库连接管理
使用 SQLAlchemy 创建 PostgreSQL 连接
"""
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from config import settings
from utils.logger import app_logger


class DatabaseManager:
    def __init__(self):
        self.engine: Engine | None = None

    def init(self):
        try:
            self.engine = create_engine(
                settings.get_database_url(),
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
            app_logger.info("Database engine initialized")
        except Exception as e:
            app_logger.error(f"Failed to initialize database engine: {e}")
            raise

    def health_check(self) -> bool:
        if not self.engine:
            return False
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            app_logger.warning(f"Database health check failed: {e}")
            return False

    def close(self):
        if self.engine:
            self.engine.dispose()
            app_logger.info("Database engine disposed")


db_manager = DatabaseManager()
