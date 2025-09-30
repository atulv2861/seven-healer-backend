from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from app.models.projects import Projects
from app.schemas.projects import (
    ProjectCreateSchema, 
    ProjectUpdateSchema, 
    ProjectResponseSchema,
    ProjectListResponseSchema,
    ProjectDetailsSchema
)
from app.services.auth import get_current_user_dependency
from app.enum import UserRoles
import math

router = APIRouter()

# Valid status options
VALID_STATUSES = ["Completed", "In Progress", "Planning", "On Hold"]

def validate_user_permissions(current_user):
    """Validate if user has permission to perform admin operations"""
    if isinstance(current_user, dict):  # Superuser
        return True
    elif hasattr(current_user, 'role') and current_user.role == UserRoles.ADMIN:
        return True
    return False

@router.post("/", response_model=ProjectResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Create a new project (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can create projects"
            )
        
        # Validate status
        if project_data.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        
        # Convert schema details to model details
        model_details = []
        for detail in project_data.details:
            model_details.append(Projects.Details(
                heading=detail.heading,
                description=detail.description
            ))
        
        # Create new project
        new_project = Projects(
            title=project_data.title,
            location=project_data.location,
            beds=project_data.beds,
            area=project_data.area,
            client=project_data.client,
            status=project_data.status,
            description=project_data.description,
            features=project_data.features,
            image=project_data.image,
            image_name=project_data.image_name,
            details=model_details
        )
        
        new_project.save()
        
        return ProjectResponseSchema(
            id=str(new_project.id),
            title=new_project.title,
            location=new_project.location,
            beds=new_project.beds,
            area=new_project.area,
            client=new_project.client,
            status=new_project.status,
            description=new_project.description,
            features=new_project.features,
            image=new_project.image,
            image_name=new_project.image_name,
            details=new_project.details,
            created_at=new_project.created_at,
            updated_at=new_project.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating project: {str(e)}"
        )

@router.get("/public", response_model=ProjectListResponseSchema)
async def get_projects_public(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),   
):
    """
    Get all projects with pagination and filtering (Public access)
    """
    try:
        # Build query filters
        query_filters = {}
        
        
        query_filters['status'] = "Completed"
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get projects with filters
        projects_query = Projects.objects(**query_filters)
        total_projects = projects_query.count()
        
        projects = projects_query.skip(skip).limit(limit).order_by('-created_at')
        
        # Convert to response format
        project_list = []
        for project in projects:
            project_list.append(ProjectResponseSchema(
                id=str(project.id),
                title=project.title,
                location=project.location,
                beds=project.beds,
                area=project.area,
                client=project.client,
                status=project.status,
                description=project.description,
                features=project.features,
                image=project.image,
                image_name=project.image_name,
                details=project.details,
                created_at=project.created_at,
                updated_at=project.updated_at
            ))
        
        return ProjectListResponseSchema(
            projects=project_list,
            total=total_projects,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching projects: {str(e)}"
        )

@router.get("/admin", response_model=ProjectListResponseSchema)
async def get_projects_admin(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    client: Optional[str] = Query(None, description="Filter by client"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    current_user = Depends(get_current_user_dependency)
):
    """
    Get all projects with pagination and filtering (Admin only - includes all projects)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can access this endpoint"
            )
        
        # Build query filters
        query_filters = {}
        
        if status and status in VALID_STATUSES:
            query_filters['status'] = status
        
        if client:
            query_filters['client__icontains'] = client
        
        if search:
            query_filters['$or'] = [
                {'title__icontains': search},
                {'description__icontains': search}
            ]
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get projects with filters
        projects_query = Projects.objects(**query_filters)
        total_projects = projects_query.count()
        
        projects = projects_query.skip(skip).limit(limit).order_by('-created_at')
        
        # Convert to response format
        project_list = []
        for project in projects:
            project_list.append(ProjectResponseSchema(
                id=str(project.id),
                title=project.title,
                location=project.location,
                beds=project.beds,
                area=project.area,
                client=project.client,
                status=project.status,
                description=project.description,
                features=project.features,
                image=project.image,
                image_name=project.image_name,
                details=project.details,
                created_at=project.created_at,
                updated_at=project.updated_at
            ))
        
        return ProjectListResponseSchema(
            projects=project_list,
            total=total_projects,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching projects: {str(e)}"
        )

@router.get("/{project_id}", response_model=ProjectResponseSchema)
async def get_project(project_id: str):
    """
    Get a specific project by ID (Public access)
    """
    try:
        project = Projects.objects(id=project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return ProjectResponseSchema(
            id=str(project.id),
            title=project.title,
            location=project.location,
            beds=project.beds,
            area=project.area,
            client=project.client,
            status=project.status,
            description=project.description,
            features=project.features,
            image=project.image,
            image_name=project.image_name,
            details=project.details,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching project: {str(e)}"
        )

@router.put("/{project_id}", response_model=ProjectResponseSchema)
async def update_project(
    project_id: str,
    project_data: ProjectUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update a project (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update projects"
            )
        
        # Find the project
        project = Projects.objects(id=project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Validate status if provided
        if project_data.status and project_data.status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        
        # Update fields
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'details' and value is not None:
                # Convert schema details to model details
                model_details = []
                for detail in value:
                    model_details.append(Projects.Details(
                        heading=detail['heading'],
                        description=detail['description']
                    ))
                setattr(project, field, model_details)
            else:
                setattr(project, field, value)
        
        project.save()
        
        return ProjectResponseSchema(
            id=str(project.id),
            title=project.title,
            location=project.location,
            beds=project.beds,
            area=project.area,
            client=project.client,
            status=project.status,
            description=project.description,
            features=project.features,
            image=project.image,
            image_name=project.image_name,
            details=project.details,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating project: {str(e)}"
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Delete a project (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete projects"
            )
        
        # Find and delete the project
        project = Projects.objects(id=project_id).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project: {str(e)}"
        )

@router.get("/stats/summary")
async def get_project_stats(current_user = Depends(get_current_user_dependency)):
    """
    Get project statistics (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_user_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view project statistics"
            )
        
        # Get total count
        total_projects = Projects.objects.count()
        
        # Get count by status
        status_counts = {}
        for status in VALID_STATUSES:
            status_counts[status] = Projects.objects(status=status).count()
        
        # Get count by client
        clients = Projects.objects.distinct('client')
        client_counts = {}
        for client in clients:
            client_counts[client] = Projects.objects(client=client).count()
        
        return {
            "total_projects": total_projects,
            "status_breakdown": status_counts,
            "client_breakdown": client_counts,
            "total_clients": len(clients)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching project statistics: {str(e)}"
        )

