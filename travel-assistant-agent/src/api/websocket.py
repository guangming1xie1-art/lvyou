import time
import asyncio
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.websocket_manager import ws_manager
from workflows.main_workflow import run_main_workflow_async
from utils.logger import app_logger

router = APIRouter()

@router.websocket("/ws/agent/stream")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = str(uuid.uuid4())
    await ws_manager.connect(connection_id, websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            action = data.get("action")
            params = data.get("params", {})
            
            if not action:
                await ws_manager.send_error(connection_id, "unknown", "Missing action", "MISSING_ACTION")
                continue
            
            # Execute requested agent action
            asyncio.create_task(handle_agent_action(connection_id, action, params))
            
    except WebSocketDisconnect:
        ws_manager.disconnect(connection_id)
    except Exception as e:
        app_logger.error(f"WebSocket error for {connection_id}: {e}")
        ws_manager.disconnect(connection_id)

async def handle_agent_action(connection_id: str, action: str, params: dict):
    start_time = time.time()
    
    async def on_progress(progress_data: dict):
        await ws_manager.broadcast_progress(connection_id, action, progress_data)

    try:
        user_message = params.get("message", "")
        user_id = params.get("user_id")
        session_id = params.get("session_id", str(uuid.uuid4()))
        
        if not user_message:
            await ws_manager.send_error(connection_id, action, "Missing message", "MISSING_MESSAGE")
            return
        
        app_logger.info(f"WebSocket {connection_id}: Processing action '{action}' with message: {user_message[:100]}...")
        
        # 发送开始进度
        await on_progress({"status": "starting", "progress": 0.0, "message": "正在启动工作流..."})
        
        # 统一使用主工作流处理所有请求
        result = await run_main_workflow_async(
            user_message=user_message,
            user_id=user_id,
            session_id=session_id
        )
        
        # 发送完成进度
        await on_progress({"status": "completed", "progress": 1.0, "message": "工作流执行完成"})
        
        # 根据不同的 action 返回相应的数据
        if action == "search":
            result_data = result.get("search_results", {})
        elif action == "recommend":
            result_data = result.get("recommendations", {})
        elif action == "book":
            result_data = result.get("booking_confirmation", {})
        elif action == "chat":
            # 返回完整结果
            result_data = {
                "status": "success" if result.get("collected_info", {}).get("complete") else "incomplete",
                "response": result.get("final_response", ""),
                "stage": result.get("stage"),
                "collected_info": result.get("collected_info", {}),
                "search_results": result.get("search_results", {}),
                "recommendations": result.get("recommendations", {}),
                "booking_confirmation": result.get("booking_confirmation", {}),
                "total_usage": result.get("total_usage", {}),
                "memory_info": {
                    "long_term_memory_count": result.get("long_term_memory", {}).get("count", 0),
                    "rewritten_query": result.get("rewritten_query"),
                }
            }
        else:
            await ws_manager.send_error(connection_id, action, f"Unknown action: {action}", "UNKNOWN_ACTION")
            return
        
        duration_ms = (time.time() - start_time) * 1000
        await ws_manager.send_completion(connection_id, action, result_data, duration_ms)
        
        app_logger.info(f"WebSocket {connection_id}: Action '{action}' completed in {duration_ms:.2f}ms")
        
    except Exception as e:
        app_logger.error(f"Error handling action {action}: {e}")
        await ws_manager.send_error(connection_id, action, str(e))
