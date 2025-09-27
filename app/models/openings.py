from mongoengine import Document, StringField, ListField, EmbeddedDocumentField, EmbeddedDocument, DateTimeField
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
    requirements = ListField(StringField(), default=list)
    responsibilities = ListField(StringField(), default=list)
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
