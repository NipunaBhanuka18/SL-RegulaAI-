from pydantic import BaseModel, Field

class GazetteMetadata(BaseModel):
    gazette_number: str = Field(..., description="The gazette number")
    page: int = Field(..., description="The page number")
    category: str = Field(..., description="The category of the document")

class DocumentChunk(BaseModel):
    content: str = Field(..., description="The text content of the chunk")
    metadata: GazetteMetadata
