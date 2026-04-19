"""
FastAPI router for document ingestion and management.
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, BackgroundTasks
from typing import Dict, Any, List
import os
import shutil
from datetime import datetime

from ..retrieval.ingestion import ingest_directory, ingest_file, ingest_default_documents, get_collection_stats, reset_collection
from ..retrieval.search import get_all_document_names
from ..models.schemas import DocumentInfo

router = APIRouter()

# In-memory document registry demo
_documents = {}

def get_data_dir():
    data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))
    return os.path.abspath(data_dir)

def get_regs_dir():
    regs_dir = os.path.join(get_data_dir(), "regulations")
    os.makedirs(regs_dir, exist_ok=True)
    return regs_dir


@router.get("", response_model=List[DocumentInfo])
async def list_documents():
    """List all available regulatory documents."""
    # Sync registry with actual ingested documents
    doc_names = get_all_document_names()
    
    # Check directory for available but uningested docs
    regs_dir = get_regs_dir()
    files = []
    if os.path.exists(regs_dir):
        files = [f for f in os.listdir(regs_dir) if f.endswith(('.txt', '.pdf', '.md'))]
        
    result_docs = []
    
    # First add ingested docs
    for name in doc_names:
        doc = DocumentInfo(
            filename=name,
            status="ingested",
            chunk_count=0, # Need more complex query to get exact count per doc
            ingested_at=datetime.now().isoformat()
        )
        result_docs.append(doc)
        if name in files:
            files.remove(name)
            
    # Then add pending docs
    for f in files:
        doc = DocumentInfo(
            filename=f,
            status="pending",
            file_size=os.path.getsize(os.path.join(regs_dir, f))
        )
        result_docs.append(doc)
        
    return result_docs


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a new regulatory document."""
    if not file.filename.endswith(('.txt', '.pdf', '.md')):
        raise HTTPException(status_code=400, detail="Only .txt, .pdf, and .md files are supported")
        
    regs_dir = get_regs_dir()
    filepath = os.path.join(regs_dir, file.filename)
    
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Optional: trigger immediate ingestion
        return {"status": "success", "filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest_documents():
    """Trigger ingestion of all documents in the regulations directory."""
    try:
        results = ingest_default_documents()
        stats = get_collection_stats()
        
        return {
            "status": "success", 
            "ingested_files": len([r for r in results if r.get('status') == 'ingested']),
            "error_files": len([r for r in results if r.get('status') == 'error']),
            "total_chunks": stats.get('total_chunks', 0),
            "details": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_store():
    """Clear the vector database completely."""
    try:
        reset_collection()
        return {"status": "success", "message": "Vector store reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """Get vector database statistics."""
    try:
        return get_collection_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
