from fastapi import APIRouter, HTTPException, Depends, status
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
    TokenResponseSchema
)
from app.models.users import Users
from app.enum import UserRoles
from app.core import config
import re

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
            is_active=new_user.is_active
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
                is_active=True
            )
        else:  # Regular user
            user_response = UserResponseSchema(
                id=str(user.id),
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active
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
            is_active=True
        )
    else:  # Regular user
        return UserResponseSchema(
            id=str(current_user.id),
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            email=current_user.email,
            phone=current_user.phone,
            role=current_user.role,
            is_active=current_user.is_active
        )

@router.post("/logout")
async def logout():
    """
    Logout user (client should remove token)
    """
    return {"message": "Successfully logged out"}