from mongoengine import Document, StringField, ListField, EmbeddedDocumentField, EmbeddedDocument, DateTimeField, BooleanField
from datetime import datetime
import uuid

class KeyResponsibilityItem(EmbeddedDocument):
    category = StringField(required=True, max_length=200)
    items = ListField(StringField(), required=True)

class JobOpening(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = StringField(required=True, unique=True, max_length=20)  # e.g., 'JD-0028'
    title = StringField(required=True, max_length=200)
    company = StringField(required=True, max_length=100)
    location = StringField(required=True, max_length=200)
    type = StringField(required=True, max_length=50, choices=["Full Time", "Part Time", "Contract", "Internship", "Freelance"])
    posted_date = StringField(required=True, max_length=100)  # e.g., 'Posted 3 weeks ago'
    description = StringField(required=True, max_length=2000)
    overview = StringField(required=True, max_length=3000)
    key_responsibilities = ListField(EmbeddedDocumentField(KeyResponsibilityItem), required=True)
    qualifications = ListField(StringField(), required=True)
    remuneration = StringField(required=True, max_length=200)
    why_join_us = StringField(required=True, max_length=2000)
    is_active = StringField(default="Active", choices=["Active", "Inactive", "Closed", "Draft"])
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'job_openings',
        'indexes': ['job_id', 'title', 'company', 'type', 'is_active', 'created_at']
    }
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(JobOpening, self).save(*args, **kwargs)

class JobApplication(Document):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Application Type
    apply_for_available_jobs = BooleanField(required=True)  # True for available jobs, False for future jobs
    selected_job_id = StringField(max_length=20)  # Job ID if applying for specific job
    
    # Personal Information
    title = StringField(required=True, max_length=10)  # Mr., Mrs., Dr., etc.
    first_name = StringField(required=True, max_length=100)
    surname = StringField(required=True, max_length=100)
    phone_number = StringField(required=True, max_length=15)
    email = StringField(required=True, max_length=255)
    
    # Address Information
    street_address = StringField(required=True, max_length=200)
    street_address_line2 = StringField(max_length=200)
    city = StringField(required=True, max_length=100)
    state_province = StringField(required=True, max_length=100)
    postal_zip_code = StringField(required=True, max_length=20)
    
    # Professional Information
    highest_education = StringField(required=True, max_length=200)
    total_experience_years = StringField(required=True, max_length=10)
    current_last_employer = StringField(required=True, max_length=200)
    current_last_designation = StringField(required=True, max_length=200)
    
    # CV Upload
    cv_filename = StringField(max_length=255)  # Original filename
    cv_data = StringField()  # Base64 encoded PDF data
    cv_size = StringField(max_length=20)  # File size in bytes
    
    # Application Status
    status = StringField(default="Pending", choices=["Pending", "Under Review", "Shortlisted", "Rejected", "Hired"])
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'job_applications',
        'indexes': ['email', 'phone_number', 'selected_job_id', 'status', 'created_at']
    }
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(JobApplication, self).save(*args, **kwargs)
    
    def set_cv(self, cv_data, filename, file_size):
        """Set CV data"""
        self.cv_data = cv_data
        self.cv_filename = filename
        self.cv_size = str(file_size)
    
    def get_cv(self):
        """Get CV data"""
        if self.cv_data:
            return {
                'data': self.cv_data,
                'filename': self.cv_filename,
                'size': self.cv_size
            }
        return None
