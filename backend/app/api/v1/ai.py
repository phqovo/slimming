from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import httpx
import json
from typing import Optional
from app.core.database import get_db
from app.core.config import get_settings
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

# ChatGPT 代理配置
PROXY_BASE_URL = "https://fly.piheqi.com"


@router.post("/chat/completions", summary="ChatGPT 流式对话")
async def chat_completions(
    request_data: dict,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    对接 OpenAI ChatGPT 接口，支持流式传输
    
    请求示例：
    {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "temperature": 0.7,
        "stream": true
    }
    """
    try:
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API Key 未配置"
            )
        
        # 准备请求数据
        payload = {
            **request_data,
            "stream": True
        }
        
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        async def stream_response():
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream(
                    "POST",
                    f"{PROXY_BASE_URL}/v1/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = json.dumps({"error": f"API Error: {error_text.decode()}"})
                        yield f"data: {error_msg}\n\n"
                        return
                    
                    async for line in response.aiter_lines():
                        if line:
                            yield line + "\n\n"
        
        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"请求失败: {str(e)}"
        )
