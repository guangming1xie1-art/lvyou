"""
JWT Token generation and verification
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..utils.logger import app_logger
from ..config import settings


class JWTHandler:
    """Handler for JWT token operations"""
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256"
    ):
        self.secret_key = secret_key or settings.jwt_secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(
        self,
        user_id: str,
        username: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode = {
            "sub": user_id,
            "username": username,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        app_logger.debug(f"Created access token for user {user_id}")
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str, username: str) -> str:
        """Create JWT refresh token (longer expiration)"""
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        to_encode = {
            "sub": user_id,
            "username": username,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        app_logger.debug(f"Created refresh token for user {user_id}")
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            app_logger.warning(f"Token verification failed: {e}")
            raise ValueError("Invalid or expired token")
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token without verification (for debugging)"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_signature": False})
            return payload
        except JWTError as e:
            app_logger.error(f"Token decode failed: {e}")
            raise
    
    def get_user_id_from_token(self, token: str) -> str:
        """Extract user ID from token"""
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token: no user ID")
        return user_id
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)


# Global JWT handler instance
jwt_handler = JWTHandler()
