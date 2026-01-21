"""Agent编排层，集中处理Agent之间的调用和日志"""

from typing import Dict, Any, List, Optional
import time
import uuid
from utils.logger import app_logger
from agents.error_handler import AgentErrorHandler

class AgentOrchestrator:
    """Agent编排器，管理多个Agent的协调执行"""
    
    def __init__(self):
        self.agents = {}
        self._request_id = None
    
    def register_agent(self, agent_name: str, agent):
        """注册Agent"""
        self.agents[agent_name] = agent
        app_logger.info(f"Registered agent: {agent_name}")
    
    async def execute_agent(
        self,
        agent_name: str,
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """执行指定的Agent"""
        
        request_id = app_logger.get_request_id()
        start_time = time.time()
        
        app_logger.info(
            f"Starting agent {agent_name}",
            agent=agent_name,
            request_id=request_id,
            message_preview=message[:100] if message else ""
        )
        
        try:
            if agent_name not in self.agents:
                raise ValueError(f"Agent {agent_name} not found")
            
            agent = self.agents[agent_name]
            # 假设 Agent 类有 run 方法
            result = await agent.run(
                message=message,
                context=context or {}
            )
            
            duration = time.time() - start_time
            
            app_logger.info(
                f"Agent {agent_name} completed",
                agent=agent_name,
                duration_ms=int(duration * 1000),
                has_error="error" in str(result)
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            return AgentErrorHandler.handle_agent_error(
                agent_name=agent_name,
                error=e,
                duration_ms=int(duration * 1000),
                request_id=request_id
            )
