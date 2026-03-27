"""
Agent认证路由

代理前端认证请求到Java auth-service
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
from utils.auth_api_client import auth_api_client
from auth.models import (
    UserRegisterRequest,
    TokenRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    LoginResponse
)

from utils.structured_logger import get_app_logger, get_error_logger

logger = get_app_logger(__name__)
error_logger = get_error_logger()

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest):
    """
    代理注册请求到Java auth-service
    
    前端调用: POST /api/auth/register
    Agent转发: POST http://java:8080/api/auth/register
    """
    try:
        logger.info(
            "User registration attempt",
            extra={
                "extra_username": user_data.username,
                "extra_email": user_data.email
            }
        )
        
        # 转发到Java auth-service
        result = await auth_api_client.register(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            confirm_password=user_data.confirm_password
        )
        
        logger.info(
            "User registration successful",
            extra={
                "extra_username": user_data.username
            }
        )
        
        # 处理Java返回的数据结构
        # API客户端已经处理了ApiResponse格式，直接返回结果
        return result
        
    except Exception as e:
        error_logger.error(
            "User registration failed",
            exc_info=True,
            extra={
                "extra_username": user_data.username,
                "extra_error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(credentials: TokenRequest):
    """
    代理登录请求到Java auth-service
    
    前端调用: POST /api/auth/login
           { "username": "user", "password": "pass" }
    
    Agent转发: POST http://java:8080/api/auth/login
    
    Java返回: { "code": 0, "data": { "user": {...}, "tokens": {...} } }
    
    Agent返回给前端: { "user": {...}, "tokens": {...} }
    """
    try:
        logger.info(
            "User login attempt",
            extra={
                "extra_username": credentials.username
            }
        )
        
        # 转发到Java auth-service
        result = await auth_api_client.login(
            username=credentials.username,
            password=credentials.password
        )
        
        logger.info(
            "User login successful",
            extra={
                "extra_username": credentials.username
            }
        )
        
        # 处理Java返回的数据结构
        # API客户端已经处理了ApiResponse格式，直接返回结果
        return result
        
    except Exception as e:
        error_logger.error(
            "User login failed",
            exc_info=True,
            extra={
                "extra_username": credentials.username,
                "extra_error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """
    代理刷新token请求到Java auth-service
    
    前端调用: POST /api/auth/refresh
           { "refresh_token": "..." }
    
    Agent转发: POST http://java:8080/api/auth/refresh
    
    Java返回token信息
    """
    try:
        logger.info("Token refresh request received")
        
        result = await auth_api_client.refresh_token(request.refresh_token)
        
        logger.info("Token refresh successful")
        
        # 处理Java返回的数据结构
        # API客户端已经处理了ApiResponse格式，直接返回结果
        return result
        
    except Exception as e:
        error_logger.error(
            "Token refresh failed",
            exc_info=True,
            extra={
                "extra_error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me")
async def get_current_user(authorization: str = None):
    """
    代理获取当前用户请求到Java auth-service
    
    前端调用: GET /api/auth/me
            Header: Authorization: Bearer <token>
    
    Agent转发: GET http://java:8080/api/auth/me
               Header: Authorization: Bearer <token>
    
    Java返回用户信息
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization token"
            )
        
        token = authorization.replace("Bearer ", "")
        logger.info("Get current user request received")
        
        result = await auth_api_client.get_current_user(token)
        
        logger.info("Get current user successful")
        
        # 处理Java返回的数据结构
        # API客户端已经处理了ApiResponse格式，直接返回结果
        return result
        
    except Exception as e:
        error_logger.error(
            "Get current user failed",
            exc_info=True,
            extra={
                "extra_error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout(authorization: str = None):
    """
    代理登出请求到Java auth-service，Java服务会将Token加入黑名单
    
    前端调用: POST /api/auth/logout
            Header: Authorization: Bearer <token>
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization token"
            )
        
        token = authorization.replace("Bearer ", "")
        logger.info("Logout request received")
        
        # 转发到 Java auth-service（Java 会在数据库中记录黑名单）
        result = await auth_api_client.logout(token)
        
        logger.info("Logout successful")
        
        return result
        
    except Exception as e:
        error_logger.error(
            "Logout failed",
            exc_info=True,
            extra={
                "extra_error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_BAD_REQUEST,
            detail=str(e)
        )