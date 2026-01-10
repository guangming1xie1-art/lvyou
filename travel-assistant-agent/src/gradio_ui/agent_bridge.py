"""Agent Bridge for Gradio UI

这个模块提供了Gradio UI和现有Agent系统之间的桥梁，
负责将用户消息路由到相应的Agent并格式化响应。
"""

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging

from agents import (
    InfoCollectionAgent,
    SearchAgent, 
    RecommendationAgent,
    BookingAgent,
    SkillBasedAgent,
    get_mcp_client
)
from utils.logger import app_logger

logger = logging.getLogger(__name__)


class AgentBridge:
    """Agent系统与Gradio UI之间的桥梁"""
    
    def __init__(self):
        # 初始化各种Agent
        self.info_agent = InfoCollectionAgent()
        self.search_agent = SearchAgent()
        self.recommendation_agent = RecommendationAgent()
        self.booking_agent = BookingAgent()
        self.skill_agent = SkillBasedAgent()
        
        # 当前会话状态
        self.session_state = {}
        self.conversation_history = []
        
        # Agent流程状态
        self.current_stage = "info_collection"  # info_collection, search, recommendation, booking
        self.collected_info = {}
        
    async def process_message(
        self, 
        user_message: str, 
        uploaded_files: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        处理用户消息并返回Agent响应
        
        Args:
            user_message: 用户输入的文本消息
            uploaded_files: 用户上传的文件列表
            
        Returns:
            包含响应文本和状态信息的字典
        """
        try:
            # 记录用户消息
            user_entry = {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat(),
                "files": uploaded_files or []
            }
            self.conversation_history.append(user_entry)
            
            # 处理多媒体文件
            if uploaded_files:
                await self._process_uploaded_files(uploaded_files)
            
            # 根据当前阶段路由到相应的Agent
            response = await self._route_to_agent(user_message)
            
            # 记录Agent响应
            agent_entry = {
                "role": "assistant", 
                "content": response["message"],
                "timestamp": datetime.now().isoformat(),
                "stage": self.current_stage,
                "metadata": response.get("metadata", {})
            }
            self.conversation_history.append(agent_entry)
            
            return {
                "success": True,
                "message": response["message"],
                "stage": self.current_stage,
                "collected_info": self.collected_info,
                "next_actions": response.get("next_actions", []),
                "multimedia": response.get("multimedia", [])
            }
            
        except Exception as e:
            error_msg = f"处理消息时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "stage": self.current_stage,
                "collected_info": self.collected_info
            }
    
    async def _route_to_agent(self, user_message: str) -> Dict[str, Any]:
        """根据当前阶段路由消息到相应的Agent"""
        
        if self.current_stage == "info_collection":
            return await self._handle_info_collection(user_message)
        elif self.current_stage == "search":
            return await self._handle_search(user_message)
        elif self.current_stage == "recommendation":
            return await self._handle_recommendation(user_message)
        elif self.current_stage == "booking":
            return await self._handle_booking(user_message)
        else:
            # 默认回到信息收集阶段
            self.current_stage = "info_collection"
            return await self._handle_info_collection(user_message)
    
    async def _handle_info_collection(self, user_message: str) -> Dict[str, Any]:
        """处理信息收集阶段"""
        try:
            # 构建状态
            state = {
                "user_message": user_message,
                "metadata": {"stage": "info_collection"}
            }
            
            # 运行信息收集Agent
            result_state = await self.info_agent.run(state)
            
            # 更新收集的信息
            if "collected_info" in result_state:
                self.collected_info.update(result_state["collected_info"])
            
            # 判断是否信息收集完整
            if self._is_info_complete():
                self.current_stage = "search"
                return {
                    "message": self._generate_collection_complete_message(),
                    "next_actions": ["开始搜索相关信息"],
                    "metadata": {"stage_transition": True}
                }
            else:
                return {
                    "message": self._generate_collection_prompt(),
                    "next_actions": self._get_missing_info_prompts(),
                    "metadata": {"stage": "info_collection"}
                }
                
        except Exception as e:
            logger.error(f"Info collection error: {e}")
            return {
                "message": "收集信息时遇到问题，请重新输入您的旅行需求。",
                "next_actions": ["重新输入需求"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_search(self, user_message: str) -> Dict[str, Any]:
        """处理搜索阶段"""
        try:
            state = {
                "user_message": user_message,
                "collected_info": self.collected_info,
                "metadata": {"stage": "search"}
            }
            
            result_state = await self.search_agent.run(state)
            
            # 检查搜索结果
            search_results = result_state.get("search_results", [])
            
            if search_results:
                self.current_stage = "recommendation"
                return {
                    "message": "搜索完成！我为您找到了相关信息，现在为您生成个性化推荐。",
                    "next_actions": ["查看推荐方案"],
                    "metadata": {"search_results_count": len(search_results)}
                }
            else:
                return {
                    "message": "搜索未找到相关信息，请尝试调整您的需求或选择其他目的地。",
                    "next_actions": ["调整需求", "更换目的地"],
                    "metadata": {"search_results": []}
                }
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "message": "搜索时遇到问题，请稍后再试。",
                "next_actions": ["重试搜索"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_recommendation(self, user_message: str) -> Dict[str, Any]:
        """处理推荐阶段"""
        try:
            state = {
                "user_message": user_message,
                "collected_info": self.collected_info,
                "search_results": self.session_state.get("search_results", []),
                "metadata": {"stage": "recommendation"}
            }
            
            result_state = await self.recommendation_agent.run(state)
            
            recommendations = result_state.get("recommendations", [])
            
            if recommendations:
                self.current_stage = "booking"
                return {
                    "message": self._format_recommendations(recommendations),
                    "next_actions": ["预订推荐方案", "查看详细信息"],
                    "metadata": {"recommendations_count": len(recommendations)}
                }
            else:
                return {
                    "message": "暂时无法生成推荐，请尝试调整您的需求。",
                    "next_actions": ["调整需求", "重新搜索"],
                    "metadata": {"recommendations": []}
                }
                
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return {
                "message": "生成推荐时遇到问题，请稍后再试。",
                "next_actions": ["重试推荐"],
                "metadata": {"error": str(e)}
            }
    
    async def _handle_booking(self, user_message: str) -> Dict[str, Any]:
        """处理预订阶段"""
        try:
            state = {
                "user_message": user_message,
                "collected_info": self.collected_info,
                "selected_recommendation": self.session_state.get("selected_recommendation"),
                "metadata": {"stage": "booking"}
            }
            
            result_state = await self.booking_agent.run(state)
            
            booking_status = result_state.get("booking_status", {})
            
            return {
                "message": self._format_booking_status(booking_status),
                "next_actions": ["确认预订", "修改订单", "查看预订详情"],
                "metadata": {"booking_status": booking_status}
            }
            
        except Exception as e:
            logger.error(f"Booking error: {e}")
            return {
                "message": "处理预订时遇到问题，请稍后再试。",
                "next_actions": ["重试预订"],
                "metadata": {"error": str(e)}
            }
    
    async def _process_uploaded_files(self, files: List) -> None:
        """处理用户上传的文件"""
        for file_info in files:
            # 这里可以添加文件处理逻辑
            # 例如：图片识别、语音转文字等
            app_logger.info(f"Processing uploaded file: {file_info}")
    
    def _is_info_complete(self) -> bool:
        """检查收集的信息是否完整"""
        required_fields = ["destination", "dates", "budget"]
        return all(field in self.collected_info and self.collected_info[field] != "未指定" 
                  for field in required_fields)
    
    def _generate_collection_prompt(self) -> str:
        """生成信息收集提示"""
        missing = []
        if not self.collected_info.get("destination") or self.collected_info["destination"] == "未指定":
            missing.append("目的地")
        if not self.collected_info.get("dates") or self.collected_info["dates"] == "未指定":
            missing.append("旅行日期")
        if not self.collected_info.get("budget") or self.collected_info["budget"] == "未指定":
            missing.append("预算范围")
        
        if missing:
            prompt = f"我正在为您规划旅行。为了提供更好的服务，请告诉我：\n"
            for item in missing:
                prompt += f"- {item}\n"
            return prompt
        else:
            return "信息收集完成！"
    
    def _get_missing_info_prompts(self) -> List[str]:
        """获取缺失信息的提示"""
        prompts = []
        if not self.collected_info.get("destination") or self.collected_info["destination"] == "未指定":
            prompts.append("请告诉我您想去哪里旅行")
        if not self.collected_info.get("dates") or self.collected_info["dates"] == "未指定":
            prompts.append("请告诉我您的出行日期和旅行天数")
        if not self.collected_info.get("budget") or self.collected_info["budget"] == "未指定":
            prompts.append("请告诉我您的预算范围")
        return prompts
    
    def _generate_collection_complete_message(self) -> str:
        """生成收集完成的消息"""
        info = self.collected_info
        return f"""✅ 信息收集完成！

📍 目的地：{info.get('destination', '未指定')}
📅 旅行时间：{info.get('dates', '未指定')}
💰 预算：{info.get('budget', '未指定')}
🎯 偏好：{', '.join(info.get('preferences', []))}

现在开始为您搜索相关信息..."""
    
    def _format_recommendations(self, recommendations: List[Dict]) -> str:
        """格式化推荐结果"""
        if not recommendations:
            return "暂无推荐结果。"
        
        message = "🎯 为您推荐以下方案：\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            message += f"**方案 {i}：**\n"
            if isinstance(rec, dict):
                for key, value in rec.items():
                    message += f"• {key}: {value}\n"
            else:
                message += f"• {rec}\n"
            message += "\n"
        
        message += "请选择您喜欢的方案进行预订。"
        return message
    
    def _format_booking_status(self, status: Dict) -> str:
        """格式化预订状态"""
        if not status:
            return "暂无预订信息。"
        
        message = "📋 预订状态：\n\n"
        for key, value in status.items():
            message += f"• {key}: {value}\n"
        
        return message
    
    def clear_conversation(self) -> None:
        """清除对话历史和状态"""
        self.conversation_history = []
        self.session_state = {}
        self.current_stage = "info_collection"
        self.collected_info = {}
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def get_stage_info(self) -> Dict[str, Any]:
        """获取当前阶段信息"""
        return {
            "current_stage": self.current_stage,
            "collected_info": self.collected_info,
            "is_complete": self._is_info_complete()
        }