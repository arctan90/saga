from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
import httpx
import asyncio

app = FastAPI()


async def make_request(request: Request, background_tasks: BackgroundTasks):
    # 创建一个事件来跟踪请求是否被取消
    cancelled = asyncio.Event()

    # 当客户端断开连接时触发
    @request.scope.get("disconnect")
    async def on_disconnect():
        cancelled.set()

    # 创建异步客户端
    async with httpx.AsyncClient() as client:
        try:
            # 发送请求到 OpenAI
            async with client.stream(
                    "POST",
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": "Hello"}],
                        "stream": True
                    },
                    headers={"Authorization": f"Bearer {api_key}"}
            ) as response:
                # 检查是否被取消
                if cancelled.is_set():
                    return

                # 流式返回响应
                async def generate():
                    async for chunk in response.aiter_bytes():
                        if cancelled.is_set():
                            break
                        yield chunk

                return StreamingResponse(generate())

        except asyncio.CancelledError:
            # 处理取消异常
            return {"error": "Request cancelled"}
        except Exception as e:
            return {"error": str(e)}


@app.post("/generate")
async def generate(request: Request, background_tasks: BackgroundTasks):
    return await make_request(request, background_tasks)