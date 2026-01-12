"""
Authentication module for JWT-based user authentication
"""
from .token import JWTHandler
from .models import (
    User,
    UserRegisterRequest,
    TokenRequest,
    TokenResponse,
    UserResponse,
    UserCreate
)
from .dependencies import get_token, get_current_user, get_current_active_user

__all__ = [
    "JWTHandler",
    "User",
    "UserRegisterRequest",
    "TokenRequest",
    "TokenResponse",
    "UserResponse",
    "UserCreate",
    "get_token",
    "get_current_user",
    "get_current_active_user"
]
