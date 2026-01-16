"""
FastAPI 主应用入口
提供 Agent 服务的 HTTP API 接口
"""
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from src.workflows.main_workflow import main_agent

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """唯一入口：接收用户消息，调用主代理"""
    result = await main_agent.ainvoke({
        "messages": [HumanMessage(content=request.message)]
    })
    
    return {
        "status": "success",
        "response": result.get("final_response", ""),
        "total_usage": result.get("usage", {}),
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
