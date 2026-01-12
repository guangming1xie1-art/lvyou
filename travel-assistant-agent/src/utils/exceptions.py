"""Agent系统的统一异常定义"""

class AgentException(Exception):
    """Agent系统的基础异常"""
    
    def __init__(
        self,
        code: str,
        message: str,
        details: dict = None,
        http_status: int = 500
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.http_status = http_status
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }

# Agent特定的异常
class AgentExecutionError(AgentException):
    """Agent执行错误"""
    def __init__(self, agent_name: str, message: str, **kwargs):
        super().__init__(
            code="AGENT_EXECUTION_ERROR",
            message=f"Agent {agent_name} 执行失败: {message}",
            **kwargs
        )

class SkillExecutionError(AgentException):
    """Skill执行错误"""
    def __init__(self, skill_name: str, message: str, **kwargs):
        super().__init__(
            code="SKILL_EXECUTION_ERROR",
            message=f"Skill {skill_name} 执行失败: {message}",
            **kwargs
        )

class JavaAPIError(AgentException):
    """Java API调用错误"""
    def __init__(self, endpoint: str, message: str, status_code: int = None, **kwargs):
        super().__init__(
            code="JAVA_API_ERROR",
            message=f"Java API {endpoint} 错误: {message}",
            details={**kwargs, "endpoint": endpoint, "status_code": status_code},
            http_status=status_code or 500
        )

class JavaAPITimeoutError(JavaAPIError):
    """Java API超时错误"""
    def __init__(self, endpoint: str, message: str = "Request timeout", **kwargs):
        super().__init__(endpoint=endpoint, message=message, status_code=408, **kwargs)

class JavaAPINotFoundError(JavaAPIError):
    """Java API资源不存在"""
    def __init__(self, endpoint: str, message: str = "Resource not found", **kwargs):
        super().__init__(endpoint=endpoint, message=message, status_code=404, **kwargs)

class JavaAPIValidationError(JavaAPIError):
    """Java API数据验证错误"""
    def __init__(self, endpoint: str, message: str = "Validation error", **kwargs):
        super().__init__(endpoint=endpoint, message=message, status_code=400, **kwargs)

class JavaAPIServerError(JavaAPIError):
    """Java API服务器错误"""
    def __init__(self, endpoint: str, message: str = "Internal server error", **kwargs):
        super().__init__(endpoint=endpoint, message=message, status_code=500, **kwargs)

class JavaAPIAuthError(JavaAPIError):
    """Java API认证错误"""
    def __init__(self, endpoint: str, message: str = "Authentication failed", **kwargs):
        super().__init__(endpoint=endpoint, message=message, status_code=401, **kwargs)

class ValidationError(AgentException):
    """数据验证错误"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            code="VALIDATION_ERROR",
            message=f"数据验证失败: {message}",
            http_status=400,
            **kwargs
        )

class TimeoutError(AgentException):
    """超时错误"""
    def __init__(self, operation: str, timeout: int, **kwargs):
        super().__init__(
            code="TIMEOUT_ERROR",
            message=f"{operation} 超时 ({timeout}s)",
            http_status=504,
            **kwargs
        )
