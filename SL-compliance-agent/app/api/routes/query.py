from fastapi import APIRouter, HTTPException
from loguru import logger
from app.schemas.query import ComplianceQueryRequest
from app.schemas.response import ComplianceQueryResponse, CitationSource
from app.pipeline.graph.builder import build_compliance_graph

router = APIRouter(prefix="/query", tags=["Query"])

# Compile graph once at module load (expensive operation)
_graph = build_compliance_graph()


@router.post("/", response_model=ComplianceQueryResponse)
async def run_compliance_query(request: ComplianceQueryRequest):
    """
    Run a compliance query through the full Agentic CRAG pipeline.
    Returns a grounded, cited answer with hallucination verification.
    """
    logger.info("[API] Incoming query: '{}'", request.query[:80])

    initial_state = {
        "query": request.query,
        "top_k": request.top_k,
        "retrieved_docs": [],
        "retrieval_attempts": 0,
        "rewritten_query": None,
        "docs_are_relevant": False,
        "draft_answer": None,
        "citations": [],
        "hallucination_detected": False,
        "generation_attempts": 0,
        "final_answer": None,
        "confidence": None,
    }

    try:
        final_state = _graph.invoke(initial_state)
    except Exception as e:
        logger.error("[API] Pipeline error: {}", e)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    answer = final_state.get("final_answer") or final_state.get("draft_answer", "")
    if not answer:
        raise HTTPException(status_code=422, detail="Could not generate a grounded answer.")

    citations = [CitationSource(**c) for c in final_state.get("citations", [])]

    return ComplianceQueryResponse(
        query=request.query,
        answer=answer,
        citations=citations,
        retrieval_attempts=final_state.get("retrieval_attempts", 1),
        hallucination_detected=final_state.get("hallucination_detected", False),
        confidence=final_state.get("confidence"),
    )
