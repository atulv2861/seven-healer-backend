from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.enum import UserRoles

class UserSignupSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: str
    role: UserRoles = UserRoles.USER

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    role: UserRoles
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseSchema

class TokenDataSchema(BaseModel):
    email: Optional[str] = None

class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[UserRoles] = None
    is_active: Optional[bool] = None

class UserPasswordUpdateSchema(BaseModel):
    new_password: str

class UserListResponseSchema(BaseModel):
    users: List[UserResponseSchema]
    total: int
    page: int
    limit: int

class SystemStatsSchema(BaseModel):
    total_blogs: int
    total_projects: int
    total_openings: int
    total_users: int

