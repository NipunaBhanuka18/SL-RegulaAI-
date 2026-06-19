from typing import List, Tuple
from loguru import logger
from app.retrieval.vectorstore import get_collection, get_embedding_model
from app.core.config import get_settings


def retrieve(query: str, top_k: int | None = None) -> List[Tuple[str, dict, float]]:
    """
    Query the ChromaDB vector store.

    Returns: List of (content, metadata, distance_score) tuples.
    Lower distance = higher relevance for cosine space.
    """
    settings = get_settings()
    k = top_k or settings.retrieval_top_k

    model = get_embedding_model()
    query_embedding = model.encode(query).tolist()
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    logger.debug("Retrieved {} chunks for query: '{}'", len(docs), query[:80])
    return list(zip(docs, metas, distances))
