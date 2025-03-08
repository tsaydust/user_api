from fastapi.requests import Request
from loguru import logger
from fastapi.responses import JSONResponse


async def log_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        await logger.complete()
        return response
    except Exception as e:
        logger.exception('发生异常了！')
        return JSONResponse(content={"detail": "服务器内部错误！"}, status_code=500)
