"""
Authentication API routes
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from .token import jwt_handler
from .models import (
    User,
    UserCreate,
    UserRegisterRequest,
    TokenRequest,
    TokenResponse,
    UserResponse,
    LoginResponse,
    RefreshTokenRequest
)
from .dependencies import get_current_user
from utils.logger import app_logger
from conf import settings


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user information
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should discard tokens)
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Success message
    """
    # In a stateful implementation, you might want to:
    # - Add the token to a blacklist/revocation list
    # - Clear session data
    # - Log the logout event
    
    app_logger.info(f"User logged out: {current_user.username}")
    
    return {"message": "Successfully logged out"}
