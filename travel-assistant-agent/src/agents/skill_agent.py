"""
Skill-based Agent for Travel Planning

This agent uses MCP skills to gather information and create travel plans.
"""

from typing import Any, Dict, List, Optional
from .base import BaseAgent
from .mcp_client import MCPClient, MCPSkillResult, get_mcp_client
import logging

logger = logging.getLogger(__name__)


class SkillBasedAgent(BaseAgent):
    """
    Agent that uses MCP skills for travel planning.
    
    This agent demonstrates:
    - Discovering available skills via MCP
    - Invoking skills based on user requests
    - Combining skill outputs to create comprehensive plans
    """
    
    name = "skill_based_agent"
    
    def __init__(self, mcp_client: MCPClient = None):
        self.mcp_client = mcp_client or get_mcp_client()
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process travel request using MCP skills.
        
        Args:
            state: Contains user_message and metadata
            
        Returns:
            Updated state with planning results
        """
        user_message = state.get("user_message", "")
        metadata = state.get("metadata", {}) or {}
        
        logger.info(f"[SkillBasedAgent] Processing: {user_message}")
        
        # Parse the user request
        parsed_request = self._parse_request(user_message, metadata)
        
        # Gather information using skills
        skill_results = await self._gather_information(parsed_request)
        
        # Create travel plan using gathered information
        final_plan = await self._create_plan(parsed_request, skill_results)
        
        return {
            **state,
            "skill_results": skill_results,
            "final_plan": final_plan,
            "agent_used": self.name
        }
    
    def _parse_request(
        self,
        user_message: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse user message into structured request"""
        import re
        
        request = {
            "destination": metadata.get("destination", ""),
            "duration_days": metadata.get("duration_days", 5),
            "budget": metadata.get("budget", 2000),
            "start_date": metadata.get("start_date", ""),
            "end_date": metadata.get("end_date", ""),
            "interests": metadata.get("interests", []),
            "accommodation_type": metadata.get("accommodation_type", "mid-range"),
            "pace": metadata.get("pace", "moderate"),
            "raw_message": user_message
        }
        
        # Try to extract destination from message
        if not request["destination"]:
            dest_match = re.search(
                r"(?:visit|go to|trip to|travel to)\s+([A-Za-z\s]+?)(?:\s+for|\s+with|\s+in|\s*$| \d)",
                user_message,
                re.IGNORECASE
            )
            if dest_match:
                request["destination"] = dest_match.group(1).strip()
        
        # Try to extract duration
        if not request.get("duration_days"):
            day_match = re.search(r"(\d+)\s*(?:days?|nights?)", user_message, re.IGNORECASE)
            if day_match:
                request["duration_days"] = int(day_match.group(1))
        
        # Try to extract budget
        if not request.get("budget"):
            budget_match = re.search(r"\$([\d,]+)", user_message)
            if budget_match:
                request["budget"] = float(budget_match.group(1).replace(",", ""))
        
        return request
    
    async def _gather_information(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, MCPSkillResult]:
        """Gather destination information using MCP skills"""
        results = {}
        destination = request.get("destination", "")
        
        if not destination:
            logger.warning("No destination specified")
            return results
        
        # 1. Search destination info
        logger.info(f"Fetching destination info for {destination}")
        results["destination_info"] = await self.mcp_client.call_skill(
            "search_destination",
            {"destination": destination, "include_tips": True}
        )
        
        # 2. Get pricing
        logger.info(f"Fetching pricing for {destination}")
        results["pricing"] = await self.mcp_client.call_skill(
            "query_prices",
            {
                "destination": destination,
                "check_in": request.get("start_date"),
                "check_out": request.get("end_date"),
                "guests": 2,
                "rooms": 1
            }
        )
        
        # 3. Get reviews
        logger.info(f"Fetching reviews for {destination}")
        results["reviews"] = await self.mcp_client.call_skill(
            "get_destination_reviews",
            {"destination": destination, "limit": 5, "include_sentiment": True}
        )
        
        # 4. Get weather
        logger.info(f"Fetching weather for {destination}")
        results["weather"] = await self.mcp_client.call_skill(
            "get_weather",
            {
                "destination": destination,
                "start_date": request.get("start_date"),
                "end_date": request.get("end_date")
            }
        )
        
        return results
    
    async def _create_plan(
        self,
        request: Dict[str, Any],
        skill_results: Dict[str, MCPSkillResult]
    ) -> Dict[str, Any]:
        """Create comprehensive travel plan using skill outputs"""
        
        destination = request.get("destination", "Unknown")
        
        # Gather data from skill results
        destination_info = None
        pricing = None
        reviews = None
        weather = None
        
        for name, result in skill_results.items():
            if result.success and result.result:
                if name == "destination_info":
                    destination_info = result.result
                elif name == "pricing":
                    pricing = result.result
                elif name == "reviews":
                    reviews = result.result
                elif name == "weather":
                    weather = result.result
        
        # Create final plan using CreateTravelPlanSkill
        plan_result = await self.mcp_client.call_skill(
            "create_travel_plan",
            {
                "destination": destination,
                "duration_days": request.get("duration_days", 5),
                "budget": request.get("budget", 2000),
                "travel_dates": {
                    "start": request.get("start_date", ""),
                    "end": request.get("end_date", "")
                },
                "interests": request.get("interests", []),
                "accommodation_type": request.get("accommodation_type", "mid-range"),
                "pace": request.get("pace", "moderate")
            }
        )
        
        if plan_result.success:
            return plan_result.result
        else:
            return {
                "destination": destination,
                "title": f"Travel Plan for {destination}",
                "overview": "Plan creation encountered an issue.",
                "error": plan_result.error,
                "raw_data": {
                    "destination_info": destination_info,
                    "pricing": pricing,
                    "reviews": reviews,
                    "weather": weather
                }
            }
    
    async def list_available_skills(self) -> List[str]:
        """List all skills available to this agent"""
        return self.mcp_client.list_skill_names()
    
    async def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """Get information about a specific skill"""
        skill = self.mcp_client.get_skill(skill_name)
        if skill:
            return {
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
                "input_schema": skill.input_schema,
                "output_schema": skill.output_schema
            }
        return None


class MCPSkillsPlanner:
    """
    Helper class for planning skill execution sequences.
    """
    
    # Predefined skill execution templates
    TEMPLATES = {
        "basic_planning": [
            {"skill": "search_destination", "parameters": {"destination": "$destination"}},
            {"skill": "query_prices", "parameters": {
                "destination": "$destination",
                "check_in": "$start_date",
                "check_out": "$end_date"
            }},
            {"skill": "create_travel_plan", "parameters": {
                "destination": "$destination",
                "duration_days": "$duration_days",
                "budget": "$budget"
            }}
        ],
        "comprehensive": [
            {"skill": "search_destination", "parameters": {"destination": "$destination", "include_tips": True}},
            {"skill": "query_prices", "parameters": {
                "destination": "$destination",
                "check_in": "$start_date",
                "check_out": "$end_date"
            }},
            {"skill": "get_destination_reviews", "parameters": {"destination": "$destination", "limit": 5}},
            {"skill": "get_weather", "parameters": {
                "destination": "$destination",
                "start_date": "$start_date",
                "end_date": "$end_date"
            }},
            {"skill": "create_travel_plan", "parameters": {
                "destination": "$destination",
                "duration_days": "$duration_days",
                "budget": "$budget",
                "travel_dates": {"start": "$start_date", "end": "$end_date"}
            }}
        ],
        "quick_check": [
            {"skill": "search_destination", "parameters": {"destination": "$destination"}},
            {"skill": "get_destination_reviews", "parameters": {"destination": "$destination", "limit": 3}}
        ]
    }
    
    @staticmethod
    def fill_parameters(
        template: List[Dict],
        parameters: Dict[str, Any]
    ) -> List[Dict]:
        """Fill template with actual parameters"""
        filled = []
        for step in template:
            params = {}
            for key, value in step.get("parameters", {}).items():
                if isinstance(value, str) and value.startswith("$"):
                    param_name = value[1:]
                    params[key] = parameters.get(param_name, value)
                else:
                    params[key] = value
            filled.append({
                "skill": step["skill"],
                "parameters": params
            })
        return filled


__all__ = [
    "SkillBasedAgent",
    "MCPSkillsPlanner",
]
