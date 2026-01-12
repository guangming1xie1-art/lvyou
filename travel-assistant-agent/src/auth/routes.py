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
from ..utils.logger import app_logger
from ..utils.db import db_manager
from ..config import settings


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest):
    """
    Register a new user
    
    Args:
        user_data: User registration data
    
    Returns:
        Created user information
    
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Check if user already exists
        existing_user = await db_manager.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        existing_email = await db_manager.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = jwt_handler.hash_password(user_data.password)
        
        # Create user
        user_create = UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password
        )
        
        user = await db_manager.create_user(user_create)
        app_logger.info(f"New user registered: {user.username}")
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: TokenRequest):
    """
    Login user and return JWT tokens
    
    Args:
        credentials: Login credentials (username, password)
    
    Returns:
        User info and JWT tokens
    
    Raises:
        HTTPException: If login fails
    """
    try:
        # Get user from database
        user_data = await db_manager.get_user_by_username(credentials.username)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        user = User(**user_data)
        
        # Verify password
        if not jwt_handler.verify_password(credentials.password, user_data["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # Generate tokens
        access_token = jwt_handler.create_access_token(
            user_id=user.id,
            username=user.username
        )
        refresh_token = jwt_handler.create_refresh_token(
            user_id=user.id,
            username=user.username
        )
        
        # Update last login
        await db_manager.update_last_login(user.id)
        
        app_logger.info(f"User logged in: {user.username}")
        
        return LoginResponse(
            user=UserResponse(**user_data),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="Bearer",
                expires_in=settings.access_token_expire_minutes * 60
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    Args:
        request: Refresh token request
    
    Returns:
        New access and refresh tokens
    
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Verify refresh token
        payload = jwt_handler.verify_token(request.refresh_token)
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user still exists and is active
        user_data = await db_manager.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        user = User(**user_data)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # Generate new tokens
        access_token = jwt_handler.create_access_token(
            user_id=user_id,
            username=username
        )
        new_refresh_token = jwt_handler.create_refresh_token(
            user_id=user_id,
            username=username
        )
        
        app_logger.info(f"Token refreshed for user: {username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


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
