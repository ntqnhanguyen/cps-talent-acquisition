"""Application model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Application(Base):
    """Application model representing a candidate's job application."""
    
    __tablename__ = "applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="applied")  # applied, parsed, scored, shortlisted, synced
    scores = Column(JSON, nullable=True, default=dict)  # skill_fit, experience_fit, education_fit, keyword_match, overall_score
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    
    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, candidate_id={self.candidate_id}, status={self.status})>"

