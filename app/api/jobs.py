"""Job management endpoints."""
import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Job, Application, Candidate
from app.schemas import JobCreate, JobResponse, JobDetailResponse, CandidateSummary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status: str = Query(None, description="Filter by status (active/closed)"),
    db: AsyncSession = Depends(get_db)
):
    """List all jobs with optional status filter."""
    try:
        query = select(Job)
        if status:
            query = query.where(Job.status == status)
        query = query.order_by(Job.created_at.desc())
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return jobs
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting."""
    try:
        job = Job(
            title=job_data.title,
            location=job_data.location,
            status=job_data.status,
            jd_text=job_data.jd_text,
            required_skills=job_data.required_skills
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        logger.info(f"Created job: {job.id} - {job.title}")
        return job
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job_detail(
    job_id: UUID,
    min_score: float = Query(None, ge=0, le=100, description="Minimum overall score filter"),
    db: AsyncSession = Depends(get_db)
):
    """Get job details with candidate pipeline."""
    try:
        # Get job with applications
        query = select(Job).where(Job.id == job_id).options(
            selectinload(Job.applications).selectinload(Application.candidate)
        )
        result = await db.execute(query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Build candidate summaries
        candidates = []
        for application in job.applications:
            overall_score = application.scores.get("overall_score") if application.scores else None
            
            # Apply score filter if specified
            if min_score is not None and (overall_score is None or overall_score < min_score):
                continue
            
            candidate_summary = CandidateSummary(
                id=application.candidate.id,
                name=application.candidate.name,
                email=application.candidate.email,
                skills=application.candidate.skills,
                experience_years=application.candidate.experience_years,
                application_status=application.status,
                overall_score=overall_score
            )
            candidates.append(candidate_summary)
        
        # Sort by score (highest first)
        candidates.sort(key=lambda x: x.overall_score if x.overall_score is not None else -1, reverse=True)
        
        # Build response
        job_detail = JobDetailResponse(
            id=job.id,
            title=job.title,
            location=job.location,
            status=job.status,
            jd_text=job.jd_text,
            required_skills=job.required_skills,
            created_at=job.created_at,
            updated_at=job.updated_at,
            candidates=candidates
        )
        
        return job_detail
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job detail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

