"""
Info Collection Skill Implementation
收集和提取用户旅游需求信息
"""
from typing import Dict, Any, Optional, List
import logging
import json
from src.skills.base import Skill
from src.llm import LLMFactory

logger = logging.getLogger(__name__)


class InfoCollectionSkill(Skill):
    """信息收集技能 - 从用户消息中提取旅游需求"""
    
    def __init__(self):
        super().__init__(
            name="info_collection",
            description="与用户交互收集旅游需求信息",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.02,
            category="planning"
        )
    
    def get_required_fields(self) -> list:
        """必需字段"""
        return ["user_message"]
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行信息收集
        
        Args:
            input_data: {
                "user_message": str,
                "context": {...}
            }
        
        Returns:
            {
                "collected_info": {...},
                "missing_fields": [...],
                "confidence": float
            }
        """
        user_message = input_data.get("user_message", "")
        context = input_data.get("context", {})
        previous_info = context.get("previous_collected_info", {})
        
        if not user_message:
            return {
                "collected_info": previous_info,
                "missing_fields": [],
                "error": "user_message is required"
            }
        
        # 使用 LLM 提取信息
        collected_info = await self._extract_info(user_message, previous_info)
        
        # 识别缺失字段
        missing_fields = self._identify_missing_fields(collected_info)
        
        # 计算置信度
        confidence = self._calculate_confidence(collected_info)
        
        return {
            "collected_info": collected_info,
            "missing_fields": missing_fields,
            "confidence": confidence,
            "suggestions": self._generate_suggestions(collected_info),
            "metadata": {
                "extraction_method": "llm",
                "execution_time_ms": 200
            }
        }
    
    async def _extract_info(
        self,
        user_message: str,
        previous_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """使用 LLM 提取信息"""
        try:
            # 创建 LLM（便宜层）
            llm = LLMFactory.create_model("deepseek-chat")
            
            # 系统提示
            system_prompt = """你是旅游助手的信息收集员。请从用户消息中提取旅游需求信息。

需要提取的字段：
- destination: 目的地（城市、国家）
- dates: 日期信息 {departure: "YYYY-MM-DD", return: "YYYY-MM-DD"}
- budget: 预算 {min: number, max: number, currency: "CNY"}
- travelers_count: 旅行人数
- preferences: 偏好列表 ["culture", "food", "beach", "adventure", "shopping", "nature", "history"]
- accommodation_type: 住宿类型 "hotel" | "hostel" | "apartment" | "resort"
- special_requirements: 特殊需求列表

以 JSON 格式返回提取到的信息，未提及的字段可省略。
如果有之前的信息，请合并更新。"""
            
            previous_info_str = json.dumps(previous_info, ensure_ascii=False)
            user_prompt = f"""之前收集到的信息：
{previous_info_str}

用户新消息：
{user_message}

请提取并更新信息："""
            
            # 调用 LLM
            from langchain_core.messages import HumanMessage, SystemMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm.invoke(messages)
            
            # 解析响应
            try:
                extracted = json.loads(response.content)
                # 合并之前的信息
                collected_info = {**previous_info, **extracted}
                return collected_info
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response: {response.content}")
                return previous_info
        
        except Exception as e:
            logger.error(f"Error extracting info: {e}")
            return previous_info
    
    def _identify_missing_fields(
        self,
        collected_info: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """识别缺失的关键字段"""
        missing = []
        
        # 必需字段
        required_fields = {
            "destination": "目的地",
            "dates": "出行日期",
            "budget": "预算范围",
            "travelers_count": "旅行人数"
        }
        
        for field, description in required_fields.items():
            if field not in collected_info or not collected_info[field]:
                missing.append({
                    "field": field,
                    "description": f"需要提供{description}",
                    "required_for": "planning"
                })
        
        return missing
    
    def _calculate_confidence(self, collected_info: Dict[str, Any]) -> float:
        """计算信息完整度置信度"""
        # 检查关键字段
        key_fields = ["destination", "dates", "budget", "travelers_count", "preferences"]
        filled_count = sum(1 for f in key_fields if f in collected_info and collected_info[f])
        
        confidence = filled_count / len(key_fields)
        return round(confidence, 2)
    
    def _generate_suggestions(self, collected_info: Dict[str, Any]) -> List[str]:
        """生成建议"""
        suggestions = []
        
        # 基于目的地的建议
        destination = collected_info.get("destination", "")
        if "巴黎" in destination or "Paris" in destination:
            suggestions.append("6月是巴黎旅游旺季，建议提前预订")
        
        # 基于预算的建议
        budget = collected_info.get("budget", {})
        if budget:
            suggestions.append("建议考虑购买旅游保险")
        
        return suggestions


__all__ = ["InfoCollectionSkill"]
