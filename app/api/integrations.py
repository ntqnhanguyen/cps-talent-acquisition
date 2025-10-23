"""Integration endpoints."""
import logging
from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Application
from app.schemas.application import SyncSuccessFactorsRequest
from app.services import SuccessFactorsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

successfactors_service = SuccessFactorsService()


@router.post("/successfactors/sync")
async def sync_to_successfactors(
    request: SyncSuccessFactorsRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Sync applications to SuccessFactors (Mock implementation).
    
    This endpoint demonstrates the integration flow.
    In production, it would make actual API calls to SAP SuccessFactors.
    """
    try:
        # Fetch applications with related data
        query = select(Application).where(
            Application.id.in_(request.application_ids)
        ).options(
            selectinload(Application.candidate),
            selectinload(Application.job)
        )
        
        result = await db.execute(query)
        applications = result.scalars().all()
        
        if not applications:
            raise HTTPException(status_code=404, detail="No applications found")
        
        if len(applications) != len(request.application_ids):
            raise HTTPException(
                status_code=404,
                detail=f"Some applications not found. Requested: {len(request.application_ids)}, Found: {len(applications)}"
            )
        
        # Prepare application data for sync
        app_data_list = []
        for app in applications:
            app_data = {
                "application_id": app.id,
                "job_id": app.job_id,
                "candidate_id": app.candidate_id,
                "candidate_name": app.candidate.name,
                "candidate_email": app.candidate.email,
                "candidate_phone": app.candidate.phone,
                "resume_url": app.candidate.resume_url,
                "scores": app.scores,
                "created_at": app.created_at
            }
            app_data_list.append(app_data)
        
        # Sync to SuccessFactors (mock)
        sync_result = await successfactors_service.sync_applications(app_data_list)
        
        # Update application status to synced
        for app in applications:
            app.status = "synced"
        
        await db.commit()
        
        logger.info(f"Synced {len(applications)} applications to SuccessFactors")
        return sync_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing to SuccessFactors: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/successfactors/documentation")
async def get_successfactors_documentation() -> Dict[str, Any]:
    """
    Get documentation for real SuccessFactors integration.
    
    Returns comprehensive guide for implementing actual SAP SuccessFactors API integration.
    """
    return successfactors_service.get_integration_documentation()

