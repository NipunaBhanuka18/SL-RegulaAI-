from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger
from app.ingestion.loader import load_pdfs_from_dir
from app.ingestion.chunker import chunk_documents
from app.retrieval.vectorstore import ingest_chunks
from app.core.config import get_settings

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


def _run_ingestion():
    """Full ingestion pipeline: load → chunk → embed → store."""
    settings = get_settings()
    logger.info("[Ingest] Starting gazette ingestion from: {}", settings.gazette_pdf_dir)
    raw_pages = load_pdfs_from_dir(settings.gazette_pdf_dir)
    chunks = chunk_documents(raw_pages)
    ingest_chunks(chunks)
    logger.info("[Ingest] Ingestion complete. {} chunks stored.", len(chunks))


@router.post("/gazettes")
async def ingest_gazettes(background_tasks: BackgroundTasks):
    """
    Trigger ingestion of all PDFs in the gazette directory.
    Runs in the background — returns immediately.
    """
    settings = get_settings()
    try:
        background_tasks.add_task(_run_ingestion)
        return {
            "status": "started",
            "message": f"Ingestion started for PDFs in: {settings.gazette_pdf_dir}",
        }
    except Exception as e:
        logger.error("[Ingest] Failed to start ingestion: {}", e)
        raise HTTPException(status_code=500, detail=str(e))
