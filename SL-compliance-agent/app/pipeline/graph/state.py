from typing import TypedDict, List
from app.schemas.document import DocumentChunk

class AgentState(TypedDict):
    question: str
    documents: List[DocumentChunk]
    generation: str
    requires_rewrite: bool
    chat_history: list
    requires_human: bool
