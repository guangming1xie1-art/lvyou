"""
数据库连接管理
使用 SQLAlchemy 创建 PostgreSQL 连接
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4
from sqlalchemy import create_engine, text, Table, MetaData, Column, String, Boolean, DateTime
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
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow
            )
            app_logger.info("Database engine initialized")
            self._create_tables()
        except Exception as e:
            app_logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            with self.engine.connect() as conn:
                # Create users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(36) PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                """))
                
                # Create audit_logs table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36),
                        action VARCHAR(255) NOT NULL,
                        endpoint VARCHAR(255),
                        method VARCHAR(10),
                        params TEXT,
                        result VARCHAR(50),
                        error_message TEXT,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """))
                
                # Create indexes for users table
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_email 
                    ON users(email)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_username 
                    ON users(username)
                """))
                
                # Create indexes for audit_logs table
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id 
                    ON audit_logs(user_id)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at 
                    ON audit_logs(created_at)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
                    ON audit_logs(action)
                """))
                
                conn.commit()
                app_logger.info("Database tables and indexes created or verified")
        except Exception as e:
            app_logger.error(f"Failed to create tables: {e}")
            # Don't raise - tables might already exist with different schema

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
    
    # ============== User Management ==============
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        user_id = str(uuid4())
        now = datetime.utcnow()
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (id, username, email, hashed_password, is_active, created_at, updated_at)
                VALUES (:id, :username, :email, :password, :is_active, :created_at, :updated_at)
            """), {
                "id": user_id,
                "username": user_data["username"],
                "email": user_data["email"],
                "password": user_data["password"],
                "is_active": True,
                "created_at": now,
                "updated_at": now
            })
            conn.commit()
        
        return {
            "id": user_id,
            "username": user_data["username"],
            "email": user_data["email"],
            "is_active": True,
            "created_at": now,
            "last_login": None
        }
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, username, email, hashed_password, is_active, created_at, last_login
                FROM users WHERE id = :user_id
            """), {"user_id": user_id})
            
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "hashed_password": row[3],
                    "is_active": row[4],
                    "created_at": row[5],
                    "last_login": row[6]
                }
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, username, email, hashed_password, is_active, created_at, last_login
                FROM users WHERE username = :username
            """), {"username": username})
            
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "hashed_password": row[3],
                    "is_active": row[4],
                    "created_at": row[5],
                    "last_login": row[6]
                }
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, username, email, hashed_password, is_active, created_at, last_login
                FROM users WHERE email = :email
            """), {"email": email})
            
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "hashed_password": row[3],
                    "is_active": row[4],
                    "created_at": row[5],
                    "last_login": row[6]
                }
        return None
    
    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login time"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                UPDATE users SET last_login = :now WHERE id = :user_id
            """), {"user_id": user_id, "now": datetime.utcnow()})
            conn.commit()
    
    # ============== Audit Logging ==============
    
    async def create_audit_log(self, audit_data: Dict[str, Any]) -> None:
        """Create an audit log entry"""
        import json
        
        log_id = str(uuid4())
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO audit_logs (id, user_id, action, endpoint, method, params, result, error_message, ip_address, user_agent, metadata)
                VALUES (:id, :user_id, :action, :endpoint, :method, :params, :result, :error_message, :ip_address, :user_agent, :metadata)
            """), {
                "id": log_id,
                "user_id": audit_data.get("user_id"),
                "action": audit_data["action"],
                "endpoint": audit_data.get("endpoint"),
                "method": audit_data.get("method"),
                "params": json.dumps(audit_data.get("params", {})),
                "result": audit_data.get("result", "success"),
                "error_message": audit_data.get("error_message"),
                "ip_address": audit_data.get("ip_address"),
                "user_agent": audit_data.get("user_agent"),
                "metadata": json.dumps(audit_data.get("metadata", {}))
            })
            conn.commit()
    
    async def get_user_audit_logs(
        self, user_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit logs for a user"""
        import json
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, user_id, action, endpoint, method, params, result, error_message, ip_address, user_agent, created_at, metadata
                FROM audit_logs
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """), {"user_id": user_id, "limit": limit, "offset": offset})
            
            logs = []
            for row in result.fetchall():
                logs.append({
                    "id": row[0],
                    "user_id": row[1],
                    "action": row[2],
                    "endpoint": row[3],
                    "method": row[4],
                    "params": json.loads(row[5]) if row[5] else {},
                    "result": row[6],
                    "error_message": row[7],
                    "ip_address": row[8],
                    "user_agent": row[9],
                    "created_at": row[10],
                    "metadata": json.loads(row[11]) if row[11] else {}
                })
            
            return logs
    
    async def get_security_events(
        self, severity: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get security events from audit logs"""
        import json
        
        query = """
            SELECT id, user_id, action, endpoint, method, params, result, error_message, ip_address, user_agent, created_at, metadata
            FROM audit_logs
            WHERE action LIKE 'security_%'
        """
        
        if severity:
            query += " AND JSON_EXTRACT(metadata, '$.severity') = :severity"
        
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        
        with self.engine.connect() as conn:
            params = {"limit": limit, "offset": offset}
            if severity:
                params["severity"] = severity
            
            result = conn.execute(text(query), params)
            
            logs = []
            for row in result.fetchall():
                logs.append({
                    "id": row[0],
                    "user_id": row[1],
                    "action": row[2],
                    "endpoint": row[3],
                    "method": row[4],
                    "params": json.loads(row[5]) if row[5] else {},
                    "result": row[6],
                    "error_message": row[7],
                    "ip_address": row[8],
                    "user_agent": row[9],
                    "created_at": row[10],
                    "metadata": json.loads(row[11]) if row[11] else {}
                })
            
            return logs


db_manager = DatabaseManager()
