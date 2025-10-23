"""Candidate model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Candidate(Base):
    """Candidate model representing a job applicant."""
    
    __tablename__ = "candidates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    linkedin = Column(String(255), nullable=True)
    resume_url = Column(String(500), nullable=False)
    skills = Column(JSON, nullable=False, default=list)
    experience_years = Column(Float, nullable=True)
    education = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name={self.name}, email={self.email})>"

