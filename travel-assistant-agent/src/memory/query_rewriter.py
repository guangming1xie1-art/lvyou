"""
查询改写器

基于记忆和对话历史，将用户查询改写为语义完整的独立查询
"""

import logging
from typing import Dict, Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from conf import settings
from llm.factory import LLMFactory

logger = logging.getLogger(__name__)


class QueryRewriter:
    """查询改写器"""
    
    def __init__(self):
        self.llm = LLMFactory.create_llm(model=settings.model_name, temperature=0)
    
    async def rewrite(
        self,
        user_query: str,
        memory: Dict[str, Any],
        conversation_history: list
    ) -> str:
        """
        查询改写
        
        Args:
            user_query: 用户原始查询
            memory: 记忆上下文
            conversation_history: 对话历史
            
        Returns:
            改写后的查询
        """
        # 1. 提取记忆信息
        long_term = memory.get("long_term", {})
        short_term = memory.get("short_term", {})
        user_profile = memory.get("user_profile", {})
        
        # 2. 格式化对话历史（最近 6 轮）
        recent_history = conversation_history[-6:] if conversation_history else []
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in recent_history
        ])
        
        # 3. 构建提示词
        prompt = self._build_prompt(
            user_query=user_query,
            long_term=long_term,
            short_term=short_term,
            user_profile=user_profile,
            history_text=history_text
        )
        
        # 4. 调用 LLM
        try:
            response = await self.llm.ainvoke([
                HumanMessage(content=prompt)
            ])
            
            rewritten_query = response.content.strip()
            
            logger.info(f"📝 查询改写：'{user_query}' → '{rewritten_query}'")
            
            return rewritten_query
            
        except Exception as e:
            logger.error(f"❌ 查询改写失败：{e}")
            # 降级：返回原始查询
            return user_query
    
    def _build_prompt(
        self,
        user_query: str,
        long_term: Dict,
        short_term: Dict,
        user_profile: Dict,
        history_text: str
    ) -> str:
        """构建改写提示词"""
        
        return f"""
你是查询改写专家。根据用户记忆和对话历史，将用户当前问题改写为语义完整的独立查询。

## 用户长期记忆（偏好）
- 酒店偏好：{long_term.get("hotel_chain", "无")}
- 饮食限制：{long_term.get("dietary", "无")}
- 预算范围：{long_term.get("budget", "无")}
- 旅行风格：{long_term.get("travel_style", "无")}

## 短期记忆（最近搜索）
- 最近搜索：{user_profile.get("recent_searches", [])}
- 上次目的地：{user_profile.get("last_destination", "无")}

## 对话历史
{history_text if history_text else "无"}

## 用户当前问题
{user_query}

## 改写规则
1. 识别代词指代（如"它"、"这个"、"上次那个"指代什么）
2. 补充省略信息（如目的地、日期等）
3. 结合用户偏好（如预算、酒店品牌等）
4. 生成语义完整、独立的查询

## 改写后的查询
"""


# 单例实例
query_rewriter = QueryRewriter()
