import uvicorn
from fastapi import FastAPI
from hooks.lifespan import lifespan
from hooks.middlewares import log_middleware
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from routers import user,address
import settings

app = FastAPI(lifespan=lifespan)
app.add_middleware(BaseHTTPMiddleware,dispatch=log_middleware)
app.include_router(user.router)
app.include_router(address.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get('/health')
async def health_check():
    return "ok"


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVER_PORT)