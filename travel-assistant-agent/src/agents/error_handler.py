"""Agent系统的中央错误处理"""

from typing import Dict, Any, Callable
import traceback
from ..utils.exceptions import AgentException
from ..utils.logger import app_logger

class AgentErrorHandler:
    """统一处理Agent和skills的错误"""
    
    @staticmethod
    def handle_skill_error(
        skill_name: str,
        error: Exception,
        **context
    ) -> Dict[str, Any]:
        """处理skill执行中的错误"""
        
        # 记录详细的错误信息
        app_logger.error(
            f"Skill {skill_name} execution failed",
            skill=skill_name,
            exception_type=type(error).__name__,
            exception=str(error),
            traceback=traceback.format_exc(),
            **context
        )
        
        # 根据错误类型返回相应的响应
        if isinstance(error, AgentException):
            return {
                "success": False,
                "error": error.to_dict(),
                "http_status": error.http_status
            }
        else:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Skill执行出错，请稍后重试",
                    "details": {
                        "exception_type": type(error).__name__
                    }
                },
                "http_status": 500
            }
    
    @staticmethod
    def handle_agent_error(
        agent_name: str,
        error: Exception,
        **context
    ) -> Dict[str, Any]:
        """处理Agent执行中的错误"""
        
        app_logger.error(
            f"Agent {agent_name} execution failed",
            agent=agent_name,
            exception_type=type(error).__name__,
            exception=str(error),
            traceback=traceback.format_exc(),
            **context
        )
        
        if isinstance(error, AgentException):
            return {
                "success": False,
                "error": error.to_dict(),
                "http_status": error.http_status
            }
        else:
            return {
                "success": False,
                "error": {
                    "code": "AGENT_EXECUTION_ERROR",
                    "message": "Agent执行出错，请稍后重试"
                },
                "http_status": 500
            }
    
    @staticmethod
    def wrap_skill_execution(skill_execute_func: Callable) -> Callable:
        """装饰器：为skill的execute方法添加错误处理"""
        async def wrapper(skill_instance, **kwargs):
            try:
                return await skill_execute_func(skill_instance, **kwargs)
            except Exception as e:
                return AgentErrorHandler.handle_skill_error(
                    skill_name=skill_instance.name,
                    error=e,
                    skill_type=getattr(skill_instance, "agent_type", "general"),
                    input_params=kwargs
                )
        return wrapper
