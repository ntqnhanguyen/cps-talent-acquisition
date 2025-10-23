"""Application schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class ApplicationBase(BaseModel):
    """Base application schema."""
    job_id: UUID
    candidate_id: UUID


class ApplicationCreate(ApplicationBase):
    """Schema for creating an application."""
    status: str = Field(default="applied")


class ApplicationResponse(ApplicationBase):
    """Schema for application response."""
    id: UUID
    status: str
    scores: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplyRequest(BaseModel):
    """Schema for apply endpoint request."""
    job_id: UUID
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None


class ShortlistRequest(BaseModel):
    """Schema for shortlist request."""
    application_id: UUID


class SyncSuccessFactorsRequest(BaseModel):
    """Schema for SuccessFactors sync request."""
    application_ids: list[UUID] = Field(..., min_length=1)

