"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for /api/ask endpoint"""
    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="User's question about insurance policies"
    )
    provider: Optional[str] = Field(
        default="UHC",
        description="Insurance provider (e.g., 'UHC', 'Aetna')"
    )

    @validator('question')
    def question_not_empty(cls, v):
        """Ensure question is not just whitespace"""
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()

    @validator('provider')
    def provider_uppercase(cls, v):
        """Normalize provider to uppercase"""
        if v:
            return v.upper()
        return "UHC"

class PolicySource(BaseModel):
    """Model for policy source citation"""
    policy_id: str = Field(..., description="Unique policy identifier")
    title: str = Field(..., description="Policy title")
    url: str = Field(..., description="Source URL")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt from policy")

class QueryResponse(BaseModel):
    """Response model for /api/ask endpoint"""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[PolicySource] = Field(
        default_factory=list,
        description="Source policy citations"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1)"
    )
    provider: str = Field(..., description="Insurance provider queried")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Response timestamp (ISO format)"
    )
    cached: bool = Field(
        default=False,
        description="Whether response was cached"
    )

class HealthResponse(BaseModel):
    """Response model for /api/health endpoint"""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    llm_proxy: str = Field(..., description="LLM proxy URL")
    chroma_collections: int = Field(..., description="Number of ChromaDB collections")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Health check timestamp (ISO format)"
    )

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional details")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Error timestamp (ISO format)"
    )

class FeedbackRequest(BaseModel):
    """Request model for /api/feedback endpoint"""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="AI-generated answer")
    rating: int = Field(..., ge=1, le=5, description="User rating (1-5)")
    comment: Optional[str] = Field(None, description="Optional feedback comment")

class FeedbackResponse(BaseModel):
    """Response model for /api/feedback endpoint"""
    success: bool = Field(..., description="Whether feedback was saved")
    message: str = Field(..., description="Confirmation message")
