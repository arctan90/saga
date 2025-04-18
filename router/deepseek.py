import asyncio
import logging
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from chat_function.deepseek import send_deepseek_request
from project_base import authenticate_api
# 日志配置
logger = logging.getLogger(__name__)

# 请求模型
# class GenerateRequest(BaseModel):
#     chat_completion_source: str
#     model: str
#     messages: List[Dict[str, Any]]
#     temperature: Optional[float] = 0.7
#     max_tokens: Optional[int] = 1000
#     stream: Optional[bool] = False
#     presence_penalty: Optional[float] = 0
#     frequency_penalty: Optional[float] = 0
#     top_p: Optional[float] = 1
#     top_k: Optional[int] = None
#     stop: Optional[List[str]] = None
#     logit_bias: Optional[Dict[str, float]] = None
#     seed: Optional[int] = None
#     n: Optional[int] = 1
#     logprobs: Optional[int] = 0
#     reverse_proxy: Optional[str] = None
#     proxy_password: Optional[str] = None


# 创建FastAPI应用
router = APIRouter()

# 存储活动的请求
active_requests = {}


# 生成路由
@router.post("/generate")
async def generate(request: Request, background_tasks: BackgroundTasks,
                   authenticated: bool = Depends(authenticate_api)):
    """
    处理生成请求
    """
    try:
        # 解析请求数据
        request_data = await request.json()

        # 验证请求数据
        if not request_data:
            return JSONResponse(status_code=400, content={"error": True})

        # 生成请求ID
        request_id = str(id(request))

        # 创建取消事件
        cancel_event = asyncio.Event()
        active_requests[request_id] = cancel_event

        # 添加清理任务
        background_tasks.add_task(cleanup_request, request_id)

        response = await send_deepseek_request(request_data, cancel_event)
        # 在响应头中添加请求ID
        if isinstance(response, StreamingResponse):
            response.headers["X-Request-ID"] = request_id
        return response

    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": {"message": str(e)}})


async def cleanup_request(request_id: str):
    """
    清理请求资源
    """
    await asyncio.sleep(300)  # 5分钟后清理
    if request_id in active_requests:
        del active_requests[request_id]
