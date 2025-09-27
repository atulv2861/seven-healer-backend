from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.utils import (
    authenticate_user, 
    create_access_token, 
    get_hashed_password, 
    get_current_user
)
from app.schemas.auth import (
    UserSignupSchema, 
    UserLoginSchema, 
    UserResponseSchema, 
    TokenResponseSchema,
    UserUpdateSchema,
    UserPasswordUpdateSchema,
    UserListResponseSchema
)
from app.models.users import Users
from app.enum import UserRoles
from app.core import config
import re
from datetime import datetime

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Dependency to get current user
async def get_current_user_dependency(token: str = Depends(oauth2_scheme)):
    """Dependency to get current user from token"""
    user = get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignupSchema):
    """
    Register a new user
    """
    try:
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate phone format (basic validation)
        if not re.match(r"^\+?[\d\s\-\(\)]{10,15}$", user_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
        
        # Check if user already exists
        existing_user = Users.objects(email=user_data.email.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = get_hashed_password(user_data.password)
        
        # Create new user
        new_user = Users(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email.lower(),
            password=hashed_password,
            phone=user_data.phone,
            role=user_data.role,
            is_active=False
        )
        
        new_user.save()
        
        # Return user data (without password)
        return UserResponseSchema(
            id=str(new_user.id),
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            email=new_user.email,
            phone=new_user.phone,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=TokenResponseSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login user and return access token
    """
    try:
        # Authenticate user
        user = authenticate_user(form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is admin and active
        if isinstance(user, dict):  # Superuser - always allow
            pass  # Superuser can always login
        else:  # Regular user - check role and status
            if user.role != UserRoles.ADMIN or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. Only active admin users can login.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Create access token
        access_token = create_access_token(subject=user.get("email") if isinstance(user, dict) else user.email)
        
        # Prepare user response
        if isinstance(user, dict):  # Superuser
            user_response = UserResponseSchema(
                id=user["id"],
                first_name=user["profile"]["firstName"],
                last_name=user["profile"]["lastName"],
                email=user["email"],
                phone="",  # Superuser doesn't have phone
                role=UserRoles.ADMIN,
                is_active=True,
                created_at=datetime.utcnow(),  # Superuser doesn't have real timestamps
                updated_at=datetime.utcnow()
            )
        else:  # Regular user
            user_response = UserResponseSchema(
                id=str(user.id),
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        
        return TokenResponseSchema(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@router.get("/me", response_model=UserResponseSchema)
async def get_current_user_info(current_user = Depends(get_current_user_dependency)):
    """
    Get current user information
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if isinstance(current_user, dict):  # Superuser
        return UserResponseSchema(
            id=current_user["id"],
            first_name=current_user["profile"]["firstName"],
            last_name=current_user["profile"]["lastName"],
            email=current_user["email"],
            phone="",
            role=UserRoles.ADMIN,
            is_active=True,
            created_at=datetime.utcnow(),  # Superuser doesn't have real timestamps
            updated_at=datetime.utcnow()
        )
    else:  # Regular user
        return UserResponseSchema(
            id=str(current_user.id),
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            email=current_user.email,
            phone=current_user.phone,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )

@router.post("/logout")
async def logout():
    """
    Logout user (client should remove token)
    """
    return {"message": "Successfully logged out"}

def validate_admin_permissions(current_user):
    """Validate if user has admin permissions"""
    if isinstance(current_user, dict):  # Superuser
        return True
    elif hasattr(current_user, 'role') and current_user.role == UserRoles.ADMIN:
        return True
    return False

@router.get("/users", response_model=UserListResponseSchema)
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and email"),
    current_user = Depends(get_current_user_dependency)
):
    """
    Get all users with pagination and filtering (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_admin_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view user list"
            )
        
        # Build query filters
        query_filters = {}
        
        if role and role in [UserRoles.ADMIN.value, UserRoles.USER.value]:
            query_filters['role'] = role
        
        if is_active is not None:
            query_filters['is_active'] = is_active
        
        if search:
            query_filters['$or'] = [
                {'first_name__icontains': search},
                {'last_name__icontains': search},
                {'email__icontains': search}
            ]
        
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Get users with filters
        users_query = Users.objects(**query_filters)
        total_users = users_query.count()
        
        users = users_query.skip(skip).limit(limit).order_by('-created_at')
        
        # Convert to response format
        user_list = []
        for user in users:
            user_list.append(UserResponseSchema(
                id=str(user.id),
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            ))
        
        return UserListResponseSchema(
            users=user_list,
            total=total_users,
            page=page,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=UserResponseSchema)
async def get_user_by_id(
    user_id: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Get a specific user by ID (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_admin_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view user details"
            )
        
        # Find the user
        user = Users.objects(id=user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponseSchema(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )

@router.put("/users/{user_id}", response_model=UserResponseSchema)
async def update_user(
    user_id: str,
    user_data: UserUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update user information (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_admin_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update users"
            )
        
        # Find the user
        user = Users.objects(id=user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate email format if provided
        if user_data.email and not re.match(r"[^@]+@[^@]+\.[^@]+", user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Validate phone format if provided
        if user_data.phone and not re.match(r"^\+?[\d\s\-\(\)]{10,15}$", user_data.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
        
        # Check if new email already exists (if being updated)
        if user_data.email and user_data.email.lower() != user.email:
            existing_user = Users.objects(email=user_data.email.lower()).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'email':
                setattr(user, field, value.lower())
            else:
                setattr(user, field, value)
        
        user.save()
        
        return UserResponseSchema(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

@router.patch("/users/{user_id}/password", response_model=UserResponseSchema)
async def update_user_password(
    user_id: str,
    password_data: UserPasswordUpdateSchema,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update user password (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_admin_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update user passwords"
            )
        
        # Find the user
        user = Users.objects(id=user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate password strength (basic validation)
        if len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Hash new password
        hashed_password = get_hashed_password(password_data.new_password)
        user.password = hashed_password
        user.save()
        
        return UserResponseSchema(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating password: {str(e)}"
        )

@router.patch("/users/{user_id}/status", response_model=UserResponseSchema)
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update user active status (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_admin_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update user status"
            )
        
        # Find the user
        user = Users.objects(id=user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update status
        user.is_active = is_active
        user.save()
        
        return UserResponseSchema(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user status: {str(e)}"
        )

@router.patch("/users/{user_id}/role", response_model=UserResponseSchema)
async def update_user_role(
    user_id: str,
    role: UserRoles,
    current_user = Depends(get_current_user_dependency)
):
    """
    Update user role (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_admin_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can update user roles"
            )
        
        # Find the user
        user = Users.objects(id=user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update role
        user.role = role
        user.save()
        
        return UserResponseSchema(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user role: {str(e)}"
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user = Depends(get_current_user_dependency)
):
    """
    Delete a user (Admin only)
    """
    try:
        # Check if user has admin permissions
        if not validate_admin_permissions(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete users"
            )
        
        # Find the user
        user = Users.objects(id=user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deleting themselves
        if isinstance(current_user, dict):  # Superuser
            pass  # Superuser can delete anyone
        else:  # Regular admin
            if str(user.id) == str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot delete your own account"
                )
        
        # Delete the user
        user.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )