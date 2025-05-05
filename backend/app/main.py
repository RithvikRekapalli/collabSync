from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.services.redis_manager import publish, subscribe
import asyncio

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to Realtime Collaboration App"}

@app.websocket("/ws/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str):
    await websocket.accept()
    channel = f"doc_{doc_id}"

    pubsub = await subscribe(channel)

    async def receive_from_redis():
        async for message in pubsub.listen():
            if message['type'] == 'message':
                await websocket.send_text(message['data'])

    redis_task = asyncio.create_task(receive_from_redis())

    try:
        while True:
            data = await websocket.receive_text()
            await publish(channel, data)
    except WebSocketDisconnect:
        redis_task.cancel()
        await pubsub.unsubscribe(channel)
        await websocket.close()


# Temporary addition
import asyncio
from app.core.database import engine
from app.models.document import Base

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
