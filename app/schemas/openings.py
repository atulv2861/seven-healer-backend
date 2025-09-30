from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class KeyResponsibilityItemSchema(BaseModel):
    category: str = Field(..., max_length=200, description="Responsibility category")
    items: List[str] = Field(..., description="List of responsibility items")

class JobOpeningBaseSchema(BaseModel):
    job_id: str = Field(..., max_length=20, description="Unique job identifier (e.g., JD-0028)")
    title: str = Field(..., max_length=200, description="Job title")
    company: str = Field(..., max_length=100, description="Company name")
    location: str = Field(..., max_length=200, description="Job location")
    type: str = Field(..., description="Job type")
    posted_date: str = Field(..., max_length=100, description="Posted date string")
    description: str = Field(..., max_length=2000, description="Job description")
    overview: str = Field(..., max_length=3000, description="Detailed job overview")
    key_responsibilities: List[KeyResponsibilityItemSchema] = Field(..., description="Key responsibilities by category")
    qualifications: List[str] = Field(..., description="Required qualifications")
    remuneration: str = Field(..., max_length=200, description="Salary/remuneration details")
    why_join_us: str = Field(..., max_length=2000, description="Why join us section")
    is_active: str = Field(default="Active", description="Job status")

class JobOpeningCreateSchema(JobOpeningBaseSchema):
    pass

class JobOpeningUpdateSchema(BaseModel):
    job_id: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    type: Optional[str] = Field(None)
    posted_date: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    overview: Optional[str] = Field(None, max_length=3000)
    key_responsibilities: Optional[List[KeyResponsibilityItemSchema]] = Field(None)
    qualifications: Optional[List[str]] = Field(None)
    remuneration: Optional[str] = Field(None, max_length=200)
    why_join_us: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[str] = Field(None)

class JobOpeningResponseSchema(JobOpeningBaseSchema):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JobOpeningListResponseSchema(BaseModel):
    job_openings: List[JobOpeningResponseSchema]
    total: int
    page: int
    limit: int

class JobOpeningStatsSchema(BaseModel):
    total_jobs: int
    active_jobs: int
    inactive_jobs: int
    closed_jobs: int
    draft_jobs: int
    type_breakdown: dict
    company_breakdown: dict
