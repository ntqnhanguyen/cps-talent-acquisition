"""Application management endpoints."""
import logging
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Job, Candidate, Application
from app.schemas import ApplicationResponse, ApplyRequest
from app.services import StorageService, AIParserService, AIScorerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["applications"])

storage_service = StorageService()
ai_parser_service = AIParserService()
ai_scorer_service = AIScorerService()


@router.post("/apply", response_model=ApplicationResponse, status_code=201)
async def apply_for_job(
    job_id: str = Form(...),
    cv_file: UploadFile = File(...),
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    linkedin: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply for a job by uploading CV.
    Automatically triggers AI parsing and scoring.
    """
    try:
        # Validate job exists
        job_uuid = uuid.UUID(job_id)
        result = await db.execute(select(Job).where(Job.id == job_uuid))
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Validate file type
        if not cv_file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        
        # Validate file size (10MB max)
        file_content = await cv_file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Generate unique filename
        file_extension = cv_file.filename.split('.')[-1]
        object_name = f"resumes/{uuid.uuid4()}.{file_extension}"
        
        # Upload to MinIO
        resume_url = await storage_service.upload_file(
            file_content,
            object_name,
            cv_file.content_type or "application/octet-stream"
        )
        
        # Extract text from CV
        cv_text = ai_parser_service.extract_text(file_content, cv_file.filename)
        
        # Parse CV with AI
        parsed_data = await ai_parser_service.parse_cv(cv_text)
        
        # Use parsed data or form data (form data takes precedence if provided)
        candidate_name = name or parsed_data.get("name") or "Unknown"
        candidate_email = email or parsed_data.get("email") or f"unknown_{uuid.uuid4().hex[:8]}@example.com"
        candidate_phone = phone or parsed_data.get("phone")
        candidate_linkedin = linkedin or parsed_data.get("linkedin")
        
        # Check if candidate exists by email
        result = await db.execute(select(Candidate).where(Candidate.email == candidate_email))
        candidate = result.scalar_one_or_none()
        
        if candidate:
            # Update existing candidate
            candidate.name = candidate_name
            candidate.phone = candidate_phone
            candidate.linkedin = candidate_linkedin
            candidate.resume_url = resume_url
            candidate.skills = parsed_data.get("skills", [])
            candidate.experience_years = parsed_data.get("experience_years")
            candidate.education = parsed_data.get("education")
        else:
            # Create new candidate
            candidate = Candidate(
                name=candidate_name,
                email=candidate_email,
                phone=candidate_phone,
                linkedin=candidate_linkedin,
                resume_url=resume_url,
                skills=parsed_data.get("skills", []),
                experience_years=parsed_data.get("experience_years"),
                education=parsed_data.get("education")
            )
            db.add(candidate)
        
        await db.flush()
        
        # Create application
        application = Application(
            job_id=job.id,
            candidate_id=candidate.id,
            status="parsed"
        )
        db.add(application)
        await db.flush()
        
        # Score candidate
        try:
            scores = await ai_scorer_service.score_candidate(
                candidate_profile={
                    "name": candidate.name,
                    "skills": candidate.skills,
                    "experience_years": candidate.experience_years,
                    "education": candidate.education
                },
                job_description=job.jd_text,
                required_skills=job.required_skills
            )
            
            application.scores = scores
            application.status = "scored"
        except Exception as e:
            logger.error(f"Error scoring candidate: {e}")
            # Continue without scores
        
        await db.commit()
        await db.refresh(application)
        
        logger.info(f"Application created: {application.id} for job {job.id}")
        return application
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing application: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/applications", response_model=List[ApplicationResponse])
async def list_applications(
    db: AsyncSession = Depends(get_db)
):
    """List all applications."""
    try:
        query = select(Application).order_by(Application.created_at.desc())
        result = await db.execute(query)
        applications = result.scalars().all()
        
        return applications
    except Exception as e:
        logger.error(f"Error listing applications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/applications/{application_id}/shortlist", response_model=ApplicationResponse)
async def shortlist_application(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Mark an application as shortlisted."""
    try:
        result = await db.execute(
            select(Application).where(Application.id == application_id)
        )
        application = result.scalar_one_or_none()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        application.status = "shortlisted"
        await db.commit()
        await db.refresh(application)
        
        logger.info(f"Application shortlisted: {application_id}")
        return application
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error shortlisting application: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

