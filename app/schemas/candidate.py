"""Candidate schemas."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class CandidateBase(BaseModel):
    """Base candidate schema."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    linkedin: Optional[str] = Field(None, max_length=255)


class CandidateCreate(CandidateBase):
    """Schema for creating a candidate."""
    resume_url: str = Field(..., min_length=1, max_length=500)
    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    education: Optional[str] = Field(None, max_length=500)


class CandidateResponse(CandidateBase):
    """Schema for candidate response."""
    id: UUID
    resume_url: str
    skills: List[str]
    experience_years: Optional[float]
    education: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

