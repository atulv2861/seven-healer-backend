from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProjectDetailsSchema(BaseModel):
    heading: str = Field(..., description="Detail heading")
    description: str = Field(..., description="Detail description")
    
    class Config:
        from_attributes = True

class ProjectBaseSchema(BaseModel):
    title: str = Field(..., max_length=200, description="Project title")
    location: str = Field(..., max_length=100, description="Project location")
    beds: str = Field(..., max_length=50, description="Number of beds")
    area: str = Field(..., max_length=100, description="Project area")
    client: str = Field(..., max_length=100, description="Client name")
    status: str = Field(..., description="Project status")
    description: str = Field(..., max_length=1000, description="Project description")
    features: List[str] = Field(default_factory=list, description="Project features")
    image: Optional[str] = Field(None, description="Base64 encoded image")
    image_name: Optional[str] = Field(None, description="Original image name")
    details: List[ProjectDetailsSchema] = Field(default_factory=list, description="Project details")

class ProjectCreateSchema(ProjectBaseSchema):
    pass

class ProjectUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    beds: Optional[str] = Field(None, max_length=50)
    area: Optional[str] = Field(None, max_length=100)
    client: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None)
    description: Optional[str] = Field(None, max_length=1000)
    features: Optional[List[str]] = Field(None)
    image: Optional[str] = Field(None, description="Base64 encoded image")
    image_name: Optional[str] = Field(None, description="Original image name")
    details: Optional[List[ProjectDetailsSchema]] = Field(None, description="Project details")

class ProjectResponseSchema(ProjectBaseSchema):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectListResponseSchema(BaseModel):
    projects: List[ProjectResponseSchema]
    total: int
    page: int
    limit: int
