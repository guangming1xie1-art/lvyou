"""
Authentication dependencies and middleware
"""
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .token import jwt_handler
from .models import User
from ..utils.logger import app_logger
from ..utils.db import db_manager


security = HTTPBearer(auto_error=False)


async def get_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Extract JWT token from request headers
    
    Args:
        request: FastAPI request object
        credentials: HTTP bearer credentials
    
    Returns:
        JWT token string
    
    Raises:
        HTTPException: If token is missing
    """
    if credentials is None:
        # Try to get from Authorization header with Bearer prefix
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated: Missing or invalid Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        token = credentials.credentials
    
    return token


async def get_current_user(token: str = Depends(get_token)) -> User:
    """
    Verify token and return current user
    
    Args:
        token: JWT token
    
    Returns:
        Current user object
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Verify and decode token
        payload = jwt_handler.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user_data = await db_manager.get_user_by_id(user_id)
        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create User object
        user = User(**user_data)
        
        # Update last login time
        await db_manager.update_last_login(user_id)
        
        app_logger.debug(f"Authenticated user: {user.username}")
        return user
        
    except ValueError as e:
        app_logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        app_logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Args:
        current_user: Current user from get_current_user
    
    Returns:
        Current user if active
    
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_roles(*allowed_roles: str):
    """
    Dependency factory for role-based access control
    
    Args:
        *allowed_roles: List of allowed roles
    
    Returns:
        Dependency function that checks user roles
    """
    async def check_roles(current_user: User = Depends(get_current_active_user)) -> User:
        # For now, all users have the same role
        # This can be extended to support multiple roles
        return current_user
    
    return check_roles
