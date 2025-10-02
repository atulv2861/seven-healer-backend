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

# Job Application Schemas
class JobApplicationBaseSchema(BaseModel):
    # Application Type
    apply_for_available_jobs: bool = Field(..., description="True if applying for available jobs, False for future jobs")
    selected_job_id: Optional[str] = Field(None, max_length=20, description="Job ID if applying for specific job")
    
    # Personal Information
    title: str = Field(..., max_length=10, description="Title (Mr., Mrs., Dr., etc.)")
    first_name: str = Field(..., max_length=100, description="First name")
    surname: str = Field(..., max_length=100, description="Surname")
    phone_number: str = Field(..., max_length=15, description="Phone number")
    email: str = Field(..., max_length=255, description="Email address")
    
    # Address Information
    street_address: str = Field(..., max_length=200, description="Street address")
    street_address_line2: Optional[str] = Field(None, max_length=200, description="Street address line 2")
    city: str = Field(..., max_length=100, description="City")
    state_province: str = Field(..., max_length=100, description="State or Province")
    postal_zip_code: str = Field(..., max_length=20, description="Postal or Zip code")
    
    # Professional Information
    highest_education: str = Field(..., max_length=200, description="Highest educational qualification")
    total_experience_years: str = Field(..., max_length=10, description="Total years of experience")
    current_last_employer: str = Field(..., max_length=200, description="Current or last employer")
    current_last_designation: str = Field(..., max_length=200, description="Current or last designation")
    
    # CV Upload
    cv_filename: Optional[str] = Field(None, max_length=255, description="CV filename")
    cv_data: Optional[str] = Field(None, description="Base64 encoded CV data")
    cv_size: Optional[str] = Field(None, max_length=20, description="CV file size")

class JobApplicationCreateSchema(JobApplicationBaseSchema):
    pass

class JobApplicationUpdateSchema(BaseModel):
    # Application Type
    apply_for_available_jobs: Optional[bool] = Field(None)
    selected_job_id: Optional[str] = Field(None, max_length=20)
    
    # Personal Information
    title: Optional[str] = Field(None, max_length=10)
    first_name: Optional[str] = Field(None, max_length=100)
    surname: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=15)
    email: Optional[str] = Field(None, max_length=255)
    
    # Address Information
    street_address: Optional[str] = Field(None, max_length=200)
    street_address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_zip_code: Optional[str] = Field(None, max_length=20)
    
    # Professional Information
    highest_education: Optional[str] = Field(None, max_length=200)
    total_experience_years: Optional[str] = Field(None, max_length=10)
    current_last_employer: Optional[str] = Field(None, max_length=200)
    current_last_designation: Optional[str] = Field(None, max_length=200)
    
    # CV Upload
    cv_filename: Optional[str] = Field(None, max_length=255)
    cv_data: Optional[str] = Field(None)
    cv_size: Optional[str] = Field(None, max_length=20)
    
    # Status (Admin only)
    status: Optional[str] = Field(None, description="Application status")

class JobApplicationResponseSchema(JobApplicationBaseSchema):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class JobApplicationListResponseSchema(BaseModel):
    applications: List[JobApplicationResponseSchema]
    total: int
    page: int
    limit: int

class JobApplicationStatsSchema(BaseModel):
    total_applications: int
    pending_applications: int
    under_review_applications: int
    shortlisted_applications: int
    rejected_applications: int
    hired_applications: int
    applications_by_job: dict

class JobApplicationStatusUpdateSchema(BaseModel):
    status: str = Field(..., description="New application status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "Under Review"
            }
        }
