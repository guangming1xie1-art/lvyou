import time
import asyncio
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .websocket_manager import ws_manager
from ..agents.search import SearchAgent
from ..agents.recommendation import RecommendationAgent
from ..agents.booking import BookingAgent
from ..utils.logger import app_logger

router = APIRouter()

@router.websocket("/ws/agent/stream")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = str(uuid.uuid4())
    await ws_manager.connect(connection_id, websocket)
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_json()
            action = data.get("action")
            params = data.get("params", {})
            
            if not action:
                await ws_manager.send_error(connection_id, "unknown", "Missing action", "MISSING_ACTION")
                continue
            
            # Execute the requested agent action
            asyncio.create_task(handle_agent_action(connection_id, action, params))
            
    except WebSocketDisconnect:
        ws_manager.disconnect(connection_id)
    except Exception as e:
        app_logger.error(f"WebSocket error for {connection_id}: {e}")
        ws_manager.disconnect(connection_id)

async def handle_agent_action(connection_id: str, action: str, params: dict):
    start_time = time.time()
    
    async def on_progress(progress_data: dict):
        if progress_data.get("status") == "partial_results":
            await ws_manager.send_intermediate_result(connection_id, action, progress_data)
        else:
            await ws_manager.broadcast_progress(connection_id, action, progress_data)

    try:
        state = {"collected_info": params}
        
        if action == "search":
            agent = SearchAgent()
            result_state = await agent.run(state, on_progress=on_progress)
            result_data = result_state.get("search_results", [])
        elif action == "recommend":
            # If recommend is called directly, it might need search results
            # For simplicity, we assume params contains everything needed or we mock it
            agent = RecommendationAgent()
            # If search_results not in params, use empty list
            state["search_results"] = params.get("search_results", [])
            result_state = await agent.run(state, on_progress=on_progress)
            result_data = result_state.get("recommendations", [])
        elif action == "book":
            agent = BookingAgent()
            # If recommendations not in params, use empty list
            state["recommendations"] = params.get("recommendations", [])
            result_state = await agent.run(state, on_progress=on_progress)
            result_data = result_state.get("booking_status", {})
        else:
            await ws_manager.send_error(connection_id, action, f"Unknown action: {action}", "UNKNOWN_ACTION")
            return

        duration_ms = (time.time() - start_time) * 1000
        await ws_manager.send_completion(connection_id, action, result_data, duration_ms)
        
    except Exception as e:
        app_logger.error(f"Error handling action {action}: {e}")
        await ws_manager.send_error(connection_id, action, str(e))
