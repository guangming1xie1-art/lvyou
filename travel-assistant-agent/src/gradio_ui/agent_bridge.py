"""Agent桥接层，连接Gradio UI到LangGraph Agent"""

from typing import Dict, Any, List, Optional
import httpx
from loguru import logger

class AgentBridge:
    """连接到Agent系统的桥接类"""
    
    def __init__(self, agent_url: str = "http://localhost:8000"):
        """初始化Agent桥接
        
        Args:
            agent_url: Agent服务的URL
        """
        self.agent_url = agent_url
        self.http_client = httpx.AsyncClient(timeout=60.0)
    
    async def chat(
        self, 
        user_input: str, 
        history: List[tuple],
        attachments: Optional[Dict[str, Any]] = None
    ) -> str:
        """与Agent进行对话
        
        Args:
            user_input: 用户输入的消息
            history: 对话历史（list of (user, assistant) tuples）
            attachments: 附件信息（图片、音频、视频等）
        
        Returns:
            Agent的响应文本
        """
        
        try:
            # 构建请求
            # 注意：history 是 (user, assistant) 元组列表
            formatted_history = []
            for user_msg, assistant_msg in history:
                if user_msg:
                    formatted_history.append({"role": "user", "content": user_msg})
                if assistant_msg:
                    formatted_history.append({"role": "assistant", "content": assistant_msg})

            payload = {
                "message": user_input,
                "conversation_history": formatted_history,
                "attachments": attachments or {}
            }
            
            # 调用Agent API
            logger.info(f"Calling Agent API at {self.agent_url}/agent/chat with payload: {payload}")
            response = await self.http_client.post(
                f"{self.agent_url}/agent/chat",
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Agent response: {result}")
            
            # 处理统一响应格式 {code, message, data}
            if isinstance(result, dict) and "data" in result:
                data = result["data"]
                return data.get("response", "Agent暂时没有回复")
            
            # 兼容原始格式
            return result.get("response", "Agent暂时没有回复")
        
        except httpx.TimeoutException:
            logger.error("Agent请求超时")
            return "Agent处理超时，请稍后重试"
        except httpx.HTTPError as e:
            logger.error(f"Agent请求失败: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response body: {e.response.text}")
            return f"与Agent通信出错：{str(e)}"
        except Exception as e:
            logger.error(f"发生意外错误: {e}")
            return f"处理请求时发生错误: {str(e)}"
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """获取Agent的状态"""
        try:
            response = await self.http_client.get(f"{self.agent_url}/agent/status")
            response.raise_for_status()
            result = response.json()
            # 处理统一响应格式
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            return result
        except Exception as e:
            logger.error(f"无法获取Agent状态: {e}")
            return {"status": "offline"}
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()

# 全局Agent桥接实例
# 注意：在实际应用中，agent_url 应该从配置中读取
from config import settings
agent_bridge = AgentBridge(agent_url=f"http://{settings.app_host}:{settings.app_port}")
