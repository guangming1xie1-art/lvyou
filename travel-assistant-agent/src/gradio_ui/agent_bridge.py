"""Agent桥接层，连接Gradio UI到LangGraph工作流

使用新的 deepagents CompiledSubAgent 架构
"""

from typing import Dict, Any, List, Optional
from loguru import logger


class AgentBridge:
    """Agent桥接类，直接调用本地工作流（不依赖HTTP）"""
    
    def __init__(self):
        """初始化Agent桥接"""
        self.logger = logger
        self.logger.info("AgentBridge initialized (local workflow mode)")
    
    async def chat(
        self, 
        user_input: str, 
        history: List[tuple],
        attachments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """与工作流进行对话
        
        Args:
            user_input: 用户输入的消息
            history: 对话历史（list of (user, assistant) tuples）
            attachments: 附件信息（图片、音频、视频等）
        
        Returns:
            工作流执行结果字典
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

            # 构建完整输入消息
            full_message = user_input
            if attachments:
                attachment_info = ", ".join([f"{k}: {v}" for k, v in attachments.items()])
                full_message = f"{user_input}\n\n[附件: {attachment_info}]"

            self.logger.info(f"Calling workflow with message: {full_message[:100]}...")
            
            # 导入并调用工作流
            from workflows.main_workflow import run_main_workflow_async
            
            result = await run_main_workflow_async(full_message)
            
            self.logger.info("Workflow completed successfully")
            
            return {
                "response": result.get("final_response", "处理完成"),
                "data": result
            }
        
        except ImportError as e:
            self.logger.error(f"导入工作流模块失败: {e}")
            return {
                "response": "系统配置错误，无法加载工作流模块",
                "error": str(e)
            }
        except Exception as e:
            self.logger.error(f"工作流执行失败: {e}")
            return {
                "response": f"处理请求时出错: {str(e)}",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """获取Agent的状态"""
        return {
            "status": "online",
            "mode": "local_workflow",
            "architecture": "deepagents CompiledSubAgent"
        }
    
    async def close(self):
        """关闭连接（本地模式不需要）"""
        self.logger.info("AgentBridge closed")


# 导出兼容的接口
def get_agent_bridge() -> AgentBridge:
    """获取AgentBridge单例"""
    return agent_bridge


# 创建全局实例（向后兼容）
agent_bridge = AgentBridge()
