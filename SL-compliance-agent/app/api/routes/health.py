from fastapi import APIRouter
from app.retrieval.vectorstore import get_collection

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    return {"status": "ok", "service": "SL-Compliance-Agent"}


@router.get("/vectorstore")
async def vectorstore_status():
    """Check ChromaDB collection status and chunk count."""
    try:
        collection = get_collection()
        count = collection.count()
        return {
            "status": "ok",
            "collection": collection.name,
            "total_chunks": count,
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
