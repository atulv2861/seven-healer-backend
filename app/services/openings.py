from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from app.models.openings import JobOpening, KeyResponsibilityItem, JobApplication
from app.schemas.openings import (
    JobOpeningCreateSchema, 
    JobOpeningUpdateSchema, 
    JobOpeningResponseSchema,
    JobOpeningListResponseSchema,
    JobOpeningStatsSchema,
    KeyResponsibilityItemSchema,
    JobApplicationCreateSchema,
    JobApplicationUpdateSchema,
    JobApplicationResponseSchema,
    JobApplicationListResponseSchema,
    JobApplicationStatsSchema,
    JobApplicationStatusUpdateSchema
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
    limit: int = Query(5, ge=1, le=100, description="Items per page")
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

# Job Application APIs

@router.post("/applications/", response_model=JobApplicationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_job_application(application_data: JobApplicationCreateSchema):
    """
    Create a new job application (Public endpoint)
    """
    try:
        # Validate that if applying for available jobs, a job_id is provided
        if application_data.apply_for_available_jobs and not application_data.selected_job_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job ID is required when applying for available jobs"
            )
        
        # If applying for specific job, verify job exists and is active
        if application_data.apply_for_available_jobs and application_data.selected_job_id:
            job = JobOpening.objects(job_id=application_data.selected_job_id, is_active="Active").first()
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Job with ID '{application_data.selected_job_id}' not found or not active"
                )
        
        # Check if user already applied for the same job (if applying for specific job)
        if application_data.apply_for_available_jobs and application_data.selected_job_id:
            existing_application = JobApplication.objects(
                email=application_data.email,
                selected_job_id=application_data.selected_job_id
            ).first()
            if existing_application:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already applied for this job"
                )
        
        # Create new application
        new_application = JobApplication(
            apply_for_available_jobs=application_data.apply_for_available_jobs,
            selected_job_id=application_data.selected_job_id,
            title=application_data.title,
            first_name=application_data.first_name,
            surname=application_data.surname,
            phone_number=application_data.phone_number,
            email=application_data.email,
            street_address=application_data.street_address,
            street_address_line2=application_data.street_address_line2,
            city=application_data.city,
            state_province=application_data.state_province,
            postal_zip_code=application_data.postal_zip_code,
            highest_education=application_data.highest_education,
            total_experience_years=application_data.total_experience_years,
            current_last_employer=application_data.current_last_employer,
            current_last_designation=application_data.current_last_designation,
            cv_filename=application_data.cv_filename,
            cv_data=application_data.cv_data,
            cv_size=application_data.cv_size
        )
        
        new_application.save()
        
        return JobApplicationResponseSchema(
            id=str(new_application.id),
            apply_for_available_jobs=new_application.apply_for_available_jobs,
            selected_job_id=new_application.selected_job_id,
            title=new_application.title,
            first_name=new_application.first_name,
            surname=new_application.surname,
            phone_number=new_application.phone_number,
            email=new_application.email,
            street_address=new_application.street_address,
            street_address_line2=new_application.street_address_line2,
            city=new_application.city,
            state_province=new_application.state_province,
            postal_zip_code=new_application.postal_zip_code,
            highest_education=new_application.highest_education,
            total_experience_years=new_application.total_experience_years,
            current_last_employer=new_application.current_last_employer,
            current_last_designation=new_application.current_last_designation,
            cv_filename=new_application.cv_filename,
            cv_data=new_application.cv_data,
            cv_size=new_application.cv_size,
            status=new_application.status,
            created_at=new_application.created_at,
            updated_at=new_application.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating job application: {str(e)}"
        )

@router.get("/applications/", response_model=JobApplicationListResponseSchema)
async def get_job_applications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by application status"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    current_user = Depends(get_current_user_dependency)
):
    """
    Get job applications (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view job applications"
            )
        
        # Build query filters
        query_filters = {}
        
        if status:
            valid_statuses = ["Pending", "Under Review", "Shortlisted", "Rejected", "Hired"]
            if status in valid_statuses:
                query_filters['status'] = status
        
        if job_id:
            query_filters['selected_job_id'] = job_id
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get applications with filters
        applications_query = JobApplication.objects(**query_filters)
        total_applications = applications_query.count()
        
        applications = applications_query.skip(skip).limit(limit).order_by('-created_at')
        
        # Convert to response format
        application_list = []
        for app in applications:
            application_list.append(JobApplicationResponseSchema(
                id=str(app.id),
                apply_for_available_jobs=app.apply_for_available_jobs,
                selected_job_id=app.selected_job_id,
                title=app.title,
                first_name=app.first_name,
                surname=app.surname,
                phone_number=app.phone_number,
                email=app.email,
                street_address=app.street_address,
                street_address_line2=app.street_address_line2,
                city=app.city,
                state_province=app.state_province,
                postal_zip_code=app.postal_zip_code,
                highest_education=app.highest_education,
                total_experience_years=app.total_experience_years,
                current_last_employer=app.current_last_employer,
                current_last_designation=app.current_last_designation,
                cv_filename=app.cv_filename,
                cv_data=app.cv_data,
                cv_size=app.cv_size,
                status=app.status,
                created_at=app.created_at,
                updated_at=app.updated_at
            ))
        
        return JobApplicationListResponseSchema(
            applications=application_list,
            total=total_applications,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job applications: {str(e)}"
        )

@router.get("/applications/{application_id}", response_model=JobApplicationResponseSchema)
async def get_job_application(
    application_id: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Get a specific job application (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view job applications"
            )
        
        # Find the application
        application = JobApplication.objects(id=application_id).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        return JobApplicationResponseSchema(
            id=str(application.id),
            apply_for_available_jobs=application.apply_for_available_jobs,
            selected_job_id=application.selected_job_id,
            title=application.title,
            first_name=application.first_name,
            surname=application.surname,
            phone_number=application.phone_number,
            email=application.email,
            street_address=application.street_address,
            street_address_line2=application.street_address_line2,
            city=application.city,
            state_province=application.state_province,
            postal_zip_code=application.postal_zip_code,
            highest_education=application.highest_education,
            total_experience_years=application.total_experience_years,
            current_last_employer=application.current_last_employer,
            current_last_designation=application.current_last_designation,
            cv_filename=application.cv_filename,
            cv_data=application.cv_data,
            cv_size=application.cv_size,
            status=application.status,
            created_at=application.created_at,
            updated_at=application.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job application: {str(e)}"
        )

@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_application(
    application_id: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Delete a job application (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete job applications"
            )
        
        # Find the application
        application = JobApplication.objects(id=application_id).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        # Delete the application
        application.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting job application: {str(e)}"
        )

@router.patch("/applications/{application_id}/status", response_model=JobApplicationResponseSchema)
async def update_application_status(
    application_id: str,
    status_data: JobApplicationStatusUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update application status (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update application status"
            )
        
        new_status = status_data.status
        valid_statuses = ["Pending", "Under Review", "Shortlisted", "Rejected", "Hired"]
        
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Find the application
        application = JobApplication.objects(id=application_id).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        # Update status
        application.status = new_status
        application.save()
        
        return JobApplicationResponseSchema(
            id=str(application.id),
            apply_for_available_jobs=application.apply_for_available_jobs,
            selected_job_id=application.selected_job_id,
            title=application.title,
            first_name=application.first_name,
            surname=application.surname,
            phone_number=application.phone_number,
            email=application.email,
            street_address=application.street_address,
            street_address_line2=application.street_address_line2,
            city=application.city,
            state_province=application.state_province,
            postal_zip_code=application.postal_zip_code,
            highest_education=application.highest_education,
            total_experience_years=application.total_experience_years,
            current_last_employer=application.current_last_employer,
            current_last_designation=application.current_last_designation,
            cv_filename=application.cv_filename,
            cv_data=application.cv_data,
            cv_size=application.cv_size,
            status=application.status,
            created_at=application.created_at,
            updated_at=application.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating application status: {str(e)}"
        )

