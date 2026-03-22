"""
记忆系统网关模块

负责管理四层记忆系统，提供统一的记忆访问接口。
与 Java memory-service API 交互，实现记忆的存储、检索和管理。

四层记忆架构：
1. 核心记忆 (Core Memory)：系统提示词，永久固定
2. 瞬时记忆 (Working Memory)：当前任务状态，用完即弃
3. 短期会话记忆 (Session Memory)：对话历史摘要，会话结束清理
4. 长期记忆 (Long-term Memory)：用户偏好和历史案例，永久存储
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from enum import Enum

from utils.java_api_client import java_api_client
from utils.logger import app_logger

logger = app_logger.getChild(__name__)


class MemoryType(Enum):
    """记忆类型枚举"""
    CORE = "core"
    WORKING = "working"
    SESSION = "session"
    LONG_TERM = "long_term"


class MemoryGateway:
    """记忆系统网关
    
    负责管理四层记忆系统，提供统一的记忆访问接口。
    与 Java memory-service API 交互，实现记忆的存储、检索和管理。
    """
    
    def __init__(self):
        """初始化记忆网关"""
        self._core_memory: Dict[str, Any] = {}
        self._working_memory: Dict[str, Any] = {}
        self._session_memory_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info("MemoryGateway initialized")
    
    async def initialize(self):
        """初始化记忆系统"""
        try:
            logger.info("Initializing memory system...")
            
            # 加载核心记忆
            await self._load_core_memory()
            
            logger.info("Memory system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
            raise
    
    async def _load_core_memory(self):
        """加载核心记忆（系统提示词）"""
        self._core_memory = {
            "role": "你是一个专业的旅游规划助手",
            "core_tasks": [
                "帮助用户规划行程",
                "搜索景点酒店",
                "提供推荐"
            ],
            "tool_guidelines": {
                "search_flights": "用于搜索航班信息",
                "search_hotels": "用于搜索酒店信息",
                "recommend_destinations": "用于推荐旅游目的地"
            },
            "prohibitions": [
                "不要推荐超出预算的方案",
                "不要编造虚假信息"
            ]
        }
        logger.info("Core memory loaded")
    
    async def create_conversation(
        self,
        user_id: int,
        session_id: str,
        title: str = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """创建会话
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            title: 会话标题（可选）
            metadata: 元数据（可选）
            
        Returns:
            会话信息
        """
        try:
            conversation = await java_api_client.create_conversation(
                user_id=user_id,
                session_id=session_id,
                title=title,
                metadata=metadata
            )
            
            logger.info(f"Created conversation {session_id} for user {user_id}")
            return conversation
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return None
    
    def get_core_memory(self) -> Dict[str, Any]:
        """获取核心记忆
        
        Returns:
            核心记忆字典
        """
        return self._core_memory.copy()
    
    def set_working_memory(self, key: str, value: Any):
        """设置瞬时记忆
        
        Args:
            key: 记忆键
            value: 记忆值
        """
        self._working_memory[key] = value
        logger.debug(f"Set working memory: {key}")
    
    def get_working_memory(self, key: str, default: Any = None) -> Any:
        """获取瞬时记忆
        
        Args:
            key: 记忆键
            default: 默认值
            
        Returns:
            记忆值
        """
        return self._working_memory.get(key, default)
    
    def clear_working_memory(self):
        """清除瞬时记忆"""
        self._working_memory.clear()
        logger.debug("Working memory cleared")
    
    async def get_session_memory(
        self,
        user_id: int,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取短期会话记忆
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            会话记忆字典，如果不存在返回 None
        """
        cache_key = f"{user_id}:{session_id}"
        
        # 先检查缓存
        if cache_key in self._session_memory_cache:
            return self._session_memory_cache[cache_key]
        
        try:
            # 从 Java API 获取会话记忆
            response = await java_api_client.get_session_memory(
                user_id=user_id,
                session_id=session_id
            )
            
            if response:
                self._session_memory_cache[cache_key] = response
                logger.info(f"Loaded session memory for session {session_id}")
            
            return response
        except Exception as e:
            logger.error(f"Failed to get session memory: {e}")
            return None
    
    async def save_message(
        self,
        user_id: int,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """保存对话消息
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            role: 角色（user/assistant/system）
            content: 消息内容
            metadata: 元数据
            
        Returns:
            消息ID
        """
        try:
            message_id = await java_api_client.save_message(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
                metadata=metadata or {}
            )
            
            # 清除缓存，强制下次重新加载
            cache_key = f"{user_id}:{session_id}"
            if cache_key in self._session_memory_cache:
                del self._session_memory_cache[cache_key]
            
            logger.info(f"Saved message {message_id} for session {session_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return None
    
    async def get_conversation_history(
        self,
        user_id: int,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取对话历史
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            limit: 返回消息数量限制
            
        Returns:
            消息列表
        """
        try:
            messages = await java_api_client.get_conversation_history(
                user_id=user_id,
                session_id=session_id,
                limit=limit
            )
            return messages
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    async def save_preference(
        self,
        user_id: int,
        preference_type: str,
        preference_value: str,
        confidence: float = 0.8,
        source: str = "conversation"
    ) -> Optional[str]:
        """保存用户偏好
        
        Args:
            user_id: 用户ID
            preference_type: 偏好类型（如 destination_type, budget_range）
            preference_value: 偏好值
            confidence: 置信度（0-1）
            source: 来源（conversation/profile）
            
        Returns:
            偏好ID
        """
        try:
            preference_id = await java_api_client.save_preference(
                user_id=user_id,
                preference_type=preference_type,
                preference_value=preference_value,
                confidence=confidence,
                source=source
            )
            
            logger.info(f"Saved preference {preference_id}: {preference_type}={preference_value}")
            return preference_id
        except Exception as e:
            logger.error(f"Failed to save preference: {e}")
            return None
    
    async def get_user_preferences(
        self,
        user_id: int,
        preference_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取用户偏好
        
        Args:
            user_id: 用户ID
            preference_type: 偏好类型（可选）
            
        Returns:
            偏好列表
        """
        try:
            preferences = await java_api_client.get_user_preferences(
                user_id=user_id,
                preference_type=preference_type
            )
            return preferences
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return []
    
    async def save_task_case(
        self,
        user_id: int,
        destination: str,
        duration_days: int,
        budget_range: str,
        plan_summary: str,
        satisfaction: Optional[float] = None
    ) -> Optional[str]:
        """保存历史任务案例
        
        Args:
            user_id: 用户ID
            destination: 目的地
            duration_days: 天数
            budget_range: 预算范围
            plan_summary: 计划摘要
            satisfaction: 满意度（0-5）
            
        Returns:
            案例ID
        """
        try:
            case_id = await java_api_client.save_task_case(
                user_id=user_id,
                destination=destination,
                duration_days=duration_days,
                budget_range=budget_range,
                plan_summary=plan_summary,
                satisfaction=satisfaction
            )
            
            logger.info(f"Saved task case {case_id} for {destination}")
            return case_id
        except Exception as e:
            logger.error(f"Failed to save task case: {e}")
            return None
    
    async def get_task_cases(
        self,
        user_id: int,
        destination: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取历史任务案例
        
        Args:
            user_id: 用户ID
            destination: 目的地（可选）
            limit: 返回数量限制
            
        Returns:
            案例列表
        """
        try:
            cases = await java_api_client.get_task_cases(
                user_id=user_id,
                destination=destination,
                limit=limit
            )
            return cases
        except Exception as e:
            logger.error(f"Failed to get task cases: {e}")
            return []
    
    async def update_session_summary(
        self,
        user_id: int,
        session_id: str,
        summary: str
    ) -> bool:
        """更新会话摘要
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            summary: 摘要内容
            
        Returns:
            是否成功
        """
        try:
            success = await java_api_client.update_session_summary(
                user_id=user_id,
                session_id=session_id,
                summary=summary
            )
            
            # 清除缓存
            cache_key = f"{user_id}:{session_id}"
            if cache_key in self._session_memory_cache:
                del self._session_memory_cache[cache_key]
            
            logger.info(f"Updated session summary for {session_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to update session summary: {e}")
            return False
    
    async def get_user_sessions(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取用户的所有会话
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            会话列表
        """
        try:
            sessions = await java_api_client.get_user_sessions(
                user_id=user_id,
                limit=limit
            )
            return sessions
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    async def archive_session(
        self,
        user_id: int,
        session_id: str
    ) -> bool:
        """归档会话
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        try:
            success = await java_api_client.archive_session(
                user_id=user_id,
                session_id=session_id
            )
            
            # 清除缓存
            cache_key = f"{user_id}:{session_id}"
            if cache_key in self._session_memory_cache:
                del self._session_memory_cache[cache_key]
            
            logger.info(f"Archived session {session_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to archive session: {e}")
            return False
    
    def build_context_prompt(
        self,
        user_id: int,
        session_id: str,
        include_long_term: bool = True,
        max_tokens: int = 2000
    ) -> str:
        """构建上下文Prompt
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            include_long_term: 是否包含长期记忆
            max_tokens: 最大token数
            
        Returns:
            上下文Prompt字符串
        """
        context_parts = []
        
        # 1. 核心记忆
        core = self.get_core_memory()
        core_prompt = f"""角色定位：{core.get('role', '')}
核心任务：{', '.join(core.get('core_tasks', []))}
注意事项：{', '.join(core.get('prohibitions', []))}"""
        context_parts.append(core_prompt)
        
        # 2. 瞬时记忆
        if self._working_memory:
            working_prompt = "当前任务状态：\n"
            for key, value in self._working_memory.items():
                working_prompt += f"- {key}: {value}\n"
            context_parts.append(working_prompt)
        
        return "\n\n".join(context_parts)

    async def extract_preferences(
        self,
        user_id: int,
        conversation_history: List[Dict[str, str]],
        confidence: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        从对话历史中提取用户偏好
        
        Args:
            user_id: 用户ID
            conversation_history: 对话历史
            confidence: 默认置信度
            
        Returns:
            提取的偏好列表
        """
        try:
            from llm.factory import LLMFactory
            
            llm = LLMFactory.create_model_by_tier(tier="cheap")
            
            # 构建提取提示词
            extraction_prompt = f"""请从以下对话历史中提取用户的旅游偏好。

对话历史：
{self._format_conversation_history(conversation_history)}

请提取以下类型的偏好：
1. destination_type: 目的地类型（如：海岛、城市、山区、乡村）
2. budget_range: 预算范围（如：5000-8000、10000-15000）
3. hotel_level: 酒店等级（如：三星、四星、五星）
4. travel_style: 旅游风格（如：休闲、探险、美食、购物、亲子）
5. duration_preference: 天数偏好（如：3-5天、7-10天）

请以JSON格式返回，每个偏好包含：
- type: 偏好类型
- value: 偏好值
- confidence: 置信度（0-1）
- source: 来源（explicit/implicit）

只返回有明确证据的偏好，置信度低于0.5的不要返回。"""

            # 调用LLM提取偏好
            from langchain_core.messages import HumanMessage
            result = await llm.ainvoke([HumanMessage(content=extraction_prompt)])
            
            # 解析结果
            import json
            try:
                preferences = json.loads(result.content)
                
                # 保存提取的偏好
                saved_preferences = []
                for pref in preferences:
                    pref_id = await self.save_preference(
                        user_id=user_id,
                        preference_type=pref.get('type'),
                        preference_value=pref.get('value'),
                        confidence=pref.get('confidence', confidence),
                        source=pref.get('source', 'implicit')
                    )
                    saved_preferences.append({
                        'id': pref_id,
                        'type': pref.get('type'),
                        'value': pref.get('value'),
                        'confidence': pref.get('confidence', confidence)
                    })
                
                logger.info(f"Extracted {len(saved_preferences)} preferences for user {user_id}")
                return saved_preferences
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse extracted preferences: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to extract preferences: {e}")
            return []

    def _format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        """格式化对话历史"""
        formatted = []
        for msg in history[-10:]:  # 只使用最近10轮对话
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)


# 全局记忆网关实例
memory_gateway = MemoryGateway()
