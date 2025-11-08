import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .database import Base, engine
from .routers import items
import redis.asyncio as aioredis  # or redis.asyncio usage

app = FastAPI(title="Knowledge Organizer", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1) 先注册 API 路由（/api/...）
app.include_router(items.router, prefix="/api")

# 2) 注册 WebSocket 路由（确保在 StaticFiles mount 之前）
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # 建立 redis 订阅并转发（同之前逻辑）
    redis_client = await aioredis.from_url(settings.CELERY_BROKER_URL, encoding="utf-8", decode_responses=True)
    pubsub = redis_client.pubsub()
    channel = settings.REDIS_PUBSUB_CHANNEL
    await pubsub.subscribe(channel)
    try:
        async def forward():
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg:
                    data = msg.get("data")
                    try:
                        await websocket.send_text(data)
                    except Exception:
                        break
                await asyncio.sleep(0.1)
        forward_task = asyncio.create_task(forward())
        while True:
            try:
                await websocket.receive_text()
            except Exception:
                break
    finally:
        forward_task.cancel()
        await pubsub.unsubscribe(channel)
        await redis_client.close()

# 3) 在最后挂载前端静态资源（占位）
frontend_dir = settings.FRONTEND_DIST_DIR
if os.path.isdir(frontend_dir):
    # 放在最后，避免拦截 /api/* 路由或 websocket
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    async def home():
        return {"message": f"Frontend not built. Put dist in '{frontend_dir}'."}