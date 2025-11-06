import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .database import Base, engine
from .routers import items
import aioredis

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(title="Knowledge Organizer", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api")

frontend_dir = settings.FRONTEND_DIST_DIR
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    async def home():
        return {"message": f"Frontend not built. Put dist in '{frontend_dir}'."}

@app.on_event("startup")
async def startup_event():
    await init_models()
    app.state.redis = await aioredis.from_url(settings.CELERY_BROKER_URL, encoding="utf-8", decode_responses=True)

@app.on_event("shutdown")
async def shutdown_event():
    if getattr(app.state, "redis", None):
        await app.state.redis.close()

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    redis = await aioredis.from_url(settings.CELERY_BROKER_URL, encoding="utf-8", decode_responses=True)
    pubsub = redis.pubsub()
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
    except WebSocketDisconnect:
        pass
    finally:
        forward_task.cancel()
        await pubsub.unsubscribe(channel)
        await redis.close()
