"""
Java认证服务API客户端

用于代理前端认证请求到Java auth-service
"""
import httpx
from typing import Dict, Any, Optional
from conf import settings
from utils.structured_logger import get_app_logger, get_error_logger

logger = get_app_logger(__name__)
error_logger = get_error_logger()


class AuthAPIClient:
    """Java认证服务API客户端"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.java_api_base_url
        self.timeout = 10.0
    
    async def register(
        self, 
        username: str, 
        email: str, 
        password: str, 
        confirm_password: str
    ) -> Dict[str, Any]:
        """调用Java auth-service的register端点"""
        try:
            logger.info(
                "Calling Java auth-service register",
                extra={
                    "extra_username": username,
                    "extra_email": email,
                    "extra_service": "auth-service",
                    "extra_endpoint": "/auth/register"
                }
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/register",
                    json={
                        "username": username,
                        "email": email,
                        "password": password,
                        "confirm_password": confirm_password
                    },
                    timeout=self.timeout
                )
                
                if response.status_code not in [200, 201]:
                    error_data = response.json() if response.content else {"detail": f"HTTP {response.status_code}"}
                    # 检查Java API的响应格式
                    if isinstance(error_data, dict) and "data" in error_data:
                        # Java ApiResponse格式的响应
                        if error_data.get("code", 0) != 0:
                            raise Exception(error_data.get("message", f"Register failed: {response.text}"))
                    raise Exception(error_data.get("detail", error_data.get("message", f"Register failed: {response.text}")))
                
                result = response.json()
                logger.info(
                    "Java auth-service register successful",
                    extra={
                        "extra_username": username,
                        "extra_status_code": response.status_code
                    }
                )
                
                # 处理Java ApiResponse格式
                if isinstance(result, dict) and "data" in result:
                    if result.get("code", 0) == 0:
                        return result["data"]  # 返回data部分
                    else:
                        raise Exception(result.get("message", "Register failed"))
                
                return result
                
        except Exception as e:
            error_logger.error(
                "Java auth-service register failed",
                exc_info=True,
                extra={
                    "extra_username": username,
                    "extra_service": "auth-service",
                    "extra_error": str(e)
                }
            )
            raise
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """调用Java auth-service的login端点"""
        try:
            logger.info(
                "Calling Java auth-service login",
                extra={
                    "extra_username": username,
                    "extra_service": "auth-service",
                    "extra_endpoint": "/auth/login"
                }
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/login",
                    json={
                        "username": username,
                        "password": password
                    },
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        # 检查Java API的响应格式
                        if isinstance(error_data, dict) and "data" in error_data:
                            if error_data.get("code", 0) != 0:
                                raise Exception(error_data.get("message", f"Login failed: {response.text}"))
                        detail = error_data.get("detail") or error_data.get("message", f"Login failed: {response.text}")
                    except:
                        detail = f"Login failed: HTTP {response.status_code}"
                    raise Exception(detail)
                
                result = response.json()
                logger.info(
                    "Java auth-service login successful",
                    extra={
                        "extra_username": username,
                        "extra_status_code": response.status_code
                    }
                )
                
                # 处理Java ApiResponse格式
                if isinstance(result, dict) and "data" in result:
                    if result.get("code", 0) == 0:
                        return result["data"]  # 返回data部分
                    else:
                        raise Exception(result.get("message", "Login failed"))
                
                return result
                
        except Exception as e:
            error_logger.error(
                "Java auth-service login failed",
                exc_info=True,
                extra={
                    "extra_username": username,
                    "extra_service": "auth-service",
                    "extra_error": str(e)
                }
            )
            raise
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """调用Java auth-service的refresh端点"""
        try:
            logger.info(
                "Calling Java auth-service refresh",
                extra={
                    "extra_service": "auth-service",
                    "extra_endpoint": "/auth/refresh"
                }
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/refresh",
                    json={"refresh_token": refresh_token},
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {"detail": f"HTTP {response.status_code}"}
                    # 检查Java API的响应格式
                    if isinstance(error_data, dict) and "data" in error_data:
                        if error_data.get("code", 0) != 0:
                            raise Exception(error_data.get("message", f"Refresh failed: {response.text}"))
                    raise Exception(error_data.get("detail", f"Refresh failed: {response.text}"))
                
                result = response.json()
                logger.info(
                    "Java auth-service refresh successful",
                    extra={
                        "extra_status_code": response.status_code
                    }
                )
                
                # 处理Java ApiResponse格式
                if isinstance(result, dict) and "data" in result:
                    if result.get("code", 0) == 0:
                        return result["data"]  # 返回data部分
                    else:
                        raise Exception(result.get("message", "Refresh failed"))
                
                return result
                
        except Exception as e:
            error_logger.error(
                "Java auth-service refresh failed",
                exc_info=True,
                extra={
                    "extra_service": "auth-service",
                    "extra_error": str(e)
                }
            )
            raise
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """调用Java auth-service的/me端点"""
        try:
            logger.info(
                "Calling Java auth-service get current user",
                extra={
                    "extra_service": "auth-service",
                    "extra_endpoint": "/auth/me"
                }
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/auth/me",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {"detail": f"HTTP {response.status_code}"}
                    # 检查Java API的响应格式
                    if isinstance(error_data, dict) and "data" in error_data:
                        if error_data.get("code", 0) != 0:
                            raise Exception(error_data.get("message", f"Get user failed: {response.text}"))
                    raise Exception(error_data.get("detail", f"Get user failed: {response.text}"))
                
                result = response.json()
                logger.info(
                    "Java auth-service get current user successful",
                    extra={
                        "extra_status_code": response.status_code
                    }
                )
                
                # 处理Java ApiResponse格式
                if isinstance(result, dict) and "data" in result:
                    if result.get("code", 0) == 0:
                        return result["data"]  # 返回data部分
                    else:
                        raise Exception(result.get("message", "Get user failed"))
                
                return result
                
        except Exception as e:
            error_logger.error(
                "Java auth-service get current user failed",
                exc_info=True,
                extra={
                    "extra_service": "auth-service",
                    "extra_error": str(e)
                }
            )
            raise
    
    async def logout(self, token: str) -> Dict[str, Any]:
        """调用Java auth-service的logout端点"""
        try:
            logger.info(
                "Calling Java auth-service logout",
                extra={
                    "extra_service": "auth-service",
                    "extra_endpoint": "/auth/logout"
                }
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/logout",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {"detail": f"HTTP {response.status_code}"}
                    # 检查Java API的响应格式
                    if isinstance(error_data, dict) and "data" in error_data:
                        if error_data.get("code", 0) != 0:
                            raise Exception(error_data.get("message", f"Logout failed: {response.text}"))
                    raise Exception(error_data.get("detail", f"Logout failed: {response.text}"))
                
                result = response.json()
                logger.info(
                    "Java auth-service logout successful",
                    extra={
                        "extra_status_code": response.status_code
                    }
                )
                
                # 处理Java ApiResponse格式
                if isinstance(result, dict) and "data" in result:
                    if result.get("code", 0) == 0:
                        return result["data"]  # 返回data部分
                    else:
                        raise Exception(result.get("message", "Logout failed"))
                
                return result
                
        except Exception as e:
            error_logger.error(
                "Java auth-service logout failed",
                exc_info=True,
                extra={
                    "extra_service": "auth-service",
                    "extra_error": str(e)
                }
            )
            raise


# 全局客户端实例
auth_api_client = AuthAPIClient()