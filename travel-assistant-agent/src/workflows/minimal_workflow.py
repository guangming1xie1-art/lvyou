"""
LangGraph + DeepAgent 混合工作流 - 最简版本
不依赖复杂的外部库，只使用基础功能
"""
import asyncio
import json
import time
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field

from utils.token_tracker import TokenTracker
from utils.logger import app_logger
from config import settings

# 工作流状态定义
@dataclass
class WorkflowState:
    # 基础状态
    user_message: str = ""
    request_id: str = ""
    stage: str = "starting"
    timestamp: float = 0.0
    
    # 数据流转
    collected_info: Dict[str, Any] = field(default_factory=dict)
    search_results: Dict[str, Any] = field(default_factory=dict)
    search_quality: float = 0.0
    validate_results: Dict[str, Any] = field(default_factory=dict)
    recommendations: Dict[str, Any] = field(default_factory=dict)
    booking_confirmation: Dict[str, Any] = field(default_factory=dict)
    final_plan: Dict[str, Any] = field(default_factory=dict)
    
    # 错误处理
    error: Optional[str] = None
    retry_count: int = 0
    error_details: Dict[str, Any] = field(default_factory=dict)
    
    # 执行控制
    status: str = "pending"  # pending, running, completed, failed, retrying
    should_retry: bool = False
    workflow_path: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_message": self.user_message,
            "request_id": self.request_id,
            "stage": self.stage,
            "timestamp": self.timestamp,
            "collected_info": self.collected_info,
            "search_results": self.search_results,
            "search_quality": self.search_quality,
            "validate_results": self.validate_results,
            "recommendations": self.recommendations,
            "booking_confirmation": self.booking_confirmation,
            "final_plan": self.final_plan,
            "error": self.error,
            "retry_count": self.retry_count,
            "error_details": self.error_details,
            "status": self.status,
            "should_retry": self.should_retry,
            "workflow_path": self.workflow_path
        }


class SimpleDeepAgent:
    """简化版 DeepAgent"""
    
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        
    async def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """模拟 DeepAgent 调用"""
        # 这里可以替换为实际的 LLM 调用
        # 目前返回模拟结果
        return {
            "content": f"模拟 DeepAgent 响应: {inputs.get('task', '无任务')}",
            "success": True
        }


class MinimalHybridWorkflow:
    """最小化混合工作流"""
    
    def __init__(self):
        self.token_tracker = TokenTracker()
        self.deep_agents = {
            "search": SimpleDeepAgent("搜索专家"),
            "recommend": SimpleDeepAgent("推荐专家")
        }
        app_logger.info("MinimalHybridWorkflow initialized")
        
    def _should_continue_after_search(self, state: WorkflowState) -> str:
        """搜索后的分支决策"""
        if state.error:
            return "error"
            
        if state.search_quality < settings.workflow_quality_threshold:
            return "retry"
            
        return "good"
    
    def _should_recommend(self, state: WorkflowState) -> str:
        """验证后的分支决策"""
        if state.error:
            return "error"
            
        if state.validate_results.get("validation_passed", False):
            return "success"
        else:
            return "error"
    
    def _should_book(self, state: WorkflowState) -> str:
        """推荐后的分支决策"""
        if state.error:
            return "error"
            
        recommendation_count = len(state.recommendations.get("recommendations", []))
        
        if recommendation_count > 0:
            return "yes"
        else:
            return "no"
    
    def _should_retry_error(self, error: Optional[str]) -> bool:
        """判断错误是否应该重试"""
        if not error:
            return False
            
        # 网络错误可以重试
        if any(keyword in error.lower() for keyword in ["network", "timeout", "connection"]):
            return True
            
        # 搜索质量低可以重试
        if "quality" in error.lower() or "搜索" in error:
            return True
            
        return False
    
    async def _collect_info(self, state: WorkflowState) -> WorkflowState:
        """节点：信息收集"""
        node_name = "collect_info"
        self.token_tracker.start_node(node_name)
        
        try:
            app_logger.info(f"[{state.request_id}] Starting collect_info node")
            
            # 模拟信息收集
            collected_info = {
                "destination": "北京",
                "duration_days": 5,
                "budget": 3000.0,
                "interests": ["文化", "历史"],
                "accommodation_type": "mid-range",
                "travel_pace": "moderate"
            }
            
            state.collected_info = collected_info
            state.stage = "info_collected"
            state.workflow_path.append(node_name)
            
            self.token_tracker.end_node(node_name, 
                                      input_tokens=len(state.user_message) // 4,
                                      output_tokens=len(str(collected_info)) // 4,
                                      success=True)
                                      
            app_logger.info(f"[{state.request_id}] collect_info completed")
            return state
            
        except Exception as e:
            error_msg = f"信息收集失败: {str(e)}"
            app_logger.error(f"[{state.request_id}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            state.error = error_msg
            state.status = "failed"
            state.stage = "error"
            state.error_details = {"node": node_name, "error": str(e)}
            state.workflow_path.append(node_name)
            return state
    
    async def _search_with_deep_agent(self, state: WorkflowState) -> WorkflowState:
        """节点：DeepAgent 搜索"""
        node_name = "search"
        self.token_tracker.start_node(node_name)
        
        try:
            app_logger.info(f"[{state.request_id}] Starting DeepAgent search")
            
            # 使用模拟 DeepAgent
            search_agent = self.deep_agents["search"]
            result = await search_agent.invoke({
                "task": "搜索旅游信息",
                "user_message": state.user_message,
                "collected_info": state.collected_info
            })
            
            # 模拟搜索结果
            search_results = {
                "search_strategy": "使用 DeepAgent 深度搜索",
                "search_results": {
                    "destinations": ["故宫", "长城", "天坛"],
                    "hotels": ["王府井大酒店", "胡同客栈"],
                    "attractions": ["故宫博物院", "八达岭长城"]
                },
                "search_quality": 0.75,
                "search_completeness": "搜索完成"
            }
            
            state.search_results = search_results
            state.search_quality = search_results["search_quality"]
            state.stage = "search_completed"
            state.workflow_path.append(node_name)
            
            # 估算 token 使用量
            input_tokens = len(json.dumps({
                "user_message": state.user_message,
                "collected_info": state.collected_info
            })) // 4
            output_tokens = len(json.dumps(search_results)) // 4
            
            self.token_tracker.end_node(node_name, 
                                      input_tokens=input_tokens,
                                      output_tokens=output_tokens,
                                      success=True)
                                      
            app_logger.info(f"[{state.request_id}] DeepAgent search completed, quality: {state.search_quality}")
            return state
            
        except Exception as e:
            error_msg = f"DeepAgent 搜索失败: {str(e)}"
            app_logger.error(f"[{state.request_id}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            state.error = error_msg
            state.search_quality = 0.0
            state.stage = "search_failed"
            state.error_details = {"node": node_name, "error": str(e)}
            state.workflow_path.append(node_name)
            return state
    
    async def _validate_results(self, state: WorkflowState) -> WorkflowState:
        """节点：结果验证"""
        node_name = "validate_results"
        self.token_tracker.start_node(node_name)
        
        try:
            app_logger.info(f"[{state.request_id}] Starting validate_results")
            
            # 验证逻辑
            validation_results = {
                "search_quality": state.search_quality,
                "validation_passed": state.search_quality >= settings.workflow_quality_threshold,
                "issues": [],
                "recommendations": []
            }
            
            # 检查搜索质量
            if state.search_quality < 0.3:
                validation_results["issues"].append("搜索质量过低")
            elif state.search_quality < 0.6:
                validation_results["issues"].append("搜索质量偏低")
                
            # 检查搜索结果完整性
            if not state.search_results:
                validation_results["issues"].append("搜索结果为空")
            elif "search_results" not in state.search_results:
                validation_results["issues"].append("搜索结果格式异常")
                
            # 生成验证建议
            if not validation_results["validation_passed"]:
                validation_results["recommendations"].append("建议重新搜索")
                
            state.validate_results = validation_results
            state.stage = "validation_completed"
            state.workflow_path.append(node_name)
            
            self.token_tracker.end_node(node_name, success=True)
            
            app_logger.info(f"[{state.request_id}] validate_results completed, passed: {validation_results['validation_passed']}")
            return state
            
        except Exception as e:
            error_msg = f"结果验证失败: {str(e)}"
            app_logger.error(f"[{state.request_id}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            state.error = error_msg
            state.validate_results = {"validation_passed": False, "issues": [str(e)]}
            state.stage = "validation_failed"
            state.error_details = {"node": node_name, "error": str(e)}
            state.workflow_path.append(node_name)
            return state
    
    async def _recommend_with_deep_agent(self, state: WorkflowState) -> WorkflowState:
        """节点：DeepAgent 推荐"""
        node_name = "recommend"
        self.token_tracker.start_node(node_name)
        
        try:
            app_logger.info(f"[{state.request_id}] Starting DeepAgent recommendation")
            
            # 使用模拟 DeepAgent
            recommend_agent = self.deep_agents["recommend"]
            result = await recommend_agent.invoke({
                "task": "生成旅游推荐",
                "user_message": state.user_message,
                "collected_info": state.collected_info,
                "search_results": state.search_results
            })
            
            # 模拟推荐结果
            recommendations = {
                "recommendation_strategy": "使用 DeepAgent 深度推荐",
                "user_analysis": "基于用户偏好分析",
                "recommendations": [
                    {
                        "id": "plan_1",
                        "title": "北京经典5日游",
                        "summary": "包含故宫、长城、天坛等经典景点",
                        "score": 0.92,
                        "strengths": ["经典景点", "文化体验"],
                        "estimated_cost": "3000-4000元",
                        "best_for": "文化爱好者"
                    },
                    {
                        "id": "plan_2", 
                        "title": "北京深度游",
                        "summary": "更深入的文化和历史体验",
                        "score": 0.88,
                        "strengths": ["深度体验", "小众景点"],
                        "estimated_cost": "4000-5000元",
                        "best_for": "深度旅行者"
                    }
                ],
                "recommendation_quality": 0.90
            }
            
            state.recommendations = recommendations
            state.stage = "recommendation_completed"
            state.workflow_path.append(node_name)
            
            # 估算 token 使用量
            input_tokens = len(json.dumps({
                "user_message": state.user_message,
                "collected_info": state.collected_info,
                "search_results": state.search_results
            })) // 4
            output_tokens = len(json.dumps(recommendations)) // 4
            
            self.token_tracker.end_node(node_name,
                                      input_tokens=input_tokens,
                                      output_tokens=output_tokens,
                                      success=True)
                                      
            app_logger.info(f"[{state.request_id}] DeepAgent recommendation completed")
            return state
            
        except Exception as e:
            error_msg = f"DeepAgent 推荐失败: {str(e)}"
            app_logger.error(f"[{state.request_id}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            state.error = error_msg
            state.recommendations = {"recommendations": [], "recommendation_quality": 0.0}
            state.stage = "recommendation_failed"
            state.error_details = {"node": node_name, "error": str(e)}
            state.workflow_path.append(node_name)
            return state
    
    async def _book(self, state: WorkflowState) -> WorkflowState:
        """节点：预订处理"""
        node_name = "book"
        self.token_tracker.start_node(node_name)
        
        try:
            app_logger.info(f"[{state.request_id}] Starting booking")
            
            # 模拟预订结果
            booking_confirmation = {
                "booking_status": "demo_confirmed",
                "booking_id": f"demo_{int(time.time())}",
                "booked_items": [
                    {
                        "type": "酒店",
                        "details": "王府井大酒店 - 4晚",
                        "price": "1200元",
                        "booking_time": "2024-01-15"
                    },
                    {
                        "type": "景点门票",
                        "details": "故宫博物院 + 八达岭长城",
                        "price": "200元",
                        "booking_time": "2024-01-15"
                    }
                ],
                "total_cost": "1400元",
                "confirmation_details": "预订确认（演示版）"
            }
            
            # 生成最终计划
            final_plan = {
                "user_requirements": state.user_message,
                "collected_info": state.collected_info,
                "search_results": state.search_results,
                "recommendations": state.recommendations,
                "booking_confirmation": booking_confirmation,
                "workflow_summary": {
                    "stages_completed": state.workflow_path,
                    "total_tokens": self.token_tracker.get_total_tokens(),
                    "workflow_success": True
                }
            }
            
            state.booking_confirmation = booking_confirmation
            state.final_plan = final_plan
            state.stage = "booking_completed"
            state.status = "completed"
            state.workflow_path.append(node_name)
            
            self.token_tracker.end_node(node_name, success=True)
            
            app_logger.info(f"[{state.request_id}] Booking completed successfully")
            return state
            
        except Exception as e:
            error_msg = f"预订处理失败: {str(e)}"
            app_logger.error(f"[{state.request_id}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            state.error = error_msg
            state.booking_confirmation = {"booking_status": "failed"}
            state.final_plan = {
                "user_requirements": state.user_message,
                "error": error_msg,
                "workflow_summary": {
                    "stages_completed": state.workflow_path,
                    "workflow_success": False
                }
            }
            state.stage = "booking_failed"
            state.status = "failed"
            state.error_details = {"node": node_name, "error": str(e)}
            state.workflow_path.append(node_name)
            return state
    
    async def _handle_error(self, state: WorkflowState) -> WorkflowState:
        """节点：错误处理和重试"""
        node_name = "handle_error"
        self.token_tracker.start_node(node_name)
        
        try:
            app_logger.info(f"[{state.request_id}] Starting error handling")
            
            # 判断是否应该重试
            should_retry = (
                state.retry_count < settings.workflow_max_retries and
                self._should_retry_error(state.error)
            )
            
            state.should_retry = should_retry
            state.retry_count = state.retry_count + 1 if should_retry else state.retry_count
            state.stage = "error_handled"
            state.status = "running" if should_retry else "failed"
            state.workflow_path.append(node_name)
            
            if should_retry:
                app_logger.info(f"[{state.request_id}] Will retry workflow (attempt {state.retry_count})")
                # 清除错误信息，重新开始
                state.error = None
                state.error_details = {}
            else:
                app_logger.warning(f"[{state.request_id}] Workflow failed after {state.retry_count} retries")
                
            self.token_tracker.end_node(node_name, success=True)
            
            return state
            
        except Exception as e:
            error_msg = f"错误处理失败: {str(e)}"
            app_logger.error(f"[{state.request_id}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            state.error = error_msg
            state.should_retry = False
            state.stage = "error_handling_failed"
            state.status = "failed"
            state.workflow_path.append(node_name)
            return state
    
    async def run(self, user_message: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """运行最小化混合工作流"""
        request_id = f"hybrid_{int(time.time())}"
        
        try:
            # 初始化追踪
            self.token_tracker.start_request(request_id)
            
            # 构建初始状态
            state = WorkflowState(
                user_message=user_message,
                request_id=request_id,
                stage="starting",
                timestamp=time.time(),
                collected_info=metadata or {},
                status="running"
            )
            
            app_logger.info(f"[{request_id}] Starting minimal hybrid workflow")
            
            # 按顺序执行节点
            execution_order = [
                self._collect_info,
                self._search_with_deep_agent,
                self._validate_results,
                self._recommend_with_deep_agent,
                self._book
            ]
            
            for node_func in execution_order:
                # 检查是否需要重试
                if state.should_retry:
                    state.should_retry = False
                    # 重新开始流程
                    continue
                    
                # 检查是否有错误
                if state.error:
                    state = await self._handle_error(state)
                    if not state.should_retry:
                        break
                    else:
                        state.error = None
                        state.error_details = {}
                        continue
                
                # 执行节点
                try:
                    state = await node_func(state)
                    
                    # 检查条件分支
                    if node_func == self._search_with_deep_agent:
                        decision = self._should_continue_after_search(state)
                        if decision == "retry":
                            state.should_retry = True
                        elif decision == "error":
                            state.error = "搜索质量不足"
                            continue
                    elif node_func == self._validate_results:
                        if not state.validate_results.get("validation_passed", False):
                            state.error = "验证失败"
                            continue
                    elif node_func == self._recommend_with_deep_agent:
                        if not state.recommendations.get("recommendations"):
                            # 推荐为空，结束工作流
                            break
                            
                except Exception as e:
                    state.error = str(e)
                    state = await self._handle_error(state)
                    if not state.should_retry:
                        break
            
            # 添加性能报告
            result_dict = state.to_dict()
            result_dict["token_report"] = self.token_tracker.generate_report()
            result_dict["efficiency_score"] = self.token_tracker.get_efficiency_score()
            
            app_logger.info(f"[{request_id}] Minimal hybrid workflow completed: {state.status}")
            return result_dict
            
        except Exception as e:
            error_msg = f"最小化混合工作流执行失败: {str(e)}"
            app_logger.error(f"[{request_id}] {error_msg}")
            
            return {
                "user_message": user_message,
                "request_id": request_id,
                "status": "failed",
                "error": error_msg,
                "token_report": self.token_tracker.generate_report(),
                "efficiency_score": 0.0
            }
        
        finally:
            self.token_tracker.reset()


# 全局实例
_minimal_workflow: Optional[MinimalHybridWorkflow] = None


async def get_minimal_workflow() -> MinimalHybridWorkflow:
    """获取最小化工作流实例"""
    global _minimal_workflow
    
    if _minimal_workflow is None:
        _minimal_workflow = MinimalHybridWorkflow()
        
    return _minimal_workflow


async def cleanup_workflow():
    """清理工作流资源"""
    global _minimal_workflow
    
    if _minimal_workflow:
        _minimal_workflow = None