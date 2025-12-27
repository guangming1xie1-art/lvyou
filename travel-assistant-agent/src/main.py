"""
FastAPI 主应用入口
提供 Agent 服务的 HTTP API 接口
"""
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from config import settings
from models.schemas import PlanningRequest, PlanningResponse, HealthResponse
from workflows import PlanningWorkflow
from utils.logger import app_logger
from utils.db import db_manager
from utils.claude import claude_client
from utils.api_client import backend_client
from agents import (
    get_mcp_client,
    init_mcp_client,
    SkillBasedAgent,
    MCPSkillsPlanner
)


# ============== MCP-related Models ==============

class MCPSkillInfo(BaseModel):
    """MCP Skill information"""
    name: str
    description: str
    category: str
    version: str = "1.0.0"
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)


class MCPSkillsListResponse(BaseModel):
    """Response for skills list endpoint"""
    skills: List[MCPSkillInfo]
    total_count: int


class SkillCallRequest(BaseModel):
    """Request to call a single skill"""
    skill_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SkillCallResponse(BaseModel):
    """Response from skill execution"""
    success: bool
    skill_name: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class BatchSkillCallRequest(BaseModel):
    """Request to call multiple skills"""
    calls: List[SkillCallRequest]


class BatchSkillCallResponse(BaseModel):
    """Response from batch skill execution"""
    results: List[SkillCallResponse]
    total_calls: int
    successful_calls: int
    failed_calls: int


class DemoPlanningRequest(BaseModel):
    """Request for demo planning with skills"""
    destination: str = Field(..., description="Travel destination")
    duration_days: int = Field(default=5, description="Number of days")
    budget: float = Field(default=2000.0, description="Budget in USD")
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    interests: List[str] = Field(default_factory=list, description="Traveler interests")
    accommodation_type: str = Field(default="mid-range", description="Accommodation preference")
    pace: str = Field(default="moderate", description="Travel pace: relaxed, moderate, packed")
    use_template: str = Field(default="comprehensive", description="Skill template: basic, comprehensive, quick")


class DemoPlanningResponse(BaseModel):
    """Response for demo planning endpoint"""
    request_id: str
    destination: str
    skills_used: List[str]
    skill_results: Dict[str, Any]
    travel_plan: Dict[str, Any]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting Travel Assistant Agent service...")
    
    db_manager.init()
    claude_client.init()
    
    # Initialize MCP Client
    try:
        await init_mcp_client()
        app_logger.info("MCP Client initialized")
    except Exception as e:
        app_logger.warning(f"MCP Client initialization failed: {e}")
    
    app_logger.info("Service started successfully")
    yield
    
    app_logger.info("Shutting down...")
    db_manager.close()
    await backend_client.close()
    
    # Disconnect MCP client
    mcp_client = get_mcp_client()
    if mcp_client.is_connected():
        await mcp_client.disconnect()
    
    app_logger.info("Service stopped")


app = FastAPI(
    title=settings.app_name,
    description="AI Travel Assistant Agent Service",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    db_ok = db_manager.health_check()
    claude_ready = claude_client.is_ready()

    claude_component = (
        "ok" if claude_ready else ("not_configured" if not claude_client.is_configured else "error")
    )

    overall_status = "healthy" if db_ok and claude_component in {"ok", "not_configured"} else "degraded"

    return {
        "status": overall_status,
        "app_env": settings.app_env,
        "components": {
            "database": "ok" if db_ok else "error",
            "claude": claude_component,
        },
    }


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "status": "running"
    }


@app.post("/agent/start-planning", response_model=PlanningResponse)
async def start_planning(request: PlanningRequest):
    if not request.user_message:
        raise HTTPException(status_code=400, detail="user_message is required")
    
    request_id = str(uuid.uuid4())
    app_logger.info(f"[{request_id}] Received planning request: {request.user_message}")
    
    try:
        workflow = PlanningWorkflow()
        result = await workflow.run(request.user_message, request.metadata)
        
        return PlanningResponse(
            request_id=request_id,
            status="completed",
            result=result
        )
    except Exception as e:
        app_logger.error(f"[{request_id}] Planning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/status/{request_id}")
async def get_status(request_id: str):
    # TODO: 实现异步任务状态查询
    return {
        "request_id": request_id,
        "status": "not_implemented",
        "message": "Async task tracking not yet implemented"
    }


# ============== MCP Endpoints ==============

@app.get("/mcp/skills", response_model=MCPSkillsListResponse)
async def list_mcp_skills():
    """
    List all available MCP skills.
    
    Returns a list of all skills registered with the MCP server,
    including their names, descriptions, categories, and schemas.
    """
    mcp_client = get_mcp_client()
    skills = mcp_client.list_skills()
    
    skill_infos = [
        MCPSkillInfo(
            name=s.name,
            description=s.description,
            category=s.category,
            version=s.version,
            input_schema=s.input_schema,
            output_schema=s.output_schema
        )
        for s in skills
    ]
    
    return {
        "skills": skill_infos,
        "total_count": len(skill_infos)
    }


@app.post("/mcp/call-skill", response_model=SkillCallResponse)
async def call_mcp_skill(request: SkillCallRequest):
    """
    Call a single MCP skill.
    
    Executes the specified skill with the given parameters and returns
    the result. Useful for testing individual skills or building custom
    workflows.
    """
    import time
    start_time = time.time()
    
    mcp_client = get_mcp_client()
    result = await mcp_client.call_skill(request.skill_name, request.parameters)
    
    execution_time_ms = (time.time() - start_time) * 1000
    
    return SkillCallResponse(
        success=result.success,
        skill_name=result.skill_name,
        result=result.result,
        error=result.error,
        execution_time_ms=execution_time_ms
    )


@app.post("/mcp/batch-call", response_model=BatchSkillCallResponse)
async def call_mcp_skills_batch(request: BatchSkillCallRequest):
    """
    Call multiple MCP skills in parallel.
    
    Executes all specified skill calls in parallel and returns the results
    for each. This is more efficient than calling skills sequentially when
    skills don't depend on each other's outputs.
    """
    mcp_client = get_mcp_client()
    
    calls = [
        {"skill": call.skill_name, "parameters": call.parameters}
        for call in request.calls
    ]
    
    results = await mcp_client.call_skills_parallel(calls)
    
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    
    return BatchSkillCallResponse(
        results=[
            SkillCallResponse(
                success=r.success,
                skill_name=r.skill_name,
                result=r.result,
                error=r.error
            )
            for r in results
        ],
        total_calls=len(results),
        successful_calls=successful,
        failed_calls=failed
    )


@app.get("/mcp/status")
async def get_mcp_status():
    """
    Get MCP client status and statistics.
    
    Returns information about the MCP connection, including:
    - Connection status
    - Number of available skills
    - List of skill names
    """
    mcp_client = get_mcp_client()
    stats = mcp_client.get_statistics()
    
    return {
        "mcp_enabled": True,
        "connected": stats["connected"],
        "skills_count": stats["skills_count"],
        "skills": stats["skills"]
    }


@app.post("/agent/demo-planning-with-skills", response_model=DemoPlanningResponse)
async def demo_planning_with_skills(request: DemoPlanningRequest):
    """
    Demo endpoint for planning with MCP Skills.
    
    This endpoint demonstrates how the Agent uses MCP skills to gather
    information and create comprehensive travel plans. It:
    1. Searches for destination information
    2. Queries pricing for hotels and flights
    3. Gets user reviews and ratings
    4. Checks weather forecast
    5. Creates a complete travel plan
    
    This is a proof-of-concept demonstrating the MCP skill integration
    pattern for future full implementation.
    """
    import time
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    app_logger.info(f"[{request_id}] Starting demo planning for {request.destination}")
    
    try:
        mcp_client = get_mcp_client()
        
        # Prepare parameters
        params = {
            "destination": request.destination,
            "duration_days": request.duration_days,
            "budget": request.budget,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "interests": request.interests,
            "accommodation_type": request.accommodation_type,
            "pace": request.pace
        }
        
        # Get the skill template
        template_name = request.use_template
        template = getattr(MCPSkillsPlanner.TEMPLATES, template_name, MCPSkillsPlanner.TEMPLATES["comprehensive"])
        
        # Fill template with parameters
        calls = MCPSkillsPlanner.fill_parameters(template, params)
        
        # Execute skills
        app_logger.info(f"[{request_id}] Executing {len(calls)} skills")
        skill_results = {}
        
        for call in calls:
            skill_name = call["skill"]
            parameters = call["parameters"]
            
            app_logger.info(f"[{request_id}] Calling skill: {skill_name}")
            
            result = await mcp_client.call_skill(skill_name, parameters)
            
            skill_results[skill_name] = {
                "success": result.success,
                "error": result.error,
                "data": result.result
            }
        
        # Create the final plan
        app_logger.info(f"[{request_id}] Creating final travel plan")
        plan_result = await mcp_client.call_skill(
            "create_travel_plan",
            {
                "destination": request.destination,
                "duration_days": request.duration_days,
                "budget": request.budget,
                "travel_dates": {"start": request.start_date, "end": request.end_date},
                "interests": request.interests,
                "accommodation_type": request.accommodation_type,
                "pace": request.pace
            }
        )
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return DemoPlanningResponse(
            request_id=request_id,
            destination=request.destination,
            skills_used=[c["skill"] for c in calls],
            skill_results=skill_results,
            travel_plan=plan_result.result if plan_result.success else {"error": plan_result.error}
        )
        
    except Exception as e:
        app_logger.error(f"[{request_id}] Demo planning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development
    )
