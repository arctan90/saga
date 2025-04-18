from logging.handlers import TimedRotatingFileHandler
import logging
import os
import asyncio
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from env_helper import EnvHelper

from router.deepseek import router as deepseek_router
from router.csm import router as csm_router

from database.mysql_helper import create_default_tables

create_default_tables()

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
app = FastAPI()
origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # 透传的response header都要放在这里
    expose_headers=["session_id", "uid", 'pd-version', 'content-type'],
)

app.include_router(deepseek_router)
app.include_router(csm_router)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logging.error(f"Validation error: {exc.json()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# 错误处理
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"message": str(exc)}}
    )


async def run_uvicorn():
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(logging.INFO)

    svc_port = int(EnvHelper.get_env_value("SVC_PORT"))
    config = uvicorn.Config("__main__:app", host="0.0.0.0", port=svc_port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    # 使用 asyncio.gather 来同时启动WebSocket客户端和uvicorn服务器
    await asyncio.gather(
        run_uvicorn()
    )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # 配置按时间分割的日志处理程序
    timed_handler = TimedRotatingFileHandler('./logfile.log', when='midnight', interval=1, backupCount=7)
    timed_handler.setFormatter(log_formatter)

    logging.basicConfig(
        level=logging.WARNING,  # 设置日志级别
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            timed_handler,
        ]
    )

    asyncio.run(main())
