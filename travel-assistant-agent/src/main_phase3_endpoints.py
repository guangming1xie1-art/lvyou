"""
Phase 3 Additional Endpoints for main.py

These endpoints should be added to src/main.py
"""

from fastapi import WebSocket, HTTPException
from typing import Optional, Dict, Any


# ============ Phase 3.1: MCP V2 Endpoints ============

@app.get("/mcp-v2/status")
async def get_mcp_v2_status():
    """Get MCP V2 server status"""
    if not mcp_server_v2:
        return {
            "enabled": False,
            "message": "MCP V2 is not enabled"
        }
    
    stats = mcp_server_v2.get_statistics()
    return {
        "enabled": True,
        "status": "running",
        **stats
    }


@app.websocket("/ws/mcp-v2")
async def mcp_v2_websocket(websocket: WebSocket):
    """MCP V2 WebSocket endpoint for real-time communication"""
    if not mcp_server_v2:
        await websocket.close(code=1011, reason="MCP V2 not enabled")
        return
    
    await mcp_server_v2.handle_websocket(websocket)


# ============ Phase 3.2: Agent Skills Endpoints ============

@app.get("/skills/list")
async def list_skills(category: Optional[str] = None):
    """List all registered skills, optionally filtered by category"""
    if not skill_registry:
        raise HTTPException(status_code=503, detail="Skills framework not initialized")
    
    if category:
        skills = skill_registry.list_by_category(category)
    else:
        skills = skill_registry.list_all()
    
    return {
        "skills": skills,
        "count": len(skills),
        "category": category
    }


@app.get("/skills/{skill_name}")
async def get_skill_info(skill_name: str):
    """Get detailed information about a specific skill"""
    if not skill_registry:
        raise HTTPException(status_code=503, detail="Skills framework not initialized")
    
    skill = skill_registry.get(skill_name)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
    
    return skill.get_metadata()


@app.post("/skills/execute")
async def execute_skill(skill_name: str, input_data: Dict[str, Any]):
    """Execute a specific skill"""
    if not skill_registry:
        raise HTTPException(status_code=503, detail="Skills framework not initialized")
    
    try:
        result = await skill_registry.execute(
            skill_name,
            input_data,
            timeout=settings.skills_max_execution_time
        )
        return {
            "success": True,
            "skill_name": skill_name,
            "result": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/skills/batch-execute")
async def execute_skills_batch(request: Dict[str, Any]):
    """Execute multiple skills in parallel or sequence"""
    if not skill_registry:
        raise HTTPException(status_code=503, detail="Skills framework not initialized")
    
    calls = request.get("calls", [])
    parallel = request.get("parallel", True)
    stop_on_error = request.get("stop_on_error", True)
    
    try:
        if parallel and settings.skills_parallel_enabled:
            results = await skill_registry.execute_parallel(
                calls,
                timeout=settings.skills_max_execution_time
            )
        else:
            results = await skill_registry.execute_sequence(
                calls,
                stop_on_error=stop_on_error,
                timeout=settings.skills_max_execution_time
            )
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/skills/categories")
async def list_skill_categories():
    """List all skill categories"""
    if not skill_registry:
        raise HTTPException(status_code=503, detail="Skills framework not initialized")
    
    categories = skill_registry.get_categories()
    return {
        "categories": categories,
        "count": len(categories)
    }


@app.post("/skills/{skill_name}/enable")
async def enable_skill(skill_name: str):
    """Enable a specific skill"""
    if not skill_registry:
        raise HTTPException(status_code=503, detail="Skills framework not initialized")
    
    try:
        skill_registry.enable(skill_name)
        return {
            "success": True,
            "skill_name": skill_name,
            "enabled": True
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/skills/{skill_name}/disable")
async def disable_skill(skill_name: str):
    """Disable a specific skill"""
    if not skill_registry:
        raise HTTPException(status_code=503, detail="Skills framework not initialized")
    
    try:
        skill_registry.disable(skill_name)
        return {
            "success": True,
            "skill_name": skill_name,
            "enabled": False
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/skills/statistics")
async def get_skills_statistics():
    """Get overall skills framework statistics"""
    if not skill_registry:
        raise HTTPException(status_code=503, detail="Skills framework not initialized")
    
    stats = skill_registry.get_statistics()
    return stats


# ============ Phase 3.3: Concurrency Statistics Endpoints ============

@app.get("/concurrency/stats")
async def get_concurrency_stats():
    """Get connection pool and rate limiter statistics"""
    stats = {
        "connection_pool": {},
        "rate_limiter": {}
    }
    
    if api_connection_pool:
        stats["connection_pool"] = api_connection_pool.get_stats()
    
    if rate_limiter_global:
        stats["rate_limiter"] = rate_limiter_global.get_stats()
    
    return stats


@app.get("/concurrency/pool-stats")
async def get_pool_stats():
    """Get detailed connection pool statistics"""
    if not api_connection_pool:
        raise HTTPException(status_code=503, detail="Connection pool not initialized")
    
    return api_connection_pool.get_stats()


@app.get("/concurrency/rate-limit-stats")
async def get_rate_limit_stats():
    """Get rate limiter statistics"""
    if not rate_limiter_global:
        raise HTTPException(status_code=503, detail="Rate limiter not initialized")
    
    return rate_limiter_global.get_stats()
