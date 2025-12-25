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


@router.post("/chat/completions", summary="AI 流式对话")
async def chat_completions(
    request_data: dict,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    对接 OpenAI ChatGPT 或 Google Gemini 接口，支持流式传输
    
    请求示例：
    {
        "model": "gpt-3.5-turbo" 或 "gemini-2.0-flash-lite",
        "provider": "openai" 或 "gemini",  // 可选，优先从 model 名推断
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "temperature": 0.7,
        "stream": true
    }
    """
    try:
        settings = get_settings()
        
        # 根据 model 名称或 provider 判断使用哪个 AI 服务
        model = request_data.get("model", "gpt-3.5-turbo")
        provider = request_data.get("provider", "")
        
        # 如果没有指定 provider，从 model 名推断
        if not provider:
            if "gemini" in model.lower():
                provider = "gemini"
            else:
                provider = "openai"
        
        if provider == "gemini":
            return await _handle_gemini_request(request_data, settings)
        else:
            return await _handle_openai_request(request_data, settings)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"请求失败: {str(e)}"
        )


async def _handle_openai_request(request_data: dict, settings):
    """处理 OpenAI ChatGPT 请求"""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API Key 未配置"
        )
    
    # 如果没有设置自定义 URL，使用官方 API
    base_url = settings.OPENAI_BASE_URL.strip() if settings.OPENAI_BASE_URL and settings.OPENAI_BASE_URL.strip() else "https://api.openai.com"
    
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
                f"{base_url}/v1/chat/completions",
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
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        }
    )


async def _handle_gemini_request(request_data: dict, settings):
    """处理 Google Gemini 请求"""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini API Key 未配置"
        )
    
    # 如果没有设置自定义 URL，使用官方 API
    base_url = settings.GEMINI_BASE_URL.strip() if settings.GEMINI_BASE_URL and settings.GEMINI_BASE_URL.strip() else "https://generativelanguage.googleapis.com"
    
    # 转换 OpenAI 格式的消息为 Gemini 格式
    messages = request_data.get("messages", [])
    gemini_contents = []
    
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        
        # Gemini 使用 "user" 和 "model" 作为角色
        if role == "system":
            # 系统消息转换为用户消息
            gemini_contents.append({
                "role": "user",
                "parts": [{"text": content}]
            })
        elif role == "user":
            gemini_contents.append({
                "role": "user",
                "parts": [{"text": content}]
            })
        elif role == "assistant":
            gemini_contents.append({
                "role": "model",
                "parts": [{"text": content}]
            })
    
    # 准备 Gemini 请求数据
    model = request_data.get("model", "gemini-2.0-flash-lite")
    payload = {
        "contents": gemini_contents,
        "generationConfig": {
            "temperature": request_data.get("temperature", 0.7),
            "maxOutputTokens": request_data.get("max_tokens", 2000)
        }
    }
    
    async def stream_response():
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                # Gemini API 端点
                url = f"{base_url}/v1beta/models/{model}:streamGenerateContent"
                params = {"key": settings.GEMINI_API_KEY}
                
                async with client.stream(
                    "POST",
                    url,
                    params=params,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = json.dumps({"error": f"Gemini API Error: {error_text.decode()}"})
                        yield f"data: {error_msg}\n\n"
                        return
                    
                    # 读取流式响应
                    buffer = ""
                    async for chunk in response.aiter_text():
                        buffer += chunk
                        
                        # Gemini 返回的是 JSON 数组，每个元素是一个 JSON 对象
                        # 尝试解析完整的 JSON 对象
                        while True:
                            try:
                                # 查找 JSON 对象的开始和结束
                                start = buffer.find('{')
                                if start == -1:
                                    break
                                    
                                # 尝试解析从 start 开始的 JSON
                                depth = 0
                                in_string = False
                                escape = False
                                end = -1
                                
                                for i in range(start, len(buffer)):
                                    c = buffer[i]
                                    
                                    if escape:
                                        escape = False
                                        continue
                                    
                                    if c == '\\':
                                        escape = True
                                        continue
                                    
                                    if c == '"':
                                        in_string = not in_string
                                        continue
                                    
                                    if not in_string:
                                        if c == '{':
                                            depth += 1
                                        elif c == '}':
                                            depth -= 1
                                            if depth == 0:
                                                end = i + 1
                                                break
                                
                                if end == -1:
                                    break
                                
                                json_str = buffer[start:end]
                                buffer = buffer[end:]
                                
                                # 解析 JSON 并转换为 OpenAI 格式
                                gemini_response = json.loads(json_str)
                                
                                # 提取文本内容
                                if "candidates" in gemini_response:
                                    for candidate in gemini_response["candidates"]:
                                        if "content" in candidate:
                                            parts = candidate["content"].get("parts", [])
                                            for part in parts:
                                                if "text" in part:
                                                    # 转换为 OpenAI 格式
                                                    openai_chunk = {
                                                        "choices": [{
                                                            "delta": {
                                                                "content": part["text"]
                                                            },
                                                            "index": 0,
                                                            "finish_reason": None
                                                        }]
                                                    }
                                                    yield f"data: {json.dumps(openai_chunk)}\n\n"
                            except json.JSONDecodeError:
                                break
                            except Exception as e:
                                print(f"Error parsing Gemini response: {e}")
                                break
                    
                    # 发送结束标记
                    yield "data: [DONE]\n\n"
                    
            except Exception as e:
                error_msg = json.dumps({"error": f"Stream Error: {str(e)}"})
                yield f"data: {error_msg}\n\n"
    
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        }
    )
