from app.pipeline.graph.state import AgentState
from app.retrieval.vectorstore import VectorStoreManager
from app.ingestion.embedder import get_embedder
from app.schemas.document import DocumentChunk, GazetteMetadata

GLOBAL_EMBEDDER = get_embedder()
GLOBAL_DB_MANAGER = VectorStoreManager(GLOBAL_EMBEDDER)
GLOBAL_STORE = GLOBAL_DB_MANAGER.get_retriever().vectorstore

def retrieve(state: AgentState):
    question = state["question"]
    
    retrieved_docs = GLOBAL_STORE.similarity_search(question, k=4)
    
    docs = []
    for doc in retrieved_docs:
        metadata = GazetteMetadata(
            gazette_number=doc.metadata.get("gazette_number", "Unknown"),
            page=int(doc.metadata.get("page", 0)),
            category=doc.metadata.get("category", "General")
        )
        chunk = DocumentChunk(
            content=doc.page_content,
            metadata=metadata
        )
        docs.append(chunk)
        
    return {"documents": docs, "question": question}
