from typing import Optional
from pydantic import BaseModel, Field

class ComplianceQueryRequest(BaseModel):
    question: str = Field(..., description="The user's question string")
    company_type: Optional[str] = Field(default=None, description="Optional company type string")
