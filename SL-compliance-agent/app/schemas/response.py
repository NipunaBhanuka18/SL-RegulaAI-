from typing import List
from pydantic import BaseModel, Field
from .document import DocumentChunk

class ComplianceQueryResponse(BaseModel):
    answer: str = Field(..., description="The final answer string")
    sources: List[DocumentChunk] = Field(..., description="List of cited DocumentChunk sources")
    requires_human_verification: bool = Field(..., description="Flag indicating if human verification is required")
