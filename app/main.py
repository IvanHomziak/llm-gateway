from sys import api_version

from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.chat import router as chat_router

app = FastAPI(title="llm-gateway")

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
