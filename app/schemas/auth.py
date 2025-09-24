from pydantic import BaseModel, EmailStr
from typing import Optional
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

class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseSchema

class TokenDataSchema(BaseModel):
    email: Optional[str] = None

