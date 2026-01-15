"""
LangGraph + DeepAgent 混合工作流
结合 LangGraph 的流程控制优势和 DeepAgent 的深度推理能力
支持多模型分层调用（便宜/标准/强力）
"""
import asyncio
import json
import time
from typing import Any, Dict, List, Optional, TypedDict

# 简化的图管理（适配当前 langgraph 版本）
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    # 如果 langgraph 不可用，创建简化版本
    LANGGRAPH_AVAILABLE = False
    print("⚠️ LangGraph not available, using simplified workflow")

from langchain_experimental import create_agent

from utils.token_tracker import TokenTracker
from utils.logger import app_logger
from config import settings
from config.llm_config import LLMFactory, ModelTier
from agents.deep_subagents import get_deep_agents_manager
from agents.mcp_tools_helper import get_mcp_tools_manager

# 工作流状态定义
class HybridWorkflowState(TypedDict, total=False):
    # 基础状态
    user_message: str
    request_id: str
    stage: str
    timestamp: float
    
    # 数据流转
    collected_info: Dict[str, Any]
    search_results: Dict[str, Any]
    search_quality: float
    validate_results: Dict[str, Any]
    recommendations: Dict[str, Any]
    booking_confirmation: Dict[str, Any]
    final_plan: Dict[str, Any]
    
    # 错误处理
    error: Optional[str]
    retry_count: int
    error_details: Dict[str, Any]
    
    # 执行控制
    status: str  # pending, running, completed, failed, retrying
    should_retry: bool
    workflow_path: List[str]  # 追踪执行路径


class SimpleWorkflowManager:
    """简化的工作流管理器（当 LangGraph 不可用时使用）"""
    
    def __init__(self):
        self.nodes = {
            "collect_info": self._collect_info,
            "search": self._search_with_deep_agent,
            "validate_results": self._validate_results,
            "recommend": self._recommend_with_deep_agent,
            "book": self._book,
            "handle_error": self._handle_error
        }
    
    async def ainvoke(self, initial_state: HybridWorkflowState) -> HybridWorkflowState:
        """简化的工作流执行"""
        current_state = initial_state.copy()
        current_state["status"] = "running"
        
        # 按顺序执行节点
        execution_order = [
            "collect_info",
            "search", 
            "validate_results",
            "recommend",
            "book"
        ]
        
        for node_name in execution_order:
            # 检查是否需要重试
            if current_state.get("should_retry"):
                current_state["should_retry"] = False
                # 重新开始流程
                continue
                
            # 检查是否有错误
            if current_state.get("error"):
                current_state = await self._handle_error(current_state)
                if not current_state.get("should_retry", False):
                    break
                else:
                    current_state["error"] = None
                    current_state["error_details"] = {}
                    continue
            
            # 执行节点
            try:
                node_func = self.nodes.get(node_name)
                if node_func:
                    current_state = await node_func(current_state)
                    
                    # 检查条件分支
                    if node_name == "search":
                        decision = self._should_continue_after_search(current_state)
                        if decision == "retry":
                            current_state["should_retry"] = True
                        elif decision == "error":
                            current_state["error"] = "搜索质量不足"
                            continue
                    elif node_name == "validate_results":
                        if not current_state.get("validate_results", {}).get("validation_passed", False):
                            current_state["error"] = "验证失败"
                            continue
                    elif node_name == "recommend":
                        if not current_state.get("recommendations", {}).get("recommendations"):
                            # 推荐为空，结束工作流
                            break
                            
            except Exception as e:
                current_state["error"] = str(e)
                current_state = await self._handle_error(current_state)
                if not current_state.get("should_retry", False):
                    break
        
        current_state["status"] = "completed"
        return current_state


class HybridTravelWorkflow:
    """LangGraph + DeepAgent 混合工作流"""
    
    def __init__(self):
        """
        初始化混合工作流
        
        使用 LLMFactory 创建三层 LLM 实例：
        - cheap_llm: 便宜层 - 用于简单任务（信息收集、预订）
        - standard_llm: 标准层 - 用于中等复杂任务（搜索、推荐）
        - power_llm: 强力层 - 用于复杂推理任务
        """
        # 获取配置
        cheap_provider = getattr(settings, 'llm_cheap_provider', 'deepseek')
        standard_provider = getattr(settings, 'llm_standard_provider', 'qwen-turbo')
        power_provider = getattr(settings, 'llm_power_provider', 'claude')
        
        # 温度参数
        temperature = getattr(settings, 'llm_temperature', 0.7)
        max_tokens = getattr(settings, 'llm_max_tokens', 4096)
        
        # 创建三层 LLM 实例
        self.cheap_llm = LLMFactory.create_llm(
            cheap_provider, 
            ModelTier.CHEAP,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.standard_llm = LLMFactory.create_llm(
            standard_provider, 
            ModelTier.STANDARD,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.power_llm = LLMFactory.create_llm(
            power_provider, 
            ModelTier.POWER,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # 记录使用的模型信息
        self.llm_info = {
            "cheap": {
                "provider": cheap_provider,
                "tier": "cheap"
            },
            "standard": {
                "provider": standard_provider,
                "tier": "standard"
            },
            "power": {
                "provider": power_provider,
                "tier": "power"
            }
        }
        
        app_logger.info(f"LLM instances created: {self.llm_info}")
        
        # 初始化组件
        self.token_tracker = TokenTracker()
        self.deep_agents_manager = None
        self.mcp_tools_manager = None
        self._llm_initialized = False
        
        # 构建工作流图
        if LANGGRAPH_AVAILABLE:
            self.graph = self._build_graph()
        else:
            self.graph = SimpleWorkflowManager()
        
        app_logger.info("HybridTravelWorkflow initialized with multi-tier LLMs")
        
    async def initialize(self):
        """异步初始化"""
        # 初始化 DeepAgents 管理器，使用标准层 LLM
        if self.deep_agents_manager is None:
            # DeepAgent 使用标准层或强力层 LLM
            deepagent_tier_str = getattr(settings, 'deepagent_search_tier', 'standard')
            try:
                deepagent_tier = ModelTier(deepagent_tier_str)
            except ValueError:
                deepagent_tier = ModelTier.STANDARD
            
            # 根据 tier 选择 LLM
            if deepagent_tier == ModelTier.POWER:
                deepagent_llm = self.power_llm
            elif deepagent_tier == ModelTier.CHEAP:
                deepagent_llm = self.cheap_llm
            else:
                deepagent_llm = self.standard_llm
            
            self.deep_agents_manager = await get_deep_agents_manager(deepagent_llm)
            
        if self.mcp_tools_manager is None:
            self.mcp_tools_manager = await get_mcp_tools_manager()
            
        self._llm_initialized = True
        app_logger.info("HybridTravelWorkflow async components initialized")
    
    def _build_graph(self):
        """构建 LangGraph 工作流"""
        if not LANGGRAPH_AVAILABLE:
            return None
            
        workflow = StateGraph(HybridWorkflowState)
        
        # 添加节点
        workflow.add_node("collect_info", self._collect_info)
        workflow.add_node("search", self._search_with_deep_agent)
        workflow.add_node("validate_results", self._validate_results)
        workflow.add_node("recommend", self._recommend_with_deep_agent)
        workflow.add_node("book", self._book)
        workflow.add_node("handle_error", self._handle_error)
        
        # 设置入口点
        workflow.set_entry_point("collect_info")
        
        # 添加边和条件分支
        workflow.add_conditional_edges(
            "search",
            self._should_continue_after_search,
            {
                "good": "validate_results",
                "retry": "search", 
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "validate_results",
            self._should_recommend,
            {
                "success": "recommend",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "recommend", 
            self._should_book,
            {
                "yes": "book",
                "no": END,
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "handle_error",
            self._should_retry_workflow,
            {
                "retry": "collect_info",  # 重试整个流程
                "end": END
            }
        )
        
        # 添加普通边
        workflow.add_edge("collect_info", "search")
        workflow.add_edge("validate_results", "recommend")
        workflow.add_edge("book", END)
        
        return workflow.compile()
    
    async def _collect_info(self, state: HybridWorkflowState) -> HybridWorkflowState:
        """节点：信息收集（使用便宜层 LLM）"""
        node_name = "collect_info"
        start_time = self.token_tracker.start_node(node_name)
        
        try:
            app_logger.info(f"[{state.get('request_id')}] Starting collect_info node (using cheap LLM)")
            
            # 信息收集系统提示词（静态，便于 Prompt Cache）
            INFO_COLLECTION_PROMPT = """你是一个专业的信息收集专家。

任务：从用户输入中提取结构化的旅游信息

输出格式（JSON）：
{
    "destination": "目的地",
    "duration_days": 天数,
    "budget": 预算数值,
    "travel_date": "出行日期",
    "interests": ["兴趣1", "兴趣2"],
    "accommodation_type": "住宿偏好",
    "travel_pace": "旅行节奏",
    "travelers_count": 人数,
    "special_requirements": "特殊要求"
}

要求：
1. 提取所有可见的旅游相关信息
2. 对于缺失的信息，设置为 null
3. 保持信息的原始性和准确性
4. 使用中文输出"""

            # 创建信息收集代理（使用 cheap_llm）
            info_agent = create_agent(
                model=self.cheap_llm,
                tools=[],
                system_prompt=INFO_COLLECTION_PROMPT
            )
            
            # 执行信息收集
            result = await info_agent.ainvoke({
                "input": state["user_message"]
            })
            
            # 解析结果
            content = result.content if hasattr(result, 'content') else str(result)
            
            try:
                collected_info = json.loads(content)
            except json.JSONDecodeError:
                collected_info = {
                    "destination": "待定",
                    "duration_days": 5,
                    "budget": 2000.0,
                    "interests": [],
                    "raw_content": content
                }
                
            # 更新状态
            updated_state = {
                **state,
                "collected_info": collected_info,
                "stage": "info_collected",
                "status": "running",
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
            
            self.token_tracker.end_node(node_name, 
                                      input_tokens=len(state["user_message"]) // 4,
                                      output_tokens=len(str(collected_info)) // 4,
                                      success=True)
                                      
            app_logger.info(f"[{state.get('request_id')}] collect_info completed")
            return updated_state
            
        except Exception as e:
            error_msg = f"信息收集失败: {str(e)}"
            app_logger.error(f"[{state.get('request_id')}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            return {
                **state,
                "error": error_msg,
                "status": "failed",
                "stage": "error",
                "error_details": {"node": node_name, "error": str(e)},
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
    
    async def _search_with_deep_agent(self, state: HybridWorkflowState) -> HybridWorkflowState:
        """节点：DeepAgent 搜索"""
        node_name = "search"
        start_time = self.token_tracker.start_node(node_name)
        
        try:
            request_id = state.get('request_id')
            app_logger.info(f"[{request_id}] Starting DeepAgent search")
            
            # 确保 DeepAgent 已初始化
            if self.deep_agents_manager is None:
                await self.initialize()
                
            # 使用 DeepAgent 执行搜索
            search_results = await self.deep_agents_manager.search_with_deep_agent(
                state["user_message"],
                state["collected_info"]
            )
            
            # 提取搜索质量
            search_quality = search_results.get("search_quality", 0.5)
            
            updated_state = {
                **state,
                "search_results": search_results,
                "search_quality": search_quality,
                "stage": "search_completed",
                "status": "running",
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
            
            # 估算 token 使用量
            input_tokens = len(json.dumps({
                "user_message": state["user_message"],
                "collected_info": state["collected_info"]
            })) // 4
            output_tokens = len(json.dumps(search_results)) // 4
            
            self.token_tracker.end_node(node_name, 
                                      input_tokens=input_tokens,
                                      output_tokens=output_tokens,
                                      success=True)
                                      
            app_logger.info(f"[{request_id}] DeepAgent search completed, quality: {search_quality}")
            return updated_state
            
        except Exception as e:
            error_msg = f"DeepAgent 搜索失败: {str(e)}"
            app_logger.error(f"[{state.get('request_id')}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            return {
                **state,
                "error": error_msg,
                "search_quality": 0.0,
                "stage": "search_failed",
                "status": "running",  # 搜索失败不直接标记为失败，可能需要重试
                "error_details": {"node": node_name, "error": str(e)},
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
    
    async def _validate_results(self, state: HybridWorkflowState) -> HybridWorkflowState:
        """节点：结果验证"""
        node_name = "validate_results"
        start_time = self.token_tracker.start_node(node_name)
        
        try:
            request_id = state.get('request_id')
            app_logger.info(f"[{request_id}] Starting validate_results")
            
            # 验证逻辑
            search_quality = state.get("search_quality", 0.0)
            search_results = state.get("search_results", {})
            
            validation_results = {
                "search_quality": search_quality,
                "validation_passed": search_quality >= settings.workflow_quality_threshold,
                "issues": [],
                "recommendations": []
            }
            
            # 检查搜索质量
            if search_quality < 0.3:
                validation_results["issues"].append("搜索质量过低")
            elif search_quality < 0.6:
                validation_results["issues"].append("搜索质量偏低")
                
            # 检查搜索结果完整性
            if not search_results:
                validation_results["issues"].append("搜索结果为空")
            elif "search_results" not in search_results:
                validation_results["issues"].append("搜索结果格式异常")
                
            # 生成验证建议
            if not validation_results["validation_passed"]:
                validation_results["recommendations"].append("建议重新搜索")
                
            updated_state = {
                **state,
                "validate_results": validation_results,
                "stage": "validation_completed",
                "status": "running",
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
            
            self.token_tracker.end_node(node_name, success=True)
            
            app_logger.info(f"[{request_id}] validate_results completed, passed: {validation_results['validation_passed']}")
            return updated_state
            
        except Exception as e:
            error_msg = f"结果验证失败: {str(e)}"
            app_logger.error(f"[{state.get('request_id')}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            return {
                **state,
                "error": error_msg,
                "validate_results": {"validation_passed": False, "issues": [str(e)]},
                "stage": "validation_failed",
                "status": "running",
                "error_details": {"node": node_name, "error": str(e)},
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
    
    async def _recommend_with_deep_agent(self, state: HybridWorkflowState) -> HybridWorkflowState:
        """节点：DeepAgent 推荐"""
        node_name = "recommend"
        start_time = self.token_tracker.start_node(node_name)
        
        try:
            request_id = state.get('request_id')
            app_logger.info(f"[{request_id}] Starting DeepAgent recommendation")
            
            # 确保 DeepAgent 已初始化
            if self.deep_agents_manager is None:
                await self.initialize()
                
            # 使用 DeepAgent 执行推荐
            recommendations = await self.deep_agents_manager.recommend_with_deep_agent(
                state["user_message"],
                state["collected_info"],
                state["search_results"]
            )
            
            updated_state = {
                **state,
                "recommendations": recommendations,
                "stage": "recommendation_completed",
                "status": "running",
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
            
            # 估算 token 使用量
            input_tokens = len(json.dumps({
                "user_message": state["user_message"],
                "collected_info": state["collected_info"],
                "search_results": state["search_results"]
            })) // 4
            output_tokens = len(json.dumps(recommendations)) // 4
            
            self.token_tracker.end_node(node_name,
                                      input_tokens=input_tokens,
                                      output_tokens=output_tokens,
                                      success=True)
                                      
            app_logger.info(f"[{request_id}] DeepAgent recommendation completed")
            return updated_state
            
        except Exception as e:
            error_msg = f"DeepAgent 推荐失败: {str(e)}"
            app_logger.error(f"[{state.get('request_id')}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            return {
                **state,
                "error": error_msg,
                "recommendations": {"recommendations": [], "recommendation_quality": 0.0},
                "stage": "recommendation_failed",
                "status": "running",
                "error_details": {"node": node_name, "error": str(e)},
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
    
    async def _book(self, state: HybridWorkflowState) -> HybridWorkflowState:
        """节点：预订处理（使用便宜层 LLM）"""
        node_name = "book"
        start_time = self.token_tracker.start_node(node_name)
        
        try:
            request_id = state.get('request_id')
            app_logger.info(f"[{request_id}] Starting booking (using cheap LLM)")
            
            # 预订系统提示词（静态）
            BOOKING_PROMPT = """你是一个专业的旅游预订专家。

任务：处理旅游预订请求

输入信息：
- 用户需求：{user_message}
- 收集信息：{collected_info}
- 推荐方案：{recommendations}

处理步骤：
1. 分析推荐方案，确定预订选项
2. 模拟预订流程（注意：这是演示版本）
3. 生成预订确认信息

返回格式（JSON）：
{
    "booking_status": "confirmed",
    "booking_id": "预订ID",
    "booked_items": [
        {
            "type": "酒店/机票/景点",
            "details": "具体信息",
            "price": "价格",
            "booking_time": "预订时间"
        }
    ],
    "total_cost": "总费用",
    "confirmation_details": "确认详情"
}

注意：这是演示版本，实际预订需要连接真实的预订系统。"""

            # 创建预订代理（使用 cheap_llm）
            booking_agent = create_agent(
                model=self.cheap_llm,
                tools=[],
                system_prompt=BOOKING_PROMPT
            )
            
            # 执行预订
            result = await booking_agent.ainvoke({
                "input": "请处理预订请求",
                "user_message": state["user_message"],
                "collected_info": state["collected_info"],
                "recommendations": state["recommendations"]
            })
            
            # 解析结果
            content = result.content if hasattr(result, 'content') else str(result)
            
            try:
                booking_confirmation = json.loads(content)
            except json.JSONDecodeError:
                booking_confirmation = {
                    "booking_status": "demo_confirmed",
                    "booking_id": f"demo_{int(time.time())}",
                    "booked_items": [],
                    "total_cost": "待确认",
                    "confirmation_details": content[:200] + "..." if len(content) > 200 else content
                }
            
            # 生成最终计划
            final_plan = {
                "user_requirements": state["user_message"],
                "collected_info": state["collected_info"],
                "search_results": state["search_results"],
                "recommendations": state["recommendations"],
                "booking_confirmation": booking_confirmation,
                "workflow_summary": {
                    "stages_completed": state.get("workflow_path", []),
                    "total_tokens": self.token_tracker.get_total_tokens(),
                    "workflow_success": True
                }
            }
            
            updated_state = {
                **state,
                "booking_confirmation": booking_confirmation,
                "final_plan": final_plan,
                "stage": "booking_completed",
                "status": "completed",
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
            
            self.token_tracker.end_node(node_name, success=True)
            
            app_logger.info(f"[{request_id}] Booking completed successfully")
            return updated_state
            
        except Exception as e:
            error_msg = f"预订处理失败: {str(e)}"
            app_logger.error(f"[{state.get('request_id')}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            return {
                **state,
                "error": error_msg,
                "booking_confirmation": {"booking_status": "failed"},
                "final_plan": {
                    "user_requirements": state["user_message"],
                    "error": error_msg,
                    "workflow_summary": {
                        "stages_completed": state.get("workflow_path", []),
                        "workflow_success": False
                    }
                },
                "stage": "booking_failed",
                "status": "failed",
                "error_details": {"node": node_name, "error": str(e)},
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
    
    async def _handle_error(self, state: HybridWorkflowState) -> HybridWorkflowState:
        """节点：错误处理和重试"""
        node_name = "handle_error"
        start_time = self.token_tracker.start_node(node_name)
        
        try:
            request_id = state.get('request_id')
            app_logger.info(f"[{request_id}] Starting error handling")
            
            current_retry_count = state.get("retry_count", 0)
            error = state.get("error")
            error_details = state.get("error_details", {})
            
            # 判断是否应该重试
            should_retry = (
                current_retry_count < settings.workflow_max_retries and
                self._should_retry_error(error, error_details)
            )
            
            updated_state = {
                **state,
                "should_retry": should_retry,
                "retry_count": current_retry_count + 1 if should_retry else current_retry_count,
                "stage": "error_handled",
                "status": "running" if should_retry else "failed",
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
            
            if should_retry:
                app_logger.info(f"[{request_id}] Will retry workflow (attempt {current_retry_count + 1})")
                # 清除错误信息，重新开始
                updated_state.update({
                    "error": None,
                    "error_details": {}
                })
            else:
                app_logger.warning(f"[{request_id}] Workflow failed after {current_retry_count} retries")
                
            self.token_tracker.end_node(node_name, success=True)
            
            return updated_state
            
        except Exception as e:
            error_msg = f"错误处理失败: {str(e)}"
            app_logger.error(f"[{state.get('request_id')}] {error_msg}")
            
            self.token_tracker.end_node(node_name, success=False, error_message=str(e))
            
            return {
                **state,
                "error": error_msg,
                "should_retry": False,
                "stage": "error_handling_failed",
                "status": "failed",
                "workflow_path": state.get("workflow_path", []) + [node_name]
            }
    
    # 条件分支决策函数
    def _should_continue_after_search(self, state: HybridWorkflowState) -> str:
        """搜索后的分支决策"""
        if state.get("error"):
            return "error"
            
        search_quality = state.get("search_quality", 0.0)
        if search_quality < settings.workflow_quality_threshold:
            return "retry"
            
        return "good"
    
    def _should_recommend(self, state: HybridWorkflowState) -> str:
        """验证后的分支决策"""
        if state.get("error"):
            return "error"
            
        validation_results = state.get("validate_results", {})
        if validation_results.get("validation_passed", False):
            return "success"
        else:
            return "error"
    
    def _should_book(self, state: HybridWorkflowState) -> str:
        """推荐后的分支决策"""
        if state.get("error"):
            return "error"
            
        recommendations = state.get("recommendations", {})
        recommendation_count = len(recommendations.get("recommendations", []))
        
        if recommendation_count > 0:
            return "yes"
        else:
            return "no"
    
    def _should_retry_workflow(self, state: HybridWorkflowState) -> str:
        """错误处理后的分支决策"""
        if state.get("should_retry", False):
            return "retry"
        else:
            return "end"
    
    def _should_retry_error(self, error: Optional[str], error_details: Dict[str, Any]) -> bool:
        """判断错误是否应该重试"""
        if not error:
            return False
            
        # 网络错误可以重试
        if any(keyword in error.lower() for keyword in ["network", "timeout", "connection"]):
            return True
            
        # DeepAgent 错误可以重试
        if "deepagent" in error.lower():
            return True
            
        # 搜索质量低可以重试
        if "quality" in error.lower() or "搜索" in error:
            return True
            
        # 临时错误可以重试
        if any(keyword in error.lower() for keyword in ["temporary", "retry", "rate limit"]):
            return True
            
        return False
    
    async def run(self, user_message: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """运行混合工作流"""
        request_id = f"hybrid_{int(time.time())}"
        
        try:
            # 初始化追踪
            self.token_tracker.start_request(request_id)
            
            # 初始化组件
            await self.initialize()
            
            # 构建初始状态
            initial_state: HybridWorkflowState = {
                "user_message": user_message,
                "request_id": request_id,
                "stage": "starting",
                "timestamp": time.time(),
                "collected_info": metadata or {},
                "search_results": {},
                "recommendations": {},
                "booking_confirmation": {},
                "final_plan": {},
                "error": None,
                "retry_count": 0,
                "error_details": {},
                "status": "pending",
                "should_retry": False,
                "workflow_path": []
            }
            
            app_logger.info(f"[{request_id}] Starting hybrid workflow")
            
            # 执行工作流
            if hasattr(self.graph, 'ainvoke'):
                result = await self.graph.ainvoke(initial_state)
            else:
                # 使用简化的工作流管理器
                result = await self.graph.ainvoke(initial_state)
            
            # 添加性能报告和 LLM 配置信息
            result["token_report"] = self.token_tracker.generate_report()
            result["efficiency_score"] = self.token_tracker.get_efficiency_score()
            result["llm_config"] = self.llm_info  # 添加使用的 LLM 配置信息
            
            app_logger.info(f"[{request_id}] Hybrid workflow completed: {result['status']}")
            return result
            
        except Exception as e:
            error_msg = f"混合工作流执行失败: {str(e)}"
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
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.deep_agents_manager:
                await self.deep_agents_manager.cleanup()
            if self.mcp_tools_manager:
                await self.mcp_tools_manager.cleanup()
            app_logger.info("HybridTravelWorkflow cleaned up")
        except Exception as e:
            app_logger.error(f"Cleanup failed: {e}")


# 全局工作流实例
_hybrid_workflow: Optional[HybridTravelWorkflow] = None


async def get_hybrid_workflow() -> HybridTravelWorkflow:
    """获取混合工作流实例"""
    global _hybrid_workflow
    
    if _hybrid_workflow is None:
        _hybrid_workflow = HybridTravelWorkflow()
        
    return _hybrid_workflow


async def cleanup_hybrid_workflow():
    """清理混合工作流资源"""
    global _hybrid_workflow
    
    if _hybrid_workflow:
        await _hybrid_workflow.cleanup()
        _hybrid_workflow = None