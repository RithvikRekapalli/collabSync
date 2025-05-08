from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.document import Document
from app.core.database import SessionLocal, engine, Base
from app.api import document_crud
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Create DB tables on startup (important for new deployments)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Register REST API routes
app.include_router(document_crud.router)

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# WebSocket endpoint for real-time document editing
@app.websocket("/ws/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: int, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    try:
        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()

        if doc:
            await websocket.send_text(doc.content)
        else:
            await websocket.send_text("")

        while True:
            data = await websocket.receive_text()
            if doc:
                doc.content = data
                await db.commit()
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for doc_id={doc_id}")

@app.get("/")
async def root():
    return {"message": "Realtime Collaboration Server is running"}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)