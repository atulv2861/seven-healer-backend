from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from app.models.openings import JobOpening, KeyResponsibilityItem
from app.schemas.openings import (
    JobOpeningCreateSchema, 
    JobOpeningUpdateSchema, 
    JobOpeningResponseSchema,
    JobOpeningListResponseSchema,
    JobOpeningStatsSchema,
    KeyResponsibilityItemSchema
)
from app.services.auth import get_current_user_dependency
from app.enum import UserRoles
import re

router = APIRouter()

# Valid job types and statuses
VALID_JOB_TYPES = ["Full Time", "Part Time", "Contract", "Internship", "Freelance"]
VALID_STATUSES = ["Active", "Inactive", "Closed", "Draft"]

def validate_user_permissions(current_user):
    """Validate if user has permission to perform admin operations"""
    if isinstance(current_user, dict):  # Superuser
        return True
    elif hasattr(current_user, 'role') and current_user.role == UserRoles.ADMIN:
        return True
    return False

def convert_key_responsibilities_to_embedded(responsibilities_data):
    """Convert Pydantic schema to MongoEngine embedded documents"""
    embedded_responsibilities = []
    for resp in responsibilities_data:
        # Handle both Pydantic model objects and dictionaries
        if hasattr(resp, 'category'):
            # Pydantic model object
            category = resp.category
            items = resp.items
        else:
            # Dictionary object
            category = resp['category']
            items = resp['items']
        
        embedded_resp = KeyResponsibilityItem(
            category=category,
            items=items
        )
        embedded_responsibilities.append(embedded_resp)
    return embedded_responsibilities

def convert_key_responsibilities_to_schema(embedded_responsibilities):
    """Convert MongoEngine embedded documents to Pydantic schema"""
    schema_responsibilities = []
    for resp in embedded_responsibilities:
        schema_resp = KeyResponsibilityItemSchema(
            category=resp.category,
            items=resp.items
        )
        schema_responsibilities.append(schema_resp)
    return schema_responsibilities

@router.post("/", response_model=JobOpeningResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_job_opening(
    job_data: JobOpeningCreateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Create a new job opening (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create job openings"
            )
        
        # Validate job type
        if job_data.type not in VALID_JOB_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job type. Must be one of: {', '.join(VALID_JOB_TYPES)}"
            )
        
        # Validate status
        if job_data.is_active not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        
        # Check if job_id already exists
        existing_job = JobOpening.objects(job_id=job_data.job_id).first()
        if existing_job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job opening with ID '{job_data.job_id}' already exists"
            )
        
        # Convert key responsibilities to embedded documents
        embedded_responsibilities = convert_key_responsibilities_to_embedded(job_data.key_responsibilities)
        
        # Create new job opening
        new_job = JobOpening(
            job_id=job_data.job_id,
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            type=job_data.type,
            posted_date=job_data.posted_date,
            description=job_data.description,
            overview=job_data.overview,
            key_responsibilities=embedded_responsibilities,
            qualifications=job_data.qualifications,
            remuneration=job_data.remuneration,
            why_join_us=job_data.why_join_us,
            requirements=job_data.requirements,
            responsibilities=job_data.responsibilities,
            is_active=job_data.is_active
        )
        
        new_job.save()
        
        return JobOpeningResponseSchema(
            id=str(new_job.id),
            job_id=new_job.job_id,
            title=new_job.title,
            company=new_job.company,
            location=new_job.location,
            type=new_job.type,
            posted_date=new_job.posted_date,
            description=new_job.description,
            overview=new_job.overview,
            key_responsibilities=convert_key_responsibilities_to_schema(new_job.key_responsibilities),
            qualifications=new_job.qualifications,
            remuneration=new_job.remuneration,
            why_join_us=new_job.why_join_us,
            requirements=new_job.requirements,
            responsibilities=new_job.responsibilities,
            is_active=new_job.is_active,
            created_at=new_job.created_at,
            updated_at=new_job.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating job opening: {str(e)}"
        )

@router.get("/", response_model=JobOpeningListResponseSchema)
async def get_job_openings(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Get all job openings with pagination (Public access)
    """
    try:
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get job openings
        jobs_query = JobOpening.objects()
        total_jobs = jobs_query.count()
        
        jobs = jobs_query.skip(skip).limit(limit).order_by('-created_at')
        
        # Convert to response format
        job_list = []
        for job in jobs:
            job_list.append(JobOpeningResponseSchema(
                id=str(job.id),
                job_id=job.job_id,
                title=job.title,
                company=job.company,
                location=job.location,
                type=job.type,
                posted_date=job.posted_date,
                description=job.description,
                overview=job.overview,
                key_responsibilities=convert_key_responsibilities_to_schema(job.key_responsibilities),
                qualifications=job.qualifications,
                remuneration=job.remuneration,
                why_join_us=job.why_join_us,
                requirements=job.requirements,
                responsibilities=job.responsibilities,
                is_active=job.is_active,
                created_at=job.created_at,
                updated_at=job.updated_at
            ))
        
        return JobOpeningListResponseSchema(
            job_openings=job_list,
            total=total_jobs,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job openings: {str(e)}"
        )

@router.get("/{job_id}", response_model=JobOpeningResponseSchema)
async def get_job_opening(job_id: str):
    """
    Get a specific job opening by job_id (Public access)
    """
    try:
        job = JobOpening.objects(job_id=job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job opening not found"
            )
        
        return JobOpeningResponseSchema(
            id=str(job.id),
            job_id=job.job_id,
            title=job.title,
            company=job.company,
            location=job.location,
            type=job.type,
            posted_date=job.posted_date,
            description=job.description,
            overview=job.overview,
            key_responsibilities=convert_key_responsibilities_to_schema(job.key_responsibilities),
            qualifications=job.qualifications,
            remuneration=job.remuneration,
            why_join_us=job.why_join_us,
            requirements=job.requirements,
            responsibilities=job.responsibilities,
            is_active=job.is_active,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job opening: {str(e)}"
        )

@router.put("/{job_id}", response_model=JobOpeningResponseSchema)
async def update_job_opening(
    job_id: str,
    job_data: JobOpeningUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update a job opening (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update job openings"
            )
        
        # Find the job opening
        job = JobOpening.objects(job_id=job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job opening not found"
            )
        
        # Validate job type if provided
        if job_data.type and job_data.type not in VALID_JOB_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job type. Must be one of: {', '.join(VALID_JOB_TYPES)}"
            )
        
        # Validate status if provided
        if job_data.is_active and job_data.is_active not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        
        # Check if new job_id already exists (if being updated)
        if job_data.job_id and job_data.job_id != job.job_id:
            existing_job = JobOpening.objects(job_id=job_data.job_id).first()
            if existing_job:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Job opening with ID '{job_data.job_id}' already exists"
                )
        
        # Update fields
        update_data = job_data.dict(exclude_unset=True)
        
        # Handle key_responsibilities conversion if provided
        if 'key_responsibilities' in update_data:
            update_data['key_responsibilities'] = convert_key_responsibilities_to_embedded(update_data['key_responsibilities'])
        
        for field, value in update_data.items():
            setattr(job, field, value)
        
        job.save()
        
        return JobOpeningResponseSchema(
            id=str(job.id),
            job_id=job.job_id,
            title=job.title,
            company=job.company,
            location=job.location,
            type=job.type,
            posted_date=job.posted_date,
            description=job.description,
            overview=job.overview,
            key_responsibilities=convert_key_responsibilities_to_schema(job.key_responsibilities),
            qualifications=job.qualifications,
            remuneration=job.remuneration,
            why_join_us=job.why_join_us,
            requirements=job.requirements,
            responsibilities=job.responsibilities,
            is_active=job.is_active,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating job opening: {str(e)}"
        )

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_opening(
    job_id: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Delete a job opening (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete job openings"
            )
        
        # Find and delete the job opening
        job = JobOpening.objects(job_id=job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job opening not found"
            )
        
        job.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting job opening: {str(e)}"
        )

@router.patch("/{job_id}/status", response_model=JobOpeningResponseSchema)
async def update_job_status(
    job_id: str,
    new_status: str = Query(..., description="New status for the job"),
    current_user = Depends(get_current_user_dependency)
):
    """
    Update job opening status (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update job status"
            )
        
        # Validate status
        if new_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        
        # Find the job opening
        job = JobOpening.objects(job_id=job_id).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job opening not found"
            )
        
        # Update status
        job.is_active = new_status
        job.save()
        
        return JobOpeningResponseSchema(
            id=str(job.id),
            job_id=job.job_id,
            title=job.title,
            company=job.company,
            location=job.location,
            type=job.type,
            posted_date=job.posted_date,
            description=job.description,
            overview=job.overview,
            key_responsibilities=convert_key_responsibilities_to_schema(job.key_responsibilities),
            qualifications=job.qualifications,
            remuneration=job.remuneration,
            why_join_us=job.why_join_us,
            requirements=job.requirements,
            responsibilities=job.responsibilities,
            is_active=job.is_active,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating job status: {str(e)}"
        )

@router.get("/stats/summary", response_model=JobOpeningStatsSchema)
async def get_job_opening_stats(current_user = Depends(get_current_user_dependency)):
    """
    Get job opening statistics (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view job opening statistics"
            )
        
        # Get total count
        total_jobs = JobOpening.objects.count()
        
        # Get count by status
        status_counts = {}
        for status in VALID_STATUSES:
            status_counts[status] = JobOpening.objects(is_active=status).count()
        
        # Get count by job type
        type_counts = {}
        for job_type in VALID_JOB_TYPES:
            type_counts[job_type] = JobOpening.objects(type=job_type).count()
        
        # Get count by company
        companies = JobOpening.objects.distinct('company')
        company_counts = {}
        for company in companies:
            company_counts[company] = JobOpening.objects(company=company).count()
        
        return JobOpeningStatsSchema(
            total_jobs=total_jobs,
            active_jobs=status_counts.get('Active', 0),
            inactive_jobs=status_counts.get('Inactive', 0),
            closed_jobs=status_counts.get('Closed', 0),
            draft_jobs=status_counts.get('Draft', 0),
            type_breakdown=type_counts,
            company_breakdown=company_counts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job opening statistics: {str(e)}"
        )

@router.get("/search/advanced")
async def advanced_search_jobs(
    title: Optional[str] = Query(None, description="Search in job title"),
    company: Optional[str] = Query(None, description="Search in company name"),
    location: Optional[str] = Query(None, description="Search in location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    status: Optional[str] = Query("Active", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    Advanced search for job openings (Public access)
    """
    try:
        # Build query filters
        query_filters = {}
        
        if status and status in VALID_STATUSES:
            query_filters['is_active'] = status
        
        if job_type and job_type in VALID_JOB_TYPES:
            query_filters['type'] = job_type
        
        if title:
            query_filters['title__icontains'] = title
        
        if company:
            query_filters['company__icontains'] = company
        
        if location:
            query_filters['location__icontains'] = location
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get job openings with filters
        jobs_query = JobOpening.objects(**query_filters)
        total_jobs = jobs_query.count()
        
        jobs = jobs_query.skip(skip).limit(limit).order_by('-created_at')
        
        # Convert to response format
        job_list = []
        for job in jobs:
            job_list.append(JobOpeningResponseSchema(
                id=str(job.id),
                job_id=job.job_id,
                title=job.title,
                company=job.company,
                location=job.location,
                type=job.type,
                posted_date=job.posted_date,
                description=job.description,
                overview=job.overview,
                key_responsibilities=convert_key_responsibilities_to_schema(job.key_responsibilities),
                qualifications=job.qualifications,
                remuneration=job.remuneration,
                why_join_us=job.why_join_us,
                requirements=job.requirements,
                responsibilities=job.responsibilities,
                is_active=job.is_active,
                created_at=job.created_at,
                updated_at=job.updated_at
            ))
        
        return JobOpeningListResponseSchema(
            job_openings=job_list,
            total=total_jobs,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in advanced search: {str(e)}"
        )
