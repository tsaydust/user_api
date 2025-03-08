from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from utils.cache import SecRedis
from utils.consul_services import CustomConsul

custom_consul = CustomConsul()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.remove()
    logger.add("logs/file.log", rotation="500 MB", enqueue=True)
    custom_consul.register()
    await custom_consul.fetch_user_service_address()
    yield
    custom_consul.deregister()
    await SecRedis().close()
