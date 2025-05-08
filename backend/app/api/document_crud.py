from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.document import Document
from app.core.database import SessionLocal
from pydantic import BaseModel
from fastapi import Request

router = APIRouter()

# Dependency for DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Pydantic models
class DocCreate(BaseModel):
    title: str
    content: str = ""

class DocUpdate(BaseModel):
    content: str

# List all documents
@router.get("/documents/")
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document))
    return result.scalars().all()

# Create a new document
@router.post("/documents/")
async def create_document(payload: DocCreate, db: AsyncSession = Depends(get_db)):
    doc = Document(title=payload.title, content=payload.content)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc

# Get a specific document by ID
@router.get("/documents/{doc_id}")
async def read_document(doc_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

# Update document content
class DocUpdate(BaseModel):
    content: str

@router.put("/documents/{doc_id}")
async def update_document(doc_id: int, payload: DocUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc.content = payload.content
    await db.commit()
    await db.refresh(doc)
    return doc
