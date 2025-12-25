"""LangGraph 工作流定义

MVP: 依次执行 4 个 Agent:
InfoCollection -> Search -> Recommendation -> Booking

后续可扩展：
- 条件分支（信息不足 -> 追问）
- 多轮迭代搜索与优化
- 工具调用 (MCP)
"""
from typing import Any, Dict, TypedDict
from langgraph.graph import StateGraph, END
from agents import (
    InfoCollectionAgent,
    SearchAgent,
    RecommendationAgent,
    BookingAgent
)
from utils.logger import app_logger


class TravelPlanningState(TypedDict, total=False):
    user_message: str
    collected_info: Dict[str, Any]
    search_results: list[Dict[str, Any]]
    recommendations: list[Dict[str, Any]]
    booking_status: Dict[str, Any]
    final_plan: Dict[str, Any]
    error: str


class PlanningWorkflow:
    def __init__(self):
        self.info_agent = InfoCollectionAgent()
        self.search_agent = SearchAgent()
        self.recommendation_agent = RecommendationAgent()
        self.booking_agent = BookingAgent()

        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(TravelPlanningState)

        workflow.add_node("collect_info", self.info_agent.run)
        workflow.add_node("search", self.search_agent.run)
        workflow.add_node("recommend", self.recommendation_agent.run)
        workflow.add_node("book", self.booking_agent.run)

        workflow.set_entry_point("collect_info")

        workflow.add_edge("collect_info", "search")
        workflow.add_edge("search", "recommend")
        workflow.add_edge("recommend", "book")
        workflow.add_edge("book", END)

        return workflow.compile()

    async def run(self, user_message: str, metadata: Dict[str, Any] | None = None):
        app_logger.info("Starting planning workflow")

        initial_state: TravelPlanningState = {
            "user_message": user_message,
            "collected_info": metadata or {}
        }

        result = await self.graph.ainvoke(initial_state)
        return result
