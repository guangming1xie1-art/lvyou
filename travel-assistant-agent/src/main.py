"""
FastAPI 主应用入口
提供 Agent 服务的 HTTP API 接口
"""
from fastapi import FastAPI
from pydantic import BaseModel
from workflows.main_workflow import run_main_workflow_async
from api.routes import router, chat_router, rag_router

app = FastAPI(title="Travel Assistant Agent API", version="2.0.0")

# Register routers
app.include_router(router)
app.include_router(chat_router)
app.include_router(rag_router)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """唯一入口：接收用户消息，调用主代理"""
    result = await run_main_workflow_async(request.message)
    
    return {
        "status": "success",
        "response": result.get("final_response", ""),
        "total_usage": result.get("total_usage", {}),
        "details": {
            "collected_info": result.get("collected_info", {}),
            "search_results": result.get("search_results", {}),
            "recommendations": result.get("recommendations", {}),
            "booking": result.get("booking_confirmation", {})
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
