"""Job schemas."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """Base job schema."""
    title: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=255)
    jd_text: str = Field(..., min_length=1)
    required_skills: List[str] = Field(default_factory=list)


class JobCreate(JobBase):
    """Schema for creating a job."""
    status: str = Field(default="active", pattern="^(active|closed)$")


class JobResponse(JobBase):
    """Schema for job response."""
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CandidateSummary(BaseModel):
    """Summary of candidate for job detail."""
    id: UUID
    name: str
    email: str
    skills: List[str]
    experience_years: Optional[float]
    application_status: str
    overall_score: Optional[float]
    
    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    """Schema for detailed job response with candidates."""
    candidates: List[CandidateSummary] = Field(default_factory=list)

