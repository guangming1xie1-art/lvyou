"""
对话窗口管理器模块

负责管理对话窗口，处理上下文窗口限制和会话管理。
提供智能压缩、滑动窗口、会话重置等功能。

功能：
1. 对话窗口监控：监控token使用情况
2. 智能压缩：压缩对话历史，保留关键信息
3. 滑动窗口：滑动窗口策略，保留最近N轮对话
4. 会话重置：当窗口超出限制时，触发会话重置
5. 摘要生成：生成对话摘要
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from enum import Enum

from llm.factory import LLMFactory
from utils.token_counter import TokenCounter
from utils.logger import app_logger

logger = app_logger.getChild(__name__)


class WindowStrategy(Enum):
    """窗口策略枚举"""
    SLIDING_WINDOW = "sliding_window"  # 滑动窗口
    INTELLIGENT_COMPRESSION = "intelligent_compression"  # 智能压缩
    SESSION_RESET = "session_reset"  # 会话重置


class SessionManager:
    """对话窗口管理器
    
    负责管理对话窗口，处理上下文窗口限制和会话管理。
    提供智能压缩、滑动窗口、会话重置等功能。
    """
    
    def __init__(
        self,
        max_tokens: int = 4000,
        window_strategy: WindowStrategy = WindowStrategy.SLIDING_WINDOW,
        compression_threshold: float = 0.8,
        reset_threshold: float = 0.95
    ):
        """
        初始化会话管理器
        
        Args:
            max_tokens: 最大token数
            window_strategy: 窗口策略
            compression_threshold: 压缩阈值（0-1）
            reset_threshold: 重置阈值（0-1）
        """
        self.max_tokens = max_tokens
        self.window_strategy = window_strategy
        self.compression_threshold = compression_threshold
        self.reset_threshold = reset_threshold
        
        # 初始化工具
        self.token_counter = TokenCounter()
        self.llm_factory = LLMFactory()
        self.summary_llm = None
        
        # 会话状态
        self.session_states: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"SessionManager initialized: max_tokens={max_tokens}, strategy={window_strategy}")
    
    async def initialize(self):
        """初始化会话管理器"""
        try:
            logger.info("Initializing SessionManager...")
            
            # 初始化摘要LLM
            self.summary_llm = self.llm_factory.get_llm(
                provider="deepseek",
                model="deepseek-chat",
                temperature=0.3
            )
            
            logger.info("SessionManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SessionManager: {e}")
            raise
    
    async def manage_window(
        self,
        user_id: int,
        session_id: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        管理对话窗口
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            messages: 消息列表
            
        Returns:
            管理结果
        """
        try:
            logger.info(f"Managing window: session={session_id}, messages={len(messages)}")
            
            # 1. 计算当前token数
            current_tokens = self._count_tokens(messages)
            
            # 2. 判断是否需要处理
            token_ratio = current_tokens / self.max_tokens
            
            if token_ratio < self.compression_threshold:
                logger.info(f"Window is safe: {current_tokens}/{self.max_tokens} tokens")
                return {
                    "action": "none",
                    "current_tokens": current_tokens,
                    "max_tokens": self.max_tokens,
                    "messages": messages
                }
            
            # 3. 根据策略处理
            if token_ratio >= self.reset_threshold:
                logger.warning(f"Window exceeds reset threshold: {token_ratio:.2%}")
                result = await self._reset_session(
                    user_id=user_id,
                    session_id=session_id,
                    messages=messages
                )
            elif self.window_strategy == WindowStrategy.SLIDING_WINDOW:
                logger.info(f"Applying sliding window: {token_ratio:.2%}")
                result = await self._apply_sliding_window(
                    user_id=user_id,
                    session_id=session_id,
                    messages=messages
                )
            elif self.window_strategy == WindowStrategy.INTELLIGENT_COMPRESSION:
                logger.info(f"Applying intelligent compression: {token_ratio:.2%}")
                result = await self._apply_intelligent_compression(
                    user_id=user_id,
                    session_id=session_id,
                    messages=messages
                )
            else:
                result = {
                    "action": "none",
                    "current_tokens": current_tokens,
                    "max_tokens": self.max_tokens,
                    "messages": messages
                }
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to manage window: {e}")
            return {
                "action": "error",
                "error": str(e),
                "messages": messages
            }
    
    def _count_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        计算消息的token数
        
        Args:
            messages: 消息列表
            
        Returns:
            token数
        """
        total_tokens = 0
        
        for msg in messages:
            content = msg.get("content", "")
            tokens = self.token_counter.count_tokens(content)
            total_tokens += tokens
        
        return total_tokens
    
    async def _apply_sliding_window(
        self,
        user_id: int,
        session_id: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        应用滑动窗口策略
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            messages: 消息列表
            
        Returns:
            处理结果
        """
        # 保留系统消息
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        
        # 计算需要保留的对话轮数
        system_tokens = self._count_tokens(system_messages)
        available_tokens = int(self.max_tokens * self.compression_threshold) - system_tokens
        
        # 从后往前保留消息
        retained_messages = system_messages.copy()
        current_tokens = system_tokens
        
        for msg in reversed(messages):
            if msg.get("role") == "system":
                continue
            
            msg_tokens = self.token_counter.count_tokens(msg.get("content", ""))
            
            if current_tokens + msg_tokens <= available_tokens:
                retained_messages.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break
        
        logger.info(f"Sliding window: {len(messages)} -> {len(retained_messages)} messages")
        
        return {
            "action": "sliding_window",
            "current_tokens": current_tokens,
            "max_tokens": self.max_tokens,
            "original_count": len(messages),
            "retained_count": len(retained_messages),
            "messages": retained_messages
        }
    
    async def _apply_intelligent_compression(
        self,
        user_id: int,
        session_id: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        应用智能压缩策略
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            messages: 消息列表
            
        Returns:
            处理结果
        """
        # 保留系统消息和最近N轮对话
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        recent_messages = messages[-10:]  # 保留最近10轮
        
        # 压缩旧消息
        old_messages = [msg for msg in messages if msg not in system_messages and msg not in recent_messages]
        
        if old_messages:
            summary = await self._generate_summary(old_messages)
            
            # 创建摘要消息
            summary_msg = {
                "role": "system",
                "content": f"对话摘要：{summary}"
            }
            
            compressed_messages = system_messages + [summary_msg] + recent_messages
        else:
            compressed_messages = system_messages + recent_messages
        
        current_tokens = self._count_tokens(compressed_messages)
        
        logger.info(f"Intelligent compression: {len(messages)} -> {len(compressed_messages)} messages")
        
        return {
            "action": "intelligent_compression",
            "current_tokens": current_tokens,
            "max_tokens": self.max_tokens,
            "original_count": len(messages),
            "compressed_count": len(compressed_messages),
            "messages": compressed_messages
        }
    
    async def _reset_session(
        self,
        user_id: int,
        session_id: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        重置会话
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            messages: 消息列表
            
        Returns:
            处理结果
        """
        # 生成会话摘要
        summary = await self._generate_summary(messages)
        
        # 保留系统消息和摘要
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        
        # 创建摘要消息
        summary_msg = {
            "role": "system",
            "content": f"会话摘要：{summary}\n\n注意：由于对话历史过长，已重置会话。请根据摘要继续对话。"
        }
        
        reset_messages = system_messages + [summary_msg]
        
        current_tokens = self._count_tokens(reset_messages)
        
        logger.warning(f"Session reset: {len(messages)} -> {len(reset_messages)} messages")
        
        return {
            "action": "session_reset",
            "current_tokens": current_tokens,
            "max_tokens": self.max_tokens,
            "original_count": len(messages),
            "reset_count": len(reset_messages),
            "summary": summary,
            "messages": reset_messages,
            "requires_user_confirmation": True
        }
    
    async def _generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        生成对话摘要
        
        Args:
            messages: 消息列表
            
        Returns:
            摘要文本
        """
        try:
            # 构建对话文本
            dialogue_text = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in messages
            ])
            
            # 生成摘要
            prompt = f"""请为以下对话生成一个简洁的摘要（不超过200字）：

{dialogue_text}

摘要："""
            
            response = await self.summary_llm.ainvoke(prompt)
            
            return response.strip()
        
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return "对话摘要生成失败"
    
    def get_session_state(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取会话状态
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话状态
        """
        return self.session_states.get(session_id)
    
    def set_session_state(
        self,
        session_id: str,
        state: Dict[str, Any]
    ):
        """
        设置会话状态
        
        Args:
            session_id: 会话ID
            state: 会话状态
        """
        self.session_states[session_id] = state
    
    def clear_session_state(self, session_id: str):
        """
        清除会话状态
        
        Args:
            session_id: 会话ID
        """
        if session_id in self.session_states:
            del self.session_states[session_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取管理器统计信息"""
        return {
            "max_tokens": self.max_tokens,
            "window_strategy": self.window_strategy.value,
            "compression_threshold": self.compression_threshold,
            "reset_threshold": self.reset_threshold,
            "active_sessions": len(self.session_states)
        }

    async def get_session_stats(
        self,
        user_id: int,
        session_id: str
    ) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            会话统计信息
        """
        try:
            from utils.java_api_client import java_api_client
            
            # 调用Java API获取会话统计
            stats = await java_api_client.get_session_stats(
                user_id=user_id,
                session_id=session_id
            )
            
            if stats:
                return {
                    "message_count": stats.get("message_count", 0),
                    "total_tokens": stats.get("total_tokens", 0),
                    "created_at": stats.get("created_at"),
                    "updated_at": stats.get("updated_at"),
                    "needs_reset": self._check_needs_reset(stats)
                }
            else:
                # 如果没有统计数据，返回默认值
                return {
                    "message_count": 0,
                    "total_tokens": 0,
                    "created_at": None,
                    "updated_at": None,
                    "needs_reset": False
                }
                
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {
                "message_count": 0,
                "total_tokens": 0,
                "created_at": None,
                "updated_at": None,
                "needs_reset": False
            }

    def _check_needs_reset(self, stats: Dict[str, Any]) -> bool:
        """检查会话是否需要重置"""
        message_count = stats.get("message_count", 0)
        total_tokens = stats.get("total_tokens", 0)
        
        # 检查消息数量
        if message_count > 50:
            return True
        
        # 检查token数量
        if total_tokens > self.reset_threshold:
            return True
        
        return False


# 全局会话管理器实例
session_manager = SessionManager()
